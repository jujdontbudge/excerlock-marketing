"""Dashboard panel: everything the send gate is waiting on the captain for (composition layer: it reads the
inbox gate's journal and the creator store's names; neither section knows about the other).

Shown, newest first, last 14 days: held/draft/uncertain sends with their reasons, handle checks that didn't pass,
withdrawals that were held, chats that couldn't be matched. A sent message or a later decision clears nothing:
the panel shows the latest state per creator and message type.
"""
import html
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

JOURNAL = Path(os.environ.get('INBOX_GATE_DB') or Path.home() / 'Library/Application Support/ExcerLock/inbox-gate.db')
WAITING = ('held', 'draft', 'uncertain')
EVENT_KINDS = ('handle-check', 'withdraw-held', 'withdraw-uncertain', 'chat-ambiguous', 'needs-captain', 'flow-error', 'grant-error')


def rows(journal_path=JOURNAL, days=14, now=None):
    if not Path(journal_path).exists():
        return []
    since = ((now or datetime.now(timezone.utc)) - timedelta(days=days)).isoformat()
    j = sqlite3.connect(f'file:{journal_path}?mode=ro', uri=True)
    j.row_factory = sqlite3.Row
    out = []
    latest = j.execute("""SELECT d.* FROM decisions d JOIN (SELECT creator_key, message_type, MAX(id) id FROM decisions
                          WHERE at >= ? GROUP BY creator_key, message_type) l ON l.id = d.id ORDER BY d.id DESC""", (since,))
    for d in latest:
        if d['outcome'] in WAITING:
            out.append({'creator': d['creator_key'], 'at': d['at'], 'what': f"{d['message_type']}: {d['outcome']}",
                        'why': '; '.join(json.loads(d['reasons'])), 'text': d['text'] or ''})
    answered = {r['ref'] for r in j.execute("SELECT ref FROM events WHERE kind='answered'")}
    for e in j.execute(f"SELECT * FROM events WHERE at >= ? AND kind IN ({','.join('?' * len(EVENT_KINDS))}) ORDER BY id DESC",
                       (since, *EVENT_KINDS)):
        data = json.loads(e['data'])
        if e['kind'] == 'handle-check' and data.get('verdict') == 'pass':
            continue
        if e['kind'] == 'needs-captain':
            if e['ref'] in answered:
                continue
            out.append({'creator': e['creator_key'], 'at': e['at'], 'what': f"needs you: {data.get('from') or ''}",
                        'why': f"{data.get('text', '')} → {data.get('summary', '')}", 'text': data.get('suggested') or ''})
            continue
        out.append({'creator': e['creator_key'], 'at': e['at'], 'what': e['kind'] + (f" {data.get('verdict')}" if 'verdict' in data else ''),
                    'why': '; '.join(data.get('reasons') or []) or json.dumps(data)[:200], 'text': ''})
    return sorted(out, key=lambda r: r['at'], reverse=True)


class GatePanel:
    def __init__(self, journal_path=JOURNAL):
        self.journal_path = journal_path

    def names(self, conn):
        try:
            return {f"sideshift:{r[0]}": r[1] for r in conn.execute(
                'SELECT s.user_id, p.name FROM sideshift_people s JOIN people p ON p.id = s.creator_id')}
        except sqlite3.Error:
            return {}

    def render(self, conn):
        items = rows(self.journal_path)
        if not items:
            return '<h2>Needs you (messages)</h2><p>Nothing waiting.</p>'
        names = self.names(conn)
        cards = ''.join(
            f"<div class=card><b>{html.escape(names.get(r['creator'], r['creator']))}</b> · {html.escape(r['what'])} · "
            f"<small>{html.escape(r['at'][:16])}</small><p>{html.escape(r['why'])}</p>"
            + (f"<p><i>{html.escape(r['text'])}</i></p>" if r['text'] else '') + '</div>' for r in items[:60])
        return f'<h2>Needs you (messages)</h2>{cards}'

    def action(self, conn, route, fields):
        return False

    def sync(self, conn):
        return {}
