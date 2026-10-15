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
| `stompers-deep-2026-10/report.md` | Stompers (social walking race app), captured 2026-10-12: company, store/paywall, invite loop, organic TikTok and Instagram, 2024 promoted TikToks, the five Oct 2026 Meta ads, brand-owned and ambassador accounts. |
| `walking-competitors-2026-10/report.md` | 104 walking apps with a hook beyond step counting (rewards, social races, games, betting, walk-to-unlock), sized and ranked by evidenced reach, with socials, Meta-ad status and closeness to Stompers and ExcerLock (2026-10-12). |
| `weward-deep-2026-10/report.md` | WeWard (walking rewards, 30M claimed users), captured 2026-10-12: Walk Mode app blocking (direct ExcerLock overlap) and how it is marketed, company and PR-led growth, rating-walkers TikTok, 395 Meta / 130 Google / 132 Apple ads ranked by EU reach and impressions. |
| `stepup-deep-2026-10/report.md` | StepUp (social step leaderboards), captured 2026-10-12: organizer-led community growth, 193 organic TikToks and 2,002 comments, store/paywall, ads. |
| `pikmin-bloom-deep-2026-10/report.md` | Pikmin Bloom (Scopely), captured 2026-10-12: character-led organic TikTok and Instagram, live-ops events, 428 Meta / 411 Google / 197 Apple ads and which sell walking. |
| `argus-deep-2026-10/report.md` | Argus (Azumio), captured 2026-10-12: near-zero social or paid presence; store, ASO and portfolio cross-promotion. |
| `social-steps-deep-2026-10/report.md` | Social Steps (solo developer), captured 2026-10-12: tiny footprint, three organic TikToks, invite mechanics, no verified ads. |
| `ugc-formats-2026/report.md` | UGC video formats, hooks and angles that work for consumer apps in 2026, from every 2026 post of 31 X UGC-teaching accounts plus 15K Reddit posts; where to start, why each works, examples. |
| `android-vs-iphone-tiktok.md` | Whether Android phones are fine for TikTok slideshow accounts (2026-10-04): operator claims, strength of each, what holds up. |
| `talking-head-2026-10/report.md` | Talking-head UGC synthesis: nine video areas, evidence-separated rankings, scripting/filming/judging, 2026 prices, roster workflow and a future creator-brief section; captured 2026-10-12–13. |
| `low-views-2026-10.md` | Why TikTok posts stall under 50 views (2026-10-14): TikTok's own weight-loss, AI-label and unoriginal-content rules, plus operator advice on warm-up, devices and posting method. |

Not yet imported, still in the archive: the three TikTok photo-mode hunts `data/tt-hunt-gym-consistency/`, `data/tt-hunt-fat-loss/`, `data/tt-hunt-dream-body/` (report, `posts.json`, slide images).

## Adding research

Follow `core/workflows/research-competitors.md` or the matching `core/skills/*-research` skill. Every report keeps its source URLs, capture date, region and coverage limits; a blocked or failed scraper is not complete coverage.
