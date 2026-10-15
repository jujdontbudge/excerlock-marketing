import unittest
from contextlib import ExitStack
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch

from gate import checks
from gate.dispatch import Gate, text_hash
from gate.live import SideShiftLive
from gate.model import Decision, IN
from .support import Case, NOW, Live, Sender, contacts, conv, invite, msg, policy


class GateBoundaries(Case):
    def test_R01_per_creator_intent_claim_is_atomic_across_chats(self):
        self.j = self.new_journal(self.root / 'shared.db')
        other = self.new_journal(self.root / 'shared.db')
        t = replace(self.type, once='per_creator')
        sender = Sender()
        second = Gate({'example': t}, Live(conv(chat='chat2')), lambda *a: ('SEND', 'ok', []), sender,
                      other, now=lambda: NOW, paused_file=self.paused)
        original = self.j.record
        nested = []
        def record(action, key, decision, text=''):
            if decision.outcome == 'dispatching' and not nested:
                nested.append(second.run(self.action(conversation_id='route2', source_chat_id='chat2')))
            return original(action, key, decision, text)
        with patch.object(self.j, 'record', side_effect=record):
            self.gate(types={'example': t}, sender=sender).run(self.action())
        self.assertEqual(len(sender.calls), 1, 'Both SQLite connections send the same once-per-creator operation')

    def test_R02_error_from_older_attempt_cannot_release_new_crashed_attempt(self):
        a = self.action()
        key = self.gate().key(self.type, a)
        self.j.record(a, key, Decision('dispatching', ['attempt A']))
        self.j.record(a, key, Decision('error', ['A definitely did not send']))
        self.j.record(a, key, Decision('dispatching', ['attempt B crashed after I/O']))
        self.j.record(a, key, Decision('error', ['late duplicate outcome for A']))
        self.assertTrue(self.j.spent(key), 'Pairing by stack position treats an unrelated error as release authority')

    def test_R02_unrelated_error_cannot_remove_recent_uncertain_effect(self):
        a = self.action()
        key = self.gate().key(self.type, a)
        for d in (Decision('dispatching', ['A']), Decision('error', ['A']),
                  Decision('dispatching', ['B crashed']), Decision('error', ['late A'])):
            self.j.record(a, key, d)
        self.assertTrue(self.j.recent_sends(a.conversation_id, a.creator_key), 'Open B must still impose the gap')

    def test_R03_question_before_unrelated_captain_message_still_vetoes_gate(self):
        q = msg('q', 'What is my rate?', direction=IN)
        c = msg('captain', 'Have a nice day', author='captain', at=NOW - timedelta(hours=9))
        sender = Sender()
        self.gate(source=Live(conv(q, c)), sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'unanswered() is repaired, but the gate filters its result away')

    def test_R03_same_timestamp_question_after_captain_still_vetoes_gate(self):
        c = msg('c', 'Hello', author='captain')
        q = msg('q', 'What is my rate?', direction=IN)
        sender = Sender()
        self.gate(source=Live(conv(c, q)), sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'Strict timestamp comparison erases a tied question despite source order')

    def test_R04_attachment_replacement_with_same_count_requires_new_review(self):
        raw = dict(id='image', createdAt=(NOW - timedelta(hours=10)).isoformat(),
                   senderUserId='U1', content='My draft', attachments=[{'id': 'old', 'url': 'old.png'}])
        class Client:
            def pages(inner, path):
                return [{'id': 'chat1', 'members': ['COMPANY', 'U1']}] if path == '/conversations' else [raw]
        source = SideShiftLive(Client(), 'COMPANY')
        seen = source.read('chat1')
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(seen.messages[0]), {'by': 'captain'})
        raw['attachments'] = [{'id': 'replacement', 'url': 'new.png'}]
        changed = source.read('chat1')
        self.assertNotEqual(seen.fingerprint, changed.fingerprint)
        sender = Sender()
        self.gate(source=source, sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'Marks retain only text and count; the replacement is blessed forever')

    def test_R05_current_generation_must_be_derived_from_live_chat(self):
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        action = self.action(contract=self.contract(inviteGeneration='invented-round'))
        g = self.gate(types={'example': t}, source=Live(conv(invite('real-round'))))
        result = g.run(action)
        self.assertTrue(result.outcome == 'held' or result.idempotency_key.endswith(':real-round'),
                        'An arbitrary producer generation becomes durable operation identity')

    def test_R05_old_round_approval_cannot_override_off_type_for_live_new_round(self):
        t = replace(self.type, mode='off', requires=('contract_open', 'not_accepted'))
        aid = self.j.approve('sideshift:U1', t.id, 'C1', text_hash(t.text), 'old invite only')
        self.assertTrue(self.j.approval_valid(aid, 'sideshift:U1', t.id, 'C1', text_hash(t.text), 'old'))
        sender = Sender()
        source = Live(conv(invite('old', at=NOW - timedelta(hours=20)), invite('new', at=NOW - timedelta(hours=1))))
        self.gate(types={'example': t}, source=source, sender=sender).run(
            self.action(approval_id=aid, contract=self.contract(inviteGeneration='old')))
        self.assertEqual(sender.calls, [], 'Generation pinned in the approval is never compared with the live invite')

    def test_R06_post_grant_pause_is_rechecked_before_send(self):
        t = policy.load()['app-access']
        sender = Sender()
        g = self.gate(types={t.id: t}, sender=sender,
                      source=Live(conv(msg('email', 'ada@example.com', direction=IN))))
        def granter(action):
            self.paused.touch()  # allowed check/grant can take several 60-second subprocesses
            return True, 'confirmed'
        g.granter = granter
        g.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'}, contract=self.contract(status='active')))
        self.assertEqual(sender.calls, [], 'The new grant step invalidates the final switch check')

    def test_R06_post_grant_cancelled_contract_is_rechecked_before_send(self):
        current = self.contract(status='active')
        t = policy.load()['app-access']
        sender = Sender()
        g = self.gate(types={t.id: t}, sender=sender, reader=lambda cid: dict(current),
                      source=Live(conv(msg('email', 'ada@example.com', direction=IN))))
        def granter(action):
            current['status'] = 'cancelled'
            return True, 'confirmed'
        g.granter = granter
        g.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'}, contract=dict(current)))
        self.assertEqual(sender.calls, [], 'Contract remains trusted across the slow grant step')

    def test_R07_final_contract_read_must_not_overwrite_new_application_evidence(self):
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        fresh = self.contract(applications=[{'id': 'req', 'status': 'pending', 'requestedAt': NOW.isoformat()}])
        sender = Sender()
        self.gate(types={t.id: t}, sender=sender, reader=lambda cid: fresh).run(
            self.action(contract=self.contract(applications=[])))
        self.assertEqual(sender.calls, [], 'Fresh handle requests are overwritten with the old empty list')

    @unittest.expectedFailure   # KNOWN LIMIT (2026-10-15): SideShift has no conditional send. A creator message that
    # lands after the sender's final live read but before delivery cannot be fenced by any client. The final read is
    # the last moment before the request leaves; this test documents the residual risk (review G27, N01, R08).
    def test_R08_actual_transport_still_has_unconditional_read_send_race(self):
        source = Live()
        sender = contacts.ContactsMCP.__new__(contacts.ContactsMCP)
        sender.live = source
        sender.preflight = lambda action: None
        delivered = []
        def call(tool, args):
            # A stop arrives after all three reads but before the remote send is delivered.
            source.conv = conv(invite(), msg('stop', 'Stop contacting me', direction=IN), fp='stop')
            delivered.append(args)
            return {'status': 'sent', 'id': 'out1'}
        sender.call = call
        self.gate(sender=sender, source=source).run(self.action())
        self.assertEqual(delivered, [], 'An extra local read is not a provider-side revision fence')

    def test_R08_lease_can_expire_after_new_post_intent_ownership_check(self):
        self.j = self.new_journal(self.root / 'lease.db')
        other = self.new_journal(self.root / 'lease.db')
        original = self.j.owns
        clock = [1000.0]
        calls = [0]
        sender = Sender()
        with ExitStack() as stack:
            stack.enter_context(patch('gate.journal.time.time', side_effect=lambda: clock[0]))
            def owns(chat, holder):
                answer = original(chat, holder)
                calls[0] += 1
                if calls[0] == 2:
                    clock[0] += 901
                    stack.enter_context(other.reserve(chat, 'replacement'))
                return answer
            stack.enter_context(patch.object(self.j, 'owns', side_effect=owns))
            self.gate(sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'The old worker sends under the replacement worker reservation')
