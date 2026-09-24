---
name: tiktok-research
description: Collect TikTok posts and their stats for a hashtag, user, search or trending feed, and download slides or videos. Use when a task needs real TikTok examples, numbers or media.
---

# TikTok research

## Before collecting
Write down the target (hashtag, user, keyword list), region, time window, minimum plays, photo mode or video, and where the output goes (`raw/<task>/` while working, a report in `research/` when finished).

## Tools, in order of preference
1. **Metadata (free):** `.venv/bin/python core/skills/tiktok-research/tiktok-research.py trending|hashtag|user TARGET --count N --out raw/<task>/result.json`. Set `TIKTOK_MS_TOKEN` in `.env` if TikTok blocks the session.
2. **Media:** `yt-dlp URL` for videos, `gallery-dl URL` for photo posts (all slides). Drop the MP3 unless the audio matters.
3. **Keyword search with filters (photo mode):** the signed-in project browser (see `BROWSER.md`) calling `https://www.tiktok.com/api/search/photo/full/?aid=1988&keyword=<kw>` page by page. This is how the archived hunts `data/tt-hunt-*` were collected; read one of their `report.md` "Coverage" sections before repeating the method.
4. **Paid-format discovery:** TikTok Creative Center or the Commercial Content Library, through the browser.

## Output
- `posts.json`: one row per post with URL, author, posted date, plays, likes, saves, comments, slide count, caption, capture date.
- A report with a Coverage section first: keywords, window, filters, how many results came back and how many were kept, and every tool limit hit (blocked pages, empty pages, pagination stops).
- On-slide text: OCR it and keep the slide image as the source of the exact wording.

## Don'ts
- Don't call a relevance-ranked search complete coverage. Why: TikTok search stops returning items without warning; the archived hunts hit empty pages mid-run.
- Don't mix promoted and organic posts in one number. Why: paid reach says nothing about how the creative performs organically (see the evidence ranks in `research/README.md`).
- Don't carry old metrics forward. Why: counts change daily; re-fetch and date every snapshot.
- Don't commit downloaded media. Why: it's large and belongs to the creators; keep it in `raw/` or the archive.
