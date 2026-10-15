"""Offline required-behavior regressions for round 48; no network or source edits.

Run: python3 -m unittest discover -s out/tests -t .
Only service responses, clock and model verdict are faked. The reader, Flow,
gate, SQLite, record CLI and ContactsMCP send boundary are real.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import revision_key, unreadable_msg
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Review48(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def replacement(self, drafts=False, malformed=True):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        # The core (sender, time, text) validates, unlike round 47's row whose
        # timestamp could not be rescued. A malformed media count forces the
        # _evidence_msg core-recovery path. Fully identified native file IDs
        # are present, but recovery throws them away.
        row = dict(id='draft', senderUserId='U1', content='My draft',
                   createdAt=(self.clock - timedelta(hours=30 if drafts else 4)).isoformat(),
                   attachments=[{'id': 'first-file'}])
        if malformed:
            row['attachmentCount'] = '1'
        else:
            # A valid row with no attachment IDs and no usable updatedAt.
            row['attachments'] = [{'name': 'first-file.jpg'}]
        self.rows.append(row)
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertEqual(self.writes, [], first)
        self.assertTrue(self.j.flags('sideshift:U1', 'msg-seen'))
        self.rows.pop()
        # The captain reviewed only the FIRST file. Settle its exact retained
        # version through the documented CLI while that row is absent.
        self.assertIn('marked answered', self.run_record('answered', 'draft'))
        self.assertIn('marked attachment-reviewed', self.run_record('looked-at', 'draft'))
        settled = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        self.assertEqual(checks.completeness(settled, self.j.flags('sideshift:U1', 'attachment-reviewed')), [])
        self.assertEqual(checks.unanswered(settled, self.j.flags('sideshift:U1', 'answered')), [])
        self.clock += timedelta(minutes=15)
        self.rows.append({**row, 'attachments': ([{'id': 'replacement-never-reviewed'}] if malformed
                                                else [{'name': 'replacement-never-reviewed.jpg'}])})
        consumed = self.job.run()
        self.assertEqual(self.sender.delivered, [], consumed)
        self.assertEqual(self.writes, [], consumed)
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BJ01_rescued_core_replacement_blocks_automatic_reminder(self):
        report = self.replacement()
        self.assertEqual(self.sender.delivered, [], f'An unseen replacement reused the first file marks: {report}')

    def test_BJ01_rescued_core_replacement_blocks_all_draft_withdrawal(self):
        report = self.replacement(drafts=True)
        self.assertEqual(self.writes, [], f'All-draft flow rejected with an unseen replacement: {report}')

    def test_BJ01_unidentifiable_valid_replacement_blocks_automatic_reminder(self):
        report = self.replacement(malformed=False)
        self.assertEqual(self.sender.delivered, [], f'A valid no-ID replacement lost its veto: {report}')

    def test_BJ01_unidentifiable_valid_replacement_blocks_all_draft_withdrawal(self):
        report = self.replacement(drafts=True, malformed=False)
        self.assertEqual(self.writes, [], f'All-draft flow forgot a valid no-ID replacement: {report}')

    def test_BI01_unreadable_payload_identity_is_stable_and_changes_with_each_payload(self):
        raw = dict(id='draft', senderUserId='U1', createdAt='bad-time',
                   content='My draft', attachments=[{'id': 'first-file'}])
        original, same = unreadable_msg(raw), unreadable_msg(dict(raw))
        self.assertEqual(revision_key(original), revision_key(same))
        self.assertEqual(checks.mark(original), checks.mark(same))
        for change in ({'attachments': [{'id': 'new-file'}]}, {'content': 'New words'},
                       {'createdAt': 'another-bad-time'}, {'extra': 'new payload field'}):
            with self.subTest(change=change):
                changed = unreadable_msg({**raw, **change})
                self.assertNotEqual(revision_key(original), revision_key(changed))
                self.assertNotEqual(checks.mark(original), checks.mark(changed))

    def test_BI02_exact_unreadable_revision_can_be_settled_live_without_covering_replacement(self):
        self.setup_flow()
        row = dict(id='draft', senderUserId='U1', createdAt='bad-time',
                   content='My draft', attachments=[{'id': 'first-file'}])
        self.rows.append(row)
        self.job.run()
        original = unreadable_msg(row)
        for command in ('answered', 'looked-at'):
            self.assertIn('marked', self.run_record(command, revision_key(original)))
        row['attachments'] = [{'id': 'replacement'}]
        self.clock += timedelta(minutes=15)
        self.job.run()
        changed = unreadable_msg(row)
        for command, kind in (('answered', 'answered'), ('looked-at', 'attachment-reviewed')):
            ambiguous = self.run_record(command, 'draft')
            self.assertIn('matches 2 message versions', ambiguous)
            # adapted 2026-10-15 (BZ01): answers use the edit-bound token
            self.assertNotIn((checks.answer_mark(changed) if kind == 'answered' else checks.mark(changed)), self.j.flags('sideshift:U1', kind))
            self.assertIn('marked', self.run_record(command, revision_key(changed)))
            self.assertIn((checks.answer_mark(changed) if kind == 'answered' else checks.mark(changed)), self.j.flags('sideshift:U1', kind))
