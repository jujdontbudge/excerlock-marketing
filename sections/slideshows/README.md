# Slideshows

The section that makes organic-looking TikTok photo slideshows for ExcerLock: hook, script, script review, images, image review, text overlay, then the captain's review. It is a cut-out module: it uses `core/`, `accounts/` and `research/`, and no other section depends on it.

Start with `workflows/make-slideshow.md`.

## Files

| Path | What it is |
|---|---|
| `workflows/make-slideshow.md` | The ordered workflow from the captain's ask to finished decks. |
| `rules.md` | The house rules (`H-<id>`) every account follows unless its README overrides one. |
| `hook-bank.md` | The captain's hook ideas. |
| `assets.md` | Shared assets: the CTA blocker screen and the proof receipts. Files live in `assets/` (gitignored). |
| `skills/hooks-and-formats/SKILL.md` | Pick a hook and a deck format. |
| `skills/write-script/SKILL.md` | Write one deck script. |
| `skills/review-script/SKILL.md` | Review a script yourself, right after writing it. |
| `accounts/<name>/README.md` | One account's slideshow notes and its `## Overrides` of house rules. |
| `accounts/<name>/decks/NN-slug/` | One deck: `script.md`, `review.md`, `log.md`. |

## Core skills it uses

- `core/skills/reference-swap/SKILL.md`: copy a real organic photo and swap in the character.
- `core/skills/review-images/SKILL.md`: review each generated image.
- `core/skills/tiktok-research/SKILL.md`: find posts to copy tips and references from.
- `core/skills/ugc-finish/SKILL.md`: grain, 1080p and one compression round on every final slide before upload.
- `core/skills/make-universal/SKILL.md`: turn a captain's correction into a universal rule when he says "make universal".

Who each account is (audience, character, voice) lives in `accounts/<name>/account.md` at the repo root, not here.
