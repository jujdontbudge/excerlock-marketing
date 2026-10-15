"""Offline counterexamples; assertions state the required behavior.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Flow, Gate, SQLite and ContactsMCP send boundary.
Only remote responses, the clock and the review verdict are faked.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import policy
from gate.live import SideShiftLive
from gate.tests.review3.support import Case, NOW
from gate.tests.review4.support import flow
from gate.tests.review7.test_round7 import CheckedSender


class DeletedReinvite(Case):
    def setup_job(self, old_hours, draft=False):
        self.clock = NOW
        self.rows = [
            dict(id='old-invite', createdAt=(NOW - timedelta(hours=old_hours)).isoformat(),
                 senderUserId=flow.COMPANY,
                 content='https://app.sideshift.app/campaign-invite/C1'),
            dict(id='new-invite', createdAt=(NOW - timedelta(hours=1)).isoformat(),
                 senderUserId=flow.COMPANY,
                 content='https://app.sideshift.app/campaign-invite/C1'),
        ]

        class Client:
            def pages(inner, path, **kw):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row) for row in self.rows]

        source = SideShiftLive(Client(), flow.COMPANY)
        contract = self.contract(createdAt=(NOW - timedelta(hours=60)).isoformat())
        sender = CheckedSender(source)
        types = policy.load()
        if draft:
            types = {key: replace(t, mode='draft') for key, t in types.items()}
        gate = self.gate(types=types, source=source, sender=sender,
                         reader=lambda cid: dict(contract))
        gate.now = lambda: self.clock
        gate.applications_reader = lambda uid: []
        contracts = SimpleNamespace(
            pages=lambda *a, **kw: [dict(contract)],
            request=lambda *a, **kw: dict(contract))
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 dict(id='C1', contractorId='U1', status='rejected'))
        job = flow.Flow(contracts, source, gate, self.j, lambda cid: ('route1', 'person1'),
                        now=lambda: self.clock,
                        read_client=SimpleNamespace(pages=lambda *a, **kw: []),
                        write_client=writer)
        self.assertEqual(job.run(), [])  # complete read observes the genuine one-hour-old re-invite
        self.assertEqual(sender.delivered, [])
        self.assertEqual(writes, [])
        # Its message is deleted upstream; the contract itself remains pending.
        # The deletion leaves valid text, identity and creation time in the native row.
        self.rows[-1]['isDeleted'] = True
        return job, sender, writes

    def test_AT01_deleted_reinvite_cannot_move_reminder_clock_back_hours(self):
        job, sender, _ = self.setup_job(old_hours=10)
        self.clock = NOW + timedelta(hours=1)
        report = job.run()
        self.assertEqual(sender.delivered, [],
                         f'Re-invited only two hours ago, yet deletion enabled a reminder: {report}')

    def test_AT01_deleted_reinvite_cannot_withdraw_new_round_in_all_draft_mode(self):
        job, sender, writes = self.setup_job(old_hours=35, draft=True)
        self.clock = NOW + timedelta(hours=6)
        report = job.run()
        self.assertEqual(sender.delivered, [])
        self.assertEqual(writes, [],
                         f'Re-invited only seven hours ago, yet deletion enabled rejection: {report}')
