"""Platform seam: everything that reads TikTok or Instagram goes through one of these adapters.

An adapter has a `name` and four methods:
  profile(username) -> Profile
  recent_posts(username, n) -> list[Post]      newest first
  post(url) -> Post
  comments(url, n) -> list[str]
Every method raises PlatformError when the platform refuses or the data is missing; it never
returns an empty result to mean "blocked".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


class PlatformError(RuntimeError):
    pass


@dataclass
class Profile:
    platform: str
    username: str
    followers: int | None
    bio: str = ""
    name: str = ""
    links: list[str] = field(default_factory=list)


@dataclass
class Post:
    url: str
    username: str
    views: int | None
    likes: int | None
    comments: int | None
    posted_at: int | None  # unix seconds
    caption: str = ""


EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_TT_PROFILE = re.compile(r"tiktok\.com/@([\w.]+)", re.I)
_TT_POST = re.compile(r"tiktok\.com/@([\w.]+)/(?:video|photo)/(\d+)", re.I)
_IG_POST = re.compile(r"instagram\.com/(?:[\w.]+/)?(?:p|reel|reels)/([\w-]+)", re.I)
_IG_PROFILE = re.compile(r"instagram\.com/([\w.]+)/?(?:\?|$)", re.I)
_PREFIX = re.compile(r"^(tiktok|tt|instagram|ig)\s*[:@]\s*@?([\w.]+)$", re.I)


def parse_link(text: str) -> dict:
    """Classify one pasted thing: a profile link, a post link, an email or a prefixed handle.

    Returns {"kind": "profile"|"post"|"email", "platform", "username", "url"}; raises ValueError.
    """
    t = text.strip()
    if m := _TT_POST.search(t):
        return {"kind": "post", "platform": "tiktok", "username": m.group(1).lower(), "url": t.split("?")[0]}
    if m := _TT_PROFILE.search(t):
        return {"kind": "profile", "platform": "tiktok", "username": m.group(1).lower(), "url": None}
    if m := _IG_POST.search(t):
        return {"kind": "post", "platform": "instagram", "username": None, "url": t.split("?")[0]}
    if m := _IG_PROFILE.search(t):
        if m.group(1).lower() not in {"p", "reel", "reels", "explore", "stories"}:
            return {"kind": "profile", "platform": "instagram", "username": m.group(1).lower(), "url": None}
    if m := _PREFIX.match(t):
        platform = "tiktok" if m.group(1).lower() in {"tiktok", "tt"} else "instagram"
        return {"kind": "profile", "platform": platform, "username": m.group(2).lower(), "url": None}
    if m := EMAIL.fullmatch(t):
        return {"kind": "email", "platform": None, "username": None, "url": t.lower()}
    raise ValueError(f"Not a TikTok/Instagram link, prefixed handle (tt:name, ig:name) or email: {text!r}")


def handles_in_bio(text: str) -> list[tuple[str, str]]:
    """Other-platform handles a creator lists in their bio, e.g. 'IG: name' or an instagram.com link."""
    found = []
    for m in re.finditer(r"instagram\.com/([\w.]+)", text, re.I):
        found.append(("instagram", m.group(1).lower()))
    for m in re.finditer(r"tiktok\.com/@([\w.]+)", text, re.I):
        found.append(("tiktok", m.group(1).lower()))
    for m in re.finditer(r"\b(ig|insta|instagram|tt|tiktok)(?:\s*[:\-]\s*@?|\s*@)([\w.]{2,30})", text, re.I):
        found.append(("tiktok" if m.group(1).lower() in {"tt", "tiktok"} else "instagram", m.group(2).lower().rstrip(".")))
    return list(dict.fromkeys(found))


def default_platforms() -> dict:
    """Instagram reads through the logged-in research browser when it exists, else the session-cookie API."""
    from ..db import DATA
    from .instagram import Instagram
    from .instagram_browser import BrowserInstagram
    from .tiktok import TikTok
    ig = BrowserInstagram() if (DATA / "ig-browser").exists() else Instagram()
    return {"tiktok": TikTok(), "instagram": ig}
