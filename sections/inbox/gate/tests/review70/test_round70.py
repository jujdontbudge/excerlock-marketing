"""Offline regressions: real Flow/Gate/SideShiftLive/ContactsMCP/SQLite boundary.

Only remote records, the clock and model verdict are faked. Assertions describe
required behavior. Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta

from gate import checks
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


AUTOMATIC_IN_C = {'contract-reminder-1', 'contract-reminder-2',
                  'warmup-guide', 'ask-app-email'}


class ReinviteReminder(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, option='a', delivery='visible', reinvite=True):
        self.setup_flow()
        first = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, first)
        initial_send = self.sender.delivered[0]
        self.assertEqual(initial_send['idempotency_key'],
                         'gate:contract-reminder-1:sideshift:U1:C1:invite1')
        if delivery != 'journal-only':
            # A successful real send normally appears in SideShift's next read.
            self.rows.append(self.raw('first-reminder', initial_send['text'], self.clock))
            observed = self.source.read('chat1', ['U1'])
            self.assertTrue(any(m.id == 'first-reminder' for m in observed.messages))
            if delivery == 'vanished':
                self.rows.pop()
            elif delivery == 'deleted':
                self.rows[-1]['isDeleted'] = True
        self.clock += timedelta(hours=1)
        if reinvite:
            self.rows.append(self.raw('invite2',
                'https://app.sideshift.app/campaign-invite/C1', self.clock))
        self.clock += timedelta(hours=6 if reinvite else 2)
        # Both invitations and the first send are stable for hours; all final
        # reads agree, the gap has elapsed and Eastern quiet hours allow sending.
        self.assertEqual(checks.quiet_hours(self.clock), [])
        self.g.types = {k: replace(t, mode='draft') if option == 'b'
                        or (option == 'c' and k not in AUTOMATIC_IN_C) else t
                        for k, t in self.g.types.items()}
        live = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        current_round = 'invite2' if reinvite else 'invite1'
        self.assertEqual(checks.invite_generation(live, self.current), current_round)
        key = f'gate:contract-reminder-1:sideshift:U1:C1:{current_round}'
        self.assertEqual(self.j.spent(key), not reinvite)
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        if reinvite and len(self.sender.delivered) == 2:
            self.assertEqual(self.sender.delivered[1]['idempotency_key'], key)
            self.assertEqual(self.sender.delivered[1]['text'], initial_send['text'])
        return report

    def test_CF01_option_a_new_round_must_get_its_due_reminder(self):
        report = self.exercise()
        self.assertEqual(len(self.sender.delivered), 2,
            f'New round has an unspent key but its six-hour reminder never sends: {report}')

    def test_CF01_option_c_new_round_must_get_its_due_reminder(self):
        report = self.exercise(option='c')
        self.assertEqual(len(self.sender.delivered), 2,
            f'Scheduled reminders are automatic in option c, but the new round is suppressed: {report}')

    def test_CF01_deleted_prior_round_delivery_must_not_suppress_new_round(self):
        report = self.exercise(delivery='deleted')
        self.assertEqual(len(self.sender.delivered), 2,
            f'A deleted old-round delivery prevents the new round reminder: {report}')

    def test_CF01_retained_prior_round_delivery_must_not_suppress_new_round(self):
        report = self.exercise(delivery='vanished')
        self.assertEqual(len(self.sender.delivered), 2,
            f'The retained old-round delivery prevents the new round reminder: {report}')

    def test_control_journal_only_prior_send_allows_new_round(self):
        # This is the coverage gap in review58's BT03 control: delivery is
        # confirmed locally but its text never appears in the source chat.
        report = self.exercise(delivery='journal-only')
        self.assertEqual(len(self.sender.delivered), 2, report)

    def test_control_option_b_does_not_automatically_send_new_round(self):
        report = self.exercise(option='b')
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_same_round_still_cannot_send_twice(self):
        report = self.exercise(reinvite=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_same_round_with_journal_only_delivery_cannot_send_twice(self):
        report = self.exercise(reinvite=False, delivery='journal-only')
        self.assertEqual(len(self.sender.delivered), 1, report)
