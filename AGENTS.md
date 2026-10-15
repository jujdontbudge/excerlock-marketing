# ExcerLock Marketing

Marketing research, creative production and creator operations for ExcerLock, an app that blocks the apps a user picks until they walk, hit a step goal or go to the gym. The app lives in a separate repository; the creator operations system lives here (see `docs/adr/0005-creator-system-is-code.md`).
"The captain" is the owner. His rules and reviews override agent judgment and older research.
Words used here are defined in `CONTEXT.md`. Why the repo is shaped this way: `docs/adr/`.

## Where to start
| Task | Start at |
|---|---|
| Make or change a slideshow | `sections/slideshows/README.md`, then `sections/slideshows/workflows/make-slideshow.md` |
| Creator-recorded UGC or the current creator brief | `sections/real-ugc/README.md` |
| Finding, contacting, signing or tracking creators and influencers | `sections/creators/README.md` |
| Automatic replies to incoming messages: add, change or turn off a rule | `sections/inbox/README.md` |
| What creators are told: deal, FAQ answers, video quality bar | `core/creator-knowledge/README.md` |
| Anything about one account's character, voice or audience | `accounts/<name>/account.md` (accounts: `zoey`, `hayden`) |
| Research competitors, TikTok posts, ads or videos | `core/workflows/research-competitors.md` and the `core/skills/*-research` skills |
| Any image with a person in it, image review, video | `core/skills/reference-swap/`, `review-images/`, `fal-video/` |
| What the app does | `core/product.md` |
| Existing research | `research/README.md` |
| Add an account or a new kind of marketing work | `core/workflows/new-account.md`, `core/workflows/new-section.md` |

Every skill is a folder with a `SKILL.md`. `scripts/link-skills` links them all into `.claude/skills/` (Claude Code) and `.agents/skills/` (Pi and Hermes; both need the repo trusted).

## Rules
- **Modules.** `sections/<name>/` is one kind of work and can be deleted on its own. A section may use `core/`, `accounts/` and `research/`; `core/` never names a section or an account; sections never name each other. Account-specific material lives only in `accounts/<name>/` and `sections/<section>/accounts/<name>/`.
- **Build on the operations system.** Every agent must read `sections/creators/README.md` before starting new work. For every new task, explicitly suggest a concrete way to extend or connect to its dashboard, approval inbox, scheduled jobs or performance feedback, so the captain has one visible system with less manual work. Reuse existing capabilities before adding parallel trackers. Use deep modules: each owns its data and decisions behind a small interface; connect through explicit adapters or a composition layer outside the sections, preserving the Modules rule above. When connecting would add needless coupling, explain why and suggest an independent module with a clear future interface.
- **One home per rule.** Every rule is written once, with its reason, and linked everywhere else. Where two files disagree, fix the one that's wrong instead of adding a third.
- **Authority.** The current captain assignment wins; then the canonical product/creative rules and explicit section overrides. Research, logs, memories and `history/` are evidence, not live instructions. Verify a recalled decision against its canonical home before acting.
- **Prompting agents.** Before writing an agent brief or a skill, make sure you understand the captain's goal and intent. In the brief, state the goal and the required output separately from any examples he gave. Examples show what he means; they are not the output and not a template. Why: an agent given an example without the goal behind it copies the example.
- **Captain feedback.** Fix the thing in front of you. When he says "make universal", follow `core/skills/make-universal/SKILL.md`.
- **Writing to creators.** Anything a creator reads (messages, briefs, guides, agreements) follows `core/writing-to-creators.md`: talk to them as "you", warm and short like a friend, say why it helps them, only what they need. Why: the captain approved this voice and creators are our friends, not readers of internal notes (2026-10-14).
- **Creator knowledge.** Facts, approved answers and the video quality bar for the creator program live in `core/creator-knowledge/`. Whenever the captain answers a creator question or changes a creator-facing term, record it there before you finish (its README says how). Why: the inbox automation answers from it, and each answer he gives should only ever be needed once (2026-10-14).
- **Automated messages: zero room for error.** Automation may send only the message types the captain explicitly approved, each switchable off on its own in one step (`sections/inbox/README.md`). Before every send, reread the creator's whole conversation live from the source (never a cached copy) and send nothing if she already did the thing, has an unanswered question, or anything is unclear. If she is waiting on the captain and no approved automation covers it, wait for him. When in doubt while building or running one, grill the captain (`mattpocock-skills:grilling`) instead of guessing. Why: on 2026-10-14 reminders went to creators who had already signed, because "pending" in SideShift was read as "unsigned".
- **Building or expanding automation.** Before shipping, list the ways it can go wrong and test each one in isolation with fakes, never against real people: states that look like one thing but mean another, stale or partial data, messages the captain sent by hand, duplicates and retries, unanswered questions, timing and time zones, scale to hundreds of creators. Be skeptical of every source field until a real example proves what it means. Give the automation as much context as possible, but make the action itself checked and narrow.
- **Money and publishing.** Ask before publishing, launching campaigns or changing budgets. Paid image authorization and limits live in `core/skills/reference-swap/SKILL.md`; check them before submitting a request.
- **Files.** Downloads and scratch go in `raw/` (gitignored). Real images go in the gitignored `assets/` folders and are listed in the tracked `assets.md` beside them.
- **Before finishing:** run `scripts/lint`. After adding, renaming or removing a skill, run `scripts/link-skills`.

## Archive
Old work not yet in this repo is at `~/firstmate-decommission-backup-2026-09-23-v2/quarantine-firstmates/excerlock-marketing-firstmate/data/`; `data/...` paths in any file point there. It holds the three TikTok photo-mode hunts (`tt-hunt-gym-consistency`, `tt-hunt-fat-loss`, `tt-hunt-dream-body`: reports, `posts.json`, slide images), deck image builds, Hayden's character options and `captain.md`. Read from it freely; ask before moving anything, and never open `account-credentials.md` or `gemini-api-key`.

## Environment
- Python tools run from `.venv/bin/`; keys live in `.env` (never print them).
- The Gemini API key in `.env` is for image generation only (`core/skills/reference-swap/swap.py`). Photo analysis, cataloguing, scoring and script drafting use the captain's Gemini subscription (the `gemini` CLI) or Claude agents, never the API key. Why: the captain pays per API call and only wants that spend on images (2026-10-04).
- Pi sessions (`pi-marketing`) add the project browser (`BROWSER.md`), Jina web tools and local Mem0 memory (`integrations/mem0-local/README.md`).
- Integration tests are listed in `integrations/*/README.md` and `tools/rich-md/README.md`.

## Maintaining this file
Keep it to what nearly every session needs. Point to the file that owns a fact instead of repeating it. Prune before adding.
