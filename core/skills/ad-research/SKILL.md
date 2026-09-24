---
name: ad-research
description: Find and record competitors' paid ads in the Meta Ad Library and the TikTok Creative Center or Commercial Content Library. Use when a task asks what competitors are running, for how long, or in which formats.
---

# Ad research

## Before collecting
Write down the advertisers or keywords, countries, time window, platforms and media type.

## Tools
1. **Meta Ad Library (official site)** first, in the project browser (`BROWSER.md`), to see what exists and confirm page names.
2. **Bounded collection:** `.venv/bin/meta-ads-collector -q QUERY -c US -s active --media-type video -n 100 -o raw/<task>/ads.json` (or `--page-ids`, `--search-pages`, date and impression filters; `--help` lists them).
3. **TikTok:** Creative Center and the Commercial Content Library in the browser; keyword discovery first, then enumerate each advertiser.
4. **Videos:** download with `yt-dlp` and hand them to the `video-analysis` skill.

## Output
A report with: a coverage matrix (advertiser × platform), totals, one written record per unique creative (hook, structure, offer, first-seen and last-seen dates, run length), and every tool limit. Finished reports go in `research/`.

## Don'ts
- Don't treat a long-running ad as a proven converter. Why: 30+ days only proves the advertiser kept paying (the "Meta longevity" rank in `research/README.md`).
- Don't count the same creative twice across placements or duplicate ad IDs. Why: advertisers run one video under many IDs, which inflates totals.
- Don't stop at the first page of results. Why: the library paginates quietly; record how far you got.
