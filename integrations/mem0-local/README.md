# Local Mem0 OSS for Pi

This is a local implementation of the official Mem0 Pi workflow using Mem0 OSS, embedded Qdrant, local FastEmbed embeddings, and `openai-codex/gpt-5.6-luna` at maximum reasoning for inferred memory extraction.

## Features

- Automatic semantic recall before every agent response
- Git-root project detection
- Repository-wide project scope and isolated session scope
- Default relevance threshold `0.3`
- Categories: identity, preferences, goals, projects, decisions, technical, relationships, routines, lessons, and work
- Tool actions: status, add, search, list/get_all, get, update, delete, and delete_all
- No automatic conversation capture or recurring approval prompt
- Approval-gated mutations
- Local storage under `~/.pi/mem0-oss`

## Commands

- `/mem0-remember <text>`
- `/mem0-forget <query>`
- `/mem0-search <query>`
- `/mem0-tour [project|session]`
- `/mem0-scope project|session`
- `/mem0-status`
- `/memory-review`

Relevant memories are recalled automatically. New memories are stored only after an explicit request.

## Components

- `.pi/extensions/local-memory.ts`
- `worker.py`
- `pi_luna.py`
- `luna-bridge.mjs`
- `.venv/`

## Verification

```bash
integrations/mem0-local/.venv/bin/python -m pytest -q integrations/mem0-local/test_worker.py
uv pip check --python integrations/mem0-local/.venv/bin/python
```
