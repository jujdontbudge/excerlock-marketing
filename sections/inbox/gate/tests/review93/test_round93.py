"""Offline authorization-boundary regressions; DC01 assertions intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, ContactsMCP, SideShiftLive and file-backed SQLite. Only remote
responses, clocks and the review verdict are fake; inherited setup forbids HTTP.
"""
from datetime import timedelta
from unittest.mock import patch

from gate import clock, policy
from gate.dispatch import text_hash
from gate.tests.review3 import support
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review92 import test_round92


class Round92Verification(test_round92.FinalSendSleep,
                          test_round92.Round91ContinuousControls):
    """All ten original round-92 tests, unchanged."""


class ApprovalAtSend(Fixture):
    def dispatch(self, option='a', *, seconds=25, remaining=5,
                 approve=True, delayed_read=True, kind='warmup-guide'):
        self.setup_system(option=option, distinct=True)
        worker = self.workers['U1']
        self.paused.touch()  # only the captain's still-valid approval may bypass
        action = self.action_for('U1', kind)
        if kind == 'at-capacity':
            action.fields = {'First': 'Ada'}
            self.rows['U1'].append(dict(id='capacity', senderUserId='U1',
                content="I don't have capacity for another campaign right now.",
                createdAt=(self.clock - timedelta(hours=2)).isoformat()))
        kind = self.types[action.message_type]
        wall = lambda: self.clock.timestamp()
        patched = patch('gate.journal.time.time', side_effect=wall)
        patched.start()
        self.addCleanup(patched.stop)
        patched = patch('gate.clock._continuous', side_effect=lambda: self.elapsed)
        patched.start()
        self.addCleanup(patched.stop)
        self.expires = None
        if approve:
            action.captain_order = 'Send this exact message once.'
            action.approval_id = worker.journal.approve(action.creator_key,
                action.message_type, action.occurrence,
                text_hash(policy.render(kind, action.fields)),
                action.captain_order)  # production default: 7,200 seconds
            self.expires = wall() + 7200

            # First call reaches the real send boundary, which returns a
            # DEFINITE no-send. Gate restores its one-use approval, explicitly
            # supporting retry (S07); no delivery or live claim remains.
            original_post = worker.sender._post

            def failed(body):
                if body['params']['name'] == 'send_message':
                    import json
                    from types import SimpleNamespace
                    return SimpleNamespace(text=json.dumps(dict(result=dict(
                        content=[dict(type='text', text=json.dumps(dict(
                            status='failed', error='definitely not sent')))]))))
                return original_post(body)

            worker.sender._post = failed
            first = worker.gate.run(action)
            self.assertEqual(first.outcome, 'error', first)
            self.assertEqual(self.deliveries, [])
            self.assertFalse(worker.journal.spent(first.idempotency_key))
            record = worker.journal.conn.execute(
                'SELECT used_at FROM approvals WHERE id=?',
                (action.approval_id,)).fetchone()
            self.assertIsNone(record['used_at'])
            worker.sender._post = original_post

            # Retry while the original approval is still valid. No change to
            # approval records or to a decision function; ordinary passage of
            # time only. The retry acquires its own fresh 900-second chat lock.
            self.elapsed += 7200 - remaining
            self.clock += timedelta(seconds=7200 - remaining)

        original_pages = worker.live.client.pages
        self.reads, self.delayed, self.effects, self.final_ages = 0, [], [], []
        original_recheck = worker.gate._final_recheck

        def recheck(*args, **kwargs):
            since = clock.Since(lambda: self.clock)
            result = original_recheck(*args, **kwargs)
            self.final_ages.append(since.age())
            return result

        worker.gate._final_recheck = recheck  # observe; never changes a veto

        def pages(path, **kwargs):
            if path == '/conversations':
                self.reads += 1
                # Gate's first read, post-review read, then the transport's own
                # read AFTER use_approval(). Its final callback will re-read
                # all chat/contract/Contacts evidence quickly and normally.
                if delayed_read and self.reads == 3:
                    record = worker.journal.conn.execute(
                        'SELECT used_at FROM approvals WHERE id=?',
                        (action.approval_id,)).fetchone()
                    self.assertIsNotNone(record['used_at'])
                    self.delayed.append(self.clock)
                    self.elapsed += seconds
                    self.clock += timedelta(seconds=seconds)
            return original_pages(path, **kwargs)

        worker.live.client.pages = pages
        original_post = worker.sender._post

        def post(body):
            if body['params']['name'] == 'send_message':
                self.effects.append(dict(at=self.clock.isoformat(),
                    seconds_after_expiry=wall() - self.expires,
                    paused=self.paused.exists()))
            return original_post(body)

        worker.sender._post = post
        result = worker.gate.run(action)
        if approve and delayed_read and remaining > 0:
            self.assertEqual(len(self.delayed), 1, result)
            self.assertEqual(self.reads, 4, result)
        return result

    def assert_expiry_stops(self, option, kind='warmup-guide'):
        result = self.dispatch(option, kind=kind)
        self.assertEqual((self.clock - support.NOW).total_seconds(), 7220)
        self.assertEqual(self.final_ages, [0], result)
        self.assertEqual(self.deliveries, [],
            f'Consumed approval expired 20 seconds before the real send '
            f'request, with PAUSED still on: {self.effects}; {result}')

    def test_DC01_auto_must_not_send_twenty_seconds_after_approval_expiry(self):
        self.assert_expiry_stops('a')

    def test_DC01_drafts_must_not_send_twenty_seconds_after_approval_expiry(self):
        self.assert_expiry_stops('b')

    def test_DC01_mixed_must_not_send_twenty_seconds_after_approval_expiry(self):
        self.assert_expiry_stops('c')

    def test_DC01_draft_reply_must_not_send_after_approval_expiry(self):
        self.assert_expiry_stops('b', kind='at-capacity')

    def test_DC01_mixed_reply_must_not_send_after_approval_expiry(self):
        self.assert_expiry_stops('c', kind='at-capacity')

    def test_control_approval_still_valid_after_delayed_transport_read_sends(self):
        result = self.dispatch(remaining=60)
        self.assertEqual(result.outcome, 'sent', result)
        self.assertEqual(len(self.deliveries), 1)
        self.assertEqual(self.effects[0]['seconds_after_expiry'], -35)

    def test_control_expired_before_retry_stops_at_entry(self):
        result = self.dispatch(remaining=-20)
        self.assertEqual(result.outcome, 'held', result)
        self.assertEqual(self.reads, 0)
        self.assertEqual(self.deliveries, [])

    def test_control_paused_without_captain_approval_stops_at_entry(self):
        result = self.dispatch(approve=False)
        self.assertEqual(result.outcome, 'held', result)
        self.assertEqual(self.reads, 0)
        self.assertEqual(self.deliveries, [])

    def test_control_unexpired_immediate_retry_sends(self):
        result = self.dispatch(delayed_read=False)
        self.assertEqual(result.outcome, 'sent', result)
        self.assertEqual(len(self.deliveries), 1)
        self.assertEqual(self.effects[0]['seconds_after_expiry'], -5)


class PreGrantClockVerification(Fixture):
    def test_pre_grant_counts_sleep_in_its_own_last_journal_wait(self):
        import inspect
        from dataclasses import replace
        from types import SimpleNamespace
        import grant

        self.setup_system(distinct=True)
        worker = self.workers['U1']
        self.continuous, delays, grants = 0, [], []
        patched = patch('gate.clock._continuous', side_effect=lambda: self.continuous)
        patched.start()
        self.addCleanup(patched.stop)
        self.rows['U1'].append(dict(id='email1', senderUserId='U1',
            content='ada@example.com',
            createdAt=(self.clock - timedelta(hours=2)).isoformat()))
        original_spent = worker.journal.spent

        def spent(key):
            if not delays and any(f.function == '_pre_grant' for f in inspect.stack()):
                # The enclosing guard, AFTER _final_recheck has returned, waits
                # on its last journal read. Sleep plus wall-clock correction.
                delays.append(key)
                self.continuous += 25
                self.elapsed += 0.5
                self.clock += timedelta(seconds=0.5)
            return original_spent(key)

        worker.journal.spent = spent

        def runner(argv, **kwargs):
            verb, email = argv[1:3]
            if verb == 'grant':
                grants.append(email)
            return SimpleNamespace(returncode=0, stderr='',
                stdout=f'{"NONE" if verb == "check" else "GRANTED"}: {email}')

        worker.gate.granter = lambda a: grant.grant(worker.journal,
            a.creator_key, a.fields['email'], 'offline review', runner=runner)
        result = worker.gate.run(replace(self.action_for('U1', 'app-access'),
                                       fields={'email': 'ada@example.com'}))
        self.assertEqual(len(delays), 1, result)
        self.assertIn('pre-grant checks took longer than 10s', str(result))
        self.assertEqual((grants, self.deliveries), ([], []), result)
