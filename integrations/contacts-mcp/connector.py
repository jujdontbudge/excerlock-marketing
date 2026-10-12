"""Composition adapter: contacts owns identity/messages; creatorops owns workflow."""
import asyncio
import json
from html import escape

import phonenumbers

from creatorops import inbound
from creatorops.db import now

from client import open_client

ACTOR = "creator-crm connector"
OWNER = "owner (creator dashboard)"
SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts_mcp_people (
  creator_id INTEGER PRIMARY KEY REFERENCES people(id) ON DELETE CASCADE,
  person_id TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS contacts_mcp_drafts (
  id TEXT PRIMARY KEY, creator_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  document TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts_mcp_health (
  id INTEGER PRIMARY KEY CHECK(id=1), reachable INTEGER NOT NULL DEFAULT 0,
  last_attempt TEXT, last_sync TEXT, error TEXT
);
INSERT OR IGNORE INTO contacts_mcp_health(id) VALUES (1);
"""


def setup(conn):
    conn.executescript(SCHEMA)


def normalize(channel, value):
    value = value.strip().lower()
    if channel == "imessage" and "@" not in value:
        phone = phonenumbers.parse(value, "US")
        if not phonenumbers.is_valid_number(phone):
            raise ValueError("Invalid creator phone")
        return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
    return value.removeprefix("@") if channel in ("instagram", "tiktok") else value


async def push_handle(client, pid, cid, channel, value):
    normalized = normalize(channel, value)
    # add_handle is insert-only. Query both linked and unlinked identities first;
    # never move a handle belonging to another person automatically.
    candidates = (await client.call("find_person", query=normalized))["candidates"]
    unlinked = await client.call("list_unlinked")
    matches = [h for p in candidates for h in p["handles"]] + unlinked
    matches = {h["id"]: h for h in matches if h["channel"] == channel
               and h["account_id"] == "default" and h["value_normalized"] == normalized}
    if matches:
        for handle in matches.values():
            if handle["person_id"] not in (None, pid):
                raise ValueError("Handle belongs to another contacts person; review identity")
            if handle["person_id"] is None:
                await client.call("link_handle", handle_id=handle["id"], person_id=pid,
                                  actor=ACTOR, reason=f"Creator CRM record {cid}",
                                  exact_proof=f"Exact {channel} handle on creator-crm:{cid}")
        return
    await client.call("add_handle", person_id=pid, channel=channel, value=value,
                      actor=ACTOR, reason=f"Creator CRM record {cid}")


async def sync(conn, client):
    """Repeatable reconciliation. Commit remote IDs immediately to survive later failures."""
    setup(conn)
    conn.execute("UPDATE contacts_mcp_health SET last_attempt=?, reachable=0, error=NULL", (now(),))
    conn.commit()
    try:
        await client.call("sync_status")
        conn.execute("UPDATE contacts_mcp_health SET reachable=1")
        conn.commit()
        count = 0
        for creator in conn.execute("SELECT * FROM people ORDER BY id").fetchall():
            cid = creator["id"]
            link = {"system": "creator-crm", "external_id": str(cid)}
            match = await client.call("find_person", query=f"creator-crm:{cid}")
            exact = [p for p in match["candidates"] if link in p.get("links", [])]
            if len(exact) > 1:
                raise ValueError("Duplicate creator link")
            saved = conn.execute("SELECT person_id FROM contacts_mcp_people WHERE creator_id=?", (cid,)).fetchone()
            if exact:
                person = exact[0]
                if saved and saved["person_id"] != person["id"]:
                    raise ValueError("Creator identity changed; review mapping")
            elif saved:
                # Do not create a second identity when the remote link is missing.
                raise ValueError("Saved creator link missing; review mapping")
            else:
                person = await client.call("create_person", display_name=creator["name"] or f"Creator {cid}", links=[link])
            pid = person["id"]
            conn.execute("INSERT OR IGNORE INTO contacts_mcp_people VALUES (?,?)", (cid, pid))
            conn.commit()
            handles = [(h["platform"], h["username"]) for h in conn.execute(
                "SELECT platform, username FROM handles WHERE person_id=?", (cid,))]
            handles += [(channel, creator[field]) for channel, field in (("email", "email"), ("imessage", "phone"))
                        if creator[field]]
            for channel, value in handles:
                await push_handle(client, pid, cid, channel, value)
            # Histories are unpaginated in the current MCP contract. Unlike get_timeline's
            # capped window this cannot silently lose a burst of >1000 messages.
            detail = await client.call("get_person", person_id=pid)
            sender_handles = {h["id"]: h for h in detail["handles"] if h.get("person_id") == pid}
            for conversation in await client.call("list_conversations", person_id=pid):
                history = await client.call("get_conversation", conversation_id=conversation["id"])
                for message in history["messages"]:
                    sender = sender_handles.get(message["sender_handle_id"])
                    if message["direction"] != "in" or not sender:
                        continue
                    inbound.record(conn, sender["value_normalized"], message.get("subject") or "",
                                   message["text"], f"contacts-mcp:{message['id']}", person_id=cid)
            count += 1
        pending = await client.call("list_drafts")
        # Replace cache only once the complete fetch succeeds. It never enters the
        # CRM's messages table, where send_approved would dispatch through Resend.
        conn.execute("DELETE FROM contacts_mcp_drafts")
        for draft in pending:
            row = conn.execute("SELECT creator_id FROM contacts_mcp_people WHERE person_id=?",
                               (draft["person_id"],)).fetchone()
            if row:
                conn.execute("INSERT INTO contacts_mcp_drafts VALUES (?,?,?)",
                             (draft["id"], row["creator_id"], json.dumps(draft, sort_keys=True)))
        conn.execute("UPDATE contacts_mcp_health SET last_sync=?, error=NULL", (now(),))
        conn.commit()
        return {"creators": count, "drafts": conn.execute("SELECT COUNT(*) FROM contacts_mcp_drafts").fetchone()[0]}
    except Exception as exc:
        conn.rollback()
        conn.execute("UPDATE contacts_mcp_health SET error=?", (type(exc).__name__,))
        conn.commit()
        raise


async def decide(conn, client, draft_id, decision):
    if decision not in ("approve", "reject"):
        raise ValueError("Invalid draft decision")
    setup(conn)
    cached = conn.execute("SELECT d.*, p.do_not_contact FROM contacts_mcp_drafts d JOIN people p ON p.id=d.creator_id WHERE d.id=?",
                          (draft_id,)).fetchone()
    if not cached:
        raise ValueError("Draft is no longer in this inbox; sync again")
    if decision == "approve" and cached["do_not_contact"]:
        raise ValueError("Creator is on the do-not-contact list")
    current = next((d for d in await client.call("list_drafts") if d["id"] == draft_id), None)
    if current is None or json.dumps(current, sort_keys=True) != cached["document"]:
        raise ValueError("Draft changed or was decided elsewhere; sync and review again")
    if decision == "approve":
        result = await client.call("approve_draft", draft_id=draft_id, authorized_by=OWNER,
                                   reason="Owner approved in creator dashboard")
    else:
        result = await client.call("reject_draft", draft_id=draft_id, actor=OWNER,
                                   reason="Owner rejected in creator dashboard")
    conn.execute("DELETE FROM contacts_mcp_drafts WHERE id=?", (draft_id,))
    conn.commit()
    # Failed sends are terminal on contacts-mcp; surface the failure, never retry.
    if result.get("status") == "failed":
        raise ValueError("contacts-mcp send failed; reconcile there before any retry")
    return result


class InboxAdapter:
    """Injected dashboard extension. Reads cache; remote mutation only on owner POST."""
    def __init__(self, client_factory=open_client):
        self.client_factory = client_factory

    def render(self, conn):
        setup(conn)
        health = conn.execute("SELECT * FROM contacts_mcp_health").fetchone()
        out = [f"<div class=card>contacts-mcp: {'reachable' if health['reachable'] else 'unreachable / not checked'}"
               f" · last sync: {escape(health['last_sync'] or 'never')}"
               f" · last check: {escape(health['last_attempt'] or 'never')}"
               f" · {escape(health['error'] or '')}</div>"]
        rows = conn.execute("SELECT d.*, p.name, p.do_not_contact FROM contacts_mcp_drafts d JOIN people p ON p.id=d.creator_id").fetchall()
        out.append(f"<h2>✋ contacts-mcp messages ({len(rows)})</h2>")
        for row in rows:
            draft = json.loads(row["document"])
            payload = draft["payload"]
            if isinstance(payload, str):
                payload = json.loads(payload)
            out.append(f"<div class=card><a href='/person/{row['creator_id']}'>{escape(row['name'] or '')}</a>"
                       f" via {escape(draft['channel'])} · {escape(draft['handle_id'])}"
                       f"<pre>{escape(json.dumps(payload, ensure_ascii=False, indent=2))}</pre>"
                       f"<form method=post action='/extension/contacts-mcp'><input type=hidden name=id value='{escape(row['id'], quote=True)}'>"
                       + ("<b>do not contact</b>" if row["do_not_contact"] else "<button name=do value=approve>Approve & send</button>")
                       + "<button class=no name=do value=reject>Reject</button></form></div>")
        return "".join(out)

    def sync(self, conn):
        entered = False
        async def run():
            nonlocal entered
            async with self.client_factory() as client:
                entered = True
                return await sync(conn, client)
        try:
            return asyncio.run(run())
        except Exception as exc:
            if not entered:
                setup(conn)
                conn.execute("UPDATE contacts_mcp_health SET reachable=0, last_attempt=?, error=?",
                             (now(), type(exc).__name__))
                conn.commit()
            # Transport exceptions may include URLs or tokens; present only type.
            raise RuntimeError(f"contacts-mcp sync failed ({type(exc).__name__})") from None

    def action(self, conn, route, fields):
        if route != "/extension/contacts-mcp":
            return False
        async def run():
            async with self.client_factory() as client:
                return await decide(conn, client, fields["id"], fields["do"])
        try:
            asyncio.run(run())
        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError(f"contacts-mcp decision failed ({type(exc).__name__}); sync before retrying") from None
        return True
