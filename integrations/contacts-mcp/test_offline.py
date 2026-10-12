"""Offline connector contract tests: fake MCP tools, real CRM/store/dashboard."""
import asyncio
import copy
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from contextlib import asynccontextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sections/creators"))
from creatorops import dashboard, inbound, intake
from creatorops.db import connect
from client import Client, ToolError, open_client
from connector import InboxAdapter, OWNER, decide, normalize, sync


class FakeClient:
    def __init__(self):
        self.people = {}
        self.handles = []
        self.drafts = []
        self.messages = []
        self.calls = []
        self.fail = None

    async def call(self, tool, **args):
        self.calls.append((tool, args))
        if tool == self.fail:
            raise RuntimeError("private server detail")
        if tool == "sync_status":
            return []
        if tool == "find_person":
            # Include all candidates, as real fuzzy resolver can do. Adapter must
            # select by actual link/handle equality, never by name/ranking alone.
            return {"candidates": [dict(p, handles=[h for h in self.handles if h["person_id"] == p["id"]])
                                   for p in self.people.values()]}
        if tool == "create_person":
            pid = f"p_{len(self.people) + 1}"
            p = dict(args, id=pid)
            self.people[pid] = p
            return p
        if tool == "get_person":
            p = self.people[args["person_id"]]
            return dict(p, handles=[h for h in self.handles if h["person_id"] == p["id"]])
        if tool == "list_unlinked":
            return [h for h in self.handles if h["person_id"] is None]
        if tool == "add_handle":
            n = normalize(args["channel"], args["value"])
            if any(h["channel"] == args["channel"] and h["value_normalized"] == n for h in self.handles):
                raise ValueError("UNIQUE handle")
            h = dict(args, id=f"h_{len(self.handles) + 1}", account_id="default", value_normalized=n)
            self.handles.append(h)
            return h
        if tool == "link_handle":
            h = next(h for h in self.handles if h["id"] == args["handle_id"])
            h["person_id"] = args["person_id"]
            return h
        if tool == "list_conversations":
            return [{"id": "c_1"}]
        if tool == "get_conversation":
            return {"id": "c_1", "messages": self.messages}
        if tool == "list_drafts":
            return copy.deepcopy(self.drafts)
        if tool in ("approve_draft", "reject_draft"):
            self.drafts = [d for d in self.drafts if d["id"] != args["draft_id"]]
            return {"status": "sent" if tool == "approve_draft" else "rejected"}
        raise AssertionError(tool)


class ConnectorTests(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        self.conn.executescript(inbound.SCHEMA)
        self.cid = intake.add(self.conn, "tt:creator.test", "test")
        self.conn.execute("UPDATE people SET email='Test@Example.com', phone='(202) 555-0123', stage='contacted' WHERE id=?", (self.cid,))
        intake.attach(self.conn, self.cid, "instagram", "Creator.Test", "test")
        self.conn.commit()
        self.client = FakeClient()

    def tearDown(self):
        self.conn.close()

    def sync(self):
        return asyncio.run(sync(self.conn, self.client))

    def draft(self, did="o_1"):
        return {"id": did, "status": "draft", "person_id": "p_1", "channel": "email", "handle_id": "h_3",
                "payload": {"text": "<message>", "subject": "Hello", "email_cc": ["copy@example.com"]}}

    def message(self, text="Yes, let's talk", mid="m_1", sender=None, direction="in"):
        sender = sender or self.client.handles[0]["id"]
        return {"id": mid, "direction": direction, "sender_handle_id": sender, "text": text, "subject": ""}

    def test_creation_idempotency_and_handles(self):
        self.sync()
        self.sync()
        self.assertEqual(len(self.client.people), 1)
        self.assertEqual(self.client.people["p_1"]["links"], [{"system": "creator-crm", "external_id": str(self.cid)}])
        self.assertEqual(self.conn.execute("SELECT person_id FROM contacts_mcp_people").fetchone()[0], "p_1")
        self.assertEqual({(h["channel"], h["value_normalized"]) for h in self.client.handles},
                         {("tiktok", "creator.test"), ("instagram", "creator.test"), ("email", "test@example.com"), ("imessage", "+12025550123")})
        self.assertEqual(sum(t == "add_handle" for t, _ in self.client.calls), 4)

    def test_remote_link_recovers_local_mapping_loss(self):
        self.sync()
        self.conn.execute("DELETE FROM contacts_mcp_people")
        self.conn.commit()
        self.sync()
        self.assertEqual(len(self.client.people), 1)

    def test_exact_existing_unlinked_handle_is_linked(self):
        self.client.handles.append({"id": "h_old", "channel": "tiktok", "account_id": "default",
                                    "value_normalized": "creator.test", "person_id": None})
        self.sync()
        self.assertEqual(self.client.handles[0]["person_id"], "p_1")
        self.assertTrue(any(t == "link_handle" for t, _ in self.client.calls))

    def test_conflicting_identity_is_not_stolen(self):
        self.client.people["p_other"] = {"id": "p_other", "links": [], "display_name": "Someone else"}
        self.client.handles.append({"id": "h_other", "channel": "tiktok", "account_id": "default",
                                    "value_normalized": "creator.test", "person_id": "p_other"})
        with self.assertRaisesRegex(ValueError, "belongs to another"):
            self.sync()
        self.assertFalse(any(t == "link_handle" for t, _ in self.client.calls))

    def test_draft_inbox_and_decisions(self):
        self.client.drafts = [self.draft(), self.draft("o_2"), dict(self.draft("o_other"), person_id="p_other")]
        self.sync()
        html = dashboard.inbox(self.conn, (InboxAdapter(),))
        self.assertIn("contacts-mcp messages (2)", html)
        self.assertIn("&lt;message&gt;", html)
        self.assertIn("copy@example.com", html)
        self.assertIn("last sync:", html)
        self.assertNotIn("o_other", html)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0], 0)
        asyncio.run(decide(self.conn, self.client, "o_1", "approve"))
        asyncio.run(decide(self.conn, self.client, "o_2", "reject"))
        approvals = [a for t, a in self.client.calls if t == "approve_draft"]
        self.assertEqual(approvals[0]["authorized_by"], OWNER)
        self.assertEqual([a for t, a in self.client.calls if t == "reject_draft"][0]["actor"], OWNER)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM contacts_mcp_drafts").fetchone()[0], 0)

    def test_stale_draft_and_do_not_contact_block_approval(self):
        self.client.drafts = [self.draft()]
        self.sync()
        self.client.drafts[0]["payload"]["text"] = "changed"
        with self.assertRaisesRegex(ValueError, "changed"):
            asyncio.run(decide(self.conn, self.client, "o_1", "approve"))
        self.sync()
        self.conn.execute("UPDATE people SET do_not_contact=1")
        self.conn.commit()
        with self.assertRaisesRegex(ValueError, "do-not-contact"):
            asyncio.run(decide(self.conn, self.client, "o_1", "approve"))
        self.assertFalse(any(t == "approve_draft" for t, _ in self.client.calls))
        asyncio.run(decide(self.conn, self.client, "o_1", "reject"))

    def test_ambiguous_send_outcome_is_not_resent(self):
        self.client.drafts = [self.draft()]
        self.sync()
        original = self.client.call
        async def uncertain(tool, **args):
            result = await original(tool, **args)
            if tool == "approve_draft":
                raise RuntimeError("Response lost after dispatch")
            return result
        self.client.call = uncertain
        with self.assertRaises(RuntimeError):
            asyncio.run(decide(self.conn, self.client, "o_1", "approve"))
        with self.assertRaisesRegex(ValueError, "decided elsewhere"):
            asyncio.run(decide(self.conn, self.client, "o_1", "approve"))
        self.assertEqual(sum(t == "approve_draft" for t, _ in self.client.calls), 1)

    def test_mapping_survives_partial_sync_and_is_backed_up(self):
        self.client.fail = "add_handle"
        with self.assertRaises(RuntimeError):
            self.sync()
        saved = self.conn.execute("SELECT person_id FROM contacts_mcp_people").fetchone()[0]
        self.client.fail = None
        self.sync()
        self.assertEqual(len(self.client.people), 1)
        backup = connect(":memory:")
        try:
            self.conn.backup(backup)
            self.assertEqual(backup.execute("SELECT person_id FROM contacts_mcp_people").fetchone()[0], saved)
        finally:
            backup.close()

    def test_inbound_uses_pipeline_and_deduplicates(self):
        self.sync()
        self.client.messages = [self.message()]
        self.sync()
        self.sync()
        p = self.conn.execute("SELECT * FROM people").fetchone()
        self.assertEqual(p["stage"], "replied")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM replies").fetchone()[0], 1)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM events WHERE kind='stage:replied'").fetchone()[0], 1)

    def test_no_and_unsubscribe_use_existing_rules(self):
        for text in ("No", "unsubscribe"):
            with self.subTest(text=text):
                self.sync()
                self.conn.execute("UPDATE people SET stage='contacted', do_not_contact=0")
                self.conn.commit()
                self.client.messages = [self.message(text, f"m_{text}")]
                self.sync()
                p = self.conn.execute("SELECT * FROM people").fetchone()
                self.assertEqual((p["stage"], p["do_not_contact"]), ("declined", 1))

    def test_outgoing_and_other_group_participants_ignored(self):
        self.sync()
        self.client.messages = [self.message("no", sender="h_stranger"), self.message("no", mid="m_out", direction="out")]
        self.sync()
        self.assertEqual(self.conn.execute("SELECT stage FROM people").fetchone()[0], "contacted")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM replies").fetchone()[0], 0)

    def test_burst_is_not_limited_to_timeline_window(self):
        self.sync()
        self.client.messages = [self.message(mid=f"m_{i}") for i in range(1001)]
        self.sync()
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM replies").fetchone()[0], 1001)
        self.assertFalse(any(t == "get_timeline" for t, _ in self.client.calls))

    def test_failure_preserves_cache_and_last_success(self):
        self.client.drafts = [self.draft()]
        self.sync()
        old = self.conn.execute("SELECT last_sync FROM contacts_mcp_health").fetchone()[0]
        self.client.fail = "list_drafts"
        with self.assertRaises(RuntimeError):
            self.sync()
        h = self.conn.execute("SELECT * FROM contacts_mcp_health").fetchone()
        self.assertEqual(h["last_sync"], old)
        self.assertEqual(h["error"], "RuntimeError")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM contacts_mcp_drafts").fetchone()[0], 1)
        self.client.fail = "sync_status"
        with self.assertRaises(RuntimeError):
            self.sync()
        self.assertEqual(self.conn.execute("SELECT reachable FROM contacts_mcp_health").fetchone()[0], 0)

    def test_email_matching_still_works(self):
        inbound.record(self.conn, "test@example.com", "", "Yes", "email_1")
        self.assertEqual(self.conn.execute("SELECT stage FROM people").fetchone()[0], "replied")

    def test_http_dashboard_routes_decisions_to_injected_adapter(self):
        # A real local HTTP handler, with fake MCP and channels. No live sends.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creators.db"
            self.sync()
            disk = connect(path)
            self.conn.backup(disk)
            disk.close()
            self.client.drafts = [self.draft()]
            @asynccontextmanager
            async def factory():
                yield self.client
            adapter = InboxAdapter(factory)
            disk = connect(path)
            adapter.sync(disk)
            disk.close()
            server = ThreadingHTTPServer(("127.0.0.1", 0), dashboard.make_handler(path, lambda: {}, lambda: {}, (adapter,)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                with opener.open(base) as response:
                    self.assertIn("o_1", response.read().decode())
                data = urllib.parse.urlencode({"id": "o_1", "do": "reject"}).encode()
                with opener.open(base + "/extension/contacts-mcp", data=data) as response:
                    self.assertEqual(response.status, 200)
                self.assertTrue(any(t == "reject_draft" for t, _ in self.client.calls))
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


class SDKTests(unittest.TestCase):
    def test_real_sdk_streamable_http_with_bearer_and_classic_server(self):
        calls = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                self.assert_bearer = self.headers.get("Authorization")
                request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                calls.append((self.assert_bearer, request))
                if "id" not in request:
                    self.send_response(202)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if request["method"] == "initialize":
                    result = {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}},
                              "serverInfo": {"name": "fake-contacts", "version": "0.1.0"}}
                elif request["method"] == "tools/list":
                    result = {"tools": [{"name": "sync_status", "inputSchema": {"type": "object"}}]}
                else:
                    result = {"content": [{"type": "text", "text": "[]"}]}
                body = json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                self.send_response(405)
                self.send_header("Content-Length", "0")
                self.end_headers()

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        async def run():
            async with open_client() as client:
                return await client.call("sync_status")
        try:
            with patch.dict(os.environ, {"CONTACTS_MCP_URL": f"http://127.0.0.1:{server.server_port}/mcp",
                                         "CONTACTS_MCP_TOKEN": "offline-test-token", "NO_PROXY": "127.0.0.1"}):
                self.assertEqual(asyncio.run(run()), [])
            self.assertTrue(all(auth == "Bearer offline-test-token" for auth, _ in calls))
            self.assertTrue(any(req["method"] == "tools/call" and req["params"]["name"] == "sync_status" for _, req in calls))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_json_text_and_safe_tool_errors(self):
        class Session:
            async def call_tool(self, name, args):
                return SimpleNamespace(is_error=name == "bad", content=[SimpleNamespace(type="text", text='{"id":"p_1"}')])
        self.assertEqual(asyncio.run(Client(Session()).call("get_person")), {"id": "p_1"})
        with self.assertRaises(ToolError):
            asyncio.run(Client(Session()).call("bad"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
