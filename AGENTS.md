# ExcerLock Marketing

Marketing research and creative production for ExcerLock, an app that blocks the apps a user picks (TikTok, Instagram and similar) until they move: walk, hit a step goal, or go to the gym. The app lives in a separate repository; nothing here builds or ships software.
The main output so far is organic-looking TikTok photo slideshows for the gym-girl and walking-girl audiences, backed by competitor and creative research.
"The captain" in the docs is the owner; his rules and reviews override agent judgment and older research.

## Where things live
- `content/slideshows/<NN-slug>/script.md`: slideshow scripts; `content/slideshows/README-02-05.md` indexes decks 02 to 05.
- `content/styles/`: style digests (JSON), indexed in its `README.md` and `index.json`. `content/prompts/`: saved JSON image prompts.
- `research/`: finished reports; start at `research/README.md`. `research/slideshows/`: the script guide, reviewer checks, hooks, formats and the image build log.
- `strategy/`: product truth (`excerlock-slideshow-questions.md`) and the draft hook bank.
- `skills/`: plain-Markdown procedures, not agent plugins. `image-reimagine.md` and `organic-iphone-photo.md` are legacy; use `organic-json-image-prompting.md`.
- `raw/`: gitignored scratch for collected evidence and media. Reference images stay here or outside the repo, never committed.
- Old work not yet in this repo is archived at `~/firstmate-decommission-backup-2026-09-23-v2/quarantine-firstmates/excerlock-marketing-firstmate/data/`. `data/...` paths in scripts and research point there. It holds the three TikTok photo-mode hunts (`tt-hunt-gym-consistency`, `tt-hunt-fat-loss`, `tt-hunt-dream-body`: reports, `posts.json`, slide images), the CTA blocker screen, the steps and screen-time receipts, the body benchmark, the Hayden character options, deck image builds and `captain.md`. Read from it freely; ask before moving anything, and never open `account-credentials.md` or `gemini-api-key`.

## Research rules
- Clarify the target, region, timeframe, output and platform before collecting.
- Preserve source URLs, capture dates, region and coverage limits. A failed or blocked scraper is not complete coverage.
- Keep the evidence ranks in `research/README.md` (organic, promoted, Meta longevity). Separate observed metrics from conclusions; views and ad longevity do not prove conversion.
- Copy structures and principles, never footage, distinctive scripts, likenesses or music.
- Do not publish, launch campaigns, change budgets or submit paid generation without approval.

## Slideshows, images and video
- Scripts follow `research/slideshows/script-writing-guide.md` and pass `research/slideshows/reviewer-checks.md` before handover. Each slide has on-screen text, one organic reference and our variation.
- Every image prompt is JSON per `skills/organic-json-image-prompting.md`. `python3 scripts/image-prompt.py check FILE...` validates; `wrap FILE --target openai|gemini|codex` prints the request without sending it.
- Style digests come from `skills/style-clone.md` and live in `content/styles/`.
- Generate through the OpenAI or Gemini API keys at the lowest quality, one image at a time; use `codex-image` only when asked.
- Video follows `skills/fal-video.md`: run `.venv/bin/python scripts/fal-video.py schema|pricing --endpoint ENDPOINT` first; `submit` needs spend approval.

## Research tools
- Single pages, JS pages, PDFs, video and galleries: `agent-web read|render|pdf|video|gallery URL --out DIR`.
- Multi-page crawl: `scripts/scrape-web URL ...` (setup in `integrations/crawlee-crawl4ai/README.md`).
- Interactive or logged-in pages, Meta Ads Library and TikTok Creative Center or Commercial Content Library: a browser. Pi's project browser and its dedicated profile are described in `BROWSER.md`.
- TikTok metadata: `.venv/bin/python scripts/tiktok-research.py trending|hashtag|user ... --out raw/RESULT.json`.
- Social media: `yt-dlp`, `gallery-dl`, `.venv/bin/nami`, `.venv/bin/instaloader` and official APIs before the browser. Meta ads: the official library first, then `.venv/bin/meta-ads-collector` for bounded collection.
- Transcription: `whisper-cli -m models/ggml-tiny.en.bin -f AUDIO -oj -of OUTPUT`; edit and verify with `ffmpeg` and `ffprobe`.
- Pi sessions (`pi-marketing`) also load `.env`, Jina `web_search`/`web_fetch`, the project browser tools and local Mem0 memory (`integrations/mem0-local/README.md`); these are not available to other agents.

## Checks and editing
- Validate every prompt JSON with `scripts/image-prompt.py check`; review scripts and images with `research/slideshows/reviewer-checks.md`.
- `scripts/rich-md FILE.md` opens a repo Markdown file in a local rich editor (`tools/rich-md/README.md`).
- Integration tests are listed in `integrations/*/README.md` and `tools/rich-md/README.md`.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
