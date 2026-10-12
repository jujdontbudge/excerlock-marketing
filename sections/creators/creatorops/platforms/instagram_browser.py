"""Instagram adapter that reads pages the way a person does: a real Chrome, logged in with the dedicated
research account, opening profile, reels and post pages and reading the data those pages load.
Instagram's JSON API answers 429 to scripted calls even with a valid session; page views keep working.

Login lives in a persistent Chrome profile at data/ig-browser (created by `creators ig-login`).
Photo posts have no view count on Instagram; only reels do, so medians use reels.
"""
from __future__ import annotations

import atexit
import json
import re
import threading

from . import PlatformError, Post, Profile

_lock = threading.Lock()


def _find(obj, key):
    """Every value stored under `key` anywhere in a JSON tree."""
    out = []
    stack = [obj]
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            for k, v in o.items():
                if k == key:
                    out.append(v)
                stack.append(v)
        elif isinstance(o, list):
            stack.extend(o)
    return out


def taken_at_from_code(code: str) -> int:
    """Instagram media ids start with milliseconds since 2011-08-24 (Instagram's epoch)."""
    from .instagram import shortcode_to_id
    return int(((shortcode_to_id(code[:11]) >> 23) + 1314220021721) / 1000)


class BrowserInstagram:
    name = "instagram"

    def __init__(self, profile_dir=None, headless=True):
        from ..db import DATA
        self.dir = str(profile_dir or DATA / "ig-browser")
        self.headless = headless
        self._pw = self._ctx = None

    def _page(self):
        if self._ctx is None:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self._ctx = self._pw.chromium.launch_persistent_context(
                self.dir, channel="chrome", headless=self.headless, args=["--no-proxy-server"],
                viewport={"width": 1280, "height": 1000})
            atexit.register(self.close)
        return self._ctx.new_page()

    def close(self):
        if self._ctx:
            self._ctx.close()
            self._pw.stop()
            self._ctx = None

    def _visit(self, url: str, scroll: bool = False) -> tuple[list, str]:
        """Open a page; return the JSON bodies it loaded plus the page HTML."""
        with _lock:
            page = self._page()
            bodies = []

            def grab(r):
                if ("graphql" in r.url or "/api/v1/" in r.url) and r.status == 200:
                    try:
                        bodies.append(json.loads(r.text()))
                    except Exception:
                        pass
            page.on("response", grab)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(6000)
                if scroll:
                    page.mouse.wheel(0, 4000)
                    page.wait_for_timeout(3000)
                if "/accounts/login" in page.url:
                    raise PlatformError("instagram: research account is logged out; run `creators ig-login`")
                html = page.content()
            finally:
                page.close()
        for m in re.finditer(r'<script type="application/json"[^>]*>(.*?)</script>', html, re.S):
            try:
                bodies.append(json.loads(m.group(1)))
            except ValueError:
                pass
        return bodies, html

    def profile(self, username: str) -> Profile:
        bodies, html = self._visit(f"https://www.instagram.com/{username}/")
        users = [u for b in bodies for u in _find(b, "user")
                 if isinstance(u, dict) and u.get("username", "").lower() == username.lower() and "follower_count" in u]
        if users:
            u = users[0]
            links = [l.get("url") for l in u.get("bio_links") or [] if l.get("url")] + ([u["external_url"]] if u.get("external_url") else [])
            return Profile("instagram", username.lower(), u.get("follower_count"), u.get("biography") or "", u.get("full_name") or "", links)
        m = re.search(r'content="([\d.,]+[KkMm]?) Followers', html)
        if not m:
            raise PlatformError(f"instagram @{username}: profile not found or not readable")
        n = m.group(1).replace(",", "")
        mult = {"k": 1e3, "m": 1e6}.get(n[-1].lower(), 1)
        return Profile("instagram", username.lower(), int(float(n.rstrip("KkMm")) * mult))

    def recent_posts(self, username: str, n: int = 20) -> list[Post]:
        bodies, _ = self._visit(f"https://www.instagram.com/{username}/", scroll=True)
        nodes = {}
        for b in bodies:
            for conn in _find(b, "xdt_api__v1__feed__user_timeline_graphql_connection"):
                for e in conn.get("edges") or []:
                    nd = e.get("node") or {}
                    if nd.get("code"):
                        nodes[nd["code"]] = nd
        reels, _ = self._visit(f"https://www.instagram.com/{username}/reels/", scroll=True)
        plays = {}
        for b in reels:
            for media in _find(b, "media"):
                if isinstance(media, dict) and media.get("code") and media.get("play_count") is not None:
                    plays[media["code"]] = media
        if not nodes and not plays:
            raise PlatformError(f"instagram @{username}: no posts returned")
        posts = []
        for code in dict.fromkeys(list(nodes) + list(plays)):
            nd, rl = nodes.get(code, {}), plays.get(code, {})
            cap = (nd.get("caption") or {}).get("text", "") if isinstance(nd.get("caption"), dict) else ""
            posts.append(Post(f"https://www.instagram.com/p/{code}/", username.lower(), rl.get("play_count"),
                              nd.get("like_count", rl.get("like_count")), nd.get("comment_count", rl.get("comment_count")),
                              nd.get("taken_at") or rl.get("taken_at") or taken_at_from_code(code), cap))
        posts.sort(key=lambda p: p.posted_at or 0, reverse=True)
        return posts[:n]

    def _post_page(self, url: str):
        code = re.search(r"/(?:p|reel|reels)/([\w-]+)", url)
        if not code:
            raise PlatformError(f"instagram: no shortcode in {url}")
        bodies, _ = self._visit(f"https://www.instagram.com/p/{code.group(1)}/")
        items = [i for b in bodies for info in _find(b, "xdt_api__v1__media__shortcode__web_info")
                 for i in (info.get("items") or [])]
        if not items:
            raise PlatformError(f"instagram post {url}: not found")
        return code.group(1), items[0], bodies

    def post(self, url: str) -> Post:
        code, it, _ = self._post_page(url)
        user = (it.get("user") or {}).get("username", "").lower()
        views = it.get("play_count") or it.get("ig_play_count") or it.get("view_count")
        if views is None and it.get("media_type") == 2 and user:      # reel: views only show on the reels grid
            reels, _ = self._visit(f"https://www.instagram.com/{user}/reels/", scroll=True)
            for b in reels:
                for media in _find(b, "media"):
                    if isinstance(media, dict) and media.get("code") == code:
                        views = media.get("play_count")
        cap = (it.get("caption") or {}).get("text", "") if isinstance(it.get("caption"), dict) else ""
        return Post(f"https://www.instagram.com/p/{code}/", user, views, it.get("like_count"), it.get("comment_count"),
                    it.get("taken_at"), cap)

    def comments(self, url: str, n: int = 50) -> list[str]:
        _, _, bodies = self._post_page(url)
        out = []
        for b in bodies:
            for conn in _find(b, "xdt_api__v1__media__media_id__comments__connection"):
                out += [(e.get("node") or {}).get("text", "") for e in conn.get("edges") or []]
        return [c for c in out if c][:n]
