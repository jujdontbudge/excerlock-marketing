"""Live checks against real TikTok, Instagram, Resend and the Claude judge. Run: LIVE=1 tests/test_live.py

Every part of the system that touches the internet is exercised here on real accounts.
Accounts: CREATORS_LIVE_TT (default lilyterpfr), CREATORS_LIVE_IG (default daddywellness).
"""
import json
import os
import re
import sys
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

os.environ["CREATORS_DATA"] = tempfile.mkdtemp()
# local test servers must not go through a system proxy
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env", override=False)

from creatorops import deals, deliverables, intake, performance, snapshot, vetting  # noqa: E402
from creatorops.channels import ResendEmail  # noqa: E402
from creatorops.db import connect  # noqa: E402
from creatorops.pipeline import advance  # noqa: E402
from creatorops.platforms import PlatformError  # noqa: E402
from creatorops.platforms.instagram import Instagram, session_file  # noqa: E402
from creatorops.platforms.tiktok import TikTok  # noqa: E402

TT = os.environ.get("CREATORS_LIVE_TT", "lilyterpfr")
IG = os.environ.get("CREATORS_LIVE_IG", "daddywellness")
LIVE = os.environ.get("LIVE") == "1"
REAL_IG_BROWSER = Path(ROOT / "sections/creators/data/ig-browser")


def show(label, value):
    print(f"  [{label}] {value}", flush=True)


@unittest.skipUnless(LIVE, "set LIVE=1")
class TikTokLive(unittest.TestCase):
    def test_adapter(self):
        t = TikTok()
        p = t.profile(TT)
        show("profile", f"@{p.username} followers={p.followers:,} bio={p.bio[:40]!r}")
        self.assertGreater(p.followers, 0)
        posts = t.recent_posts(TT, 10)
        show("posts", [(x.url.rsplit('/', 1)[-1], x.views, x.comments) for x in posts[:5]])
        self.assertTrue(all(x.views is not None for x in posts))
        with_c = max(posts, key=lambda x: x.comments or 0)
        comments = t.comments(with_c.url, 20)
        show("comments", comments[:5])
        self.assertTrue(comments)
        single = t.post(with_c.url)
        show("single post", (single.views, single.likes, single.comments))
        self.assertGreater(single.views, 0)
        with self.assertRaises(PlatformError):
            t.profile("this-user-should-not-exist-938475")

    def test_lead_to_measured_post(self):
        conn = connect(Path(os.environ["CREATORS_DATA"]) / "live.db")
        t = TikTok()
        plats = {"tiktok": t, "instagram": Instagram()}
        latest = t.recent_posts(TT, 3)[0]
        pid = intake.add(conn, latest.url, "live-test", plats)          # a post link resolves to its creator
        self.assertEqual(intake.add(conn, f"https://www.tiktok.com/@{TT}", "live-test", plats), pid)
        h = conn.execute("SELECT id FROM handles WHERE person_id=? AND platform='tiktok'", (pid,)).fetchone()
        snapshot.refresh(conn, h["id"], plats)
        s = conn.execute("SELECT * FROM snapshots ORDER BY id DESC LIMIT 1").fetchone()
        show("snapshot", f"followers={s['followers']:,} median={s['median_views']:,} posts={s['posts_sampled']} "
                         f"30d={s['posts_last_30d']} comments={len(json.loads(s['comments']))}")
        self.assertGreater(s["median_views"], 0)
        use_judge = os.environ.get("CREATORS_LIVE_NO_JUDGE") != "1"
        sc = vetting.vet(conn, pid, use_judge=use_judge)
        show("score", f"{sc.score}/100 {sc.track}")
        if use_judge:
            j = json.loads(conn.execute("SELECT judgement FROM scores ORDER BY id DESC LIMIT 1").fetchone()[0])
            show("judge", j)
            self.assertIn(j.get("fit"), {"good", "maybe", "poor"})
        # a deal whose match term is a word from a real caption: the job must find that real post
        word = max(re.findall(r"[#\w]{4,}", latest.caption) or [latest.url.rsplit("/", 1)[-1]], key=len)
        for ev in ("shortlist", "contacted", "replied"):
            advance(conn, pid, ev)
        start = date.fromtimestamp(latest.posted_at) - timedelta(days=1)
        did = deals.propose(conn, pid, deals.Terms("ugc", "tiktok", 200, videos=1, match_terms=[word]), start)
        deals.approve(conn, did)
        deals.sign(conn, did, start)
        found = deliverables.find_posts(conn, did, plats)
        dl = conn.execute("SELECT * FROM deliverables WHERE deal_id=?", (did,)).fetchone()
        show("find_posts", f"term={word!r} -> {dl['post_url']}")
        self.assertEqual(len(found), 1)
        performance.measure(conn, dl["id"], plats)
        m = conn.execute("SELECT * FROM post_metrics ORDER BY id DESC LIMIT 1").fetchone()
        show("measure", f"views={m['views']} likes={m['likes']} comments={m['comments']} what_app={m['what_app']}")
        self.assertIsNotNone(m["views"])
        show("renewal", performance.renewal(conn, did))


@unittest.skipUnless(LIVE, "set LIVE=1")
class InstagramLive(unittest.TestCase):
    def test_anonymous_is_refused_loudly(self):
        with self.assertRaises(PlatformError):
            Instagram(cookies={}).profile(IG)

    @unittest.skipUnless(REAL_IG_BROWSER.exists(), "no Instagram research login: run `sections/creators/creators ig-login` once")
    def test_adapter_and_lead(self):
        from creatorops.platforms.instagram_browser import BrowserInstagram
        ig = BrowserInstagram(profile_dir=REAL_IG_BROWSER)
        p = ig.profile(IG)
        show("ig profile", f"@{p.username} followers={p.followers:,}")
        posts = ig.recent_posts(IG, 12)
        show("ig posts", [(x.url, x.views, x.comments) for x in posts[:5]])
        self.assertTrue(posts)
        with_c = max(posts, key=lambda x: x.comments or 0)
        comments = ig.comments(with_c.url, 20)
        show("ig comments", comments[:5])
        self.assertTrue(comments)
        single = ig.post(with_c.url)
        show("ig single post", (single.views, single.likes, single.comments))
        self.assertEqual(single.url, with_c.url)
        self.assertTrue(any(x.views for x in posts), "no reel views read")
        conn = connect(":memory:")
        pid = intake.add(conn, f"https://www.instagram.com/{IG}/", "live-test")
        snapshot.refresh(conn, 1, {"instagram": ig})
        show("ig score", vetting.vet(conn, pid, use_judge=False).score)


@unittest.skipUnless(LIVE, "set LIVE=1")
class OutboundLive(unittest.TestCase):
    def test_resend_email(self):
        # Resend's test inbox: a real API send that reaches no person
        mid = ResendEmail().send("delivered@resend.dev", "creator system live test", "If you can read this the email channel works.")
        show("resend id", mid)
        self.assertTrue(mid)

    def test_dashboard_on_real_tiktok(self):
        from http.server import ThreadingHTTPServer
        from creatorops.channels import default_channels
        from creatorops.dashboard import make_handler
        db = Path(os.environ["CREATORS_DATA"]) / "dash-live.db"
        srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(db, lambda: {"tiktok": TikTok(), "instagram": Instagram()},
                                                                 default_channels))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_port}"
        try:
            urllib.request.urlopen(base + "/add", urllib.parse.urlencode({"text": f"tt:{TT}"}).encode()).read()
            urllib.request.urlopen(base + "/jobs", b"").read()
            html = urllib.request.urlopen(base + "/").read().decode()
            m = re.search(r"(\d+)/100 · (\w+)", html)
            show("dashboard inbox", m.group(0) if m else html[:300])
            self.assertIsNotNone(m)
        finally:
            srv.shutdown()


if __name__ == "__main__":
    unittest.main(verbosity=2)
