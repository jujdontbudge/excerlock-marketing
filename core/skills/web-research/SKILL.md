---
name: web-research
description: Read or crawl web pages, JS pages, PDFs, galleries and X posts, and pull social profiles or posts. Use for any research that needs content from the web outside TikTok and the ad libraries.
---

# Web research

## Tools, in order of preference
1. **One page, PDF, video or gallery:** `agent-web read|render|pdf|video|gallery URL --out raw/<task>/`. `render` for pages that need JavaScript.
2. **Many pages on one site:** `scripts/scrape-web URL ...` (setup and flags in `integrations/crawlee-crawl4ai/README.md`).
3. **Social profiles and posts:** `yt-dlp`, `gallery-dl`, `.venv/bin/nami`, `.venv/bin/instaloader`, and official APIs.
4. **Logged-in or interactive pages:** the project browser (`BROWSER.md`). If a login is needed, the user runs `python3 scripts/browser-login.py --headed-login URL`.

## Output
Save raw pages in `raw/<task>/`. Findings keep their source URL and capture date. Finished reports go in `research/` (see `research/README.md`).

## Don'ts
- Don't report a blocked or empty fetch as "nothing found". Why: a failed scraper is missing coverage, not evidence of absence.
- Don't paraphrase numbers without the source URL next to them. Why: nobody can check them later.
