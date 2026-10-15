"""Offline effect-boundary counterexamples; assertions state required behavior.

Run: python3 -m unittest discover -s out/tests -t .
Only service responses, wall clocks and the model verdict are faked.
Production code is unchanged.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


class ObservedInviteTransition(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, option='a', withdrawal=True, metadata='absent',
                 vanish=False, unchanged=False):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in {'contract-reminder-1', 'contract-reminder-2',
                                                   'warmup-guide', 'ask-app-email'}) else t
                        for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        row = self.rows[0]
        link = row['content']
        row.update(createdAt=(self.clock - timedelta(hours=40 if withdrawal else 7)).isoformat(),
                   content=link if unchanged else 'Earlier unrelated note.')
        if metadata == 'false':
            row['isEdited'] = False
        elif metadata == 'stale':
            row.update(isEdited=True, updatedAt=(self.clock - timedelta(hours=39 if withdrawal else 6.5)).isoformat())
        # At t0, the journal positively establishes that this row was NOT an
        # invitation. The first invite can only have appeared after this read.
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(minutes=15)
        row['content'] = link
        if metadata == 'correct':
            row.update(isEdited=True, updatedAt=self.clock.isoformat())
        self.source.read('chat1', ['U1'])
        if not unchanged:
            self.assertIn(row['id'], checks.changed_messages(self.j.events('sideshift:U1')))
        if vanish:
            self.rows[:] = [self.raw('remaining', 'Thanks for your interest.',
                                    self.clock - timedelta(hours=5))]
        # Every final resource is stable, with all evidence reads completing
        # promptly. The new invitation is at most thirty minutes old.
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CH01_auto_must_not_reject_observed_new_invite_as_forty_hours_old(self):
        report = self.exercise()
        self.assertEqual(self.writes, [], report)

    def test_CH01_all_message_types_drafted_still_must_not_reject_new_invite(self):
        report = self.exercise(option='b')
        self.assertEqual(self.writes, [], report)

    def test_CH01_mixed_mode_must_not_reject_new_invite(self):
        report = self.exercise(option='c')
        self.assertEqual(self.writes, [], report)

    def test_CH01_false_edit_flag_cannot_age_new_invite(self):
        report = self.exercise(metadata='false')
        self.assertEqual(self.writes, [], report)

    def test_CH01_reused_edit_clock_cannot_age_new_invite(self):
        report = self.exercise(metadata='stale')
        self.assertEqual(self.writes, [], report)

    def test_CH01_retained_new_invite_must_not_acquire_old_row_age(self):
        report = self.exercise(vanish=True)
        self.assertEqual(self.writes, [], report)

    def test_CH01_auto_must_not_remind_thirty_minute_invite(self):
        report = self.exercise(withdrawal=False)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_current_edit_clock_preserves_new_invite(self):
        report = self.exercise(metadata='correct')
        self.assertEqual(self.writes, [], report)

    def test_control_unchanged_old_invite_can_be_withdrawn(self):
        report = self.exercise(unchanged=True)
        self.assertEqual(len(self.writes), 1, report)

    def test_control_drafts_contain_premature_reminder(self):
        report = self.exercise(option='b', withdrawal=False)
        self.assertEqual(self.sender.delivered, [], report)


class ObservedSigningTransition(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, withdrawal=False, vanish=False, edited=False):
        self.setup_flow()
        self.writes = []
        if withdrawal:
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
            self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
                self.writes.append((a, kw)) or
                dict(id='C1', contractorId='U1', status='rejected'))
        # A row older than both the contract (60h) and the first invite. Its
        # current signing words demonstrably appeared after this old creation.
        row = dict(id='old-creator-note', senderUserId='U1',
                   createdAt=(self.clock - timedelta(hours=70)).isoformat(), content='')
        self.rows.append(row)
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(minutes=15)
        row['content'] = '📨 Requested handle @ada (tiktok) for this contract.'
        if edited:
            row.update(isEdited=True, updatedAt=self.clock.isoformat())
        self.source.read('chat1', ['U1'])
        self.assertIn(row['id'], checks.changed_messages(self.j.events('sideshift:U1')))
        if vanish:
            self.rows.pop()
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CH01_observed_new_handle_request_must_stop_reminder(self):
        report = self.exercise()
        self.assertEqual(self.sender.delivered, [], report)

    def test_CH01_observed_new_handle_request_must_stop_draft_only_withdrawal(self):
        report = self.exercise(withdrawal=True)
        self.assertEqual(self.writes, [], report)

    def test_CH01_retained_new_handle_request_must_stop_draft_only_withdrawal(self):
        report = self.exercise(withdrawal=True, vanish=True)
        self.assertEqual(self.writes, [], report)

    def test_control_current_handle_request_edit_clock_blocks_withdrawal(self):
        report = self.exercise(withdrawal=True, edited=True)
        self.assertEqual(self.writes, [], report)

