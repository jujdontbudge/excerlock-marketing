"""Offline counterexamples. Assertions state required behavior and fail on this snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Flow, Gate, file-backed SQLite, ContactsMCP preflight/send.
Only service responses, time and the review verdict are faked. No network.
"""
from datetime import timedelta
from types import SimpleNamespace
from dataclasses import replace
from unittest.mock import patch

from gate import policy
from gate.live import SideShiftLive
from gate.tests.review3.support import Case, NOW, flow
from gate.tests.review7.test_round7 import CheckedSender


class InviteHistory(Case):
    def setup_flow(self, old_hours, new_hours=1, draft=False):
        self.j = self.new_journal(self.root / 'gate.db')
        self.clock = NOW
        journal_clock = patch('gate.journal.datetime')
        journal_clock.start().now.side_effect = lambda *a: self.clock
        self.addCleanup(journal_clock.stop)
        self.rows = [
            dict(id='old-invite', createdAt=(NOW - timedelta(hours=old_hours)).isoformat(),
                 senderUserId=flow.COMPANY,
                 content='https://app.sideshift.app/campaign-invite/C1'),
            dict(id='new-invite', createdAt=(NOW - timedelta(hours=new_hours)).isoformat(),
                 senderUserId=flow.COMPANY,
                 content='https://app.sideshift.app/campaign-invite/C1'),
        ]
        self.chat_reads = 0

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                self.chat_reads += 1
                return [dict(row) for row in self.rows]

        self.source = SideShiftLive(Client(), flow.COMPANY)
        self.current = self.contract(createdAt=(NOW - timedelta(hours=60)).isoformat())
        self.sender = CheckedSender(self.source)
        types = policy.load()
        if draft:
            types = {k: replace(t, mode='draft') for k, t in types.items()}
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

    def read_then_route_failure(self, old_hours, draft=False):
        self.setup_flow(old_hours, draft=draft)

        def unavailable_route(cid):
            raise OSError('contacts unavailable after complete SideShift read')

        self.job.routes = unavailable_route
        report = self.job.run()
        self.assertEqual(self.chat_reads, 1)
        self.assertTrue(any('error OSError' in line for line in report), report)
        self.assertEqual(self.sender.delivered, [])
        self.assertEqual(self.writes, [])
        # SideShift subsequently removes the newer invite row entirely.
        self.rows.pop()
        self.job.routes = lambda cid: ('route1', 'person1')

    def test_AU01_complete_invite_read_survives_route_error_before_later_reminder(self):
        self.read_then_route_failure(old_hours=10)
        self.clock = NOW + timedelta(hours=1)
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Two-hour-old re-invite was consumed before route failure; later run: {report}')

    def test_AU01_complete_invite_read_survives_route_error_before_all_draft_withdrawal(self):
        self.read_then_route_failure(old_hours=35, draft=True)
        self.clock = NOW + timedelta(hours=6)
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [])
        self.assertEqual(self.writes, [],
                         f'Seven-hour-old re-invite was consumed before route failure; later run: {report}')

    def test_AU02_reminder_key_cannot_regress_when_recorded_reinvite_disappears(self):
        self.setup_flow(old_hours=20, new_hours=7)
        first_report = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, first_report)
        first_send = self.sender.delivered[0]
        self.assertEqual(first_send['idempotency_key'],
                         'gate:contract-reminder-1:sideshift:U1:C1:new-invite')
        self.assertIn('new-invite', self.j.flags('sideshift:U1', 'invite-seen'))
        # Delivery remains confirmed in the append-only journal. The upstream
        # reminder is deleted and the invite row vanishes four hours later.
        self.rows = [self.rows[0],
                     dict(id='reminder-sent', createdAt=NOW.isoformat(),
                          senderUserId=flow.COMPANY, content=first_send['text'], isDeleted=True)]
        self.clock = NOW + timedelta(hours=4)
        second_report = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1,
                         f'Same 11-hour-old round, confirmed reminder sent twice: '
                         f'{[s["idempotency_key"] for s in self.sender.delivered]}; {second_report}')
