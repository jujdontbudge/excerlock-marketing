"""Deliverables: post-date schedule, draft review, finding the live post and lateness."""
from __future__ import annotations

import json
import random
import sqlite3
from datetime import date, datetime, timedelta, timezone

from .db import event, now


def schedule(videos: int, start: date, period_days: int, seed: int) -> list[date]:
    """Pure: spread posts evenly over the period with a random day inside each slot (Jake: don't negotiate dates)."""
    rng = random.Random(seed)
    slot = period_days / videos
    return [start + timedelta(days=int(i * slot + rng.random() * slot)) for i in range(videos)]


def record_draft(conn: sqlite3.Connection, deliverable_id: int, url: str) -> None:
    conn.execute("UPDATE deliverables SET draft_url=?, status='draft_in' WHERE id=?", (url, deliverable_id))
    event(conn, "draft_in", deal_id=_deal(conn, deliverable_id), deliverable=deliverable_id, url=url)
    conn.commit()


def approve_draft(conn: sqlite3.Connection, deliverable_id: int) -> None:
    conn.execute("UPDATE deliverables SET status='approved' WHERE id=? AND status='draft_in'", (deliverable_id,))
    conn.commit()


def record_post(conn: sqlite3.Connection, deliverable_id: int, url: str, posted_at: int | None = None) -> None:
    ts = datetime.fromtimestamp(posted_at, timezone.utc).isoformat() if posted_at else now()
    conn.execute("UPDATE deliverables SET post_url=?, posted_at=?, status='posted' WHERE id=?", (url, ts, deliverable_id))
    event(conn, "posted", deal_id=_deal(conn, deliverable_id), deliverable=deliverable_id, url=url)
    conn.commit()


def _deal(conn, deliverable_id):
    return conn.execute("SELECT deal_id FROM deliverables WHERE id=?", (deliverable_id,)).fetchone()["deal_id"]


def matches(caption: str, terms: list[str]) -> bool:
    c = caption.lower()
    return any(t.lower() in c for t in terms if t)


def find_posts(conn: sqlite3.Connection, deal_id: int, platforms: dict) -> list[int]:
    """Look at the creator's recent posts and link any that mention the deal's terms to open deliverables."""
    d = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
    terms = json.loads(d["match_terms"]) + ([d["promo_code"]] if d["promo_code"] else [])
    h = conn.execute("SELECT username FROM handles WHERE person_id=? AND platform=?", (d["person_id"], d["platform"])).fetchone()
    if not h or not terms:
        return []
    start = datetime.fromisoformat(d["start_date"]).replace(tzinfo=timezone.utc).timestamp() - 86400
    known = {r["post_url"] for r in conn.execute("SELECT post_url FROM deliverables WHERE post_url IS NOT NULL")}
    found = []
    for p in sorted(platforms[d["platform"]].recent_posts(h["username"], 20), key=lambda p: p.posted_at or 0):
        if p.url in known or (p.posted_at or 0) < start or not matches(p.caption, terms):
            continue
        open_ = conn.execute("SELECT id FROM deliverables WHERE deal_id=? AND post_url IS NULL ORDER BY due_date LIMIT 1",
                             (deal_id,)).fetchone()
        if not open_:
            break
        record_post(conn, open_["id"], p.url, p.posted_at)
        found.append(open_["id"])
    return found


def mark_late(conn: sqlite3.Connection, today: date) -> list[int]:
    rows = conn.execute("SELECT id FROM deliverables WHERE post_url IS NULL AND status!='late' AND due_date < ?",
                        (today.isoformat(),)).fetchall()
    for r in rows:
        conn.execute("UPDATE deliverables SET status='late' WHERE id=?", (r["id"],))
        event(conn, "late", deal_id=_deal(conn, r["id"]), deliverable=r["id"])
    conn.commit()
    return [r["id"] for r in rows]
