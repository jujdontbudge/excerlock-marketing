"""Creator portal: the only public pages. One secret link per deal; the creator signs, adds payout details
and hands in draft and post links. No accounts, no third-party signing service.

Signing records what US e-signature law (E-SIGN Act, UETA) looks for: consent to sign electronically,
intent (typed legal name + checkbox), the exact text signed (stored, with its SHA-256), time, IP and
browser. A copy goes to the creator by email.
"""
from __future__ import annotations

import hashlib
from datetime import date
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import deals, deliverables, inbound
from .db import connect, event, now

CSS = """body{font:16px/1.5 system-ui;margin:0;background:#f6f6f4;color:#1e1e1e}main{max-width:720px;margin:auto;padding:20px}
.card{background:#fff;border:1px solid #ddd;border-radius:12px;padding:16px;margin:12px 0}pre{white-space:pre-wrap;font:14px/1.5 system-ui}
input,select{font:16px system-ui;padding:8px;border:1px solid #bbb;border-radius:8px;width:100%;box-sizing:border-box;margin:4px 0}
button{font:600 16px system-ui;border:0;border-radius:8px;padding:10px 16px;background:#1971c2;color:#fff;margin-top:8px}
label.chk{display:flex;gap:8px;align-items:flex-start}label.chk input{width:auto}.ok{color:#2b8a3e;font-weight:600}.mut{color:#777;font-size:14px}"""


def _page(title, body):
    return (f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>{escape(title)}</title>"
            f"<style>{CSS}</style><main>{body}</main>")


def _deal_for(conn, token):
    return conn.execute("SELECT d.*, p.name, p.email FROM deals d JOIN people p ON p.id=d.person_id WHERE d.portal_token=?",
                        (token,)).fetchone()


def view(conn, token: str) -> str:
    d = _deal_for(conn, token)
    if not d:
        return _page("Not found", "<h1>This link isn't valid.</h1>")
    contract = Path(d["contract_path"]).read_text()
    brief = Path(d["brief_path"]).read_text()
    sig = conn.execute("SELECT * FROM signatures WHERE deal_id=? ORDER BY id DESC LIMIT 1", (d["id"],)).fetchone()
    out = [f"<h1>Hey {escape((d['name'] or '').split(' ')[0])} 👋</h1>",
           f"<div class=card><pre>{escape(brief)}</pre></div>", f"<div class=card><pre>{escape(contract)}</pre>"]
    if sig:
        out.append(f"<p class=ok>Signed by {escape(sig['legal_name'])} on {sig['signed_at'][:10]}.</p></div>")
    elif d["status"] == "approved":
        out.append(f"""<form method=post action='/c/{token}/sign'>
<input name=legal_name placeholder='Your full legal name' required>
<input name=email type=email placeholder='Your email (we send your copy here)' value='{escape(d['email'] or '')}' required>
<label class=chk><input type=checkbox name=esign required> I agree to sign electronically and that my typed name is my signature.</label>
<label class=chk><input type=checkbox name=agree required> I have read and agree to this agreement.</label>
<button>Sign agreement</button></form></div>""")
    else:
        out.append("<p class=mut>This agreement isn't open for signing yet.</p></div>")
    pd = conn.execute("SELECT * FROM payout_details WHERE person_id=?", (d["person_id"],)).fetchone()
    out.append(f"""<div class=card><h2>How should we pay you?</h2>
{"<p class=ok>Saved: " + escape(pd['method']) + " · " + escape(pd['address']) + "</p>" if pd else ""}
<form method=post action='/c/{token}/payout'><select name=method><option value=paypal>PayPal</option><option value=wise>Wise</option></select>
<input name=address placeholder='PayPal or Wise email' required><input name=legal_name placeholder='Legal name on that account'>
<input name=country placeholder='Country' value='US'><button>Save payout details</button></form></div>""")
    rows = conn.execute("SELECT * FROM deliverables WHERE deal_id=? ORDER BY due_date", (d["id"],)).fetchall()
    if rows:
        out.append("<div class=card><h2>Your videos</h2>")
        for r in rows:
            state = ("posted ✅" if r["post_url"] else "draft approved, post it!" if r["status"] == "approved"
                     else "draft sent, we'll reply within 24h" if r["status"] == "draft_in" else f"due {r['due_date']}")
            out.append(f"<p><b>Video due {r['due_date']}</b> · {state}</p>")
            if not r["post_url"]:
                kind = "post" if r["status"] == "approved" else "draft"
                label = "Link to the live post" if kind == "post" else "Draft link (Google Drive, Dropbox, TikTok draft share...)"
                out.append(f"<form method=post action='/c/{token}/{kind}'><input type=hidden name=id value={r['id']}>"
                           f"<input name=url type=url placeholder='{label}' required><button>Send</button></form>")
        out.append("</div>")
    return _page("ExcerLock collab", "".join(out))


def sign(conn, token: str, legal_name: str, email: str, ip: str, user_agent: str, mailer=None) -> int:
    d = _deal_for(conn, token)
    if not d or d["status"] != "approved":
        raise ValueError("agreement not open for signing")
    if not legal_name.strip() or "@" not in email:
        raise ValueError("name and email are required")
    text = Path(d["contract_path"]).read_text()
    digest = hashlib.sha256(text.encode()).hexdigest()
    at = now()
    cur = conn.execute("INSERT INTO signatures(deal_id, legal_name, email, ip, user_agent, signed_at, contract_sha256, contract_text)"
                       " VALUES (?,?,?,?,?,?,?,?)", (d["id"], legal_name.strip(), email.strip().lower(), ip, user_agent, at, digest, text))
    conn.execute("UPDATE people SET email=COALESCE(email, ?) WHERE id=?", (email.strip().lower(), d["person_id"]))
    event(conn, "contract_signed", d["person_id"], d["id"], name=legal_name, ip=ip, sha256=digest)
    deals.sign(conn, d["id"], date.today())
    signed = deals_dir(d) / "contract-signed.md"
    signed.write_text(text + f"\n\n---\nSigned electronically by {legal_name.strip()} <{email.strip()}> at {at} from {ip}."
                      f"\nSHA-256 of the agreement text: {digest}\n")
    if mailer:
        try:
            mailer.send(email.strip(), "Your signed ExcerLock agreement", signed.read_text())
        except Exception as e:  # signing stands even if the copy bounces
            event(conn, "copy_email_failed", d["person_id"], d["id"], error=str(e)[:200])
    conn.commit()
    return cur.lastrowid


def deals_dir(d) -> Path:
    return Path(d["contract_path"]).parent


def save_payout(conn, token: str, method: str, address: str, legal_name: str, country: str) -> None:
    d = _deal_for(conn, token)
    if not d or method not in ("paypal", "wise") or "@" not in address:
        raise ValueError("pick PayPal or Wise and give the account email")
    conn.execute("INSERT INTO payout_details(person_id, method, address, legal_name, country, updated_at) VALUES (?,?,?,?,?,?)"
                 " ON CONFLICT(person_id) DO UPDATE SET method=excluded.method, address=excluded.address,"
                 " legal_name=excluded.legal_name, country=excluded.country, updated_at=excluded.updated_at",
                 (d["person_id"], method, address.strip().lower(), legal_name.strip(), country.strip(), now()))
    event(conn, "payout_details_saved", d["person_id"], d["id"], method=method)
    conn.commit()


def hand_in(conn, token: str, deliverable_id: int, kind: str, url: str) -> None:
    d = _deal_for(conn, token)
    row = conn.execute("SELECT * FROM deliverables WHERE id=? AND deal_id=?", (deliverable_id, d["id"] if d else -1)).fetchone()
    if not row or not url.startswith("http"):
        raise ValueError("unknown video or bad link")
    (deliverables.record_post if kind == "post" else deliverables.record_draft)(conn, deliverable_id, url)
    deals.close_if_done(conn, d["id"])


def make_handler(db_path, mailer_factory=None):
    class H(BaseHTTPRequestHandler):
        def _send(self, html, code=200):
            b = html.encode()
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("X-Robots-Tag", "noindex")
            self.end_headers()
            self.wfile.write(b)

        def _parts(self):
            parts = urlparse(self.path).path.strip("/").split("/")
            return parts if len(parts) >= 2 and parts[0] == "c" else None

        def do_GET(self):
            parts = self._parts()
            if not parts or len(parts) != 2:
                return self._send(_page("ExcerLock", "<h1>ExcerLock</h1>"), 404)
            conn = connect(db_path)
            try:
                self._send(view(conn, parts[1]))
            finally:
                conn.close()

        def do_POST(self):
            if urlparse(self.path).path == "/hooks/resend":
                body = self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 1_000_000))
                conn = connect(db_path)
                try:
                    res = inbound.handle_webhook(conn, {k.lower(): v for k, v in self.headers.items()}, body)
                    return self._send(res)
                except PermissionError:
                    return self._send("forbidden", 401)
                finally:
                    conn.close()
            parts = self._parts()
            if not parts or len(parts) != 3:
                return self._send("not found", 404)
            n = min(int(self.headers.get("Content-Length", 0)), 20000)
            f = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}
            token, action = parts[1], parts[2]
            ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
            conn = connect(db_path)
            try:
                if action == "sign":
                    if not (f.get("esign") and f.get("agree")):
                        raise ValueError("tick both boxes to sign")
                    sign(conn, token, f.get("legal_name", ""), f.get("email", ""), ip, self.headers.get("User-Agent", ""),
                         mailer_factory() if mailer_factory else None)
                elif action == "payout":
                    save_payout(conn, token, f.get("method", ""), f.get("address", ""), f.get("legal_name", ""), f.get("country", ""))
                elif action in ("draft", "post"):
                    hand_in(conn, token, int(f.get("id", 0)), action, f.get("url", ""))
                else:
                    raise ValueError("unknown action")
            except Exception as e:
                return self._send(_page("Problem", f"<div class=card>{escape(str(e))}</div><a href='/c/{escape(token)}'>back</a>"), 400)
            finally:
                conn.close()
            self.send_response(303)
            self.send_header("Location", f"/c/{token}")
            self.end_headers()

        def log_message(self, *a):
            pass
    return H


def serve(db_path=None, host="127.0.0.1", port=8766):
    from .channels import ResendEmail
    srv = ThreadingHTTPServer((host, port), make_handler(db_path, ResendEmail))
    print(f"creator portal on http://{host}:{port}")
    srv.serve_forever()
