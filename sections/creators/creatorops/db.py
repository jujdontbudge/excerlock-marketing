"""The one store every module shares: SQLite schema, connection and the event log."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SECTION = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("CREATORS_DATA", SECTION / "data"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS people (
  id INTEGER PRIMARY KEY,
  name TEXT, email TEXT, phone TEXT, notes TEXT DEFAULT '',
  stage TEXT NOT NULL DEFAULT 'new',
  do_not_contact INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS handles (
  id INTEGER PRIMARY KEY,
  person_id INTEGER NOT NULL REFERENCES people(id),
  platform TEXT NOT NULL, username TEXT NOT NULL COLLATE NOCASE,
  source TEXT NOT NULL, added_at TEXT NOT NULL,
  UNIQUE(platform, username)
);
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY,
  handle_id INTEGER NOT NULL REFERENCES handles(id),
  taken_at TEXT NOT NULL,
  followers INTEGER, posts_sampled INTEGER, median_views INTEGER,
  posts_last_30d INTEGER, bio TEXT,
  posts TEXT NOT NULL DEFAULT '[]', comments TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS scores (
  id INTEGER PRIMARY KEY,
  person_id INTEGER NOT NULL REFERENCES people(id),
  scored_at TEXT NOT NULL, score INTEGER NOT NULL, track TEXT NOT NULL,
  reasons TEXT NOT NULL, judgement TEXT
);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY,
  person_id INTEGER NOT NULL REFERENCES people(id),
  deal_id INTEGER REFERENCES deals(id),
  kind TEXT NOT NULL, channel TEXT NOT NULL, to_addr TEXT,
  subject TEXT, body TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  created_at TEXT NOT NULL, sent_at TEXT, provider_id TEXT, error TEXT
);
CREATE TABLE IF NOT EXISTS deals (
  id INTEGER PRIMARY KEY,
  person_id INTEGER NOT NULL REFERENCES people(id),
  track TEXT NOT NULL, platform TEXT NOT NULL,
  price_usd REAL NOT NULL, videos INTEGER NOT NULL, period_days INTEGER NOT NULL,
  upfront_pct INTEGER NOT NULL, rights TEXT NOT NULL, promo_code TEXT,
  match_terms TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'proposed',
  start_date TEXT, created_at TEXT NOT NULL,
  brief_path TEXT, contract_path TEXT
);
CREATE TABLE IF NOT EXISTS deliverables (
  id INTEGER PRIMARY KEY,
  deal_id INTEGER NOT NULL REFERENCES deals(id),
  due_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled',
  draft_url TEXT, post_url TEXT UNIQUE, posted_at TEXT
);
CREATE TABLE IF NOT EXISTS post_metrics (
  id INTEGER PRIMARY KEY,
  deliverable_id INTEGER NOT NULL REFERENCES deliverables(id),
  taken_at TEXT NOT NULL, age_days REAL,
  views INTEGER, likes INTEGER, comments INTEGER,
  what_app INTEGER NOT NULL, comment_sample TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY,
  deal_id INTEGER NOT NULL REFERENCES deals(id),
  kind TEXT NOT NULL, amount_usd REAL NOT NULL,
  status TEXT NOT NULL DEFAULT 'owed',
  created_at TEXT NOT NULL, paid_at TEXT
);
CREATE TABLE IF NOT EXISTS payout_details (
  person_id INTEGER PRIMARY KEY REFERENCES people(id),
  method TEXT NOT NULL, address TEXT NOT NULL, legal_name TEXT, country TEXT,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS signatures (
  id INTEGER PRIMARY KEY,
  deal_id INTEGER NOT NULL REFERENCES deals(id),
  legal_name TEXT NOT NULL, email TEXT NOT NULL, ip TEXT, user_agent TEXT,
  signed_at TEXT NOT NULL, contract_sha256 TEXT NOT NULL, contract_text TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY, at TEXT NOT NULL, kind TEXT NOT NULL,
  person_id INTEGER, deal_id INTEGER, data TEXT NOT NULL DEFAULT '{}'
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# columns added after the first release: (table, column, declaration)
MIGRATIONS = [
    ("deals", "portal_token", "TEXT"),
    ("payments", "provider", "TEXT"),
    ("payments", "provider_ref", "TEXT"),
    ("payments", "error", "TEXT"),
]


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    """Open (and create if needed) the store. ':memory:' gives a throwaway store for tests."""
    if path is None:
        DATA.mkdir(parents=True, exist_ok=True)
        path = DATA / "creators.db"
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    for table, col, decl in MIGRATIONS:
        if col not in {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")
    return conn


def event(conn: sqlite3.Connection, what: str, person_id=None, deal_id=None, **data) -> None:
    conn.execute("INSERT INTO events(at, kind, person_id, deal_id, data) VALUES (?,?,?,?,?)",
                 (now(), what, person_id, deal_id, json.dumps(data, default=str)))
