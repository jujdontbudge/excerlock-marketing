"""Offline counterexamples. Required-behavior assertions fail on round 37.

Run: python3 -m unittest discover -s out/tests -t .
Real Flow, SideShiftLive, Gate, Journal and ContactsMCP send boundary;
only remote responses, time and the model's verdict are faked.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks, policy
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


class DurableEvidence(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def test_AY01_observed_recent_creator_activity_survives_missing_row_in_draft_mode(self):
        self.setup_flow()
        # Draft mode only affects messages; Flow still reaches withdrawal.
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='trying', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content='I am still trying to create the accounts.'))
        writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        first = self.job.run()
        self.assertEqual(writes, [], first)
        self.assertTrue(any('last 24 hours' in line for line in first), first)
        # The reader has consumed her activity and withdrawal has held for it.
        # Upstream later removes the row entirely, as with missing invites in
        # the existing regressions. No answer or keep/release decision occurs.
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(writes, [],
                         f'Observed activity only 75 minutes old was forgotten; draft-only Flow withdrew: {second}')

    def test_AY02_retargeted_tied_invite_cannot_reverse_round_and_repeat_reminder(self):
        self.setup_flow(invite_ids=('round-A', 'round-B'))
        first = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, first)
        self.assertTrue(self.sender.delivered[0]['idempotency_key'].endswith(':round-B'))
        # A is no longer live evidence for C1, but still classifies as an invite.
        self.rows[0].update(content='https://app.sideshift.app/campaign-invite/C2',
                            isEdited=True, updatedAt=self.clock.isoformat())
        self.clock += timedelta(hours=4)
        second = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1,
                         f'Invite for another contract masked reconstructed C1 evidence: '
                         f'{[s["idempotency_key"] for s in self.sender.delivered]}; {second}')

    def test_AY03_every_observed_outbound_revision_retains_duplicate_protection(self):
        self.setup_flow()
        t = self.g.types['contract-reminder-1']
        exact = policy.render(t, {'First': 'Ada'})
        # First revision is seen while the invite is too young for any send.
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=1)).isoformat()
        self.rows.append(self.raw('manual', 'I will send the next steps shortly.',
                                  self.clock - timedelta(minutes=1)))
        self.assertEqual(self.job.run(), [])
        self.assertGreaterEqual(len(self.g._seen_out('sideshift:U1')), 1)   # adapted 2026-10-15 (CE01): captain invites count too
        # Same native id, edited to the exact approved reminder. Gate observes
        # this revision on a complete read and refuses its exact duplicate.
        self.clock += timedelta(hours=6)
        self.rows[-1].update(content=exact, isEdited=True, updatedAt=self.clock.isoformat())
        observed = self.job.run()
        self.assertEqual(self.sender.delivered, [], observed)
        self.assertTrue(any('already in the chat' in line for line in observed), observed)
        self.rows[-1].update(content='', isDeleted=True)
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Second observed revision disappeared from durable duplicate checks: {second}')

    def test_AY04_remembered_manual_warmup_must_allow_onboarding_to_continue(self):
        self.setup_flow()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=1)).isoformat()
        guide = policy.render(self.g.types['warmup-guide'], {'First': 'Ada'})
        self.rows.append(self.raw('manual-guide', guide, self.clock - timedelta(minutes=45)))
        # Flow observes a manual guide before handle approval makes the contract
        # active. No Gate send receipt exists for a direct SideShift message.
        self.assertEqual(self.job.run(), [])
        self.assertIn(checks.text_digest(guide), [x['digest'] for x in self.g._seen_out('sideshift:U1')])   # adapted (CE01)
        self.current['status'] = 'active'
        self.rows[-1].update(content='', isDeleted=True)
        reports = []
        for _ in range(2):
            self.clock += timedelta(minutes=15)
            reports.append(self.job.run())
        wanted = policy.render(self.g.types['ask-app-email'], {})
        self.assertTrue(any(s['text'] == wanted for s in self.sender.delivered),
                        f'Observed guide is permanently held as a duplicate, but Flow never advances: {reports}')
