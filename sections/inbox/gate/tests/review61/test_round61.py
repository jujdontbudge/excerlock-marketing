"""Offline counterexamples; assertions state required behavior at real effect boundaries."""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.live import LiveReadError
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Round61(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def settle(self, mid):
        self.assertIn('marked answered', self.run_record('answered', mid))
        self.assertIn('marked attachment-reviewed', self.run_record('looked-at', mid))

    def drafts_and_writer(self):
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or dict(id='C1', contractorId='U1', status='rejected'))

    def missing_creation(self, *, known_creation=False, content='I am still trying.'):
        self.setup_flow()
        self.drafts_and_writer()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        row = dict(id='trying', senderUserId='U1', content=content,
                   isEdited=True, updatedAt=(self.clock - timedelta(hours=30)).isoformat())
        if known_creation:
            row['createdAt'] = (self.clock - timedelta(hours=31)).isoformat()
        self.rows.append(row)
        if known_creation:
            self.source.read('chat1', ['U1'])
        else:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        self.retained = [json.loads(e['data']) for e in self.j.events('sideshift:U1')
                         if e['kind'] == 'msg-seen' and json.loads(e['data'])['id'] == row['id']]
        self.rows.pop()
        self.settle(row['id'])
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BW01_updatedAt_cannot_stand_in_for_unknown_creation(self):
        report = self.missing_creation()
        self.assertEqual(self.writes, [], f'Unknown creation rescued as old creation: {report}; {self.retained}')

    def test_control_known_old_creation_and_edit_permit_withdrawal(self):
        report = self.missing_creation(known_creation=True)
        self.assertEqual(len(self.writes), 1, report)

    def signing_notice(self, *, company=False, malformed=True, drafts=False, withdraw=False):
        self.setup_flow()
        if drafts or withdraw:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        if withdraw:
            self.drafts_and_writer()
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        text = ('✅ Your handle @ada (tiktok) was approved for ExcerLock' if company else
                '📨 Requested handle @ada (tiktok) for this contract.')
        row = dict(id='signing', senderUserId=(fixtures.flow.COMPANY if company else 'U1'),
                   createdAt=(self.clock - timedelta(hours=30 if withdraw else 4)).isoformat(), content=text)
        if malformed:
            row['senderName'] = {'display': 'Ada' if not company else 'Johan'}
        self.rows.append(row)
        if malformed:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        self.rows.pop()
        # A content/attachment settlement is not a decision to undo signing.
        self.settle(row['id'])
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BW02_rescued_handle_request_must_still_stop_reminders(self):
        report = self.signing_notice()
        self.assertEqual(self.sender.delivered, [], f'Observed handle request lost its signing veto: {report}')

    def test_BW02_rescued_company_approval_must_still_stop_reminders(self):
        report = self.signing_notice(company=True)
        self.assertEqual(self.sender.delivered, [], f'Observed company approval lost its signing veto: {report}')

    def test_BW02_rescued_handle_request_must_stop_draft_only_withdrawal(self):
        report = self.signing_notice(withdraw=True)
        self.assertEqual(self.writes, [], f'Observed handle request was followed by rejection: {report}')

    def test_control_readable_vanished_handle_request_stops_reminder(self):
        report = self.signing_notice(malformed=False)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_readable_vanished_approval_stops_reminder(self):
        report = self.signing_notice(company=True, malformed=False)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_drafts_contain_rescued_notice_reminder(self):
        report = self.signing_notice(drafts=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_readable_vanished_request_stops_draft_only_withdrawal(self):
        report = self.signing_notice(malformed=False, withdraw=True)
        self.assertEqual(self.writes, [], report)
