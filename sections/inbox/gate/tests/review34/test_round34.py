"""Offline counterexamples; assertions state required behavior.

Run: python3 -m unittest discover -s out/tests -t .
Real Flow, Gate, SideShiftLive, SQLite and ContactsMCP send/preflight.
Only service replies, the clock and model verdicts are faked.
"""
from dataclasses import replace
from datetime import timedelta
import threading
from types import SimpleNamespace
from unittest.mock import patch

from gate import policy
from gate.dispatch import Gate
from gate.journal import Journal
from gate.live import SideShiftLive
from gate.tests.review3.support import Case, NOW, flow
from gate.tests.review7.test_round7 import CheckedSender


class InviteEvidence(Case):
    def setup_job(self, old_hours, draft=False):
        self.j = self.new_journal(self.root / 'shared.db')
        self.clock = NOW
        clock_patch = patch('gate.journal.datetime')
        clock_patch.start().now.side_effect = lambda *a: self.clock
        self.addCleanup(clock_patch.stop)
        self.old = self.raw_invite('old-invite', old_hours)
        self.new = self.raw_invite('new-invite', 1)
        self.rows = [self.old]
        self.reads = 0
        self.on_read = lambda: None

        class Client:
            def pages(inner, path, **kw):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                self.reads += 1
                self.on_read()
                return [dict(row) for row in self.rows]

        self.source = SideShiftLive(Client(), flow.COMPANY)
        self.current = self.contract(createdAt=(NOW - timedelta(hours=60)).isoformat())
        self.sender = CheckedSender(self.source)
        types = policy.load()
        if draft:
            types = {key: replace(t, mode='draft') for key, t in types.items()}
        self.g = self.gate(types=types, source=self.source, sender=self.sender,
                           reader=lambda cid: dict(self.current))
        self.g.applications_reader = lambda uid: []
        self.g.now = lambda: self.clock
        self.writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: self.writes.append((a, kw)) or
                                 dict(id='C1', contractorId='U1', status='rejected'))
        contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(self.current)],
                                    request=lambda *a, **kw: dict(self.current))
        self.job = flow.Flow(contracts, self.source, self.g, self.j,
                             lambda cid: ('route1', 'person1'), now=lambda: self.clock,
                             read_client=SimpleNamespace(pages=lambda *a, **kw: []),
                             write_client=writer)

    def raw_invite(self, mid, hours):
        return dict(id=mid, createdAt=(NOW - timedelta(hours=hours)).isoformat(),
                    senderUserId=flow.COMPANY,
                    content='https://app.sideshift.app/campaign-invite/C1')

    def test_AV01_withdrawal_own_complete_read_must_preserve_reinvite(self):
        self.setup_job(old_hours=40, draft=True)
        self.new = self.raw_invite('new-invite', 0)

        def withdrawal_read():
            if self.reads == 2:
                # Flow saw the old invitation; withdrawal's own fresh, complete
                # read sees the newer row and correctly vetoes this attempt.
                self.rows = [self.old, self.new]

        self.on_read = withdrawal_read
        first = self.job.run()
        self.assertEqual(self.reads, 2, first)
        self.assertTrue(any('younger than 24 hours' in line for line in first), first)   # adapted 2026-10-15: invites close at 24h
        self.assertEqual(self.writes, [])
        self.assertEqual(self.sender.delivered, [])
        # Six hours later the upstream row has vanished. Its last complete
        # observation was in withdrawal, not Flow's earlier read.
        self.rows = [self.old]
        self.on_read = lambda: None
        self.clock += timedelta(hours=6)
        later = self.job.run()
        self.assertEqual(self.writes, [],
                         f'Withdrawal consumed the six-hour-old round but later rejects: {later}')

    def test_AV02_round_must_be_revalidated_when_other_reader_advances_journal(self):
        self.setup_job(old_hours=10)
        self.new = self.raw_invite('new-invite', 7)
        consumed, release = threading.Event(), threading.Event()
        observed, errors = [], []

        class OlderReadClient:
            def pages(inner, path, **kw):
                if path == '/conversations':
                    yield dict(id='chat1', members=[flow.COMPANY, 'U1'])
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                # This worker started its read BEFORE the re-invite vanished.
                yield dict(self.old)
                yield dict(self.new)
                consumed.set()
                if not release.wait(5):
                    raise AssertionError('test did not release the in-flight read')

        def finish_older_read():
            other_journal = Journal(self.root / 'shared.db')
            try:
                source = SideShiftLive(OlderReadClient(), flow.COMPANY)
                gate = Gate(self.g.types, source, lambda *a: ('SEND', 'offline', []),
                            CheckedSender(source), other_journal, now=lambda: self.clock,
                            paused_file=self.paused, contract_reader=lambda cid: dict(self.current),
                            applications_reader=lambda uid: [])
                other = flow.Flow(self.job.contracts_client, source, gate, other_journal,
                                  self.job.routes, now=lambda: self.clock,
                                  read_client=self.job.read_client)
                observed.extend(other.run())
            except BaseException as exc:
                errors.append(repr(exc))
            finally:
                other_journal.conn.close()

        worker = threading.Thread(target=finish_older_read)
        worker.start()

        def cleanup():
            release.set()
            worker.join(5)

        self.addCleanup(cleanup)
        self.assertTrue(consumed.wait(5), errors)
        # The row has now vanished upstream: every new read by the main worker
        # correctly returns only old-invite. The earlier read is still in flight.

        def reviewer(*args):
            if not observed:
                release.set()
                worker.join(5)
                self.assertFalse(worker.is_alive())
                self.assertEqual(errors, [])
                self.assertTrue(observed)
                self.assertIn('new-invite', self.j.flags('sideshift:U1', 'invite-seen'))
                self.assertTrue(any('being handled' in line for line in observed), observed)
                self.clock += timedelta(minutes=2)  # well outside the 10s window
            return 'SEND', 'offline full-chat review', []

        self.g.reviewer = reviewer
        first = self.job.run()
        self.assertTrue(observed, first)
        # Its confirmed delivery remains in SQLite even when SideShift marks the
        # remote reminder deleted. Four hours later it is still the SAME round.
        self.rows = [self.old]
        if self.sender.delivered:
            sent = self.sender.delivered[0]
            self.rows.append(dict(id='delivered-reminder', createdAt=self.clock.isoformat(),
                                  senderUserId=flow.COMPANY, content=sent['text'], isDeleted=True))
        self.clock += timedelta(hours=4)
        second = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1,
                         f'History advanced during review; duplicate confirmed reminder keys: '
                         f'{[s["idempotency_key"] for s in self.sender.delivered]}; {second}')
