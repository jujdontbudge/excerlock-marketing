"""Handle newness checks (captain, 2026-10-14: new = created in the last 3 days, both TikTok and Instagram)."""
import unittest
from datetime import datetime, timedelta, timezone

from gate.handles import Profile, judge, requested

NOW = datetime(2026, 10, 15, 3, 0, tzinfo=timezone.utc)
tt = lambda days=1, posts=0, exists=True: Profile('tiktok', 'k', exists, NOW - timedelta(days=days) if exists else None, posts, 0, None if exists else 'status 10221')
ig = lambda posts=0, followers=0, exists=True: Profile('instagram', 'k', exists, None, posts, followers, None if exists else 'not found')


class Judge(unittest.TestCase):
    def test_fresh_pair_passes(self):
        self.assertEqual(judge({'tiktok': tt(), 'instagram': ig()}, NOW)[0], 'pass')

    def test_kamila_case_old_tiktok_fails(self):
        # 2026-10-15: @kamila_walks TikTok was created 2025-04-06 (0 videos); never auto-approve.
        self.assertEqual(judge({'tiktok': tt(days=557), 'instagram': ig()}, NOW)[0], 'fail')

    def test_p_case_instagram_only_with_posts(self):
        # 2026-10-14: P linked only an older Instagram with 4 posts.
        verdict, reasons = judge({'instagram': ig(posts=4)}, NOW)
        self.assertEqual(verdict, 'fail')
        self.assertTrue(any('both' in r for r in reasons))

    def test_missing_platform_or_unreadable_profile_asks(self):
        self.assertEqual(judge({'tiktok': tt()}, NOW)[0], 'ask')
        self.assertEqual(judge({'tiktok': tt(exists=False), 'instagram': ig()}, NOW)[0], 'ask')
        self.assertEqual(judge({'tiktok': tt(), 'instagram': ig(exists=False)}, NOW)[0], 'ask')

    def test_boundaries(self):
        self.assertEqual(judge({'tiktok': tt(days=3), 'instagram': ig()}, NOW)[0], 'pass')
        self.assertEqual(judge({'tiktok': tt(days=3.01), 'instagram': ig()}, NOW)[0], 'fail')
        self.assertEqual(judge({'tiktok': tt(), 'instagram': ig(followers=49)}, NOW)[0], 'pass')
        self.assertEqual(judge({'tiktok': tt(), 'instagram': ig(followers=50)}, NOW)[0], 'fail')
        self.assertEqual(judge({'tiktok': tt(), 'instagram': ig(posts=1)}, NOW)[0], 'fail')
        self.assertEqual(judge({'tiktok': tt(posts=2), 'instagram': ig()}, NOW)[0], 'ask')

    def test_ugc_or_brand_in_username_fails(self):
        # 2026-10-15: Jenna linked @jenaugc5; the captain: no "ugc" in usernames.
        for handle in ('jenaugc5', 'UGC.emma', 'emma_excerlock'):
            p = {'tiktok': Profile('tiktok', handle, True, NOW - timedelta(days=1), 0, 0), 'instagram': ig()}
            self.assertEqual(judge(p, NOW)[0], 'fail', handle)

    def test_parse_handle_request(self):
        self.assertEqual(requested('📨 Requested 2 handles: @kamila_walks (tiktok), @kamila_walks (instagram) for this contract.'),
                         {'tiktok': 'kamila_walks', 'instagram': 'kamila_walks'})
        self.assertEqual(requested('📨 Requested handle @p.hudson.fitness (instagram) for this contract.'), {'instagram': 'p.hudson.fitness'})


if __name__ == '__main__':
    unittest.main()
