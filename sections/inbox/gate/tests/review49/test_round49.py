"""Offline required-behavior regressions; failures demonstrate round-49 defects.

Run: python3 -m unittest discover -s out/tests -t .
Real reader, journal, record CLI, Flow, Gate and ContactsMCP send boundary.
Only remote responses, time and the model verdict are faked.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case, flow, handles
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Review49(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def unknown_file_replacement(self, *, drafts=False, rescued=False):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        # Odd entries expressly remain random u- signatures in this round's
        # design. Different payloads are observed, not an invisible CDN change.
        row = dict(id='draft', senderUserId='U1', content='My draft',
                   createdAt=(self.clock - timedelta(hours=30 if drafts else 4)).isoformat(),
                   attachmentCount='1' if rescued else 1,
                   attachments=['https://cdn.invalid/first-file.jpg'])
        self.rows.append(row)
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertEqual(self.writes, [], first)
        original = next(json.loads(e['data']) for e in self.j.events('sideshift:U1')
                        if e['kind'] == 'msg-seen' and json.loads(e['data'])['id'] == 'draft')
        self.assertTrue(original['attachments_sig'].startswith('u-'))
        self.rows.pop()
        # The real CLI permits settlement of the retained u- version while it
        # is absent. This should never authorize an unidentified replacement.
        # A correct implementation may refuse these marks altogether: u-
        # files are explicitly never settleable. Do not require the bug.
        self.run_record('answered', 'draft')
        self.run_record('looked-at', 'draft')
        self.clock += timedelta(minutes=15)
        replacement = {**row, 'attachments': ['https://cdn.invalid/unreviewed-replacement.jpg']}
        self.rows.append(replacement)
        changed = self.source._evidence_msg(replacement, ('U1',))
        self.assertNotIn(checks.mark(changed), self.j.flags('sideshift:U1', 'attachment-reviewed'))
        consumed = self.job.run()
        self.assertEqual(self.sender.delivered, [], consumed)
        self.assertEqual(self.writes, [], consumed)
        # The changed payload was consumed and vetoed, but the journal retained
        # only the first random signature. No captain marks the replacement.
        versions = [e for e in self.j.events('sideshift:U1')
                    if e['kind'] == 'msg-seen' and json.loads(e['data'])['id'] == 'draft']
        self.retained_versions = len(versions)
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BK01_odd_attachment_replacement_blocks_reminder(self):
        report = self.unknown_file_replacement()
        self.assertEqual(self.sender.delivered, [],
                         f'Unreviewed replacement forgotten ({self.retained_versions} retained revision): {report}')

    def test_BK01_odd_attachment_replacement_blocks_all_draft_withdrawal(self):
        report = self.unknown_file_replacement(drafts=True)
        self.assertEqual(self.writes, [],
                         f'All-draft Flow rejected after forgetting unreviewed replacement: {report}')

    def test_BK01_rescued_odd_attachment_replacement_blocks_reminder(self):
        report = self.unknown_file_replacement(rescued=True)
        self.assertEqual(self.sender.delivered, [], f'Recovered replacement forgotten: {report}')

    def test_BK01_rescued_odd_attachment_replacement_blocks_all_draft_withdrawal(self):
        report = self.unknown_file_replacement(drafts=True, rescued=True)
        self.assertEqual(self.writes, [], f'All-draft Flow rejected after recovered replacement: {report}')

    def test_BK02_unrecognized_platform_cannot_disappear_from_handle_verdict(self):
        self.setup_flow()
        self.current['status'] = 'active'
        apps = [dict(id='tt', platform='tiktok', handle='ada.walks'),
                dict(id='ig', platform='instagram', handle='ada.walks'),
                dict(id='other', platform='youtube', handle='ada_ugc')]
        for a in apps:
            a.update(status='pending', requestedAt=(self.clock - timedelta(hours=1)).isoformat(),
                     programId=flow.CAMPAIGN, creator={'id': 'U1'})
        self.job.read_client = SimpleNamespace(pages=lambda *a, **kw: apps)
        fetched = []

        def fetch(platform, handle):
            fetched.append((platform, handle))
            return handles.Profile(platform, handle, True,
                                   self.clock - timedelta(hours=2) if platform == 'tiktok' else None, 0, 0)

        self.job.fetchers = {p: (lambda h, p=p: fetch(p, h)) for p in ('tiktok', 'instagram')}
        self.job.run()
        verdicts = [json.loads(e['data']) for e in self.j.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(verdicts), 1)
        self.assertIn('ada_ugc', json.dumps(verdicts[0]['handles']))
        self.assertNotEqual(verdicts[0]['verdict'], 'pass',
                            f'Unverifiable requested account silently excluded from verdict: {verdicts[0]}; fetched={fetched}')
