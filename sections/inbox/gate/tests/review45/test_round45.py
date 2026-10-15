"""Offline required-behavior tests. New findings intentionally fail this snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real reader, Flow, Gate, SQLite and ContactsMCP boundary; only external responses,
time and the model verdict are faked. No network or paid calls.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review3.support import Case, handles, flow
from gate import checks
from gate.tests.review35 import test_round35 as fixtures


class Review45(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def consume_bad_file_then_remove(self, drafts=False):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        # A malformed, non-list media field must remain UNKNOWN, not become
        # proof that this otherwise readable creator message had no file.
        self.rows.append(dict(id='file', createdAt=(self.clock - timedelta(hours=30 if drafts else 4)).isoformat(),
                              senderUserId='U1', content='', attachments=False))
        writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertEqual(writes, [], first)
        self.assertTrue(any('bad attachments' in line for line in first), first)
        self.assertEqual(self.j.flags('sideshift:U1', 'attachment-reviewed'), set())
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        return writes

    def test_BG01_unreadable_false_media_must_survive_before_automatic_reminder(self):
        self.consume_bad_file_then_remove()
        reviewed = []
        def review(conv, *args):
            reviewed.append([(m.id, m.attachments) for m in conv.messages])
            return 'SEND', 'No attachment needing review was supplied.', []
        self.g.reviewer = review
        later = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Unreadable media became no media: {later}; reviewed={reviewed}')

    def test_BG01_unreadable_false_media_must_survive_before_all_draft_withdrawal(self):
        writes = self.consume_bad_file_then_remove(drafts=True)
        later = self.job.run()
        self.assertEqual(writes, [], f'Unsettled malformed media was forgotten before rejection: {later}')

    def test_BG02_every_requested_account_must_affect_handle_verdict(self):
        self.setup_flow()
        self.current['status'] = 'active'
        requested = [
            dict(id='tt-bad', platform='tiktok', handle='ada_ugc'),
            dict(id='tt-good', platform='tiktok', handle='ada.walks'),
            dict(id='ig-good', platform='instagram', handle='ada.walks'),
        ]
        for row in requested:
            row.update(status='pending', requestedAt=(self.clock - timedelta(hours=1)).isoformat(),
                       programId=flow.CAMPAIGN, creator={'id': 'U1'})
        self.job.read_client = SimpleNamespace(pages=lambda *a, **kw: requested)
        checked = []
        def profile(platform, handle):
            checked.append((platform, handle))
            return handles.Profile(platform, handle, True,
                                   self.clock - timedelta(hours=2) if platform == 'tiktok' else None,
                                   posts=0, followers=0)
        self.job.fetchers = {p: (lambda h, p=p: profile(p, h)) for p in ('tiktok', 'instagram')}
        self.job.run()
        verdicts = [json.loads(e['data']) for e in self.j.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(verdicts), 1)
        self.assertTrue(any('tt-bad=tiktok:ada_ugc' in ref
                            for ref in self.j.flags('sideshift:U1', 'handle-check')))
        self.assertNotEqual(verdicts[0]['verdict'], 'pass',
                            f'Banned requested account silently overwritten: {verdicts}; fetched={checked}')


class Round44Verification(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def test_BF01_readable_question_and_unknown_file_are_retained(self):
        self.setup_flow()
        self.rows.append(dict(id='question', createdAt=(self.clock - timedelta(hours=4)).isoformat(),
                              senderUserId='U1', content='What is the payment?', attachmentCount='1'))
        first = self.job.run()
        self.assertTrue(any('bad attachmentCount' in line for line in first), first)
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        history = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        retained = next(m for m in history.messages if m.id == 'question')
        self.assertEqual(retained.text, 'What is the payment?')
        self.assertGreater(retained.attachments, 0)
        self.assertTrue(retained.attachments_sig.startswith('u-'))
        self.assertTrue(checks.completeness(history))
        self.assertTrue(checks.unanswered(history))
        self.job.run()
        self.assertEqual(self.sender.delivered, [])

    def test_BF02_ascii_validation_precedes_unicode_lowercasing(self):
        self.assertEqual(checks.email_tokens('\N{KELVIN SIGN}ada@example.com'), set())
        self.assertEqual(checks.email_tokens('ada@\N{KELVIN SIGN}mail.com'), set())
        self.assertEqual(checks.email_tokens('<ADA@EXAMPLE.COM>.'), {'ada@example.com'})
