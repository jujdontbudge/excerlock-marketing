import unittest
"""Offline review-100 regressions. Real Gate, Flow, ContactsMCP and SQLite.

Only remote responses, clocks and the review verdict are faked by the inherited
fixture. Its HTTP implementation forbids network. Production files are unchanged.
Run: python3 -m unittest discover -s out/tests -t .
"""
from gate.dispatch import CAPTAIN_TEXT, text_hash
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review99 import test_round99 as previous


class PromiseFixture(Fixture):
    # Only fixture methods; prior regression assertions run in verification.
    prepare = previous.LastCallPromises.prepare
    at_hour = previous.LastCallPromises.at_hour
    last_call = previous.LastCallPromises.last_call
    promise_row = previous.LastCallPromises.promise_row
    run_withdrawal = previous.LastCallPromises.run_withdrawal


class UnrecognizedPromises(PromiseFixture):
    def check_promise(self, text, option='c', edited=False, receipt=False):
        self.prepare(option=option, invite_age=20 if receipt else 25)
        if receipt:
            action = self.action_for('U1', CAPTAIN_TEXT)
            action.fields = {'text': text}
            action.captain_order = 'Send these exact words once.'
            action.approval_id = self.j.approve(action.creator_key,
                action.message_type, action.occurrence, text_hash(text),
                action.captain_order)
            sent = self.worker1.gate.run(action)
            self.assertEqual(sent.outcome, 'sent', sent)
            self.assertEqual(len(self.deliveries), 1)
            self.deliveries.clear()
            self.at_hour(25)
        else:
            self.promise_row(2 if edited else 20,
                             edited=20 if edited else None, text=text)
        report = self.run_withdrawal()
        self.assertEqual(self.writes, [],
            f'Invite closed five hours after an explicit twelve-hour promise: {report}')

    def test_DJ01_mixed_spelled_twelve_more_hours_must_hold_withdrawal(self):
        self.check_promise('Your ExcerLock invite stays open for twelve more hours, then we will close it.')

    def test_DJ01_auto_additional_hours_must_hold_withdrawal(self):
        self.check_promise('Your ExcerLock invite stays open for 12 additional hours, then we will close it.', option='a')

    def test_DJ01_drafts_mode_still_must_honor_manual_promise(self):
        self.check_promise('Your ExcerLock invite stays open for twelve more hours, then we will close it.', option='b')

    def test_DJ01_edited_spelled_promise_must_hold_withdrawal(self):
        self.check_promise('Your ExcerLock invite stays open for twelve more hours, then we will close it.', edited=True)

    def test_DJ01_confirmed_captain_receipt_must_honor_spelled_promise(self):
        self.check_promise('Your ExcerLock invite stays open for twelve more hours, then we will close it.', receipt=True)

    def test_control_numeric_more_hours_is_honored(self):
        self.check_promise('Your ExcerLock invite stays open for 12 more hours, then we will close it.')

    def test_control_one_more_day_is_honored(self):
        self.check_promise('Your ExcerLock invite stays open for one more day, then we will close it.')

    @unittest.skip('superseded 2026-10-15: "when I say send, you send": a captain order is not held for contract state or keep-invite')
    def test_DJ01_unrecognized_promise_also_bypasses_keep_invite_veto(self):
        self.prepare()
        self.j.event('sideshift:U1', 'keep-invite', 'C1', {'reason': 'Keep it open.'})
        words = 'Your ExcerLock invite stays open for twelve more hours, then we will close it.'
        action = self.action_for('U1', CAPTAIN_TEXT)
        action.fields = {'text': words}
        action.captain_order = 'Send these exact words once.'
        action.approval_id = self.j.approve(action.creator_key,
            action.message_type, action.occurrence, text_hash(words), action.captain_order)
        result = self.worker1.gate.run(action)
        self.assertEqual(self.deliveries, [], result)


class ClosedInvitePromises(PromiseFixture):
    def closed_promise(self, option='c', status='rejected', kind=CAPTAIN_TEXT, age=25):
        self.prepare(option=option, invite_age=age)
        self.contracts['U1']['status'] = status
        action = self.action_for('U1', kind)
        words = self.last_call()
        action.fields = {'text': words} if kind == CAPTAIN_TEXT else {'First': 'Ada'}
        action.captain_order = 'Send these exact words once.'
        action.approval_id = self.j.approve(action.creator_key, kind,
            action.occurrence, text_hash(words), action.captain_order)
        result = self.worker1.gate.run(action)
        return result

    @unittest.skip('superseded 2026-10-15: "when I say send, you send": a captain order is not held for contract state or keep-invite')
    def test_DJ02_mixed_captain_text_must_not_claim_rejected_invite_stays_open(self):
        result = self.closed_promise()
        self.assertEqual(self.deliveries, [], result)

    @unittest.skip('superseded 2026-10-15: "when I say send, you send": a captain order is not held for contract state or keep-invite')
    def test_DJ02_drafts_release_must_not_claim_rejected_invite_stays_open(self):
        result = self.closed_promise(option='b')
        self.assertEqual(self.deliveries, [], result)

    @unittest.skip('superseded 2026-10-15: "when I say send, you send": a captain order is not held for contract state or keep-invite')
    def test_DJ02_auto_captain_text_must_not_claim_rejected_invite_stays_open(self):
        result = self.closed_promise(option='a')
        self.assertEqual(self.deliveries, [], result)

    @unittest.skip('superseded 2026-10-15: "when I say send, you send": a captain order is not held for contract state or keep-invite')
    def test_DJ02_already_signed_invite_cannot_get_last_call_as_captain_text(self):
        result = self.closed_promise(status='active')
        self.assertEqual(self.deliveries, [], result)

    @unittest.skip('superseded 2026-10-15: "when I say send, you send": a captain order is not held for contract state or keep-invite')
    def test_control_released_template_checks_rejected_contract(self):
        result = self.closed_promise(kind='contract-reminder-2')
        self.assertEqual(result.outcome, 'held', result)
        self.assertEqual(self.deliveries, [], result)

    def test_control_captain_text_on_current_pending_invite_can_send(self):
        result = self.closed_promise(status='pending', age=20)
        self.assertEqual(result.outcome, 'sent', result)
        self.assertEqual(len(self.deliveries), 1)


class DefiniteFailurePromises(PromiseFixture):
    def no_send_then_due(self, option='c', approved=False):
        self.prepare(option=option)
        action = self.action_for('U1', 'contract-reminder-2')
        action.fields = {'First': 'Ada'}
        if approved:
            action.captain_order = 'Send the reminder once.'
            action.approval_id = self.j.approve(action.creator_key,
                action.message_type, action.occurrence, text_hash(self.last_call()),
                action.captain_order)
        original = self.worker1.live.client.pages
        reads = []

        def pages(path, **kwargs):
            if path == '/conversations':
                reads.append(path)
                if len(reads) == 3:  # ContactsMCP's final read, after dispatch intent
                    raise RuntimeError('transient SideShift read failure')
            return original(path, **kwargs)

        self.worker1.live.client.pages = pages
        result = self.worker1.gate.run(action)
        self.worker1.live.client.pages = original
        self.assertEqual(len(reads), 3, result)
        self.assertEqual(result.outcome, 'error', result)
        self.assertEqual(self.deliveries, [])
        self.assertEqual(self.j.delivery(result.idempotency_key), 'none')
        self.assertFalse(self.j.spent(result.idempotency_key))
        self.at_hour(25)
        report = self.run_withdrawal()
        self.assertEqual(len(self.writes), 1,
            f'No last-call was delivered, but a closed dispatch attempt postpones the 24h withdrawal: {report}')

    def test_DJ03_mixed_definite_no_send_must_not_create_promise(self):
        self.no_send_then_due()

    def test_DJ03_auto_definite_no_send_must_not_create_promise(self):
        self.no_send_then_due(option='a')

    def test_DJ03_released_draft_definite_no_send_must_not_create_promise(self):
        self.no_send_then_due(option='b', approved=True)

    def test_control_uncertain_send_must_preserve_possible_promise(self):
        self.prepare()
        original = self.worker1.sender._post

        def post(body):
            if body.get('params', {}).get('name') == 'send_message':
                raise RuntimeError('response lost after request could have left')
            return original(body)

        self.worker1.sender._post = post
        action = self.action_for('U1', 'contract-reminder-2')
        action.fields = {'First': 'Ada'}
        result = self.worker1.gate.run(action)
        self.worker1.sender._post = original
        self.assertEqual(result.outcome, 'uncertain', result)
        self.at_hour(25)
        self.run_withdrawal()
        self.assertEqual(self.writes, [])

