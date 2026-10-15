"""Required-behavior counterexamples. No network; production code is unchanged.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


class Review41(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def draft_withdrawal(self):
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))

    def question(self, hours):
        self.rows.append(dict(id='question', createdAt=(self.clock - timedelta(hours=hours)).isoformat(),
                              senderUserId='U1', content='What should I film for the first video?'))
        return self.source.read('chat1').messages[-1]

    def test_BC01_sender_change_cannot_settle_question_before_withdrawal(self):
        self.setup_flow()
        self.draft_withdrawal()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        question = self.question(30)
        first = self.job.run()
        self.assertEqual(self.writes, [], first)
        self.assertTrue(any('waiting for an answer' in line for line in first), first)
        # Exactly the same unresolved words; only the upstream attribution changes.
        self.rows[-1]['senderUserId'] = self.job.live.company_id
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertNotIn(checks.mark(question), self.j.flags('sideshift:U1', 'answered'))
        self.assertEqual(self.writes, [], f'Sender metadata settled an unanswered question: {second}')

    def test_BC01_sender_change_cannot_clear_question_before_automatic_reminder(self):
        self.setup_flow()
        question = self.question(4)
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertTrue(any('nobody has marked answered' in line for line in first), first)
        self.rows[-1]['senderUserId'] = self.job.live.company_id
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertNotIn(checks.mark(question), self.j.flags('sideshift:U1', 'answered'))
        self.assertEqual(self.sender.delivered, [], f'Observed question lost its deterministic veto: {second}')

    def test_BC02_inbound_link_cannot_authorize_withdrawal_without_our_invite(self):
        self.setup_flow()
        self.draft_withdrawal()
        # The only link in the chat was written by HER. No delivered invite.
        self.rows[0].update(senderUserId='U1', createdAt=(self.clock - timedelta(hours=40)).isoformat())
        inbound = self.source.read('chat1').messages[0]
        self.assertEqual(inbound.direction, 'in')
        self.assertIsNone(checks.invite_time(self.source.read('chat1'), self.current))
        # Settling her text does not authorize treating it as an outbound invite.
        self.j.event('sideshift:U1', 'answered', checks.mark(inbound), {'by': 'captain'})
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertEqual(self.writes, [], f'Her pasted URL became proof of our invite delivery: {report}')

    def test_BC02_inbound_link_cannot_authorize_automatic_reminder_without_our_invite(self):
        self.setup_flow()
        self.rows[0]['senderUserId'] = 'U1'
        self.source.read('chat1')
        self.assertIsNone(checks.invite_time(self.source.read('chat1'), self.current))
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [], f'No outbound invite exists, but a reminder was sent: {report}')
