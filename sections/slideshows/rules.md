# Slideshow house rules

These are the defaults for every account. Skills, workflows and reviews link to a rule by its ID (`H-<id>`) instead of copying it.

An account overrides a rule only in `sections/slideshows/accounts/<name>/README.md` under `## Overrides`, as `- H-<id>: <new rule>. Why: <reason>.` Where no override exists, the rule below holds.

The captain's word wins over everything here. Numbers in the `Why:` lines come from the 611-post hook study (`data/slideshow-copy-analysis/report.md`), the 319-deck body study (`data/slideshow-body-analysis/report.md`) and the operators' AI-copy study (`data/slideshow-ai-copy-x/report.md`). They are observed metrics, not proof of conversion.

## Shape

### H-slide-count
Default: a deck has 5 to 7 slides. A different source count is evidence, not permission: use another count only with an explicit captain-approved exception recorded in the work item before production.
Why: the captain found 8 too long. Saves peak in the 6 to 9 slide range (24.7 per 1k against 10.2 for 3 to 5 slides), and a short deck gets viewers to the last slide before they drop off.

### H-cta-last-slide
The app tip can sit on any value slide, written as one of her own tips with truthful selected-app behavior. The last slide is "GO GET THIS" with the full App Store bar (`sections/slideshows/assets/appstore-card.png`: icon, name, subtitle, Open button) pasted top right at half the slide width, with no label under it, by `sections/slideshows/scripts/app_icon.py`. Before a download CTA is finalized, verify actual release/access status under `core/product.md`; an unresolved status blocks the handoff, not permission to invent a waitlist or replacement CTA. Why: the captain chose this ending on 2026-10-06, replacing the slide-4 card rule.

### H-no-cheat-sheet
Don't make a cheat sheet, a list, an iPhone Notes screenshot, or any slide that lays out the whole day or the whole process. Each slide gives one useful piece that solves part of the problem.
Why: the app is the cheat. A slide that solves the whole day kills the download, and a Notes page reads as "here is the whole plan".

### H-no-number-progress
Don't write number-progress talk ("takes me from 9k to 15k", before and after counts). Numbers appear only inside a real screenshot or in a tip's own setting (speed 3, incline 12, 30 minutes).
Why: nobody talks like that. It sounds like a metric, not a person.

## Copy

### H-copy-voice
Write flat, human statements in the voice of the real posts the account copies from. No em dashes. No metaphors, analogies or sayings. No "clever" contrast lines. Very few words per slide: aim under 12, and only a tip copied whole may run longer.
Why: the captain rejected two rounds of AI-written scripts for sounding like AI ("not a single good word"). The corpus's 1M+ view tier is made of 1 to 3 word slides, and a real post's wording already carries the niche's dialect.

### H-captain-copy-final
Preserve the captain’s slide text or title exactly. Do not paraphrase, shorten, normalize or supply alternatives. Deliver the requested work, referring to his slides by number. For a production conflict, apply the truthful-proof guardrail in `core/creative-rules.md` without silently editing his words.
Why: his titles already sit in the winning hook shapes, and rewriting them is where the rejected rounds went wrong.

### H-one-story
Every deck tells one continuous story a 13-year-old can follow slide by slide. Each slide answers "and then what?" from the one before. The product moment is set up before it and paid off after it. No implied jumps.
Why: operators give each slide one narrative job so the deck reads like someone telling a story, not a list of interchangeable tips. A reader who loses the thread stops swiping.

### H-organic-feed
Every deck must look like it belongs among the organic top-saving decks on the feed: text, photo style, slide count and one quiet product screenshot all match them. Nothing may read as an ad, and the copy must sound human.
Why: this is the captain's acceptance test. Native photo hooks beat designed ones (185,600 against 118,950 median views), and a product slide written like the free slides saves at 95.8 per 1k while store-card wording saves at 0.6 to 1.2.

## Process

### H-scope-confirm
Before any content work starts, state the exact item count and the list of items and get the captain's go. "All of them" means the last set he explicitly decided, never everything on file. Reference notes (such as hooks matched to sample posts) are not scope until he assigns them a format or says to script them.
Why: 19 scripts were once written when only 4 hook-to-format pairings were wanted.

## Pictures

### H-one-look
All six references in a deck share one look, as if the same girl took every photo in the same few weeks of her life: the same kind of light, colour grade, photo quality (candid phone snaps, never one editorial shot among them), season and places (e.g. her beige apartment, her bright boutique gym, her neighbourhood walk). Pick the deck's look first, then the six references within it. Where you can, take several from one creator's posts, since they already share a look.
Why: the captain, 2026-10-04: an elegant food photo next to a gritty gym barbell made the deck feel like strangers' photos stitched together. One look makes it read as one girl's story.

### H-gym-pictures
Don't pick pictures to match each slide's text. Every deck is gym and fitness pictures: about 3 hard gym shots (gym mirror selfies or her in the gym), and the rest gym-related: a gym or outdoor-workout picture, dumbbells or other gym gear. No random home, pet, kitchen or parking-lot photos just because the text mentions them.
Why: the captain, 2026-10-06: deck 1 had a dog, a kitchen and a parking lot because the pictures were matched to the tips, and most of it wasn't gym or fitness at all.

### H-house-look
The look is open within `H-gym-pictures`: gym fits, gym machines, gym photos, gym gear, outdoor walks or workouts. Pictures are not chosen to match each slide's text. Use at most one treadmill or walking pad per deck. Filter out only what the captain doesn't want:
- dark, gritty or grimy gyms and rooms;
- dirt trails, mud, messy or dull nature;
- coats, beanies and heavy outdoor gear; on the character, only gym fits or comfy clothes;
- plain, unflattering or low-effort photos.
Why: the captain, 2026-10-04. First he rejected dark gyms and "dirty ugly women walking in dirty nature". Then, when every deck came back as bedrooms and treadmills: "don't narrow too much on my initial prompts, keep it very open, just have negatives to filter out the stuff I don't want, and make it specific to the script the images are for".

### H-no-watch
Don't show an Apple Watch or any smartwatch: not in a reference photo, not in a prompt, not on the character. If a reference shows one, find another reference.
Why: it is the captain's call, and the generator copies the reference, so a watch in the reference ends up in the image even when the prompt says no watch.

### H-real-reference
Every slide picture is a copy of one real organic photo someone else posted, made with `core/skills/reference-swap/SKILL.md`. Nothing is generated from a description alone.
Why: the captain, 2026-10-02: "any slide ever made will always be a copy of another existing organic slide". A real photo's grain, light and clutter can be kept but not faked.

### H-keep-brands
Keep natural, real-looking branding wherever a real scene would show it (plates, shoes, supplements, packaging, gym machines), 1:1 with the reference. No invented or garbled words, captions or watermarks.
Why: real brands make the photo more organic. Blanket "no logos" scenes look staged.

### H-place-type
The swap preserves the selected reference's place and concept: a commercial gym stays that gym, a barbell scene stays a barbell scene. Select references using `H-gym-pictures`, not literal tip illustration.
Why: the reference supplies a coherent fitness world and believable camera treatment.

### H-style-not-identity
A reference gives everything except the person. Her face and hair come from the account's master reference; nothing of the reference person (face, tattoos, signature jewellery) stays. "Organic" means the photo's treatment, never a plainer, heavier or less attractive person.
Why: copying a real person's likeness is off-limits, and the captain wants the character as attractive as or more attractive than the reference while the photo stays raw. "It matches the reference" is not a defence for a worse-looking person.
