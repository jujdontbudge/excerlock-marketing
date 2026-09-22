<!-- firstmate:global-worker:start -->
# Global worker instructions

This is the canonical global behavior for ordinary workers and scouts.
Its authoritative owner is `WORKER.md` in the Firstmate repository; edit that file, then run `bin/fm-ensure-agents-md.sh` for each project to refresh its managed copy.
Do not edit the managed copy inside a project's `AGENTS.md` by hand.
Project-owned instructions live outside the managed markers in that project's `AGENTS.md`.

## Work safely

- Follow the task instructions and the project's own instructions.
- Keep changes within the requested scope and do not discard work you did not create.
- Use the repository's existing build and test entry points when present; do not force irrelevant files or tools into a repository.
- Never delete, skip, weaken, or narrow tests merely to make a change pass.
- Prefer behavioral tests that exercise the user-visible or public contract.
- For a bug fix, reproduce the failure end to end as an end user before fixing it, then prove the same path works afterward.
- Before finishing, inspect the complete diff, confirm the full requested scope is covered, and remove unrelated changes.
- Report failures truthfully and mention only meaningful risk, decisions, or follow-up.
- Communicate in concise plain English.

## Architecture decisions

Projects may keep architecture decision records in `docs/adr/`.
Use short records describing context, decision, and consequences, named like `0001-example-decision.md`.
Preserve ADR history rather than rewriting an accepted decision in place.
Remind the user when a consequential architectural decision deserves an ADR, but never author one without explicit `/adr-verbatim` authority.

## Editing instruction layers

There are exactly three instruction owners: Firstmate behavior in `FIRSTMATE.md`, global worker behavior in `WORKER.md`, and project-specific behavior outside the managed worker section of each project's `AGENTS.md`.
Change the narrowest owner that applies.
Never add supervisor identity, fleet operation, delegation, merge authority, or monitoring mechanics to `WORKER.md` or to a project's managed worker section.
<!-- firstmate:global-worker:end -->
# ExcerLock Marketing

This workspace supports ExcerLock marketing. The app repository is separate.
Its purpose is audience and channel research, marketing strategy, creative production, campaign development, and performance learning.
Judge work by source quality, truthful representation, creative usefulness, platform compliance, publishing approval, and measurable marketing outcomes rather than software-delivery procedure.

## Method
- Clarify the target, region, timeframe, output, and platform before collecting.
- Use the lightest working route and preserve source URLs, dates, region, and coverage limits.
- A failed or blocked scraper is not complete coverage.
- Separate observed metrics from conclusions. Views and ad longevity do not prove conversion.
- Do not publish, launch campaigns, change budgets, or submit paid generation without approval.
- Slideshow scripts: follow `research/slideshows/script-writing-guide.md` (captain's walkthrough and preferences, each with its reason) and run `research/slideshows/reviewer-checks.md` before handing over; scripts live in `content/slideshows/`, each slide with on-screen text, one organic reference and our variation.

## Tools
- Web pages/JS/PDF/video/gallery: `agent-web read|render|pdf|video|gallery URL --out DIR`.
- Search/read fallback: Jina `web_search` and `web_fetch`.
- Multi-page crawl: `scripts/scrape-web URL ...`; use the project browser for interaction or login. See `BROWSER.md` for the dedicated profile and login workflow.
- TikTok trends/hashtags/profiles: `scripts/tiktok-research.py trending|hashtag|user ... --out raw/RESULT.json`.
- Social media: `yt-dlp`, `gallery-dl`, `.venv/bin/nami`, `.venv/bin/instaloader`, official APIs, then the project browser.
- Meta ads: official library first; `.venv/bin/meta-ads-collector` for bounded structured collection.
- TikTok ads: official Creative Center or Commercial Content Library through the browser.
- Transcription: `whisper-cli -m models/ggml-tiny.en.bin -f AUDIO -oj -of OUTPUT`; edit/verify with ffmpeg and ffprobe.
- Image prompting and generation: every image prompt is JSON, following `skills/organic-json-image-prompting.md` (workflows, schema, reference manifest, vendor wrapping). Validate and wrap with `python3 scripts/image-prompt.py check|wrap FILE`. Style digests come from `skills/style-clone.md` and live in `content/styles/`. Generate through the API keys at the lowest quality, one image at a time; use the `codex_image` bridge only when asked.
- Video: `.venv/bin/python scripts/fal-video.py schema|pricing|submit|status|result --endpoint ENDPOINT`. It allows verified Seedance, Kling, OmniHuman, and WAN video endpoints; check schema and price before submission.
- Memory: relevant Mem0 memories are recalled automatically. `local_memory` supports project/session/global search and full CRUD; mutations require explicit approval. Commands: `/mem0-remember`, `/mem0-forget`, `/mem0-search`, `/mem0-tour`, `/mem0-scope`, `/mem0-status`, and `/memory-review`.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
