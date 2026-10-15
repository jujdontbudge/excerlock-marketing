"""Offline required-behavior tests; service responses, clock and SEND verdict are fakes."""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.live import LiveReadError
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Round62(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def rescued_reinvite(self, *, malformed=True, withdrawal=False, drafts=False,
                         old_enough=False, withdrawals_enabled=True):
        self.setup_flow()
        if drafts or withdrawal:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        if not withdrawals_enabled:
            self.job.write_client = None
        self.current['createdAt'] = (self.clock - timedelta(hours=100)).isoformat()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=70 if withdrawal else 8)).isoformat()
        # This is a genuine later invite, with independently readable company ID,
        # contract link and creation time. Only its display metadata is broken.
        age = (40 if old_enough else 30) if withdrawal else (7 if old_enough else 4)
        row = self.raw('reinvite', 'https://app.sideshift.app/campaign-invite/C1',
                       self.clock - timedelta(hours=age))
        if malformed:
            row['senderName'] = {'display': 'Johan'}
        self.rows.append(row)
        if malformed:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        retained = [json.loads(e['data']) for e in self.j.events('sideshift:U1')
                    if e['kind'] == 'msg-seen' and json.loads(e['data'])['id'] == row['id']]
        self.assertEqual(len(retained), 1)
        self.assertEqual(retained[0]['text'], row['content'])
        self.rows.pop()
        if malformed:
            self.assertIn('marked answered', self.run_record('answered', row['id']))
            self.assertIn('marked attachment-reviewed', self.run_record('looked-at', row['id']))
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BX01_rescued_reinvite_must_reset_reminder_clock(self):
        report = self.rescued_reinvite()
        self.assertEqual(self.sender.delivered, [],
                         f'Reminder sent only 4h15m after observed re-invite: {report}')

    def test_BX01_rescued_reinvite_must_reset_draft_only_withdrawal_clock(self):
        report = self.rescued_reinvite(withdrawal=True)
        self.assertEqual(self.writes, [],
                         f'Contract rejected only 30h15m after observed re-invite: {report}')

    def test_control_readable_vanished_reinvite_resets_reminder_clock(self):
        report = self.rescued_reinvite(malformed=False)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_readable_vanished_reinvite_resets_withdrawal_clock(self):
        report = self.rescued_reinvite(malformed=False, withdrawal=True)
        self.assertEqual(self.writes, [], report)

    def test_control_drafts_contain_early_reminder(self):
        report = self.rescued_reinvite(drafts=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_settled_old_reinvite_allows_reminder(self):
        report = self.rescued_reinvite(old_enough=True)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_settled_old_reinvite_allows_withdrawal(self):
        report = self.rescued_reinvite(withdrawal=True, old_enough=True)
        self.assertEqual(len(self.writes), 1, report)

    def test_control_disabling_withdrawals_contains_draft_only_effect(self):
        report = self.rescued_reinvite(withdrawal=True, withdrawals_enabled=False)
        self.assertEqual(self.writes, [], report)
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (BX01 fix): the 30h-old re-invite now counts, so withdrawal is not even due yet
        self.assertTrue(any('no SideShift key' in line or 'draft' in line for line in report), report)
