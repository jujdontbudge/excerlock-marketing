# contacts-mcp ↔ creator operations

Phase 7 connector. contacts-mcp owns canonical person IDs, handles and its messages; the creator CRM retains its local workflow IDs as `creator-crm:<id>` links. This integration composes both systems outside the sections. It does not open the contacts database or call a channel directly.

## Settings and dependencies

Set `CONTACTS_MCP_URL` (the daemon's full `/mcp` endpoint, loopback or private tailnet) and `CONTACTS_MCP_TOKEN` (its bearer token) in the marketing repository's private `.env`. Values are never logged. Missing configuration fails the connector command without affecting standalone creator commands. No credentials or services are installed by this change.

Use the repository `.venv` and root `requirements.txt`; `mcp==2.2.0` was already pinned. The connector adds `phonenumbers` for normalization consistent with contacts-mcp (US default, E.164 output). The transport uses the [official Python SDK Streamable HTTP client](https://py.sdk.modelcontextprotocol.io/api/mcp/client/streamable_http/) with bearer authentication and 30-second request timeouts.

## Run

From the marketing repository:

```sh
integrations/contacts-mcp/contacts-creators sync
integrations/contacts-mcp/contacts-creators serve
integrations/contacts-mcp/contacts-creators jobs
# Optional: select the same existing creator database for every command.
integrations/contacts-mcp/contacts-creators sync --db /absolute/path/creators.db
```

`sync` only reconciles people/handles, reads pending drafts and imports inbound replies; it never approves or sends. Run it alongside the existing three-hour creator job. Alternatively, `jobs` syncs first and then runs the existing creator jobs (which can send previously approved CRM messages and process payouts). If sync fails, that composed job stops before running creator jobs. No scheduler/service configuration is changed here.

`serve` starts the existing dashboard with the adapter injected. Its inbox shows cached contacts drafts and a health line with last successful sync, last check, reachability at that check and a safe error class. Run `sync` before opening it, or use its existing “Run jobs now” button, which also syncs first. The standalone creator dashboard remains usable without this optional integration. Health is a recorded check, not a live connection probe.

Approving a contacts draft calls `approve_draft` with `authorized_by = "owner (creator dashboard)"` and the approval reason; that remote tool sends immediately. Rejecting calls `reject_draft` with the same owner as actor. Both require a pending draft from the linked creator, recheck that the cached document still matches the remote draft, and remove the cache entry after a decision. Approval is blocked for do-not-contact creators. No automatic approvals or send rules are added. Full payloads, including recipients and attachments, are shown for review. Contacts drafts never enter the CRM messages table, so its Resend/DM dispatcher cannot send them a second time. Failed remote sends are terminal and require manual reconciliation in contacts-mcp.

## Ownership and seams

The integration owns three `contacts_mcp_*` tables inside the creator SQLite store: creator↔person mapping, draft cache and health. This stores the returned person ID on the creator side without adding contacts-specific fields to the creator domain. Tables initialize idempotently, are included in existing backups, and mappings/cache rows cascade when a creator is deleted. Remote identity is verified by the actual external link, never fuzzy ranking or name. If the local mapping is lost, the remote link recovers it. Missing/changed links and handles owned by another person stop sync for review. Removed/changed CRM handles do not delete remote history or automatically unlink previous handles. Creator merges after synchronization require reviewing/consolidating canonical identities; the adapter deliberately refuses to steal a handle from another person.

The dashboard's generic `extensions` argument supplies `render(conn)`, `action(conn, route, fields) -> bool`, and `sync(conn)`. Existing calls default to no extensions. Only this integration knows contacts-mcp. The shared inbound handler gains a keyword-only `person_id` for adapters with verified identity; email matching remains the default. Its existing quoted-text stripping, duplicate provider ID handling, do-not-contact and legal pipeline transitions remain authoritative.

The current MCP has no incremental message-events tool. Sync uses `list_conversations` + unpaginated `get_conversation`, and passes unseen inbound messages through the existing handler with provider ID `contacts-mcp:<message-id>`. Only a sender handle owned by the linked person is accepted (other group members and outgoing messages are ignored). Initial sync imports existing history too; subsequent syncs deduplicate through the replies table. This avoids the capped timeline window losing a busy interval, but large histories are reread each pass. A paginated event feed with a durable ingestion cursor and sender person/handle ID would improve efficiency; no server addition is required for correctness with the present unpaginated conversation contract.

This phase consumes contacts drafts/messages; existing CRM-generated outreach continues through its existing channel seam. Migrating all CRM message creation/sending and historical mail into contacts-mcp is a separate channel migration.

## Tests

```sh
.venv/bin/python integrations/contacts-mcp/test_offline.py
scripts/test
scripts/lint
```

Tests use fake MCP tools with the real CRM store/pipeline and a local dashboard HTTP server. No live contacts daemon, channel or message send is used. They cover identity recovery/idempotency, normalized handles/unlinked matches/conflicts, draft review and decisions, stale drafts/do-not-contact approval blocks, inbound replay, refusal/unsubscribe, group sender attribution, history bursts beyond the timeline limit, safe errors, ambiguous dispatch responses without resend, mapping backup/partial sync durability and health/cache preservation. The SDK transport is exercised against a localhost fake HTTP MCP server, including bearer headers and classic protocol negotiation. Included in `scripts/test`.
