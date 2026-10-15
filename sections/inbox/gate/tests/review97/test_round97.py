"""Offline round-97 regressions; DG01 delivery assertions intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, ContactsMCP, SideShiftLive and file-backed SQLite. The inherited
fixture forbids HTTP; only remote responses, review and clocks are faked.
"""
from datetime import timedelta
from unittest.mock import patch

from gate import policy
from gate.dispatch import text_hash
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review96 import test_round96 as previous


class Round96Verification(previous.EarlyNoSendExpiry):
    """All eleven direct round-96 tests, unchanged."""


class Round95ExpiryVerification(previous.Round95ExpiryVerification):
    """Five round-95 tests, unchanged."""


class Round95BudgetVerification(previous.Round95BudgetVerification):
    """Nine round-94 tests, unchanged."""


class Round95InheritedVerification(previous.Round95InheritedVerification):
    """Twenty round-93 tests, unchanged."""


class BeforeIntentExpiry(Fixture):
    def retry_after_hold(self, option='c', kind='at-capacity', *,
                         stop='review', restart=False, remaining=5,
                         correction=True, approve=True, asleep=False):
        self.setup_system(option=option, distinct=True)
        worker = self.workers['U1']
        action = self.action_for('U1', kind)
        if kind == 'at-capacity':
            action.fields = {'First': 'Ada'}
            self.rows['U1'].append(dict(id='capacity', senderUserId='U1',
                content="I don't have capacity for another campaign right now.",
                createdAt=(self.clock - timedelta(hours=2)).isoformat()))
        self.continuous, self.stops = 0, []
        for target, getter in (
            ('gate.journal.time.time', lambda: self.clock.timestamp()),
            ('gate.clock._continuous', lambda: self.continuous),
        ):
            patched = patch(target, side_effect=getter)
            patched.start()
            self.addCleanup(patched.stop)
        if approve:
            self.paused.touch()
            action.captain_order = 'Send these exact words once.'
            action.approval_id = worker.journal.approve(action.creator_key,
                kind, action.occurrence,
                text_hash(policy.render(self.types[kind], action.fields)),
                action.captain_order)  # normal default TTL, no SQL edits
            self.clock += timedelta(seconds=7200 - remaining)
            self.elapsed += 7200 - remaining
            self.continuous += 7200 - remaining

        def delay():
            self.stops.append(stop)
            self.continuous += 25
            self.elapsed += 0.5 if asleep else 25
            self.clock += timedelta(seconds=0.5 if correction else 25)

        original_review = worker.gate.reviewer
        original_contract = worker.gate.contract_reader
        original_post = worker.sender._post

        def review(*args):
            delay()
            return 'HOLD', 'temporary review unavailable; try again', []

        def contract(cid):
            delay()
            raise RuntimeError('temporary contract read failure')

        def post(body):
            if body['params']['name'] == 'get_person':
                delay()
                raise RuntimeError('temporary Contacts read failure')
            return original_post(body)

        if stop == 'review':
            worker.gate.reviewer = review
        elif stop == 'contract':
            worker.gate.contract_reader = contract
        elif stop == 'preflight':
            worker.sender._post = post
        else:
            raise AssertionError(stop)
        first = worker.gate.run(action)
        worker.gate.reviewer = original_review
        worker.gate.contract_reader = original_contract
        worker.sender._post = original_post
        if not approve:
            self.assertEqual(first.outcome, 'draft', first)
            self.assertEqual(self.stops, [])
            return first, None

        self.assertEqual(first.outcome, 'held', first)
        self.assertEqual(self.stops, [stop], first)
        self.assertEqual(self.deliveries, [], first)
        self.assertEqual(self.continuous, 7200 - remaining + 25)
        self.assertTrue(self.paused.exists())
        self.assertNotIn('dispatching', worker.journal.outcomes(first.idempotency_key))
        self.assertFalse(worker.journal.spent(first.idempotency_key))
        # No approval consumption, transport attempt or restore: these early
        # held returns never reach the round-96 _unsent cleanup.
        self.assertIsNone(worker.journal.conn.execute(
            'SELECT used_at FROM approvals WHERE id=?',
            (action.approval_id,)).fetchone()['used_at'])
        if restart:
            worker = self.worker('U1')  # new Gate + SQLite connection
        second = worker.gate.run(action)
        self.assertTrue(self.paused.exists())
        self.assertEqual(self.continuous, 7200 - remaining + 25)
        return first, second

    def assert_expired_retry_stops(self, option='c', kind='at-capacity', **kw):
        first, second = self.retry_after_hold(option, kind, **kw)
        self.assertEqual(self.deliveries, [],
            f'Approval reused at elapsed {self.continuous}s through PAUSED '
            f'after a pre-intent hold; first={first}; retry={second}')

    def test_DG01_auto_guide_review_hold_must_expire_approval(self):
        self.assert_expired_retry_stops('a', 'warmup-guide')

    def test_DG01_released_draft_review_hold_must_expire_approval(self):
        self.assert_expired_retry_stops('b')

    def test_DG01_mixed_reply_review_hold_must_expire_approval(self):
        self.assert_expired_retry_stops()

    def test_DG01_mixed_guide_review_hold_must_expire_approval(self):
        self.assert_expired_retry_stops('c', 'warmup-guide')

    def test_DG01_mixed_reply_restart_must_expire_approval(self):
        self.assert_expired_retry_stops(restart=True)

    def test_DG01_contract_failure_before_intent_must_expire_approval(self):
        self.assert_expired_retry_stops(stop='contract')

    def test_DG01_first_preflight_failure_must_expire_approval(self):
        self.assert_expired_retry_stops(stop='preflight')

    def test_DG01_sleep_and_clock_correction_must_expire_approval(self):
        self.assert_expired_retry_stops(asleep=True)

    def test_control_no_correction_blocks_retry(self):
        first, second = self.retry_after_hold(correction=False)
        self.assertEqual(self.deliveries, [], (first, second))
        self.assertEqual(second.outcome, 'held', second)

    def test_control_still_valid_approval_can_retry(self):
        first, second = self.retry_after_hold(remaining=60)
        self.assertEqual(second.outcome, 'sent', (first, second))
        self.assertEqual(len(self.deliveries), 1)

    def test_control_unapproved_mixed_reply_stays_draft(self):
        first, _ = self.retry_after_hold(approve=False)
        self.assertEqual(first.outcome, 'draft', first)
        self.assertEqual(self.deliveries, [])

    def test_control_unapproved_drafts_stay_draft(self):
        first, _ = self.retry_after_hold('b', approve=False)
        self.assertEqual(first.outcome, 'draft', first)
        self.assertEqual(self.deliveries, [])
