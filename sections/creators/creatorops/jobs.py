"""Jobs: the one function a scheduler calls. Everything it does is safe to repeat."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta, timezone

from . import deals, deliverables, outreach, payouts, performance, snapshot, vetting
from .db import event
from .pipeline import advance

STALE_DAYS = 7


def run(conn: sqlite3.Connection, platforms: dict, channels: dict, today: date | None = None,
        use_judge: bool = True) -> dict:
    today = today or date.today()
    log = {k: [] for k in ("refreshed", "scored", "followups", "no_reply", "reminders", "posts_found", "late",
                           "measured", "closed", "sent", "errors")}

    def attempt(what, fn):
        try:
            return fn()
        except Exception as e:
            log["errors"].append(f"{what}: {e}"[:300])

    # 1. new or stale leads: snapshot then score
    cutoff = (datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)).isoformat()
    for h in conn.execute(
            "SELECT h.id, h.person_id FROM handles h JOIN people p ON p.id=h.person_id"
            " WHERE p.stage IN ('new','scored','shortlisted','contacted','followed_up','replied','negotiating','signed')"
            " AND COALESCE((SELECT MAX(taken_at) FROM snapshots WHERE handle_id=h.id), '') < ?", (cutoff,)).fetchall():
        if attempt(f"refresh handle {h['id']}", lambda: snapshot.refresh(conn, h["id"], platforms)):
            log["refreshed"].append(h["id"])
    for p in conn.execute("SELECT id FROM people WHERE stage='new' AND id IN (SELECT h.person_id FROM handles h"
                          " JOIN snapshots s ON s.handle_id=h.id)").fetchall():
        if attempt(f"score {p['id']}", lambda: vetting.vet(conn, p["id"], use_judge)):
            log["scored"].append(p["id"])

    # 2. follow-ups and giving up
    for p in conn.execute("SELECT id, stage FROM people WHERE stage IN ('contacted','followed_up') AND do_not_contact=0"):
        last = conn.execute("SELECT MAX(sent_at) t FROM messages WHERE person_id=? AND status='sent'", (p["id"],)).fetchone()["t"]
        pending = conn.execute("SELECT 1 FROM messages WHERE person_id=? AND status IN ('draft','approved','ready')",
                               (p["id"],)).fetchone()
        if not last or pending or datetime.fromisoformat(last).date() > today - timedelta(days=outreach.FOLLOWUP_AFTER_DAYS):
            continue
        n = conn.execute("SELECT COUNT(*) n FROM messages WHERE person_id=? AND kind='followup' AND status='sent'",
                         (p["id"],)).fetchone()["n"]
        if n >= outreach.MAX_FOLLOWUPS:
            advance(conn, p["id"], "no_reply")
            log["no_reply"].append(p["id"])
        else:
            log["followups"].append(outreach.draft(conn, p["id"], "followup"))

    # 3. post-day reminders, finding live posts, lateness
    for dl in conn.execute("SELECT dl.id, dl.deal_id, de.person_id FROM deliverables dl JOIN deals de ON de.id=dl.deal_id"
                           " WHERE dl.due_date<=? AND dl.status='scheduled' AND de.status='active'", (today.isoformat(),)).fetchall():
        log["reminders"].append(outreach.draft(conn, dl["person_id"], "reminder", dl["deal_id"]))
        conn.execute("UPDATE deliverables SET status='reminded' WHERE id=?", (dl["id"],))
    for d in conn.execute("SELECT id FROM deals WHERE status='active'").fetchall():
        found = attempt(f"find posts deal {d['id']}", lambda: deliverables.find_posts(conn, d["id"], platforms))
        log["posts_found"] += found or []
    log["late"] = deliverables.mark_late(conn, today)

    # 4. measure posts at 1/3/7 days, close finished deals
    for dl_id in performance.due_measurements(conn):
        if attempt(f"measure {dl_id}", lambda: performance.measure(conn, dl_id, platforms)):
            log["measured"].append(dl_id)
    for d in conn.execute("SELECT id FROM deals WHERE status='active'").fetchall():
        if deals.close_if_done(conn, d["id"]):
            log["closed"].append(d["id"])

    # 5. payouts in flight
    log["payouts_settled"] = attempt("payout status", lambda: payouts.check_sending(conn)) or []

    # 6. send whatever is approved (auto-send kinds are approved at draft time)
    log["sent"] = outreach.send_approved(conn, channels)
    event(conn, "jobs_run", day=today.isoformat(), **{k: len(v) for k, v in log.items()})
    conn.commit()
    return log
