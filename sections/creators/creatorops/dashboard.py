"""Dashboard: a local web page over the store. Read views plus the approval inbox (every ✋ in the system)."""
from __future__ import annotations

import json
from datetime import date
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import deals, deliverables, intake, jobs, outreach, payouts, performance
from .db import connect
from .pipeline import STAGES, advance, do_not_contact

CSS = """body{font:14px system-ui;margin:0;background:#f6f6f4;color:#1e1e1e}nav{background:#1e1e1e;padding:10px 16px}
nav a{color:#fff;margin-right:16px;text-decoration:none;font-weight:600}main{padding:16px;max-width:1300px}
.card{background:#fff;border:1px solid #ddd;border-radius:10px;padding:12px;margin:8px 0}h2{margin:18px 0 6px}
.board{display:flex;gap:8px;overflow-x:auto}.col{min-width:170px;background:#ecebe6;border-radius:8px;padding:6px}
.col h3{font-size:12px;margin:4px;text-transform:uppercase;color:#555}.chip{background:#fff;border-radius:6px;padding:6px;margin:4px 0;font-size:13px}
button{border:0;border-radius:6px;padding:5px 10px;margin:2px;cursor:pointer;background:#1971c2;color:#fff}
button.no{background:#aaa}textarea{width:100%;height:110px}table{border-collapse:collapse;width:100%}
td,th{border-bottom:1px solid #eee;padding:4px 6px;text-align:left;font-size:13px}.mut{color:#777;font-size:12px}
.tag{background:#ffec99;border-radius:99px;padding:1px 7px;font-size:11px}form{display:inline}pre{white-space:pre-wrap}"""


def btn(action, label, cls="", **fields):
    hidden = "".join(f'<input type="hidden" name="{k}" value="{escape(str(v))}">' for k, v in fields.items())
    return f'<form method="post" action="{action}">{hidden}<button class="{cls}">{label}</button></form>'


def page(title, body):
    return (f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>{title}</title>"
            f"<style>{CSS}</style><nav><a href='/'>Inbox</a><a href='/board'>Pipeline</a><a href='/deals'>Deals</a></nav>"
            f"<main>{body}</main>")


def handle_str(conn, pid):
    return " ".join(f"{ {'tiktok': 'tt', 'instagram': 'ig'}[h['platform']]}:@{escape(h['username'])}" for h in
                    conn.execute("SELECT platform, username FROM handles WHERE person_id=?", (pid,)))


def inbox(conn, extensions=()):
    out = ["<h1>Approval inbox</h1>",
           "<div class=card><form method=post action='/add'><input name=text size=50 placeholder='TikTok/IG link or tt:handle'>"
           "<button>Add lead</button></form> " + btn("/jobs", "Run jobs now") + "</div>"]
    out.extend(extension.render(conn) for extension in extensions)
    rows = conn.execute("SELECT p.*, s.score, s.track, s.reasons, s.judgement FROM people p JOIN scores s ON s.person_id=p.id"
                        " WHERE p.stage='scored' AND s.id=(SELECT MAX(id) FROM scores WHERE person_id=p.id)"
                        " ORDER BY s.score DESC").fetchall()
    out.append(f"<h2>✋ Pick who to contact ({len(rows)})</h2>")
    for r in rows:
        j = json.loads(r["judgement"] or "{}")
        out.append(f"<div class=card><b><a href='/person/{r['id']}'>{escape(r['name'] or '')}</a></b> {handle_str(conn, r['id'])}"
                   f" <span class=tag>{r['score']}/100 · {r['track']}</span><div class=mut>{escape(j.get('reason', '') or '')}</div>"
                   + btn("/stage", "Shortlist", pid=r["id"], ev="shortlist") + btn("/stage", "Skip", "no", pid=r["id"], ev="skip")
                   + "</div>")
    short = conn.execute("SELECT * FROM people WHERE stage='shortlisted' AND do_not_contact=0 AND id NOT IN"
                         " (SELECT person_id FROM messages WHERE kind='first')").fetchall()
    if short:
        out.append(f"<h2>Shortlisted, no message yet ({len(short)})</h2>")
        for r in short:
            out.append(f"<div class=card>{escape(r['name'] or '')} {handle_str(conn, r['id'])} "
                       + btn("/draft", "Draft first message", pid=r["id"]) + "</div>")
    msgs = conn.execute("SELECT m.*, p.name FROM messages m JOIN people p ON p.id=m.person_id WHERE m.status IN ('draft','ready','failed')").fetchall()
    out.append(f"<h2>✋ Messages ({len(msgs)})</h2>")
    for m in msgs:
        head = f"<b>{m['kind']}</b> to {escape(m['name'] or '')} via {m['channel']} {escape(m['to_addr'] or '')} <span class=tag>{m['status']}</span>"
        if m["status"] == "draft":
            out.append(f"<div class=card>{head}<form method=post action='/msg'><input type=hidden name=id value={m['id']}>"
                       f"<textarea name=body>{escape(m['body'])}</textarea><button name=do value=approve>{'Approve & send' if m['channel'] == 'email' else 'Approve (then paste DM)'}</button>"
                       f"<button class=no name=do value=reject>Reject</button></form></div>")
        elif m["status"] == "ready":
            out.append(f"<div class=card>{head}<pre>{escape(m['body'])}</pre><div class=mut>Paste this DM in the app, then:</div>"
                       + btn("/msg", "Mark DM sent", id=m["id"], do="dm_sent") + "</div>")
        else:
            out.append(f"<div class=card>{head}<div class=mut>{escape(m['error'] or '')}</div></div>")
    conn.executescript(__import__("creatorops.inbound", fromlist=["SCHEMA"]).SCHEMA)
    reps = conn.execute("SELECT r.*, p.name FROM replies r LEFT JOIN people p ON p.id=r.person_id WHERE r.handled=0"
                        " ORDER BY r.id DESC").fetchall()
    if reps:
        out.append(f"<h2>Replies ({len(reps)})</h2>")
        for r in reps:
            who = f"<a href='/person/{r['person_id']}'>{escape(r['name'] or '')}</a>" if r["person_id"] else "unknown sender"
            out.append(f"<div class=card>{who} &lt;{escape(r['from_addr'])}&gt; · {escape(r['subject'] or '')}"
                       f"<pre>{escape((r['body'] or '')[:1500])}</pre>" + btn("/reply-done", "Done", "no", id=r["id"]) + "</div>")
    waiting = conn.execute("SELECT * FROM people WHERE stage IN ('contacted','followed_up','replied','negotiating')").fetchall()
    if waiting:
        out.append("<h2>Conversations</h2>")
        for r in waiting:
            evs = {"contacted": ["replied", "declined"], "followed_up": ["replied", "declined"],
                   "replied": ["negotiating", "declined"], "negotiating": ["declined"]}[r["stage"]]
            out.append(f"<div class=card><a href='/person/{r['id']}'>{escape(r['name'] or '')}</a> <span class=tag>{r['stage']}</span> "
                       + "".join(btn("/stage", e, pid=r["id"], ev=e) for e in evs)
                       + (f"<a href='/person/{r['id']}#deal'>propose deal →</a>" if r["stage"] in ("replied", "negotiating") else "")
                       + "</div>")
    ds = conn.execute("SELECT d.*, p.name FROM deals d JOIN people p ON p.id=d.person_id WHERE d.status IN ('proposed','approved')").fetchall()
    out.append(f"<h2>✋ Deals to approve / sign ({len(ds)})</h2>")
    for d in ds:
        action = (btn("/deal", "Approve terms", id=d["id"], do="approve") if d["status"] == "proposed" else
                  f"<form method=post action='/deal'><input type=hidden name=id value={d['id']}><input type=hidden name=do value=sign>"
                  f"<input type=date name=start value='{date.today().isoformat()}'><button>Creator signed</button></form>")
        out.append(f"<div class=card><a href='/deal/{d['id']}'>Deal {d['id']}</a> · {escape(d['name'] or '')} · {d['track']} ·"
                   f" ${d['price_usd']:.0f} for {d['videos']} videos / {d['period_days']} days <span class=tag>{d['status']}</span> {action}</div>")
    drafts = conn.execute("SELECT dl.*, p.name FROM deliverables dl JOIN deals d ON d.id=dl.deal_id JOIN people p ON p.id=d.person_id"
                          " WHERE dl.status='draft_in'").fetchall()
    out.append(f"<h2>✋ Video drafts to review ({len(drafts)})</h2>")
    for d in drafts:
        out.append(f"<div class=card>{escape(d['name'] or '')} · due {d['due_date']} · <a href='{escape(d['draft_url'])}'>draft</a> "
                   + btn("/deliv", "Approve draft", id=d["id"], do="approve") + "</div>")
    pays = conn.execute("SELECT py.*, p.name FROM payments py JOIN deals d ON d.id=py.deal_id JOIN people p ON p.id=d.person_id"
                        " WHERE py.status IN ('owed','approved','sending')").fetchall()
    out.append(f"<h2>✋ Payments ({len(pays)})</h2>")
    for p in pays:
        pd = conn.execute("SELECT method, address FROM payout_details WHERE person_id=(SELECT person_id FROM deals WHERE id=?)",
                          (p["deal_id"],)).fetchone()
        to = f"{pd['method']} {escape(pd['address'])}" if pd else "no payout details yet"
        b = (btn("/pay", f"Approve payout ({payouts.provider().name})", id=p["id"], do="approve") if p["status"] == "owed"
             else btn("/pay", "Mark paid", id=p["id"], do="paid") if p["status"] == "approved" else "")
        out.append(f"<div class=card>{escape(p['name'] or '')} · {p['kind']} ${p['amount_usd']:.2f} → {to} <span class=tag>{p['status']}</span> {b}"
                   f"<div class=mut>{escape(p['error'] or '')}</div></div>")
    return page("Inbox", "".join(out))


def board(conn):
    cols = []
    for st in STAGES:
        rows = conn.execute("SELECT p.*, (SELECT score FROM scores WHERE person_id=p.id ORDER BY id DESC LIMIT 1) score,"
                            " (SELECT MAX(s.median_views) FROM snapshots s JOIN handles h ON h.id=s.handle_id WHERE h.person_id=p.id) mv"
                            " FROM people p WHERE stage=? ORDER BY score DESC", (st,)).fetchall()
        chips = "".join(f"<div class=chip><a href='/person/{r['id']}'>{escape(r['name'] or '')}</a><div class=mut>"
                        f"{r['score'] if r['score'] is not None else '–'}/100 · median {r['mv'] or 0:,}</div></div>" for r in rows)
        cols.append(f"<div class=col><h3>{st} ({len(rows)})</h3>{chips}</div>")
    return page("Pipeline", f"<h1>Pipeline</h1><div class=board>{''.join(cols)}</div>")


def person(conn, pid):
    p = conn.execute("SELECT * FROM people WHERE id=?", (pid,)).fetchone()
    out = [f"<h1>{escape(p['name'] or '')} <span class=tag>{p['stage']}</span></h1>",
           f"<div class=card>email: {escape(p['email'] or '–')} · phone: {escape(p['phone'] or '–')}"
           + (" · <b>do not contact</b>" if p["do_not_contact"] else btn("/dnc", "Do not contact", "no", pid=pid)) + "</div>"]
    for s in conn.execute("SELECT s.*, h.platform, h.username FROM snapshots s JOIN handles h ON h.id=s.handle_id WHERE h.person_id=?"
                          " ORDER BY s.id DESC LIMIT 6", (pid,)):
        out.append(f"<div class=card><b>{s['platform']} @{escape(s['username'])}</b> · {s['taken_at'][:16]} · followers {s['followers'] or 0:,}"
                   f" · median views {s['median_views'] or 0:,} ({s['posts_sampled']} posts) · {s['posts_last_30d']} posts/30d"
                   f"<div class=mut>{escape(s['bio'] or '')}</div></div>")
    sc = conn.execute("SELECT * FROM scores WHERE person_id=? ORDER BY id DESC LIMIT 1", (pid,)).fetchone()
    if sc:
        out.append(f"<h2>Score {sc['score']}/100 · {sc['track']}</h2><div class=card><ul>"
                   + "".join(f"<li>{escape(r)}</li>" for r in json.loads(sc["reasons"]))
                   + f"</ul><pre class=mut>{escape(sc['judgement'] or '')}</pre></div>")
    out.append("<h2 id=deal>Propose a deal</h2><div class=card><form method=post action='/propose'>"
               f"<input type=hidden name=pid value={pid}>track <select name=track><option>ugc<option>influencer</select> "
               "platform <select name=platform><option>tiktok<option>instagram</select> price $<input name=price size=5> "
               "videos <input name=videos value=4 size=2> days <input name=days value=14 size=3> upfront % <input name=upfront value=25 size=3> "
               "code <input name=code size=8><button>Propose</button></form></div>")
    out.append("<h2>History</h2><div class=card><table>" + "".join(
        f"<tr><td class=mut>{e['at'][:16]}</td><td>{e['kind']}</td><td class=mut>{escape(e['data'][:160])}</td></tr>"
        for e in conn.execute("SELECT * FROM events WHERE person_id=? ORDER BY id DESC LIMIT 40", (pid,))) + "</table></div>")
    return page(p["name"] or "Person", "".join(out))


def deals_page(conn):
    rows = conn.execute("SELECT d.*, p.name FROM deals d JOIN people p ON p.id=d.person_id ORDER BY d.id DESC").fetchall()
    body = "".join(f"<tr><td><a href='/deal/{d['id']}'>{d['id']}</a></td><td>{escape(d['name'] or '')}</td><td>{d['track']}</td>"
                   f"<td>${d['price_usd']:.0f}</td><td>{d['status']}</td><td>{performance.renewal(conn, d['id'])['verdict']}</td></tr>" for d in rows)
    return page("Deals", f"<h1>Deals</h1><div class=card><table><tr><th>#<th>creator<th>track<th>price<th>status<th>verdict</tr>{body}</table></div>")


def deal_page(conn, did):
    d = conn.execute("SELECT d.*, p.name FROM deals d JOIN people p ON p.id=d.person_id WHERE d.id=?", (did,)).fetchone()
    r = performance.renewal(conn, did)
    sig = conn.execute("SELECT * FROM signatures WHERE deal_id=? ORDER BY id DESC LIMIT 1", (did,)).fetchone()
    out = [f"<h1>Deal {did} · {escape(d['name'] or '')} <span class=tag>{d['status']}</span></h1>",
           f"<div class=card>Creator portal: <a href='{deals.portal_url(conn, did)}'>{deals.portal_url(conn, did)}</a>"
           + (f" · signed by {escape(sig['legal_name'])} {sig['signed_at'][:16]} from {escape(sig['ip'] or '')}" if sig else " · not signed")
           + "</div>",
           f"<div class=card>verdict <b>{r['verdict']}</b> · views {r['views']:,} · \"what app\" comments {r['what_app']}"
           f" ({r['what_app_per_1k']}/1k views) · CPM ${r['cpm_usd'] or '–'} · late {r['late']}</div><h2>Deliverables</h2><div class=card><table>"]
    for dl in conn.execute("SELECT * FROM deliverables WHERE deal_id=? ORDER BY due_date", (did,)):
        m = conn.execute("SELECT * FROM post_metrics WHERE deliverable_id=? ORDER BY id DESC LIMIT 1", (dl["id"],)).fetchone()
        stats = f"{m['views'] or 0:,} views · {m['what_app']} what-app" if m else ""
        link = f"<a href='{escape(dl['post_url'])}'>post</a>" if dl["post_url"] else (
            f"<form method=post action='/deliv'><input type=hidden name=id value={dl['id']}><input name=url placeholder='draft or post URL'>"
            "<button name=do value=draft>Draft in</button><button name=do value=post>Posted</button></form>")
        out.append(f"<tr><td>{dl['due_date']}</td><td>{dl['status']}</td><td>{link}</td><td>{stats}</td></tr>")
    out.append("</table></div>")
    for kind in ("brief", "contract"):
        path = d[f"{kind}_path"]
        if path and Path(path).exists():
            out.append(f"<h2>{kind.title()}</h2><div class=card><pre>{escape(Path(path).read_text())}</pre></div>")
    return page(f"Deal {did}", "".join(out))


def make_handler(db_path, platforms_factory, channels_factory, extensions=()):
    class H(BaseHTTPRequestHandler):
        def _send(self, html, code=200):
            b = html.encode()
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            conn = connect(db_path)
            path = urlparse(self.path).path.strip("/").split("/")
            try:
                if path == [""]:
                    self._send(inbox(conn, extensions))
                elif path[0] == "board":
                    self._send(board(conn))
                elif path[0] == "person":
                    self._send(person(conn, int(path[1])))
                elif path[0] == "deals":
                    self._send(deals_page(conn))
                elif path[0] == "deal":
                    self._send(deal_page(conn, int(path[1])))
                else:
                    self._send("not found", 404)
            finally:
                conn.close()

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            f = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}
            conn = connect(db_path)
            route = urlparse(self.path).path
            back = self.headers.get("Referer", "/")
            try:
                if any(extension.action(conn, route, f) for extension in extensions):
                    pass
                elif route == "/add":
                    pid = intake.add(conn, f["text"], "dashboard", platforms_factory())
                    back = f"/person/{pid}"
                elif route == "/jobs":
                    for extension in extensions:
                        extension.sync(conn)
                    jobs.run(conn, platforms_factory(), channels_factory())
                elif route == "/stage":
                    advance(conn, int(f["pid"]), f["ev"])
                    if f["ev"] == "shortlist":
                        outreach.draft(conn, int(f["pid"]), "first")
                elif route == "/draft":
                    outreach.draft(conn, int(f["pid"]), "first")
                elif route == "/reply-done":
                    conn.execute("UPDATE replies SET handled=1 WHERE id=?", (int(f["id"]),))
                    conn.commit()
                elif route == "/dnc":
                    do_not_contact(conn, int(f["pid"]), "dashboard")
                elif route == "/msg":
                    if f["do"] == "approve":
                        outreach.approve(conn, int(f["id"]), f.get("body"))
                        outreach.send_approved(conn, channels_factory())
                    elif f["do"] == "reject":
                        outreach.reject(conn, int(f["id"]))
                    else:
                        outreach.mark_dm_sent(conn, int(f["id"]))
                elif route == "/propose":
                    did = deals.propose(conn, int(f["pid"]), deals.Terms(
                        f["track"], f["platform"], float(f["price"]), int(f["videos"]), int(f["days"]), int(f["upfront"]),
                        promo_code=f.get("code", "")))
                    back = f"/deal/{did}"
                elif route == "/deal":
                    if f["do"] == "approve":
                        deals.approve(conn, int(f["id"]))
                    else:
                        deals.sign(conn, int(f["id"]), date.fromisoformat(f["start"]))
                elif route == "/deliv":
                    i = int(f["id"])
                    {"draft": lambda: deliverables.record_draft(conn, i, f["url"]),
                     "post": lambda: deliverables.record_post(conn, i, f["url"]),
                     "approve": lambda: deliverables.approve_draft(conn, i)}[f["do"]]()
                elif route == "/pay":
                    (payouts.approve if f["do"] == "approve" else payouts.mark_paid)(conn, int(f["id"]))
            except Exception as e:
                self._send(page("Error", f"<div class=card><b>{escape(type(e).__name__)}</b>: {escape(str(e))}</div><a href='{escape(back)}'>back</a>"), 400)
                return
            finally:
                conn.close()
            self.send_response(303)
            self.send_header("Location", back)
            self.end_headers()

        def log_message(self, *a):
            pass
    return H


def serve(db_path=None, host="127.0.0.1", port=8765, platforms_factory=None, channels_factory=None, extensions=()):
    from .channels import default_channels
    from .platforms import default_platforms
    srv = ThreadingHTTPServer((host, port), make_handler(db_path, platforms_factory or default_platforms,
                                                         channels_factory or default_channels, extensions))
    print(f"dashboard on http://{host}:{port}")
    srv.serve_forever()
