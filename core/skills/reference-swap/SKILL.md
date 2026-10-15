---
name: reference-swap
description: Make any image with a person in it by copying a real organic photo and swapping in the account's character, with one short plain-text prompt on Nano Banana Pro. Use for every slide picture, character reference, video first frame or any other generated image that shows a person.
---
# Reference swap

Every person image starts from a real organic photo. Preserve scene, camera, light, pose and expression while swapping the account's approved adult identity; bounded outfit/prop changes below are explicit exceptions, not scene replacement. Why: a generator can preserve a real phone photo's treatment more reliably than invent it. Method evidence: `research/ai-ugc-reference-first/video.md`.

## Inputs

- The real reference photo, saved in `raw/`.
- The account's master reference (`accounts/<name>/assets.md`), attached as image 2 on every image she is in, always. The only exception is when the master reference is being made. Why: without it the model invents a new girl (captain, 2026-10-04).
- What the image is for: the slide's text, or the video it starts.

## Steps

1. **Find the reference** (half the time goes here). Use a real photo whose scene, framing and mood already show what the image needs. It should have one person, a face that is big enough and not hidden (unless the slide hides it), natural hands, shine but no blown-out skin, a background with some personality, little or no caption and no smartwatch.
2. **Analyse it.** Write down what makes it real:
   - **Facial expression first:** head angle and tilt, where the pupils point, eyelids, brows, which mouth corner lifts, lip press or pout, mood.
   - **Camera:** front or rear, lens, height and angle, framing.
   - **Light:** where it comes from, shine on the skin, clipped areas.
   - **Phone processing:** grain, smoothing, sharpening.
   - **Pose and hands.**
   - **Background:** people, clutter and brands.
   - **Imperfections.**
   - **What has to change:** the person's identity, tattoos, jewellery, captions.

   Then analyse the **character's master reference** the same way (image 2): her skin texture and tone, brows, eye colour, natural lip colour, hair colour, roots, parting and flyaways, and anything she always wears. Write it once as the account's identity line (`accounts/<name>/account.md`, "Identity line") and reuse it; refresh it only when the master changes.

   Keep the notes in the deck log or a `raw/` notes file.
3. **Write one short plain-text prompt.** Template:
   > Edit image 1. Replace the woman with the woman in image 2 and keep everything else exactly the same: [the place and its key objects], the people in the background, the framing and crop, the camera angle, the lighting, her exact pose [one line naming it], her outfit [or: her outfit's cut, changed to (new colour)], and the same expression and eye direction as in image 1. Keep the photo's ordinary iPhone quality.
   >
   > From image 2 take only her face and hair. [The account's identity line, body line and makeup line, pasted word for word.] [Her own branded items, accessories and organic touches, one line.] [Remove: tattoos / the caption / the source's jewellery.]

   - **The body line is required.** Every account file has one (`accounts/<name>/account.md`, "Body line"). Paste it word for word; never rewrite it. Why: without it the model keeps the reference woman's body, and the captain got girls who were "overly skinny and small, not toned" on every slide (2026-10-04). Image 2 only carries the face and hair, so the body has to be written.
   - **The makeup line is required too** (same file). Why: without it the model paints on glam makeup (contour, lashes, gloss); the captain wants natural makeup on both girls (2026-10-04).
   - **Name what makes the photo real, so the model keeps it.** From the analysis, list the background objects, scuffs, mirror marks, lighting and phone processing in the "keep" sentence. Why: what the prompt doesn't name, the model cleans up or rebuilds.
   - **The identity line is required** (same file). Why: "take her face and hair from image 2" alone let her face drift slide to slide; naming her own skin, brows and hair holds it.
   - **Personalization is bounded.** Use the five-to-seven scene-object quota below, which supersedes the older three-to-five touch quota rather than adding to it. Objects stay subtle, visibly natural and varied across the set. Preserve scene layout, background people, pose, expression, framing and processing. Record allowed differences separately from the fixed-photo contract so review does not reject requested changes.
   - **Make it not look like a copy of the reference.** On at least half the slides of a deck, change her outfit colour (name the new colour in the prompt, e.g. "change her set to sage green"). On every slide, including slides with no person, add five to seven random everyday objects in the scene where they'd really be: a crumpled receipt, keys, a half-eaten snack, a charger cable, a hoodie on a chair, a shopping bag, a mug, an open makeup bag, a candle. Pick different ones per slide. Why: with only three or four small touches and the reference's own outfit, the outputs "straight up look identical" to the source posts (captain, 2026-10-06).
   - **Add organic branded items.** Swap one or two of the reference's generic or off-brand items for real brands a girl like her owns, and keep the real brands already in the photo. Examples: an Owala or Stanley bottle, AirPods or AirPods Max, a CASETiFY or clear phone case with a sticker, an Alo or Lululemon set, a Celsius can. Why: real brands make the photo read as her life (captain, 2026-10-04; `H-keep-brands`).

   When the master reference is being made, there is no image 2. Describe the new person instead: the genetic-difference traits (below), hair colour, and the account's body line.
4. **Authorize, then generate once.** Before the first paid roll of a task/deck, obtain captain approval for image count and stated current cost. Record the approval before submitting. Inside that scope, roll one image at a time, at 1K, another only after failed review. Reuse a stable per-image ledger across reference/prompt changes; failures count as attempts. The runner's `--dry-run` validates inputs without credentials or spend. Actual calls require authorization and estimated-cost flags:
   ```
   .venv/bin/python core/skills/reference-swap/swap.py --prompt P.txt --out raw/<task>/roll-1.png --ref REF.jpg --face MASTER.png -n 1 --state raw/<task>/image-ledger.json --approval '<captain approval record>' --estimated-cost <current-estimate>
   ```
   Why: the captain pays for every roll and three-at-once tripled the cost of slides that passed on the first try (captain, 2026-10-06).
   - **Provider: fal.** Run the same model through fal's `fal-ai/nano-banana-pro/edit` ($0.15 per 1K image, checked 2026-10-14), with the reference as image 1 and the master as image 2, `aspect_ratio: auto`, logged in the same per-image ledger. Why: the captain's Gemini API project hit its monthly spending cap and he said "use gemini models on fal" (2026-10-14). FLUX.2 [max] on fal declined our identity swaps under its content policy (2026-10-14), so don't use it. The working runner is `raw/decks-2026-10-14/fal_roll.py` until it is promoted next to `swap.py`.
   - Model: Nano Banana Pro (`--model pro`, default) at 1K. Verify current pricing when requesting spend; old estimates are not quotes. The captain moved back from Flash because it rebuilt rooms and gave leaner bodies. For text-only cleanup of a no-person photo, paste just the cleaned region onto the original.
   - The output keeps the reference's own shape (`swap.py` picks the nearest supported ratio). Why: forcing 9:16 onto a 3:4 photo made the model rebuild the room to fill the extra height.
5. **Pick and check.** Run `core/skills/review-images/SKILL.md` on each roll beside the reference. Keep the best one that passes.
6. **If none passes:** change one line of the prompt and roll again. If that fails too, change the reference. Never stack an edit on top of a generated image.
7. **Show the captain** the reference and the chosen image side by side, before any further spend.

## Don'ts

- Don't make an image from a text description alone, or from a JSON prompt. Why: an invented scene looks like AI; the captain retired the JSON workflow and style digests on 2026-10-02.
- Don't attach anything but the reference and the master reference: no physique, outfit, phone-case or old scene renders. Why: every extra full photo is another scene, and the model blended them into a different gym, camera and pose (G66 v1).
- Make the new identity clearly distinct: for a new master, name three or four differentiating traits (skin tone, eye colour, nose, lips, hair colour) without a celebrity likeness. Why: the captain requires a fictional adult, not impersonation; a vague replacement prompt retained the source face in H12 round 3.
- Don't pile on beauty adjectives or face-shape words ("heart-shaped, high cheekbones, sharp jaw", root colour, freckles). Why: a long list averages into an uncanny face (G66 v4) and the shape words gave a face the captain called "so weird" (H12).
- Don't script the expression muscle by muscle. Tell the model to keep the expression from image 1, then check it in a face crop. Why: a new face forced into a written expression looks strained, and facial expression is what sells the photo (captain).
- Don't stack edits or edit a generated image. Regenerate from the reference instead. Why: each edit adds seams that show, especially once animated.
- Don't pick a reference with a tiny or hidden face when making a master reference. Why: the output keeps the input's framing, and a postage-stamp face comes out smeared (G66).
- Don't change the scene, pose or camera. Swap outfit colours and props for her own (branded items above) in the same single prompt. Why: the background and framing are what make it a real photo; the items are what make it hers.
- Review the body as hard as the face: the waist must be clearly the narrowest part of her, and the legs, chest and arms must match the body line. Why: the captain rejects a pretty face on a small, flat, "normal fit" body.
- Don't add text to the image. Why: on-screen text is added in the editor.
- Further attempts beyond three or resolution above 1K require separate captain approval and stated cost, recorded with `--exception-approval`. Approval flags record permission already received, never permission the agent grants itself. Keep the same ledger; outputs refuse overwrites and failures exit nonzero. Batch/fal experiments are archived, not production alternatives. Why: spend is his decision.

## Outputs

- Trial rolls remain in raw. After approval, promote selected media into the calling workflow's gitignored assets folder and tracked manifest, recording reference, prompt, roll/ledger, model, size and cost. Keep originals and provenance; paid requests are never part of a test run.

## Runner verification

`scripts/test` exercises dry-run attempt accounting, project-wide nonparallel submission, approval/cost/resolution gates, exclusive outputs and truthful failures using local fixtures and mocked provider responses. These tests never call the paid provider. Dry runs reuse the actual image ledger; do not replace it to evade the attempt limit.
