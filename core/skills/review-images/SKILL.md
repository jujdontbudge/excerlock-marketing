---
name: review-images
description: Judge a generated image in a separate session, crop by crop, against its reference, its prompt JSON, the account's character and the section's rules, and write a PASS or FAIL verdict. Use after every image generation, before the image is used anywhere.
---
# Review images

The reviewer is a separate session that never generated the image. It assumes every image is broken
until proven otherwise: the job is to find the fault, not to confirm the pass. Write the verdict only
after every step below is done, and quote the evidence for each step. A verdict with a skipped step is
invalid.

## Inputs

- The generated image at full resolution.
- Its organic reference (or style digest from `library/styles/`) and any previous frames in the series.
- The on-screen text that will sit on it, if any.
- Its prompt JSON with the reference manifest, passing `python3 core/skills/image-prompt/check.py check FILE --rules sections/<section>/image-rules.json`.
- The account's `## Character` section in `accounts/<name>/account.md`, with its reference images (and physique anchor or body benchmark, if the account names one) from `accounts/<name>/assets/`.
- The section's rules (`sections/<section>/rules.md`) and the account's overrides for that section.

## Steps

1. Step 0: confirm the inputs and the manifest.
2. Step 1: crop each region at 2x or more and look at it on its own. Report what you saw per crop.
3. Step 1b: judge appeal.
4. Step 2: check mirror logic (mirror shots only).
5. Step 3: count everything out loud.
6. Step 4: compare the body to the account's character.
7. Step 5: put the image beside its reference.
8. Step 6: check the story fit.
9. Write the verdict in the format below.

Uncertain on any check means FAIL. Why: regenerating is cheap; a broken image going out is not.

## Checks

### Step 0: inputs
- **Inputs complete.** Pass: every input above is present. Fail: any input is missing; send it back without reviewing. Why: a verdict without the reference, the prompt JSON or the character is a guess.
- **Manifest respected.** Pass: nothing listed in any manifest entry's `must_not_transfer` appears in the image. Fail: anything from a `must_not_transfer` list shows up (the source person's face, body, outfit, case, layout). Why: the manifest is the fence between style and identity.

### Step 1: zoom crops
- **Face and neck.** Pass: eyes match, teeth and lips are clean, one neck joins head to torso at a possible angle (the head faces no further than about 90 degrees from the chest). Fail: mismatched eyes, smeared teeth, a missing or twisted neck. Why: faces are where viewers look first and where AI tells show.
- **Each arm.** Pass: shoulder, elbow, wrist, hand in order; the elbow bends one way; the forearm is not longer than the upper arm; the hand joins at the wrist. Fail: any reversed joint, stretched segment or detached hand. Why: impossible limbs mark the image as generated.
- **Each hand.** Pass: five fingers, thumb on the correct side, fingers actually grip what they touch (phone, cup, bar). Fail: extra or fused fingers, a wrong-side thumb, an object floating in the hand. Why: hands are the most common generation failure.
- **Torso.** Pass: one waist; chest and hips face the way the shoulders do unless the pose clearly twists at the waist; straps and seams continue. Fail: a doubled waist, a body facing two ways, doubled straps or broken seams. Why: torso errors read as a warped body.
- **Each leg.** Pass: hip, knee, ankle, foot in order; the knee bends backward only; shin about as long as thigh; the foot points the way the shin does; the sole is on the floor or clearly lifted. Fail: any backward knee, odd segment length, twisted foot or sole floating just above the floor. Why: legs are the second most common anatomy failure.
- **Feet and shoes.** Pass: two shoes of the same pair with consistent laces and soles. Fail: a third shoe, a floating shoe or mismatched shoes. Why: the eye catches a wrong shoe count at once.
- **Held and worn objects.** Pass: one headphone set (on the neck or the head, not both), one phone in one hand, one cup or bottle with natural real-looking branding or none. Fail: duplicated props, a phone in two hands, invented, garbled or misspelled words on any object. Why: duplicated props and fake text are classic AI tells.

### Step 1b: appeal (every image with a person)
- **Appeal.** Pass: the person is as attractive as or more attractive than the organic inspiration and the account's character and casting image: an attractive face and the physique the character describes. Fail: a plainer, ordinary-looking, boxier, heavier or less aspirational person, even when the photo looks perfectly organic. Why: organic is the photo's treatment, never the person; "it looks real" is not a defence.
- **No polish.** Pass: the attractiveness comes from casting while the photo stays an ordinary phone photo. Fail: retouched, beauty-filtered, graded or studio-lit. Why: polish is the AI look; it is not how to make her attractive.

### Step 2: mirror and reflection (mirror shots only)
- **Phone in the reflection.** Pass: the phone is visible in the reflection, held in the hand that would hold it. Fail: no phone, or a phone in the wrong hand. Why: a mirror selfie without the phone is physically impossible.
- **Reflection matches the body.** Pass: same clothing, same pose, no second person, no extra limb in the mirror frame. Fail: any mismatch between the person and the reflection. Why: broken reflections are an instant AI tell.
- **Mirrored text.** Pass: text, logos and screens in the reflection are mirrored or unreadable. Fail: reflected text reads the right way round. Why: real mirrors reverse text.

### Step 3: counts
- **Counts.** Pass: counted out loud in the report: 1 head, 2 arms, 2 hands, 10 fingers, 2 legs, 2 feet, and one of each prop the prompt JSON lists (1 phone, 1 headphone set). Fail: any count that differs. Why: counting forces the reviewer to actually look.

### Step 4: physique (every body-visible shot, before pictures included)
- **Body matches the character.** Pass: the body matches the account's `## Character` section and, side by side, its physique anchor or body benchmark. Fail: a visibly slimmer, heavier, flatter, softer or boxier body, or anything the Character section rules out. Why: the reviewer compares to the account's picture and words, not to the organic reference; "it matches the reference" is not a defence.
- **Body not hidden.** Pass: the pose, angle and outfit show the body the character describes. Fail: a pose or garment hides it (a flat side profile, a baggy top covering the figure) when the prompt asked for a body shot. Why: a hidden body fails the character as surely as a wrong one.

### Step 5: reference side by side
- **Camera feel.** Pass: the same phone-camera look as the reference: lighting direction, grain, colour, framing. Fail: cleaner, sharper, more cinematic or differently lit than the reference. Why: the reference is the organic benchmark for the photo.
- **Devices and props.** Pass: devices and props follow the reference and the prompt JSON: no device swapped, no phone added where the scene had none, no case pattern on a screen or bezel. Fail: a swapped device, an added phone, a case pattern painted onto a screen. Why: forced props repeat across images and read as a templated ad.
- **Account props.** Pass: the character's own props (such as her phone case) match the Character section and appear only when really in frame. Fail: a wrong case, or a case pattern on something that is not a case. Why: signature props are part of her continuity.
- **Brands.** Pass: branding matches the reference and the prompt JSON's `brands_and_props`. Fail: invented logos, readable text the reference did not have, or brands scrubbed from a scene that had them. Why: natural brands read as organic; invented text reads as AI.
- **Section rules.** Pass: the image breaks none of the picture rules in the section's `rules.md` or the account's overrides. Fail: any broken rule; name it by its ID. Why: the section's rules are the owner's standing calls, and this skill does not repeat them.

### Step 6: story fit
- **Text matches the photo.** Pass: the photo shows what the on-screen text says ("mirror pic" has a mirror; "treadmill" shows a treadmill). Fail: any contradiction between text and photo. Why: a mismatch breaks the story at a glance.
- **Before copy.** Pass: "how i was" or "before" copy sits only on a before photo of her. Fail: before copy on a chart, a screenshot or a current photo. Why: the viewer reads the photo as proof of the text.
- **Named assets.** Pass: where the section's rules or the account's `assets.md` name a specific real asset for this slot, the image is that asset, unedited. Fail: a different or edited asset. Why: named assets are the owner's approved versions.
- **No repeats.** Pass: no two images in the set read as the same scene. Fail: two near-identical scenes; fail one of them. Why: repeats waste a slot and look templated.
- **One point.** Pass: the photo fits the single point its text makes. Fail: the photo shows something else or several things. Why: each image carries one piece of the story.

## Verdict format (required)

```
item: <id>   image: <path>   reference: <path>
crops: face OK | arm-L OK | arm-R OK | hand-L OK | hand-R OK | torso OK | leg-L FAIL: <what> | ...
appeal: OK / FAIL: <what>
mirror: OK / n.a. / FAIL: <what>
counts: head 1, arms 2, hands 2, fingers 10, legs 2, feet 2, phones 1, headphones 1
physique: OK / n.a. / FAIL: <what>
reference: OK / FAIL: <what>
rules: OK / FAIL: <rule ID and what>
story: OK / FAIL: <what>
VERDICT: PASS | FAIL -> fix: <which prompt JSON field changes and how, or the surgical_edit to run>
```

## Outputs

- The verdict, written where the calling workflow keeps its review record.

## Rules

- PASS only when every line is OK. Why: one broken detail is enough to expose the image.
- The fix is a JSON change (a corrected field or a `surgical_edit`), never a prose patch. Why: see `core/skills/image-prompt/SKILL.md`.
- The worker resubmits to the same procedure, and an image is done only after a written PASS record exists. Why: an unrecorded pass cannot be checked later.
- The worker never edits a verdict, never marks PASS itself, and never uses an image without its PASS record. If the reviewer session dies or hits a limit, the worker starts a new reviewer session and waits. Why: the generator judging its own work is what this skill exists to prevent.
