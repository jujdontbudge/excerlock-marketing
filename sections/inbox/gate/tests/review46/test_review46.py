"""Offline counterexamples; required-behavior assertions fail on this snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Flow, Gate, SQLite and ContactsMCP boundary. Only external
responses, clock and model verdict are faked. No production changes or network.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review3.support import Case, flow, handles
from gate.tests.review35 import test_round35 as fixtures


class Review46(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def consume_bad_time_question(self, drafts=False):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='payment-question', senderUserId='U1',
                              content='What is the payment?', createdAt='not-a-timestamp',
                              timestamp=(self.clock - timedelta(hours=30 if drafts else 4)).isoformat()))
        writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        self.reviewed = []

        def review(conv, *args):
            self.reviewed.append([(m.id, m.text) for m in conv.messages])
            questions = [m.text for m in conv.messages if m.direction == 'in' and '?' in m.text]
            return ('HOLD', 'An unanswered question remains.', questions) if questions else (
                'SEND', 'No creator question was supplied.', [])

        self.g.reviewer = review
        first = self.job.run()
        self.assertTrue(any('no live read' in line and 'Invalid isoformat' in line for line in first), first)
        self.assertEqual(self.sender.delivered, [], first)
        self.assertEqual(writes, [], first)
        self.assertEqual(self.j.flags('sideshift:U1', 'answered'), set())
        self.rows.pop()  # upstream removes the already-consumed row
        self.clock += timedelta(minutes=15)  # well outside the accepted 10-second gap
        return writes

    def test_BH01_readable_question_with_bad_primary_time_must_block_later_reminder(self):
        self.consume_bad_time_question()
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Consumed question was discarded: {report}; review saw {self.reviewed}')

    def test_BH01_readable_question_with_bad_primary_time_must_block_all_draft_withdrawal(self):
        writes = self.consume_bad_time_question(drafts=True)
        report = self.job.run()
        self.assertEqual(writes, [], f'All-draft Flow rejected despite the consumed question: {report}')

    def incomplete_handle_batch(self, incomplete):
        self.setup_flow()
        self.current['status'] = 'active'
        requests = [dict(id='incomplete', **incomplete),
                    dict(id='good-tt', platform='tiktok', handle='ada.walks'),
                    dict(id='good-ig', platform='instagram', handle='ada.walks')]
        for r in requests:
            r.update(status='pending', requestedAt=(self.clock - timedelta(hours=1)).isoformat(),
                     programId=flow.CAMPAIGN, creator={'id': 'U1'})
        self.job.read_client = SimpleNamespace(pages=lambda *a, **kw: requests)
        self.fetched = []

        def fetch(platform, handle):
            self.fetched.append((platform, handle))
            return handles.Profile(platform, handle, True,
                                   self.clock - timedelta(hours=2) if platform == 'tiktok' else None, 0, 0)

        self.job.fetchers = {p: (lambda h, p=p: fetch(p, h)) for p in ('tiktok', 'instagram')}
        self.job.run()
        events = [e for e in self.j.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(events), 1)
        self.assertIn('incomplete=', events[0]['ref'])
        return json.loads(events[0]['data'])

    def test_BH02_missing_platform_cannot_hide_banned_requested_account(self):
        result = self.incomplete_handle_batch({'handle': 'ada_ugc'})
        self.assertNotEqual(result['verdict'], 'pass',
                            f'Banned handle silently excluded from checked batch: {result}; fetched={self.fetched}')

    def test_BH02_missing_handle_cannot_be_a_successfully_checked_request(self):
        result = self.incomplete_handle_batch({'platform': 'tiktok'})
        self.assertNotEqual(result['verdict'], 'pass',
                            f'Unidentifiable pending TikTok silently excluded: {result}; fetched={self.fetched}')


class Round45AdditionalVerification(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def test_BG01_recovery_requires_exact_empty_media_types(self):
        self.setup_flow()
        base = dict(id='file', senderUserId='U1', content='',
                    createdAt=(self.clock - timedelta(hours=4)).isoformat())
        for fields in ({'attachments': False}, {'attachmentCount': False}, {'attachmentCount': 0.0},
                       {'attachments': {}}, {'attachments': ''}, {'attachmentCount': '0'}):
            with self.subTest(fields=fields):
                recovered = self.source._evidence_msg({**base, **fields}, ('U1',))
                self.assertGreater(recovered.attachments, 0)
                self.assertTrue(recovered.attachments_sig.startswith('u-'))
        for fields in ({}, {'attachments': None, 'attachmentCount': None},
                       {'attachments': [], 'attachmentCount': 0}):
            with self.subTest(empty=fields):
                self.assertEqual(self.source._evidence_msg({**base, **fields}, ('U1',)).attachments, 0)

    def test_BG02_duplicate_platforms_in_one_chat_notice_ask_without_fetching(self):
        self.setup_flow()
        self.rows.append(dict(id='handles', senderUserId='U1',
                              createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              content='📨 Requested 3 handles: @ada_ugc (tiktok), @ada.walks (tiktok), '
                                      '@ada.walks (instagram) for this contract.'))

        def no_fetch(handle):
            self.fail('Ambiguous accounts must go to the captain before a profile is selected')

        self.job.fetchers = {p: no_fetch for p in ('tiktok', 'instagram')}
        self.job.run()
        verdicts = [json.loads(e['data']) for e in self.j.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(verdicts), 1)
        self.assertEqual(verdicts[0]['verdict'], 'ask')
        self.assertEqual(len(verdicts[0]['handles']), 3)
