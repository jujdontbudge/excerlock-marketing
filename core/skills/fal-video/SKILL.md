---
name: fal-video
description: Generate realistic video through verified fal.ai video endpoints, with live schema and pricing checks before any spend. Use when a still (usually a `video_first_frame` image) needs to become a video clip.
---
# fal.ai video generation

Supported video families include Seedance 2.0/2.5, Kling 2.6/V3, Kling LipSync, OmniHuman and WAN 2.1. The exact allowlist is in `core/skills/fal-video/fal-video.py`. The script reads `FAL_KEY` from the repo-root `.env`.

## Inputs

- The first frame or reference images, the motion wanted, the format and the budget.
- Stills, including first frames, come from `core/skills/image-prompt/SKILL.md` (`video_first_frame` mode).

## Steps

1. Confirm the prompt, intended use, reference rights, likeness consent, format and budget.
2. Pick a suitable allowlisted video endpoint.
3. Run `.venv/bin/python core/skills/fal-video/fal-video.py schema --endpoint ENDPOINT` and `pricing --endpoint ENDPOINT` before building the input.
4. Write schema-valid input JSON in `raw/` and state the expected cost.
5. Submit only after the captain approves the spend:
   `.venv/bin/python core/skills/fal-video/fal-video.py submit --endpoint ENDPOINT --input raw/INPUT.json --approve-spend`
6. Poll with `status --request-id ID`, retrieve with `result --request-id ID`, and inspect dimensions, duration, continuity, hands, product fidelity and audio.

## Outputs

- The video file and its request ID, saved outside the repo or in `raw/`.

## Don'ts

- Don't submit without explicit spend approval and a stated cost. Why: every submit is paid, and spend is the captain's decision.
- Don't build input from memory. Why: endpoint schemas and prices change; the live `schema` and `pricing` calls are the source of truth.
- Don't write a complex video prompt. Why: one continuous take with no zoom and no cuts keeps the motion believable.
- Don't add an endpoint to the allowlist before confirming its official schema and that it generates video. Why: the script must never become an unrestricted image or model runner.
