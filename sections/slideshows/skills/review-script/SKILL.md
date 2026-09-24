---
name: review-script
description: Reviews one slideshow deck script against the house rules and the writing skill, in a separate session from the writer, and writes a pass or fail verdict per check. Use after write-script and before the script goes to the captain.
---

# Review a slideshow script

You are a separate reviewer. You did not write this script. Assume it is wrong until each check proves otherwise: your job is to find the fault, not to confirm the pass.

## Inputs

- The deck's `sections/slideshows/accounts/<name>/decks/NN-slug/script.md`.
- The account's `accounts/<name>/account.md` and `sections/slideshows/accounts/<name>/README.md`. Apply the account's character and voice, and its `## Overrides`: an override replaces the house rule it names.
- `sections/slideshows/rules.md` (house rules) and `sections/slideshows/skills/write-script/SKILL.md` (structure and Don'ts).
- `sections/slideshows/assets.md` and the account's `accounts/<name>/assets.md` (the CTA screen and receipts).
- The other decks in the same batch and the account's earlier decks, for the cross-deck checks.

## Steps

1. Run every check below on the script. Quote the slide text or line you judged.
2. Write the verdict to the deck's `review.md`: one line per check, `OK` or `FAIL: <what> -> fix: <one-line fix>`, then `VERDICT: PASS` or `VERDICT: FAIL`.
3. PASS only when every check is OK. A failed check is a rewrite, not a note. The writer fixes it and sends it back to a reviewer who runs every check again.

## Rules for the review

- The writer never grades its own script and never marks PASS. Why: the maker cannot see its own mistakes.
- If the reviewer session dies or hits a limit, start a new reviewer session and wait. Why: a script passed by its own writer is not reviewed.
- Don't comment on the captain's own words beyond checking they are verbatim (`H-captain-copy-final`). Why: his copy is final.

## Checks

### Promise and story

- **Title promise.** Pass: read the title, then only the value slides; each one literally delivers what the title promised, in the title's frame ("how i" gives ways, "why you're not" gives "your doing X, do Y instead", "want X but" gives "this is what i did"). Fail: a value slide is a statistic, a mood line, or phrased outside the frame. Why: the reader came for what the title promised and saves what they can do.
- **Hook verbatim.** Pass: slide 1 is the captain's title exactly as he wrote it. Fail: any change in words, spelling, case or punctuation. Why: `H-captain-copy-final`.
- **Second pull.** Pass: slide 2 is short, casual and a reason to swipe (a receipt, a before picture, real proof). Fail: slide 2 is a tip, a long line, or decorative proof. Why: the proof on slide 2 is the corpus's highest-view shape and makes the tips after it believable.
- **One story.** Pass: a 13-year-old could retell the deck slide by slide, each slide answers "and then what?", and the product moment is set up before and paid off after. Fail: a jump, a slide that could be moved anywhere, or a list of loose tips. Why: `H-one-story`.
- **Standalone slide.** Pass: each slide read alone, with no other slide, still makes sense. Fail: a slide that needs another slide to be understood, such as a hook line in a value slot. Why: a line standing alone that makes no sense is where the viewer leaves.
- **Last slide.** Pass: the deck ends on a value slide, real proof, or a payoff that adds something, over an organic picture. Fail: a rule, mood line or summary that adds nothing, or a staged or app-made picture. Why: a slide that adds nothing is where the viewer leaves, and the last picture sits under the comments and the share.

### Value

- **Real tips.** Pass: every value slide is a tip from a real post's value slide (or the captain's words), copied word for word where a source exists, with its source cited under the slide. Fail: an invented or vague tip, an uncited tip, or text taken from a hook slide. Why: a copied tip has already been tested on this reader and carries the niche's dialect.
- **One piece.** Pass: each value slide gives one piece that solves part of the problem. Fail: a list, a cheat sheet, a Notes screenshot, or a slide that covers the whole day or the whole process. Why: `H-no-cheat-sheet`.
- **No repeats.** Pass: every slide says something different. Fail: two slides that say the same thing in different words or places. Why: redundancy is the number one AI tell.
- **Banned sources.** Pass: no copy or picture from a source banned in the account README. Fail: any use of one. Why: the captain banned it.
- **Statistics.** Pass: a statistic appears only as a payoff, rehook or switch-up, and one the reader can apply to their own life. Fail: a statistic on a value slide, or a lecture statistic. Why: the number lands; the lecture doesn't.

### CTA

- **CTA slot and form.** Pass: the CTA is slide 4, one aside in "use excerlock to ...", "use an app like excerlock ...", "excerlock blocks ..." form or the captain's exact text. Fail: another slide number, ad or slogan wording, or "i use excerlock" as the frame. Why: `H-cta-slide-4`, and slogan wording saves at 0.6 to 1.2 per 1k against 95.8 for an aside.
- **CTA image.** Pass: the CTA slide's picture is the blocker screen named in `sections/slideshows/assets.md`, unedited, full frame, with no other image note. Fail: any other image or a new image written for it. Why: one blocker screen on every deck keeps the CTA consistent.

### Copy and voice

- **Voice.** Pass: flat human statements in the account's voice, very few words per slide, no em dashes, no metaphors, analogies, sayings or clever contrast lines, lowercase and casual where the account voice is lowercase. Fail: any of those. Why: `H-copy-voice`.
- **Captain's copy.** Pass: every line the captain wrote (title, slide text, CTA) appears verbatim. Fail: any paraphrase, shortening or normalising. Why: `H-captain-copy-final`.
- **Varied lengths.** Pass: slide lengths vary on purpose (a two-word slide next to a full tip). Fail: every slide the same length and shape. Why: a deck that mixes short and long slides gets both views and saves.
- **Brackets.** Pass: the only brackets in on-screen text are the captain's own, and at most one "!!" aside line appears across the whole batch, in one deck. Fail: any agent-written bracket, or a second "!!" aside. Why: agent brackets read as AI.
- **Number progress.** Pass: numbers appear only inside real screenshots and in a tip's own setting (speed 3, incline 12, 30 minutes). Fail: "from 9k to 15k" or before and after counts in the copy. Why: `H-no-number-progress`.
- **Organic feed.** Pass: the deck as a whole (text, slide count, picture plan, one quiet product slide) would sit unnoticed among organic top-saving decks. Fail: anything that reads as an ad. Why: `H-organic-feed`.

### Shape and references

- **Slide count.** Pass: 5 to 7 slides. Fail: fewer than 5, or 8 or more. Why: `H-slide-count`.
- **One reference per slide.** Pass: exactly one organic reference per slide, with URL, account, slide number, what it shows, and the observed numbers with the capture date. Fail: a missing field, alternates or backups. Why: the captain won't choose between options, and every picture needs a real photo behind it.
- **No reused references.** Pass: no reference photo repeats across slides or across the account's decks, except the receipts and the CTA screen. Fail: any repeat. Why: repeats look templated, and a templated deck reads as an ad.
- **Picture fits the text.** Pass: each slide's reference shows the slide's message, and slide 1's picture is an aesthetic shot of the account's world. Fail: a random aesthetic photo under a tip, or a low-energy hook picture. Why: the picture is what a 13-year-old reads before the words.
- **Faces.** Pass: at most 2 face photos, each with an exact organic reference and a variation that places the account's character in that style. Fail: a third face, or a face with no organic reference. Why: more faces read as a staged shoot, and all-AI faces read as ads.
- **Screenshots and receipts.** Pass: at most 2 screenshots per deck (the CTA excluded); receipts are the ones named in `assets.md`, the same across decks, unedited. Fail: a third screenshot, a different receipt, or an edited one. Why: a deck of screenshots stops looking like a person's photos, and one receipt keeps the account believable.
- **Before copy.** Pass: "how i was" or before copy sits over a before picture. Fail: before copy over a steps or stats screenshot. Why: the copy reads as a before picture of the person; a chart there breaks the story.
- **No watch.** Pass: no Apple Watch or smartwatch in any reference or variation. Fail: any watch. Why: `H-no-watch`.
- **Variation rules.** Pass: each variation keeps the reference's type of place and concept, copies its devices and props 1:1, adds no phone where the reference has none, and takes only the style from the reference, with the person from the account's `account.md`. Fail: a changed place type, an added phone or prop, or a person copied from the reference. Why: `H-place-type`, `H-phone-case`, `H-style-not-identity`.
- **Account rules.** Pass: everything in the account's `account.md` and README (character, voice, overrides, banned sources) holds. Fail: any account rule broken. Why: the account's rules are what make the deck sound and look like that account.
