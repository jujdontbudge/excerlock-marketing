# SideShift applicants → creator operations

This composition adapter connects SideShift job applicants to the existing creator dashboard and three-hour jobs. SideShift messages remain owned by the [contacts adapter](../contacts-mcp/README.md). This adapter never reads chats, opens support channels, drafts messages, sends messages, posts jobs, or makes automatic applicant decisions.

## Setup and commands

Use the repository `.venv` (existing `requests` and `python-dotenv` dependencies). Set `SIDESHIFT_API_KEY` in the private root `.env`; locally the adapter also reads that single variable from `/Users/johansardar/contacts-mcp/.env` when unset. Keys, raw API responses and URLs are never logged. Minimum scopes: `jobs:read`, `applicants:read`, `applicants:write` for owner decisions. No messages, recruit or Discover scope is used.

```sh
integrations/sideshift/sideshift-creators sync
integrations/sideshift/sideshift-creators serve
integrations/sideshift/sideshift-creators jobs
# Use the same database for all commands if overriding the default:
integrations/sideshift/sideshift-creators sync --db /absolute/path/creators.db
# Preserve the existing contacts message panel and sync in one composition:
integrations/sideshift/sideshift-creators serve --contacts
integrations/sideshift/sideshift-creators jobs --contacts
```

`sync` uses only remote GET requests and writes imported data/research locally. It reads the company overview, job list and details, paginated job applicants and advanced application answers, and each applicant's top posts. The overview is a counts/sample surface, so it is never treated as the entire queue. The job-list API is bounded at 100 without pagination; sync refuses to report success if the overview says more jobs exist than the list exposes. Unknown fields are preserved in the cached documents. Private uploaded-video download links are displayed on the private dashboard; sync refreshes them. No uploads or downloads of applicant videos occur here.

`serve` injects the generic dashboard `render`, `action`, `sync` extension. The panel includes answers, uploaded video links, handles, score, status, requirements hints, research errors and health. Missing/ambiguous answers are marked for review; flags never decide an applicant. Run sync first; the existing “Run jobs now” button also syncs the injected extensions before creator jobs.

`jobs` syncs first, then runs ordinary creator jobs. **Those existing jobs can send previously approved CRM messages and process payouts.** This wrapper adds no approvals or new send rules. A sync error stops the wrapper before creator jobs. Missing SideShift configuration instead records `MissingKey` and disables its sync, leaving creator commands usable. With `--contacts`, contacts sync retains its existing failure behavior.

## Ownership and seams

The adapter owns `sideshift_people`, `sideshift_applications`, `sideshift_decisions`, and `sideshift_health` in the existing creator SQLite store, included in its normal backups. The external user ID maps to one creator; `(user_id, job_id)` is the unique application link, including when one creator applies to multiple jobs. Adapter tables cascade on deletion. Applicant documents, answers, private video links, job documents and top posts stay in this store, never tracked files. Existing handles/emails reuse intake identities; conflicts stop for human identity review rather than stealing handles. A generic intake `create` function supports people with no handles. Creator merges after linking need deliberate consolidation of external mappings; the adapter does not guess.

For public handles, sync uses the existing snapshot platform seam (seven-day freshness) and numerical vetting. Snapshot failures are recorded as safe classes and leave the application reviewable; no paid analysis API is used. Top posts are preserved as context, not used as a biased substitute for the normal recent-post snapshot. Scores remain unavailable without snapshots. Automatic sync never shortlists or declines new applicants.

Only owner POSTs to `/extension/sideshift` can request `Accepted` or `Declined` through `POST /applicants/status`, with exactly `userId`, `jobId`, `newStatus`. The adapter re-reads the application for stale status/answers, validates local pipeline compatibility and blocks Accept for do-not-contact creators. Decline remains permitted without clearing do-not-contact. Generic pipeline transitions permit owner shortlisting/declining of new or scored applicants: Accept maps to `shortlisted`; Decline maps to `declined`. No fictitious outreach or score is added. Accept on a creator already beyond shortlist, or Decline on a signed/terminal creator, stops before the API call for review. Multiple applications remain separate remote decisions, but share one local creator stage; conflicting job decisions therefore require human review.

Before a write, a durable decision journal stores a UUID used as the API idempotency key. No automatic POST retries occur. A timeout/failure leaves the decision uncertain and blocks another click. Sync finishes the local pipeline move only when the remote status matches that already-owner-authorized intent. Otherwise reconcile in SideShift, then sync; if the owner confirms the write never happened, remove the specific pending journal row manually after backing up the store. Never bulk-clear uncertain decisions. Decisions made independently in SideShift are shown as remote statuses but do not automatically move the local pipeline.

Errors shown in health/CLI use safe classes only; API bodies, credentials and platform error messages are suppressed. HTTP requests have 30-second timeouts, reject redirects, stop on 429 and honor `Retry-After` within the current client. There are no immediate retries; scheduled runs can try again later. Cache survives failures and records last successful sync separately from the last attempt.

## Deploy on the MacBook Air (manual; not performed here)

The existing [creator deployment](../../sections/creators/README.md) installs core services but neither ships integration directories nor copies this key. Its deploy command also rewrites `.env` and resets service commands: if used later, repeat the key and wrapper steps below. Do not replace the Air's database.

1. From this repository, copy reviewed code, preserving the Air's data:

   ```sh
   rsync -az --exclude data --exclude __pycache__ --exclude '*.pyc' sections/creators/ johansardar@100.78.200.121:excerlock-creators/sections/creators/
   ssh johansardar@100.78.200.121 'mkdir -p ~/excerlock-creators/integrations/sideshift'
   rsync -az --exclude __pycache__ integrations/sideshift/ johansardar@100.78.200.121:excerlock-creators/integrations/sideshift/
   ```

   If enabling `--contacts`, also copy `integrations/contacts-mcp/` to the corresponding Air directory and install its documented `mcp==2.2.0` and `phonenumbers` dependencies. Preserve its existing private URL/token settings.

2. Transfer only the SideShift key into the Air's private `.env` without displaying it. This command replaces only that setting and keeps all other environment lines:

   ```sh
   .venv/bin/python - <<'PY' | ssh johansardar@100.78.200.121 'umask 077; tmp=$(mktemp); cat > "$tmp"; ~/excerlock-creators/.venv/bin/python - "$tmp" <<"REMOTE"
   import os, sys
   from pathlib import Path
   p = Path.home() / "excerlock-creators/.env"
   line = Path(sys.argv[1]).read_text().strip()
   if not line.startswith("SIDESHIFT_API_KEY=") or len(line.split("=",1)[1]) < 1:
       raise SystemExit("MissingKey")
   text = p.read_text() if p.exists() else ""
   p.write_text("\n".join(s for s in text.splitlines() if not s.startswith("SIDESHIFT_API_KEY=")) + "\n" + line + "\n")
   os.chmod(p, 0o600)
   Path(sys.argv[1]).unlink()
   REMOTE'
   import sys
   sys.path.insert(0, "integrations/sideshift")
   from dotenv import load_dotenv
   load_dotenv(".env")
   from client import api_key
   key = api_key()
   if not key:
       raise SystemExit("MissingKey")
   print("SIDESHIFT_API_KEY=" + key)
   PY
   ```

3. On the Air, verify dependencies and run a read-only remote sync against the existing default store:

   ```sh
   cd ~/excerlock-creators
   .venv/bin/python -c 'import requests, dotenv'
   integrations/sideshift/sideshift-creators sync
   ```

4. On the Air, stop only dashboard and jobs, replace their executable with the wrapper, preserve all other plist settings (including the existing 10800-second interval), and reload. Portal, backups, Tailscale Serve/Funnel and the database path stay as configured:

   ```sh
   launchctl bootout "gui/$(id -u)/com.excerlock.creators.dashboard"
   launchctl bootout "gui/$(id -u)/com.excerlock.creators.jobs"
   ~/excerlock-creators/.venv/bin/python - <<'PY'
   import plistlib
   from pathlib import Path
   wrapper = str(Path.home() / "excerlock-creators/integrations/sideshift/sideshift-creators")
   for service in ("dashboard", "jobs"):
       path = Path.home() / f"Library/LaunchAgents/com.excerlock.creators.{service}.plist"
       config = plistlib.loads(path.read_bytes())
       config["ProgramArguments"][0] = wrapper
       # To retain contacts integration, append "--contacts" to both arrays.
       path.write_bytes(plistlib.dumps(config))
   PY
   launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.excerlock.creators.dashboard.plist
   launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.excerlock.creators.jobs.plist
   ```

   If launchd still reports the old service, wait for `launchctl print` to show it gone before bootstrapping, as in the existing deployment script. Jobs have `RunAtLoad`: bootstrapping runs the composed job, including existing authorized sends/payouts. Check `logs/dashboard.log`, `logs/jobs.log`, the existing tailnet dashboard and its SideShift health/counts. Owner decisions remain manual. Rollback changes `ProgramArguments[0]` back to the prior CLI (standalone or contacts wrapper), removes any newly added `--contacts` flag and reloads those two services; imported data remains backed up.

## Verification

```sh
.venv/bin/python integrations/sideshift/test_offline.py
scripts/test
scripts/lint
```

Fake HTTP exercises the real store, intake, snapshots, vetting and pipeline: replay, pagination, no handles/email, identity conflicts, flags, HTML escaping/video links, owner payloads, do-not-contact, stale/advanced-stage decision blocks, API errors/cache retention, missing key, rate limiting and ambiguous-write reconciliation. No test sends messages or uses live applicant decisions.

Latest local verification (2026-10-12): 16 adapter tests pass, including a real localhost dashboard GET/owner POST with fake SideShift HTTP and optional contacts composition loading. Read-only live sync against a gitignored scratch creator store reports **1 job, 0 applicants, 0 research errors**. The live advanced queue rejects `limit=100` with 400 but accepts `limit=25`, so queue pagination uses 25. No live status changes or messages were made. Zero applicants means actual applicant payloads have not yet been observed; answer parsing is covered by documented-shape fixtures.

The complete `scripts/test` run passes the adapter, contacts, creator and Python helper suites, then stops at the unrelated Mem0 integration because the installed Pi runtime cannot resolve `jiti`. The remaining crawler suite also cannot run: the crawler integration’s private Python executable is absent. Neither prerequisite is changed by this adapter. `scripts/lint` reports only the 33 known existing image-link problems, with no new findings.
