"""Offline counterexamples. Assertions state the required behavior and intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
Uses actual gate/transport/journal code, private SQLite databases and fake services only.
"""
from dataclasses import replace
from datetime import timedelta
import threading
import unittest
import time
from types import SimpleNamespace
from unittest.mock import patch

from gate.journal import Journal
from gate.model import Decision, IN
from gate.tests.review4.support import Case, NOW, Live, conv, invite, msg, policy, withdraw
from gate.tests.review7.test_round7 import CheckedSender


class SigningObservations(Case):
    def changed_read(self, target):
        """A request is seen exactly once, then redacted. Later reminders must still stop."""
        base = conv(invite(at=NOW - timedelta(hours=7)))
        positive = conv(*base.messages, msg('request', '📨 Requested 2 handles for this contract.',
                                            direction=IN, at=NOW), fp='new-request')
        reads = []

        class Source(Live):
            def read(inner, *a, **kw):
                reads.append(1)
                return positive if len(reads) == target else base

        source = Source(base)
        sender = CheckedSender(source)
        types = policy.load()
        g = self.gate(types=types, source=source, sender=sender, reader=lambda cid: self.contract())
        g.applications_reader = lambda uid: []
        first = g.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'}))
        self.assertEqual(len(reads), target)
        self.assertNotEqual(first.outcome, 'sent')
        self.assertEqual(sender.delivered, [])
        # Six hours later, at invite age 13h, the second reminder is due and the notice is gone.
        g.now = lambda: NOW + timedelta(hours=6)
        second = g.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'Read {target} saw signing but did not retain it; later reminder {second.outcome}')

    def test_Z01_changed_review_reread_retains_signing(self):
        self.changed_read(2)

    def test_Z01_changed_transport_read_retains_signing(self):
        self.changed_read(3)

    def test_Z01_changed_last_read_retains_signing(self):
        self.changed_read(4)

    def test_Z01_draft_spent_key_still_retains_observed_signing_before_withdrawal(self):
        t = replace(policy.load()['contract-reminder-1'], mode='draft')
        old = invite(at=NOW - timedelta(hours=7))
        source = Live(conv(old, msg('request', '📨 Requested 2 handles for this contract.', direction=IN, at=NOW)))
        g = self.gate(types={t.id: t}, source=source, reader=lambda cid: self.contract())
        g.applications_reader = lambda uid: []
        a = self.action(message_type=t.id, fields={'First': 'Ada'},
                        contract=self.contract(inviteGeneration=old.id))
        self.j.record(a, g.key(t, a), Decision('sent', ['earlier reminder'], 'Earlier reminder'))
        held = g.run(a)
        self.assertEqual(held.reasons, ['already sent (idempotency key spent)'])
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append(kw) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(old), self.j,
                                   'sideshift:U1', NOW + timedelta(hours=33), writer, lambda: [])
        self.assertEqual(writes, [], f'Draft gate read signing before its spent-key veto; later {result}')

    def test_Z01_withdraw_keeps_positive_application_when_contract_read_fails(self):
        old = conv(invite(at=NOW - timedelta(hours=40)))
        request = {'id': 'req1', 'status': 'pending', 'requestedAt': (NOW - timedelta(hours=1)).isoformat()}
        first = withdraw.withdraw('C1', lambda cid: None, lambda: old, self.j, 'sideshift:U1', NOW,
                                  read_applications=lambda: [request])
        self.assertEqual(first[0], 'held')
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append(kw) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        second = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: old, self.j,
                                    'sideshift:U1', NOW + timedelta(hours=3), writer, lambda: [])
        self.assertEqual(writes, [], f'Positive application discarded on failed contract read; later {second}')


class JournalWaits(Case):
    def contended_database(self):
        """The test writer is a real second WAL connection; its wait exceeds the documented 10s span."""
        path = self.root / 'contention.db'
        self.j = self.new_journal(path)
        acquired, release = threading.Event(), threading.Event()
        errors, workers = [], []

        def start(change):
            def writer():
                other = Journal(path)
                try:
                    other.conn.execute('BEGIN IMMEDIATE')
                    change()
                    acquired.set()
                    release.wait(11.0)
                    other.conn.execute('COMMIT')
                except BaseException as exc:
                    errors.append(exc)
                    acquired.set()
                finally:
                    other.conn.close()
            worker = threading.Thread(target=writer)
            workers.append(worker)
            worker.start()
            if not acquired.wait(5):
                raise AssertionError('Test writer did not acquire the transaction')

        def finish():
            release.set()
            for worker in workers:
                worker.join(5)
            self.assertEqual(errors, [])

        self.addCleanup(finish)
        return start

    def test_Z02_final_signing_journal_write_cannot_outlive_send_evidence(self):
        # 2026-10-15 (CI01): the final read now records its observation time, which waits on the lock inside the
        # evidence window, so the span check holds; this case is no longer an accepted limit
        """Adapted 2026-10-15: after the Z01/Z02 fixes no journal write sits between the final reads and the request
        (_observe writes only new facts; the span is checked after every journal call). Traced: send_message leaves at
        0.0s; the 11s wait this test measures is the 'sent' record written AFTER delivery. The cancellation lands
        during the final chat read, inside the accepted 10-second evidence window (README "Known limits")."""
        start = self.contended_database()
        current, reads = self.contract(status='active'), []

        class Source(Live):
            def read(inner, *a, **kw):
                reads.append(1)
                if len(reads) == 4:  # after final contract GET, immediately before span check and _vetoes
                    start(lambda: current.update(status='cancelled'))
                return inner.conv

        source = Source()
        sender = CheckedSender(source)
        t = policy.load()['warmup-guide']
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: dict(current))
        begun = time.monotonic()
        result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'}, contract=dict(current)))
        self.assertGreater(time.monotonic() - begun, 10)
        self.assertEqual(current['status'], 'cancelled')
        self.assertEqual(sender.delivered, [],
                         f'Timer passes before _vetoes writes maybe-signed and blocks 11s; {result.outcome}')

    def test_Z02_withdraw_intent_lock_wait_cannot_outlive_evidence(self):
        start = self.contended_database()
        current, writes = self.contract(), []
        real_event = self.j.event

        def event(creator, kind, ref, data):
            if kind == 'withdraw-intent':  # all remote reads and SPAN check already finished
                start(lambda: current.update(status='active'))
            return real_event(creator, kind, ref, data)

        writer = SimpleNamespace(request=lambda *a, **kw: writes.append(kw) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        begun = time.monotonic()
        with patch.object(self.j, 'event', side_effect=event):
            result = withdraw.withdraw('C1', lambda cid: dict(current),
                                       lambda: conv(invite(at=NOW - timedelta(hours=40))), self.j,
                                       'sideshift:U1', NOW, writer, lambda: [])
        self.assertGreater(time.monotonic() - begun, 10)
        self.assertEqual(current['status'], 'active')
        self.assertEqual(writes, [], f'withdraw-intent blocks 11s after SPAN check, then rejects active contract: {result}')


class ContactsEvidence(Case):
    def test_Z03_dnc_preflight_must_not_age_out_during_transport_read(self):
        clock, reads, blocked, person_checks = [1000.0], [], [False], []

        class Source(Live):
            def read(inner, *a, **kw):
                reads.append(1)
                if len(reads) == 3:  # ContactsMCP's own potentially slow membership/history fetch
                    blocked[0] = True
                    clock[0] += 45.0
                return inner.conv

        class Sender(CheckedSender):
            def call(inner, tool, args):
                if tool == 'get_person':
                    person_checks.append(clock[0])
                    return {'id': args['person_id'], 'handles': [], 'tags': ['do-not-contact'] if blocked[0] else []}
                return super().call(tool, args)

        source = Source()
        sender = Sender(source)
        t = policy.load()['warmup-guide']
        g = self.gate(types={t.id: t}, source=source, sender=sender,
                      reader=lambda cid: self.contract(status='active'))
        g.now = lambda: NOW + timedelta(seconds=clock[0] - 1000)
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'}, contract=self.contract(status='active')))
        self.assertTrue(blocked[0])
        self.assertEqual(len(reads), 4)
        self.assertGreater(clock[0] - min(person_checks), 10)
        self.assertEqual(sender.delivered, [],
                         f'Contacts DNC evidence ages 45s; final timer starts afterwards and delivers: {result.outcome}')
