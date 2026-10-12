"""TikTok adapter. Free sources only: the public profile page, yt-dlp and the web comment endpoint."""
from __future__ import annotations

import json
import re

import requests
import yt_dlp

from . import PlatformError, Post, Profile

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
_STATE = re.compile(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', re.S)


class TikTok:
    name = "tiktok"

    def __init__(self, session: requests.Session | None = None):
        self.http = session or requests.Session()
        self.http.headers.update({"User-Agent": UA, "Referer": "https://www.tiktok.com/"})

    def profile(self, username: str) -> Profile:
        r = self.http.get(f"https://www.tiktok.com/@{username}", timeout=30)
        m = _STATE.search(r.text)
        if r.status_code != 200 or not m:
            raise PlatformError(f"tiktok profile @{username}: HTTP {r.status_code}, no page state")
        info = json.loads(m.group(1)).get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {}).get("userInfo")
        if not info or not info.get("user"):
            raise PlatformError(f"tiktok profile @{username}: account not found or private")
        user, stats = info["user"], info.get("stats") or info.get("statsV2") or {}
        link = (user.get("bioLink") or {}).get("link")
        return Profile("tiktok", user.get("uniqueId", username).lower(), int(stats.get("followerCount", 0)),
                       user.get("signature", ""), user.get("nickname", ""), [link] if link else [])

    def _ydl(self, url: str, flat: bool, end: int | None = None) -> dict:
        opts = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": flat}
        if end:
            opts["playlistend"] = end
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            raise PlatformError(f"tiktok via yt-dlp {url}: {e}") from e

    @staticmethod
    def _post(e: dict, username: str) -> Post:
        url = e.get("webpage_url") or e.get("url")
        return Post(url, (e.get("uploader") or username).lower(), e.get("view_count"), e.get("like_count"),
                    e.get("comment_count"), e.get("timestamp"), e.get("description") or e.get("title") or "")

    def recent_posts(self, username: str, n: int = 20) -> list[Post]:
        info = self._ydl(f"https://www.tiktok.com/@{username}", flat=True, end=n)
        entries = [e for e in info.get("entries") or [] if e]
        if not entries:
            raise PlatformError(f"tiktok @{username}: no videos returned")
        posts = [self._post(e, username) for e in entries[:n]]
        return sorted(posts, key=lambda p: p.posted_at or 0, reverse=True)

    def post(self, url: str) -> Post:
        info = self._ydl(url, flat=False)
        m = re.search(r"@([\w.]+)/", url)
        return self._post(info, m.group(1) if m else "")

    def comments(self, url: str, n: int = 50) -> list[str]:
        m = re.search(r"/(?:video|photo)/(\d+)", url)
        if not m:
            raise PlatformError(f"tiktok comments: no post id in {url}")
        out, cursor = [], 0
        while len(out) < n:
            r = self.http.get("https://www.tiktok.com/api/comment/list/", timeout=30, params={
                "aid": 1988, "aweme_id": m.group(1), "count": min(50, n - len(out)), "cursor": cursor})
            if r.status_code != 200 or not r.text:
                raise PlatformError(f"tiktok comments {url}: HTTP {r.status_code}")
            d = r.json()
            out += [c.get("text", "") for c in d.get("comments") or []]
            if not d.get("has_more") or not d.get("comments"):
                break
            cursor = d.get("cursor", cursor + 50)
        return out[:n]
