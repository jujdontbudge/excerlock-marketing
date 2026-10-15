"""Round-five counterexamples. All transports are private offline fakes.
Run: python3 -m unittest discover -s out/tests -t .
"""
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch
import sys
import types
import unittest

from gate import checks
from gate.dispatch import DefiniteNoSend, text_hash
from gate.live import SideShiftLive
from gate.model import Decision, IN
from gate.tests.review4.support import Case, InboxCase, NOW, Live, Sender, contacts, conv, invite, msg, flow, grant, policy, propose, withdraw
import record


class InviteAndApplications(Case):
    def test_S01_genuine_reinvite_inside_repost_hour_must_not_be_withdrawn(self):
        chat = conv(invite('old', at=NOW - timedelta(hours=50)),
                    msg('approval', '✅ Your handle @old (tiktok) was approved for this contract.', at=NOW - timedelta(minutes=45)),
                    invite('captain-reinvited', at=NOW - timedelta(minutes=15)))
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or {'status': 'rejected'})
        withdraw.withdraw('C1', lambda cid: self.contract(applications=[]), lambda: chat,
                          self.j, 'sideshift:U1', NOW, writer, lambda: [])
        self.assertEqual(writes, [], 'A real 15-minute-old invite disappears inside the heuristic repost window')

    def test_S01_delayed_repost_must_not_erase_signing_evidence(self):
        chat = conv(invite('original', at=NOW - timedelta(hours=20)),
                    msg('signed', '📨 Requested handle @ada (tiktok) for this contract', direction=IN, at=NOW - timedelta(hours=19)),
                    msg('approval', '✅ Your handle @ada (tiktok) was approved for this contract.', at=NOW - timedelta(hours=18)),
                    invite('delayed-platform-repost', at=NOW - timedelta(hours=16)))
        self.assertTrue(checks.maybe_accepted(chat, self.contract()), 'Elapsed time is not evidence of a new business invite')

    def test_S02_unknown_required_applications_must_block_reminder(self):
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        sender = Sender()
        self.gate(types={t.id: t}, sender=sender).run(self.action(contract=self.contract(applications=None, applications_required=True)))
        self.assertEqual(sender.calls, [], 'not_accepted currently converts unknown coverage to no requests')

    def test_S02_contract_get_without_applications_must_not_reuse_stale_empty_evidence(self):
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        sender = Sender()
        # GET /contracts/C1 lacks application coverage; a request was made after the list snapshot.
        self.gate(types={t.id: t}, sender=sender, reader=lambda cid: self.contract()).run(
            self.action(contract=self.contract(applications=[], applications_required=True)))
        self.assertEqual(sender.calls, [], 'Fresh absence is not proof the cached empty application list is still current')

    def test_S02_missing_application_reader_is_unknown_for_withdrawal(self):
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or {'status': 'rejected'})
        withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(invite(at=NOW - timedelta(hours=40))),
                          self.j, 'sideshift:U1', NOW, writer)
        self.assertEqual(writes, [], 'With no reader and no applications field, withdrawal treats unknown as empty')

    def test_S03_slow_applications_read_must_not_leave_contract_check_stale(self):
        current = self.contract(applications=[])
        writes = []
        def apps():
            current['status'] = 'active'
            return []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or {'status': 'rejected'})
        withdraw.withdraw('C1', lambda cid: dict(current), lambda: conv(invite(at=NOW - timedelta(hours=40))),
                          self.j, 'sideshift:U1', NOW, writer, apps)
        self.assertEqual(writes, [], 'The contract becomes active during a potentially slow fresh applications fetch')

    def test_S04_withdrawal_response_for_other_contract_cannot_confirm_success(self):
        writer = SimpleNamespace(request=lambda *a, **kw: {'data': {'id': 'OTHER', 'contractorId': 'U2', 'status': 'rejected'}})
        outcome, _ = withdraw.withdraw('C1', lambda cid: self.contract(applications=[]),
                                      lambda: conv(invite(at=NOW - timedelta(hours=40))),
                                      self.j, 'sideshift:U1', NOW, writer, lambda: [])
        self.assertNotEqual(outcome, 'withdrawn', 'Status alone is not an identity-bound withdrawal receipt')


class DispatchBoundaries(Case):
    def test_S05_grant_gap_requires_fresh_route_preflight(self):
        t = policy.load()['app-access']
        blocked = [False]
        source = Live(conv(msg('email', 'ada@example.com', direction=IN)))
        delivered = []
        class CheckedSender(contacts.ContactsMCP):
            def __init__(inner):
                inner.live = source
            def call(inner, tool, args):
                if tool == 'get_conversation':
                    return {'id': args['conversation_id'], 'channel': 'sideshift', 'external_id': 'sideshift:chat1',
                            'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
                if tool == 'get_person':
                    return {'id': args['person_id'], 'handles': [], 'tags': ['do-not-contact'] if blocked[0] else []}
                if tool == 'send_message':
                    delivered.append(args)
                    return {'status': 'sent', 'id': 'out1'}
                raise AssertionError(tool)
        sender = CheckedSender()
        g = self.gate(types={t.id: t}, sender=sender, source=source)
        def granter(a):
            blocked[0] = True
            return True, 'confirmed'
        g.granter = granter
        g.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'}, contract=self.contract(status='active')))
        self.assertEqual(delivered, [], 'Final route/DNC check is before the slow grant; Contacts.send does not repeat it')

    def test_S05_grant_gap_requires_a_new_live_read_even_in_preview(self):
        t = policy.load()['app-access']
        source = Live(conv(msg('email', 'ada@example.com', direction=IN)))
        sender = Sender()
        g = self.gate(types={t.id: t}, sender=sender, source=source)
        def granter(a):
            source.conv = conv(msg('email', 'ada@example.com', direction=IN), msg('stop', 'Stop contacting me', direction=IN), fp='stop')
            return True, 'confirmed'
        g.granter = granter
        g.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'}, contract=self.contract(status='active')))
        self.assertEqual(sender.calls, [], 'Post-grant vetoes reuse the pre-grant conversation, so fake/dry senders approve stale chat')

    def test_S06_unversioned_legacy_spent_key_must_not_block_a_new_round_forever(self):
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        g = self.gate(types={t.id: t}, source=Live(conv(invite('new-round'))))
        a = self.action(contract=self.contract())
        self.j.record(a, g.key(t, a), Decision('sent', ['legacy round'], 'Old wording.'))
        d = g.run(a)
        self.assertTrue(d.idempotency_key.endswith(':new-round'), 'Resolve the live operation before deciding whether legacy evidence applies; ambiguous legacy history may still require reconciliation')

    def test_S07_definite_no_send_does_not_consume_captain_approval(self):
        t = replace(self.type, mode='off')
        aid = self.j.approve('sideshift:U1', t.id, 'C1', text_hash(t.text), 'send it')
        class TemporarySender(Sender):
            def send(inner, *a, **kw):
                raise DefiniteNoSend('chat changed before any request left')
        g = self.gate(types={t.id: t}, sender=TemporarySender())
        first = g.run(self.action(approval_id=aid))
        self.assertEqual(first.outcome, 'error')
        sender = Sender()
        g.sender = sender
        second = g.run(self.action(approval_id=aid))
        self.assertEqual(second.outcome, 'sent', 'Definitely unsent work permanently loses its only captain authorization')

    def test_S08_attempt_id_is_own_insert_not_later_connections_max(self):
        self.j = self.new_journal(self.root / 'attempt.db')
        other = self.new_journal(self.root / 'attempt.db')
        a = self.action()
        key = 'operation'
        original = self.j.record
        def interleaved_record(*args, **kw):
            original(*args, **kw)
            other.record(a, key, Decision('dispatching', ['worker B']))
        with patch.object(self.j, 'record', side_effect=interleaved_record):
            aid = self.j.begin_attempt(a, key, Decision('dispatching', ['worker A']))
        own = self.j.conn.execute('SELECT MIN(id) FROM decisions').fetchone()[0]
        self.assertEqual(aid, own, 'SELECT MAX returns B; A can release B and leave its own definitely-unsent intent stuck')

    @unittest.expectedFailure   # KNOWN LIMIT (2026-10-15), same as R08: any check-then-send has an instant between the
    # last lock check and the request; without a fence at SideShift it can't be closed. Documented in sections/inbox/README.md.
    def test_S09_lease_expiry_after_last_creator_owns_check_is_not_fenced(self):
        self.j = self.new_journal(self.root / 'lease.db')
        other = self.new_journal(self.root / 'lease.db')
        original = self.j.owns
        clock, calls = [1000.0], [0]
        sender = Sender()
        with ExitStack() as stack:
            stack.enter_context(patch('gate.journal.time.time', side_effect=lambda: clock[0]))
            def owns(key, holder):
                answer = original(key, holder)
                calls[0] += 1
                # adapted 2026-10-15 (CT02): each lock check now also covers her account group, so the final
                # check is call 6 (chat, creator, group x2); the limit is still the instant after it
                if calls[0] == 6:
                    clock[0] += 901
                    stack.enter_context(other.reserve(key, 'replacement'))
                return answer
            stack.enter_context(patch.object(self.j, 'owns', side_effect=owns))
            self.gate(sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'The stale worker still reaches the effect after a newer creator owner takes over')


class InboxBoundaries(InboxCase):
    def test_S10_uncovered_request_without_question_mark_stays_visible(self):
        t = policy.load()['app-access']
        a = self.action(message_type=t.id, fields={'email': 'ada@example.com'}, contract=self.contract(status='active'))
        key = self.gate(types={t.id: t}).key(t, a)
        self.j.record(a, key, Decision('sent', ['old email reply'], policy.render(t, a.fields)))
        self.run_inbox(items=[{'id': 'in1', 'channel': 'sideshift', 'conversation_id': 'route1',
                               'text': 'Please explain when I will be paid. My email is ada@example.com', 'person': {'name': 'Ada'}}])
        self.assertEqual(self.marked[0]['outcome'], 'escalated', 'Exact outgoing text plus no ASCII question mark does not prove inbound coverage')

    def test_S11_human_email_receipt_request_is_not_automated(self):
        self.run_inbox(items=[{'id': 'in1', 'channel': 'email', 'conversation_id': 'route1',
                               'text': 'Please send the receipt for my payment', 'person': {'name': 'Ada'}}],
                       proposals=[{'message_id': 'in1', 'action': 'ignore', 'reason': 'receipt'}])
        self.assertEqual(self.marked[0]['outcome'], 'escalated', 'A topic word is not trusted automated-sender evidence')

    def test_S12_malformed_channel_diagnostic_does_not_starve_next_message(self):
        items = [{'id': 'in1', 'channel': None, 'conversation_id': 'route1'},
                 {'id': 'in2', 'channel': 'sideshift', 'conversation_id': 'route1'}]
        self.no_crash(lambda: self.run_inbox(items=items, proposals=[{'message_id': x['id'], 'action': 'escalate'} for x in items]))
        self.assertIn('in2', [m['message_id'] for m in self.marked], 'Diagnostic format outside try crashes on channel=None')

    def test_S12_null_list_item_does_not_starve_next_message(self):
        self.no_crash(lambda: self.run_inbox(items=[None, {'id': 'in2', 'channel': 'sideshift', 'conversation_id': 'route1'}],
                                           proposals=[{'message_id': 'in2', 'action': 'escalate'}]))
        self.assertIn('in2', [m['message_id'] for m in self.marked], 'Claim/list extraction still precedes per-item validation')


class GrantAndEvidence(Case):
    def test_S13_none_for_other_account_cannot_authorize_mutation(self):
        calls = []
        def runner(args, **kw):
            calls.append(args[1])
            return SimpleNamespace(returncode=0, stdout='NONE: other@example.com' if args[1] == 'check' else 'GRANTED: ada@example.com', stderr='')
        grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner)
        self.assertNotIn('grant', calls, 'NONE prefix is the one status still not bound to the checked recipient')

    def test_S14_revoked_premium_must_not_use_historical_receipt(self):
        replies = iter(['ACTIVE: ada@example.com', 'NONE: ada@example.com', 'GRANTED: ada@example.com'])
        calls = []
        def runner(args, **kw):
            calls.append(args[1])
            return SimpleNamespace(returncode=0, stdout=next(replies), stderr='')
        self.assertTrue(grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner)[0])
        # Premium was revoked after the first confirmed operation; a later notification must verify it.
        grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner)
        self.assertGreaterEqual(calls.count('check'), 2, 'An append-only historic grant is treated as current entitlement forever')

    def test_S15_attachment_count_without_identity_cannot_inherit_looked_at_authority(self):
        raw = dict(id='image', createdAt=(NOW - timedelta(hours=10)).isoformat(), senderUserId='U1', content='Draft', attachmentCount=1)
        class Client:
            def pages(inner, path):
                return [{'id': 'chat1', 'members': ['COMPANY', 'U1']}] if path == '/conversations' else [raw]
        source = SideShiftLive(Client(), 'COMPANY')
        old = source.read('chat1').messages[0]
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(old), {'by': 'captain'})
        raw['updatedAt'] = NOW.isoformat()  # same count/text, attachments replaced; provider omitted identities
        sender = Sender()
        self.gate(source=source, sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'Count-only attachments have no revision identity; the old review authorizes all replacements')

    def test_S16_attachment_signed_url_refresh_is_not_a_new_image(self):
        raw = dict(id='image', createdAt=(NOW - timedelta(hours=10)).isoformat(), senderUserId='U1', content='Draft',
                   attachments=[{'id': 'stable-image', 'url': 'https://cdn/image?signature=first'}])
        class Client:
            def pages(inner, path):
                return [{'id': 'chat1', 'members': ['COMPANY', 'U1']}] if path == '/conversations' else [raw]
        source = SideShiftLive(Client(), 'COMPANY')
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(source.read('chat1').messages[0]), {'by': 'captain'})
        raw['attachments'][0]['url'] = 'https://cdn/image?signature=refreshed'
        self.assertEqual(checks.completeness(source.read('chat1'), self.j.flags('sideshift:U1', 'attachment-reviewed')), [],
                         'Hashing transport metadata reopens the same reviewed image every URL refresh')

    def test_S17_ambiguous_message_prefix_cannot_mark_arbitrary_message(self):
        chat = conv(msg('abcdef-one', 'What is my rate?', direction=IN), msg('abcdef-two', 'What do I film?', direction=IN))
        client_module = types.ModuleType('client')
        client_module.Client = lambda *a: SimpleNamespace(pages=lambda *a, **kw: [])
        dotenv = types.ModuleType('dotenv')
        dotenv.load_dotenv = lambda *a: None
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client_module, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline'}))
            stack.enter_context(patch.object(record, 'find_creator', return_value=('U1', 'Ada', 'chat1')))
            stack.enter_context(patch.object(record, 'Journal', return_value=self.j))
            stack.enter_context(patch('gate.live.SideShiftLive', return_value=Live(chat)))
            stack.enter_context(patch.object(sys, 'argv', ['record.py', 'answered', 'Ada', 'abcdef']))
            stack.enter_context(redirect_stdout(StringIO()))
            record.main()
        self.assertEqual(self.j.flags('sideshift:U1', 'answered'), set(), 'Ambiguous prefix grants authority to the first matching question')


class JournalCompatibility(Case):
    def test_S18_pre_upgrade_definite_no_send_does_not_become_a_permanent_open_attempt(self):
        path = self.root / 'legacy.db'
        self.j = self.new_journal(path)
        a = self.action()
        key = self.gate().key(self.type, a)
        self.j.record(a, key, Decision('dispatching', ['about to send']))
        # Exact pre-upgrade record shape: one intent, then a definite-no-send result.
        self.j.record(a, key, Decision('error', ['not sent: no linked person for this chat']))
        upgraded = self.new_journal(path)  # exercise initialization/migration against persisted history
        self.assertFalse(upgraded.spent(key), 'No migration links pre-upgrade errors to their known unsent attempts')


class CrossCreatorGrant(Case):
    def test_S19_one_email_has_one_mutation_owner_across_creators(self):
        mutations = []
        def second_runner(args, **kw):
            if args[1] == 'check':
                return SimpleNamespace(returncode=0, stdout='NONE: shared@example.com', stderr='')
            mutations.append('U2')
            return SimpleNamespace(returncode=0, stdout='GRANTED: shared@example.com', stderr='')
        def first_runner(args, **kw):
            if args[1] == 'check':
                return SimpleNamespace(returncode=0, stdout='NONE: shared@example.com', stderr='')
            mutations.append('U1')
            # A second valid creator supplies the same email while U1's remote grant is in flight.
            grant.grant(self.j, 'sideshift:U2', 'shared@example.com', 'other creator', second_runner)
            return SimpleNamespace(returncode=0, stdout='GRANTED: shared@example.com', stderr='')
        grant.grant(self.j, 'sideshift:U1', 'shared@example.com', 'creator one', first_runner)
        self.assertEqual(len(mutations), 1, 'Grant-intent uniqueness is creator+email, not the shared external account')
