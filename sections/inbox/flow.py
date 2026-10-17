"""SideShift contract flow: decides what each ExcerLock contract needs and hands every message to the send gate.
Replaces contract_reminders.py (2026-10-14). Run by launchd every 15 minutes; it never sends by itself.

Per contract in campaign v4mH50Sz9sUdkssqcd2L:
- she accepted (a handle request in her chat, or the contract is active):
    record it once, check the requested handles are new (gate/handles.py) and record the verdict,
    then propose `ask-app-email` (once per creator);
- invite open and not accepted: 6h after the invite propose `contract-reminder-1`, 12h after propose `contract-reminder-2` (the last-call: open 12 more hours);
- 24h after the invite (and 12h after the last-call), still not accepted: record `withdraw-due`. Withdrawing is a separate, explicit step
  (withdraw.py) and never sends a message (captain, 2026-10-14).
Usage: .venv/bin/python sections/inbox/flow.py [--dry-run]
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / 'integrations/sideshift'))

from gate import checks, clock, handles, policy  # noqa: E402
from gate.dispatch import Gate  # noqa: E402
from gate.journal import Journal  # noqa: E402
from gate.live import LiveReadError, SideShiftLive, application_owner, collect_applications  # noqa: E402
from gate.model import Action  # noqa: E402
import withdraw  # noqa: E402

CAMPAIGN = 'v4mH50Sz9sUdkssqcd2L'
WARMUP_DOC = '1guNLxDR65XXBlYbMOgHIeUw_aRi8cT8J3fSS71vNIEY'
COMPANY = 'L9suC60QYBRzy8rRY16r1FtjyPT2'
REMINDERS = ((checks.INVITE_AGE['invite_6h'], 'contract-reminder-1'), (checks.INVITE_AGE['invite_12h'], 'contract-reminder-2'))   # the gate enforces the same ages
WITHDRAW_AFTER = timedelta(hours=24)


def first_name(contract):
    name = contract.get('contractorName') if isinstance(contract, dict) else None
    return name.split(' ')[0].strip() if isinstance(name, str) else ''   # odd data never crashes the run (review N20)


class Flow:
    def __init__(self, contracts_client, live, gate, journal, routes, now=None, fetchers=None, write_client=None, read_client=None):
        """routes(chat_id) -> (contacts conversation id, person id) or (None, None)."""
        self.contracts_client, self.live, self.gate, self.journal, self.routes = contracts_client, live, gate, journal, routes
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.fetchers = fetchers or {'tiktok': handles.fetch_tiktok, 'instagram': handles.fetch_instagram}
        self.write_client = write_client  # None until a contracts:write key exists: withdrawals then only record why they held
        self.read_client = read_client    # SIDESHIFT_READ_KEY: SideShift's own handle-request records

    def fetch_contract(self, contract_id):
        got = self.contracts_client.request('GET', f'/contracts/{contract_id}')
        return got.get('data', got) if isinstance(got, dict) else got

    def chats_by_creator(self):
        out = {}
        for c in self.live.client.pages('/conversations'):
            for m in c.get('members', []):
                if m != COMPANY:
                    out.setdefault(m, []).append(c['id'])
        return out

    def applications_by_creator(self):
        """SideShift's handle requests for this campaign, by creator id ({} without a read key)."""
        if self.read_client is None:
            return {}
        out = {}
        try:
            for a in self.read_client.pages('/applications'):
                uid = application_owner(a, CAMPAIGN)   # unreadable rows make coverage unknown (AK01)
                if uid is None:
                    continue
                out.setdefault(uid, []).append(a)
                self.remember_request(uid, a)   # durable the moment it is read, whatever fails next (AG02)
        except Exception as exc:   # a later page failed: rows already read still prove requests (review AD01)
            exc.partial = out
            raise
        return out

    def run(self):
        report = []
        chats = self.chats_by_creator()
        apps_partial = {}
        try:
            apps = self.applications_by_creator()
        except Exception as exc:   # unknown, not empty: blocks withdrawal; chat signals still block reminders (R07)
            apps, apps_partial = None, getattr(exc, 'partial', {})   # rows read before the failure still count (AD01)
            report.append(f'handle requests could not be read from SideShift ({type(exc).__name__})')
        for contract in self.contracts_client.pages('/contracts', programId=CAMPAIGN):
            if not isinstance(contract, dict) or not contract.get('contractorId') or not contract.get('id'):
                report.append('a contract row with no id or creator was skipped')   # review R18
                continue
            uid, key = contract.get('contractorId'), f"sideshift:{contract.get('contractorId')}"
            try:
                self.observe(key, contract, apps_partial.get(uid, []) if apps is None else apps.get(uid, []))   # before any chat read (AB01)
                found = chats.get(uid, [])
                if len(found) != 1:
                    self.journal.event(key, 'chat-ambiguous', contract.get('id'), {'chats': found})
                    report.append(f'{first_name(contract)}: {len(found)} SideShift chats found, needs a person')
                    continue
                try:
                    conv = self.live.read(found[0], [uid])
                except LiveReadError as exc:
                    chat_part = getattr(exc, 'partial', None)   # a notice read before the failure still counts (AE02)
                    if chat_part is not None and checks.signing_seen(chat_part, contract) \
                            and contract['id'] not in self.journal.flags(key, 'maybe-signed'):
                        self.journal.event(key, 'maybe-signed', contract['id'], {'by': 'flow-partial-chat'})
                    report.append(f'{first_name(contract)}: no live read ({exc})')
                    continue
                self.journal.remember_invites(key, contract['id'], checks.invite_links(conv, {'id': contract['id']}))   # AU01
                evidence = {'applications': None if apps is None or self.read_client is None else apps.get(uid, []),
                            'applications_required': True}   # no read key = unknown, never "none" (S02)
                if checks.signing_seen(conv, {**contract, **evidence}) \
                        and contract['id'] not in self.journal.flags(key, 'maybe-signed'):   # before routes etc. (AC01)
                    self.journal.event(key, 'maybe-signed', contract['id'], {'status': checks.status(contract), 'by': 'flow-chat'})
                report += self.handle({**contract, **evidence}, conv, key)
            except Exception as exc:  # one creator's odd data must never stop the others (review G25)
                self.journal.event(key, 'flow-error', f"{contract.get('id')}:{self.now():%Y-%m-%dT%H}", {'error': f'{type(exc).__name__}: {exc}'[:300]})
                report.append(f'{first_name(contract)}: error {type(exc).__name__}, recorded for a person')
        return report

    def remember_request(self, uid, a):
        """Journal one of her handle requests as soon as it is read, before contracts are even listed (review AG02)."""
        self.journal.remember_request(f'sideshift:{uid}', a)

    def observe(self, key, contract, apps):
        """Record positive signing evidence the moment Flow reads it, before any chat read can fail or be ambiguous
        (review AB01): an active contract, or a request of hers not provably older than this contract. Without the
        chat the invite round is unknown, so a request counts unless its date is before the contract's own."""
        try:
            created = checks.ts(contract.get('createdAt')) if contract.get('createdAt') else None
        except ValueError:
            created = None
        def newer(a):
            try:
                return created is None or not a.get('requestedAt') or checks.ts(a['requestedAt']) >= created
            except (ValueError, TypeError):
                return True
        seen = checks.status(contract) in checks.ONBOARDING_STATUSES or any(
            not isinstance(a, dict) or newer(a) for a in (apps or []))
        if seen and contract['id'] not in self.journal.flags(key, 'maybe-signed'):
            self.journal.event(key, 'maybe-signed', contract['id'], {'status': checks.status(contract), 'by': 'flow-read'})

    def identity_check(self, base):
        """Read her contacts identity live (route, person, every linked account) through the sender's preflight, which
        also journals each linked account; an unreadable identity or a restriction holds (review CV01). Without a
        sender that can check, nothing irreversible happens."""
        sender = getattr(self.gate, 'sender', None) if self.gate is not None else None
        if sender is None or not hasattr(sender, 'preflight'):
            return ['her contacts identity could not be checked']
        from gate.dispatch import DefiniteNoSend
        try:
            sender.restricted = self.journal.restricted
            sender.link_person = self.journal.link_person
            sender.person_restricted = self.journal.person_restricted
            sender.remember_remote_dnc = self.journal.remember_remote_dnc
            sender.preflight(Action(message_type='withdrawal-check', fields={}, trigger='withdrawal identity check', **base))
        except DefiniteNoSend as exc:
            return [f'contacts identity: {exc}']
        except Exception as exc:
            return [f'contacts identity could not be read ({type(exc).__name__})']
        return []

    def check_handles(self, key, conv, contract):
        """Check the handles she requested in the current invite round, once per request (review G19). SideShift's
        records are used when available (one check per set of request ids); chat notices otherwise."""
        invited = checks.invite_time(conv, contract)
        done = self.journal.flags(key, 'handle-check')
        structured = checks.structured_requests(contract, invited, eligible_only=True)
        if structured:   # the reviewed handles are part of the identity: an edited handle is checked again (R17)
            pairs = [(a['platform'], str(a['handle']).lstrip('@')) for a in structured if a.get('platform') and a.get('handle')]
            if len(pairs) != len(structured):   # a request we can't fully read is never skipped (review BH02)
                pairs.append(('unknown', 'incomplete-request'))
            ref = 'apps:' + ','.join(sorted(f"{a.get('requestId') or a.get('id')}={a.get('platform')}:{a.get('handle')}" for a in structured))
            batches = [(ref, pairs)]
        else:   # a chat notice: its id plus its content, so an edited request is checked again (review N17)
            batches = [(checks.mark(m), handles.requested_pairs(m.text)) for m in conv.messages if m.kind == 'handle_request'
                       and m.direction == 'in' and not m.deleted and (invited is None or checks.ts(m.at) >= invited)]
        for ref, pairs in batches:
            if ref in done:
                continue
            wanted = dict(pairs)
            unchecked = sorted({p for p, _ in pairs if p not in self.fetchers and p != 'unknown'})
            if unchecked:   # a platform we can't check is never left out of a verdict (review BK02)
                self.journal.event(key, 'handle-check', f'{ref}@{self.now():%Y-%m-%dT%H}',
                                   {'handles': [f'{p}:@{h}' for p, h in pairs], 'verdict': 'ask',
                                    'reasons': [f'{p} accounts can\'t be checked automatically; check it yourself' for p in unchecked]})
                continue
            if ('unknown', 'incomplete-request') in pairs:
                self.journal.event(key, 'handle-check', f'{ref}@{self.now():%Y-%m-%dT%H}',
                                   {'handles': [f'{p}:@{h}' for p, h in pairs], 'verdict': 'ask',
                                    'reasons': ['a handle request is missing its platform or handle; check it in SideShift']})
                continue
            several = sorted({p for p, _ in pairs if len({h for q, h in pairs if q == p}) > 1})
            if several:   # two accounts on one platform: never check only one of them; the captain picks (BG02)
                self.journal.event(key, 'handle-check', f'{ref}@{self.now():%Y-%m-%dT%H}',
                                   {'handles': [f'{p}:@{h}' for p, h in pairs], 'verdict': 'ask',
                                    'reasons': [f'more than one {p} account requested; which one is hers to use?' for p in several]})
                continue
            profiles = {p: self.fetchers[p](h) for p, h in wanted.items() if p in self.fetchers}
            verdict, reasons = handles.judge(profiles, self.now())
            if verdict == 'ask':
                # not final (missing or unreadable data, or a person must decide): shown, and re-checked next hour (R17)
                self.journal.event(key, 'handle-check', f'{ref}@{self.now():%Y-%m-%dT%H}', {'handles': wanted, 'verdict': verdict, 'reasons': reasons})
                continue
            self.journal.event(key, 'handle-check', ref, {'handles': wanted, 'verdict': verdict, 'reasons': reasons})

    def handle(self, contract, conv, key):
        name, status = first_name(contract), checks.status(contract)
        self.journal.event(key, f'contract-{status}', contract['id'], {'status': status})
        if status in checks.CLOSED_STATUSES:
            return [f'{name}: contract {status}, nothing to do']
        for m in conv.messages:   # every revision, even without a hooked reader (review AY01)
            self.journal.remember_message(key, m)
        self.journal.remember_invites(key, contract['id'], checks.invite_links(conv, {'id': contract['id']}))
        events = self.journal.events(key)
        conv = checks.with_history(conv, events)   # decide on everything ever seen, not only what is visible now (AY01)
        contract = {**contract, 'recorded_invites': checks.recorded_invites(contract, events)}   # (AT01)
        if checks.recorded_signing(contract, events):
            contract = {**contract, 'signing_recorded': True}   # seen before; a redacted notice can't erase it (V04)
        # the invite round is derived by the gate from the live chat (review R05); the flow doesn't claim one
        conversation_id, person_id = self.routes(conv.external_id)
        base = dict(channel='sideshift', conversation_id=conversation_id or 'unrouted', source_chat_id=conv.external_id,
                    person_id=person_id, creator_key=key, contract=contract, occurrence=contract['id'])   # merged (AU02)
        if checks.signing_seen(conv, contract):   # positive evidence only is recorded; unknown records are not (V04)
            self.journal.event(key, 'maybe-signed', contract['id'], {'status': status})
        if checks.maybe_accepted(conv, contract):
            self.check_handles(key, conv, contract)
        if checks.accepted(conv, contract):   # positive proof only: the contract is active
            # delivered = in the chat (even if deleted later) or a confirmed send in the journal (review AQ02)
            # definitely-unsent attempts are retried (AR01); any account ever linked to her counts (review CR01)
            states = [self.journal.delivery(f'gate:warmup-guide:{acct}') for acct in self.journal.component_accounts(key)]
            guide = 'sent' if 'sent' in states else ('unclear' if 'unclear' in states else 'none')
            delivered = (guide == 'sent' or any(WARMUP_DOC in m.text for m in conv.messages
                                                if m.direction == 'out' or m.author == 'us-unreadable')   # garbled ours too
                         or any(words and WARMUP_DOC in words   # sent by hand on another account of hers (review CS01)
                                for _, words, _ in self.journal.component_deliveries(key)))
            if not delivered and guide == 'unclear':
                self.journal.event(key, 'needs-captain', f'warmup-guide-unclear:{contract["id"]}',
                                   {'summary': 'warm-up guide send is unclear; check the chat and record it'})
                return [f'{name}: warm-up guide send unclear, waiting for a person']
            if not delivered:
                # promised "as soon as you sign" to everyone invited before the guide went with the contract
                d = self.gate.run(Action(message_type='warmup-guide', fields={'First': name},
                                         trigger=f'contract {contract["id"]} active, no guide in chat', **base))
                return [f'{name}: signed, no warm-up guide yet → warmup-guide {d.outcome} ({"; ".join(d.reasons)[:160]})']
            d = self.gate.run(Action(message_type='ask-app-email', fields={}, trigger=f'contract {contract["id"]} active', **base))
            return [f'{name}: signed → ask-app-email {d.outcome} ({"; ".join(d.reasons)[:160]})']
        if status != 'pending':
            return [f'{name}: contract {status}, nothing to do']
        if checks.maybe_accepted(conv, contract):
            return [f'{name}: linked handles, waiting for handle approval in SideShift (no reminders)']
        invited = checks.invite_time(conv, contract)
        if invited is None:
            return [f'{name}: no invite link from us found in the chat, needs a person']
        age = self.now() - invited
        if age >= WITHDRAW_AFTER:
            # not due before every "open N more hours" we told her has run out (review DI03)
            deadline = withdraw.close_after(checks.with_history(conv, self.journal.events(key)), invited, self.journal.delivered_texts(key))
            if deadline is None or self.now() < deadline:
                until = 'unknown, the captain decides' if deadline is None else f'{deadline:%Y-%m-%d %H:%M} UTC'
                return [f'{name}: invite past 24h, but we told her it stays open until {until}']
            self.journal.event(key, 'withdraw-due', f"{contract['id']}:{checks.invite_generation(conv, contract)}", {'invited': invited.isoformat()})
            uid = key.split(':', 1)[-1]
            def fresh_apps():   # rows read before a failed page still count as signing evidence (AD01)
                try:
                    return self.applications_by_creator().get(uid, [])
                except Exception as exc:
                    self.observe(key, contract, getattr(exc, 'partial', {}).get(uid, []))
                    raise
            fresh_apps = None if self.read_client is None else fresh_apps
            started = clock.Since(self.now)   # the identity read is evidence too: its age counts, asleep or not (CW01, DA01)
            held = self.identity_check(base)   # who she is in contacts, read now, before any withdrawal (review CV01)
            if held:
                self.journal.event(key, 'withdraw-held', f"{contract['id']}:{self.now():%Y-%m-%dT%H}", {'reasons': held})
                return [f'{name}: 24h → withdraw held ({"; ".join(held)[:200]})']
            outcome, reasons = withdraw.withdraw(contract['id'], self.fetch_contract, lambda: self.live.read(conv.external_id, list(conv.creator_ids)),
                                                 self.journal, key, self.now(), self.write_client, fresh_apps,
                                                 started=started)
            return [f'{name}: 24h → withdraw {outcome} ({"; ".join(reasons)[:200]})']
        # the warm-up guide always goes with the contract (captain, 2026-10-15): once per invite round, unless a
        # message of ours after this invite already carries it. Fresh invites only (the job runs every 15 minutes), so
        # invites from before this rule get their reminders as before
        guide_type = getattr(self.gate, 'types', {}).get('contract-invite')   # switch it off with mode: off
        if guide_type is not None and guide_type.effective_mode == 'auto' and age < timedelta(hours=checks.INVITE_AGE['invite_6h']) and not any(WARMUP_DOC in (m.text or '') and m.direction == 'out' and checks.ts(m.at) >= invited for m in conv.messages):
            d = self.gate.run(Action(message_type='contract-invite', fields={'First': name, 'first': (name or '').lower()},
                                     trigger=f'contract {contract["id"]} invited, no warm-up guide since', **base))
            return [f'{name}: invited → contract-invite with warm-up guide {d.outcome} ({"; ".join(d.reasons)[:160]})']
        for hours, message_type in reversed(REMINDERS):
            if age >= timedelta(hours=hours):
                d = self.gate.run(Action(message_type=message_type, fields={'First': name},
                                         trigger=f'contract {contract["id"]} invite age {age}', **base))
                return [f'{name}: {message_type} {d.outcome} ({"; ".join(d.reasons)[:160]})']
        return []


def contacts_routes(contacts):
    """SideShift chat id -> (contacts conversation id, person id). Duplicates or unclear people -> (None, None) (G01)."""
    by_external = {}
    for c in contacts.call('list_conversations', {'channel': 'sideshift'}):
        by_external.setdefault(c.get('external_id', '').split(':', 1)[-1], []).append(c['id'])

    def route(chat_id):
        ids = by_external.get(chat_id, [])
        if len(ids) != 1:
            return None, None
        detail = contacts.call('get_conversation', {'conversation_id': ids[0], 'limit': 1})
        people = {p.get('person_id') for p in detail.get('participants', []) if p.get('person_id')}
        return ids[0], (people.pop() if len(people) == 1 else None)
    return route


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='never send; use a throwaway copy of the real journal')
    args = ap.parse_args()
    from dotenv import load_dotenv
    load_dotenv(REPO / '.env')
    from client import Client
    from gate.contacts import ContactsMCP
    from gate.review import ClaudeReviewer

    class DrySender:
        def preflight(self, action):   # the real sender's pre-checks, so a dry run fails where a real one would
            if hasattr(contacts, 'preflight'):
                contacts.preflight(action)

        def send(self, action, text, key, authorized_by):
            print(f'  DRY RUN, would send to {action.creator_key}: {text!r}')
            return {'status': 'sent', 'id': 'dry-run'}

    if args.dry_run:   # a throwaway copy of the real journal: sees real history, leaves nothing behind
        import tempfile
        from gate.journal import snapshot
        journal = snapshot(Path(tempfile.mkdtemp(prefix='gate-dry-')) / 'gate.db')
    else:
        journal = Journal()
    contacts = ContactsMCP()
    live = SideShiftLive(Client(), COMPANY, on_notice=journal.remember_notice)   # durable notices from the first read (AJ01)
    contacts.live = live   # the sender re-reads the chat right before sending (review N01)
    contracts_client = Client(os.environ['SIDESHIFT_CONTRACTS_KEY'])

    def read_contract(contract_id):
        got = contracts_client.request('GET', f'/contracts/{contract_id}')
        return got.get('data', got) if isinstance(got, dict) else got
    read_key = os.environ.get('SIDESHIFT_READ_KEY')
    read_client = Client(read_key) if read_key else None

    def read_applications(uid):
        if read_client is None:
            raise RuntimeError('no SIDESHIFT_READ_KEY')
        return collect_applications(read_client, CAMPAIGN, uid,   # rows journaled as read; kept on a failed page (AE01, AH02)
                                    on_row=lambda owner, a: journal.remember_request(f'sideshift:{owner}', a))
    gate = Gate(policy.load(), live, ClaudeReviewer(), DrySender() if args.dry_run else contacts, journal,
                contract_reader=read_contract, applications_reader=read_applications)   # dry runs honor PAUSED (R19)
    write_key = None if args.dry_run else os.environ.get('SIDESHIFT_CONTRACTS_WRITE_KEY')
    flow = Flow(contracts_client, live, gate, journal, contacts_routes(contacts), read_client=read_client,
                write_client=Client(write_key) if write_key else None)
    for line in flow.run():
        print(line)


if __name__ == '__main__':
    main()
