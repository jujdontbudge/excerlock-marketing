"""Snapshot: dated stats for one handle (followers, median views, recent comments) plus contact discovery."""
from __future__ import annotations

import json
import sqlite3
import statistics
import time

from .db import event, now
from .intake import _person_for, attach
from .platforms import EMAIL, handles_in_bio

POSTS = 20          # Jake: judge baseline views over recent posts, not the few that popped
COMMENT_POSTS = 3   # posts whose comments are sampled
COMMENTS_EACH = 30


def summarize(posts: list, today: float | None = None) -> dict:
    """Pure: median views and activity from a list of Post."""
    today = today or time.time()
    views = [p.views for p in posts if p.views is not None]
    return {
        "posts_sampled": len(posts),
        "median_views": int(statistics.median(views)) if views else None,
        "posts_last_30d": sum(1 for p in posts if p.posted_at and today - p.posted_at < 30 * 86400),
    }


def refresh(conn: sqlite3.Connection, handle_id: int, platforms: dict) -> int:
    """Fetch and store a new snapshot for one handle. Returns the snapshot id. Raises PlatformError."""
    h = conn.execute("SELECT * FROM handles WHERE id=?", (handle_id,)).fetchone()
    adapter = platforms[h["platform"]]
    prof = adapter.profile(h["username"])
    posts = adapter.recent_posts(h["username"], POSTS)
    comments = []
    for p in sorted(posts, key=lambda p: p.comments or 0, reverse=True)[:COMMENT_POSTS]:
        if p.comments:
            comments += adapter.comments(p.url, COMMENTS_EACH)
    s = summarize(posts)
    cur = conn.execute(
        "INSERT INTO snapshots(handle_id, taken_at, followers, posts_sampled, median_views, posts_last_30d, bio, posts, comments)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (handle_id, now(), prof.followers, s["posts_sampled"], s["median_views"], s["posts_last_30d"], prof.bio,
         json.dumps([p.__dict__ for p in posts]), json.dumps(comments)))
    person = h["person_id"]
    text = "\n".join([prof.bio, *prof.links])
    for platform, username in handles_in_bio(text):
        if platform != h["platform"] and _person_for(conn, platform, username) is None:
            attach(conn, person, platform, username, f"bio of {h['platform']}:{h['username']}")
    if m := EMAIL.search(prof.bio):
        conn.execute("UPDATE people SET email=COALESCE(email, ?) WHERE id=?", (m.group(0).lower(), person))
    if prof.name:
        conn.execute("UPDATE people SET name=? WHERE id=? AND name=?", (prof.name, person, h["username"]))
    event(conn, "snapshot", person, handle=h["username"], platform=h["platform"], **s)
    conn.commit()
    return cur.lastrowid


def latest(conn: sqlite3.Connection, person_id: int) -> list[sqlite3.Row]:
    """Newest snapshot per handle of a person."""
    return conn.execute(
        "SELECT s.*, h.platform, h.username FROM snapshots s JOIN handles h ON h.id=s.handle_id"
        " WHERE h.person_id=? AND s.id = (SELECT MAX(id) FROM snapshots WHERE handle_id=h.id)", (person_id,)).fetchall()
