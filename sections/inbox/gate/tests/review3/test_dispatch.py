"""Assertions express required behavior; failures demonstrate review findings."""
from dataclasses import replace
from contextlib import ExitStack
from datetime import timedelta
from unittest.mock import patch

from gate.dispatch import DefiniteNoSend, text_hash
from gate.model import Decision, IN
from .support import Case, NOW, Live, Sender, contacts, conv, invite, msg, policy


class Dispatch(Case):
    def test_N01_lease_lost_after_final_check_cannot_dispatch(self):
        self.j = self.new_journal(self.root / 'shared.db')
        other = self.new_journal(self.root / 'shared.db')
        clock = [1000.0]
        original = self.j.record
        sender = Sender()
        with ExitStack() as stack:
            stack.enter_context(patch('gate.journal.time.time', side_effect=lambda: clock[0]))
            def record(action, key, decision, text=''):
                if decision.outcome == 'dispatching':
                    # Suspension immediately after owns() succeeds, before the intent commit.
                    clock[0] += 901
                    stack.enter_context(other.reserve(action.conversation_id, 'new-owner'))
                return original(action, key, decision, text)
            stack.enter_context(patch.object(self.j, 'record', side_effect=record))
            self.gate(sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'Expired owner sends while another worker holds the same chat')

    def test_N01_real_contacts_transport_discards_revision(self):
        source = Live()
        delivered = []
        sender = contacts.ContactsMCP.__new__(contacts.ContactsMCP)
        sender.preflight = lambda action: None
        def call(tool, args):
            source.conv = conv(invite(), msg('stop', 'Stop contacting me', direction=IN), fp='changed')
            delivered.append(args)
            return {'status': 'sent', 'id': 'out1'}
        sender.call = call
        self.gate(sender=sender, source=source).run(self.action())
        self.assertEqual(delivered, [], 'Actual ContactsMCP.send ignores expected_fingerprint and delivers after stop')

    def test_N06_approval_expiry_is_rechecked_at_consumption(self):
        clock = [1000.0]
        with patch('gate.journal.time.time', side_effect=lambda: clock[0]):
            aid = self.j.approve('sideshift:U1', 'example', 'C1', text_hash(self.type.text), 'send once', ttl=10)
            def review(*a):
                clock[0] = 1011.0
                return 'SEND', 'old approval expired', []
            sender = Sender()
            self.gate(sender=sender, reviewer=review, types={'example': replace(self.type, mode='off')}).run(self.action(approval_id=aid))
        self.assertEqual(sender.calls, [], 'Expired approval still overrides type off/pause/quiet hours')

    def test_N06_approval_hash_binds_exact_bytes(self):
        aid = self.j.approve('sideshift:U1', 'example', 'C1', text_hash('Approved  message.'), 'these exact words')
        self.assertFalse(self.j.approval_valid(aid, 'sideshift:U1', 'example', 'C1', text_hash('Approved message.')))

    def test_N06_approval_does_not_transfer_to_new_invite_round(self):
        t = replace(self.type, mode='off', requires=('contract_open', 'not_accepted'))
        source = Live(conv(invite('old', at=NOW - timedelta(hours=20))))
        sender = Sender()
        g = self.gate(source=source, sender=sender, types={'example': t}, reviewer=lambda *a: ('HOLD', 'wait', []))
        aid = self.j.approve('sideshift:U1', t.id, 'C1', text_hash(t.text), 'send for the old invite')
        g.run(self.action(approval_id=aid, contract=self.contract(inviteGeneration='old')))
        source.conv = conv(invite('new', at=NOW - timedelta(hours=1)))
        g.reviewer = lambda *a: ('SEND', 'ok', [])
        g.run(self.action(approval_id=aid, contract=self.contract(inviteGeneration='new')))
        self.assertEqual(sender.calls, [], 'Approval from a held old round authorizes the new round')

    def test_N07_definite_no_send_can_retry_without_integrity_crash(self):
        class Repairable(Sender):
            def send(self, *a, **kw):
                if not self.calls:
                    self.calls.append('definitely no request left')
                    raise DefiniteNoSend('repairable local issue')
                return super().send(*a, **kw)
        sender = Repairable()
        g = self.gate(sender=sender)
        self.assertEqual(g.run(self.action()).outcome, 'error')
        result, error = self.no_crash(lambda: g.run(self.action()))
        self.assertIsNone(error, error)
        self.assertEqual(result.outcome, 'sent')

    def test_N08_unrelated_old_error_cannot_release_new_intent(self):
        a = self.action()
        key = self.gate().key(self.type, a)
        # An old-schema error predates the durable-intent implementation.
        self.j.record(a, key, Decision('error', ['pre-upgrade definite failure']))
        self.j.record(a, key, Decision('dispatching', ['new attempt; process died after network I/O']))
        self.assertTrue(self.j.spent(key), 'Counting errors releases an unrelated later crashed intent')

    def test_N09_released_no_send_intent_is_not_a_recent_send(self):
        a = self.action()
        key = self.gate().key(self.type, a)
        # adapted 2026-10-15: a release names its attempt (review R02 requires it); the gate always writes it so
        attempt = self.j.begin_attempt(a, key, Decision('dispatching', ['attempt']))
        self.j.record(a, key, Decision('error', [f'attempt:{attempt}', 'definitely no send']))
        self.assertEqual(self.j.recent_sends(a.conversation_id, a.creator_key), [], 'Unsent attempt postpones other work')

    def test_N10_missing_contract_owner_is_not_positive_binding(self):
        sender = Sender()
        active = {'id': 'C1', 'status': 'active'}
        self.gate(sender=sender, types=policy.load(), reader=lambda cid: active).run(
            self.action(message_type='ask-app-email', contract=active))
        self.assertEqual(sender.calls, [], 'Contract without contractorId supplies positive acceptance')

    def test_N10_fresh_contract_id_must_match_requested_id(self):
        sender = Sender()
        self.gate(sender=sender, types=policy.load(), reader=lambda cid: self.contract(id='OTHER', status='active')).run(
            self.action(message_type='ask-app-email', contract=self.contract(status='active')))
        self.assertEqual(sender.calls, [], 'Same status and owner conceal wrong contract response')

    def test_N10_route_requires_exact_external_chat_identity(self):
        sender = contacts.ContactsMCP.__new__(contacts.ContactsMCP)
        sender.call = lambda tool, args: (
            {'external_id': 'sideshift:other-chat1', 'channel': 'sideshift',
             'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
            if tool == 'get_conversation' else {'tags': []})
        with self.assertRaises(DefiniteNoSend):
            sender.preflight(self.action(source_chat_id='chat1'))

    def test_N11_dnc_changed_during_review_is_rechecked_in_contacts(self):
        tags = []
        sender = contacts.ContactsMCP.__new__(contacts.ContactsMCP)
        sent = []
        def call(tool, args):
            if tool == 'get_conversation':
                return {'id': args['conversation_id'], 'external_id': 'sideshift:chat1', 'channel': 'sideshift',
                        'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
            if tool == 'get_person':
                return {'id': args['person_id'], 'handles': [], 'tags': list(tags)}
            sent.append(args)
            return {'status': 'sent', 'id': 'out1'}
        sender.call = call
        def review(*a):
            tags.append('do-not-contact')
            return 'SEND', 'restriction changed while reviewing', []
        self.gate(sender=sender, reviewer=review).run(self.action())
        self.assertEqual(sent, [], 'Contacts preflight happens only before the slow reviewer')

    def test_N12_answered_flag_does_not_cover_edited_message(self):
        from gate import checks
        self.j.event('sideshift:U1', 'answered', 'q', {'by': 'captain'})
        edited = msg('q', 'Thanks. New question: what do I film?', direction=IN)
        self.assertEqual(checks.unanswered(conv(edited), self.j.flags('sideshift:U1', 'answered')), [edited])

    def test_N12_reviewed_attachment_does_not_cover_replacement_attachment(self):
        self.j.event('sideshift:U1', 'attachment-reviewed', 'image', {'by': 'captain'})
        sender = Sender()
        source = Live(conv(msg('image', 'Replaced image', direction=IN, attachments=2)))
        self.gate(sender=sender, source=source).run(self.action())
        self.assertEqual(sender.calls, [], 'Review of the old attachment ID blesses new unseen media')

    def test_N13_unrelated_captain_text_does_not_answer_every_question(self):
        from gate import checks
        q = msg('q', 'What is the rate? What should I film?', direction=IN)
        captain = msg('c', 'Have a nice day', author='captain', at=NOW - timedelta(hours=9))
        self.assertEqual(checks.unanswered(conv(q, captain)), [q])

    def test_N14_reply_receipt_uses_source_message_id_not_contacts_id(self):
        from gate import checks
        source_q = msg('sideshift-source-id', 'Which login email? ada@example.com', direction=IN)
        self.grant_receipt()
        g = self.gate(types=policy.load(), source=Live(conv(source_q)))
        g.granter = lambda action: (True, 'GRANTED: ada@example.com')   # adapted 2026-10-15: live check required (S14)
        d = g.run(self.action(message_type='app-access', fields={'email': 'ada@example.com'},
                              occurrence='contacts-message-id', contract=self.contract(status='active')))
        self.assertEqual(d.outcome, 'sent')
        self.assertEqual(checks.unanswered(conv(source_q), self.j.flags('sideshift:U1', 'answered')), [],
                         'Producer uses contacts message IDs but live unanswered() uses SideShift IDs')

    def test_N15_invalid_fresh_contract_result_becomes_hold(self):
        g = self.gate(reader=lambda cid: None)
        result, error = self.no_crash(lambda: g.run(self.action()))
        self.assertIsNone(error, error)
        self.assertEqual(result.outcome, 'held')
