"""Offline required-behavior regressions. Production sources are unchanged."""
from dataclasses import replace
from datetime import timedelta

from gate import checks, policy
from gate.tests.review3.support import Case, NOW
from gate.tests.review35 import test_round35 as fixtures


class ContradictoryDeliveryClock(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, vanish=False, option='a', metadata='absent', change=True):
        self.setup_flow()
        self.clock = NOW - timedelta(hours=4)
        text = policy.render(self.g.types['contract-reminder-1'], {'First': 'Ada'})
        row = self.raw('captain-note', 'Earlier unrelated note.' if change else text,
                       NOW - timedelta(hours=10))
        if metadata == 'false':
            row['isEdited'] = False
        elif metadata == 'stale':
            row.update(isEdited=True, updatedAt=(NOW - timedelta(hours=9)).isoformat())
        self.rows.append(row)
        self.source.read('chat1', ['U1'])
        # This read establishes that the note still had DIFFERENT words three
        # hours AFTER the current invitation. Its creation date therefore cannot
        # prove that the reminder text predates this invitation.
        self.assertLess(checks.invite_time(self.source.read('chat1'), self.current), self.clock)
        self.clock += timedelta(hours=1)
        row['content'] = text
        if metadata == 'correct':
            row.update(isEdited=True, updatedAt=self.clock.isoformat())
        self.source.read('chat1', ['U1'])
        if vanish:
            self.rows.pop()
        self.clock += timedelta(hours=3)
        self.assertEqual(checks.quiet_hours(self.clock), [])
        automatic_in_c = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in automatic_in_c) else t
                        for k, t in self.g.types.items()}
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CG01_observed_edit_without_edit_flag_cannot_be_exempted_as_old_delivery(self):
        report = self.exercise()
        self.assertEqual(self.sender.delivered, [],
                         f'Already-delivered current-round reminder was sent again: {report}')

    def test_CG01_observed_edit_with_false_flag_cannot_be_exempted(self):
        report = self.exercise(metadata='false')
        self.assertEqual(self.sender.delivered, [], report)

    def test_CG01_observed_edit_with_unchanged_old_edit_time_cannot_be_exempted(self):
        report = self.exercise(metadata='stale')
        self.assertEqual(self.sender.delivered, [], report)

    def test_CG01_retained_observed_edit_cannot_be_exempted(self):
        report = self.exercise(vanish=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CG01_option_c_also_duplicates_current_round_reminder(self):
        report = self.exercise(option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_unchanged_proven_old_text_allows_current_round(self):
        report = self.exercise(change=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_drafts_contain_the_duplicate(self):
        report = self.exercise(option='b')
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_correct_current_round_edit_clock_blocks_duplicate(self):
        report = self.exercise(metadata='correct')
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('already in the chat' in line for line in report), report)
