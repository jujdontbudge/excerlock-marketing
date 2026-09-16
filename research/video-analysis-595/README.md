# Video analysis, 595 videos — evidence pack guide

This folder holds the captain-facing outputs of the 595-video creative research
(540 long-running Meta Ad Library creatives + 55 TikToks over 10,000 views,
analyzed 2026-09-15). The narrative deliverable is `report.md` in this folder.
This README explains how to use the bulk evidence files and how to read the
evidence ranks honestly.

## What to read, in order

1. **`report.md`** — the canonical narrative: corpus accounting, organic /
   promoted / longevity findings, the twelve repeated creative structures
   (§8), ethical ExcerLock applications by audience (§9), claim and
   brand-safety risks (§10), limitations (§11).
2. **`INDEX.md`** — one-page captain-facing summary (hooks, 12 structures,
   white space, shoot-first recommendations).
3. Bulk evidence files under the firstmate `data/` tree (below) when you need
   per-video detail.

## Bulk evidence files (NOT copied into git — authoritative paths)

These live in the firstmate home tree and stay there; cite these absolute
paths rather than duplicating megabytes of JSONL:

| File | Lines | Size | What it is |
|---|---|---|---|
| `/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/records.validated.jsonl` | 595 | ~2.9 MB | One signed per-video analysis record per video (stable IDs cited throughout `report.md`) |
| `/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/manifest.jsonl` | 595 | ~367 KB | Input manifest: which videos were queued, sources, stable IDs |
| `/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/comments.jsonl` | 55 | ~94 KB | TikTok comment-evidence rows (PKG-B); 47 unavailable / 8 empty-at-capture are accounted for in `tiktok-comments` research |
| `/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/validation.md` | 74 | ~16 KB | PKG-C validation methods, corrections, spot-check scores |
| `/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/usage.json` | 58 | ~2.4 KB | Spend/model accounting (see below) |
| `/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/failures.jsonl` | — | — | Count discrepancy and missing-media accounting (referenced by report §12) |

Use `records.validated.jsonl` for everything per-video: hooks, structures,
timestamps, captions, CTA placement, stable IDs. `comments.jsonl` maps comment
language to video moments — it contains no verbatim comment text by design.

## Spend note

Total spend was **$6.10** of a $10.00 cap (`usage.json`: `spent_usd
6.100442`, model `gemini-3.8-flash`, standard generate_content endpoint,
prompt versions v2–v5, batch pilot 8 videos still queued and uncancelled at
completion with skip-done guards). No further analysis spend is authorized
without a new captain decision.

## Evidence ranks — do not collapse them

Every finding in `report.md` carries one of three evidence ranks. Keep the
label with the claim:

- **Organic** (31 unpromoted TikToks) — the genuine creative signal; highest
  weight. View counts are single-capture snapshots (2026-09-12).
- **Promoted** (24 TikToks with `isAd=true`) — paid-format patterns only;
  view counts are distribution, not verdicts. Discount multipliers
  accordingly.
- **Meta longevity** (540 long-running Meta creatives) — a **reuse/longevity
  signal only**. Longevity ≠ performance; an ad running 30+ days proves the
  advertiser kept paying for it, not that it converts.

## Honesty rules that travel with this research

- Organic vs promoted vs Meta-longevity labels are never merged or dropped.
- No comment text is quoted anywhere (comment evidence is structural only).
- Meta longevity is never presented as a performance or conversion claim.
- Copy structures and principles, never footage, distinctive scripts,
  likenesses, or music.

## Superseded file

`/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/playbook.md`
is a **pre-analysis skeleton** (33 lines, "PENDING synthesis"). It is
superseded by `report.md` §8–§10, which carry the transferable structures,
audience applications, and safety list inside the final report. Do not fill it
in or resurrect a separate playbook.
