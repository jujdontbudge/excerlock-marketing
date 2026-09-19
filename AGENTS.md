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
- Images: use the `codex_image` tool for generation and editing; it wraps the local subscription-backed Codex bridge and preserves the user's final prompt.
- Image prompting: organic iPhone photo template `skills/organic-iphone-photo.md`, style cloning `skills/style-clone.md`, saved styles `content/styles/`.
- Video: `.venv/bin/python scripts/fal-video.py schema|pricing|submit|status|result --endpoint ENDPOINT`. It allows verified Seedance, Kling, OmniHuman, and WAN video endpoints; check schema and price before submission.
- Memory: relevant Mem0 memories are recalled automatically. `local_memory` supports project/session/global search and full CRUD; mutations require explicit approval. Commands: `/mem0-remember`, `/mem0-forget`, `/mem0-search`, `/mem0-tour`, `/mem0-scope`, `/mem0-status`, and `/memory-review`.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
