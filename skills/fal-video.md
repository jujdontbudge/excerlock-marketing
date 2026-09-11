---
name: fal-video
description: Generate realistic video through verified fal.ai video endpoints with live schema and pricing checks.
---
# fal.ai video generation

Supported video families include Seedance 2.0/2.5, Kling 2.6/V3, Kling LipSync, OmniHuman, and WAN 2.1. The exact allowlist is in `scripts/fal-video.py`.

1. Confirm prompt, intended use, reference rights, likeness consent, format, and budget.
2. Select a suitable allowlisted video endpoint.
3. Run `.venv/bin/python scripts/fal-video.py schema --endpoint ENDPOINT` and `pricing --endpoint ENDPOINT` before constructing input.
4. Prepare schema-valid JSON and show the expected cost.
5. Submit only after explicit spend approval:
   `.venv/bin/python scripts/fal-video.py submit --endpoint ENDPOINT --input raw/INPUT.json --approve-spend`
6. Poll with `status`, retrieve with `result`, and inspect dimensions, duration, continuity, hands, product fidelity, audio, and claims.

Use `codex-image` for stills. Add further fal video endpoints only after confirming their official schema and that they generate video.
