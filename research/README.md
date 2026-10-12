# Research

Finished evidence only: reports with sources, capture dates and coverage limits. Nothing here is an instruction; the rules and procedures live in `core/skills/` and `sections/*/`.
Bulk evidence (JSONL, images) stays in the archive; `data/...` paths mean `~/firstmate-decommission-backup-2026-09-23-v2/quarantine-firstmates/excerlock-marketing-firstmate/data/`.

## Evidence ranks

Findings carry one of three labels. Keep them when you quote a finding.

- **Organic**: unpromoted TikTok posts. The real creative signal, highest weight. View counts are single-capture snapshots.
- **Promoted**: TikTok posts with `isAd=true`. Paid-format patterns only; views show distribution, not quality.
- **Meta longevity**: long-running Meta Ad Library creatives. An ad running 30+ days proves the advertiser kept paying, not that it converts.

## Reports

| Path | What it is |
|---|---|
| `competitor-universe/report.md` | Names-first list of fitness competitors across movement-gated screen time, step rewards, walking, women's fitness, gym, physique and habit apps, with tiers and evidence labels. |
| `creative-30d/report.md` | Competitor creatives over 30 days: coverage per competitor and platform, written records of high performers (F01-F16+). |
| `ad-video-30d/report.md` | Competitor video ads over 30 days from the Meta Ad Library (US) and TikTok Commercial Content Library, one record per creative. Copied from `data/competitor-ad-video-30d-resume/report.md`. |
| `video-analysis-595/` | 595 videos (540 long-running Meta creatives + 55 TikToks): findings by evidence rank, twelve repeated structures, hooks. Start at its `INDEX.md`; `README.md` gives the bulk evidence paths. |
| `liked-slideshows/` | Voice taste board from 12 liked TikTok photo posts (54 slides, 2026-09-16): two independent caption analyses. |
| `slideshow-articles.md` | Business and operations lessons from three X articles on TikTok slideshow marketing (the deck-writing lessons are in the hooks-and-formats skill). |
| `low-cost-ios-marketing-x.md` | Public X posts, 2026-03-26 to 2026-09-26, from people scaling iOS apps with cheap organic distribution. @johansardar's following list was login-walled, so these are not confirmed follows. |
| `ai-ugc-omni-notes.md` | Working notes (not yet a skill) from the first AI UGC phone-walk tests with Omni 1.1 Flash: what worked, the two-women failure, extension prompts, checks before handing over. |
| `ai-ugc-reference-first/` | Kristian Jennings' reference-first AI UGC method (31-min video, transcript and frames analysed, `video.md`) and an audit of our image, character and video workflow against it (`audit.md`, proposals only). |
| `walking-apps-30d/report.md` | How 8 walking/step-counter apps (StepsApp, WalkFit, Pedometer++, Pacer, Map My Walk, Stepz, Pedometer - Run & Step Counter, Leap's purple Pedometer) marketed 2026-09-02 → 2026-10-02: Meta and TikTok ads, TikTok and Instagram organic, creator posts, coverage gaps. |
| `data/tiktok-comments/report.md` (archive) | TikTok comment evidence; already folded into the 595-video report. |
| `ugc-formats-2026/report.md` | UGC video formats, hooks and angles that work for consumer apps in 2026, from every 2026 post of 31 X UGC-teaching accounts plus 15K Reddit posts; where to start, why each works, examples. |
| `android-vs-iphone-tiktok.md` | Whether Android phones are fine for TikTok slideshow accounts (2026-10-04): operator claims, strength of each, what holds up. |

Not yet imported, still in the archive: the three TikTok photo-mode hunts `data/tt-hunt-gym-consistency/`, `data/tt-hunt-fat-loss/`, `data/tt-hunt-dream-body/` (report, `posts.json`, slide images).

## Adding research

Follow `core/workflows/research-competitors.md` or the matching `core/skills/*-research` skill. Every report keeps its source URLs, capture date, region and coverage limits; a blocked or failed scraper is not complete coverage.
