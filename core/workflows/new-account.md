# New account

Ordered steps for adding a TikTok account and its character.

1. **Name it.** Folder names are lowercase: `accounts/<name>/`.
2. **Write `accounts/<name>/account.md`** in the same format as the existing accounts: the `lint-names` comment (every name and signature prop that must never appear in universal files), `## Audience`, `## Character`, `## Voice`, `## Assets`.
3. **Design the character.** Collect inspiration with `core/skills/tiktok-research/SKILL.md`, digest the looks with `core/skills/style-clone/SKILL.md`, and write casting prompts with `core/skills/image-prompt/SKILL.md`. Generate options one at a time at the lowest quality and let the captain pick. Record rejected options and the reason in the Character section as "Don't … Why: …".
4. **Lock the look.** Copy the approved reference images into `accounts/<name>/assets/` (gitignored) and list them in `accounts/<name>/assets.md`.
5. **Give her props of her own.** Check the other accounts' Character sections so she doesn't share a signature prop, hair or phone case with another character.
6. **Join a section.** For each section the account posts in, create `sections/<section>/accounts/<name>/README.md` with `## Overrides` (usually "None") and `## Decks` (or that section's equivalent).
7. **Run `scripts/lint`.** It reads the new `lint-names` and fails if any universal file mentions them.
