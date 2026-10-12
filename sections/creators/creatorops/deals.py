"""Deals: one agreement with one person. Terms in, brief + contract files out; signing schedules the work."""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta

from .db import DATA, SECTION, event, now
from .deliverables import schedule
from .outreach import _Blank, _fields
from .pipeline import advance


@dataclass
class Terms:
    track: str                      # ugc | influencer
    platform: str                   # tiktok | instagram
    price_usd: float
    videos: int = 4
    period_days: int = 14
    upfront_pct: int = 25
    rights: str = "Brand may repost the videos on its own accounts and use them in paid ads for 6 months."
    promo_code: str = ""
    match_terms: list[str] = field(default_factory=lambda: ["excerlock"])
    formats: str = "(captain picks)"


def _render(conn, deal_id: int, start: date) -> tuple[str, str]:
    d = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
    extra = json.loads(conn.execute("SELECT data FROM events WHERE deal_id=? AND kind='deal_proposed'",
                                    (deal_id,)).fetchone()["data"])
    dates = schedule(d["videos"], start, d["period_days"], seed=deal_id)
    f = _fields(conn, d["person_id"], deal_id) | {k: d[k] for k in d.keys()} | extra | {
        "start_date": start.isoformat(), "first_due": dates[0].isoformat(), "last_due": dates[-1].isoformat(),
        "upfront_usd": f"{d['price_usd'] * d['upfront_pct'] / 100:.2f}",
        "balance_usd": f"{d['price_usd'] * (100 - d['upfront_pct']) / 100:.2f}"}
    out = DATA / "deals" / str(deal_id)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for kind in ("brief", "contract"):
        p = out / f"{kind}.md"
        p.write_text((SECTION / "templates" / f"{kind}.md").read_text().format_map(_Blank(f)))
        paths.append(str(p))
    conn.execute("UPDATE deals SET brief_path=?, contract_path=? WHERE id=?", (*paths, deal_id))
    return paths[0], paths[1]


def propose(conn: sqlite3.Connection, person_id: int, terms: Terms, start: date | None = None) -> int:
    """Create a proposed deal and its brief + contract drafts. Waits in the approval inbox."""
    cur = conn.execute(
        "INSERT INTO deals(person_id, track, platform, price_usd, videos, period_days, upfront_pct, rights, promo_code,"
        " match_terms, created_at, portal_token) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (person_id, terms.track, terms.platform, terms.price_usd, terms.videos, terms.period_days, terms.upfront_pct,
         terms.rights, terms.promo_code, json.dumps(terms.match_terms), now(), secrets.token_urlsafe(18)))
    deal_id = cur.lastrowid
    event(conn, "deal_proposed", person_id, deal_id, formats=terms.formats)
    _render(conn, deal_id, start or date.today() + timedelta(days=3))
    conn.commit()
    return deal_id


def portal_url(conn: sqlite3.Connection, deal_id: int) -> str:
    token = conn.execute("SELECT portal_token FROM deals WHERE id=?", (deal_id,)).fetchone()["portal_token"]
    return os.environ.get("CREATORS_PUBLIC_URL", "http://127.0.0.1:8766").rstrip("/") + f"/c/{token}"


def approve(conn: sqlite3.Connection, deal_id: int) -> int:
    """Captain approved the terms: draft the offer message carrying the creator's portal link. Returns its id."""
    from .outreach import draft
    conn.execute("UPDATE deals SET status='approved' WHERE id=? AND status='proposed'", (deal_id,))
    event(conn, "deal_approved", deal_id=deal_id)
    d = conn.execute("SELECT person_id FROM deals WHERE id=?", (deal_id,)).fetchone()
    return draft(conn, d["person_id"], "offer", deal_id, {"portal_url": portal_url(conn, deal_id)})


def sign(conn: sqlite3.Connection, deal_id: int, start: date) -> list[int]:
    """Creator signed: schedule deliverables, owe the upfront payment, move the person to 'signed'."""
    d = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
    if d["status"] != "approved":
        raise ValueError(f"deal {deal_id} is '{d['status']}'; the captain approves terms before signing")
    _render(conn, deal_id, start)
    ids = [conn.execute("INSERT INTO deliverables(deal_id, due_date) VALUES (?,?)", (deal_id, day.isoformat())).lastrowid
           for day in schedule(d["videos"], start, d["period_days"], seed=deal_id)]
    conn.execute("UPDATE deals SET status='active', start_date=? WHERE id=?", (start.isoformat(), deal_id))
    if d["upfront_pct"]:
        conn.execute("INSERT INTO payments(deal_id, kind, amount_usd, created_at) VALUES (?,?,?,?)",
                     (deal_id, "upfront", round(d["price_usd"] * d["upfront_pct"] / 100, 2), now()))
    advance(conn, d["person_id"], "signed", deal=deal_id)
    event(conn, "deal_signed", d["person_id"], deal_id, start=start.isoformat())
    conn.commit()
    return ids


def close_if_done(conn: sqlite3.Connection, deal_id: int) -> bool:
    """All posted -> balance owed and deal done."""
    d = conn.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
    open_ = conn.execute("SELECT COUNT(*) n FROM deliverables WHERE deal_id=? AND post_url IS NULL", (deal_id,)).fetchone()["n"]
    if d["status"] != "active" or open_:
        return False
    balance = round(d["price_usd"] * (100 - d["upfront_pct"]) / 100, 2)
    if balance:
        conn.execute("INSERT INTO payments(deal_id, kind, amount_usd, created_at) VALUES (?,?,?,?)",
                     (deal_id, "balance", balance, now()))
    conn.execute("UPDATE deals SET status='done' WHERE id=?", (deal_id,))
    event(conn, "deal_done", d["person_id"], deal_id)
    conn.commit()
    return True


