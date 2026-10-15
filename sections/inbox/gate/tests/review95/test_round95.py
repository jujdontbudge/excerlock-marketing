"""Offline adversarial approval-retry regressions; DE01 assertions fail.

Run: python3 -m unittest discover -s out/tests -t .
The inherited fixture runs real Gate, ContactsMCP, SideShiftLive and file-backed
SQLite and forbids HTTP. Remote data, review and clocks alone are faked.
"""
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review94 import test_round94 as previous


class Round94Verification(previous.ApprovalElapsedDeadline):
    """All nine round-94 approval-budget tests, unchanged."""


class Round93Verification(previous.Round93Verification):
    """All twenty round-93 tests inherited by round 94, unchanged."""


class RestoredApprovalDeadline(Fixture):
    dispatch = previous.ApprovalElapsedDeadline.dispatch

    def retry_after_elapsed_expiry(self, option, kind, restart=False):
        original_setup = self.setup_system

        def setup(*args, **kwargs):
            original_setup(*args, **kwargs)
            worker = self.workers['U1']
            original_run = worker.gate.run

            def run(action):
                self.last_action = action
                return original_run(action)

            worker.gate.run = run  # capture only; every decision is real

        self.setup_system = setup
        first = self.dispatch(option, kind, correction=True)
        worker = self.workers['U1']
        self.assertEqual(first.outcome, 'error', first)
        self.assertIn('approval expired before the send', str(first))
        self.assertEqual(self.deliveries, [], first)
        self.assertEqual(self.continuous, 7220)
        self.assertIsNone(worker.journal.conn.execute(
            'SELECT used_at FROM approvals WHERE id=?',
            (self.last_action.approval_id,)).fetchone()['used_at'])
        self.assertFalse(worker.journal.spent(first.idempotency_key))
        self.assertTrue(self.paused.exists())
        # No additional correction, elapsed time or approval. Public run() on
        # the SAME approval after Gate's own definite-no-send restoration.
        if restart:
            worker = self.worker('U1')  # fresh Gate and SQLite connection
        second = worker.gate.run(self.last_action)
        self.assertEqual(self.continuous, 7220)
        self.assertTrue(self.paused.exists())
        self.assertTrue(self.final_ages)
        self.assertTrue(all(age == 0 for age in self.final_ages))
        return first, second

    def assert_expired_retry_stops(self, option, kind, restart=False):
        first, second = self.retry_after_elapsed_expiry(option, kind, restart)
        self.assertEqual(self.deliveries, [],
            f'Approval already rejected for elapsed expiry, then restored and '
            f'reused at elapsed {self.continuous}s with PAUSED on; '
            f'first={first}; retry={second}')

    def test_DE01_auto_guide_retry_cannot_revive_expired_approval(self):
        self.assert_expired_retry_stops('a', 'warmup-guide')

    def test_DE01_draft_release_retry_cannot_revive_expired_approval(self):
        self.assert_expired_retry_stops('b', 'at-capacity')

    def test_DE01_mixed_reply_retry_cannot_revive_expired_approval(self):
        self.assert_expired_retry_stops('c', 'at-capacity')

    def test_DE01_mixed_guide_retry_cannot_revive_expired_approval(self):
        self.assert_expired_retry_stops('c', 'warmup-guide')

    def test_DE01_fresh_worker_retry_cannot_revive_expired_approval(self):
        self.assert_expired_retry_stops('c', 'at-capacity', restart=True)
