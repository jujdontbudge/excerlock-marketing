"""Outreach: draft messages from the editable templates, approve them, send the approved ones.

Message kinds: first, invite (to people who already wrote to us), followup, reminder (post day). Anything listed in CREATORS_AUTO_SEND
(comma-separated kinds, empty by default) skips the approval inbox.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from .db import SECTION, event, now
from .pipeline import advance

TEMPLATES = SECTION / "templates"
FOLLOWUP_AFTER_DAYS = 4
MAX_FOLLOWUPS = 2


def auto_send_kinds() -> set[str]:
    return {k.strip() for k in os.environ.get("CREATORS_AUTO_SEND", "").split(",") if k.strip()}


def render(kind: str, fields: dict) -> tuple[str, str]:
    """Template file -> (subject, body). First line 'Subject: ...' is the subject."""
    text = (TEMPLATES / f"{kind}.md").read_text().format_map(_Blank(fields))
    first, _, body = text.partition("\n")
    return first.removeprefix("Subject:").strip(), body.strip() + "\n"


class _Blank(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def _fields(conn, person_id: int, deal_id=None) -> dict:
    p = conn.execute("SELECT * FROM people WHERE id=?", (person_id,)).fetchone()
    h = conn.execute("SELECT platform, username FROM handles WHERE person_id=? ORDER BY id", (person_id,)).fetchone()
    f = {"name": (p["name"] or "").split(" ")[0] or "there", "handle": f"@{h['username']}" if h else "",
         "platform": {"tiktok": "TikTok", "instagram": "Instagram"}.get(h["platform"], "") if h else ""}
    if deal_id:
        d = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
        f |= {"promo_code": d["promo_code"] or "", "videos": d["videos"], "price_usd": f"{d['price_usd']:.0f}",
              "period_days": d["period_days"]}
    return f


def draft(conn: sqlite3.Connection, person_id: int, kind: str, deal_id: int | None = None,
          extra: dict | None = None) -> int:
    p = conn.execute("SELECT * FROM people WHERE id=?", (person_id,)).fetchone()
    if p["do_not_contact"]:
        raise ValueError(f"person {person_id} is on the do-not-contact list")
    subject, body = render(kind, _fields(conn, person_id, deal_id) | (extra or {}))
    channel, to = ("email", p["email"]) if p["email"] else ("dm", _fields(conn, person_id)["handle"])
    status = "approved" if kind in auto_send_kinds() else "draft"
    cur = conn.execute("INSERT INTO messages(person_id, deal_id, kind, channel, to_addr, subject, body, status, created_at)"
                       " VALUES (?,?,?,?,?,?,?,?,?)", (person_id, deal_id, kind, channel, to, subject, body, status, now()))
    event(conn, "message_drafted", person_id, deal_id, kind=kind, channel=channel, message_id=cur.lastrowid)
    conn.commit()
    return cur.lastrowid


def approve(conn: sqlite3.Connection, message_id: int, body: str | None = None) -> None:
    if body is not None:
        conn.execute("UPDATE messages SET body=? WHERE id=?", (body, message_id))
    conn.execute("UPDATE messages SET status='approved' WHERE id=? AND status='draft'", (message_id,))
    conn.commit()


def reject(conn: sqlite3.Connection, message_id: int) -> None:
    conn.execute("UPDATE messages SET status='rejected' WHERE id=? AND status='draft'", (message_id,))
    conn.commit()


def send_approved(conn: sqlite3.Connection, channels: dict) -> list[int]:
    """Send every approved message. DMs become 'ready' for a human to paste. Returns sent ids."""
    sent = []
    for m in conn.execute("SELECT * FROM messages WHERE status='approved'").fetchall():
        try:
            pid = channels[m["channel"]].send(m["to_addr"], m["subject"], m["body"])
        except Exception as e:
            conn.execute("UPDATE messages SET status='failed', error=? WHERE id=?", (str(e)[:300], m["id"]))
            continue
        status = "ready" if m["channel"] == "dm" else "sent"
        conn.execute("UPDATE messages SET status=?, sent_at=?, provider_id=? WHERE id=?", (status, now(), pid, m["id"]))
        event(conn, "message_" + status, m["person_id"], m["deal_id"], kind=m["kind"], message_id=m["id"])
        if status == "sent":
            _after_send(conn, m)
        sent.append(m["id"])
    conn.commit()
    return sent


def mark_dm_sent(conn: sqlite3.Connection, message_id: int) -> None:
    """A human pasted a 'ready' DM; count it as sent."""
    m = conn.execute("SELECT * FROM messages WHERE id=? AND status='ready'", (message_id,)).fetchone()
    if not m:
        raise ValueError(f"message {message_id} is not a ready DM")
    conn.execute("UPDATE messages SET status='sent', sent_at=? WHERE id=?", (now(), message_id))
    _after_send(conn, m)
    conn.commit()


def _after_send(conn, m) -> None:
    """A message actually reached the creator: move their stage."""
    stage = conn.execute("SELECT stage FROM people WHERE id=?", (m["person_id"],)).fetchone()["stage"]
    if m["kind"] in ("first", "invite") and stage == "shortlisted":
        advance(conn, m["person_id"], "contacted")
    elif m["kind"] == "followup" and stage in ("contacted", "followed_up"):
        advance(conn, m["person_id"], "followed_up")
