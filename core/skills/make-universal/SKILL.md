---
name: make-universal
description: Turn the captain's feedback into a permanent rule in the file that caused the behaviour. Use whenever the captain corrects a script, image or other output and says "make universal".
---

# Make universal

The captain gives a correction plus the reason, then says **make universal**. You write it once, into the file that produced the mistake, so no agent repeats it.
Without those words, fix only the thing in front of you and save nothing.

## 1. Find the file that caused it

| The mistake is in | And it applies to | Write it into |
|---|---|---|
| Script text, slide order, tip choice | every account | the section's writing skill (its `README.md` names it) |
| The hook or the format | every account | the section's hook or format skill |
| A house rule for the whole section (slide count, CTA, copy voice) | every account | `sections/<section>/rules.md` |
| How an image looks | every account | `core/skills/review-images/SKILL.md` (a check), plus `core/skills/image-prompt/SKILL.md` if the prompt caused it |
| A style digest | every account | `core/skills/style-clone/SKILL.md` |
| Her face, body, props, voice or audience | one account | `accounts/<name>/account.md` |
| How one account's decks differ from the house rules | one account | `sections/<section>/accounts/<name>/README.md` (`## Overrides` or its account rules) |

If the correction names one account's character or props ("her eyes are always blue-grey"), it's account-level: it never goes in a universal file. If it names an account but the lesson is general ("she had another account's phone case"), write the general version into the universal file ("Don't give a character a prop from another account's character") and nothing account-specific.
If you can't tell which file, ask the captain before writing.

## 2. Write it in that file's form

- **Skills that produce things** (write-script, hooks-and-formats, image-prompt, style-clone) and account Character sections: a negative with the reason, under `## Don'ts`.
  `- Don't put two tips on one slide. Why: <the captain's reason>.`
- **Review skills** (review-script, review-images): a check with pass, fail and reason.
  `- **One tip per slide.** Pass: each value slide gives one tip. Fail: two or more. Why: <reason>.`
- **Rules files** (`rules.md`, `## Overrides`): the rule plus `Why:`, under its ID.

Use the captain's reason in his own words. A rule without a reason doesn't go in.

## 3. Keep one home per rule
- If the new rule contradicts an existing one, replace the old one. Never leave both.
- If it repeats an existing rule, sharpen that one instead of adding a copy.
- Other files link to the rule; they never copy it.

## 4. Push it up the ladder when you can
If the rule is mechanical (a word, prop or field that must never appear), also add it to the section's checker rules (`sections/<section>/image-rules.json`, read by `core/skills/image-prompt/check.py --rules`), so the mistake fails automatically.

## 5. Finish
Run `scripts/lint`, then tell the captain the exact file and the line you added or replaced.
