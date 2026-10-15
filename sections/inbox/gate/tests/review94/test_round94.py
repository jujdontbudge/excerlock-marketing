"""Offline regression tests. DD01 assertions intentionally fail on the supplied gate.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, ContactsMCP, SideShiftLive and file-backed SQLite. The fixture's
requests adapter forbids HTTP; remote responses, review and clocks are fakes.
"""
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import clock, policy
from gate.dispatch import text_hash
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review93 import test_round93 as previous


class Round93Verification(previous.ApprovalAtSend,
                          previous.Round92Verification,
                          previous.PreGrantClockVerification):
    """All twenty original round-93 tests, unchanged."""


class ApprovalElapsedDeadline(Fixture):
    def dispatch(self, option='c', kind='at-capacity', *, remaining=5,
                 correction=True, asleep=False, approve=True):
        self.setup_system(option=option, distinct=True)
        worker = self.workers['U1']
        action = self.action_for('U1', kind)
        if kind == 'at-capacity':
            action.fields = {'First': 'Ada'}
            self.rows['U1'].append(dict(id='capacity', senderUserId='U1',
                content="I don't have capacity for another campaign right now.",
                createdAt=(self.clock - timedelta(hours=2)).isoformat()))
        self.continuous, self.delays, self.effects, self.final_ages = 0, [], [], []
        wall = lambda: self.clock.timestamp()
        for target, getter in (
            ('gate.journal.time.time', wall),
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
                action.captain_order)  # real default TTL: 7200 seconds
            original_post = worker.sender._post

            def failed(body):
                if body['params']['name'] == 'send_message':
                    result = dict(status='failed', error='definitely not sent')
                    return SimpleNamespace(text=json.dumps(dict(result=dict(
                        content=[dict(type='text', text=json.dumps(result))]))))
                return original_post(body)

            # Public, supported restore-and-retry path. No approval row is
            # edited by this test; Gate._unsent restores the real approval.
            worker.sender._post = failed
            first = worker.gate.run(action)
            self.assertEqual(first.outcome, 'error', first)
            self.assertEqual(self.deliveries, [])
            self.assertFalse(worker.journal.spent(first.idempotency_key))
            self.assertIsNone(worker.journal.conn.execute(
                'SELECT used_at FROM approvals WHERE id=?',
                (action.approval_id,)).fetchone()['used_at'])
            worker.sender._post = original_post
            self.clock += timedelta(seconds=7200 - remaining)
            self.elapsed += 7200 - remaining
            self.continuous += 7200 - remaining

        original_pages = worker.live.client.pages
        self.reads = 0

        def pages(path, **kwargs):
            if path == '/conversations':
                self.reads += 1
                if self.reads == 3:
                    # Gate has consumed the approval. The transport's own
                    # live read waits 25s. NTP/manual clock correction loses
                    # 24.5s of wall time; continuous time still counts it all.
                    if approve:
                        self.assertIsNotNone(worker.journal.conn.execute(
                            'SELECT used_at FROM approvals WHERE id=?',
                            (action.approval_id,)).fetchone()['used_at'])
                    self.delays.append(self.clock)
                    self.continuous += 25
                    self.elapsed += 0.5 if asleep else 25
                    self.clock += timedelta(seconds=0.5 if correction else 25)
            return original_pages(path, **kwargs)

        worker.live.client.pages = pages
        original_recheck = worker.gate._final_recheck

        def recheck(*args, **kwargs):
            since = clock.Since(lambda: self.clock)
            reasons = original_recheck(*args, **kwargs)
            self.final_ages.append(since.age())
            return reasons

        worker.gate._final_recheck = recheck  # observation only
        original_post = worker.sender._post

        def post(body):
            if body['params']['name'] == 'send_message':
                self.effects.append(dict(elapsed=self.continuous,
                    paused=self.paused.exists(),
                    wall=self.clock.isoformat()))
            return original_post(body)

        worker.sender._post = post
        return worker.gate.run(action)

    def assert_expired_approval_stops(self, option, kind='warmup-guide', asleep=False):
        result = self.dispatch(option, kind, asleep=asleep)
        self.assertEqual(len(self.delays), 1, result)
        self.assertEqual(self.reads, 4, result)
        self.assertEqual(self.continuous, 7220)
        self.assertEqual(self.final_ages, [0], result)
        self.assertTrue(self.paused.exists())
        self.assertEqual(self.deliveries, [],
            f'Approval TTL exceeded by 20s; PAUSED still on; '
            f'fresh final evidence, wall corrected during transport read: '
            f'{self.effects}; {result}')

    def test_DD01_auto_must_enforce_elapsed_approval_lifetime(self):
        self.assert_expired_approval_stops('a')

    def test_DD01_drafts_must_enforce_elapsed_approval_lifetime(self):
        self.assert_expired_approval_stops('b', 'at-capacity')

    def test_DD01_mixed_guide_must_enforce_elapsed_approval_lifetime(self):
        self.assert_expired_approval_stops('c')

    def test_DD01_mixed_reply_must_enforce_elapsed_approval_lifetime(self):
        self.assert_expired_approval_stops('c', 'at-capacity')

    def test_DD01_sleep_and_wall_correction_must_expire_mixed_approval(self):
        self.assert_expired_approval_stops('c', 'at-capacity', asleep=True)

    def test_control_without_wall_correction_round93_fix_stops_send(self):
        result = self.dispatch(correction=False)
        self.assertEqual(self.continuous, 7220)
        self.assertEqual(self.final_ages, [0])
        self.assertEqual(self.deliveries, [], result)
        self.assertIn('approval expired before the send', str(result))

    def test_control_sufficient_lifetime_still_sends_after_clock_correction(self):
        result = self.dispatch(remaining=60)
        self.assertEqual(self.continuous, 7165)
        self.assertEqual(result.outcome, 'sent', result)
        self.assertEqual(len(self.deliveries), 1)

    def test_control_mixed_reply_without_approval_remains_a_draft(self):
        result = self.dispatch(approve=False)
        self.assertEqual(result.outcome, 'draft', result)
        self.assertEqual(self.delays, [])
        self.assertEqual(self.deliveries, [])

    def test_control_automatic_mixed_guide_without_approval_still_sends(self):
        result = self.dispatch(kind='warmup-guide', approve=False)
        self.assertEqual(result.outcome, 'sent', result)
        self.assertEqual(len(self.deliveries), 1)
