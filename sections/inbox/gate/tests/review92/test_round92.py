"""Offline effect-boundary regressions. DB01 assertions intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, ContactsMCP, SideShiftLive and file-backed SQLite; only remote
responses, clocks and the review verdict are fake. The fixture forbids HTTP.
"""
from datetime import timedelta
from unittest.mock import patch

from gate import clock
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review91 import test_round91 as previous


class FinalSendSleep(Fixture):
    def run_guide(self, option='a', *, rollback=True, asleep=True, seconds=25):
        self.setup_system(option=option, distinct=True)
        self.continuous = 0
        continuous_patch = patch('gate.clock._continuous', side_effect=lambda: self.continuous)
        continuous_patch.start()
        self.addCleanup(continuous_patch.stop)
        worker = self.workers['U1']
        self.reads, self.suspensions = 0, []
        self.effect_evidence = []
        original_post = worker.sender._post

        def post(body):
            if body['params']['name'] == 'send_message':
                self.effect_evidence.append(dict(
                    status=self.contracts['U1']['status'],
                    evidence_age=self.continuous,
                    since_cancel=self.continuous - 5,
                    monotonic_age=self.elapsed,
                    wall_age=(self.clock - self.started_wall).total_seconds()))
            return original_post(body)

        worker.sender._post = post

        def fetch(cid):
            self.reads += 1
            snapshot = dict(self.contracts['U1'])
            if self.reads == 2:
                # First fresh-contract read is after review. This second read is
                # inside the real transport's _final_recheck, before its final
                # chat, contacts and journal checks. Suspend AFTER the server
                # took its active snapshot, before returning that snapshot.
                self.started_wall = self.clock
                self.age = clock.Since(lambda: self.clock)
                self.continuous += 5
                self.contracts['U1']['status'] = 'cancelled'
                self.continuous += seconds - 5
                awake = 0.5 if asleep else seconds
                self.elapsed += awake
                # During sleep the wall clock is corrected back by the sleep
                # duration. Both old guards see 0.5s; continuous sees 25s.
                self.clock += timedelta(seconds=0.5 if rollback else seconds)
                self.suspensions.append(snapshot)
            return snapshot

        worker.gate.contract_reader = fetch
        decision = worker.gate.run(self.action_for('U1'))
        if option != 'b':
            self.assertEqual(len(self.suspensions), 1, decision)
            self.assertEqual(self.suspensions[0]['status'], 'active')
            self.assertEqual(self.contracts['U1']['status'], 'cancelled')
            self.assertEqual(self.age.age(), seconds)
        return decision

    def assert_stops(self, option):
        decision = self.run_guide(option)
        self.assertEqual(self.elapsed, 0.5)
        self.assertEqual((self.clock - self.started_wall).total_seconds(), 0.5)
        self.assertEqual(self.deliveries, [],
            f'Final send used a 25-second-old active contract, cancelled 20s '
            f'before delivery: {self.effect_evidence}; {decision}')

    def test_DB01_auto_final_send_must_count_sleep_despite_wall_correction(self):
        self.assert_stops('a')

    def test_DB01_mixed_final_send_must_count_sleep_despite_wall_correction(self):
        self.assert_stops('c')

    def test_control_wall_advance_without_correction_holds(self):
        decision = self.run_guide(rollback=False)
        self.assertEqual(self.deliveries, [], decision)
        self.assertIn('final checks took longer than 10s', str(decision))

    def test_control_awake_delay_with_wall_correction_holds(self):
        decision = self.run_guide(asleep=False)
        self.assertEqual(self.deliveries, [], decision)
        self.assertIn('final checks took longer than 10s', str(decision))

    def test_control_short_sleep_remains_within_accepted_window(self):
        decision = self.run_guide(seconds=7)
        self.assertEqual(len(self.deliveries), 1, decision)
        self.assertEqual(self.effect_evidence[0]['since_cancel'], 2)

    def test_control_drafts_never_reach_final_send(self):
        decision = self.run_guide(option='b')
        self.assertEqual(decision.outcome, 'draft', decision)
        self.assertEqual(self.reads, 0)
        self.assertEqual(self.deliveries, [])


class Round91ContinuousControls(Fixture):
    """Verify the actual DA01 fixes work even when wall time loses the sleep."""
    withdrawal = previous.SleepEvidence.withdrawal
    premium = previous.SleepEvidence.premium

    def continuous_clock(self):
        self.continuous = 0
        patched = patch('gate.clock._continuous', side_effect=lambda: self.continuous)
        patched.start()
        self.addCleanup(patched.stop)

    def advance(self, seconds, asleep):
        self.assertTrue(asleep)
        self.continuous += seconds
        self.elapsed += 0.25
        self.clock += timedelta(seconds=0.25)

    def assert_withdrawal_stops(self, option):
        self.continuous_clock()
        report = self.withdrawal(option)
        self.assertEqual(self.continuous, 25)
        self.assertEqual(self.elapsed, 0.5)
        self.assertEqual(self.writes, [], report)

    def test_control_DA01_continuous_clock_stops_auto_withdrawal(self):
        self.assert_withdrawal_stops('a')

    def test_control_DA01_continuous_clock_stops_draft_withdrawal(self):
        self.assert_withdrawal_stops('b')

    def test_control_DA01_continuous_clock_stops_mixed_withdrawal(self):
        self.assert_withdrawal_stops('c')

    def test_control_DA01_continuous_clock_stops_premium_commit(self):
        self.continuous_clock()
        decision = self.premium()
        self.assertEqual(len(self.suspensions), 1)
        self.assertEqual(self.continuous, 25)
        self.assertEqual(self.elapsed, 0.5)
        self.assertEqual(self.grants, [], decision)
        self.assertEqual(self.deliveries, [], decision)
