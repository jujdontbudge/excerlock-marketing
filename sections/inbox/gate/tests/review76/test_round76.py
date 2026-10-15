"""Offline required-behavior assertions at real effect boundaries.

Run: python3 -m unittest discover -s out/tests -t .
Only remote responses, time and the model verdict are faked. No network or
production-source changes. Assertions named CL01 fail on the supplied snapshot.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import revision_key
from gate.tests.review3.support import Case, NOW
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class MediaActivity(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def modes(self, option):
        scheduled = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in scheduled) else t
                        for k, t in self.g.types.items()}

    def settle(self, message):
        # Real captain commands settle these exact words/files. Neither command
        # authorizes withdrawal or waives its independent 24-hour activity rule.
        # Use the revision the real captain UI presents, including any
        # conservative clock normalization supplied by with_history.
        current = self.source.read('chat1', ['U1'])
        shown = checks.with_history(current, self.j.events('sideshift:U1'))
        matches = [m for m in shown.messages if m.id == message.id
                   and m.text == message.text and m.attachments_sig == message.attachments_sig]
        self.assertEqual(len(matches), 1)
        key = revision_key(matches[0])
        self.assertIn('marked answered', self.run_record('answered', key))
        self.assertIn('marked attachment-reviewed', self.run_record('looked-at', key))

    def exercise(self, *, withdrawal=True, option='a', vanished=False,
                 metadata='stale', change=True, old=False, refresh_url=False):
        self.setup_flow()
        self.modes(option)
        if withdrawal:
            self.rows[0]['createdAt'] = (NOW - timedelta(hours=40)).isoformat()
        row = dict(id='setup-photo', senderUserId='U1' if withdrawal else fixtures.flow.COMPANY,
                   createdAt=(NOW - timedelta(hours=50)).isoformat(),
                   content='My account setup.' if withdrawal else 'Account setup example.',
                   attachments=[dict(id='file-A', url='https://cdn.invalid/A.jpg')])
        if metadata == 'stale':
            row.update(isEdited=True, updatedAt=(NOW - timedelta(hours=49)).isoformat())
        elif metadata == 'false':
            row.update(isEdited=False, updatedAt=(NOW - timedelta(hours=49)).isoformat())
        self.rows.append(row)
        self.clock = NOW - timedelta(hours=31) if old else NOW - timedelta(minutes=30)
        first = next(m for m in self.source.read('chat1', ['U1']).messages if m.id == row['id'])
        if withdrawal:
            self.settle(first)
        self.clock += timedelta(minutes=15)
        if change:
            row['attachments'] = [dict(id='file-A' if refresh_url else 'file-B',
                                       url='https://cdn.invalid/B.jpg')]
        if metadata == 'correct':
            row.update(isEdited=True, updatedAt=self.clock.isoformat())
        second = next(m for m in self.source.read('chat1', ['U1']).messages if m.id == row['id'])
        self.assertEqual(first.text, second.text)
        self.assertEqual(first.attachments, second.attachments)
        if change and not refresh_url:
            self.assertNotEqual(first.attachments_sig, second.attachments_sig)
        else:
            self.assertEqual(first.attachments_sig, second.attachments_sig)
        if withdrawal:
            # The change invalidated the first answer. Explicitly settle both
            # revisions by their keys, including the historical file.
            self.settle(first)
            self.settle(second)
        if vanished:
            self.rows.remove(row)
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or dict(id='C1', contractorId='U1', status='rejected'))
        self.clock = NOW
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CL01_auto_must_not_withdraw_after_observed_file_replacement(self):
        report = self.exercise()
        self.assertEqual(self.writes, [], report)

    def test_CL01_drafts_must_not_withdraw_after_observed_file_replacement(self):
        report = self.exercise(option='b')
        self.assertEqual(self.writes, [], report)

    def test_CL01_mixed_must_not_withdraw_after_observed_file_replacement(self):
        report = self.exercise(option='c')
        self.assertEqual(self.writes, [], report)

    def test_CL01_removed_file_replacement_must_retain_recent_activity(self):
        report = self.exercise(option='b', vanished=True)
        self.assertEqual(self.writes, [], report)

    def test_CL01_false_edit_flag_cannot_erase_observed_file_activity(self):
        report = self.exercise(metadata='false')
        self.assertEqual(self.writes, [], report)

    def test_CL01_absent_edit_metadata_cannot_erase_observed_file_activity(self):
        report = self.exercise(metadata='absent')
        self.assertEqual(self.writes, [], report)

    def test_CL01_auto_must_respect_gap_after_captain_file_replacement(self):
        report = self.exercise(withdrawal=False)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CL01_mixed_must_respect_gap_after_captain_file_replacement(self):
        report = self.exercise(withdrawal=False, option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_CL01_removed_captain_file_replacement_must_retain_gap(self):
        report = self.exercise(withdrawal=False, vanished=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_current_file_edit_time_stops_withdrawal(self):
        report = self.exercise(metadata='correct')
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in line for line in report), report)

    def test_control_current_captain_file_edit_time_stops_reminder(self):
        report = self.exercise(withdrawal=False, metadata='correct')
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 180' in line for line in report), report)

    def test_control_unchanged_old_file_can_be_withdrawn(self):
        report = self.exercise(change=False)
        self.assertEqual(len(self.writes), 1, report)

    def test_control_same_id_transport_url_refresh_can_be_withdrawn(self):
        report = self.exercise(refresh_url=True)
        self.assertEqual(len(self.writes), 1, report)

    def test_control_actual_old_file_replacement_can_be_withdrawn(self):
        report = self.exercise(old=True, metadata='correct')
        self.assertEqual(len(self.writes), 1, report)

    def test_control_draft_mode_contains_media_gap_send(self):
        report = self.exercise(withdrawal=False, option='b')
        self.assertEqual(self.sender.delivered, [], report)
