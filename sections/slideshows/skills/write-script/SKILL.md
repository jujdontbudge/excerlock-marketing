---
name: write-script
description: Writes one slideshow deck script (on-screen text, one organic reference and our variation per slide) for a given account and title or topic. Use after the scope is confirmed and a hook and format are chosen, before any image work.
---

# Write a slideshow script

## Inputs

- The title (the captain's hook) or, if there is no title yet, the topic.
- The account's `accounts/<name>/account.md` (audience, character, voice) and `sections/slideshows/accounts/<name>/README.md` (overrides, banned sources, account notes).
- `sections/slideshows/rules.md`: the house rules. An override in the account README replaces the rule it names.
- The hook and format from `sections/slideshows/skills/hooks-and-formats/SKILL.md`.
- `sections/slideshows/assets.md`: the CTA blocker screen and the proof receipts. The account's `accounts/<name>/assets.md` may add its own.

## Output

`sections/slideshows/accounts/<name>/decks/NN-slug/script.md`. `NN` is the next free deck number for that account; `slug` is a few words of the title.

## Steps

1. **Check scope.** Write only the decks in the list the captain confirmed (`H-scope-confirm`).
2. **Read the title's frame.** It decides how every value slide is phrased:
   - "how i ..." gives the reasons and ways the narrator does it.
   - "why you're not ..." gives "your doing X, do Y instead" or "instead of X do Y".
   - "want X but ..." gives "this is what i did".
3. **Find the copy.** Collect value tips from the post bank (`data/slideshow-accounts-web`) and fresh TikTok or Instagram research (`core/skills/tiktok-research/SKILL.md`). Compare several complete recent winning decks and read the audience's comments for their wording. Note each post's URL, account, slide number and observed numbers with the capture date.
4. **Build the deck, 5 to 7 slides** (`H-slide-count`):
   - **Slide 1, hook.** The captain's title, as written (`H-captain-copy-final`). With only a topic, pick a hook with hooks-and-formats and get the captain's OK before writing the rest. The picture is an aesthetic shot of the account's world that stops the scroll, as the account README describes.
   - **Slide 2, proof.** A second reason to swipe: a receipt from `assets.md`, a before picture, or a real proof photo. Short, casual text ("heres proof", "and i KNOW what im talking about", "but then i remembered how i was"). It may end with a short pointer line ending in `>>>`.
   - **Slide 3, value.** The single most helpful tip for the title's promise, one piece only (`H-no-cheat-sheet`). Copy it word for word from a value slide of a high-performing post where one exists.
   - **Slide 4, CTA** (`H-cta-slide-4`). One friendly aside naming the product: "use excerlock to ...", "use an app like excerlock ...", "excerlock blocks ...", or the captain's exact text. Lowercase, exclamation marks and small typos are fine. The image is the blocker screen named in `sections/slideshows/assets.md`, unedited, full frame.
   - **Slides 5 to 7, value.** More tips in the same frame, each a different piece, each copied where a source exists. Value after the CTA keeps the CTA an aside instead of the point.
   - **Last slide, payoff.** Only if it adds something: a genuinely intriguing statistic, a rehook or a resolve. Otherwise the deck ends on its last value slide.
5. **Write each slide entry** in this shape:

   ```
   ## Slide N (hook | proof | value | CTA | payoff)
   - Text: <on-screen text, exactly as it will appear>
   - Copy source: <captain's words | URL, account, slide number, observed numbers, capture date>
   - Reference: <exactly one organic photo: URL, account, slide number, what it shows, plays and saves as observed on the capture date>
   - Variation: <our picture: the scene placed in the reference's style with the account's character, or the named asset from assets.md>
   ```

   The CTA slide's Reference and Variation both name the blocker screen from `assets.md` and nothing else.
6. **Add the deck summary** at the top of the file: title, account, frame, slide count, face count, screenshot count (CTA excluded), and a one-line retell a 13-year-old would give.
7. **Run the self-check** below, fix what fails, then hand the script to `sections/slideshows/skills/review-script/SKILL.md` in a separate session.

## Self-check

1. Read the title, then only the value slides. Does each one literally deliver the title's promise, in the title's frame?
2. Is slide 2 short, casual and a reason to swipe?
3. Is every value slide a real tip from a real post's value slide (or the captain's words), cited under the slide, and one piece only?
4. Is the CTA on slide 4, one aside in an allowed form, with the blocker screen as its image?
5. Do slide lengths vary on purpose (a two-word slide next to a full tip)?
6. Could a 13-year-old retell the deck slide by slide, and does each slide make sense alone?
7. At most 2 faces, each with an exact organic reference? At most 2 screenshots, CTA excluded? One reference per slide, none reused across slides or decks?
8. Do all house rules in `sections/slideshows/rules.md` hold, with the account's overrides applied?

## Don'ts

The house rules in `sections/slideshows/rules.md` also apply; they are not repeated here.

### Copy

- Don't put a statistic or a mood line on a value slide. Why: the reader came for reasons and a statistic is not one; mood slides save at 7.4 per 1k while light tips save at 36.5.
- Don't use a statistic anywhere except as a payoff, rehook or switch-up, and then only one the reader can apply to their own life. Why: the compounding "10,000 steps a day is 3,650,000 a year" deck reached 1.5M views, while lecture statistics all sit under 50K. The number lands; the lecture doesn't.
- Don't go from the hook straight into the tips. Why: "text on slide 1, picture that proves it on slide 2" is the highest-view shape in the corpus (median 442,550 views), and the proof early keeps the tips after it believable.
- Don't write vague or invented tips. Why: tips with one concrete action and a line of why save at 45.7 per 1k, and a tip that already went viral has already been tested on this reader.
- Don't copy a hook slide's text into a value slot. Why: a hook line standing alone in the middle of a deck makes no sense; value text must come from a value slide.
- Don't copy from one viral first slide alone. Why: the hook doesn't show the mechanism; several complete winning decks and the audience's comments do.
- Don't copy from a source the captain banned. Why: it is his call; the account README lists banned sources.
- Don't phrase a value slide outside the title's frame. Why: the reader was promised reasons, fixes or a story by the title, and the corpus keeps instructions in the second person and proof in the first.
- Don't write the CTA as ad copy or with "i use excerlock" as the frame. Why: a product slide written like the free slides saves at 95.8 per 1k while slogan wording saves at 0.6 to 1.2, and the brand's own first person is the weaker voice.
- Don't make every slide the same length or shape. Why: the 1M+ view tier is 1 to 3 word slides and the high-save tier is 15-word slides; a deck that mixes both gets both, and the break is where the reader feels the deck land.
- Don't put two slides in one deck that say the same thing, even in a different place or words. Cut one and shorten the deck. Why: redundancy is the number one AI tell.
- Don't write parentheticals in on-screen text. The only brackets are the captain's own. A needed aside is its own short line with "!!", in at most one deck of a batch. Why: agent-written brackets read as AI.
- Don't end on a filler slide (a rule, a mood line, a summary that adds nothing). Why: a slide that adds nothing is the slide where the viewer leaves.

### Pictures and references

- Don't open on a low-energy picture (a phone in bed) or anything outside the account's world. Why: the hook picture is what stops the scroll.
- Don't use anything but real proof on the proof slide. Why: a fake or decorative proof breaks the trust the rest of the deck spends.
- Don't pair "how i was" or before copy with a steps or stats screenshot. Why: that copy reads as a before picture of the person; a chart there breaks the story.
- Don't use a different receipt per deck, and don't edit or crop one beyond what the layout needs. Why: one real receipt across all decks keeps the account consistent and believable.
- Don't write a new image for the CTA slide. Why: the one blocker screen in `assets.md`, on every deck, is the product itself and keeps the CTA consistent.
- Don't use more than 2 face photos. After two, use a faceless scene that fits the tip. Why: more faces read as a staged shoot.
- Don't use a face photo without an exact organic reference behind it. Why: all-AI, visually perfect images read as ads; a digested real photo keeps the imperfections that make it organic.
- Don't use more than 2 screenshots per deck (the CTA does not count). Why: a deck of screenshots stops looking like a person's photos.
- Don't put a random aesthetic photo under a tip. The picture must show the tip's message. Why: the picture is the context a 13-year-old reads before the words; a mismatch makes the slide make no sense.
- Don't close on a staged or app-made picture. Why: the last picture is the one that sits under the comments and the share.
- Don't reuse a reference photo across slides or decks. Only the receipts and the CTA screen repeat. Why: repeats look templated, and a templated deck reads as an ad.
- Don't give alternates or backups. Exactly one reference per slide. Why: the captain won't choose between options; picking is the writer's job.
