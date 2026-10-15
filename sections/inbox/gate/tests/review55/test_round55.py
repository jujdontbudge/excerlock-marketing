"""Required-behavior tests; four intentionally fail on the reviewed snapshot.

Real Flow, SideShiftLive, Gate, ContactsMCP boundary and private SQLite journal.
Only remote responses, time and the review verdict are fakes. No network.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


AUTOMATIC_IN_C = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}


class EditedInviteClock(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def mode(self, option):
        self.g.types = {
            key: replace(t, mode='draft' if option == 'b' or (option == 'c' and key not in AUTOMATIC_IN_C) else 'auto')
            for key, t in self.g.types.items()
        }

    def prepare_replacement(self, *, old_hours, option, edit=True):
        self.setup_flow()
        self.mode(option)
        self.writes = []
        self.job.write_client = SimpleNamespace(request=self.reject)
        # Initially this old message invites her to a DIFFERENT contract.
        # C1 exists but has never been invited in this chat. The first complete
        # Flow read records the old text and correctly takes no action on C1.
        self.rows[0].update(
            createdAt=(self.clock - timedelta(hours=old_hours)).isoformat(),
            content='https://app.sideshift.app/campaign-invite/OLD',
        )
        first = self.job.run()
        self.assertTrue(any('no invite link' in line for line in first), first)
        self.assertEqual(self.writes, [])
        self.assertEqual(self.sender.delivered, [])
        self.clock += timedelta(minutes=15)
        self.introduced = self.clock
        if edit:
            # Correct the contract URL by editing the old native row. Its
            # createdAt remains old; updatedAt is when C1's link first appears.
            self.rows[0].update(
                content='https://app.sideshift.app/campaign-invite/C1',
                updatedAt=self.introduced.isoformat(), isEdited=True,
            )
        else:
            # Control: introduce exactly the same link as a new native row.
            self.rows.append(self.raw('new-invite',
                'https://app.sideshift.app/campaign-invite/C1', self.introduced))
        # Nothing changes during any check or read. The edit is a full hour
        # before this run, far outside the accepted ten-second evidence window.
        self.clock += timedelta(hours=1)

    def reject(self, *args, **kwargs):
        self.writes.append((args, kwargs))
        return dict(id='C1', contractorId='U1', status='rejected')

    def test_BQ01_option_b_recently_introduced_invite_cannot_be_withdrawn(self):
        self.prepare_replacement(old_hours=40, option='b')
        self.assertTrue(all(t.effective_mode == 'draft' for t in self.g.types.values()))
        report = self.job.run()
        self.assertEqual(self.writes, [],
            f'C1 was first invited one hour ago, but all-draft Flow rejected it: {report}; {self.writes}')

    def test_BQ01_option_c_recently_introduced_invite_cannot_be_withdrawn(self):
        self.prepare_replacement(old_hours=40, option='c')
        report = self.job.run()
        self.assertEqual(self.writes, [],
            f'C1 was first invited one hour ago, but selective automation rejected it: {report}; {self.writes}')

    def test_BQ01_automatic_reminder_cannot_use_the_previous_contract_link_age(self):
        self.prepare_replacement(old_hours=7, option='c')
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [],
            f'First C1 invite is one hour old, but its six-hour reminder was sent: {report}; {self.sender.delivered}')

    def test_control_new_row_recent_invite_is_not_withdrawn_in_draft_mode(self):
        self.prepare_replacement(old_hours=40, option='b', edit=False)
        report = self.job.run()
        self.assertEqual(self.writes, [], report)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_new_row_recent_invite_is_not_reminded(self):
        self.prepare_replacement(old_hours=7, option='c', edit=False)
        report = self.job.run()
        self.assertEqual(self.writes, [], report)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_unedited_old_current_invite_can_be_withdrawn(self):
        self.setup_flow()
        self.mode('b')
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.writes = []
        self.job.write_client = SimpleNamespace(request=self.reject)
        report = self.job.run()
        self.assertEqual(len(self.writes), 1, report)
        self.assertIn('withdraw withdrawn', report[0])

    def test_control_unedited_seven_hour_invite_can_get_automatic_reminder(self):
        self.setup_flow()
        self.mode('c')
        report = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, report)
        self.assertIn('contract-reminder-1 sent', report[0])

    def test_control_original_link_and_replacement_are_both_in_the_journal(self):
        self.prepare_replacement(old_hours=40, option='b')
        self.source.read('chat1', ['U1'])
        history = checks.with_history(self.source.read('chat1', ['U1']), self.j.events('sideshift:U1'))
        links = {m.text for m in history.messages}
        self.assertIn('https://app.sideshift.app/campaign-invite/OLD', links)
        self.assertIn('https://app.sideshift.app/campaign-invite/C1', links)

    def creator_activity(self, *, edit):
        self.setup_flow()
        self.mode('b')
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='trying', senderUserId='U1', content='Hi!',
                              createdAt=(self.clock - timedelta(hours=30)).isoformat()))
        old = self.source.read('chat1', ['U1']).messages[-1]
        self.j.event('sideshift:U1', 'answered', checks.mark(old), {'by': 'captain'})
        self.clock += timedelta(minutes=15)
        text = 'I am still trying to create my accounts.'
        if edit:
            self.rows[-1].update(content=text, updatedAt=self.clock.isoformat(), isEdited=True)
        else:
            self.rows.append(dict(id='new-trying', senderUserId='U1', content=text,
                                  createdAt=self.clock.isoformat()))
        self.clock += timedelta(hours=1)
        current = next(m for m in self.source.read('chat1', ['U1']).messages if m.text == text)
        # Settle the words she wrote, as in BB01's existing activity test.
        # The independent "she has been active in the last 24h" rule still applies.
        self.j.event('sideshift:U1', 'answered', checks.mark(current), {'by': 'captain'})
        self.writes = []
        self.job.write_client = SimpleNamespace(request=self.reject)
        return self.job.run()

    def test_BQ01_recent_creator_edit_cannot_lose_the_24_hour_activity_veto(self):
        report = self.creator_activity(edit=True)
        self.assertEqual(self.writes, [],
            f'She wrote that she is still trying one hour ago, but her invite was withdrawn: {report}; {self.writes}')

    def test_control_same_recent_activity_as_a_new_row_blocks_withdrawal(self):
        report = self.creator_activity(edit=False)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in line for line in report), report)
