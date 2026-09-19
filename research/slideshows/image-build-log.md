# Slideshows 02-05 image build log (2026-09-19)

Outputs, prompts, digests and verdicts live outside the repo in the firstmate data folder `data/slideshows-02-05-images/` (`out/<deck>/<slide>.png`, `.prompt.txt`, `.digest.json`, `.usage.json`; `out/refs/` reference slides; `out/digests/` the 14 style digests; `review.html`, `review.md`, `review.json`). Runners: `tools/gpt2_batch.py` (gpt-image-2), `tools/nb_batch.py` (Nano Banana 2.5), `tools/build_prompts.py`, `tools/build_review.py`. No image is committed.

## Method (per generated image)

1. Organic reference fetched with `agent-web gallery` into `raw/refs/` (gitignored); the named slide copied to `out/refs/`.
2. Style digest written with `skills/style-clone.md` (vision by the worker's own model, Claude; palette hex reads taken from the image; brands generic in the digest).
3. Prompt = task line + digest summary as the content idea + hard place-type constraint + the script's draft scene + pin line + the digest's style block + the `skills/organic-iphone-photo.md` older-iPhone realism list + brands line (keep the reference's real-looking brands 1:1) + must-nots. Non-face: text only, the source photo is never sent (`skills/image-reimagine.md`); from the captain's rejection onward no phone or case is mentioned in any non-face prompt and devices/props follow the reference 1:1.
4. Non-face: `gpt-image-2`, `quality: low`, `1024x1536`, `moderation: low`, one run with concurrent calls (the OpenAI Batch API has no images endpoint). Face/body: `gemini-2.5-flash-image` via `generateContent`, `responseModalities: ["IMAGE"]`, `aspectRatio 9:16`, character references attached (grace reference with the watch removed + `girl-crop.jpg` + `case-leopard.png`), submitted as one Gemini Batch job with a concurrent fallback.
5. Review: separate fresh-eyes sub-agent on `research/slideshows/reviewer-checks.md`, reference beside the image; one regeneration per failed finding.

## Cost basis

gpt-image-2 low: ~840-1060 text input tokens + 158 image output tokens per call; estimated at USD 5/M input and USD 40/M output = about USD 0.011 per call (the skill's "about a cent"). Nano Banana 2.5: ~1290 output tokens, about USD 0.04 per image (from `data/learnings.md`).

## Per image

| Slide | Model / settings | Calls (kept + discarded) | Est. cost | Outcome |
|---|---|---|---|---|
| 02 s1 | gemini-2.5-flash-image, 9:16, one Batch job, refs attached | 1 | 0.04 | PASS (reviewer note: reference's brown set + red tumbler kit on our girl) |
| 02 s2 | none: steps-edit-01.png + Screen Time placeholder | 0 | 0 | the captain's Screen Time capture does not exist yet; placeholder on the right half |
| 02 s3 | gemini-2.5-flash-image, batch | 2 | 0.08 | v1 coastal like the reference but text on her head, v2 residential dusk street PASS |
| 02 s4 | none (CTA placeholder) | 0 | 0 | captain supplies Instagram screenshot |
| 02 s5 | gpt-image-2 low 1024x1536 | 3 | 0.033 | v1 fail (37:56 readout, person), v2 carried the leopard phone (captain's rejection), v3 PASS |
| 02 s6 | gpt-image-2 low | 1 | 0.011 | PASS |
| 03 s1 | gemini-2.5-flash-image, batch; then edit passes | 2 + 2 edits | 0.16 | v1 and v2 both rendered two pairs of headphones; a 2.5 edit removed both; a gemini-3.1-flash-image (Nano Banana 2) edit on v2 removed only the on-ear pair: PASS |
| 03 s2 | none: steps-edit-01.png full-bleed | 0 | 0 | |
| 03 s3 | gpt-image-2 low | 4 | 0.044 | v1 text-fit, v2 phone+towel (rejection), v3 wrong brand (Life Fitness vs Primal), v4 PASS |
| 03 s4 | none (CTA placeholder) | 0 | 0 | |
| 03 s5 | gpt-image-2 low | 2 | 0.022 | v1 near copy of the reference, v2 PASS |
| 03 s6 | gpt-image-2 low | 3 | 0.033 | v1 iPad turned into a leopard phone (rejection), v3 tablet but black pad, v4 pink YAGUD pad PASS |
| 04 s1 | gemini-2.5-flash-image, batch | 1 | 0.04 | PASS (skin paler than the character line) |
| 04 s2 | none: steps-edit-01.png full-bleed | 0 | 0 | |
| 04 s3 | gpt-image-2 low | 1 | 0.011 | PASS |
| 04 s4 | none (CTA placeholder) | 0 | 0 | |
| 04 s5 | gpt-image-2 low | 2 | 0.022 | v1 added a Life Fitness logo the reference lacks, v2 unbranded PASS |
| 04 s6 | gpt-image-2 low | 2 | 0.022 | v1 side mirror at the rear window, v2 PASS |
| 05 s1 | gemini-2.5-flash-image, batch | 1 | 0.04 | PASS |
| 05 s2 | none: reuse round10-before/before-final.png | 0 | 0 | as the script says |
| 05 s3 | none: steps-month-01.png full-bleed | 0 | 0 | |
| 05 s4 | none (CTA placeholder) | 0 | 0 | |
| 05 s5 | none: reuse slideshow 01 slide 4 base | 0 | 0 | the base is `images/reimagine/yermospam-1793-s5-gpt2-low-01.png` (matched against `build/slide-04.jpg`); the script's @gabylrei s4 citation is the barbell style source of a different take, not this image |
| 05 s6 | gemini-2.5-flash-image, batch | 1 | 0.04 | PASS |
| (discarded) | gpt-image-2 low | 3 | 0.033 | one run fired before a prompt patch had applied; outputs deleted |
| character ref | gemini-2.5-flash-image edit | 1 | 0.04 | watch removed from the approved grace reference, everything else identical |

gpt-image-2 total: 21 calls, about USD 0.23. Nano Banana: 11 calls (8 slide generations in two Batch jobs, 1 watch-removal edit on the character reference, 2 headphone edits), about USD 0.44. Build total about USD 0.67 (estimates from the token counts; Gemini prepaid balance was USD 4.41 before the Nano Banana calls).

Batch note: `batchGenerateContent` on `gemini-2.5-flash-image` with inline requests succeeded on the paid tier (both jobs finished in under two minutes), so the runner's sequential fallback was not needed. The watch on `grace-final-leopard-case.png` was removed with a 2.5 edit pass first (`out/character/grace-ref.png`) so no reference carried a watch.

## Result

14 generated images (8 gpt-image-2, 6 Nano Banana), 4 real-screenshot slides (one with a Screen Time placeholder), 2 reused approved images, 4 CTA placeholders: 24 slides. 9 slides were regenerated at least once after review (02 s5 x2, 03 s3 x3, 03 s5, 03 s6 x2, 04 s5, 04 s6, 02 s3, 03 s1 + edits); every final image passed the reviewer against its reference.

## Deviations from the brief

- 02 s3 and 05 s6 are "most of body" shots of our girl, so they go to Nano Banana with the character references (captain's rule) rather than gpt-image-2 as the firstmate inventory listed.
- 05 s2 and 05 s5 are reused images per the scripts ("No generation"), not new generations.
- Gemini Batch API and the "lowest output size" flag: gemini-2.5-flash-image takes no `imageSize`; the runner tries `batchGenerateContent` first and falls back to concurrent calls (the free-tier Batch refusal is on record in `data/learnings.md`).
