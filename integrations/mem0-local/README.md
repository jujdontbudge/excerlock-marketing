# Project memory integration

One implementation owner: the machine-level shared engine at `~/.local/share/firstmate-projects/local-memory.ts` and its `mem0/worker.py`. The project extension imports it through `project-policy.mjs`; the former separate Luna worker is archived under `history/experiments/mem0-local/`.

## Effective project policy

- **Manual recall only.** No automatic memory hooks are registered here. Existing project records remain searchable, not always-loaded rules.
- **No automatic capture or queue flush.** No conversation extraction/model calls originate from these project hooks. Fleet-wide configuration and other projects are unchanged.
- Explicit approved CRUD, project/session isolation, local embeddings/storage, and commands are owned by the shared engine. Current behavior is queried, not copied into this README.
- `/mem0-status` and `local_memory` status show effective `autoCapture=false` / `automaticRecall=false`, alongside `engineAutoCapture` / `engineAutomaticRecall`. Those engine defaults may still be true for other integrations.
- The reviewed 291 records are retained as evidence; keyword flags were not sufficient grounds to delete them. Follow canonical project files over recalled historical rules. Never store secrets.

Commands: `/mem0-search`, `/mem0-remember`, `/mem0-forget`, `/mem0-tour`, `/mem0-scope`, `/mem0-status`, `/memory-review`. Mutation requests retain the engine’s approval gate.

## Verification

`node --test integrations/mem0-local/test_project_policy.mjs` loads the actual shared extension through installed Pi’s Jiti/package resolution, checks its registration and real read-only status, and exercises rejection of unapproved mutations. No provider extraction call or memory write is made.

Prerequisites: this Mac’s shared engine/Python environment and installed Pi runtime. A standalone checkout without them cannot run this integration; it must not silently substitute the archived worker. Existing sessions need an extension reload/restart to receive the new registration policy. A launcher that bypasses project extensions does not receive this adapter.
