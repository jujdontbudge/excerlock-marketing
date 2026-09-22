# Reviewer checks for slideshow scripts and images

Positive checks, run before anything goes to the captain. Each line is a pass condition; the rule and its reason live in `research/slideshows/script-writing-guide.md`. A failed line is a rewrite, not a note.

## Script reviewer

1. Redundancy: no two slides in the deck say the same thing in different words or places; every value slide is a different piece.
2. Parentheticals: the only brackets in on-screen text are the captain's own CTA wording and his titles; no agent-written brackets anywhere. At most one "!!" aside line in the whole set of decks, and it appears in one deck only.
3. Hook in value slot: every value slide's text comes from a value slide of a real post (or the captain's own words) and reads as a tip, not as a hook.
4. Number-progress talk: no "from 9k to 15k", no before/after step counts in the copy; numbers appear only in real screenshots and in a tip's own setting (speed 3, incline 12, 30 minutes).
5. 50-IQ standalone test: each slide, read alone with no other slide, still makes sense to a 13-year-old; the deck retold slide by slide is a story, not a list.
6. Cheat sheets: no slide, list, Notes page or screenshot lays out the whole day or the whole process; each value slide gives one piece only.
7. Shape: 5 to 7 slides, CTA on slide 4 in one of the captain's forms ("use excerlock to...", "use an app like excerlock...", "excerlock blocks...", or his exact text), never "i use excerlock" as the frame; the last slide is a value slide or a proof, not filler.
8. References: exactly one organic reference per slide with URL, account, slide number, what it shows and the observed numbers; no alternates; no reference photo repeated across slides or decks except the screen-time screenshot and the CTA.
9. Banned sources: no copy from @rrachfitness 7378132607768349985 slide 2; no iPhone Notes screenshots; no Apple Watch in any reference.
10. Steps and before: the only steps screenshot is `data/slide5-steps/steps-final-16349.png` and the only screen-time screenshot is `data/slide5-steps/screentime-final.png`; 'how i was / before' copy never sits on a chart.
11. Housekeeping: captain's title and CTA text verbatim; lowercase and casual voice; no em dashes; max 2 faces and max 2 screenshots (CTA excluded); the CTA image is `data/cta-shield/shield-1080x2340.png` unedited (no generated CTA anywhere).

## Image reviewer (runs after generation, before overlay) - strengthened 2026-09-19

The reviewer is a SEPARATE session that never generated the image. It assumes every image is broken until proven otherwise: the job is to find the fault, not to confirm the pass. Write the verdict only after every step below is done, and quote the evidence for each step. A verdict with a skipped step is invalid.

### Step 0 - inputs
- The generated image at full resolution, its organic reference, the slide's on-screen text, the slide's prompt JSON (`skills/organic-json-image-prompting.md`, passing `scripts/image-prompt.py check`) with its reference manifest, and the character sheet. Missing any of these → do not review, send it back.
- Check the image against the manifest: nothing listed in any entry's `must_not_transfer` appears in the image.

### Step 1 - zoom crops (mandatory, one per region, at >=2x)
Crop and look at each region separately; report what you saw per crop:
- Face + neck: eyes match, teeth/lips clean, one neck that connects head to torso at a possible angle (head cannot face further than ~90° from the chest).
- Each arm: shoulder → elbow → wrist → hand. Elbow bends one way, forearm not longer than upper arm, hand attached at the wrist.
- Each hand: five fingers, thumb on the correct side, fingers hold the object they touch (phone, cup, bar).
- Torso: one waist, chest and hips face the same way the shoulders do unless the pose clearly twists at the waist; no doubled straps or clothing seams that don't continue.
- Each leg: hip → knee → ankle → foot. Knee bends backward only, shin ≈ thigh length, foot points the same way as the shin, sole on the floor or clearly lifted.
- Feet/shoes: two shoes, same pair, laces/soles consistent, no third shoe or floating shoe.
- Any object she holds/wears: headphones (one pair, on neck OR head, not both), phone (one, in one hand, case only where allowed), cup/bottle (one, with natural real-looking branding or plain; no invented, garbled or misspelled words).
Any impossibility in any crop → FAIL. Uncertain → FAIL (regenerating is cheap; a broken slide going out is not).

### Step 1b - appeal (positive check, every image with a person)
- PASS only if she is as attractive as or more attractive than the organic inspiration (and, for our character, her sheet and casting image): attractive face, aspirational physique per the benchmark on current pictures.
- Organic is judged on the photo only (camera, light, place, texture, framing, processing, clutter, imperfections). A plainer, ordinary-looking, boxier, heavier or less aspirational person is a FAIL even when the photo looks perfectly organic; "it looks real" is not a defence. Before slides keep the captain's softer-body exemption.
- Also FAIL the reverse: a retouched, beauty-filtered or studio-lit photo is not how to make her attractive.

### Step 2 - mirror and reflection logic (for any mirror selfie)
- The phone is visible in the reflection, held in the hand that would hold it.
- Reflection matches the body: same clothing, same pose, no second person, no extra limb in the mirror frame.
- Text, logos, and screens in the reflection are mirrored or blank, never readable the right way round.

### Step 3 - counts
- One of everything on her: 1 head, 2 arms, 2 hands, 10 fingers, 2 legs, 2 feet, 1 phone, 1 headphone set. Count them out loud in the report.

### Step 4 - physique (every body-visible shot)
- Not fat, not wiry: thick toned legs, big breasts, slim soft arms, no muscle definition, tight waist, real skin texture. Compare to `out/character/physique-anchor.png`; a visibly slimmer/heavier/flatter body → FAIL.

### Step 5 - reference side-by-side
- Same camera feel as the reference: phone-camera look, lighting direction, grain, colour, framing.
- Devices and props copied 1:1 from the reference: no device swapped, no phone or case added, no case pattern on a screen or bezel.
- Phone case appears only in face/body shots where she holds the phone.
- Brands 1:1 with the reference; no invented logos or readable text that the reference did not have.
- No Apple Watch. No watch at all unless the reference has one.

### Step 6 - story fit
- Contradictions with the on-screen text: "mirror pic" with no mirror; text says treadmill, photo shows street; "how i was"/before copy on anything but a before photo of her.
- Steps/stats slides use `data/slide5-steps/steps-final-16349.png` only; screen-time slides use `data/slide5-steps/screentime-final.png` only, and CTA slides use `data/cta-shield/shield-1080x2340.png` only, unedited, no generation, no crop beyond the layout.
- Redundancy across the deck: two photos that read as the same scene → FAIL one.
- Photo fits the slide's single tip.

### Verdict format (required)
```
slide: <deck>-s<n>   image: <path>   reference: <path>
crops: face OK | arm-L OK | arm-R OK | hand-L OK | hand-R OK | torso OK | leg-L FAIL: <what> | ...
mirror: OK / n.a. / FAIL: <what>
counts: head 1, arms 2, hands 2, fingers 10, legs 2, feet 2, phones 1, headphones 1
physique: OK / FAIL: <what>
reference: OK / FAIL: <what>
story: OK / FAIL: <what>
VERDICT: PASS | FAIL -> regenerate with: <one-line fix instruction for the prompt>
```
- PASS only when every line is OK. The worker copies the FAIL fix line into the next prompt and resubmits to the SAME reviewer procedure; a slide is done only after a written PASS record exists in review.json.
- The worker never edits a verdict, never marks PASS itself, and never ships a slide without its PASS record. If the reviewer dies or hits a limit, the worker starts a new reviewer session and waits.

## HARD RULE - her body in every picture, before pictures included (captain 2026-09-20, third time raised)

- Don't ever render her soft, flat, shapeless, or like a beginner gym girl - not in a hook, not in a value slide, and NOT in a "before" slide. Why: the captain has rejected this three times; it makes her look worse than the viewer and the account is selling her body.
- Every picture that shows her body copies the body in `data/slideshow-02-05-plan/body-benchmark-02-s1.png` (deck 02 slide 1): thick toned legs, big chest, tight waist, slim soft arms, no muscle definition, visibly fit. Why: one benchmark image removes interpretation; the reviewer compares to a picture, not to words.
- A "before" slide is told by the setting, outfit, and caption, never by a worse body. Why: the story works fine with the same body; a worse body breaks the rule above and there is no exception. Scope (captain correction 2026-09-20): the benchmark rule applies to CURRENT pictures; before slides are exempt and may look softer/heavier, that is the story (deck 03 slide 2 is exempt; deck 05 slides 1 and 2 both count as current on the captain's call).

- (creation) Attach physique-anchor + benchmark as references and state the body explicitly in every body-visible prompt. For 05 s2 the baggy tee must still show the body (tee tucked/cropped or fitted, shorts showing thick legs) - 'baggy' is not allowed to hide it.
- (review) The reviewer puts the benchmark beside every body shot; softer/flatter/slimmer/boxier = FAIL on any current picture; before slides exempt.
- (captain addition 2026-09-20) Her arms must NOT be muscular at all - no visible biceps, triceps, or shoulder definition. Arms are slim and soft, feminine. Reviewer: any muscular arm = FAIL. Benchmark comparison: legs/chest/waist from the benchmark; arms slimmer and softer than the benchmark if it shows definition.
- (body vs reference, captain 2026-09-20, fourth rejection of 05 s1) 1. The organic reference decides camera, lighting, place, framing, outfit ONLY - never her body. Her body always comes from the benchmark and the prompt must say it in plain words: hourglass, curvy, round full glutes, thick toned thighs, big chest, small waist, slim soft arms, flattering pose.
- 2. For body shots do NOT attach the organic reference as an image input. Pass its style as text (digest) and attach only character sheet + physique anchor + benchmark (02 s1). An attached flat body outweighs any words.
- 3. Pose/angle may change from the reference when it hides the body: use a three-quarter back angle, slight hip pop, chest visible. Flat side profile = FAIL.
- 4. Reviewer judges the body only against the benchmark; 'matches the reference' is not a defence.
