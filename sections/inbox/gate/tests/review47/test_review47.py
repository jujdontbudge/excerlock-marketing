"""Offline required-behavior regressions. BI01/BI02 intentionally fail this snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Flow, Gate, SQLite, record CLI and ContactsMCP boundary.
Only service responses, time and the model verdict are faked. No network.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Review47(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def add_unreadable_file(self):
        self.rows.append(dict(id='draft', senderUserId='U1', content='My draft',
                              createdAt='bad-time', attachments=[{'id': 'first-file'}]))

    def replaced_unreadable_file(self, drafts=False):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        self.add_unreadable_file()
        first = self.job.run()
        self.assertTrue(any('no live read' in line for line in first), first)
        self.assertEqual(self.sender.delivered, [])
        self.assertEqual(self.writes, [])
        old_row = self.rows.pop()
        # The captain reviewed the FIRST file in SideShift. After the malformed
        # row vanishes, the documented CLI can settle its retained revision.
        self.assertIn('marked answered', self.run_record('answered', 'draft'))
        self.assertIn('marked attachment-reviewed', self.run_record('looked-at', 'draft'))
        settled = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        self.assertEqual(checks.completeness(settled, self.j.flags('sideshift:U1', 'attachment-reviewed')), [])
        self.assertEqual(checks.unanswered(settled, self.j.flags('sideshift:U1', 'answered')), [])
        # A replacement of the same native message is consumed in a later run.
        # Its file id differs, but the malformed time still prevents a full read.
        self.clock += timedelta(minutes=15)
        self.rows.append({**old_row, 'attachments': [{'id': 'replacement-never-reviewed'}]})
        second = self.job.run()
        self.assertTrue(any('no live read' in line for line in second), second)
        self.assertEqual(self.sender.delivered, [])
        self.assertEqual(self.writes, [])
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BI01_replacement_unreadable_file_needs_new_look_before_reminder(self):
        report = self.replaced_unreadable_file()
        self.assertEqual(self.sender.delivered, [],
                         f'A look at first-file covered replacement-never-reviewed: {report}')

    def test_BI01_replacement_unreadable_file_blocks_all_draft_withdrawal(self):
        report = self.replaced_unreadable_file(drafts=True)
        self.assertEqual(self.writes, [],
                         f'All-draft Flow withdrew with a consumed, unreviewed replacement: {report}')

    def test_BI02_captain_can_answer_retained_unreadable_row_while_it_is_still_live(self):
        self.setup_flow()
        self.add_unreadable_file()
        self.job.run()
        self.assertTrue(any(json.loads(e['data']).get('kind') == 'unreadable'
                            for e in self.j.events('sideshift:U1') if e['kind'] == 'msg-seen'))
        output, error = self.no_crash(lambda: self.run_record('answered', 'draft'))
        self.assertIsNone(error, f'Documented settlement cannot reach the journaled fallback: {error}')
        self.assertIn('marked answered', output)
        self.assertTrue(self.j.flags('sideshift:U1', 'answered'))

    def test_BI02_captain_can_review_retained_unreadable_row_while_it_is_still_live(self):
        self.setup_flow()
        self.add_unreadable_file()
        self.job.run()
        output, error = self.no_crash(lambda: self.run_record('looked-at', 'draft'))
        self.assertIsNone(error, f'Documented settlement cannot reach the journaled fallback: {error}')
        self.assertIn('marked attachment-reviewed', output)
        self.assertTrue(self.j.flags('sideshift:U1', 'attachment-reviewed'))
