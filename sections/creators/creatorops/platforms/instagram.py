"""Instagram adapter. Instagram refuses anonymous requests, so this uses a logged-in web session.

The session comes from `sections/creators/data/ig_session.json` (written by `creators ig-login`)
or the IG_SESSIONID environment variable. Use a spare account, not a personal one: automated
reads can get the session challenged.
"""
from __future__ import annotations

import json
import os
import re

import requests

from . import PlatformError, Post, Profile
from .tiktok import UA

APP_ID = "936619743392459"
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def shortcode_to_id(code: str) -> int:
    n = 0
    for ch in code:
        n = n * 64 + _ALPHABET.index(ch)
    return n


def session_file():
    from ..db import DATA
    return DATA / "ig_session.json"


class Instagram:
    name = "instagram"

    def __init__(self, cookies: dict | None = None):
        if cookies is None:
            cookies = {}
            f = session_file()
            if f.exists():
                cookies = json.loads(f.read_text())
            elif os.environ.get("IG_SESSIONID"):
                cookies = {"sessionid": os.environ["IG_SESSIONID"]}
        self.cookies = cookies
        self.http = requests.Session()
        self.http.headers.update({"User-Agent": UA, "X-IG-App-ID": APP_ID, "Referer": "https://www.instagram.com/"})
        for k, v in cookies.items():
            self.http.cookies.set(k, v, domain=".instagram.com")
        if "csrftoken" in cookies:
            self.http.headers["X-CSRFToken"] = cookies["csrftoken"]

    def _get(self, path: str, **params) -> dict:
        if "sessionid" not in self.cookies:
            raise PlatformError("instagram: no logged-in session; run `sections/creators/creators ig-login`")
        r = self.http.get("https://www.instagram.com" + path, params=params, timeout=30)
        if r.status_code != 200:
            raise PlatformError(f"instagram {path}: HTTP {r.status_code} {r.text[:120]}")
        try:
            return r.json()
        except ValueError as e:
            raise PlatformError(f"instagram {path}: not JSON (session expired?)") from e

    def _user(self, username: str) -> dict:
        user = self._get("/api/v1/users/web_profile_info/", username=username).get("data", {}).get("user")
        if not user:
            raise PlatformError(f"instagram @{username}: account not found")
        return user

    def profile(self, username: str) -> Profile:
        u = self._user(username)
        links = [b.get("url") for b in u.get("bio_links") or [] if b.get("url")]
        bio = u.get("biography", "")
        if u.get("business_email"):
            bio += f"\n{u['business_email']}"
        return Profile("instagram", u["username"].lower(), u.get("edge_followed_by", {}).get("count"),
                       bio, u.get("full_name", ""), links)

    @staticmethod
    def _item(it: dict) -> Post:
        cap = (it.get("caption") or {}).get("text", "") if isinstance(it.get("caption"), dict) else ""
        views = it.get("play_count") or it.get("ig_play_count") or it.get("view_count")
        return Post(f"https://www.instagram.com/p/{it['code']}/", it.get("user", {}).get("username", "").lower(),
                    views, it.get("like_count"), it.get("comment_count"), it.get("taken_at"), cap)

    def recent_posts(self, username: str, n: int = 20) -> list[Post]:
        uid = self._user(username)["id"]
        items, max_id = [], None
        while len(items) < n:
            d = self._get(f"/api/v1/feed/user/{uid}/", count=min(33, n), **({"max_id": max_id} if max_id else {}))
            items += d.get("items") or []
            max_id = d.get("next_max_id")
            if not d.get("more_available") or not max_id:
                break
        if not items:
            raise PlatformError(f"instagram @{username}: no posts returned")
        posts = [self._item(i) for i in items[:n]]
        return sorted(posts, key=lambda p: p.posted_at or 0, reverse=True)

    def _media_id(self, url: str) -> int:
        m = re.search(r"/(?:p|reel|reels)/([\w-]+)", url)
        if not m:
            raise PlatformError(f"instagram: no shortcode in {url}")
        return shortcode_to_id(m.group(1)[:11])

    def post(self, url: str) -> Post:
        items = self._get(f"/api/v1/media/{self._media_id(url)}/info/").get("items") or []
        if not items:
            raise PlatformError(f"instagram post {url}: not found")
        return self._item(items[0])

    def comments(self, url: str, n: int = 50) -> list[str]:
        mid, out, min_id = self._media_id(url), [], None
        while len(out) < n:
            d = self._get(f"/api/v1/media/{mid}/comments/", can_support_threading="true",
                          **({"min_id": min_id} if min_id else {}))
            out += [c.get("text", "") for c in d.get("comments") or []]
            min_id = d.get("next_min_id")
            if not min_id or not d.get("comments"):
                break
        return out[:n]
