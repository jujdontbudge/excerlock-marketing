"""The send gate. Every automatic creator message goes through Gate.run(action), and nothing else may send.

Order (any failure stops it and is journaled with the reason):
 1. the message type exists, renders from its approved template with valid fields only, and is switched on, or a
    one-use captain approval bound to this creator, type, occurrence and exact text exists (no producer can claim one);
 2. the idempotency key (namespaced by creator, occurrence and invite round) was never spent;
 3. the sender's definite pre-checks pass (linked person, route belongs to this creator, not do-not-contact);
 4. a per-chat lock owned by this run alone;
 5. the whole chat is read LIVE and every veto runs: chat/creator/contract binding, unknown senders, attachments
    nobody looked at, state (pending is never unsigned), do-not-contact, quiet hours, minimum gap (chat AND journal),
    the same text already sent, an unanswered question;
 6. draft-mode types stop here as a draft for the captain;
 7. Claude Opus reads the whole chat and must answer SEND (it can only stop a send);
 8. the chat is read live again and the contract re-read; if anything changed, or ANY veto now fails with the
    current time and switches (quiet hours, PAUSED, 24h), hold;
 9. the lock is confirmed still ours, the key re-checked, and a 'dispatching' intent committed BEFORE the send;
10. send through contacts-mcp with the idempotency key and the chat fingerprint. A failure after the request may
    have left is 'uncertain' and is never retried automatically.
Remaining limit (review G27): SideShift has no conditional send, so a message she writes in the second between the
final read and delivery can't be fenced. The final read is the last moment before the request leaves.
"""
import hashlib
import json
import inspect
import os
import re
import time
import uuid
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from . import checks, clock
from .journal import Busy
from .live import LiveReadError
from .model import Conversation, Decision
from .policy import MessageType, PolicyError, render

PAUSED = Path(__file__).resolve().parents[1] / 'PAUSED'
CAPTAIN_TEXT = 'captain-text'  # the captain's own exact words, sent only with his one-use approval


import contextvars

GRANT_GUARD = contextvars.ContextVar('grant_guard', default=None)   # last-instant check before a Premium grant
GRANT_WALL = contextvars.ContextVar('grant_wall', default=None)     # the gate's wall clock, for the grant's evidence age (DA01)


class DefiniteNoSend(RuntimeError):
    """Raised by a sender BEFORE any request leaves (missing person, wrong route, do-not-contact). Safe to retry."""


def text_hash(text):
    """Exact bytes: an approval covers these words exactly, spacing included (review N06)."""
    return hashlib.sha256(text.encode()).hexdigest()[:24]


CONTRACT_STATES = {'contract_open', 'not_accepted', 'accepted', 'contract_active'}
EVIDENCE_SPAN = 10   # seconds: all final reads (chat, contract, handle requests) must fit in this window (review U03, W01)


class Gate:
    def __init__(self, types, live, reviewer, sender, journal, now=None, paused_file=PAUSED, contract_reader=None, granter=None,
                 applications_reader=None, entitlement=None):
        self.types, self.live, self.reviewer, self.sender, self.journal = types, live, reviewer, sender, journal
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.paused_file = Path(paused_file)
        self.contract_reader = contract_reader  # contract id -> fresh contract dict; production always passes one
        # granter(action) -> (ok, line): gives free Premium for action.fields['email'] as the LAST step before an
        # app-access send, after every check passed (review N02). Without one, a recorded grant is required.
        self.granter = granter
        self.applications_reader = applications_reader   # creator id -> her current handle requests (fresh)
        # entitlement(email) -> True only when a READ-ONLY check says Premium is active now (never grants). Used when
        # the grant's own confirmation is older than EVIDENCE_SPAN at the final check (review AC02).
        self.entitlement = entitlement
        self._premium_at = None   # (email, monotonic time) of the last confirmation in this run
        self._reviewed = None     # evidence digest the review's SEND covers (review BD02)
        self._reviewed_tokens = {}   # message id -> answer token of the revision the review saw (review CD01)
        self.auto_switch = None   # optional callable -> reasons; an extra off-switch for automatic sends (review CD02)

        if live is not None and hasattr(live, 'on_notice') and getattr(live, 'on_notice', None) is None:
            live.on_notice = journal.remember_notice   # signing notices durable as each row is read (AI01)

    def key(self, t, action):
        if t.once == 'per_creator':
            return f'gate:{t.id}:{action.creator_key}'
        occurrence = action.occurrence
        if CONTRACT_STATES & set(t.requires) and (action.contract or {}).get('id'):
            occurrence = action.contract['id']   # one identity per contract, whoever proposes it (review N24)
        if not occurrence:
            raise PolicyError('per_occurrence type needs an occurrence')
        generation = (action.contract or {}).get('inviteGeneration')
        return f'gate:{t.id}:{action.creator_key}:{occurrence}' + (f':{generation}' if generation else '')

    # ---------------------------------------------------------------- entry

    def run(self, action):
        if hasattr(self.sender, 'preflight'):   # its person check consults DNC on every linked account (review CN01)
            try:
                self.sender.restricted = self.journal.restricted
                self.sender.link_person = self.journal.link_person            # (review CP01)
                self.sender.person_restricted = self.journal.person_restricted
                self.sender.remember_remote_dnc = self.journal.remember_remote_dnc   # (review CY01)
            except AttributeError:
                pass
        self._reviewed, self._premium_at = None, None   # per run: never carried over from another send
        self._reviewed_seen, self._reviewed_tokens = 0, {}
        holder = f'gate-{os.getpid()}-{uuid.uuid4().hex}'   # unique per run: no re-entry, no shared ownership (G05)
        if action.message_type == CAPTAIN_TEXT:
            t = MessageType(id=CAPTAIN_TEXT, mode='auto', channel=action.channel, approved='captain order', fields=('text',),
                            once='per_occurrence', quiet_hours=False, min_gap_minutes=0, requires=(), replaces_unanswered=True,
                            text='{text}')
        else:
            t = self.types.get(action.message_type)
            if t is None:
                return self._done(action, '', Decision('held', [f'unknown message type {action.message_type}']))
        try:
            key = self.key(t, action)
            text = render(t, action.fields)
        except PolicyError as exc:
            return self._done(action, '', Decision('held', [str(exc)]))
        if t.channel != action.channel:
            return self._done(action, key, Decision('held', [f'type is for {t.channel}, not {action.channel}']))
        ordered = self._approved(action, t, text, pin=False)
        self._approval_budget = None
        if ordered:   # its remaining life, anchored now on the sleep-aware clock: a wall-clock change can't extend it (DD01)
            expires = self.journal.approval_expires(action.approval_id)
            self._approval_budget = (clock.Since(self.now), (expires or 0) - time.time())
        self.sender.captain_ordered = bool(ordered)   # his order passes his own do-not-contact holds too (2026-10-15)
        try:
            if t.id == CAPTAIN_TEXT and not ordered:
                return self._done(action, key, Decision('held', ['captain-text needs a one-use captain approval for these exact words'], text))
            switched = self._switch_vetoes(t, ordered)
            if switched:
                return self._done(action, key, Decision('held', switched, text))
            round_based = bool(action.contract and CONTRACT_STATES & set(t.requires))
            if not round_based and self.journal.spent(key):   # round-based keys are checked once the live round is known (S06)
                return self._done(action, key, Decision('held', ['already sent (idempotency key spent)'], text))
            try:
                if hasattr(self.sender, 'preflight'):
                    self.sender.preflight(action)
            except DefiniteNoSend as exc:
                return self._done(action, key, Decision('held', [f'cannot send yet: {exc}'], text))
            try:   # one owner per chat AND per creator (review R01: one creator can have two routes)
                with self.journal.reserve(action.conversation_id, holder), self.journal.reserve(action.creator_key, holder), \
                        self.journal.reserve(f'person-lock:{action.person_id or action.creator_key}', holder), \
                        self.journal.reserve('component-lock:' + min(self.journal.component_accounts(action.creator_key)), holder):
                    # ...and per human across every account/person record ever linked (review CS02)
                    # one send at a time per known person too, so two accounts of hers can't race (review CR01)
                    try:
                        return self._guarded(action, t, key, text, ordered, holder)
                    finally:   # expire before any lock is released, so no other worker can take it first (review DH01)
                        if ordered:
                            self._approval_expired(action)
            except Busy as exc:
                return self._done(action, key, Decision('held', [str(exc)], text))
        finally:
            if ordered:   # every exit checks the elapsed budget, held returns too (review DG01)
                self._approval_expired(action)

    # ---------------------------------------------------------------- checks

    def _several_accounts(self, action):
        """She has more than one SideShift account linked to her (ever): every check would have to span all of them,
        so automation stops and the captain handles her by hand (review CU01-CU03). Live: 0 of 7 people."""
        others = sorted(self.journal.component_accounts(action.creator_key) - {action.creator_key})
        return [f'she has other linked SideShift accounts ({", ".join(others)}); the captain handles her'] if others else []

    def _owns(self, action, holder):
        # ...and the lock of her CURRENT group of linked accounts: a group that grew mid-run means another worker
        # may own it, so nothing happens until the run starts over (review CT02)
        group = 'component-lock:' + min(self.journal.component_accounts(action.creator_key))
        return (self.journal.owns(action.conversation_id, holder) and self.journal.owns(action.creator_key, holder)
                and self.journal.owns(group, holder))

    def _approved(self, action, t, text, pin=True):
        """pin=False only looks (before the live read); the approval is pinned to an invite round only once the
        round is known from the live chat."""
        approval = getattr(action, 'approval_id', None)
        if not approval:
            return False
        live_round_known = not (action.contract and CONTRACT_STATES & set(t.requires)) or 'inviteGeneration' in (action.contract or {})
        return self.journal.approval_valid(approval, action.creator_key, t.id, action.occurrence, text_hash(text),
                                           (action.contract or {}).get('inviteGeneration'), pin=pin and live_round_known)

    def _switch_vetoes(self, t, ordered):
        if ordered:
            return []
        if self.paused_file.exists():
            return ['automation is paused (sections/inbox/PAUSED)']
        if t.effective_mode == 'off':
            return [f'message type {t.id} is off']
        if t.effective_mode == 'auto' and self.auto_switch is not None:   # e.g. the inbox's INBOX_AUTO, re-checked
            return list(self.auto_switch())                                # before every effect (review CD02)
        return []

    def _read(self, action):
        """Every live chat read goes through here, so whatever it shows is observed before any check can return."""
        try:
            conv = self.live.read(action.source_chat_id, [action.creator_key.split(':', 1)[-1]])
        except LiveReadError as exc:   # what it read before failing still counts as signing evidence (AE02)
            if getattr(exc, 'partial', None) is not None:
                self._observe(action, exc.partial)
            raise
        self._observe(action, conv)
        return conv

    def _observe(self, action, conv):
        """Record positive signing evidence for this contract the moment any read shows it, before any comparison,
        key check or veto can return (review V04, Y03, Z01). Writes only when new, so a known fact never waits on the
        database. Unknown records are never recorded."""
        if conv is not None:   # every message revision, whatever the reader (review AY01)
            for m in conv.messages:
                if not m.vanished:
                    self.journal.remember_message(action.creator_key, m)
        c = action.contract
        if not (c and c.get('id')):
            return
        if conv is not None:   # every genuine invite read is kept for the invite clock (AT01)
            self.journal.remember_invites(action.creator_key, c['id'],
                                          [m for m in checks.invite_links(conv, {'id': c['id']}) if m.text])
        if conv is None:   # no chat to place a request in an invite round: any request or an active contract counts (AA01)
            seen = checks.status(c) in checks.ONBOARDING_STATUSES or bool(checks.structured_requests(c))
        else:
            seen = checks.signing_seen(conv, c)
        if seen and c['id'] not in self.journal.flags(action.creator_key, 'maybe-signed'):
            self.journal.event(action.creator_key, 'maybe-signed', c['id'], {'status': c.get('status'), 'by': 'gate'})

    def _seen_out(self, creator_key):
        """Our deliveries in her chat as observed on earlier reads ('out-seen': time and words digest)."""
        out = []
        for e in self.journal.events(creator_key):
            if e['kind'] == 'out-seen':
                try:
                    out.append(json.loads(e['data']))
                except (ValueError, TypeError):
                    continue
        return [d for d in out if d.get('at')]

    def _sent_elsewhere(self, t, action, text):
        """A once-per-creator message already reached this human on another account: a gate receipt, or the same
        words observed as our delivery there (manual sends included) (review CR01, CS01)."""
        for acct in sorted(self.journal.component_accounts(action.creator_key) - {action.creator_key}):
            if self.journal.spent(f'gate:{t.id}:{acct}'):
                return [f'already sent to another account of hers ({acct})']
        digest = checks.text_digest(text)
        norm = ' '.join(text.split())
        for acct, words, ref in self.journal.component_deliveries(action.creator_key):
            if (words is not None and ' '.join(words.split()) == norm) or (words is None and ref == digest):
                return [f'these exact words already reached her on another account ({acct})']
        return []

    def _signing(self, action, conv):
        """Every decision consults the recorded signing evidence, so a later deleted or emptied notice can't erase it."""
        c = action.contract
        if not (c and c.get('id')):
            return action
        events = self.journal.events(action.creator_key)
        c = {**c, 'recorded_invites': checks.recorded_invites(c, events)}   # the invite clock never rolls back (AT01)
        if checks.recorded_signing(c, events):
            c = {**c, 'signing_recorded': True}
        return replace(action, contract=c)

    def _vetoes(self, action, t, text, conv, ordered, now, exclude_attempt=None):
        live = conv   # what the chat shows NOW: the only thing that can authorize anything (review AZ02)
        conv = checks.with_history(conv, self.journal.events(action.creator_key))   # everything ever seen: vetoes (AY01)
        if self._reviewed is not None and checks.evidence_digest(conv) != self._reviewed:
            return ['new evidence appeared after the review (it never saw it); propose again']   # (BD02)
        action = self._signing(action, conv)
        key = action.creator_key
        reasons = checks.binding(conv, action)
        if action.contract and CONTRACT_STATES & set(t.requires) and checks.invite_order_unclear(conv, action.contract):
            reasons.append('two invites share a time and one is gone from the chat; the captain decides which is current')
        pinned = (action.contract or {}).get('inviteGeneration')
        if pinned and CONTRACT_STATES & set(t.requires) and checks.invite_generation(conv, action.contract) != pinned:
            reasons.append('the invite round changed since this send was keyed; propose again')   # (AV02)
        reasons += checks.completeness(conv, self.journal.flags(key, 'attachment-reviewed'))
        reasons += checks.state(conv, action, [r for r in t.requires if r != 'premium_granted'], now)
        reasons += checks.name_matches(action, live)   # personalisation must match SideShift's current name (AL02, BP01)
        if 'premium_granted' in t.requires:
            email = (action.fields.get('email') or '').lower()
            written = {m.text for m in live.messages if m.direction == 'in' and not m.deleted and not m.vanished}   # as written (BF02)
            if not email or email not in {tok for w in written for tok in checks.email_tokens(w)}:   # whole address only (BA02)
                reasons.append('the email is not in her own live messages')   # review N02: live provenance
            elif self.granter is None:   # a historical receipt is not current Premium; only a live check may claim it (S14)
                reasons.append('free Premium can only be confirmed by a live check (no granter configured)')
        if self.journal.restricted(key):
            reasons.append('do-not-contact')
        if checks.promised_open(text) and action.contract and any(   # "then we'll close it" vs his keep (DI04)
                e['kind'] == 'keep-invite' and e['ref'] == action.contract.get('id') for e in self.journal.events(key)):
            reasons.append('the captain said to keep this invite open; a message saying we will close it contradicts him')
        reasons += self._switch_vetoes(t, ordered)
        if not ordered:
            if t.quiet_hours:
                reasons += checks.quiet_hours(now)
            seen_out = [checks.ts(d['at']) for d in self._seen_out(key)]   # deliveries seen earlier, even if redacted (AX02)
            for d in self._seen_out(key):   # and their edits; unknown edit time counts as now (BT02)
                e = d.get('edited_at') or ''
                if e:
                    seen_out.append(now if e == 'unknown' or checks.ts(e) < checks.ts(d['at']) else checks.ts(e))
            for acct in self.journal.component_accounts(key) - {key}:   # her other accounts count too (review CR01)
                seen_out += self.journal.recent_sends(None, acct, exclude_attempt)
                seen_out += [checks.ts(d['at']) for d in self._seen_out(acct)]
                for d in self._seen_out(acct):
                    e = d.get('edited_at') or ''
                    if e:
                        seen_out.append(now if e == 'unknown' or checks.ts(e) < checks.ts(d['at']) else checks.ts(e))
                # the same edit-time rules as for this chat: unexplained changes there are unknown = recent (CT01)
                other = checks.with_history(Conversation(source='sideshift', external_id='', creator_ids=(), messages=(),
                                                         fingerprint='', read_at=''), self.journal.events(acct))
                for m in other.messages:
                    if m.direction == 'out' and not checks.gap_exempt(m):
                        seen_out.append(checks.ts(m.at))
                        if m.edited_at:
                            seen_out.append(checks.content_time(m) or now)
            reasons += checks.min_gap(conv, now, t.min_gap_minutes,
                                      self.journal.recent_sends(action.conversation_id, key, exclude_attempt) + seen_out)   # own attempt never counts (V01)
        # a per-invite message is a duplicate only within the current invite round: a delivery provably before the
        # round started doesn't count; unclear timing still does (review CF01)
        since = (checks.invite_time(conv, action.contract)
                 if action.contract and t.once == 'per_occurrence' and CONTRACT_STATES & set(t.requires) else None)
        changed = checks.changed_messages(self.journal.events(key))
        if checks.already_in_chat(conv, text, since, changed):
            reasons.append('this exact text is already in the chat')
        elif checks.text_digest(text) in {d.get('digest') for d in self._seen_out(key) if not checks.before_round(d, since, changed)}:
            reasons.append('this exact text was sent to her before (since deleted from the chat)')
        unread = [m for m in checks.unanswered(conv, self.journal.answered(key)) if m.kind == 'unreadable']
        if unread:   # a message we could not read at all: the captain settles it (record.py answered) (review BH01)
            reasons.append(f'{len(unread)} message(s) from her could not be read; the captain checks them')
        waiting = [m for m in checks.unanswered(conv, self.journal.answered(key)) if '?' in m.text]
        if waiting and not t.replaces_unanswered:   # every unmarked question blocks, wherever it sits (review R03)
            reasons.append(f'she asked something nobody has marked answered: "{waiting[-1].text[:120]}"')
        if ordered:   # his order is his judgment: only mechanical safety stops it, the right chat and no double send
            # (captain 2026-10-15: "when I say send, you send")
            keep = set(checks.binding(conv, action)) | {'this exact text is already in the chat',
                                                        'this exact text was sent to her before (since deleted from the chat)'}
            reasons = [r for r in reasons if r in keep]
        return reasons

    def _fresh_contract(self, action, conv=None):
        """Fresh handle requests, then the fresh contract. Each successful read is observed right away, before any
        later read can fail or a status change can return (review AA01); conv is the latest chat read."""
        if not action.contract or self.contract_reader is None:
            return action.contract, []
        fresh_apps, apps_known = None, False
        if self.applications_reader is not None:   # handle requests first, then the contract: the status is the newest (T02)
            try:
                fresh_apps, apps_known = self.applications_reader(action.creator_key.split(':', 1)[-1]), True
                self._observe(replace(action, contract={**action.contract, 'applications': fresh_apps}), conv)
            except Exception as exc:   # rows read before a failed page still count (AE01)
                fresh_apps, apps_known = None, True
                self._observe(replace(action, contract={**action.contract, 'applications': getattr(exc, 'partial', None) or []}), conv)
        try:
            fresh = self.contract_reader(action.contract['id'])
        except Exception as exc:
            return action.contract, [f'could not re-read the contract ({type(exc).__name__})']
        if not isinstance(fresh, dict):
            return action.contract, ['the contract re-read returned nothing usable']
        if fresh.get('id') != action.contract.get('id'):
            return action.contract, ['the contract re-read returned a different contract']
        if fresh.get('contractorId') != action.contract.get('contractorId'):
            return action.contract, ['the contract re-read belongs to someone else']
        self._observe(replace(action, contract={**action.contract, **fresh}), conv)   # e.g. now active (AA01)
        if str(fresh.get('status')).lower() != str(action.contract.get('status')).lower():
            return fresh, [f"the contract changed to {fresh.get('status')} during the check"]
        merged = {**action.contract, **fresh, 'inviteGeneration': action.contract.get('inviteGeneration')}
        if 'contractorName' not in fresh:
            merged['contractorName'] = None   # an omitted name is unknown now, not the old one (review BP01)
        if 'applications' not in fresh:
            if apps_known:
                merged['applications'] = fresh_apps
            elif action.contract.get('applications_required'):
                merged['applications'] = None   # an old list is not proof nothing new arrived (S02)
        return merged, []

    # ---------------------------------------------------------------- the guarded part

    def _guarded(self, action, t, key, text, ordered, holder):
        round_based = bool(action.contract and CONTRACT_STATES & set(t.requires))
        if not round_based and self.journal.spent(key):   # re-check under the lock (G04); round-based: after the read
            return self._done(action, key, Decision('held', ['already sent (idempotency key spent)'], text))
        several = self._several_accounts(action)
        if several:
            return self._done(action, key, Decision('held', several, text))
        if t.once == 'per_creator':   # once per HUMAN: any account ever linked to her counts (review CR01, CS01)
            elsewhere = self._sent_elsewhere(t, action, text)
            if elsewhere:
                return self._done(action, key, Decision('held', elsewhere, text))
        uid = action.creator_key.split(':', 1)[-1]
        try:
            conv = self._read(action)
        except LiveReadError as exc:
            return self._done(action, key, Decision('held', [f'no complete live read: {exc}'], text))
        if action.contract:   # journaled invites and signing join the contract BEFORE the round and key (AU02)
            action.contract = self._signing(action, conv).contract
        if action.contract and CONTRACT_STATES & set(t.requires):
            live_round = checks.invite_generation(checks.with_history(conv, self.journal.events(action.creator_key)),
                                                  action.contract)   # the chat itself, plus what it showed before (R05, AY02)
            claimed = action.contract.get('inviteGeneration')
            if claimed and claimed != live_round:
                return self._done(action, key, Decision('held', ['the invite round changed; propose again'], text, fingerprint=conv.fingerprint))
            legacy = self.key(t, replace(action, contract={**action.contract, 'inviteGeneration': None}))   # pre-round key (S06)
            action.contract = {**action.contract, 'inviteGeneration': live_round}
            key = self.key(t, action)
            if self.journal.spent(key):
                return self._done(action, key, Decision('held', ['already sent (idempotency key spent)'], text))
            if legacy and legacy != key and self.journal.spent(legacy):
                return self._done(action, key, Decision('held', ['a send from before invite rounds exists for this contract; '
                                                                  'the captain reconciles it once'], text))
            if ordered and not self._approved(action, t, text):
                return self._done(action, key, Decision('held', ['captain approval is for another invite round'], text))
        if action.contract and 'not_accepted' in t.requires:
            # "not yet signed" needs SideShift's own handle-request records, read now, whoever proposed it (review S02)
            if self.applications_reader is None:
                return self._done(action, key, Decision('held', ['no handle-request reader configured'], text, fingerprint=conv.fingerprint))
            try:
                apps = self.applications_reader(uid)
            except Exception as exc:   # rows read before a failed page still count; coverage stays unknown (AE01)
                apps = None
                self._observe(replace(action, contract={**action.contract, 'applications': getattr(exc, 'partial', None) or []}), conv)
            action.contract = {**action.contract, 'applications': apps, 'applications_required': True}
            self._observe(action, conv)   # her handle requests count as soon as they are read (Z01)
        reasons = self._vetoes(action, t, text, conv, ordered, self.now())
        if reasons:
            return self._done(action, key, Decision('held', reasons, text, fingerprint=conv.fingerprint))
        if t.effective_mode == 'draft' and not ordered:
            return self._done(action, key, Decision('draft', ['draft mode: the captain sends it'], text, fingerprint=conv.fingerprint))
        facts = ({'contract_status': (action.contract or {}).get('status'),
                  'name_in_sideshift': (action.contract or {}).get('contractorName')} if action.contract else {})
        if getattr(conv, 'creator_name', ''):
            facts['name_on_her_sideshift_chat'] = conv.creator_name   # the reviewer can check the greeting (BP01)
        try:
            takes_facts = len(inspect.signature(self.reviewer).parameters) >= 4
        except (TypeError, ValueError):
            takes_facts = False
        shown = checks.with_history(conv, self.journal.events(action.creator_key))   # the reviewer sees vanished ones too
        self._reviewed = checks.evidence_digest(shown)   # SEND covers exactly this evidence, nothing added later (BD02)
        self._reviewed_seen = self.journal.seen_mark(action.creator_key)   # its answers count from here (CB01)
        self._reviewed_tokens = {m.id: checks.answer_mark(m) for m in shown.messages
                                 if not m.vanished and not m.deleted}   # exactly what was reviewed (CD01)
        verdict, why, unanswered = self.reviewer(shown, text, t.id, facts) if takes_facts else self.reviewer(shown, text, t.id)
        if ordered and verdict != 'SEND':   # the review never overrules the captain's order: kept as a note only (2026-10-15)
            verdict, why, unanswered = 'SEND', f'captain order (review would have held: {why})', []
        if verdict != 'SEND':
            return self._done(action, key, Decision('held', [f'review: {why}'] + [f'unanswered: {u}' for u in unanswered],
                                                     text, fingerprint=conv.fingerprint))
        # everything again, with the current time, switches, chat and contract (G06, G07, G11)
        try:
            again = self._read(action)
        except LiveReadError as exc:
            return self._done(action, key, Decision('held', [f'no complete live re-read: {exc}'], text, fingerprint=conv.fingerprint))
        if again.fingerprint != conv.fingerprint:
            return self._done(action, key, Decision('held', ['the chat changed during the review'], text, fingerprint=again.fingerprint))
        fresh, changed = self._fresh_contract(action, again)
        self._observe(replace(action, contract=fresh), again)
        if changed:
            return self._done(action, key, Decision('held', changed, text, fingerprint=again.fingerprint))
        action.contract = fresh
        reasons = self._vetoes(action, t, text, again, ordered, self.now())
        if reasons:
            return self._done(action, key, Decision('held', reasons, text, fingerprint=again.fingerprint))
        try:   # route, person and do-not-contact again, right before sending (review N11)
            if hasattr(self.sender, 'preflight'):
                self.sender.preflight(action)
        except DefiniteNoSend as exc:
            return self._done(action, key, Decision('held', [f'cannot send now: {exc}'], text, fingerprint=again.fingerprint))
        if not self._owns(action, holder):
            return self._done(action, key, Decision('held', ['lost the chat lock during the check'], text, fingerprint=again.fingerprint))
        if self.journal.spent(key):
            return self._done(action, key, Decision('held', ['already sent (idempotency key spent)'], text))
        if ordered and not self._approved(action, t, text):
            return self._done(action, key, Decision('held', ['captain approval expired or no longer matches'], text))
        policy_now = self._policy_now(t, ordered)   # before ANY effect, the grant included (U04)
        if policy_now:
            return self._done(action, key, Decision('held', policy_now, text))
        if 'premium_granted' in t.requires and self.granter is not None:
            # grant.py calls this guard in the instant before the irreversible grant (review W03)
            # it re-checks EVERYTHING, not only the switches: contract, chat, do-not-contact, approval, locks (X01)
            token = GRANT_GUARD.set(lambda: self._pre_grant(action, t, key, text, again, ordered, holder))
            wall_token = GRANT_WALL.set(self.now)
            try:
                self._premium_at = None
                asked = clock.Since(self.now)   # the confirmation happened after this: never under-counted (AD02, DA01)
                ok, line = self.granter(action)
                if ok:
                    self._premium_at = ((action.fields.get('email') or '').lower(), asked)
            finally:
                GRANT_GUARD.reset(token)
                GRANT_WALL.reset(wall_token)
            if not ok:
                return self._done(action, key, Decision('held', [f'free Premium grant did not go through: {line}'], text,
                                                         fingerprint=again.fingerprint))
            # the grant can take minutes: read the chat again, re-check the route and do-not-contact, the contract
            # and every veto before sending (review R06, S05)
            try:
                after = self._read(action)
            except LiveReadError as exc:
                return self._done(action, key, Decision('held', [f'Premium granted, but no live re-read: {exc}'], text))
            if after.fingerprint != again.fingerprint:
                return self._done(action, key, Decision('held', ['Premium granted, but the chat changed meanwhile'], text, fingerprint=after.fingerprint))
            try:
                if hasattr(self.sender, 'preflight'):
                    self.sender.preflight(action)
            except DefiniteNoSend as exc:
                return self._done(action, key, Decision('held', [f'Premium granted, but cannot send now: {exc}'], text))
            fresh, changed = self._fresh_contract(action, after)
            if changed:
                return self._done(action, key, Decision('held', ['Premium granted, but: ' + changed[0]], text, fingerprint=again.fingerprint))
            action.contract = fresh
            reasons = self._vetoes(action, t, text, after, ordered, self.now())
            if reasons:
                return self._done(action, key, Decision('held', ['Premium granted, but: ' + r for r in reasons], text, fingerprint=again.fingerprint))
        if ordered and not self.journal.use_approval(action.approval_id):
            return self._done(action, key, Decision('held', ['captain approval was already used or expired'], text))
        policy_now = self._policy_now(t, ordered)
        if policy_now:
            return self._done(action, key, Decision('held', policy_now, text))
        # durable intent BEFORE the request leaves (G03); it must be the only live claim on this send (R01)
        attempt = self.journal.begin_attempt(action, key, Decision('dispatching', ['about to send'], text, key, again.fingerprint))
        if not self.journal.sole_attempt(key, attempt):
            return self._unsent(action, key, attempt, 'another worker claimed this send', text, ordered)
        if not self._owns(action, holder):   # lost the lock while recording (review N01)
            return self._unsent(action, key, attempt, 'lost the chat lock', text, ordered)
        authorized = (f'captain order: {action.captain_order}' if ordered
                      else f'message type {t.id} (captain approved {t.approved})')
        try:
            kwargs = {}
            params = inspect.signature(self.sender.send).parameters
            if 'expected_fingerprint' in params:
                kwargs['expected_fingerprint'] = again.fingerprint
            if 'recheck' in params:   # after the transport's own final read: contract, records, chat, lock (U02, U03, V02)
                kwargs['recheck'] = lambda final: self._final_recheck(action, t, text, final, ordered, holder, attempt)
            if 'observe' in params:   # the transport's final read is observed even when it changed (Z01)
                kwargs['observe'] = lambda final: self._observe(action, final)
            result = self.sender.send(action, text, key, authorized, **kwargs)
        except DefiniteNoSend as exc:
            return self._unsent(action, key, attempt, str(exc), text, ordered)
        except Exception as exc:  # the request may have left: never retry this key automatically
            return self._done(action, key, Decision('uncertain', [f'send raised {type(exc).__name__}: {str(exc)[:160]}'],
                                                     text, fingerprint=again.fingerprint))
        return self._outcome(action, t, key, text, again, result, why, attempt, ordered, reviewed=shown)

    def _policy_now(self, t, ordered):
        """Re-read the message type's file right before sending: an off switch or new wording stops it (review U04)."""
        if not t.source or ordered:
            return []
        try:
            from .policy import parse
            now_t = parse(t.source)
        except Exception as exc:
            return [f'message type file can no longer be read ({type(exc).__name__})']
        if replace(now_t, source='') != replace(t, source=''):   # ANY field, safety fields included (review W02)
            return [f'message type {t.id} changed while checking (now {now_t.effective_mode})']
        return []

    def _pre_grant(self, action, t, key, text, seen, ordered, holder):
        """In the instant before the irreversible Premium grant (the entitlement check before it can take minutes):
        fresh contract, the chat unchanged since `seen`, every veto, the captain's approval, the route, the locks and
        the policy, all read within EVIDENCE_SPAN on the monotonic clock (review X01)."""
        since = clock.Since(self.now)   # (DB01)
        reasons = self._final_recheck(action, t, text, seen, ordered, holder, premium=False)   # route/DNC too (Y01, Z03)
        reasons += self._switch_vetoes(t, ordered)
        if ordered and not self._approved(action, t, text):
            reasons.append('captain approval expired or no longer matches')
        if self.journal.spent(key):
            reasons.append('already sent (idempotency key spent)')
        if since.age() > EVIDENCE_SPAN:   # last: after every wait
            reasons.append(f'the pre-grant checks took longer than {EVIDENCE_SPAN}s, so their evidence may be stale')
        return reasons

    def _final_recheck(self, action, t, text, final, ordered, holder=None, attempt=None, premium=True):
        """Called by the transport after its own final live read, right before the request. Contract and records are
        read first, then the chat again (it must be unchanged since the transport's read), then the locks (U03, V02)."""
        self._observe(action, final)   # also observed here, for transports without an observe hook
        since = clock.Since(self.now)   # monotonic, wall and sleep-counting clocks: the largest wins (X04, DB01)
        fresh, changed = self._fresh_contract(action, final)
        if changed:
            return changed
        try:
            latest = self._read(replace(action, contract=fresh))
        except LiveReadError as exc:
            return [f'no live re-read after the contract check ({exc})']
        try:   # contacts route and do-not-contact tag are evidence too: re-read inside the window (Z03)
            if hasattr(self.sender, 'preflight'):
                self.sender.preflight(action)
        except DefiniteNoSend as exc:
            return [f'cannot send now: {exc}']
        reasons = [] if latest.fingerprint == final.fingerprint else ['the chat changed during the final checks']
        probe = replace(action, contract=fresh)
        reasons += self._vetoes(probe, t, text, latest, ordered, self.now(), attempt) + self._policy_now(t, ordered)
        if holder is not None and not self._owns(action, holder):
            reasons.append('lost the chat lock during the final checks')
        if premium and 'premium_granted' in t.requires:   # "Premium is on" needs a confirmation inside the window (AC02)
            email = (action.fields.get('email') or '').lower()
            confirmed = self._premium_at
            if not confirmed or confirmed[0] != email:
                reasons.append('no Premium confirmation for this email in this run')
            elif confirmed[1].age() > EVIDENCE_SPAN:
                if self.entitlement is None or not self.entitlement(email):   # read-only; never a second grant
                    reasons.append('Premium could not be confirmed active right before sending')
        reasons += self._several_accounts(action)   # a link learned mid-run stops it too (CU03)
        if t.once == 'per_creator':   # re-checked at the last moment, across her accounts (review CS02)
            reasons += self._sent_elsewhere(t, action, text)
        if attempt is not None and not self.journal.sole_attempt(self.key(t, action), attempt):
            reasons.append('another worker claimed this send')
        # LAST, after every read AND every journal wait: a database lock can stall too (U03, X04, Z02)
        if ordered:   # consumed earlier, then a slow transport read: the approval must still be in date now (DC01)
            if self._approval_expired(action):
                reasons.append('the captain\'s approval expired before the send')
        if since.age() > EVIDENCE_SPAN:
            reasons.append(f'the final checks took longer than {EVIDENCE_SPAN}s, so their evidence may be stale')
        return reasons

    def _approval_expired(self, action):
        """The captain's approval ran out by its wall deadline OR this run's sleep-aware budget (DD01); once seen,
        expired for good, so no later restore can revive it (DE01)."""
        expires = self.journal.approval_expires(action.approval_id)
        budget = getattr(self, '_approval_budget', None)
        if expires is None or expires <= time.time() or budget is None or budget[0].age() >= budget[1]:
            self.journal.expire_approval(action.approval_id)
            return True
        return False

    def _unsent(self, action, key, attempt, why, text, ordered):
        """Definitely not sent: release the attempt and give the captain's approval back (review S07), unless it has
        expired meanwhile: every no-send path ends here, so none can skip that check (DF01)."""
        if ordered:
            self._approval_expired(action)
            self.journal.restore_approval(action.approval_id)
        return self._done(action, key, Decision('error', [f'attempt:{attempt}', f'not sent: {why}'], text))

    def _outcome(self, action, t, key, text, conv, result, why, attempt=None, ordered=False, reviewed=None):
        if not isinstance(result, dict):
            return self._done(action, key, Decision('uncertain', [f'unexpected send result {str(result)[:120]!r}'], text, fingerprint=conv.fingerprint))
        status, outbox = result.get('status'), result.get('id')
        if status == 'sent':
            if t.replaces_unanswered:
                # the full-chat review confirmed this reply answers everything open; mark exactly those messages (N14)
                # exactly the revisions the review saw, vanished ones included (review AZ03)
                for m in checks.unanswered(reviewed or conv, self.journal.answered(action.creator_key)):
                    self.journal.answer(action.creator_key, checks.answer_mark(m),
                                        {'by': t.id, 'outbox': outbox, 'since': self._reviewed_seen})
            return self._done(action, key, Decision('sent', [why], text, key, conv.fingerprint, outbox))
        if status == 'failed' and not result.get('already_used'):
            return self._unsent(action, key, attempt, str(result.get('error')), text, ordered)
        used = ' (key already used)' if result.get('already_used') else ''
        return self._done(action, key, Decision('uncertain', [f"send status {status!r}{used}: {result.get('error')}"],
                                                 text, fingerprint=conv.fingerprint, outbox_id=outbox))

    def _done(self, action, key, decision):
        decision.idempotency_key = key
        self.journal.record(action, key or f'invalid:{action.message_type}', decision)
        return decision
