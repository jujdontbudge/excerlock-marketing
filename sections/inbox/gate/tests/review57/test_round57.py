"""Offline counterexamples: assertions state the required safe behavior.

Real SideShiftLive, Flow, Gate, ContactsMCP boundary and private SQLite journal.
Only service responses, time and the SEND review verdict are fakes.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import LiveReadError
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


class Round57(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def drafts_and_writer(self):
        self.g.types = {key: replace(t, mode='draft') for key, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))

    def rescued_zero_edit(self, *, withdrawal, flag=0):
        self.setup_flow()
        if withdrawal:
            self.drafts_and_writer()
        self.rows[0].update(createdAt=(self.clock - timedelta(hours=40 if withdrawal else 7)).isoformat(),
                            content='https://app.sideshift.app/campaign-invite/OLD')
        self.source.read('chat1', ['U1'])
        # isEdited is malformed; even though 0 == False, 0 is not a JSON boolean.
        # C1 was introduced only one hour ago, as the retained updatedAt says.
        self.rows[0].update(content='https://app.sideshift.app/campaign-invite/C1',
                            updatedAt=(self.clock - timedelta(hours=1)).isoformat(), isEdited=flag)
        with self.assertRaises(LiveReadError):
            self.source.read('chat1', ['U1'])
        # All final reads are complete and stable, 15 minutes after the failure.
        self.rows[:] = [self.raw('other', 'Thanks for your interest.', self.clock - timedelta(hours=5))]
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BS01_numeric_zero_edit_flag_cannot_authorize_withdrawal(self):
        report = self.rescued_zero_edit(withdrawal=True)
        self.assertEqual(self.writes, [], f'Numeric zero was rescued as unedited, rejecting a 75-minute invite: {report}')

    def test_BS01_numeric_zero_edit_flag_cannot_authorize_reminder(self):
        report = self.rescued_zero_edit(withdrawal=False)
        self.assertEqual(self.sender.delivered, [], f'Numeric zero was rescued as unedited, reminding at 75 minutes: {report}')

    def test_control_other_garbled_edit_flag_holds_withdrawal(self):
        report = self.rescued_zero_edit(withdrawal=True, flag='false')
        self.assertEqual(self.writes, [], report)

    def inverted_activity(self, *, inverted):
        self.setup_flow()
        self.drafts_and_writer()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        row = dict(id='trying', senderUserId='U1', content='I am still trying to create my accounts.',
                   createdAt=(self.clock - timedelta(hours=1)).isoformat(), isEdited=True,
                   updatedAt=(self.clock - timedelta(hours=30) if inverted else self.clock - timedelta(minutes=45)).isoformat())
        self.rows.append(row)
        observed = self.source.read('chat1', ['U1'])
        message = next(m for m in observed.messages if m.id == 'trying')
        self.j.event('sideshift:U1', 'answered', checks.mark(message), {'by': 'captain'})
        # Creation time positively proves recent activity. Settling its words
        # must not clear the separate 24-hour activity guard.
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BS02_older_edit_timestamp_cannot_erase_recent_creation_activity(self):
        report = self.inverted_activity(inverted=True)
        self.assertEqual(self.writes, [], f'75-minute-old creator message lost its activity guard to older updatedAt: {report}')

    def test_control_chronological_activity_blocks_withdrawal(self):
        report = self.inverted_activity(inverted=False)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in line for line in report), report)

    def inverted_invite(self, *, withdrawal, inverted=True):
        self.setup_flow()
        if withdrawal:
            self.drafts_and_writer()
        # Individually valid aware timestamps, but an edit cannot precede
        # the row's creation. This must hold or use the later known activity.
        self.rows[0].update(createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                            isEdited=True,
                            updatedAt=(self.clock - timedelta(hours=40 if withdrawal else 7)
                                       if inverted else self.clock - timedelta(minutes=45)).isoformat())
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BS02_edit_before_creation_cannot_age_invite_into_withdrawal(self):
        report = self.inverted_invite(withdrawal=True)
        self.assertEqual(self.writes, [], f'Created 75 minutes ago, but older edit time authorized withdrawal: {report}')

    def test_BS02_edit_before_creation_cannot_age_invite_into_reminder(self):
        report = self.inverted_invite(withdrawal=False)
        self.assertEqual(self.sender.delivered, [], f'Created 75 minutes ago, but older edit time authorized reminder: {report}')

    def test_control_recent_chronological_invite_is_not_withdrawn(self):
        report = self.inverted_invite(withdrawal=True, inverted=False)
        self.assertEqual(self.writes, [], report)
