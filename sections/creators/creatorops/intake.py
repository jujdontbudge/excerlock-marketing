"""Intake: any link, handle or email in, one person out. Merges duplicates instead of creating them."""
from __future__ import annotations

import sqlite3

from .db import event, now
from .platforms import parse_link


def create(conn: sqlite3.Connection, name: str, source: str = "intake") -> int:
    """Create a person without a public handle; external adapters own deduplication."""
    cur = conn.execute("INSERT INTO people(name, created_at) VALUES (?,?)", (name, now()))
    event(conn, "lead_added", cur.lastrowid, source=source)
    conn.commit()
    return cur.lastrowid


def _person_for(conn, platform, username):
    row = conn.execute("SELECT person_id FROM handles WHERE platform=? AND username=?", (platform, username)).fetchone()
    return row["person_id"] if row else None


def attach(conn: sqlite3.Connection, person_id: int, platform: str, username: str, source: str) -> bool:
    """Give a person another handle. Returns False if the handle already belongs to someone."""
    if _person_for(conn, platform, username) is not None:
        return False
    conn.execute("INSERT INTO handles(person_id, platform, username, source, added_at) VALUES (?,?,?,?,?)",
                 (person_id, platform, username, source, now()))
    event(conn, "handle_added", person_id, platform=platform, username=username, source=source)
    return True


def add(conn: sqlite3.Connection, text: str, source: str, platforms: dict | None = None,
        name: str | None = None, person_id: int | None = None) -> int:
    """Add one lead from any source. Returns the person id (existing one if already known).

    Post links are resolved to their author (needs `platforms`); an email alone needs `person_id`.
    """
    link = parse_link(text)
    if link["kind"] == "email":
        if person_id is None:
            hit = conn.execute("SELECT id FROM people WHERE email=?", (link["url"],)).fetchone()
            if hit:
                return hit["id"]
            raise ValueError("An email needs the person it belongs to (person_id)")
        conn.execute("UPDATE people SET email=? WHERE id=?", (link["url"], person_id))
        return person_id
    platform, username = link["platform"], link["username"]
    if link["kind"] == "post" and not username:
        if not platforms:
            raise ValueError("Resolving an Instagram post link needs the platform adapters")
        username = platforms[platform].post(link["url"]).username
    existing = _person_for(conn, platform, username)
    if existing is not None:
        event(conn, "seen_again", existing, source=source)
        conn.commit()
        return existing
    if person_id is None:
        cur = conn.execute("INSERT INTO people(name, created_at) VALUES (?,?)", (name or username, now()))
        person_id = cur.lastrowid
        event(conn, "lead_added", person_id, source=source, text=text)
    attach(conn, person_id, platform, username, source)
    conn.commit()
    return person_id


def merge(conn: sqlite3.Connection, keep: int, drop: int) -> None:
    """Fold person `drop` into `keep` (same human found twice)."""
    for table in ("handles", "scores", "messages", "deals"):
        conn.execute(f"UPDATE {table} SET person_id=? WHERE person_id=?", (keep, drop))
    d = conn.execute("SELECT email, phone FROM people WHERE id=?", (drop,)).fetchone()
    conn.execute("UPDATE people SET email=COALESCE(email, ?), phone=COALESCE(phone, ?) WHERE id=?",
                 (d["email"], d["phone"], keep))
    conn.execute("UPDATE events SET person_id=? WHERE person_id=?", (keep, drop))
    conn.execute("DELETE FROM people WHERE id=?", (drop,))
    event(conn, "merged", keep, dropped=drop)
    conn.commit()
