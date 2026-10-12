"""Performance: measure live posts and decide renew / fix / cut.

Jake's signal is the "wait, what app is this?" comment, not raw views. A post is measured at
1, 3 and 7 days old so every creator is compared on the same windows.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone

from .db import event, now

WINDOWS = (1, 3, 7)
WHAT_APP = re.compile(
    r"what(?:'?s| is)? (?:the |this |that )?app|which app|app name|name of (?:the |this )?app|"
    r"what app|link (?:to|for) (?:the |this )?app|where (?:can i|do i|to) (?:get|download)|"
    r"what'?s it called|is (?:this|it) on (?:android|iphone|ios)", re.I)


def what_app_count(comments: list[str]) -> int:
    return sum(1 for c in comments if WHAT_APP.search(c))


def measure(conn: sqlite3.Connection, deliverable_id: int, platforms: dict) -> int:
    d = conn.execute("SELECT dl.*, de.platform FROM deliverables dl JOIN deals de ON de.id=dl.deal_id WHERE dl.id=?",
                     (deliverable_id,)).fetchone()
    adapter = platforms[d["platform"]]
    post = adapter.post(d["post_url"])
    comments = adapter.comments(d["post_url"], 100) if post.comments else []
    posted = datetime.fromisoformat(d["posted_at"]) if d["posted_at"] else datetime.now(timezone.utc)
    age = (datetime.now(timezone.utc) - posted).total_seconds() / 86400
    hits = [c for c in comments if WHAT_APP.search(c)]
    cur = conn.execute("INSERT INTO post_metrics(deliverable_id, taken_at, age_days, views, likes, comments, what_app,"
                       " comment_sample) VALUES (?,?,?,?,?,?,?,?)",
                       (deliverable_id, now(), round(age, 2), post.views, post.likes, post.comments, len(hits),
                        json.dumps((hits + comments)[:20])))
    event(conn, "measured", deal_id=d["deal_id"], deliverable=deliverable_id, views=post.views, what_app=len(hits))
    conn.commit()
    return cur.lastrowid


def due_measurements(conn: sqlite3.Connection) -> list[int]:
    """Posted deliverables that have crossed a window without a measurement in it."""
    due = []
    for d in conn.execute("SELECT id, posted_at FROM deliverables WHERE post_url IS NOT NULL").fetchall():
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(d["posted_at"])).total_seconds() / 86400
        taken = [r["age_days"] for r in conn.execute("SELECT age_days FROM post_metrics WHERE deliverable_id=?", (d["id"],))]
        passed = [w for w in WINDOWS if age >= w]
        if passed and not any(t >= passed[-1] for t in taken):
            due.append(d["id"])
    return due


def renewal(conn: sqlite3.Connection, deal_id: int) -> dict:
    """Latest numbers per post, summed, turned into a verdict. Installs/codes come later from attribution."""
    d = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
    rows = conn.execute(
        "SELECT pm.* FROM post_metrics pm JOIN deliverables dl ON dl.id=pm.deliverable_id WHERE dl.deal_id=?"
        " AND pm.id=(SELECT MAX(id) FROM post_metrics WHERE deliverable_id=pm.deliverable_id)", (deal_id,)).fetchall()
    views = sum(r["views"] or 0 for r in rows)
    what = sum(r["what_app"] for r in rows)
    late = conn.execute("SELECT COUNT(*) n FROM deliverables WHERE deal_id=? AND status='late'", (deal_id,)).fetchone()["n"]
    cpm = d["price_usd"] / views * 1000 if views else None
    per_k = what / views * 1000 if views else 0
    if not rows:
        verdict = "wait"
    elif what >= 3 or per_k >= 0.2:
        verdict = "renew"
    elif views and cpm is not None and cpm < 5:
        verdict = "fix"       # attention without product interest: change the integration, not the creator
    else:
        verdict = "cut"
    return {"posts_measured": len(rows), "views": views, "what_app": what, "what_app_per_1k": round(per_k, 3),
            "cpm_usd": round(cpm, 2) if cpm else None, "late": late, "verdict": verdict}
