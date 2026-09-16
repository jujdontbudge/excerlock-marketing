# ExcerLock research index

Finished research organized under this tree. Every report here is a
content-complete copy; bulk JSONL evidence stays in the firstmate `data/`
tree (authoritative paths given per section) rather than being duplicated
into git.

## How to read evidence ranks

Findings across these reports carry three evidence labels. Never collapse or
drop them:

- **Organic** — unpromoted TikTok posts; the genuine creative signal, highest
  weight. View counts are single-capture snapshots (capture 2026-09-12).
- **Promoted** — TikTok posts with `isAd=true`; paid-format patterns only.
  View counts show distribution, not quality. Discount accordingly.
- **Meta longevity** — long-running Meta Ad Library creatives. A reuse
  signal only: an ad running 30+ days proves the advertiser kept paying,
  **not** that it converts. Longevity ≠ performance.

Additional standing rules: no comment text is quoted anywhere (comment
evidence is structural only); copy structures and principles, never footage,
distinctive scripts, likenesses, or music; no claim travels without its
evidence rank.

## What's here

### `competitor-universe/report.md`
The fitness competitor universe: names-first master list across
movement-gated screen time, step rewards, walking social, women's fitness,
gym/strength, physique, and habit categories, with competitive tiers,
evidence labels (confirmed-active marketers vs store-active only), and a
deduplicated evidence table.

### `creative-30d/report.md`
Competitor creative collection over a 30-day window (Phase 2 of the
competitor map): per-competitor coverage matrix by platform, confirmed-active
marketers, and written records of high-performing creatives (F01–F16+).

### `ad-video-30d/report.md`
Competitor video ads, rolling 30 days, from the Meta Ad Library (US view)
and TikTok Commercial Content Library (keyword discovery + advertiser-level
enumeration): coverage matrix, totals, and one written record per accessible
unique creative.

**Relationship note:** this is the finished **resume** report, copied from
`/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/competitor-ad-video-30d-resume/report.md`.
The earlier non-resume run (`.../data/competitor-ad-video-30d/report.md`) is
byte-identical to it (same 18,802-line report); the resume folder marks the
run that actually completed. Cite this copy.

### `video-analysis-595/` (see its README + INDEX)
The 595-video creative analysis (540 long-running Meta creatives + 55
TikToks): evidence ranks, organic/promoted/longevity findings, the twelve
repeated structures, audience applications, and claim-safety bounds.

- `report.md` — canonical final narrative
- `README.md` — how to use the bulk evidence (records, manifest, comments,
  validation, usage) at their authoritative firstmate `data/` paths, with
  line counts; the $6.10 spend note; honesty rules
- `INDEX.md` — one-page captain-facing summary: hooks, 12 structures, white
  space, shoot-first list

### `tiktok-comments` (evidence only, no copy)
The TikTok comment-evidence report (PKG-B) lives at
`/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/tiktok-comments/report.md`
(139 lines). Its findings are already folded into the 595-video report and
its raw rows into `comments.jsonl` (path in
`video-analysis-595/README.md`), so it is pointed at rather than copied.

## Superseded material

- `/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/gemini-video-batch/playbook.md`
  — a pre-analysis **skeleton** ("PENDING synthesis", 33 lines). Superseded by
  the 595-video report's §8–§10, which carry the transferable structures,
  applications, and safety list inside the final report. Do not fill it in;
  no separate playbook exists or should be created.
- The pre-existing 71-line coordinator preflight report inside
  `.../data/gemini-video-batch/` was superseded by the final 595-video
  synthesis report (noted in that report's §12).

## Adjacent work kept as-is

`research/slideshows/` is untouched by this organization pass.

## Provenance

Copied from the firstmate evidence tree
(`/Users/johansardar/firstmates/excerlock-marketing-firstmate/data/`) on
2026-09-16, local-only, no analysis re-run, no additional spend.
