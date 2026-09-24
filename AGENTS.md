# ExcerLock Marketing

Marketing research and creative production for ExcerLock, an app that blocks the apps a user picks until they walk, hit a step goal or go to the gym. The app lives in a separate repository; nothing here ships software.
"The captain" is the owner. His rules and reviews override agent judgment and older research.
Words used here are defined in `CONTEXT.md`. Why the repo is shaped this way: `docs/adr/`.

## Where to start
| Task | Start at |
|---|---|
| Make or change a slideshow | `sections/slideshows/README.md`, then `sections/slideshows/workflows/make-slideshow.md` |
| Anything about one account's character, voice or audience | `accounts/<name>/account.md` (accounts: `zoey`, `hayden`) |
| Research competitors, TikTok posts, ads or videos | `core/workflows/research-competitors.md` and the `core/skills/*-research` skills |
| Image prompts, style digests, image review, video | `core/skills/image-prompt/`, `style-clone/`, `review-images/`, `fal-video/` |
| What the app does | `core/product.md` |
| Existing research | `research/README.md` |
| Add an account or a new kind of marketing work | `core/workflows/new-account.md`, `core/workflows/new-section.md` |

Every skill is a folder with a `SKILL.md`. `scripts/link-skills` links them all into `.claude/skills/` (Claude Code) and `.agents/skills/` (Pi and Hermes; both need the repo trusted).

## Rules
- **Modules.** `sections/<name>/` is one kind of work and can be deleted on its own. A section may use `core/`, `accounts/`, `library/` and `research/`; `core/` and `library/` never name a section or an account; sections never name each other. Account-specific material lives only in `accounts/<name>/` and `sections/<section>/accounts/<name>/`.
- **One home per rule.** Every rule is written once, with its reason, and linked everywhere else. Where two files disagree, fix the one that's wrong instead of adding a third.
- **Captain feedback.** Fix the thing in front of you. When he says "make universal", follow `core/skills/make-universal/SKILL.md`.
- **Money and publishing.** Ask before publishing, launching campaigns, changing budgets or any paid generation beyond the lowest-quality single images the image-prompt skill allows.
- **Files.** Downloads and scratch go in `raw/` (gitignored). Real images go in the gitignored `assets/` folders and are listed in the tracked `assets.md` beside them.
- **Before finishing:** run `scripts/lint`. After adding or renaming a skill, run `scripts/link-skills`.

## Archive
Old work not yet in this repo is at `~/firstmate-decommission-backup-2026-09-23-v2/quarantine-firstmates/excerlock-marketing-firstmate/data/`; `data/...` paths in any file point there. It holds the three TikTok photo-mode hunts (`tt-hunt-gym-consistency`, `tt-hunt-fat-loss`, `tt-hunt-dream-body`: reports, `posts.json`, slide images), deck image builds, Hayden's character options and `captain.md`. Read from it freely; ask before moving anything, and never open `account-credentials.md` or `gemini-api-key`.

## Environment
- Python tools run from `.venv/bin/`; keys live in `.env` (never print them).
- Pi sessions (`pi-marketing`) add the project browser (`BROWSER.md`), Jina web tools and local Mem0 memory (`integrations/mem0-local/README.md`).
- Integration tests are listed in `integrations/*/README.md` and `tools/rich-md/README.md`.

## Maintaining this file
Keep it to what nearly every session needs. Point to the file that owns a fact instead of repeating it. Prune before adding.
