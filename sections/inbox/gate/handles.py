"""Is a handle a creator just linked a new account? (captain, 2026-10-14: "new" = created in the last 3 days.)

TikTok shows the account's creation time publicly. Instagram doesn't when logged out, so an Instagram account
only counts as new-looking (0 posts, under 50 followers, exists) and is never auto-approved on its own: the verdict
is 'pass' only when both accounts are linked, the TikTok was created within 3 days, and the Instagram looks new.
Everything else is 'ask' (goes to the captain) or 'fail' (clearly not new). Fetchers are free and headless.
"""
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import requests

NEW_DAYS = 3
IG_MAX_POSTS = 0
IG_MAX_FOLLOWERS = 50
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141 Safari/537.36'
IG_UA = 'Instagram 320.0.0.34.109 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100; en_US; 567067343)'


@dataclass(frozen=True)
class Profile:
    platform: str
    handle: str
    exists: bool
    created_at: datetime = None     # TikTok only
    posts: int = None
    followers: int = None
    error: str = None


def fetch_tiktok(handle, get=requests.get):
    try:
        html = get(f'https://www.tiktok.com/@{handle}', headers={'User-Agent': UA}, timeout=20).text
        m = re.search(r'__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', html)
        d = json.loads(m.group(1))['__DEFAULT_SCOPE__'].get('webapp.user-detail', {}) if m else {}
    except Exception as exc:
        return Profile('tiktok', handle, False, error=type(exc).__name__)
    user, stats = d.get('userInfo', {}).get('user', {}), d.get('userInfo', {}).get('stats', {})
    if not user.get('uniqueId'):
        return Profile('tiktok', handle, False, error=f'status {d.get("statusCode")}')
    if not _same_account(user.get('uniqueId'), handle):   # stats of another account prove nothing (review BM02)
        return Profile('tiktok', handle, False, error=f'TikTok returned a different account (@{user.get("uniqueId")})')
    created = user.get('createTime')
    return Profile('tiktok', handle, True, datetime.fromtimestamp(created, timezone.utc) if created else None,
                   stats.get('videoCount'), stats.get('followerCount'))


def fetch_instagram(handle, get=requests.get):
    try:
        r = get(f'https://i.instagram.com/api/v1/users/web_profile_info/?username={handle}',
                headers={'User-Agent': IG_UA, 'x-ig-app-id': '567067343352427'}, timeout=20)
        user = r.json()['data']['user']
    except Exception as exc:
        return Profile('instagram', handle, False, error=type(exc).__name__)
    if not user:
        return Profile('instagram', handle, False, error='not found')
    if not _same_account(user.get('username'), handle):   # stats of another account prove nothing (review BM02)
        return Profile('instagram', handle, False, error=f'Instagram returned a different account (@{user.get("username")})')
    return Profile('instagram', handle, True, None, user['edge_owner_to_timeline_media']['count'], user['edge_followed_by']['count'])


def _same_account(returned, requested):
    """The profile answered is the handle asked for (case-insensitive, without @). Missing = not proven."""
    return (isinstance(returned, str) and isinstance(requested, str)
            and returned.strip().lstrip('@').lower() == requested.strip().lstrip('@').lower())


def _known(n):
    return isinstance(n, int) and not isinstance(n, bool) and n >= 0


def judge(profiles, now=None):
    """profiles: {'tiktok': Profile|None, 'instagram': Profile|None} -> ('pass'|'ask'|'fail', [reasons]).
    Unknown or impossible data is never a pass (review G20)."""
    now = now or datetime.now(timezone.utc)
    reasons, fail = [], False
    tt, ig = profiles.get('tiktok'), profiles.get('instagram')
    if not tt or not ig:
        reasons.append('needs both a TikTok and an Instagram linked')
    if tt:
        if not tt.exists:
            reasons.append(f'TikTok @{tt.handle} could not be checked ({tt.error})')
        elif tt.created_at is None:
            reasons.append(f'TikTok @{tt.handle} has no creation date')
        elif tt.created_at > now + timedelta(minutes=10):
            reasons.append(f'TikTok @{tt.handle} shows a creation date in the future ({tt.created_at:%Y-%m-%d})')
        elif now - tt.created_at > timedelta(days=NEW_DAYS):
            fail = True
            reasons.append(f'TikTok @{tt.handle} was created {tt.created_at:%Y-%m-%d}, not in the last {NEW_DAYS} days')
        elif not _known(tt.posts) or not _known(tt.followers):
            reasons.append(f'TikTok @{tt.handle} video or follower count is unknown')
        elif tt.posts > 0:
            reasons.append(f'TikTok @{tt.handle} already has {tt.posts} videos')
    if ig:
        if not ig.exists:
            reasons.append(f'Instagram @{ig.handle} could not be checked ({ig.error})')
        elif not _known(ig.posts) or not _known(ig.followers):
            reasons.append(f'Instagram @{ig.handle} post or follower count is unknown')
        elif ig.posts > IG_MAX_POSTS:
            fail = True
            reasons.append(f'Instagram @{ig.handle} already has {ig.posts} posts')
        elif ig.followers >= IG_MAX_FOLLOWERS:
            fail = True
            reasons.append(f'Instagram @{ig.handle} already has {ig.followers} followers')
    for p in (tt, ig):   # captain, 2026-10-15: no "ugc" (or ExcerLock) in the username
        if p and re.search(r'ugc|excerlock', p.handle or '', re.I):
            fail = True
            reasons.append(f'@{p.handle} has "UGC" or "ExcerLock" in the username')
    if fail:
        return 'fail', reasons
    return ('ask', reasons) if reasons else ('pass', [f'TikTok created {tt.created_at:%Y-%m-%d}, Instagram has 0 posts'])


HANDLES = re.compile(r'@([A-Za-z0-9._]+) \((tiktok|instagram)\)')


ANY_HANDLE = re.compile(r'@([^\s()]+) \(([^)\s]+)\)')   # every "@handle (platform)", supported or not (BL02)
DECLARED = re.compile(r'Requested (\d+) handles')


def requested_pairs(handle_request_text):
    """Every (platform, handle) in a request notice, duplicates and unsupported platforms included (BG02, BL02). If
    the pairs don't add up to the count the notice declares, an ('unknown', 'incomplete-request') pair is added so
    the batch is never judged on part of it."""
    pairs = [(platform.lower(), handle) for handle, platform in ANY_HANDLE.findall(handle_request_text)]
    declared = DECLARED.search(handle_request_text)
    expected = int(declared.group(1)) if declared else 1
    if not pairs or len(pairs) != expected:
        pairs.append(('unknown', 'incomplete-request'))
    return pairs


def requested(handle_request_text):
    """'📨 Requested 2 handles: @a (tiktok), @a (instagram) for this contract.' -> {'tiktok': 'a', 'instagram': 'a'}"""
    return {platform: handle for handle, platform in HANDLES.findall(handle_request_text)}
