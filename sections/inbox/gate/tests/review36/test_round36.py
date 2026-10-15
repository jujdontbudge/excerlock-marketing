"""Offline regressions: assertions express required behavior and fail on this snapshot.
Run: python3 -m unittest discover -s out/tests -t .
"""
from datetime import timedelta

from gate import checks, policy
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review3.support import Case


class RedactedEvidence(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def test_AX01_redacted_earlier_tied_invite_cannot_duplicate_confirmed_reminder(self):
        self.setup_flow(invite_ids=('round-A', 'round-B'))
        first = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, first)
        self.assertTrue(self.sender.delivered[0]['idempotency_key'].endswith(':round-B'))
        self.assertEqual(self.j.flags('sideshift:U1', 'invite-seen'), {'round-A', 'round-B'})
        # Four hours later, the earlier invite is a native tombstone retaining
        # its identity and time; the later invite is unchanged. No new invite.
        self.rows[0].update(isDeleted=True, content='')
        self.rows.append(self.raw('delivered-reminder', '', self.clock, isDeleted=True))
        self.clock += timedelta(hours=4)
        second = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1,
                         f'Redacted earlier invite reversed the known round: '
                         f'{[s["idempotency_key"] for s in self.sender.delivered]}; {second}')

    def test_AX02_observed_manual_copy_cannot_be_resent_after_native_text_redaction(self):
        self.setup_flow()
        text = policy.render(self.g.types['contract-reminder-1'], {'First': 'Ada'})
        self.rows.append(self.raw('manual-copy', text, self.clock - timedelta(hours=4)))
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertTrue(any('already in the chat' in line for line in first), first)
        # Gate already observed this exact delivery; only its text is redacted.
        self.rows[-1].update(isDeleted=True, content='')
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Redaction erased the previously observed delivery: {second}')

    def test_AX03_older_ambiguous_pair_cannot_block_a_strictly_newer_round(self):
        self.setup_flow(invite_ids=('round-A', 'round-B'))
        # Initial read establishes history but makes no delivery (invite <6h).
        for r in self.rows:
            r['createdAt'] = (self.clock - timedelta(hours=1)).isoformat()
        self.assertEqual(self.job.run(), [])
        self.assertEqual(self.sender.delivered, [])
        self.rows.pop(0)
        # An unequivocally later invite starts a new round. The ambiguity in
        # the older pair cannot affect which invite is current now.
        self.rows.append(self.raw('round-C', 'https://app.sideshift.app/campaign-invite/C1', self.clock))
        self.clock += timedelta(hours=7)
        current = self.source.read('chat1')
        contract = self.g._signing(self.action(contract=self.current), current).contract
        self.assertEqual(checks.invite_generation(current, contract), 'round-C')
        report = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1,
                         f'A known current round was blocked by an irrelevant old tie: {report}')
