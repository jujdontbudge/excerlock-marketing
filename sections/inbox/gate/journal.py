"""Append-only record of every gate decision, and a per-chat lock shared by every producer.

SQLite at $INBOX_GATE_DB (default ~/Library/Application Support/ExcerLock/inbox-gate.db). Rows are never updated
or deleted, except reservations, which expire. An idempotency key that was ever 'dispatching', 'sent' or 'uncertain' is
spent forever: 'dispatching' is written and committed BEFORE the send leaves, so a crash mid-send can never lead to a
second send; an uncertain send is never retried automatically, a person reconciles it (review G03).
"""
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DEFAULT = Path.home() / 'Library/Application Support/ExcerLock/inbox-gate.db'
SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY, at TEXT NOT NULL, creator_key TEXT NOT NULL, channel TEXT NOT NULL,
  conversation_id TEXT NOT NULL, source_chat_id TEXT, message_type TEXT NOT NULL, occurrence TEXT,
  idempotency_key TEXT NOT NULL, outcome TEXT NOT NULL CHECK (outcome IN ('sent','held','draft','error','uncertain','dispatching')),
  reasons TEXT NOT NULL, text TEXT, fingerprint TEXT, outbox_id TEXT, trigger TEXT, captain_order TEXT);
CREATE INDEX IF NOT EXISTS decisions_creator ON decisions(creator_key, at);
CREATE INDEX IF NOT EXISTS decisions_key ON decisions(idempotency_key, outcome);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY, at TEXT NOT NULL, creator_key TEXT NOT NULL, kind TEXT NOT NULL, ref TEXT, data TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS events_creator ON events(creator_key, at);
CREATE UNIQUE INDEX IF NOT EXISTS events_once ON events(creator_key, kind, ref);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
CREATE TABLE IF NOT EXISTS approvals (
  id TEXT PRIMARY KEY, at TEXT NOT NULL, creator_key TEXT NOT NULL, message_type TEXT NOT NULL, occurrence TEXT,
  text_hash TEXT NOT NULL, captain_words TEXT NOT NULL, expires_at REAL NOT NULL, used_at TEXT, generation TEXT);
CREATE TABLE IF NOT EXISTS reservations (conversation_id TEXT PRIMARY KEY, holder TEXT NOT NULL, expires_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS seen_last (creator_key TEXT NOT NULL, rev TEXT NOT NULL, last_at TEXT NOT NULL,
  PRIMARY KEY (creator_key, rev));
CREATE TRIGGER IF NOT EXISTS decisions_no_update BEFORE UPDATE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS decisions_no_delete BEFORE DELETE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions are append-only'); END;
"""


DECISION_GUARDS = (
    "CREATE TRIGGER IF NOT EXISTS decisions_no_update BEFORE UPDATE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions are append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS decisions_no_delete BEFORE DELETE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions are append-only'); END",
)


class Busy(RuntimeError):
    pass


def snapshot(destination):
    """A complete, consistent copy of the real journal (including unflushed WAL writes) for dry runs."""
    destination = Path(destination)
    dst = sqlite3.connect(str(destination))
    source = Path(os.environ.get('INBOX_GATE_DB') or DEFAULT)   # the journal production opens (review N18)
    if source.exists():
        src = sqlite3.connect(f'file:{source}?mode=ro', uri=True)
        src.backup(dst)
        src.close()
    dst.close()
    return Journal(destination)


class Journal:
    def __init__(self, path=None):
        path = path or os.environ.get('INBOX_GATE_DB') or DEFAULT
        if str(path) != ':memory:':
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), timeout=30, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        if str(path) != ':memory:':
            self.conn.execute('PRAGMA journal_mode=WAL')
        self._migrate()
        self.conn.executescript(SCHEMA)

    def _migrate(self):
        """2026-10-15: 'dispatching' joined the allowed outcomes. Old databases are copied into the new shape once."""
        self.conn.execute('DROP INDEX IF EXISTS one_dispatch_per_key')   # retries after a definite no-send need a 2nd intent (N07)
        cols = [r['name'] for r in self.conn.execute("PRAGMA table_info(approvals)")]
        if cols and 'generation' not in cols:
            self.conn.execute('ALTER TABLE approvals ADD COLUMN generation TEXT')
        row = self.conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='decisions'").fetchone()
        if not row or 'dispatching' in row['sql']:
            return
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            self.conn.execute('DROP TRIGGER IF EXISTS decisions_no_update')
            self.conn.execute('DROP TRIGGER IF EXISTS decisions_no_delete')
            self.conn.execute('ALTER TABLE decisions RENAME TO decisions_v1')
            for stmt in SCHEMA.split(';'):
                if 'CREATE TABLE IF NOT EXISTS decisions' in stmt:
                    self.conn.execute(stmt)
            self.conn.execute('INSERT INTO decisions SELECT * FROM decisions_v1')
            self.conn.execute('DROP TABLE decisions_v1')
            for stmt in DECISION_GUARDS:   # guards back BEFORE commit: never a moment of editable history (N19)
                self.conn.execute(stmt)
            self.conn.execute('COMMIT')
        except BaseException:
            self.conn.execute('ROLLBACK')
            raise

    @contextmanager
    def reserve(self, conversation_id, holder, ttl=900):
        """One owner per chat. Holders must be unique per run; re-entry, even by the same holder, is refused (G05)."""
        now = time.time()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            row = self.conn.execute('SELECT holder, expires_at FROM reservations WHERE conversation_id=?', (conversation_id,)).fetchone()
            if row and row['expires_at'] > now:
                raise Busy(f'chat is being handled by {row["holder"]}')
            self.conn.execute('INSERT OR REPLACE INTO reservations VALUES (?,?,?)', (conversation_id, holder, now + ttl))
            self.conn.execute('COMMIT')
        except BaseException:
            self.conn.execute('ROLLBACK')
            raise
        try:
            yield
        finally:
            self.conn.execute('DELETE FROM reservations WHERE conversation_id=? AND holder=?', (conversation_id, holder))

    def owns(self, conversation_id, holder):
        """Still the unexpired owner? Checked right before a send, so a suspended worker can't send after expiry."""
        row = self.conn.execute('SELECT holder, expires_at FROM reservations WHERE conversation_id=?', (conversation_id,)).fetchone()
        return bool(row) and row['holder'] == holder and row['expires_at'] > time.time()

    def _attempts(self, key):
        """Every 'dispatching' row is an attempt; it is closed only by an 'error' whose reasons name it
        ('attempt:<id>'), i.e. a definite no-send for exactly that attempt (review N07, N08, R02).
        Returns (ever sent or uncertain, open attempt rows)."""
        rows = list(self.conn.execute("SELECT id, outcome, at, reasons FROM decisions WHERE idempotency_key=? ORDER BY id", (key,)))
        done = any(r['outcome'] in ('sent', 'uncertain') for r in rows)
        released = {ref for r in rows if r['outcome'] == 'error' for ref in json.loads(r['reasons'] or '[]')
                    if isinstance(ref, str) and ref.startswith('attempt:')}
        # Legacy (pre-attempt-id) shape: the old schema allowed ONE attempt per key, so an unreferenced error right
        # after the key's FIRST attempt closes exactly that attempt (S18); any later unreferenced error closes nothing (R02).
        attempts = [r for r in rows if r['outcome'] == 'dispatching']
        if attempts:
            first = attempts[0]
            after = [r for r in rows if r['id'] > first['id']]
            if after and after[0]['outcome'] == 'error' and not any(
                    isinstance(x, str) and x.startswith('attempt:') for x in json.loads(after[0]['reasons'] or '[]')):
                released.add(f"attempt:{first['id']}")
        open_rows = [r for r in rows if r['outcome'] == 'dispatching' and f"attempt:{r['id']}" not in released]
        return done, open_rows

    def spent(self, key):
        done, open_rows = self._attempts(key)
        return done or bool(open_rows)

    def begin_attempt(self, action, key, decision):
        """Record a dispatch intent and return ITS OWN row id: a unique token in the row finds it, whatever other
        connections write meanwhile (review S08), and the normal record path still runs (N01)."""
        import uuid
        token = f'intent:{uuid.uuid4().hex}'
        decision.reasons = list(decision.reasons) + [token]
        self.record(action, key, decision)
        row = self.conn.execute("SELECT id FROM decisions WHERE idempotency_key=? AND outcome='dispatching' AND reasons LIKE ?",
                                (key, f'%{token}%')).fetchone()
        return row['id'] if row else None

    def sole_attempt(self, key, attempt_id):
        """True when this attempt is the only live claim on the key: nothing sent or uncertain, no other open
        attempt (review R01: two connections can't both own one operation)."""
        done, open_rows = self._attempts(key)
        return not done and [r['id'] for r in open_rows] == [attempt_id]

    # captain approvals: created only by the captain's own command (send.py), one use, bound to recipient and exact text
    def approve(self, creator_key, message_type, occurrence, text_hash, captain_words, ttl=7200):
        import uuid
        aid = 'apr_' + uuid.uuid4().hex
        self.conn.execute('INSERT INTO approvals (id, at, creator_key, message_type, occurrence, text_hash, captain_words, expires_at) '
                          'VALUES (?,?,?,?,?,?,?,?)', (aid, datetime.now(timezone.utc).isoformat(), creator_key, message_type,
                                                       occurrence or '', text_hash, captain_words, time.time() + ttl))
        return aid

    def approval_valid(self, aid, creator_key, message_type, occurrence, text_hash, generation=None, pin=True):
        """Valid, unused, unexpired, and bound to this creator, type, occurrence and exact text. The first check pins
        it to the current invite round, so it can never carry over to a new one (review N06)."""
        row = self.conn.execute('SELECT * FROM approvals WHERE id=?', (aid,)).fetchone()
        if not (row and row['used_at'] is None and row['expires_at'] > time.time() and row['creator_key'] == creator_key
                and row['message_type'] == message_type and row['occurrence'] == (occurrence or '') and row['text_hash'] == text_hash):
            return False
        if not pin:
            return row['generation'] is None or generation is None or row['generation'] == generation
        if row['generation'] is None:
            self.conn.execute('UPDATE approvals SET generation=? WHERE id=? AND generation IS NULL', (generation or '', aid))
            return True
        return row['generation'] == (generation or '')

    def approval_expires(self, aid):
        """When the captain's approval runs out (epoch seconds), or None if there is no such approval (review DC01)."""
        row = self.conn.execute('SELECT expires_at FROM approvals WHERE id=?', (aid,)).fetchone()
        return row['expires_at'] if row else None

    def expire_approval(self, aid):
        """Seen expired: terminal and durable, so restoring it after a no-send can never revive it (review DE01)."""
        self.conn.execute('UPDATE approvals SET expires_at=0 WHERE id=?', (aid,))

    def restore_approval(self, aid):
        """A definitely-unsent attempt gives the captain's one-use approval back (review S07)."""
        self.conn.execute('UPDATE approvals SET used_at=NULL WHERE id=?', (aid,))

    def use_approval(self, aid):
        cur = self.conn.execute('UPDATE approvals SET used_at=? WHERE id=? AND used_at IS NULL AND expires_at > ?',
                                (datetime.now(timezone.utc).isoformat(), aid, time.time()))
        return cur.rowcount == 1

    def remember_request(self, creator_key, a):
        """Journal one of her handle requests the moment it is read ('request-seen', by request id, with requestedAt):
        signing evidence that no later failure, redaction or crash can erase (review AG02, AH02)."""
        import hashlib
        rid = str(a.get('requestId') or a.get('id') or hashlib.sha256(json.dumps(a, sort_keys=True, default=str).encode()).hexdigest()[:16])
        ref = f"{rid}@{a.get('requestedAt')}"   # every revision of its date is kept, not only the first (review BN01)
        if ref not in self.flags(creator_key, 'request-seen'):
            self.event(creator_key, 'request-seen', ref, {'requestedAt': a.get('requestedAt'), 'status': a.get('status'),
                                                          'platform': a.get('platform'), 'handle': a.get('handle')})

    def remember_contract(self, c):
        """An active contract read anywhere is signing evidence for it: journal 'maybe-signed' at once (AJ02)."""
        if (isinstance(c, dict) and c.get('id') and c.get('contractorId')
                and str(c.get('status') or '').lower() == 'active'):
            key = f"sideshift:{c['contractorId']}"
            if c['id'] not in self.flags(key, 'maybe-signed'):
                self.event(key, 'maybe-signed', c['id'], {'status': 'active', 'by': 'contract-list'})

    def remember_invites(self, creator_key, contract_id, links):
        """Journal each genuine invite for a contract as it is seen, so a later deletion can't roll its clock back."""
        known = self.flags(creator_key, 'invite-seen')
        from .checks import invite_row
        from .live import invite_contract_id
        for m in links:
            from .checks import content_time
            ct = content_time(m)
            ref = m.id if not m.edited_at else f'{m.id}#{contract_id}@{ct.isoformat() if ct else "unknown"}'   # edited-in ones too (BQ01)
            contract_id = contract_id or invite_contract_id(m.text)
            ours = m.direction == 'out' or invite_row(m)   # only invites WE sent (review BC02), garbled rows too (BX01)
            if ref not in known and ours and contract_id and ct is not None:
                self.event(creator_key, 'invite-seen', ref, {'contract': contract_id, 'id': m.id, 'at': ct.isoformat(), 'direction': 'out',
                                                              'edited': bool(m.edited_at), 'created': m.at})

    def remember_message(self, creator_key, m):
        """Every message revision as it is read ('msg-seen', by id and content), so a message that is later deleted,
        blanked, edited or removed upstream still counts as evidence (review AY01-AY04). Only ever adds vetoes."""
        from dataclasses import asdict
        from .live import revision_key
        ref = revision_key(m)   # attachments are part of a revision, not only the words (AZ01)
        now = datetime.now(timezone.utc).isoformat()   # the LATEST time each revision was read, not just the first (CI01)
        self.conn.execute('INSERT INTO seen_last (creator_key, rev, last_at) VALUES (?,?,?) '
                          'ON CONFLICT(creator_key, rev) DO UPDATE SET last_at=MAX(last_at, excluded.last_at)',
                          (creator_key, ref, now))
        last = self.conn.execute("SELECT ref FROM events WHERE creator_key=? AND kind='msg-seen' AND ref LIKE ? "
                                 "ORDER BY id DESC LIMIT 1", (creator_key, m.id.replace('%', r'\%') + '#%')).fetchone()
        if last and last['ref'].split('@seen', 1)[0] == ref:
            return   # the same revision as the last time this message was seen
        if ref in self.flags(creator_key, 'msg-seen'):
            ref = f'{ref}@seen{time.time_ns()}'   # it came BACK to an earlier form: a new observation (review CA01)
        data = {k: v for k, v in asdict(m).items() if k != 'vanished'}
        self.event(creator_key, 'msg-seen', ref, data)

    def answer(self, creator_key, token, data):
        """Record that a message (by its answer token) was answered. Every answer is its own fact, so the captain can
        answer the same words again after they changed and came back (review CA01)."""
        ref = token if token not in self.flags(creator_key, 'answered') else f'{token}@{time.time_ns()}'
        return self.event(creator_key, 'answered', ref, {**data, 'token': token})

    def seen_mark(self, creator_key):
        """The latest message observation for a creator: an answer given for what was seen up to here (review CB01)."""
        row = self.conn.execute("SELECT MAX(id) AS m FROM events WHERE creator_key=? AND kind='msg-seen'", (creator_key,)).fetchone()
        return row['m'] or 0

    def answered(self, creator_key):
        """Answer tokens that still hold: answered, and not seen in any other form since (review CA01)."""
        from .checks import valid_answers
        return valid_answers(self.events(creator_key))

    def remember_notice(self, creator_key, m):
        """Journal a message from her chat the moment it is read: every revision ('msg-seen'), plus the specific facts
        below. It outlives a later redaction, a crash mid-read or another worker's decision (review AI01, AY01)."""
        self.remember_message(creator_key, m)
        from .checks import gap_exempt
        if ((m.direction == 'out' and not gap_exempt(m))   # every delivery of ours except exact system notices (CE01, CK02)
                or (m.author == 'us-unreadable' and m.text.strip())):
            # our delivery (readable, or our unreadable row with words): time and words, spacing/duplicates (AX02, BV03)
            from .checks import text_digest
            ref = m.id if not m.edited_at else f'{m.id}~{m.edited_at}'   # each edited revision too (review BT02)
            if ref in self.flags(creator_key, 'out-seen'):
                ref = f'{ref}#{text_digest(m.text)}'   # changed words under a reused clock are their own fact (CG01)
            if m.text.strip() and ref not in self.flags(creator_key, 'out-seen'):
                self.event(creator_key, 'out-seen', ref, {'id': m.id, 'at': m.at, 'edited_at': m.edited_at,
                                                          'digest': text_digest(m.text)})
            if m.kind == 'text':
                return   # other kinds (a notice- or invite-shaped captain row, an unreadable row) are checked below too
        from .checks import invite_row
        if invite_row(m) and m.kind == 'unreadable':
            self.remember_invites(creator_key, None, [m])
        if m.kind == 'invite_link':   # every invite row WE sent, as read: it can only move the clock later (AV01)
            from .live import invite_contract_id
            cid = invite_contract_id(m.text)
            from .checks import content_time
            ct = content_time(m)
            ref = m.id if not m.edited_at else f'{m.id}#{cid}@{ct.isoformat() if ct else "unknown"}'   # edited-in ones too (BQ01)
            if m.direction == 'out' and cid and ct is not None and ref not in self.flags(creator_key, 'invite-seen'):   # (BC02)
                self.event(creator_key, 'invite-seen', ref, {'contract': cid, 'id': m.id, 'at': ct.isoformat(), 'direction': 'out',
                                                              'edited': bool(m.edited_at), 'created': m.at})
            return
        from .checks import signing_notice
        signing = signing_notice(m)   # garbled other fields don't undo a notice (review BW02)
        ref = f'{m.id}@{m.at}' + (f'~{m.edited_at}' if m.edited_at else '')   # every dated revision kept (BO01, BR01)
        if signing and ref not in self.flags(creator_key, 'notice-seen'):   # only real signing notices are signing evidence
            self.event(creator_key, 'notice-seen', ref,   # dated by its content time; unknown edit -> no date (counts)
                       {'at': None if m.edited_at == 'unknown' else (m.edited_at or m.at), 'kind': m.kind})

    def delivered_texts(self, creator_key):
        """What we told her that may have reached her: confirmed or uncertain sends and attempts still open, each with
        its time and words. An attempt closed by a definite no-send told her nothing (review DJ03)."""
        out = []
        keys = [r['idempotency_key'] for r in self.conn.execute(
            'SELECT DISTINCT idempotency_key FROM decisions WHERE creator_key=?', (creator_key,))]
        for key in keys:
            _, open_rows = self._attempts(key)
            rows = list(self.conn.execute("SELECT id, at, text, outcome FROM decisions WHERE idempotency_key=? ORDER BY id", (key,)))
            open_ids = {r['id'] for r in open_rows}
            out += [{'at': r['at'], 'text': r['text']} for r in rows
                    if r['outcome'] in ('sent', 'uncertain') or r['id'] in open_ids]
        return out

    def outcomes(self, key):
        """Every outcome recorded for one idempotency key, oldest first."""
        return [r['outcome'] for r in self.conn.execute('SELECT outcome FROM decisions WHERE idempotency_key=? ORDER BY id', (key,))]

    def delivery(self, key):
        """'sent' (confirmed), 'unclear' (uncertain, or an attempt still open) or 'none' (never tried, or every attempt
        definitely did not send, so it may be tried again). Built on the same attempt resolution as spent() (AR01)."""
        if self.conn.execute("SELECT 1 FROM decisions WHERE idempotency_key=? AND outcome='sent' LIMIT 1", (key,)).fetchone():
            return 'sent'
        done, open_rows = self._attempts(key)
        return 'unclear' if done or open_rows else 'none'

    def premium_owners(self, email):
        """Every creator that ever acknowledged, claimed or received Premium for this email, legacy receipts too (V03),
        as (creator, kind) pairs."""
        email = email.lower()
        out = {(json.loads(r['data']).get('by'), r['kind']) for r in self.conn.execute(
            "SELECT kind, data FROM events WHERE creator_key=? AND kind IN ('premium-acknowledged','grant-intent')",
            (f'premium:{email}',))}
        out |= {(r['creator_key'], 'premium-granted') for r in self.conn.execute(
            "SELECT creator_key FROM events WHERE kind='premium-granted' AND lower(ref)=?", (email,))}
        return {(by, kind) for by, kind in out if by}

    def creator_premium_emails(self, creator_key):
        """Every email this creator ever acknowledged, claimed or received Premium for, legacy receipts too: one
        Premium account per creator; a different address after any of them is a transfer the captain decides (CX01)."""
        out = {r['ref'].lower() for r in self.conn.execute(
            "SELECT ref FROM events WHERE creator_key=? AND kind='premium-granted'", (creator_key,)) if r['ref']}
        for r in self.conn.execute("SELECT ref, data FROM events WHERE creator_key LIKE 'premium:%' "
                                   "AND kind IN ('premium-acknowledged','grant-intent')"):
            if json.loads(r['data']).get('by') == creator_key and r['ref']:
                out.add(r['ref'].lower())
        return out

    def settle_premium(self, creator_key, email, active, fresh=lambda: True):
        """After the entitlement check, in ONE write transaction (so two creators on two connections can't both pass):
        re-read every owner of this email and acknowledge (active) or claim it for a grant (not active). Returns
        'ok', 'other' (belongs to another creator), 'other-email' (she already has or claimed Premium on another address), 'revoked' (was ours, not active now), 'unresolved' (an earlier
        grant attempt never confirmed) or 'stale' (fresh() says the caller's checks were too old by the time the write
        lock was ours; nothing written). Review X02, Y01."""
        email = email.lower()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            owners = self.premium_owners(email)
            if not fresh():
                result = 'stale'
            elif {by for by, _ in owners} - {creator_key}:
                result = 'other'
            elif self.creator_premium_emails(creator_key) - {email}:   # she already has another one (CX01)
                result = 'other-email'
            elif active:
                self.event(f'premium:{email}', 'premium-acknowledged', email, {'email': email, 'by': creator_key})
                result = 'ok'
            elif any(kind != 'grant-intent' for _, kind in owners):
                result = 'revoked'
            elif owners:
                result = 'unresolved'
            else:
                result = 'ok' if self.claim_grant(creator_key, email) else 'unresolved'
            self.conn.execute('COMMIT')
        except BaseException:
            self.conn.execute('ROLLBACK')
            raise
        return result

    def claim_grant(self, creator_key, email):
        """One owner per Premium ACCOUNT (the email), across all creators, durably (review N26, S19)."""
        return self.event(f'premium:{email.lower()}', 'grant-intent', email.lower(), {'email': email.lower(), 'by': creator_key})

    def premium_granted(self, creator_key, email):
        """A confirmed `excerlock-access grant` for exactly this email (event 'premium-granted', see grant.py)."""
        if not email:
            return False
        for r in self.conn.execute("SELECT data FROM events WHERE creator_key=? AND kind='premium-granted'", (creator_key,)):
            data = json.loads(r['data'])
            if data.get('email', '').lower() == email.lower() and str(data.get('result', '')).startswith('GRANTED'):
                return True
        return False

    def recent_sends(self, conversation_id, creator_key, exclude_attempt=None):
        """Times of our sends to this chat or creator the journal knows (even if SideShift doesn't show them yet):
        sent, uncertain, and attempts still open. A definitely-unsent attempt is not a send (review N09, R02)."""
        from datetime import datetime as _dt
        out = []
        keys = {r['idempotency_key'] for r in self.conn.execute(
            "SELECT DISTINCT idempotency_key FROM decisions WHERE conversation_id != 'pre-gate' AND (conversation_id=? OR creator_key=?)",
            (conversation_id, creator_key))}
        for key in keys:
            out += [_dt.fromisoformat(r['at']) for r in self.conn.execute(
                "SELECT at FROM decisions WHERE idempotency_key=? AND outcome IN ('sent','uncertain')", (key,))]
            out += [_dt.fromisoformat(r['at']) for r in self._attempts(key)[1] if r['id'] != exclude_attempt]
        return out

    def flags(self, creator_key, kind):
        """Refs of events of one kind for a creator (e.g. 'answered' message ids, 'attachment-reviewed' ids)."""
        return {r['ref'] for r in self.conn.execute('SELECT ref FROM events WHERE creator_key=? AND kind=?', (creator_key, kind))}

    def link_person(self, person_id, source_key):
        """Remember that a source account was seen linked to a canonical person, durably (review CP01)."""
        if person_id and source_key and source_key not in self.flags(f'person:{person_id}', 'linked-account'):
            self.event(f'person:{person_id}', 'linked-account', source_key, {})

    def component_accounts(self, source_key):
        """Every account ever connected to this one through any person record (linked-account facts), itself included:
        the same human, whichever account or person id contacts shows today (review CQ01, CR01)."""
        links = [(r['creator_key'][len('person:'):], r['ref']) for r in self.conn.execute(
            "SELECT creator_key, ref FROM events WHERE kind='linked-account' AND creator_key LIKE 'person:%'")]
        people, accounts, todo = set(), {source_key}, [('a', source_key)]
        while todo:
            kind, node = todo.pop()
            for pid, acct in links:
                if kind == 'a' and acct == node and pid not in people:
                    people.add(pid); todo.append(('p', pid))
                elif kind == 'p' and pid == node and acct not in accounts:
                    accounts.add(acct); todo.append(('a', acct))
        return accounts

    def component_deliveries(self, source_key):
        """Our deliveries observed on the OTHER accounts of this human (out-seen facts and our message revisions),
        manual ones included: (account, words) pairs (review CS01)."""
        out = []
        for acct in self.component_accounts(source_key) - {source_key}:
            for e in self.events(acct):
                try:
                    d = json.loads(e['data'])
                except (ValueError, TypeError):
                    continue
                if e['kind'] == 'msg-seen' and (d.get('direction') == 'out' or d.get('author') == 'us-unreadable'):
                    out.append((acct, d.get('text') or '', d.get('id')))
                elif e['kind'] == 'out-seen':
                    out.append((acct, None, d.get('digest')))
        return out

    def person_restricted(self, person_id):
        """A person is do-not-contact while ANY account ever connected to them is, through any person record ever seen
        (accounts and person records form one connected group: a merge or move in contacts never drops a restriction;
        only the captain turning that account's do-not-contact off does) (review CP01, CQ01)."""
        if not person_id:
            return False
        links = [(r['creator_key'][len('person:'):], r['ref']) for r in self.conn.execute(
            "SELECT creator_key, ref FROM events WHERE kind='linked-account' AND creator_key LIKE 'person:%'")]
        people, accounts, todo = {person_id}, set(), [('p', person_id)]
        while todo:
            kind, node = todo.pop()
            for pid, acct in links:
                if kind == 'p' and pid == node and acct not in accounts:
                    accounts.add(acct); todo.append(('a', acct))
                elif kind == 'a' and acct == node and pid not in people:
                    people.add(pid); todo.append(('p', pid))
        return any(self.restricted(a) for a in accounts)

    def restricted(self, creator_key):
        """Do-not-contact from either source; in each the latest event wins (enabled true/false): the captain's own
        ('do-not-contact', record.py dnc) and a contacts tag ever seen on her person ('remote-dnc', review CY01).
        A tag seen once sticks to the account even if contacts later moves it to an untagged person; only the
        captain's `record.py dnc <name> off` releases it."""
        def on(kind):
            row = self.conn.execute("SELECT data FROM events WHERE creator_key=? AND kind=? ORDER BY id DESC LIMIT 1",
                                    (creator_key, kind)).fetchone()
            return bool(row) and json.loads(row['data']).get('enabled', True) is not False
        return on('do-not-contact') or on('remote-dnc')

    def remember_remote_dnc(self, person_id, accounts):
        """A contacts do-not-contact tag was read on this person: keep it on every account linked to them (CY01)."""
        for key in accounts:
            if key and not self.restricted(key):
                self.event(key, 'remote-dnc', f'{datetime.now(timezone.utc).isoformat()}@{person_id}',
                           {'enabled': True, 'person_id': person_id})

    def record(self, action, key, decision, text=''):
        return self._insert(action, key, decision, text)

    def _insert(self, action, key, decision, text=''):
        cur = self.conn.execute(
            'INSERT INTO decisions (at, creator_key, channel, conversation_id, source_chat_id, message_type, occurrence, '
            'idempotency_key, outcome, reasons, text, fingerprint, outbox_id, trigger, captain_order) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (datetime.now(timezone.utc).isoformat(), action.creator_key, action.channel, action.conversation_id,
             action.source_chat_id, action.message_type, action.occurrence, key, decision.outcome,
             json.dumps(decision.reasons, ensure_ascii=False), text or decision.text, decision.fingerprint,
             decision.outbox_id, action.trigger, action.captain_order))
        return cur.lastrowid

    def event(self, creator_key, kind, ref, data):
        """Record a fact about a creator once (per creator, kind, ref). Returns True if it was new."""
        cur = self.conn.execute('INSERT OR IGNORE INTO events (at, creator_key, kind, ref, data) VALUES (?,?,?,?,?)',
                                (datetime.now(timezone.utc).isoformat(), creator_key, kind, ref,
                                 json.dumps(data, ensure_ascii=False, default=str)))
        return cur.rowcount == 1

    def events(self, creator_key):
        """Every event for a creator in order, plus one 'msg-last' row per message revision giving the latest time
        it was read (consumers that don't know the kind ignore it) (review CI01)."""
        rows = [dict(r) for r in self.conn.execute('SELECT * FROM events WHERE creator_key=? ORDER BY id', (creator_key,))]
        rows += [{'id': 0, 'at': r['last_at'], 'creator_key': creator_key, 'kind': 'msg-last', 'ref': r['rev'],
                  'data': json.dumps({'at': r['last_at']})}
                 for r in self.conn.execute('SELECT rev, last_at FROM seen_last WHERE creator_key=?', (creator_key,))]
        return rows

    def history(self, creator_key):
        return [dict(r) for r in self.conn.execute('SELECT * FROM decisions WHERE creator_key=? ORDER BY id', (creator_key,))]
