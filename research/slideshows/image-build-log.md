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
| 02 s1 | gemini-2.5-flash-image, 9:16, refs attached | pending (Gemini credits depleted, 402) | | face, hook |
| 02 s2 | none: steps-edit-01.png + Screen Time placeholder | 0 | 0 | the captain's Screen Time capture does not exist yet; placeholder on the right half |
| 02 s3 | gemini-2.5-flash-image (our girl from behind, most of body) | pending | | |
| 02 s4 | none (CTA placeholder) | 0 | 0 | captain supplies Instagram screenshot |
| 02 s5 | gpt-image-2 low 1024x1536 | 3 | 0.033 | v1 fail (37:56 readout, person), v2 carried the leopard phone (captain's rejection), v3 PASS |
| 02 s6 | gpt-image-2 low | 1 | 0.011 | PASS |
| 03 s1 | gemini-2.5-flash-image | pending | | face, hook |
| 03 s2 | none: steps-edit-01.png full-bleed | 0 | 0 | |
| 03 s3 | gpt-image-2 low | 4 | 0.044 | v1 text-fit, v2 phone+towel (rejection), v3 wrong brand (Life Fitness vs Primal), v4 PASS |
| 03 s4 | none (CTA placeholder) | 0 | 0 | |
| 03 s5 | gpt-image-2 low | 2 | 0.022 | v1 near copy of the reference, v2 PASS |
| 03 s6 | gpt-image-2 low | 3 | 0.033 | v1 iPad turned into a leopard phone (rejection), v3 tablet but black pad, v4 pink YAGUD pad PASS |
| 04 s1 | gemini-2.5-flash-image | pending | | face, hook |
| 04 s2 | none: steps-edit-01.png full-bleed | 0 | 0 | |
| 04 s3 | gpt-image-2 low | 1 | 0.011 | PASS |
| 04 s4 | none (CTA placeholder) | 0 | 0 | |
| 04 s5 | gpt-image-2 low | 2 | 0.022 | v1 added a Life Fitness logo the reference lacks, v2 unbranded PASS |
| 04 s6 | gpt-image-2 low | 2 | 0.022 | v1 side mirror at the rear window, v2 PASS |
| 05 s1 | gemini-2.5-flash-image | pending | | face, hook |
| 05 s2 | none: reuse round10-before/before-final.png | 0 | 0 | as the script says |
| 05 s3 | none: steps-month-01.png full-bleed | 0 | 0 | |
| 05 s4 | none (CTA placeholder) | 0 | 0 | |
| 05 s5 | none: reuse slideshow 01 slide 4 base | 0 | 0 | the base is `images/reimagine/yermospam-1793-s5-gpt2-low-01.png` (matched against `build/slide-04.jpg`); the script's @gabylrei s4 citation is the barbell style source of a different take, not this image |
| 05 s6 | gemini-2.5-flash-image (our girl from behind) | pending | | |
| (discarded) | gpt-image-2 low | 3 | 0.033 | one run fired before a prompt patch had applied; outputs deleted |

gpt-image-2 total: 21 calls, about USD 0.23. Nano Banana: 0 so far (blocked on prepaid credits, about USD 0.30 for the 6 slides plus the watch-removal edit).

## Deviations from the brief

- 02 s3 and 05 s6 are "most of body" shots of our girl, so they go to Nano Banana with the character references (captain's rule) rather than gpt-image-2 as the firstmate inventory listed.
- 05 s2 and 05 s5 are reused images per the scripts ("No generation"), not new generations.
- Gemini Batch API and the "lowest output size" flag: gemini-2.5-flash-image takes no `imageSize`; the runner tries `batchGenerateContent` first and falls back to concurrent calls (the free-tier Batch refusal is on record in `data/learnings.md`).
