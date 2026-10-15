"""Whole lifecycle through module interfaces with fake platforms and channels. No network."""
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

os.environ["CREATORS_DATA"] = tempfile.mkdtemp()
# local test servers must not go through a system proxy
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
os.environ["CREATORS_JUDGE_CMD"] = "true"  # offline: the AI judge returns nothing, the number still stands
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from creatorops import deals, deliverables, intake, jobs, outreach, performance, snapshot, vetting  # noqa: E402
from creatorops.db import connect  # noqa: E402
from creatorops.pipeline import IllegalMove, advance  # noqa: E402
from creatorops.platforms import handles_in_bio, parse_link  # noqa: E402
from fakes import FakeChannel, FakePlatform, Post, Profile  # noqa: E402

NOW = int(time.time())


def world():
    tt, ig = FakePlatform("tiktok"), FakePlatform("instagram")
    tt.profiles["jane.fit"] = Profile("tiktok", "jane.fit", 40000, "gym girl | IG: jane.lifts | jane@mail.com", "Jane Doe")
    tt.posts["jane.fit"] = [Post(f"https://www.tiktok.com/@jane.fit/video/{i}", "jane.fit", 20000 + i * 1000, 900, 40,
                                 NOW - i * 2 * 86400, "leg day") for i in range(1, 13)]
    tt.comment_map[tt.posts["jane.fit"][0].url] = ["what app is this??", "I love how you explain your routine",
                                                   "🔥🔥", "where did you get those leggings", "@friend"]
    ig.profiles["jane.lifts"] = Profile("instagram", "jane.lifts", 9000, "", "Jane")
    ig.posts["jane.lifts"] = [Post(f"https://www.instagram.com/p/AAA{i}/", "jane.lifts", 3000, 100, 5, NOW - i * 86400) for i in range(5)]
    return {"tiktok": tt, "instagram": ig}, {"email": FakeChannel("email"), "dm": FakeChannel("dm")}


class Pure(unittest.TestCase):
    def test_parse_link(self):
        self.assertEqual(parse_link("https://www.tiktok.com/@Jane.Fit?lang=en")["username"], "jane.fit")
        self.assertEqual(parse_link("https://www.tiktok.com/@jane.fit/video/123")["kind"], "post")
        self.assertEqual(parse_link("https://www.instagram.com/jane.lifts/")["platform"], "instagram")
        self.assertEqual(parse_link("https://www.instagram.com/reel/Cx12_ab/")["kind"], "post")
        self.assertEqual(parse_link("ig:jane.lifts")["username"], "jane.lifts")
        self.assertEqual(parse_link("Jane@Mail.com")["kind"], "email")
        with self.assertRaises(ValueError):
            parse_link("hello")

    def test_bio_handles(self):
        self.assertEqual(handles_in_bio("IG: jane.lifts | tiktok.com/@jane.fit"),
                         [("tiktok", "jane.fit"), ("instagram", "jane.lifts")])

    def test_score(self):
        big = vetting.score(120000, [100000] * 10, ["what app is this?", "this is so true for me"], 10)
        small = vetting.score(800, [800, 50, 60], ["🔥", "😍"], 1)
        self.assertEqual(big.track, "influencer")
        self.assertEqual(small.track, "ugc")
        self.assertGreater(big.score, 85)
        self.assertLess(small.score, 25)

    def test_schedule(self):
        days = deliverables.schedule(4, date(2026, 10, 1), 14, seed=7)
        self.assertEqual(len(days), 4)
        self.assertEqual(days, sorted(days))
        self.assertTrue(all(date(2026, 10, 1) <= d < date(2026, 10, 15) for d in days))
        self.assertEqual(days, deliverables.schedule(4, date(2026, 10, 1), 14, seed=7))

    def test_what_app(self):
        self.assertEqual(performance.what_app_count(["What's the app called", "what app is this", "which app??",
                                                     "app name pls", "cute", "love the app"]), 4)


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        self.plats, self.chans = world()

    def stage(self, pid):
        return self.conn.execute("SELECT stage FROM people WHERE id=?", (pid,)).fetchone()["stage"]

    def lead(self):
        pid = intake.add(self.conn, "https://www.tiktok.com/@jane.fit", "test", self.plats)
        for h in self.conn.execute("SELECT id FROM handles WHERE person_id=?", (pid,)).fetchall():
            snapshot.refresh(self.conn, h["id"], self.plats)
        return pid

    def test_intake_dedupes_and_discovers(self):
        pid = self.lead()
        self.assertEqual(intake.add(self.conn, "tt:jane.fit", "phone", self.plats), pid)
        self.assertEqual(intake.add(self.conn, "https://www.instagram.com/jane.lifts/", "form", self.plats), pid)
        p = self.conn.execute("SELECT * FROM people WHERE id=?", (pid,)).fetchone()
        self.assertEqual((p["email"], p["name"]), ("jane@mail.com", "Jane Doe"))
        other = intake.add(self.conn, "tt:someone.else", "test")
        intake.merge(self.conn, pid, other)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM handles WHERE person_id=?", (pid,)).fetchone()[0], 3)

    def test_overlapping_senders_send_each_email_once(self):
        # Review T03 (2026-10-15): the 3-hourly job and the dashboard approve both called send_approved on the same row.
        pid = self.lead()
        vetting.vet(self.conn, pid, use_judge=False)
        advance(self.conn, pid, "shortlist")
        mid = outreach.draft(self.conn, pid, "first")
        outreach.approve(self.conn, mid)
        other = sqlite3.connect(self.path) if hasattr(self, "path") else None
        chans = self.chans
        inner = chans["email"].send

        def send_while_another_run_starts(*a, **kw):
            # a second run starts while the first one's provider call is in flight
            self.assertEqual(outreach.send_approved(self.conn, chans), [])
            return inner(*a, **kw)
        chans["email"].send = send_while_another_run_starts
        outreach.send_approved(self.conn, chans)
        self.assertEqual(len(chans["email"].sent), 1)

    def test_uncertain_send_is_never_retried(self):
        pid = self.lead()
        vetting.vet(self.conn, pid, use_judge=False)
        advance(self.conn, pid, "shortlist")
        mid = outreach.draft(self.conn, pid, "first")
        outreach.approve(self.conn, mid)

        def timeout(*a, **kw):
            raise TimeoutError("read timed out")
        self.chans["email"].send = timeout
        outreach.send_approved(self.conn, self.chans)
        self.assertEqual(self.conn.execute("SELECT status FROM messages WHERE id=?", (mid,)).fetchone()[0], "uncertain")
        self.chans["email"] = type(self.chans["email"])("email")
        outreach.send_approved(self.conn, self.chans)
        self.assertEqual(self.chans["email"].sent, [])

    def test_provider_gets_a_stable_idempotency_key(self):
        pid = self.lead()
        vetting.vet(self.conn, pid, use_judge=False)
        advance(self.conn, pid, "shortlist")
        mid = outreach.draft(self.conn, pid, "first")
        outreach.approve(self.conn, mid)
        keys = []
        inner = self.chans["email"].send
        self.chans["email"].send = lambda to, subject, body, idempotency_key=None: keys.append(idempotency_key) or inner(to, subject, body)
        outreach.send_approved(self.conn, self.chans)
        self.assertEqual(keys, [f"creatorops-message-{mid}"])

    def test_outreach_to_no_reply(self):
        pid = self.lead()
        vetting.vet(self.conn, pid, use_judge=False)
        self.assertEqual(self.stage(pid), "scored")
        with self.assertRaises(IllegalMove):
            advance(self.conn, pid, "signed")
        advance(self.conn, pid, "shortlist")
        mid = outreach.draft(self.conn, pid, "first")
        self.assertEqual(outreach.send_approved(self.conn, self.chans), [])  # nothing sends unapproved
        outreach.approve(self.conn, mid)
        outreach.send_approved(self.conn, self.chans)
        self.assertEqual(self.chans["email"].sent[0][0], "jane@mail.com")
        self.assertIn("Jane", self.chans["email"].sent[0][2])
        self.assertEqual(self.stage(pid), "contacted")
        day = date.today()
        for _ in range(3):
            day += timedelta(days=5)
            log = jobs.run(self.conn, self.plats, self.chans, today=day, use_judge=False)
            for m in log["followups"]:
                outreach.approve(self.conn, m)
                outreach.send_approved(self.conn, self.chans)
                self.conn.execute("UPDATE messages SET sent_at=? WHERE id=?", (day.isoformat() + "T00:00:00+00:00", m))
        self.assertEqual(self.stage(pid), "no_reply")
        self.assertEqual(len(self.chans["email"].sent), 3)

    def test_auto_send_and_dnc(self):
        pid = self.lead()
        vetting.vet(self.conn, pid, use_judge=False)
        advance(self.conn, pid, "shortlist")
        os.environ["CREATORS_AUTO_SEND"] = "first"
        try:
            outreach.draft(self.conn, pid, "first")
        finally:
            del os.environ["CREATORS_AUTO_SEND"]
        outreach.send_approved(self.conn, self.chans)
        self.assertEqual(self.stage(pid), "contacted")
        from creatorops.pipeline import do_not_contact
        do_not_contact(self.conn, pid, "asked")
        with self.assertRaises(ValueError):
            outreach.draft(self.conn, pid, "followup")

    def test_dm_needs_a_human(self):
        pid = intake.add(self.conn, "tt:jane.fit", "test")
        snapshot.refresh(self.conn, 1, self.plats)
        self.conn.execute("UPDATE people SET email=NULL WHERE id=?", (pid,))
        vetting.vet(self.conn, pid, use_judge=False)
        advance(self.conn, pid, "shortlist")
        mid = outreach.draft(self.conn, pid, "first")
        outreach.approve(self.conn, mid)
        outreach.send_approved(self.conn, self.chans)
        self.assertEqual(self.stage(pid), "shortlisted")      # not contacted until a human pastes it
        outreach.mark_dm_sent(self.conn, mid)
        self.assertEqual(self.stage(pid), "contacted")

    def test_deal_to_renewal(self):
        pid = self.lead()
        vetting.vet(self.conn, pid, use_judge=False)
        for ev in ("shortlist", "contacted", "replied"):
            advance(self.conn, pid, ev)
        start = date.today() - timedelta(days=10)
        did = deals.propose(self.conn, pid, deals.Terms("influencer", "tiktok", 400, videos=2, promo_code="JANE10"), start)
        brief = Path(self.conn.execute("SELECT brief_path FROM deals WHERE id=?", (did,)).fetchone()[0]).read_text()
        self.assertIn("JANE10", brief)
        self.assertNotIn("{", brief)
        with self.assertRaises(ValueError):
            deals.sign(self.conn, did, start)                  # captain hasn't approved
        deals.approve(self.conn, did)
        dls = deals.sign(self.conn, did, start)
        self.assertEqual(self.stage(pid), "signed")
        self.assertEqual(self.conn.execute("SELECT amount_usd FROM payments").fetchone()[0], 100)
        due = date.fromisoformat(self.conn.execute("SELECT due_date FROM deliverables WHERE id=?", (dls[0],)).fetchone()[0])
        log = jobs.run(self.conn, self.plats, self.chans, today=due, use_judge=False)
        self.assertEqual(len(log["reminders"]), 1)
        jobs.run(self.conn, self.plats, self.chans, today=due, use_judge=False)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM messages WHERE kind='reminder'").fetchone()[0], 1)
        # creator posts twice with the code; jobs finds, measures and closes the deal
        tt = self.plats["tiktok"]
        for i, url in enumerate(["https://www.tiktok.com/@jane.fit/video/901", "https://www.tiktok.com/@jane.fit/video/902"]):
            tt.posts["jane.fit"].insert(0, Post(url, "jane.fit", 50000, 3000, 120, NOW - (5 - i) * 86400, "my screen time fix, code JANE10"))
            tt.comment_map[url] = ["wait what app is this", "which app??", "omg same"]
        log = jobs.run(self.conn, self.plats, self.chans, today=date.today(), use_judge=False)
        self.assertEqual(len(log["posts_found"]), 2)
        self.assertEqual(len(log["measured"]), 2)
        self.assertEqual(log["closed"], [did])
        r = performance.renewal(self.conn, did)
        self.assertEqual((r["views"], r["what_app"], r["verdict"]), (100000, 4, "renew"))
        self.assertEqual(self.conn.execute("SELECT kind, amount_usd FROM payments ORDER BY id").fetchall()[1][:], ("balance", 300))

    def test_judge_parses_agent_output(self):
        class Out:
            returncode, stderr = 0, ""
            stdout = 'sure:\n{"content_type":"talking-head","audience":"gym girls","parasocial":"strong","fit":"good","reason":"x"}'
        self.assertEqual(vetting.judge("bio", ["c"], ["k"], run=lambda *a, **k: Out())["fit"], "good")


class Dashboard(unittest.TestCase):
    def test_pages_and_add(self):
        from creatorops.dashboard import make_handler
        from http.server import ThreadingHTTPServer
        db = Path(os.environ["CREATORS_DATA"]) / "dash.db"
        plats, chans = world()
        srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(db, lambda: plats, lambda: chans))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_port}"
        try:
            data = urllib.parse.urlencode({"text": "tt:jane.fit"}).encode()
            body = urllib.request.urlopen(base + "/add", data).read().decode()
            self.assertIn("Propose a deal", body)
            urllib.request.urlopen(base + "/jobs", b"").read()
            self.assertIn("Pick who to contact (1)", urllib.request.urlopen(base + "/").read().decode())
            for path in ("/board", "/deals", "/person/1"):
                self.assertEqual(urllib.request.urlopen(base + path).status, 200)
        finally:
            srv.shutdown()


class FakeHTTP:
    """Records requests and answers like PayPal's sandbox."""
    def __init__(self):
        self.calls = []

    def _resp(self, code, body):
        class R:
            status_code, text = code, json.dumps(body)
            def json(self_inner):
                return body
        return R()

    def post(self, url, **kw):
        self.calls.append(("POST", url, kw.get("json")))
        if url.endswith("/oauth2/token"):
            return self._resp(200, {"access_token": "tok"})
        return self._resp(201, {"batch_header": {"payout_batch_id": "BATCH1"}})

    def get(self, url, **kw):
        self.calls.append(("GET", url, None))
        return self._resp(200, {"batch_header": {"batch_status": "SUCCESS"}, "items": [{"transaction_status": "SUCCESS"}]})


class PortalAndPayouts(unittest.TestCase):
    def setUp(self):
        self.db = Path(tempfile.mkdtemp()) / "p.db"
        self.conn = connect(self.db)
        plats, _ = world()
        pid = intake.add(self.conn, "tt:jane.fit", "test")
        snapshot.refresh(self.conn, 1, plats)
        vetting.vet(self.conn, pid, use_judge=False)
        for ev in ("shortlist", "contacted", "replied"):
            advance(self.conn, pid, ev)
        self.did = deals.propose(self.conn, pid, deals.Terms("ugc", "tiktok", 300, videos=1, upfront_pct=50))
        self.offer = deals.approve(self.conn, self.did)
        self.token = self.conn.execute("SELECT portal_token FROM deals WHERE id=?", (self.did,)).fetchone()[0]
        self.pid = pid

    def test_offer_carries_portal_link(self):
        body = self.conn.execute("SELECT body FROM messages WHERE id=?", (self.offer,)).fetchone()[0]
        self.assertIn(f"/c/{self.token}", body)

    def test_creator_signs_and_hands_in_through_http(self):
        from http.server import ThreadingHTTPServer
        from creatorops.portal import make_handler
        mailer = FakeChannel("email")
        srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.db, lambda: mailer))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_port}/c/{self.token}"
        post = lambda path, **f: urllib.request.urlopen(base + path, urllib.parse.urlencode(f).encode()).read().decode()
        try:
            self.assertIn("Sign agreement", urllib.request.urlopen(base).read().decode())
            with self.assertRaises(urllib.error.HTTPError):       # unticked boxes refuse
                post("/sign", legal_name="Jane Doe", email="jane@mail.com")
            page = post("/sign", legal_name="Jane Doe", email="jane@mail.com", esign="on", agree="on")
            self.assertIn("Signed by Jane Doe", page)
            post("/payout", method="paypal", address="jane@paypal.com", legal_name="Jane Doe", country="US")
            dl = self.conn.execute("SELECT id FROM deliverables WHERE deal_id=?", (self.did,)).fetchone()[0]
            post("/draft", id=dl, url="https://drive.google.com/x")
            deliverables.approve_draft(self.conn, dl)
            post("/post", id=dl, url="https://www.tiktok.com/@jane.fit/video/777")
            with self.assertRaises(urllib.error.HTTPError):
                urllib.request.urlopen(f"http://127.0.0.1:{srv.server_port}/c/wrong-token/sign", b"legal_name=x")
        finally:
            srv.shutdown()
        c = connect(self.db)
        sig = c.execute("SELECT * FROM signatures").fetchone()
        self.assertEqual(len(sig["contract_sha256"]), 64)
        self.assertEqual(c.execute("SELECT status FROM deals WHERE id=?", (self.did,)).fetchone()[0], "done")
        self.assertEqual(mailer.sent[0][0], "jane@mail.com")
        self.assertEqual([r[0] for r in c.execute("SELECT kind FROM payments ORDER BY id")], ["upfront", "balance"])

    def test_paypal_payout_is_idempotent_and_settles(self):
        from creatorops import payouts
        from creatorops.portal import save_payout
        deals.sign(self.conn, self.did, date.today())
        pay = self.conn.execute("SELECT id FROM payments").fetchone()[0]
        with self.assertRaises(payouts.PayoutError):                 # no payout details yet
            payouts.approve(self.conn, pay, payouts.PayPal("id", "secret", http=FakeHTTP()))
        save_payout(self.conn, self.token, "paypal", "jane@paypal.com", "Jane Doe", "US")
        http = FakeHTTP()
        pp = payouts.PayPal("id", "secret", http=http)
        self.assertEqual(payouts.approve(self.conn, pay, pp), "sending")
        body = [c[2] for c in http.calls if c[1].endswith("/payouts")][0]
        self.assertEqual(body["sender_batch_header"]["sender_batch_id"], f"excerlock-payment-{pay}")
        self.assertEqual(body["items"][0]["amount"]["value"], "150.00")
        self.assertEqual(payouts.approve(self.conn, pay, pp), "sending")   # second click sends nothing
        self.assertEqual(len([c for c in http.calls if c[1].endswith("/payouts")]), 1)
        self.assertEqual(payouts.check_sending(self.conn, pp), [pay])
        self.assertEqual(self.conn.execute("SELECT status FROM payments WHERE id=?", (pay,)).fetchone()[0], "paid")

    def test_manual_payout(self):
        from creatorops import payouts
        deals.sign(self.conn, self.did, date.today())
        pay = self.conn.execute("SELECT id FROM payments").fetchone()[0]
        self.assertEqual(payouts.approve(self.conn, pay, payouts.Manual()), "approved")
        payouts.mark_paid(self.conn, pay)
        self.assertEqual(self.conn.execute("SELECT status FROM payments WHERE id=?", (pay,)).fetchone()[0], "paid")

    def test_old_store_migrates(self):
        import sqlite3
        old = Path(tempfile.mkdtemp()) / "old.db"
        with sqlite3.connect(old) as c:
            c.execute("CREATE TABLE deals (id INTEGER PRIMARY KEY, person_id INTEGER)")
            c.execute("CREATE TABLE payments (id INTEGER PRIMARY KEY)")
        cols = {r["name"] for r in connect(old).execute("PRAGMA table_info(deals)")}
        self.assertIn("portal_token", cols)


class Inbound(unittest.TestCase):
    def sign(self, secret, body, ts=None):
        import base64, hashlib, hmac
        ts = str(ts or int(time.time()))
        key = base64.b64decode(secret.removeprefix("whsec_"))
        sig = base64.b64encode(hmac.new(key, f"msg_1.{ts}.".encode() + body, hashlib.sha256).digest()).decode()
        return {"svix-id": "msg_1", "svix-timestamp": ts, "svix-signature": f"v1,{sig}"}

    def test_reply_moves_stage_and_no_blocks(self):
        from creatorops import inbound
        conn = connect(":memory:")
        a = intake.add(conn, "tt:a", "t"); b = intake.add(conn, "tt:b", "t")
        for pid, mail in ((a, "a@x.com"), (b, "b@x.com")):
            conn.execute("UPDATE people SET email=?, stage='contacted' WHERE id=?", (mail, pid))
        secret = "whsec_" + __import__("base64").b64encode(b"k" * 24).decode()
        body = json.dumps({"type": "email.received", "data": {"email_id": "e1", "from": "A <a@x.com>", "subject": "Re: hi"}}).encode()
        self.assertEqual(inbound.handle_webhook(conn, self.sign(secret, body), body, secret), "ok")
        self.assertEqual(conn.execute("SELECT stage FROM people WHERE id=?", (a,)).fetchone()[0], "replied")
        inbound.handle_webhook(conn, self.sign(secret, body), body, secret)          # same email twice: stored once
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM replies").fetchone()[0], 1)
        with self.assertRaises(PermissionError):
            inbound.handle_webhook(conn, self.sign("whsec_" + "AAAA" * 6, body), body, secret)
        with self.assertRaises(PermissionError):
            inbound.handle_webhook(conn, self.sign(secret, body, ts=int(time.time()) - 3600), body, secret)
        inbound.record(conn, "b@x.com", "Re: PAID SPONSORSHIP", "No thanks\n\nOn Mon, Johan wrote:\n> Hey")
        row = conn.execute("SELECT stage, do_not_contact FROM people WHERE id=?", (b,)).fetchone()
        self.assertEqual(tuple(row), ("declined", 1))


if __name__ == "__main__":
    unittest.main()
