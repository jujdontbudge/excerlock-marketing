"""Sends through the local contacts-mcp server (its outbox gives idempotency and rate limits)."""
import json
from pathlib import Path

import requests


class ContactsMCP:
    def __init__(self, config=None):
        cfg = config or json.load(open(Path.home() / '.claude.json'))['mcpServers']['contacts']
        self.url, self.i = cfg['url'], 0
        self.h = {**cfg.get('headers', {}), 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        r = self._post({'method': 'initialize', 'params': {'protocolVersion': '2025-06-18', 'capabilities': {},
                                                           'clientInfo': {'name': 'inbox-gate', 'version': '1'}}})
        self.h['mcp-session-id'] = r.headers.get('mcp-session-id')
        requests.post(self.url, headers=self.h, json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, timeout=30)

    def _post(self, body):
        self.i += 1
        return requests.post(self.url, headers=self.h, json={'jsonrpc': '2.0', 'id': self.i, **body}, timeout=90)

    def call(self, tool, args):
        txt = self._post({'method': 'tools/call', 'params': {'name': tool, 'arguments': args}}).text
        if 'data:' in txt[:40]:
            txt = [l[5:] for l in txt.splitlines() if l.startswith('data:')][-1]
        body = json.loads(txt)
        if not isinstance(body, dict) or 'error' in body or not isinstance(body.get('result'), dict):
            raise RuntimeError(f'{tool}: contacts-mcp returned an error or no result')   # never read as "nothing" (AA02)
        res = body['result']
        if res.get('isError'):
            raise RuntimeError(f"{tool}: {res.get('content', [{}])[0].get('text', '')[:300]}")
        content = res.get('content', [{}])[0].get('text', '{}')
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    def _observe_person(self, action, person):
        """Keep what this person record positively shows, whatever else turns out unreadable later: every SideShift
        account it explicitly lists, and an exact 'do-not-contact' tag on them (review CZ01). Only accounts the record
        itself lists; the route's own account is added after the route is verified."""
        record = person.get('person', person) if isinstance(person, dict) else None
        if not isinstance(record, dict) or not record.get('id') or record.get('id') != action.person_id:
            return
        raw = record.get('handles') if 'handles' in record else person.get('handles')
        listed = [f"sideshift:{h['value_normalized']}" for h in (raw if isinstance(raw, list) else [])
                  if isinstance(h, dict) and h.get('channel') == 'sideshift'
                  and isinstance(h.get('value_normalized'), str) and h['value_normalized'].strip()]
        link = getattr(self, 'link_person', None)
        if link is not None:
            for key in listed:
                link(action.person_id, key)
        tags = record.get('tags')
        keep = getattr(self, 'remember_remote_dnc', None)
        if keep is not None and isinstance(tags, list) and 'do-not-contact' in tags:
            keep(action.person_id, listed)

    def preflight(self, action):
        """Definite checks before any request leaves. Raises DefiniteNoSend (safe to fix and retry)."""
        from .dispatch import DefiniteNoSend
        if not action.person_id:
            raise DefiniteNoSend('no linked person for this chat')
        uid = action.creator_key.split(':', 1)[-1]
        try:
            conv = self.call('get_conversation', {'conversation_id': action.conversation_id, 'limit': 1})
            person = self.call('get_person', {'person_id': action.person_id})
        except Exception as exc:
            raise DefiniteNoSend(f'could not verify the route ({type(exc).__name__})') from None
        self._observe_person(action, person)   # before ANY hold can return: positive evidence is never lost (CZ01)
        if not isinstance(conv, dict) or conv.get('id') != action.conversation_id:   # evidence for THIS route only (BN02)
            raise DefiniteNoSend('the route read is not the conversation we would send through')
        parts = (conv or {}).get('participants') if isinstance(conv, dict) else None
        # exactly one readable participant: an unreadable entry is unknown routing, never filtered away (BM01)
        if not isinstance(parts, list) or len(parts) != 1 or not isinstance(parts[0], dict):
            raise DefiniteNoSend('the route\'s participants can\'t be read as exactly one person')
        if (conv or {}).get('channel') not in (None, action.channel):
            raise DefiniteNoSend('route is on another channel')
        if (conv or {}).get('external_id', '').split(':')[-1] != action.source_chat_id:
            raise DefiniteNoSend('route is not the chat that was read')   # exact id, not a suffix (review N10)
        if [p.get('value_normalized') for p in parts] != [uid] or parts[0].get('person_id') != action.person_id:
            raise DefiniteNoSend('route does not belong to exactly this creator')
        record = person.get('person', person) if isinstance(person, dict) else None
        tags = record.get('tags') if isinstance(record, dict) else None
        if not isinstance(record, dict) or not record.get('id') or record.get('id') != action.person_id:
            raise DefiniteNoSend('the person record read is not this person (do-not-contact unknown)')   # AB03
        link = getattr(self, 'link_person', None)
        if link is not None:   # remember every READABLE linked account first, before any other hold returns (CP01, CQ02)
            link(action.person_id, action.creator_key)
            raw_handles = record.get('handles') if 'handles' in record else (person.get('handles') if isinstance(person, dict) else None)
            for h in raw_handles if isinstance(raw_handles, list) else []:
                if (isinstance(h, dict) and h.get('channel') == 'sideshift' and isinstance(h.get('value_normalized'), str)
                        and h['value_normalized'].strip()):
                    link(action.person_id, f"sideshift:{h['value_normalized']}")
        if not isinstance(tags, list):   # an unreadable person is not a clear one (review AA02)
            raise DefiniteNoSend('could not read the person record (do-not-contact unknown)')
        if 'do-not-contact' in tags:   # before other tags are judged: the verified route's account keeps it (CZ01)
            keep = getattr(self, 'remember_remote_dnc', None)
            if keep is not None:   # durable before holding: a later move to an untagged person can't clear it (CY01)
                raw = record.get('handles') if 'handles' in record else (person.get('handles') if isinstance(person, dict) else None)
                keep(action.person_id, [action.creator_key] + [
                    f"sideshift:{h['value_normalized']}" for h in (raw if isinstance(raw, list) else [])
                    if isinstance(h, dict) and h.get('channel') == 'sideshift'
                    and isinstance(h.get('value_normalized'), str) and h['value_normalized'].strip()])
            raise DefiniteNoSend('person is tagged do-not-contact')
        if not all(isinstance(t, str) for t in tags):   # every tag must be readable text (live: all strings) (BL01)
            raise DefiniteNoSend('a tag on this person can\'t be read (do-not-contact unknown)')
        # a captain's do-not-contact on ANY account linked to this person stops this one too (review CN01)
        handles = record.get('handles') if 'handles' in record else (person.get('handles') if isinstance(person, dict) else None)
        if not isinstance(handles, list) or not all(isinstance(h, dict) for h in handles):
            raise DefiniteNoSend('the person\'s linked accounts can\'t be read (do-not-contact unknown)')
        for h in handles:   # every linked account must be readable: unknown is never "not restricted" (review CO01)
            ch, val = h.get('channel'), h.get('value_normalized')
            if not isinstance(ch, str) or not ch.strip() or (ch == 'sideshift' and (not isinstance(val, str) or not val.strip())):
                raise DefiniteNoSend('a linked account of this person can\'t be read (do-not-contact unknown)')
        person_restricted = getattr(self, 'person_restricted', None)
        if person_restricted is not None and person_restricted(action.person_id):
            raise DefiniteNoSend('an account ever linked to this person is do-not-contact')   # (CP01)
        restricted = getattr(self, 'restricted', None)
        if restricted is not None:
            for h in handles:
                if h.get('channel') == 'sideshift' and restricted(f"sideshift:{h['value_normalized']}"):
                    raise DefiniteNoSend(f"a linked account of this person is do-not-contact (sideshift:{h['value_normalized']})")

    def send(self, action, text, key, authorized_by, expected_fingerprint=None, recheck=None, observe=None):
        """Re-reads the chat live one last time and refuses if it changed since the gate's final read (review N01).
        SideShift can't condition the send itself, so this is the narrowest gap possible (G27)."""
        from .dispatch import DefiniteNoSend
        if not action.person_id:
            raise DefiniteNoSend('no linked person for this chat')
        live = getattr(self, 'live', None)
        if live is None or not expected_fingerprint:
            raise DefiniteNoSend('no live reader to confirm the chat right before sending')
        try:
            now = live.read(action.source_chat_id, [action.creator_key.split(':', 1)[-1]])
        except Exception as exc:
            if observe is not None and getattr(exc, 'partial', None) is not None:
                observe(exc.partial)   # what it read before failing still counts as signing evidence (AF01)
            raise DefiniteNoSend(f'final live read failed ({type(exc).__name__})') from None
        if observe is not None:   # the gate sees this read whatever it shows, even when it stops the send (Z01)
            observe(now)
        if now.fingerprint != expected_fingerprint:
            raise DefiniteNoSend('the chat changed right before sending')
        if recheck is not None:
            reasons = recheck(now)
            if reasons:
                raise DefiniteNoSend('final check: ' + '; '.join(reasons)[:200])
        return self.call('send_message', {'conversation_id': action.conversation_id, 'person_id': action.person_id,
                                          'channel': action.channel, 'text': text, 'created_by': 'inbox-gate',
                                          'authorized_by': authorized_by, 'reason': f'{action.message_type}: {action.trigger}'[:300],
                                          'idempotency_key': key})
