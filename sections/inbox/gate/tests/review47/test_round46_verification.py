"""Additional passing verification of the round-46 fixes, using real gate readers."""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case, flow
from gate.tests.review35 import test_round35 as fixtures


class Round46Verification(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def test_BH01_alternate_timestamp_and_updatedAt_recover_readable_question(self):
        self.setup_flow()
        for alternate in ('timestamp', 'updatedAt'):
            with self.subTest(alternate=alternate):
                raw = dict(id='question', senderUserId='U1', content='What is the payment?',
                           createdAt='bad-primary', **{alternate: self.clock.isoformat()})
                recovered = self.source._evidence_msg(raw, ('U1',))
                self.assertEqual(recovered.direction, 'in')
                self.assertEqual(recovered.text, raw['content'])
                if alternate == 'updatedAt':   # adapted 2026-10-15 (review BW01): an edit time never dates creation;
                    self.assertEqual(recovered.kind, 'unreadable')   # kept as an unread message with unknown activity
                    self.assertEqual(recovered.edited_at, 'unknown')
                else:
                    self.assertEqual(recovered.at, self.clock.isoformat())

    def test_BH01_nonrecord_consumed_before_failure_blocks_later_all_draft_withdrawal(self):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        original_pages = self.source.client.pages

        def pages(path, **kwargs):
            if path == '/support-channels/chat1/messages':
                return list(self.rows)  # preserve a non-record row instead of copying it as a dict
            return original_pages(path, **kwargs)

        self.source.client.pages = pages
        self.rows.append(None)
        writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        first = self.job.run()
        self.assertTrue(any('no live read' in line for line in first), first)
        self.assertTrue(any(json.loads(e['data']).get('kind') == 'unreadable'
                            for e in self.j.events('sideshift:U1') if e['kind'] == 'msg-seen'))
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        later = self.job.run()
        self.assertEqual(writes, [], later)
        retained = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        self.assertTrue(checks.unanswered(retained))
        self.assertTrue(checks.completeness(retained))

    def test_BH02_incomplete_batch_explicitly_asks_without_fetching_profiles(self):
        self.setup_flow()
        self.current['status'] = 'active'
        apps = [dict(id='missing-platform', handle='ada_ugc'),
                dict(id='tt', platform='tiktok', handle='ada.walks'),
                dict(id='ig', platform='instagram', handle='ada.walks')]
        for row in apps:
            row.update(status='pending', programId=flow.CAMPAIGN, creator={'id': 'U1'},
                       requestedAt=(self.clock - timedelta(hours=1)).isoformat())
        self.job.read_client = SimpleNamespace(pages=lambda *a, **kw: apps)

        def forbidden_fetch(handle):
            self.fail('An incomplete batch must ask before selecting accounts to fetch')

        self.job.fetchers = dict(tiktok=forbidden_fetch, instagram=forbidden_fetch)
        self.job.run()
        verdicts = [json.loads(e['data']) for e in self.j.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(verdicts), 1)
        self.assertEqual(verdicts[0]['verdict'], 'ask')
