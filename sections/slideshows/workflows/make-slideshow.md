# Make a slideshow

The ordered path from the captain's ask to finished decks he can judge. Every step names the skill that does it; the rules live in those skills and in `sections/slideshows/rules.md`.

## Inputs

- The account name, and the titles or topics the captain wants.
- The account's `accounts/<name>/account.md` and `sections/slideshows/accounts/<name>/README.md` (its overrides of the house rules).

## Where deck files go

`sections/slideshows/accounts/<name>/decks/NN-slug/`:

- `script.md`: the script from write-script.
- `review.md`: the script reviewer's verdicts, then the image reviewer's verdict per slide.
- `log.md`: the build log. Per slide: the reference (URL and slide), the prompt text, model and size, number of rolls and cost, each review result and fix, and the final image path.

Downloads and trial rolls stay in `raw/`. After approval, copy final media into the deck's gitignored `assets/` folder and list them with source/prompt/roll provenance in its tracked `assets.md`. Record final and posted status without guessing publication from a local build.

## Steps

1. **Confirm scope.** Tell the captain the exact number of decks and list them (account, title or topic, format), and wait for his go (`H-scope-confirm`). If he switches the account mid-task (from one account to another), restart from this step for the new account: re-read its `accounts/<name>/account.md` and `sections/slideshows/accounts/<name>/README.md`, re-confirm scope, and build under `sections/slideshows/accounts/<new-name>/decks/` — never reuse the old account's deck folder, script or generated images. Why: the account's character, audience and overrides change every slide's script and image; carrying them across accounts produces the previous character in the new account's deck.
2. **Pick angle, hook and format.** If the captain gave no topic, pick an angle from "Future angles" in `sections/slideshows/hook-bank.md` and rotate through them so an account doesn't repeat one back to back. Then run `sections/slideshows/skills/hooks-and-formats/SKILL.md` for each deck.
3. **Write the script.** Run `sections/slideshows/skills/write-script/SKILL.md`. One deck folder per deck.
4. **Review the script.** Run `sections/slideshows/skills/review-script/SKILL.md` yourself, in the same session that wrote the script; never spawn a subagent or new session for it. Why: a separate reviewer re-reads every rule file and wastes too many tokens (captain, 2026-09-24). Fix every FAIL and review again until `review.md` says `VERDICT: PASS`.
5. **Captain review of the scripts.** Show him the passed scripts. Apply his changes to his words exactly (`H-captain-copy-final`), then re-run step 4 on anything that changed.
6. **Build each image slide.** Receipt slides use the files named in `sections/slideshows/assets.md`. The last slide is built like any other, then gets the App Store bar (`H-cta-last-slide`). For every other slide, in order:
   1. **Find the reference.** One real organic gym or fitness photo (`H-gym-pictures`), not one matched to the slide's text (a real post in the niche; never reuse a reference across slides or decks), inside the deck's one look (`H-one-look`). Fetch it into `raw/`.
   2. **Authorize spend.** Before submitting anything, apply the spend gate in `core/skills/reference-swap/SKILL.md` and record the deck approval, image count and stated cost.
   3. **Swap.** Apply `core/skills/reference-swap/SKILL.md` to one image at a time, with the master reference on person slides. Use the authorized outfit/prop modifications; a no-person image still starts from a real reference. Apply the section's picture rules.
   4. **Review the image.** Run `core/skills/review-images/SKILL.md` yourself, in the same session, with the reference beside the image (same reason as step 4). Roll again or apply the reviewer's fix line (never an edit on a generated image) until the slide holds a written PASS.
   5. **Add the text overlay.** Put the slide's on-screen text on the passed image exactly as the script has it.
7. **Show the captain.** One page with one row per deck. Each row shows every slide image with its on-screen text below it. Never show references, prompts or review sheets. Why: he judges the finished slide; references and reviews are worker material.
8. **Take his feedback.** Fix the affected slides from the step they belong to, and note what changed in that deck's `review.md`. Nothing else changes. When the captain says "make universal", run `core/skills/make-universal/SKILL.md`, which writes the correction into the skill, rules file or account file that caused it.
9. **Finish and prepare handoff.** After his OK, run `core/skills/ugc-finish/SKILL.md`, record the compression route and output manifest, and update the account work index. Use only the finished files for an authorized handoff. Publication and account sends are separately authorized under `AGENTS.md`.
