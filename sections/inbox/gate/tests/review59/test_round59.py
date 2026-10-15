"""Offline required-behavior counterexamples; assertions fail on this snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real Flow, Gate, SideShiftLive, record CLI, SQLite and ContactsMCP send boundary.
Only remote responses, time and the SEND review verdict are fakes.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import LiveReadError
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Round59(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def drafts_and_writer(self):
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))

    def settle(self, mid, malformed):
        self.assertIn('marked answered', self.run_record('answered', mid))
        if malformed:
            self.assertIn('marked attachment-reviewed', self.run_record('looked-at', mid))

    def unreadable_edit(self, *, malformed=True, edit='recent'):
        self.setup_flow()
        self.drafts_and_writer()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        row = dict(id='trying', senderUserId='U1',
                   createdAt=(self.clock - timedelta(hours=30)).isoformat(),
                   content={'text': 'I am still trying.'} if malformed else 'I am still trying.')
        if edit != 'none':
            row.update(isEdited=True, updatedAt=(
                'garbled' if edit == 'unknown' else
                (self.clock - timedelta(hours=1 if edit == 'recent' else 26)).isoformat()))
        self.rows.append(row)
        if malformed:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        self.rows.pop()
        self.settle('trying', malformed)
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BU01_settling_unreadable_content_cannot_erase_recent_edit_activity(self):
        report = self.unreadable_edit()
        self.assertEqual(self.writes, [],
            f'Old creation replaced known 75-minute edit activity and allowed rejection: {report}')

    def test_BU01_settling_unreadable_content_cannot_erase_unknown_edit_activity(self):
        report = self.unreadable_edit(edit='unknown')
        self.assertEqual(self.writes, [],
            f'An explicitly edited row with unknown edit time was treated as unedited: {report}')

    def test_control_readable_recent_edit_blocks_withdrawal_after_settlement(self):
        report = self.unreadable_edit(malformed=False)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in s for s in report), report)

    def test_control_old_unreadable_edit_can_be_settled(self):
        report = self.unreadable_edit(edit='old')
        self.assertEqual(len(self.writes), 1, report)

    def test_control_unedited_old_unreadable_content_can_be_settled(self):
        report = self.unreadable_edit(edit='none')
        self.assertEqual(len(self.writes), 1, report)

    def unreadable_outbound(self, *, malformed=True, recent=True, drafts=False):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        row = self.raw('captain-update',
                       {'text': 'I will check the accounts this afternoon.'} if malformed else
                       'I will check the accounts this afternoon.',
                       self.clock - (timedelta(minutes=1) if recent else timedelta(hours=4)))
        self.rows.append(row)
        if malformed:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        self.rows.pop()
        if malformed:
            self.settle('captain-update', malformed=True)
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BU02_unreadable_captain_delivery_still_counts_for_minimum_gap(self):
        report = self.unreadable_outbound()
        self.assertEqual(self.sender.delivered, [],
            f'Proven company sender was replaced by creator direction, bypassing the 180-minute gap: {report}')

    def test_control_readable_captain_delivery_blocks_minimum_gap(self):
        report = self.unreadable_outbound(malformed=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 180' in s for s in report), report)

    def test_control_old_settled_unreadable_captain_delivery_allows_reminder(self):
        report = self.unreadable_outbound(recent=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_draft_mode_contains_unreadable_captain_gap_bypass(self):
        report = self.unreadable_outbound(drafts=True)
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (BU02 fix): the gap now holds it before the draft stage; either contains it
        self.assertTrue(any('draft' in s or 'min gap' in s for s in report), report)

    def vanished_edited_invite(self, *, disappear=True, first_contract='C1'):
        self.setup_flow()
        self.rows[0]['content'] = f'https://app.sideshift.app/campaign-invite/{first_contract}'
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(minutes=15)
        self.rows[0].update(content='https://app.sideshift.app/campaign-invite/OLD',
                            isEdited=True, updatedAt=self.clock.isoformat())
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(minutes=15)
        self.rows[0].update(content='https://app.sideshift.app/campaign-invite/C1',
                            updatedAt=self.clock.isoformat())
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(hours=6)
        if disappear:
            self.rows[:] = [self.raw('unrelated', 'Thanks for your interest.',
                                    self.clock - timedelta(hours=5))]
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BU03_missing_edited_invite_has_unambiguous_latest_revision(self):
        report = self.vanished_edited_invite()
        history = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        links = checks.invite_links(history, self.current)
        self.assertEqual({m.id for m in links}, {'invite1'})
        self.assertEqual(len({checks.content_time(m) for m in links}), 2)
        self.assertEqual(len(self.sender.delivered), 1,
            f'Two revisions of one invite at different content times became an artificial tie: {report}')

    def test_control_live_edited_invite_has_unambiguous_latest_revision(self):
        report = self.vanished_edited_invite(disappear=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_missing_single_edited_invite_can_be_reconstructed(self):
        report = self.vanished_edited_invite(first_contract='OTHER')
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_genuine_equal_time_invites_with_one_missing_hold(self):
        self.setup_flow(invite_ids=('first', 'second'))
        self.source.read('chat1', ['U1'])
        self.rows.pop(0)
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('two invites share a time' in s for s in report), report)
