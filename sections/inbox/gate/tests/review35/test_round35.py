"""Offline counterexamples. Assertions state required behavior and fail on this snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Gate, Flow, SQLite and ContactsMCP preflight/send;
only remote responses, the clock and the model verdict are faked.
"""
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import policy
from gate.live import SideShiftLive
from gate.review import payload
from gate.tests.review3.support import Case, NOW, flow
from gate.tests.review7.test_round7 import CheckedSender


class RetainedDelivery(Case):
    def setup_flow(self, invite_ids=('invite1',)):
        self.j = self.new_journal(self.root / 'gate.db')
        self.clock = NOW
        clock_patch = patch('gate.journal.datetime')
        clock_patch.start().now.side_effect = lambda *a: self.clock
        self.addCleanup(clock_patch.stop)
        self.rows = [self.raw(mid, 'https://app.sideshift.app/campaign-invite/C1',
                              NOW - timedelta(hours=7)) for mid in invite_ids]
        self.current = self.contract(createdAt=(NOW - timedelta(hours=60)).isoformat())

        class Client:
            def pages(inner, path, **kw):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row) for row in self.rows]

        self.source = SideShiftLive(Client(), flow.COMPANY)
        self.sender = CheckedSender(self.source)
        self.g = self.gate(types=policy.load(), source=self.source, sender=self.sender,
                           reader=lambda cid: dict(self.current))
        self.g.applications_reader = lambda uid: []
        self.g.now = lambda: self.clock
        contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(self.current)],
                                    request=lambda *a, **kw: dict(self.current))
        self.job = flow.Flow(contracts, self.source, self.g, self.j,
                             lambda chat: ('route1', 'person1'), now=lambda: self.clock,
                             read_client=SimpleNamespace(pages=lambda *a, **kw: []))

    def raw(self, mid, text, at, **kw):
        return dict(id=mid, createdAt=at.isoformat(), senderUserId=flow.COMPANY,
                    content=text, **kw)

    def test_AW01_deleted_captain_message_still_counts_for_minimum_gap(self):
        self.setup_flow()
        captain = self.raw('captain-update', 'I will check the accounts this afternoon.',
                           NOW - timedelta(minutes=1))
        self.rows.append(captain)
        # Positive control: the same delivery, when not deleted, holds reminder 1.
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertTrue(any('min gap 180' in line for line in first), first)
        captain['isDeleted'] = True
        # A deleted delivery is also absent from the model's review input.
        # adapted 2026-10-15 (review AW01 fix): the reviewer now sees deleted deliveries, marked as deleted
        self.assertIn('"deleted": true', payload(self.source.read('chat1'), 'test', 'test'))
        second = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Deleting a one-minute-old captain delivery bypassed the three-hour gap: {second}')

    def test_AW01_deleted_manual_copy_cannot_enable_an_automatic_duplicate(self):
        self.setup_flow()
        t = self.g.types['contract-reminder-1']
        text = policy.render(t, {'First': 'Ada'})
        captain = self.raw('manually-sent-reminder', text, NOW - timedelta(hours=4))
        self.rows.append(captain)
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertTrue(any('already in the chat' in line for line in first), first)
        # Captain's direct SideShift sends have no Gate decision/spent key.
        captain['isDeleted'] = True
        second = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'The exact reminder was already delivered by the captain: {second}')

    def test_AW02_removing_earlier_tied_invite_cannot_change_round_and_duplicate_reminder(self):
        # Source order resolves equal timestamps (the existing T03 contract).
        self.setup_flow(invite_ids=('round-A', 'round-B'))
        first = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, first)
        sent = self.sender.delivered[0]
        self.assertEqual(sent['idempotency_key'],
                         'gate:contract-reminder-1:sideshift:U1:C1:round-B')
        self.assertEqual(self.j.delivery(sent['idempotency_key']), 'sent')
        self.assertEqual(self.j.flags('sideshift:U1', 'invite-seen'), {'round-A', 'round-B'})
        # Four hours later: the EARLIER invite disappears; the current round-B
        # remains unchanged. The reminder row vanishes but its receipt is durable.
        # No new invite, no concurrency, no evidence-window race.
        self.rows = [self.rows[1]]
        self.clock += timedelta(hours=4)
        second = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1,
                         f'Merging missing round-A after live round-B reversed their order and sent twice: '
                         f'{[s["idempotency_key"] for s in self.sender.delivered]}; {second}')

