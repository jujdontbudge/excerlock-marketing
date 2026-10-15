"""Assertions describe required safe behavior; each test fails on this snapshot."""
import sqlite3
from contextlib import ExitStack, contextmanager
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch

from gate.dispatch import Gate
from gate.journal import Busy
from gate.live import SideShiftLive
from gate.model import Decision, IN
from .support import (Case, NOW, Sender, StaticLive, RawClient, conversation, invite,
                               message, raw, policy)


class DispatchDefects(Case):
    def test_G01_recipient_route_is_not_bound_to_read_chat(self):
        g = self.gate()
        g.run(self.action(conversation_id='route-for-another-human', person_id='other-person',
                          creator_key='sideshift:OTHER'))
        self.assertEqual(g.sender.calls, [], 'Read U1 but dispatched to unverified OTHER route')

    def test_G01_group_chat_is_not_an_identity_proof(self):
        g = self.gate(conv=conversation(invite(), members=('U1', 'U2')))
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G02_producer_can_manufacture_a_captain_order(self):
        self.paused.touch()
        self.clock = NOW + timedelta(hours=12)
        t = replace(self.type, mode='off')
        g = self.gate(types_={'reminder': t})
        g.run(self.action(captain_order='captain approved (asserted by automated producer)'))
        self.assertEqual(g.sender.calls, [], 'No authenticated approval bound to this target/text')

    def test_G03_crash_after_provider_effect_leaves_key_unspent(self):
        # BaseException models process death, outside the Exception catch. The sender already accepted.
        sender = Sender(effect=lambda: (_ for _ in ()).throw(SystemExit('power loss')))
        g = self.gate(sender=sender)
        try:
            g.run(self.action())
        except SystemExit:
            pass
        # adapted 2026-10-15: the gate now adds the invite round it reads live (review R05) to the key
        keys = [r[0] for r in self.journal.conn.execute("SELECT idempotency_key FROM decisions WHERE outcome='dispatching'")]
        self.assertTrue(keys and all(self.journal.spent(k) for k in keys),
                        'No durable dispatching/uncertain intent survived the crash')

    def test_G03_record_failure_after_success_allows_retry(self):
        self.journal.conn.execute("CREATE TRIGGER fail_record BEFORE INSERT ON decisions BEGIN SELECT RAISE(FAIL, 'disk failure'); END")
        g = self.gate()
        try:
            g.run(self.action())
        except sqlite3.DatabaseError:
            pass
        self.journal.conn.execute('DROP TRIGGER fail_record')
        g.run(self.action())
        self.assertLessEqual(len(g.sender.calls), 1, 'Second dispatch after lost success record')

    def test_G04_key_is_rechecked_after_acquiring_lock(self):
        # B checked spent=False; A commits before B acquires. B must recheck under ownership.
        reserve = self.journal.reserve
        @contextmanager
        def interleave(cid, holder):
            self.journal.record(self.action(), 'gate:reminder:C1', Decision('sent', ['A completed'], 'different approved text'))
            with reserve(cid, holder):
                yield
        with patch.object(self.journal, 'reserve', interleave):
            g = self.gate()
            g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G04_same_occurrence_for_different_creators_collides(self):
        t = replace(self.type, id='captain-text', once='per_occurrence')
        g = self.gate()
        a = self.action(occurrence='onboarding-2026-10-14')
        b = replace(a, creator_key='sideshift:U2', source_chat_id='chat2', conversation_id='route2')
        self.assertNotEqual(g.key(t, a), g.key(t, b))

    def test_G05_expired_lease_does_not_fence_live_owner(self):
        j2 = self.new_journal()
        lease_clock = [1000]
        with ExitStack() as stack:
            def reviewer(*args):
                lease_clock[0] += 901  # owner suspended beyond the 900-second lease
                stack.enter_context(j2.reserve('route1', 'new-worker'))
                return 'SEND', 'old worker resumed', []
            g = self.gate(reviewer=reviewer)
            with patch('gate.journal.time.time', side_effect=lambda: lease_clock[0]):
                g.run(self.action())
        self.assertEqual(g.sender.calls, [], 'Old worker sends while new worker owns reservation')

    def test_G05_same_gate_holder_allows_nested_owners(self):
        blocked = False
        with self.journal.reserve('route1', 'same-instance'):
            try:
                with self.journal.reserve('route1', 'same-instance'):
                    pass
            except Busy:
                blocked = True
        self.assertTrue(blocked, 'Holder belongs to Gate instance, not one exclusive run')

    def test_G06_fingerprint_ignores_safety_fields(self):
        from gate.live import fingerprint
        for change in ({'senderUserId': 'STRANGER'}, {'attachmentCount': 1},
                       {'createdAt': '2026-10-14T15:59:00Z'}, {'senderExternalUserId': 'other'}):
            with self.subTest(change=change):
                self.assertNotEqual(fingerprint([raw()]), fingerprint([raw(**change)]))

    def test_G06_new_send_with_stale_source_ignores_local_gap(self):
        # SideShift publication lags contacts delivery; journal already has confirmed send at NOW.
        g = self.gate()
        g.run(self.action())
        g.run(self.action(occurrence='C2', fields={'First': 'Bea'}))
        self.assertEqual(len(g.sender.calls), 1, 'No journal-based confirmed-send gap for this route')

    def test_G06_second_read_new_attachment_or_unknown_sender_still_sends(self):
        client = RawClient([raw(senderUserId='U1')])
        source = SideShiftLive(client, 'COMPANY')
        def reviewer(*args):
            client.rows[0].update(senderUserId='STRANGER', attachmentCount=1)
            return 'SEND', 'reviewed old roles', []
        g = self.gate(source=source, reviewer=reviewer)
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G06_membership_change_is_invisible(self):
        client = RawClient([raw()])
        def reviewer(*args):
            client.members = ('U2',)
            return 'SEND', 'old member', []
        g = self.gate(source=SideShiftLive(client, 'COMPANY'), reviewer=reviewer)
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G07_review_crosses_quiet_hour_boundary(self):
        self.clock = NOW.replace(hour=0, minute=59) + timedelta(days=1)  # 20:59 Eastern
        def reviewer(*args):
            self.clock += timedelta(minutes=2)
            return 'SEND', 'ok', []
        g = self.gate(reviewer=reviewer)
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G07_pause_created_during_review_is_ignored(self):
        def reviewer(*args):
            self.paused.touch()
            return 'SEND', 'ok', []
        g = self.gate(reviewer=reviewer)
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G07_no_36h_dispatch_deadline(self):
        self.clock = NOW + timedelta(days=2)
        g = self.gate()
        # Same requirements as real reminders; producer timing is not a gate precondition.
        g.run(self.action())
        self.assertEqual(g.sender.calls, [], 'Unsigned pending contract is >36h old')

    def test_G08_stored_fallback_is_accepted_as_live(self):
        g = self.gate(source=SideShiftLive(RawClient([raw(source='stored')]), 'COMPANY'))
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G12_older_unexamined_attachment_is_ignored(self):
        c = conversation(message(id='image', direction=IN, text='', attachments=1),
                         *(message(id=f'thanks{i}', direction=IN, text='thanks') for i in range(6)))
        g = self.gate(conv=c)
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G12_attachment_array_without_count_is_ignored(self):
        g = self.gate(source=SideShiftLive(RawClient([raw(senderUserId='U1', content='',
                                                        attachments=[{'url': 'https://example.invalid/image'}])]), 'COMPANY'))
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G13_deleted_outgoing_does_not_answer_questions(self):
        from gate.checks import unanswered
        q = message(direction=IN, text='What do I upload?')
        c = conversation(q, message(id='deleted', deleted=True, text='obsolete answer'))
        self.assertEqual(unanswered(c), [q])

    def test_G13_unrelated_outgoing_does_not_answer_questions(self):
        from gate.checks import unanswered
        q = message(direction=IN, text='What do I upload?')
        self.assertEqual(unanswered(conversation(q, message(id='other', text='Have a nice day'))), [q])

    def test_G17_malformed_success_response_is_journaled(self):
        g = self.gate(sender=Sender(result='unexpected text response'))
        error = None
        try:
            g.run(self.action())
        except Exception as exc:
            error = exc
        self.assertIsNone(error, f'Malformed post-send response escaped before uncertain commit: {error}')

    def test_G17_already_used_uncertain_is_not_a_retryable_hold(self):
        g = self.gate(sender=Sender(result={'already_used': True, 'status': 'uncertain', 'id': 'existing'}))
        d = g.run(self.action())
        self.assertEqual(d.outcome, 'uncertain')
        self.assertTrue(self.journal.spent(d.idempotency_key))

    def test_G18_missing_person_burns_key_before_any_send(self):
        from .support import contacts_module
        sender = contacts_module.ContactsMCP.__new__(contacts_module.ContactsMCP)
        sender.call = lambda *a: {'status': 'sent', 'id': 'fixed'}
        g = self.gate(sender=sender)
        d = g.run(self.action(person_id=None))
        self.assertFalse(self.journal.spent(d.idempotency_key), 'Locally rejected before any request; repair should remain possible')

    def test_G26_dnc_has_no_gate_precondition(self):
        # A linked DNC fact is already durable; gate never consults journal facts or restrictions.
        self.journal.event('sideshift:U1', 'do-not-contact', 'captain-decision', {'enabled': True})
        g = self.gate()
        g.run(self.action())
        self.assertEqual(g.sender.calls, [])

    def test_G27_changes_after_last_read_are_unfenced(self):
        source = StaticLive()
        delivered = []
        class ConditionalSender:
            def send(self, action, text, key, auth, expected_fingerprint=None):
                source.conv = conversation(invite(), message(id='stop', direction=IN, text='Stop messaging me'), fp='changed')
                # Fake conditional provider: if no revision precondition is supplied, it delivers.
                if expected_fingerprint and expected_fingerprint != source.conv.fingerprint:
                    return {'status': 'failed', 'error': 'revision mismatch'}
                delivered.append(text)
                return {'status': 'sent', 'id': 'o1'}
        g = self.gate(source=source, sender=ConditionalSender())
        g.run(self.action())
        self.assertEqual(delivered, [], 'No conditional source revision travels to sender')
