---
name: review-script
description: Reviews one slideshow deck script against the goal and the house rules, in the same session that wrote it, and writes a pass or fail verdict per check. Use after write-script and before the script goes to the captain.
---

# Review a slideshow script

The agent that wrote the script reviews it in the same session; don't spawn a subagent or new session. Why: a separate reviewer re-reads every rule file and wastes too many tokens (captain, 2026-09-24). Switch from writer to reviewer: forget why you made each choice and assume the script is wrong until each check proves otherwise. Read it as the scroller, not the author.

## Inputs

- The deck's `sections/slideshows/accounts/<name>/decks/NN-slug/script.md`.
- The account's `accounts/<name>/account.md` and `sections/slideshows/accounts/<name>/README.md`.
- `sections/slideshows/rules.md` (house rules) and `sections/slideshows/skills/write-script/SKILL.md`.

## Steps

1. Read the active assignment and record explicit captain-approved exceptions in the deck log. Run every check below against the house rules plus those exceptions. Quote the slide text or line you judged.
2. Write the verdict to the deck's `review.md`: one line per check, `OK` or `FAIL: <what> -> fix: <one-line fix>`, then `VERDICT: PASS` or `VERDICT: FAIL`.
3. PASS only when every check is OK. A failed check is a rewrite, not a note. Fix it and run every check again.

## Checks

- **Promise.** Pass: every non-CTA slide serves the goal behind the title (the outcome she wants), in the title's frame ("how i" gives ways, "why you're not" gives what she's doing wrong plus what to do instead). A slide may come from outside the hook's topic (food, sleep, routine) when it serves that goal. Fail: a slide that doesn't move her toward the outcome, a mood line, or a statistic where a usable tip belongs. Why: the reader came for the result, not the topic; the winning decks mix life areas and save what she can do.
- **No sameyness.** Pass: the value slides come from different parts of her life; no two slides are the same tip in different clothes. Fail: two slides that reduce to the same advice (five "just walk more" variants). Why: repetition is the number one AI tell, and the corpus wins on spread (lunch, gym, car park).
- **Every slide earns it.** Pass: each non-CTA slide entertains or gives something usable; nothing repeats another slide; nothing feels like a pitch. Fail: filler, a repeated point, or a slide that could be cut without loss. Why: a slide that adds nothing is where the viewer leaves.
- **One story.** Pass: a 13-year-old could retell the deck slide by slide, each slide answers "and then what?", and the product moment is set up before and paid off after. Fail: a jump, a slide that could sit anywhere, or a loose list. Why: `H-one-story`.
- **Hook verbatim.** Pass: slide 1 is the captain's title exactly as he wrote it. Fail: any change in words, spelling, case or punctuation. Why: `H-captain-copy-final`.
- **Last slide.** Pass: the ending follows `H-cta-last-slide` or the recorded explicit exception. Review the last value slide for payoff separately from the CTA.
- **Voice.** Pass: flat human statements in the account's voice, very few words per slide, no em dashes, no metaphors, analogies, sayings or clever contrast lines, lowercase and casual where the account voice is lowercase. Fail: any of those. Why: `H-copy-voice`.
- **Captain's copy.** Pass: every line the captain wrote (title, slide text, CTA) appears verbatim. Fail: any paraphrase, shortening or normalising. Why: `H-captain-copy-final`.
- **Varied lengths.** Pass: slide lengths vary on purpose (a two-word slide next to a full tip). Fail: every slide the same length and shape. Why: a deck that mixes short and long slides gets both views and saves.
- **Brackets.** Pass: the only brackets in on-screen text are the captain's own. Fail: any agent-written bracket. Why: agent brackets read as AI.
- **Number progress.** Pass: numbers appear only in a tip's own setting (speed 3, incline 12, 30 minutes). Fail: "from 9k to 15k" or before-and-after counts in the copy. Why: `H-no-number-progress`.
- **No walking gate outside the CTA.** Pass: no value slide tells the reader to allow an activity only while walking. Fail: a tip like "only listen to a podcast while walking". Why: that gate is ExcerLock's feature, and giving it away free steals the product's shine (captain, 2026-09-24).
- **CTA slot and form.** Pass: the app appears once as one of her own tips on any value slide, and the last slide is "GO GET THIS" with the App Store bar. Fail: ad or slogan wording, "i use excerlock" as the frame, or any other image. Why: `H-cta-last-slide`, and slogan wording saves at 0.6 to 1.2 per 1k against 95.8 for an aside.
- **Organic feed.** Pass: the deck as a whole would sit unnoticed among organic top-saving decks. Fail: anything that reads as an ad. Why: `H-organic-feed`.
- **Slide count.** Pass: follows `H-slide-count` or a recorded captain-approved count exception. A source skeleton's count alone is not an exception.
- **Picture lines.** Pass: every picture is gym or fitness (`H-gym-pictures`), about 3 hard gym shots, no watch. Fail: a picture picked to match the tip's words (a dog, a kitchen, a parking lot), or any watch. Why: `H-gym-pictures` and `H-no-watch`.
- **Account rules.** Pass: everything in the account's `account.md` and README holds. Fail: any account rule broken. Why: the account's rules are what make the deck sound like that account.
