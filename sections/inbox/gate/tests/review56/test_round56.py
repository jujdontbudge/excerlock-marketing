"""Required-behavior counterexamples, offline and against unchanged production code.

Run: python3 -m unittest discover -s out/tests -t .
The real Flow, SideShiftLive, Gate, SQLite journal and ContactsMCP send boundary
run with fake service responses, an offline SEND verdict and a private clock.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import LiveReadError
from gate.handles import Profile
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


class Review56(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def drafts(self):
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}

    def enable_withdrawal(self):
        self.writes = []
        def reject(*args, **kwargs):
            self.writes.append((args, kwargs))
            return dict(id='C1', contractorId='U1', status='rejected')
        self.job.write_client = SimpleNamespace(request=reject)

    def edited_notice(self, *, withdrawal=False, fresh_row=False):
        self.setup_flow()
        self.current['createdAt'] = (self.clock - timedelta(hours=48)).isoformat()
        self.job.fetchers = {'tiktok': lambda handle: Profile('tiktok', handle, False, error='offline')}
        if withdrawal:
            self.drafts()
            self.enable_withdrawal()
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        introduction = self.clock - timedelta(hours=30 if withdrawal else 1)
        # The old row predates C1. Only the current revision introduces the
        # signing notice, AFTER C1's genuine first invite.
        self.rows.append(dict(id='notice1', senderUserId='U1',
            content='📨 Requested handle @ada.walks (tiktok) for this contract.',
            createdAt=(introduction if fresh_row else self.clock - timedelta(hours=60)).isoformat(),
            isEdited=not fresh_row, updatedAt=introduction.isoformat()))
        return self.job.run()

    def test_BR01_edited_in_post_invite_signing_notice_blocks_reminder(self):
        report = self.edited_notice()
        self.assertEqual(self.sender.delivered, [],
            f'Current notice introduced AFTER invite, but automatic reminder sent: {report}')

    def test_BR01_edited_in_signing_notice_blocks_all_draft_withdrawal(self):
        report = self.edited_notice(withdrawal=True)
        self.assertEqual(self.sender.delivered, [])
        self.assertEqual(self.writes, [],
            f'Notice appeared 10h after C1 invite; creation time erased signing: {report}')

    def test_control_new_row_signing_notice_blocks_reminder(self):
        report = self.edited_notice(fresh_row=True)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('linked handles' in line for line in report), report)

    def test_control_new_row_signing_notice_blocks_withdrawal(self):
        report = self.edited_notice(withdrawal=True, fresh_row=True)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('linked handles' in line for line in report), report)

    def rescued_invite(self, *, withdrawal, malformed=True):
        self.setup_flow()
        if withdrawal:
            self.drafts()
            self.enable_withdrawal()
        self.rows[0].update(createdAt=(self.clock - timedelta(hours=40 if withdrawal else 7)).isoformat(),
                            content='https://app.sideshift.app/campaign-invite/OLD')
        self.source.read('chat1', ['U1'])  # C1 was not present in the original revision.
        # edited_at has a valid type and a valid aware timestamp. The unrelated
        # isDeleted field is malformed, so the complete read must fail.
        self.rows[0].update(content='https://app.sideshift.app/campaign-invite/C1',
                            updatedAt=(self.clock - timedelta(hours=1)).isoformat(), isEdited=True)
        if malformed:
            self.rows[0]['isDeleted'] = 'false'
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        # Native row subsequently disappears. All final reads agree and finish
        # quickly; the loss was fifteen minutes before the action, not a race.
        self.rows[:] = [self.raw('older-delivery', 'Thanks for your interest.',
                                  self.clock - timedelta(hours=5))]
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BR02_partial_read_cannot_restore_old_clock_for_withdrawal(self):
        report = self.rescued_invite(withdrawal=True)
        self.assertEqual(self.writes, [],
            f'Failed read rescued a one-hour-old invite as 40h old and rejected C1: {report}')

    def test_BR02_partial_read_cannot_restore_old_clock_for_reminder(self):
        report = self.rescued_invite(withdrawal=False)
        self.assertEqual(self.sender.delivered, [],
            f'Failed read rescued a one-hour-old invite as 7h old and sent reminder: {report}')

    def test_control_complete_read_retains_missing_invite_edit_time(self):
        report = self.rescued_invite(withdrawal=True, malformed=False)
        self.assertEqual(self.writes, [], report)

    def activity_revision(self, *, clear_metadata=False, older_revision=False):
        self.setup_flow()
        self.drafts()
        self.enable_withdrawal()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        row = dict(id='trying', senderUserId='U1', content='I am still trying to create my accounts.',
                   createdAt=(self.clock - timedelta(hours=30)).isoformat(), isEdited=True,
                   updatedAt=(self.clock - timedelta(hours=1)).isoformat())
        self.rows.append(row)
        observed = self.source.read('chat1', ['U1'])
        message = next(m for m in observed.messages if m.id == 'trying')
        self.j.event('sideshift:U1', 'answered', checks.mark(message), {'by': 'captain'})
        first = self.job.run()
        self.assertEqual(self.writes, [], first)
        self.assertTrue(any('last 24 hours' in line for line in first), first)
        if clear_metadata:
            row.pop('isEdited')
            row.pop('updatedAt')
        elif older_revision:
            row['updatedAt'] = row['createdAt']
        self.clock += timedelta(minutes=15)
        # The recent revision is still durably recorded before this run.
        self.assertTrue(any(e['kind'] == 'msg-seen' and
                            json.loads(e['data']).get('edited_at') == message.edited_at
                            for e in self.j.events('sideshift:U1')))
        return self.job.run()

    def test_BR03_redacted_edit_metadata_cannot_erase_recorded_recent_activity(self):
        report = self.activity_revision(clear_metadata=True)
        self.assertEqual(self.writes, [],
            f'Known one-hour-old creator activity vanished from the independent 24h guard: {report}')

    def test_BR03_older_timestamp_cannot_erase_recorded_recent_activity(self):
        report = self.activity_revision(older_revision=True)
        self.assertEqual(self.writes, [],
            f'Known one-hour-old creator activity lost to an older metadata revision: {report}')

    def test_control_unchanged_edit_metadata_retains_recent_activity_veto(self):
        report = self.activity_revision()
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in line for line in report), report)

    def test_control_unknown_invite_edit_time_holds_reminders(self):
        self.setup_flow()
        self.rows[0].update(isEdited=True, updatedAt='unusable')
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [], report)
        self.assertIsNone(checks.invite_time(self.source.read('chat1'), self.current))

    def test_control_unknown_invite_edit_time_holds_withdrawal(self):
        self.setup_flow()
        self.drafts()
        self.enable_withdrawal()
        self.rows[0].update(createdAt=(self.clock - timedelta(hours=40)).isoformat(),
                            isEdited=True, updatedAt='unusable')
        report = self.job.run()
        self.assertEqual(self.writes, [], report)
        self.assertIsNone(checks.invite_time(self.source.read('chat1'), self.current))

    def test_control_unknown_creator_edit_time_retains_activity_veto(self):
        self.setup_flow()
        self.drafts()
        self.enable_withdrawal()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='trying', senderUserId='U1', content='Still trying.',
                             createdAt=(self.clock - timedelta(hours=30)).isoformat(),
                             isEdited=True, updatedAt='unusable'))
        message = next(m for m in self.source.read('chat1').messages if m.id == 'trying')
        self.j.event('sideshift:U1', 'answered', checks.mark(message), {'by': 'captain'})
        report = self.job.run()
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in line for line in report), report)

    def test_control_signing_lower_bound_keeps_original_invite_creation(self):
        self.setup_flow()
        created = self.clock - timedelta(hours=40)
        self.rows[0].update(createdAt=created.isoformat(), isEdited=True,
                            updatedAt=(self.clock - timedelta(hours=1)).isoformat())
        self.rows.append(dict(id='request', senderUserId='U1',
            content='📨 Requested handle @ada.walks (tiktok) for this contract.',
            createdAt=(self.clock - timedelta(hours=30)).isoformat()))
        conv = self.source.read('chat1')
        self.assertEqual(checks.first_invite_time(conv, self.current), created)
        self.assertTrue(checks.signing_seen(conv, self.current))
