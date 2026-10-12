"""Pipeline: the only place a person's stage changes. Illegal moves raise instead of corrupting the board."""
from __future__ import annotations

import sqlite3

from .db import event

# event -> {from stage: to stage}
TRANSITIONS = {
    "scored":      {"new": "scored", "scored": "scored"},
    "shortlist":   {"scored": "shortlisted"},           # captain picks who to contact
    "skip":        {"new": "skipped", "scored": "skipped"},
    "contacted":   {"shortlisted": "contacted"},
    "followed_up": {"contacted": "followed_up", "followed_up": "followed_up"},
    "replied":     {"contacted": "replied", "followed_up": "replied"},
    "negotiating": {"replied": "negotiating"},
    "signed":      {"replied": "signed", "negotiating": "signed", "signed": "signed"},
    "declined":    {s: "declined" for s in ("contacted", "followed_up", "replied", "negotiating")},
    "no_reply":    {"contacted": "no_reply", "followed_up": "no_reply"},
    "reopen":      {s: "scored" for s in ("skipped", "declined", "no_reply")},
}
STAGES = ["new", "scored", "shortlisted", "contacted", "followed_up", "replied", "negotiating",
          "signed", "declined", "no_reply", "skipped"]


class IllegalMove(ValueError):
    pass


def advance(conn: sqlite3.Connection, person_id: int, ev: str, **data) -> str:
    stage = conn.execute("SELECT stage FROM people WHERE id=?", (person_id,)).fetchone()["stage"]
    to = TRANSITIONS.get(ev, {}).get(stage)
    if to is None:
        raise IllegalMove(f"person {person_id}: can't '{ev}' from stage '{stage}'")
    conn.execute("UPDATE people SET stage=? WHERE id=?", (to, person_id))
    event(conn, f"stage:{ev}", person_id, frm=stage, to=to, **data)
    conn.commit()
    return to


def do_not_contact(conn: sqlite3.Connection, person_id: int, reason: str) -> None:
    conn.execute("UPDATE people SET do_not_contact=1 WHERE id=?", (person_id,))
    event(conn, "do_not_contact", person_id, reason=reason)
    conn.commit()
