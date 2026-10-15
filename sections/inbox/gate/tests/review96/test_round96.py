"""Offline regressions: DF01 assertions fail on the supplied production code.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, ContactsMCP, SideShiftLive and file-backed SQLite; HTTP is forbidden
by the inherited fixture. Only remote responses, review and clocks are faked.
"""
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review94 import test_round94 as round94
from gate.tests.review95 import test_round95 as round95


class Round95ExpiryVerification(round95.RestoredApprovalDeadline):
    """The five DE01 delivery assertions, unchanged."""


class Round95BudgetVerification(round95.Round94Verification):
    """The nine inherited round-94 assertions, unchanged."""


class Round95InheritedVerification(round95.Round93Verification):
    """The twenty inherited round-93 assertions, unchanged."""


class EarlyNoSendExpiry(Fixture):
    dispatch = round94.ApprovalElapsedDeadline.dispatch

    def retry_after_early_stop(self, option='c', kind='at-capacity', *,
                              stop='read-error', restart=False, remaining=5,
                              correction=True, approve=True):
        original_setup = self.setup_system

        def setup(*args, **kwargs):
            original_setup(*args, **kwargs)
            worker = self.workers['U1']
            original_run = worker.gate.run

            def run(action):
                self.last_action = action
                return original_run(action)

            worker.gate.run = run  # observation only
            original_pages = worker.live.client.pages
            self.stops = []

            def pages(path, **kwargs):
                # round94.dispatch's outer wrapper has just waited 25s on the
                # third read, AFTER consuming the approval. Its clocks move
                # forward only 0.5 wall seconds after a backward correction.
                # The initial ordinary definite failure has no `reads` yet.
                if path == '/conversations' and getattr(self, 'reads', 0) == 3:
                    self.stops.append(stop)
                    if stop == 'read-error':
                        raise RuntimeError('transient remote read failure')
                    if stop == 'chat-changed':
                        self.rows['U1'].append(dict(id='ack', senderUserId='U1',
                            content='Okay, thanks.', createdAt=self.clock.isoformat()))
                    if stop == 'contract-error':
                        original_contract = worker.gate.contract_reader

                        def fail_once(cid):
                            worker.gate.contract_reader = original_contract
                            raise RuntimeError('transient contract read failure')

                        worker.gate.contract_reader = fail_once
                return original_pages(path, **kwargs)

            worker.live.client.pages = pages

        self.setup_system = setup
        first = self.dispatch(option, kind, remaining=remaining,
                              correction=correction, approve=approve)
        worker = self.workers['U1']
        if not approve:
            return first, None
        self.assertEqual(first.outcome, 'error', first)
        self.assertEqual(self.stops, [stop], first)
        self.assertEqual(self.deliveries, [], first)
        self.assertEqual(self.continuous, 7200 - remaining + 25)
        self.assertTrue(self.paused.exists())
        self.assertFalse(worker.journal.spent(first.idempotency_key))
        self.assertIsNone(worker.journal.conn.execute(
            'SELECT used_at FROM approvals WHERE id=?',
            (self.last_action.approval_id,)).fetchone()['used_at'])
        if stop in ('read-error', 'chat-changed'):
            self.assertEqual(self.final_ages, [], first)  # callback never ran
        else:
            self.assertEqual(self.final_ages, [0], first)  # early return

        # No extra time, clock correction, approval, policy change or SQL edit.
        # The transient remote problem is gone. Public run() on the SAME
        # approval, with PAUSED still present, may use a fresh worker/connection.
        if restart:
            worker = self.worker('U1')
        second = worker.gate.run(self.last_action)
        self.assertEqual(self.continuous, 7200 - remaining + 25)
        self.assertTrue(self.paused.exists())
        return first, second

    def assert_expired_retry_stops(self, option='c', kind='at-capacity', **kw):
        first, second = self.retry_after_early_stop(option, kind, **kw)
        self.assertEqual(self.deliveries, [],
            f'Expired approval reused at elapsed {self.continuous}s through '
            f'PAUSED after an early no-send; first={first}; retry={second}')

    def test_DF01_auto_guide_read_failure_must_not_revive_approval(self):
        self.assert_expired_retry_stops('a', 'warmup-guide')

    def test_DF01_released_draft_read_failure_must_not_revive_approval(self):
        self.assert_expired_retry_stops('b', 'at-capacity')

    def test_DF01_mixed_reply_read_failure_must_not_revive_approval(self):
        self.assert_expired_retry_stops()

    def test_DF01_mixed_guide_read_failure_must_not_revive_approval(self):
        self.assert_expired_retry_stops('c', 'warmup-guide')

    def test_DF01_mixed_reply_restart_must_not_revive_approval(self):
        self.assert_expired_retry_stops(restart=True)

    def test_DF01_changed_transport_chat_must_not_revive_approval(self):
        self.assert_expired_retry_stops(stop='chat-changed')

    def test_DF01_final_contract_error_must_not_revive_approval(self):
        self.assert_expired_retry_stops(stop='contract-error')

    def test_control_wall_expiry_blocks_retry_without_correction(self):
        first, second = self.retry_after_early_stop(correction=False)
        self.assertEqual(self.deliveries, [], (first, second))
        self.assertEqual(second.outcome, 'held', second)

    def test_control_valid_approval_restored_after_transient_failure(self):
        first, second = self.retry_after_early_stop(remaining=60)
        self.assertEqual(second.outcome, 'sent', (first, second))
        self.assertEqual(len(self.deliveries), 1)

    def test_control_unapproved_mixed_reply_stays_draft(self):
        first, _ = self.retry_after_early_stop(approve=False)
        self.assertEqual(first.outcome, 'draft', first)
        self.assertEqual(self.stops, [])
        self.assertEqual(self.deliveries, [])

    def test_control_unapproved_draft_option_stays_draft(self):
        first, _ = self.retry_after_early_stop('b', approve=False)
        self.assertEqual(first.outcome, 'draft', first)
        self.assertEqual(self.stops, [])
        self.assertEqual(self.deliveries, [])
