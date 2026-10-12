"""Inbound: creator replies to outreach@ arrive here (Namecheap forwards a copy to Resend Receiving, Resend
calls our webhook). A reply moves the creator to 'replied'; a plain no puts them on do-not-contact.

Webhooks are signed the Svix way: HMAC-SHA256 over "{svix-id}.{svix-timestamp}.{raw body}" with the
base64 secret after "whsec_", base64 output, header "v1,<sig>" (several allowed), 5-minute tolerance.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import sqlite3
import time

import requests

from .db import event, now
from .pipeline import advance, do_not_contact

SCHEMA = """CREATE TABLE IF NOT EXISTS replies (
  id INTEGER PRIMARY KEY, received_at TEXT NOT NULL, provider_id TEXT UNIQUE,
  from_addr TEXT NOT NULL, subject TEXT, body TEXT, person_id INTEGER REFERENCES people(id), handled INTEGER NOT NULL DEFAULT 0
);"""
NO = re.compile(r"^\s*(no|nope|no thanks|no thank you|not interested|unsubscribe|stop|remove me)\b[\s.!]*$", re.I | re.M)


def verify(secret: str, headers: dict, body: bytes, tolerance: int = 300, at: float | None = None) -> bool:
    try:
        msg_id, ts, sigs = headers["svix-id"], headers["svix-timestamp"], headers["svix-signature"]
        if abs((at or time.time()) - int(ts)) > tolerance:
            return False
        key = base64.b64decode(secret.removeprefix("whsec_"))
    except (KeyError, ValueError):
        return False
    expected = base64.b64encode(hmac.new(key, f"{msg_id}.{ts}.".encode() + body, hashlib.sha256).digest()).decode()
    return any(hmac.compare_digest(expected, s.split(",", 1)[1]) for s in sigs.split() if s.startswith("v1,"))


def _addr(value) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    m = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", value or "")
    return m.group(0).lower() if m else ""


def fetch_text(email_id: str) -> str:
    key = os.environ.get("RESEND_FULL_API_KEY")
    if not key:
        return ""
    r = requests.get(f"https://api.resend.com/emails/receiving/{email_id}", timeout=30,
                     headers={"Authorization": f"Bearer {key}"})
    return (r.json().get("text") or "") if r.status_code == 200 else ""


def strip_quoted(text: str) -> str:
    """The new part of a reply, without the quoted thread."""
    out = []
    for line in text.splitlines():
        if line.startswith(">") or re.match(r"^On .+wrote:\s*$", line) or line.strip() == "-----Original Message-----":
            break
        out.append(line)
    return "\n".join(out).strip()


def record(conn: sqlite3.Connection, from_addr: str, subject: str, body: str, provider_id: str | None = None) -> int | None:
    """Store one reply and act on it. Returns the person id it matched, if any."""
    conn.executescript(SCHEMA)
    if provider_id and conn.execute("SELECT 1 FROM replies WHERE provider_id=?", (provider_id,)).fetchone():
        return None
    p = conn.execute("SELECT * FROM people WHERE lower(email)=lower(?)", (from_addr,)).fetchone()
    new = strip_quoted(body)
    conn.execute("INSERT INTO replies(received_at, provider_id, from_addr, subject, body, person_id) VALUES (?,?,?,?,?,?)",
                 (now(), provider_id, from_addr, subject, new or body, p["id"] if p else None))
    if p:
        event(conn, "reply_received", p["id"], subject=subject)
        if new and NO.search(new.splitlines()[0]):
            do_not_contact(conn, p["id"], "replied no")
            if p["stage"] in ("contacted", "followed_up", "replied", "negotiating"):
                advance(conn, p["id"], "declined")
        elif p["stage"] in ("contacted", "followed_up"):
            advance(conn, p["id"], "replied")
    conn.commit()
    return p["id"] if p else None


def handle_webhook(conn: sqlite3.Connection, headers: dict, body: bytes, secret: str | None = None) -> str:
    secret = secret or os.environ.get("RESEND_WEBHOOK_SECRET", "")
    if not secret or not verify(secret, headers, body):
        raise PermissionError("bad webhook signature")
    payload = json.loads(body)
    if payload.get("type") != "email.received":
        return "ignored"
    d = payload.get("data", {})
    text = fetch_text(d.get("email_id", "")) if d.get("email_id") else ""
    record(conn, _addr(d.get("from")), d.get("subject", ""), text, d.get("email_id"))
    return "ok"
