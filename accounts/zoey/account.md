# Zoey
<!-- lint-names: Zoey, Grace, our girl, leopard, grace-final-leopard-case, grace-ref-no-watch, body-benchmark-02-s1, @graceelizabethlifts -->

Zoey is the existing TikTok account. Its character is called "our girl" in the deck scripts and "Grace" in old file names (her first approved picture was remade from a @graceelizabethlifts gym mirror photo in the `round8-grace` folder). Slideshow decks 01 to 05 are hers.

## Audience

Gym girls, about 16 to 26, who save and share "dream body" posts. The account sells a body result, and she is the result.

## Character

### Look

- A young adult woman with long dark blonde hair, worn down, in a ponytail or in a low bun.
- Tanned golden skin with real texture: pores, visible sports-bra tan lines and a light sweat sheen.
- Gym clothes that look bought and worn: matching seamless sets (sage green or black), white crew socks, white trainers.
- Silver-grey over-ear headphones, on her head or around her neck.
- Her phone has a leopard-print case (tan and black spots) with a dark reddish-brown raised rim and a large square camera cutout in the top corner. Reference: `case-leopard.png` in `assets.md`.
- Her face is the face in her approved reference picture (`assets.md`). There is no written face sheet yet.

### Body (HARD rule, captain 2026-09-19 and 2026-09-20)

In every picture that shows her body she looks very good: an hourglass, curvy figure with round full glutes, thick toned thighs and legs, big breasts, a small tight waist and slim, soft, feminine arms. The body in `body-benchmark-02-s1.png` is the target: copy its legs, chest and waist; make the arms as slim and soft as the benchmark or softer. Every body-visible prompt states this body in plain words, and the physique anchor and benchmark are attached (`assets.md`).

- Don't render her fat, soft, flat, shapeless, wiry or like a beginner gym girl. Why: the captain rejected this three times (deck 05 slide 1 looked "fat and wiry"); a girl who looks worse than the viewer makes the deck a lie, and the viewer scrolls.
- Don't give her muscular arms: no visible biceps, triceps or shoulder definition. Why: muscular arms read as a lifter or bodybuilder look this audience does not want; the aspiration is thick legs and a small waist with slim arms (captain, 2026-09-20).
- Don't make her legs thin. Why: the 2026-09-17 note "keep her slim, thick arms and legs were rejected" is superseded for the legs by the 2026-09-19 rule "thick toned legs"; only the arms stay slim.
- Don't show a worse body on a before slide. The before is told by the setting, outfit, posture, light and caption. Why: the story works with the same body, and a softer body breaks the body rule; the old before-slide exemption was deleted.
- Don't let clothes hide the body. A baggy tee is tucked, cropped or fitted, and shorts show the thick legs. Why: deck 02 slide 3, 05 slide 2 and 05 slide 6 failed review for hidden bodies (oversized or knotted tops, square-on angles).
- Don't show a visible vein. At most a barely noticeable faint vein on the left forearm. Why: the captain rejected a visible vein (2026-09-17).
- Don't give her tattoos. Why: the generator kept adding forearm tattoos she does not have, and each one had to be edited out.

### Body versus the organic reference (captain 2026-09-20, after the fourth rejection of deck 05 slide 1)

1. Don't let the organic reference decide her body. The reference gives camera, light, place, framing and outfit only; her body comes from the benchmark. Why: when the reference girl was flat or wiry, the model copied her, four times.
2. Don't attach the organic reference photo to a body shot in the `character_new_image` workflow. Attach only her character reference, the physique anchor and the benchmark, and pass the reference's style as text. Why: an attached flat body outweighs any words. The newer exception (captain, 2026-09-22) is the `character_replaces_person` workflow in `core/skills/image-prompt/SKILL.md`: there the organic photo is attached with its face and body under `must_not_transfer`, and the anchor and benchmark are still attached. If the source body leaks in, redo the slide without the photo.
3. Don't keep a reference pose that hides her body. Use a three-quarter back angle, a slight hip pop and a visible chest; a flat side profile fails. Why: the hook sells the body, and a pose that hides it fails the job even when it matches the reference.
4. Don't accept "it matches the reference" in review. Her body is judged only against the benchmark. Why: the reviewer compares to a picture, not to words, and the reference is not the target.

### Props and details

- Don't treat the phone case as part of her body, and don't force her phone into a picture. The case shows only in a mirror selfie, where the phone's back faces the mirror. A front-camera selfie shows no phone (the phone is the camera); a scrolling scene shows the phone edge-on with the screen toward her. Why: the case was once listed with her hair and skin, and every face prompt then forced a phone held camera-out into the picture, even on a couch (captain, 2026-09-19: "why are you forcing the phone into every pic").
- Don't put her phone or the leopard case into a picture that does not show her face or body. Why: on the walking-pad slide the generator turned an iPad into a leopard "phone" with the pattern painted on the bezel.
- Don't attach the case reference except to mirror-selfie calls, and never let its hand, nails or rings transfer. Why: the case crop comes from a real person's photo; only the case belongs to her.
- Don't give the leopard case or her headphones to another account's character. Why: another account's casting render inherited the leopard case and was marked non-canonical for it.
- Don't render two sets of headphones. One pair, on her head or around her neck, never both. Why: the generator kept adding a second pair (twice on deck 03 slide 1, and again in later rounds) and each needed an edit.
- Don't attach `grace-final-leopard-case.png` as it is. Attach `grace-ref-no-watch.png`. Why: the approved picture shows a smartwatch on her left wrist, the captain banned watches, and a watch in a reference ends up in the image.
- Don't crop tighter than the source photo when remaking one of her pictures. Why: a closer crop was rejected as "too close to screen" (captain, 2026-09-17).

## Voice

- Lowercase, casual and spoken, with her typos kept: "your" for "you're", "ur", "im", "cant", "heres", "legit", "ez".
- One word in caps for emphasis: "i KNOW", "NOTHING was moving", "cardio AFTER".
- First person for proof ("heres proof", "this was me"), second person for instructions ("your parking as close as you can").
- A short pointer line ending in `>>>` leads into the value slides ("what actually worked >>>").
- An aside is its own short line with "!!" ("free steps!!!"), used rarely.
- The captain writes her titles, and his words are final. His style: one spoken lowercase sentence, a concrete noun (steps, legs, fat), often a twist at the end: "i didn't want to get 10k steps today but...", "why you're not hitting your steps (it's not your legs)", "want to lose fat but nothing is working? this is what i did", "how i get my steps in as a phone addict".
- The CTA lines are his too, and may keep his brackets: "use excerlock to make your phone block apps if your not moving. i legit cant scroll unless im walking around (works on the treadmill!!)".
- Deck 01 is in sentence case because it predates this voice; new decks are lowercase.

## Assets

Her reference pictures, physique anchor, body benchmark and case reference: `accounts/zoey/assets.md`.
