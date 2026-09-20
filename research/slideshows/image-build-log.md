# Slideshows 02-05 image build log (2026-09-19)

Outputs, prompts, digests and verdicts live outside the repo in the firstmate data folder `data/slideshows-02-05-images/` (`out/<deck>/<slide>.png`, `.prompt.txt`, `.digest.json`, `.usage.json`; `out/refs/` reference slides; `out/digests/` the 16 style digests; `out/character/physique-anchor.png` the body reference; `out/round1/`, `out/round2/` superseded face/body renders; `review.html`, `review.md`, `review.json`). Runners: `tools/gpt2_batch.py` (gpt-image-2), `tools/nb_batch.py` (Nano Banana 2.5), `tools/build_prompts.py`, `tools/build_review.py`. No image is committed.

## Method (per generated image)

1. Organic reference fetched with `agent-web gallery` into `raw/refs/` (gitignored); the named slide copied to `out/refs/`.
2. Style digest written with `skills/style-clone.md` (vision by the worker's own model, Claude; palette hex reads taken from the image; brands generic in the digest).
3. Prompt = task line + digest summary as the content idea + hard place-type constraint + the script's draft scene + pin line + the digest's style block + the `skills/organic-iphone-photo.md` older-iPhone realism list + brands line (keep the reference's real-looking brands 1:1) + must-nots. Non-face: text only, the source photo is never sent (`skills/image-reimagine.md`); from the captain's rejection onward no phone or case is mentioned in any non-face prompt and devices/props follow the reference 1:1.
4. Non-face: `gpt-image-2`, `quality: low`, `1024x1536`, `moderation: low`, one run with concurrent calls (the OpenAI Batch API has no images endpoint). Face/body: `gemini-2.5-flash-image` via `generateContent`, `responseModalities: ["IMAGE"]`, `aspectRatio 9:16`, character references attached (round 3: `physique-anchor.png` first with "copy her figure 1:1", then `case-leopard.png` and the grace reference with the watch removed; rounds 1-2: grace reference + `girl-crop.jpg` + `case-leopard.png`), submitted as one Gemini Batch job with a concurrent fallback.
5. Review: separate fresh-eyes sub-agent on `research/slideshows/reviewer-checks.md`, reference beside the image; one regeneration per failed finding. Round 3 (physique redo) was reviewed by the team-lead (items 1-11) after the sub-agent hit its session limit mid-review.
6. Physique (captain's second review): a text-only PHYSIQUE block did not change Nano Banana 2.5's body (round 2 still slim), so a physique anchor was built: a mirror selfie of our girl generated from the grace reference (2.5, two candidates), the better one body-edited on `gemini-3.1-flash-image` (Nano Banana 2) to thick toned thighs/glutes, full bust, tight waist, slim toned arms; attached as the first reference for every face/body prompt. Round 3 held on all six.

## Cost basis

gpt-image-2 low: ~840-1060 text input tokens + 158 image output tokens per call; estimated at USD 5/M input and USD 40/M output = about USD 0.011 per call (the skill's "about a cent"). Nano Banana 2.5: ~1290 output tokens, about USD 0.04 per image (from `data/learnings.md`). Nano Banana 2 (`gemini-3.1-flash-image`, 1K edits): ~1420-1470 output tokens, estimated at about USD 0.07 per edit.

## Per image

| Slide | Model / settings | Calls (kept + discarded) | Est. cost | Outcome |
|---|---|---|---|---|
| 02 s1 | gemini-2.5-flash-image, 9:16, Batch, refs attached | 3 | 0.12 | round 1 PASS but superseded by the physique redo; round 2 (text PHYS only) slim; round 3 with the anchor PASS |
| 02 s2 | none: steps-final-16349.png + Screen Time placeholder | 0 | 0 | the captain's Screen Time capture does not exist yet; placeholder on the right half |
| 02 s3 | gemini-2.5-flash-image, batch | 4 | 0.16 | v1 coastal like the reference but text on her head, v2 residential dusk street PASS; round 2 (physique redo) head turned with partial face; round 3 with the anchor, back of the head only, PASS |
| 02 s4 | none (CTA placeholder) | 0 | 0 | captain supplies Instagram screenshot |
| 02 s5 | gpt-image-2 low 1024x1536 | 3 | 0.033 | v1 fail (37:56 readout, person), v2 carried the leopard phone (captain's rejection), v3 PASS |
| 02 s6 | gpt-image-2 low | 1 | 0.011 | PASS |
| 03 s1 | gemini-2.5-flash-image, batch; then edit passes | 4 + 3 edits | 0.34 | v1 and v2 both rendered two pairs of headphones; a 2.5 edit removed both; a 3.1 edit on v2 removed only the on-ear pair: PASS, superseded; round 2 slim; round 3 with the anchor rendered two pairs again plus a HYDRATE word on the tumbler, one 3.1 edit fixed both: PASS |
| 03 s2 | gemini-2.5-flash-image, batch; one 3.1 edit | 1 + 1 edit | 0.11 | captain's second review: a BEFORE picture (couch, blanket, snacks, phone, dim light) replaces the steps chart; new reference @iliana.rdz96 7654815554305363218 s3 (2.4M plays) found by a scanner sub-agent over the hunts; render PASS except invented readable packet names, one 3.1 edit made the packets plain: PASS. The old steps screenshot is archived as `out/03/s2-old-steps.png` |
| 03 s3 | gpt-image-2 low | 4 | 0.044 | v1 text-fit, v2 phone+towel (rejection), v3 wrong brand (Life Fitness vs Primal), v4 PASS |
| 03 s4 | none (CTA placeholder) | 0 | 0 | |
| 03 s5 | gpt-image-2 low | 2 | 0.022 | v1 near copy of the reference, v2 PASS |
| 03 s6 | gpt-image-2 low | 3 | 0.033 | v1 iPad turned into a leopard phone (rejection), v3 tablet but black pad, v4 pink YAGUD pad PASS |
| 04 s1 | gemini-2.5-flash-image, batch | 3 | 0.12 | round 1 PASS, superseded; round 2 slim; round 3 with the anchor PASS (note: small swoosh on the socks) |
| 04 s2 | none: steps-final-16349.png full-bleed | 0 | 0 | the one steps receipt |
| 04 s3 | gpt-image-2 low | 1 | 0.011 | PASS |
| 04 s4 | none (CTA placeholder) | 0 | 0 | |
| 04 s5 | gpt-image-2 low | 2 | 0.022 | v1 added a Life Fitness logo the reference lacks, v2 unbranded PASS |
| 04 s6 | gpt-image-2 low | 2 | 0.022 | v1 side mirror at the rear window, v2 PASS |
| 05 s1 | gemini-2.5-flash-image, batch | 3 | 0.12 | round 1 PASS by the reviewer, FAILED by the captain (fat/wiry); round 2 slim; round 3 with the anchor PASS, physique clearly on target |
| 05 s2 | gemini-2.5-flash-image, batch | 1 | 0.04 | before picture regenerated in the physique redo so the face matches the new hooks (baggy black tee, softer body): PASS; the slideshow 01 before-final.png reuse is dropped |
| 05 s3 | none: steps-final-16349.png full-bleed | 0 | 0 | the one steps receipt |
| 05 s4 | none (CTA placeholder) | 0 | 0 | |
| 05 s5 | none: reuse slideshow 01 slide 4 base | 0 | 0 | the base is `images/reimagine/yermospam-1793-s5-gpt2-low-01.png` (matched against `build/slide-04.jpg`); the script's @gabylrei s4 citation is the barbell style source of a different take, not this image |
| 05 s6 | gemini-2.5-flash-image, batch | 3 | 0.12 | round 1 PASS, superseded; round 2 blue shorts (the digest's "blue shorts pop" line leaked, now stripped); round 3 black shorts with the anchor PASS |
| (discarded) | gpt-image-2 low | 3 | 0.033 | one run fired before a prompt patch had applied; outputs deleted |
| character ref | gemini-2.5-flash-image edit | 1 | 0.04 | watch removed from the approved grace reference, everything else identical |
| physique anchor | gemini-2.5-flash-image x2, then one gemini-3.1-flash-image body edit | 2 + 1 edit | 0.15 | two mirror-selfie candidates from grace-ref; candidate 1 body-edited to the captain's physique = `out/character/physique-anchor.png` |

Rounds 3-6 (captain's third review, inbox 005-007): 02 s1 had a twisted back leg and an owl-neck that the team-lead's own interim review passed; the phone/case was being forced into every face picture (the launch brief listed the case as a character attribute, carried into the CHAR prompt block and every attached reference). Fixes: pose pinned and 02 s1 regenerated; case made a mirror-selfie-only prop (CHAR block, guide, reviewer-checks, script character lines); 03 s2 rebuilt as a photo from across the table with no phone; the Image reviewer section replaced by the captain's Step 0-6 procedure with mandatory zoom crops and a required verdict record; brand rule 1:1 with the reference. reviewer-2 (fresh separate session) ran rounds 3-6; every FAIL was fixed with the reviewer's own fix line (Nano Banana 2 edit passes where the anatomy was right, a regeneration where it was not) and resubmitted until all eight face/body slides held a written PASS record (stored in `review.json`, rendered on `review.html`). Calls in these rounds: 5 Nano Banana 2.5 generations (02 s1, 03 s2 x3, 02 s3) and 17 Nano Banana 2 edits (02 s1 x1, 03 s1 x3, 04 s1 x2, 02 s3 x3, 05 s6 x3, 03 s2 x4, 05 s2 x1), about USD 1.39.

Rounds 7-9 (captain's fourth review, inbox 008-012): deck 05 s1/s2 rejected a third time on the body. HARD body rule (benchmark image `data/slideshow-02-05-plan/body-benchmark-02-s1.png` = the passed 02 s1, copied to `out/character/body-benchmark.png`; legs/chest/waist from it, arms slim and soft with no muscle definition; current pictures only, before slides exempt, 05 s1 and 05 s2 counted as current) added verbatim to the guide, reviewer-checks, the four script character blocks and the PHYS prompt block; anchor + benchmark attached to every body-visible generation. 05 s1 + 05 s2 remade in one Batch call; 05 s2 passed after a sock edit; 05 s1 took the cap of two regenerations to reach the benchmark body, then one edit pass (soft arms, blank locker plates in the mirror) for its PASS record. Other current body slides re-checked against the benchmark: all pass. Steps receipt replaced with `steps-final-16349.png` on 02 s2, 04 s2, 05 s3. Calls: 3 Nano Banana 2.5 generations, 2 Nano Banana 2 edits, about USD 0.26.

gpt-image-2 total: 21 calls, about USD 0.23. Nano Banana 2.5: 34 calls (8 round-1 slides, 8 round-2 slides, 6 round-3 slides, 5 rounds 3-6 regenerations, 3 rounds 7-9 regenerations, 2 anchor candidates, 1 watch-removal edit, 1 headphone edit), about USD 1.36. Nano Banana 2 (3.1) edits: 23 (4 before the third review, 17 in rounds 3-6, 2 in rounds 7-9), about USD 1.61. Build total about USD 3.20 (estimates from the token counts). Gemini credits ran out once mid-build (402) and were topped up by the captain.

Batch note: `batchGenerateContent` on `gemini-2.5-flash-image` with inline requests succeeded on the paid tier (both jobs finished in under two minutes), so the runner's sequential fallback was not needed. The watch on `grace-final-leopard-case.png` was removed with a 2.5 edit pass first (`out/character/grace-ref.png`) so no reference carried a watch.

## Result

16 generated images (8 gpt-image-2, 8 Nano Banana), 3 real-screenshot slides (all `steps-final-16349.png`; 02 s2 with a Screen Time placeholder), 1 reused approved image (05 s5), 4 CTA placeholders: 24 slides. Every Nano Banana face/body slide was rebuilt in the physique redo (rounds 2 and 3) and then taken through the Step 0-6 procedure (rounds 3-6) until it held a written PASS record from a separate reviewer session; the non-face gpt-image-2 slides keep their earlier reference-side-by-side PASS verdicts.

## Deviations from the brief

- 02 s3 and 05 s6 are "most of body" shots of our girl, so they go to Nano Banana with the character references (captain's rule) rather than gpt-image-2 as the firstmate inventory listed.
- 05 s5 is a reused image per the script ("No generation"); 05 s2 was regenerated in the physique redo so the before picture carries the same face as the new hooks.
- Deck 03 slide 2 is now a generated before picture (face 2 of 2 in that deck), not the steps receipt; the script's "15k" pointer line was dropped because a chart is not a before picture.
- Gemini Batch API and the "lowest output size" flag: gemini-2.5-flash-image takes no `imageSize`; the runner tries `batchGenerateContent` first and falls back to concurrent calls (the free-tier Batch refusal is on record in `data/learnings.md`).
