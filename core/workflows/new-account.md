# New account

Ordered steps for adding a TikTok account and its character.

1. **Name it.** Folder names are lowercase: `accounts/<name>/`.
2. **Write `accounts/<name>/account.md`** in the same format as the existing accounts: the `lint-names` comment (account-specific identifiers excluded from universal files), `## Audience`, `## Character`, `## Voice`, `## Assets`.
3. **Make her master reference.** Get the captain's broad description (age, looks, hair, skin). Pick a real close-up photo of one girl that fits the account's world (big clear face, natural hands, no caption) and swap in the new person with `core/skills/reference-swap/SKILL.md`, describing her in one plain sentence. Roll it and let the captain pick. Record rejected options and the reason in the Character section as "Don't … Why: …".
4. **Lock the look.** Copy the approved reference images into `accounts/<name>/assets/` (gitignored) and list them in `accounts/<name>/assets.md`.
5. **Record the approved identity.** Inspect the master reference and write its Identity line alongside the Body and Makeup lines. Keep characters visually distinct; choose accessories per scene rather than assigning mandatory signature props.
6. **Join a section.** For each section the account posts in, create `sections/<section>/accounts/<name>/README.md` with `## Overrides` (usually "None") and `## Decks` (or that section's equivalent).
7. **Run `scripts/lint`.** It reads the new `lint-names` and fails if any universal file mentions them.

## Handles and platform accounts

Record existing platform accounts before planning additions, and keep those accounts. Checking a cleaner handle does not authorize renaming an existing account.

Display names use the captain's approved character name. For usernames, try the bare name first, then underscores or periods before or after the complete name where the platform allows them, including doubled underscores. If needed, add the complete word `fitness`; a separator may go between the full name and the full word. Use no numbers or product-brand wording.

Never insert punctuation inside a name or word. Why: the captain wants names and words readable and explicitly rejected splitting them in the middle (2026-10-08). If a platform forbids leading or trailing separators, use a valid arrangement of complete words instead.

Record the live validator result, source and check date. An accepted draft is not a reserved username or a created account.
