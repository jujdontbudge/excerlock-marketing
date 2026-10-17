import unittest
"""Offline promise regressions. Real Gate, Flow, transport readers and SQLite.

Only remote responses, clock and review verdict are fakes. No network.
Run: python3 -m unittest discover -s out/tests -t .
"""
from datetime import timedelta

from gate import checks, policy
from gate.dispatch import CAPTAIN_TEXT, text_hash
from gate.tests.review3 import support
from gate.tests.review84.test_round84 import Fixture


class LastCallPromises(Fixture):
    def prepare(self, option='c', invite_age=20):
        self.setup_system(option=option, distinct=True)
        self.invited = self.clock - timedelta(hours=invite_age)
        self.contracts['U1'].update(status='pending', createdAt=self.invited.isoformat())
        self.rows['U1'] = [self.raw('invite1',
            'https://app.sideshift.app/campaign-invite/C1', self.invited)]
        self.writes = []
        self.worker1 = self.workers['U1']
        job = self.worker1.job

        def request(method, path, **kwargs):
            self.assertEqual((method, path), ('GET', '/contracts/C1'))
            return {'data': dict(self.contracts['U1'])}

        def reject(method, path, **kwargs):
            self.assertEqual((method, path), ('POST', '/contracts/C1/reject'))
            self.writes.append((self.clock, path))
            return {'data': dict(id='C1', contractorId='U1', status='rejected')}

        from types import SimpleNamespace
        job.contracts_client.request = request
        job.write_client = SimpleNamespace(request=reject)
        return job

    def at_hour(self, hour):
        target = self.invited + timedelta(hours=hour)
        self.elapsed += (target - self.clock).total_seconds()
        self.clock = target

    def last_call(self):
        return policy.render(self.types['contract-reminder-2'], {'First': 'Ada'})

    def promise_row(self, created, edited=None, text=None):
        row = self.raw('last-call', text or self.last_call(),
                       self.invited + timedelta(hours=created))
        if edited is not None:
            row['updatedAt'] = (self.invited + timedelta(hours=edited)).isoformat()
            row['isEdited'] = True
        self.rows['U1'].append(row)
        return row

    def run_withdrawal(self):
        report = self.run_job('U1')
        self.assertFalse(self.deliveries, report)
        return report

    def send_then_remove(self, option='c', approved=False, captain_text=False):
        job = self.prepare(option)
        kind = CAPTAIN_TEXT if captain_text else 'contract-reminder-2'
        action = self.action_for('U1', kind)
        action.fields = {'text': self.last_call()} if captain_text else {'First': 'Ada'}
        if approved:
            action.captain_order = 'Send these exact words once.'
            action.approval_id = self.worker1.journal.approve(action.creator_key,
                kind, action.occurrence, text_hash(self.last_call()), action.captain_order)
        sent = self.worker1.gate.run(action)
        self.assertEqual(sent.outcome, 'sent', sent)
        self.assertEqual(len(self.deliveries), 1)
        self.assertIn(support.withdraw.LAST_CALL, self.deliveries[0]['text'])
        # The confirmed delivery is deleted before a later read observes its row.
        # Its real durable send receipt remains; no journal rows are edited.
        self.assertTrue(any(r['outcome'] == 'sent' and
            support.withdraw.LAST_CALL in r['text'] for r in
            self.j.conn.execute('SELECT * FROM decisions')))
        deleted = self.promise_row(20)
        self.rows['U1'].remove(deleted)
        self.assertFalse(any(support.withdraw.LAST_CALL in m.text for m in
            self.worker1.live.read('chat1', ['U1']).messages))
        self.deliveries.clear()
        self.at_hour(25)  # Five hours after delivery; fresh evidence, no slow reads.
        report = self.run_withdrawal()
        self.assertEqual(self.writes, [],
            f'Confirmed promise was only five hours old; withdrawal: {report}')

    def test_DI01_auto_receipt_survives_deleted_unobserved_last_call(self):
        self.send_then_remove(option='a')

    def test_DI01_mixed_receipt_survives_deleted_unobserved_last_call(self):
        self.send_then_remove()

    def test_DI01_released_draft_receipt_survives_deleted_last_call(self):
        self.send_then_remove(option='b', approved=True)

    def test_DI01_captain_text_receipt_survives_deleted_last_call(self):
        self.send_then_remove(approved=True, captain_text=True)

    def edited_promise(self, *, created=2, edited=21, reinvite=False, unknown=False, option='c'):
        self.prepare(option=option, invite_age=25)
        if reinvite:
            self.rows['U1'].insert(0, self.raw('old-invite',
                'https://app.sideshift.app/campaign-invite/C1',
                self.invited - timedelta(hours=30)))
        row = self.promise_row(created, edited)
        if unknown:
            row.pop('updatedAt')
            row['isEdited'] = True
        live = self.worker1.live.read('chat1', ['U1'])
        promise = next(m for m in live.messages if m.id == 'last-call')
        if unknown:
            self.assertIsNone(checks.content_time(promise))
        else:
            self.assertEqual(checks.content_time(promise),
                             self.invited + timedelta(hours=edited))
        report = self.run_withdrawal()
        self.assertEqual(self.writes, [],
            f'Promise appeared four hours ago (or timing unknown); {report}')

    def test_DI02_edited_in_last_call_gets_twelve_hours_from_edit(self):
        self.edited_promise()

    def test_DI02_repeat_promise_edit_restarts_twelve_hours(self):
        self.edited_promise(created=12)

    def test_DI02_row_created_before_current_reinvite_still_counts_its_new_promise(self):
        self.edited_promise(created=-1, reinvite=True)

    def test_DI02_unknown_edit_time_cannot_authorize_withdrawal(self):
        self.edited_promise(unknown=True)

    def test_DI02_drafts_mode_still_withdraws_before_edited_promise_deadline(self):
        self.edited_promise(option='b')

    def test_DI03_withdraw_due_waits_for_last_call_deadline(self):
        self.prepare(invite_age=25)
        self.promise_row(20)
        report = self.run_withdrawal()
        self.assertEqual(self.writes, [], report)  # actual withdrawal is correctly held
        due = self.j.flags('sideshift:U1', 'withdraw-due')
        self.assertEqual(due, set(),
            f'Not due until hour 32, but recorded as due at hour 25: {report}')

    def kept_invite(self, option='c', approved=False):
        self.prepare(option=option)
        self.j.event('sideshift:U1', 'keep-invite', 'C1',
                     {'reason': 'Keep this invite open for her.'})
        action = self.action_for('U1', 'contract-reminder-2')
        action.fields = {'First': 'Ada'}
        if approved:
            action.captain_order = 'Send the reminder.'
            action.approval_id = self.worker1.journal.approve(action.creator_key,
                action.message_type, action.occurrence,
                text_hash(self.last_call()), action.captain_order)
        d = self.worker1.gate.run(action)
        sent = list(self.deliveries)
        self.deliveries.clear()
        self.promise_row(20)
        self.at_hour(32)
        report = self.run_withdrawal()
        self.assertEqual(self.writes, [], report)
        self.assertIn('the captain said to keep this invite', str(report))
        self.assertEqual(sent, [],
            f'Sent a closure promise despite an existing keep-invite: {d}; {report}')

    def test_DI04_auto_last_call_cannot_promise_to_close_kept_invite(self):
        self.kept_invite(option='a')

    def test_DI04_mixed_last_call_cannot_promise_to_close_kept_invite(self):
        self.kept_invite()

    @unittest.skip('captain 2026-10-15: "when I say send, you send": his own order overrides his earlier keep-invite')
    def test_DI04_released_draft_does_not_clear_keep_invite(self):
        self.kept_invite(option='b', approved=True)

    def test_control_visible_recent_last_call_holds(self):
        self.prepare(invite_age=25)
        self.promise_row(20)
        self.run_withdrawal()
        self.assertEqual(self.writes, [])

    def test_control_observed_then_deleted_last_call_holds(self):
        self.prepare(invite_age=25)
        row = self.promise_row(20)
        self.worker1.live.read('chat1', ['U1'])
        self.rows['U1'].remove(row)
        self.run_withdrawal()
        self.assertEqual(self.writes, [])

    def test_control_elapsed_last_call_allows_silent_withdrawal(self):
        self.prepare(invite_age=25)
        self.promise_row(12)
        self.run_withdrawal()
        self.assertEqual(len(self.writes), 1)

    def test_control_old_twelve_hour_reminder_does_not_invent_new_promise(self):
        self.prepare(invite_age=25)
        self.promise_row(12, text="Hi Ada, your contract invite is still open. "
            "Link your new accounts and sign whenever you're ready.")
        self.run_withdrawal()
        self.assertEqual(len(self.writes), 1)

    def test_control_existing_old_reminder_receipt_does_not_send_changed_words_again(self):
        self.prepare()
        old = "Hi Ada, your contract invite is still open. Link your new accounts and sign whenever you're ready."
        self.promise_row(12, text=old)
        action = self.action_for('U1', 'contract-reminder-2')
        action.fields = {'First': 'Ada'}
        action.contract['inviteGeneration'] = 'invite1'
        from gate.model import Decision
        self.j.record(action, self.worker1.gate.key(self.types[action.message_type], action),
                      Decision('sent', ['historical old wording'], old))
        d = self.worker1.gate.run(action)
        self.assertEqual(d.outcome, 'held', d)
        self.assertIn('already sent', str(d.reasons))
        self.assertEqual(self.deliveries, [])

    def test_control_reinvite_gets_a_new_last_call_round(self):
        self.prepare()
        first = self.action_for('U1', 'contract-reminder-2')
        first.fields = {'First': 'Ada'}
        d = self.worker1.gate.run(first)
        self.assertEqual(d.outcome, 'sent', d)
        self.promise_row(20)
        self.worker1.live.read('chat1', ['U1'])
        self.at_hour(50)
        self.rows['U1'].append(self.raw('invite2',
            'https://app.sideshift.app/campaign-invite/C1', self.clock))
        self.at_hour(70)
        second = self.action_for('U1', 'contract-reminder-2')
        second.fields = {'First': 'Ada'}
        d = self.worker1.gate.run(second)
        self.assertEqual(d.outcome, 'sent', d)
        self.assertEqual(len(self.deliveries), 2)
        self.assertNotEqual(self.deliveries[0]['idempotency_key'],
                            self.deliveries[1]['idempotency_key'])

    def test_control_last_call_at_twenty_four_hours_is_held(self):
        self.prepare(invite_age=25)
        action = self.action_for('U1', 'contract-reminder-2')
        action.fields = {'First': 'Ada'}
        d = self.worker1.gate.run(action)
        self.assertEqual(d.outcome, 'held', d)
        self.assertIn('contract_open', str(d.reasons))
        self.assertEqual(self.deliveries, [])

    def test_control_unapproved_draft_last_call_stays_draft(self):
        self.prepare(option='b')
        action = self.action_for('U1', 'contract-reminder-2')
        action.fields = {'First': 'Ada'}
        d = self.worker1.gate.run(action)
        self.assertEqual(d.outcome, 'draft', d)
        self.assertEqual(self.deliveries, [])
