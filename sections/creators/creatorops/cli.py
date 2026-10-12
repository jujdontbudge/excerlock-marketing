"""Command line for the creator system: sections/creators/creators <command> --help"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from dotenv import load_dotenv

from .db import DATA, SECTION, connect

load_dotenv(SECTION.parents[1] / ".env", override=False)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="creators", description=__doc__)
    ap.add_argument("--db", help="store path (default sections/creators/data/creators.db)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="add leads: links, tt:handle, ig:handle (args or a file with one per line)")
    a.add_argument("items", nargs="*")
    a.add_argument("--file")
    a.add_argument("--source", default="manual")
    sub.add_parser("jobs", help="refresh, score, follow-ups, reminders, post checks, measurements, sends")
    r = sub.add_parser("refresh", help="snapshot one person's handles now")
    r.add_argument("person", type=int)
    v = sub.add_parser("vet", help="score one person now")
    v.add_argument("person", type=int)
    v.add_argument("--no-judge", action="store_true")
    sub.add_parser("list", help="people by stage")
    s = sub.add_parser("serve", help="open the dashboard")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8765)
    pt = sub.add_parser("portal", help="serve the public creator portal (signing, payout details, draft links)")
    pt.add_argument("--host", default="127.0.0.1")
    pt.add_argument("--port", type=int, default=8766)
    b = sub.add_parser("backup", help="copy the store to data/backups/, keep the newest 30")
    il = sub.add_parser("ig-login", help="log the Instagram research account into data/ig-browser (or import its cookies)")
    il.add_argument("--cookies", help="JSON list of instagram.com cookies exported from a logged-in browser")
    il.add_argument("--headed", action="store_true", help="open a visible window and log in by hand")
    args = ap.parse_args(argv)

    if args.cmd == "ig-login":
        return ig_login(args.cookies, args.headed)
    if args.cmd == "portal":
        from .portal import serve as serve_portal
        return serve_portal(args.db, args.host, args.port)
    if args.cmd == "backup":
        return backup(connect(args.db))
    if args.cmd == "serve":
        from .dashboard import serve
        return serve(args.db, args.host, args.port)
    conn = connect(args.db)
    from .platforms import default_platforms
    if args.cmd == "add":
        from .intake import add
        items = list(args.items) + (open(args.file).read().split() if args.file else [])
        plats = default_platforms()
        for it in items:
            try:
                print(it, "-> person", add(conn, it, args.source, plats))
            except Exception as e:
                print(it, "-> ERROR", e, file=sys.stderr)
    elif args.cmd == "jobs":
        from .channels import default_channels
        from .jobs import run
        print(json.dumps(run(conn, default_platforms(), default_channels()), indent=1))
    elif args.cmd == "refresh":
        from .snapshot import refresh
        for h in conn.execute("SELECT id FROM handles WHERE person_id=?", (args.person,)).fetchall():
            print("snapshot", refresh(conn, h["id"], default_platforms()))
    elif args.cmd == "vet":
        from .vetting import vet
        s = vet(conn, args.person, not args.no_judge)
        print(s.score, s.track, *s.reasons, sep="\n")
    elif args.cmd == "list":
        for r in conn.execute("SELECT p.id, p.name, p.stage, (SELECT score FROM scores WHERE person_id=p.id ORDER BY id DESC LIMIT 1) sc"
                              " FROM people p ORDER BY p.stage, sc DESC"):
            print(f"{r['id']:>4}  {r['stage']:<12} {r['sc'] if r['sc'] is not None else '-':>4}  {r['name']}")


def backup(conn):
    """Consistent copy of the live store (SQLite online backup), newest 30 kept."""
    import sqlite3
    from datetime import datetime
    d = DATA / "backups"
    d.mkdir(parents=True, exist_ok=True)
    target = d / f"creators-{datetime.now():%Y%m%d-%H%M%S}.db"
    with sqlite3.connect(target) as out:
        conn.backup(out)
    for old in sorted(d.glob("creators-*.db"))[:-30]:
        old.unlink()
    print("backup", target)


def ig_login(cookies_file=None, headed=False):
    """Put a logged-in research account into data/ig-browser, then check it can read a profile."""
    import os
    from playwright.sync_api import sync_playwright
    DATA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(DATA / "ig-browser"), channel="chrome", headless=not headed,
                                                   args=["--no-proxy-server"])
        page = ctx.new_page()
        if cookies_file:
            ctx.add_cookies(json.loads(open(cookies_file).read()))
            page.goto("https://www.instagram.com/")
        else:
            page.goto("https://www.instagram.com/accounts/login/")
            page.wait_for_timeout(4000)
            user, pw = os.environ.get("IG_SCRAPER_USER"), os.environ.get("IG_SCRAPER_PASSWORD")
            login_field = page.locator("input[name=username], input[name=email]")
            if user and pw and login_field.is_visible():
                login_field.fill(user)
                page.locator("input[type=password]").fill(pw)
                page.keyboard.press("Enter")
            if headed:
                print("Finish login and any Instagram verification in the browser window (5 minutes)...", flush=True)

        def ready():
            blocked = ("/accounts/login", "/accounts/suspended", "/challenge/", "/checkpoint/")
            return (not any(path in page.url for path in blocked)
                    and any(c["name"] == "sessionid" for c in ctx.cookies("https://www.instagram.com")))

        for _ in range(300 if headed else 30):
            page.wait_for_timeout(1000)
            if ready():
                break
        ok = ready()
        print("logged in" if ok else f"login or verification unfinished (page: {page.url})")
        ctx.close()
    if not ok:
        raise SystemExit(1)
    if ok:
        from .platforms.instagram_browser import BrowserInstagram
        ig = BrowserInstagram()
        print("check:", ig.profile("instagram").followers, "followers on @instagram")
        ig.close()
