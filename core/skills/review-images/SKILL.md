---
name: review-images
description: Judge a generated image in the same session that made it, side by side with the real reference it copies, and write a PASS or FAIL verdict. Use after every image generation, before the image is used anywhere.
---
# Review images

The agent that generated the image reviews it in the same session; don't spawn a subagent or new session. Why: a separate reviewer re-reads every input and wastes too many tokens (captain, 2026-09-24). Assume every image is broken until proven otherwise: the job is to find the fault, not to confirm the pass. Write the verdict only after every step is done.

## Inputs

- The generated image at full resolution.
- The real reference it copies (`core/skills/reference-swap/SKILL.md`), and the account's master reference.
- The prompt text, and the on-screen text that will sit on the image.
- The account's `## Character` section in `accounts/<name>/account.md`, and the section's rules plus the account's overrides.

## Steps

1. **Side by side with the reference.** Build one image with the reference on the left and the result on the right, plus a face crop of each. Look at it yourself. Ask open questions ("what is different?", "does she look like a real person?"), never a checklist of yes/no ticks. Why: a ticked checklist called a different gym "intact" on G66 v1.
2. Run every check below and quote what you saw.
3. Write the verdict.

Uncertain on any check means FAIL. Why: regenerating is cheap; a broken image going out is not.

## Checks

### Same photo
- **Scene kept.** Pass: same place, framing, camera angle, background people and light as the reference, allowing only the outfit/prop changes explicitly authorized in the prompt. Fail: a different room, camera distance, layout or an unrequested modification. Why: the reference supplies the scene; bounded personalization is not scene replacement.
- **Pose kept.** Pass: same body position, hand positions and phone position. Fail: she stands where she sat, a hand moved, a knee came down. Why: v2 of G66 re-posed her and lost the photo.
- **Expression kept.** Pass: in the face crops, same head tilt, gaze direction, eyelids, brows and mouth shape. Fail: a calmer, smilier or pouting version. Why: facial expression is everything (captain, 2026-10-02).
- **Photo quality.** Pass: the same phone-camera look, grain and processing. Fail: cleaner, sharper, more retouched or more cinematic. Why: polish is the AI look.

### Person
- **Real person.** Pass: she looks like a real girl in an ordinary phone photo: believable skin, hair and face proportions. Fail: airbrushed, waxy, uncanny, wig-like hair, mismatched skin. Why: the captain rejected G66 v4 as "alien".
- **Right person.** Pass: the face and hair match the account's master reference (or, when making the master, the captain's description). Fail: a drifted face, wrong hair colour or wrong age. Why: one girl across every slide.
- **Not the source.** Pass: the generated identity is distinct from the source, with no source face, tattoos or identifying jewellery. Fail: a retained source identity. Why: the captain requires a distinct fictional adult, not impersonation.
- **Appeal.** Pass: as attractive as or more attractive than the reference person, with the body the Character section describes. Fail: plainer, heavier, boxier. Why: organic is the photo's treatment, never the person.
- **Body.** Pass: the body matches the account's body line: the waist is clearly the narrowest part of her, much narrower than hips and chest, and her legs, chest and arms are as the line says. Fail: small all over, flat, "normal fit", thin legs. Why: the captain rejected every girl who looked "overly skinny and small, not toned" (2026-10-04).

### Anatomy and objects
- **Face and neck.** Pass: matching eyes, clean teeth and lips, one neck at a possible angle. Fail: anything else. Why: faces are where viewers look first.
- **Arms, hands, legs.** Pass: joints in order and bending the right way, five fingers, thumbs on the correct side, hands actually gripping what they hold, feet on the floor or clearly lifted. Fail: any reversed, extra, fused or floating part. Why: limbs and hands are the most common AI failures.
- **Counts.** Count the visible anatomy and objects against the pose and crop; hidden limbs need not appear. Fail extra, fused or anatomically impossible parts, not legitimate occlusion. Why: counting forces inspection without inventing parts outside the frame.
- **Mirror shots.** Pass: the phone shows in the reflection, the reflection matches the body, and reflected text is reversed or unreadable. Fail: anything else. Why: broken reflections are an instant AI tell.
- **Text.** Pass: no caption left, no invented or garbled words. Real brands from the reference stay. Fail: leftover caption, fake text, or brands scrubbed. Why: invented text reads as AI; real brands read as organic.

### Fit
- **Section rules.** Pass: breaks none of the picture rules in the section's `rules.md` or the account's overrides. Fail: name the rule by its ID. Why: those are the captain's standing calls.
- **Set fit.** Apply the calling section's picture policy and explicit overrides. Check coherent treatment, caption space and unintended repetition. Literal illustration of the words is required only when that policy or the assignment calls for it.

## Verdict format (required)

```
item: <id>   image: <path>   reference: <path>   roll: <n>
same photo: OK / FAIL: <what>
person: OK / FAIL: <what>
anatomy: OK / FAIL: <what>   counts: head 1, arms 2, hands 2, fingers 10, legs 2, feet 2, ...
fit: OK / FAIL: <rule ID or what>
VERDICT: PASS | FAIL -> fix: <another roll / the one prompt line to change / a different reference>
```

## Rules

- Show the captain the reference and the chosen image side by side before spending on another round. Embed the images in one HTML page as base64 and show it inline with `::inline-vis`. Why: he decides from the picture, and blind retries waste his money.
- PASS only when every line is OK. Why: one broken detail is enough to expose the image.
- An image is done only after a written PASS record exists. Why: an unrecorded pass can't be checked later.
