# Make a slideshow

The ordered path from the captain's ask to finished decks he can judge. Every step names the skill that does it; the rules live in those skills and in `sections/slideshows/rules.md`.

## Inputs

- The account name, and the titles or topics the captain wants.
- The account's `accounts/<name>/account.md` and `sections/slideshows/accounts/<name>/README.md` (its overrides of the house rules).

## Where deck files go

`sections/slideshows/accounts/<name>/decks/NN-slug/`:

- `script.md`: the script from write-script.
- `review.md`: the script reviewer's verdicts, then the image reviewer's verdict per slide.
- `log.md`: the build log. Per slide: reference fetched, style digest, prompt file, model and settings, calls and cost, each review result and fix, and the final image path.

Reference images and generated images stay out of git, in `raw/` (gitignored). `log.md` records where each one is.

## Steps

1. **Confirm scope.** Tell the captain the exact number of decks and list them (account, title or topic, format), and wait for his go (`H-scope-confirm`).
2. **Pick hook and format.** Run `sections/slideshows/skills/hooks-and-formats/SKILL.md` for each deck.
3. **Write the script.** Run `sections/slideshows/skills/write-script/SKILL.md`. One deck folder per deck.
4. **Review the script.** Run `sections/slideshows/skills/review-script/SKILL.md` in a separate session. Fix every FAIL and review again until `review.md` says `VERDICT: PASS`.
5. **Captain review of the scripts.** Show him the passed scripts. Apply his changes to his words exactly (`H-captain-copy-final`), then re-run step 4 on anything that changed.
6. **Build each image slide.** Skip the CTA slide and receipt slides; they use the files named in `sections/slideshows/assets.md`. For every other slide, in order:
   1. **Style clone.** Fetch the slide's organic reference into `raw/` and digest its style with `core/skills/style-clone/SKILL.md`.
   2. **Image prompt.** Write the JSON prompt with `core/skills/image-prompt/SKILL.md`, applying `sections/slideshows/rules.md`, `sections/slideshows/image-rules.json`, and the account's `account.md` for the character.
   3. **Generate.** Follow the generation section of the image-prompt skill: lowest quality, one image at a time, spend approval before any paid call.
   4. **Review the image.** Run `core/skills/review-images/SKILL.md` in a separate session with the reference beside the image. Regenerate or edit with the reviewer's fix line until the slide holds a written PASS.
   5. **Add the text overlay.** Put the slide's on-screen text on the passed image exactly as the script has it.
7. **Show the captain.** One page with one row per deck. Each row shows every slide image with its on-screen text below it. Never show references, prompts or review sheets. Why: he judges the finished slide; references and reviews are worker material.
8. **Take his feedback.** Fix the affected slides from the step they belong to, and note what changed in that deck's `review.md`. Nothing else changes. When the captain says "make universal", run `core/skills/make-universal/SKILL.md`, which writes the correction into the skill, rules file or account file that caused it.
