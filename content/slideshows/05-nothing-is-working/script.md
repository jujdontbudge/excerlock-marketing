# Slideshow 05 - want to lose fat but nothing is working? this is what i did, 6 slides

Written to `research/slideshows/script-writing-guide.md` (the captain's walkthrough plus his image and reference preferences). Format: "want X but", so slide 2 is the before picture and every value slide is "this is what i did", in the order value, CTA, value, value. Face photos: 2 (slides 1 and 2), both already in hand, so this deck needs no new face generation. Screenshots: 1 slide (slide 3), plus the captain's CTA screenshot. One organic reference per slide, none repeated in any deck. No Apple Watch in any prompt or reference. Images here are references and prompts only; nothing is generated until the captain says go.

**Our girl.** Character reference `data/slideshow-01-final/images/round8-grace/grace-final-leopard-case.png`: dark blonde hair, slim build, tanned skin with real texture, leopard-print phone case, silver over-ear headphones, no watch (the reference picture shows one on her left wrist; do not carry it into any prompt). Before version (heavier build, white crop top, black leggings): `data/slideshow-01-final/images/round10-before/before-final.png`.

**In hand.** The two pictures above. Steps month view `data/slide5-steps/steps-month-01.png` (Apple Health, Steps, M view, 15,510 average, dark mode). Approved slideshow 01 slide 4 meal-prep photo (stacked black containers of ground turkey, green beans and sweet potato rounds on a granite kitchen counter, flash, nobody in frame) under `data/slideshow-01-final/build/slide-04.jpg` (texted) and its untexted base `data/slideshow-01-final/images/reimagine/gabylrei-1069-s4-gpt2-low-0N.png`. All `data/` paths are the firstmate data folder, as in slideshow 01.

Overlay defaults: native TikTok text look, clean sans, white, soft drop shadow, 9:16, top third unless noted.

---

## Slide 1 (hook, face photo 1 of 2, gym mirror pic)

**On-screen text**
```
want to lose fat but nothing is working?

this is what i did
```

**Organic reference**
- @graceelizabethlifts, https://www.tiktok.com/@graceelizabethlifts/photo/7662822176965266701 (773.8K plays, 104.7K likes, 9.8K saves, captured 2026-09-16), slide 1: full-body mirror selfie in a bright upscale commercial gym, cream machines, wood-look floor, phone over the lower face. Saved as `content/styles/gym-mirror-selfie-bright-commercial.json`; it is the reference behind our approved slideshow 01 slide 1 picture.

**Our variation**
- No generation. Reuse `data/slideshow-01-final/images/round8-grace/grace-final-leopard-case.png` untexted (our girl now, bright gym mirror selfie, phone in the leopard case). This is the "after" the deck pays off, shown first. The picture shows an Apple Watch on her left wrist: before use it needs a `codex_image --edit` pass to remove the watch (captain's rule, no Apple Watch anywhere; the edit needs his go like any generation).
- Text placement: line 1 across the top 12%, 2 lines; "this is what i did" smaller right under it, everything above her head.

---

## Slide 2 (second curiosity pull, the before picture, face photo 2 of 2)

**On-screen text**
```
this was me. gym 5x a week and NOTHING was moving
```
Bottom line, smaller, last 10% of the frame:
```
what actually worked >>>
```

**Organic reference**
- @gelou.fitness "did 10,000 steps daily for 2 weeks" / "lost some fat i guess", https://www.tiktok.com/@gelou.fitness/photo/7620413720165928212 (781.2K plays, 41K likes, 3.6K saves, 2 slides, posted 2026-03-23), slide 1: a heavier gym mirror selfie in a black tee and shorts, phone at chest height, squat racks behind, flat gym light; slide 2 is the same spot two weeks later. The before picture as the reason to swipe.

**Our variation**
- No generation. Reuse `data/slideshow-01-final/images/round10-before/before-final.png` as is (our girl, heavier build, white crop top, black leggings, hallway with warm ceiling light, hand on the banister). The same in-hand picture opens deck 03 slide 2 on the captain's instruction (one consistent before); the reference photos differ.
- Text placement: line 1 centred, top 15%, 2 lines; pointer line small, centred, bottom 8%.

---

## Slide 3 (value 1: what i did, the walking, screenshot 1 of 1)

**On-screen text**
```
i got 10k steps a day. every single day, even rest days

(a walk after dinner + the treadmill after lifting and its done)
```

**Copy source**
- @garely.lifts "top 5 ways to loss weight", https://www.tiktok.com/@garely.lifts/photo/7534922789371825438 (883.6K plays, 109.3K likes, 8.9K saves, 6 slides, posted 2025-08-04), slide 5 (a value slide, not the hook) verbatim: "4. get 10k steps a day". The rest is her saying how, in plain words; the bracket points at slides 6 and deck 03's after-dinner walk.

**Organic reference**
- @lucieengland0 "15,000 steps a day until I'm 70kg UPDATEEESSSS..." / "Mid week updated on the steppies", https://www.tiktok.com/@lucieengland0/photo/7608330902782938390 (96.5K plays, 2.2K likes, 7 slides, posted 2026-02-18), slide 2: full-bleed Apple Health Steps screenshot, W view, AVERAGE 15,118 steps, 15-21 Feb 2026, with "We're going strong this week / Start of the year: 78.8kg / Now: 76.6kg" typed over the chart. A steps screenshot used as fat-loss proof.

**Our variation**
- No generation. Full-bleed real screenshot `data/slide5-steps/steps-month-01.png` (month view, 15,510 average), so the receipt reads as a habit, not one good week.
- Text placement: line 1 centred over the empty upper chart area, about 25% down, 2 lines; bracket smaller under it.

---

## Slide 4 (CTA)

**On-screen text**
```
excerlock blocks my tiktok unless im walking so i legit had no choice

(this is the only reason the 10k actually happened)
```

**Image**
- captain supplies Instagram screenshot

- Text placement: line 1 large, top 12%, 3 lines; bracket smaller under it.

---

## Slide 5 (value 2: what i did, the food)

**On-screen text**
```
i ate in a deficit and hit 1g of protein per lb of bodyweight

you cant lose fat unless your in a caloric deficit, no matter how many steps you walk (protein keeps you full so the deficit doesnt suck)
```

**Copy source**
- @paaofit "fat loss made simple", https://www.tiktok.com/@paaofit/photo/7480192668828699950 (1.0M plays, 115.2K likes, 34.2K saves, 2 slides, posted 2025-03-10), slide 2 "Fat Loss: Most to Least Important": "1 Caloric Deficit - You can't lose fat unless you're in a caloric deficit (burning more calories than you eat)" and "2 Protein Intake - ... Consume 0.7g-1.0g per pound of body weight. Protein helps reduce hunger". Cardio is number 5 on her list.

**Organic reference**
- @gabylrei, https://www.tiktok.com/@gabylrei/photo/7663840390155341069 (233.6K plays, 32.5K likes, 4,750 saves, captured 2026-09-16), slide 4: high-angle phone photo of a loaded barbell lying across a wooden lifting platform with a pink belt and small plates, flat gym light. It is the style source (`data/slideshow-01-final/images/reimagine/gabylrei-1069-s4-source.jpg`) our approved slideshow 01 slide 4 meal-prep photo was reimagined from. No person, no watch.

**Our variation**
- No generation. Reuse the slideshow 01 slide 4 base image (stacked black meal-prep containers of ground turkey, green beans and sweet potato rounds on a granite kitchen counter, kettle and jars behind, flash), untexted, from `data/slideshow-01-final/images/reimagine/gabylrei-1069-s4-gpt2-low-0N.png` (the one used in the build). No face, no person.
- Text placement: line 1 large, top 12%, 2 lines; the explanation block smaller under it, over the kettle and counter above the containers.

---

## Slide 6 (value 3 and last slide: the order at the gym, treadmill pic)

**On-screen text**
```
i lift first and do cardio AFTER. use your energy for your lifting and muscle gains first, then 20 mins incline walk

(this is where a big chunk of the steps come from btw)
```

**Copy source**
- @trainwtaylorx "Cardio tips for burning fat while gaining muscle", https://www.tiktok.com/@trainwtaylorx/photo/7278071181725584686 (964.7K plays, 29.4K likes, 16.7K saves, 4 slides, posted 2023-09-12), slide 2 verbatim: "cardio AFTER a lift / use your energy for your lifting and muscle gains FIRST".

**Organic reference**
- @lift.with.em "How I've lost 5kg in the last 1&1/2 months", https://www.tiktok.com/@lift.with.em/photo/7637215971492580630 (327.3K plays, 10.6K likes, 9.3K saves, 2 slides, posted 2026-05-07), slide 1 "My ~25 min~ Incline Treadmill Routine you NEED (For fat loss)": phone photo from behind of her walking on a treadmill in a commercial gym, black tee, blue shorts, white socks and trainers, blonde ponytail, the treadmill console and a dark gym wall with the gym's name ahead, flat gym light. Looks like a friend took it mid-walk. No face, no watch.

**Our variation**
- Style: digest @lift.with.em slide 1 with `skills/style-clone.md` (proposed slug `liftwithem-0630-s1-treadmill-from-behind`), polish: raw. No face.
- Prompt: phone photo from behind of our girl walking on a treadmill in a commercial gym, oversized black tee, black bike shorts, white socks and trainers on the moving belt, dark blonde ponytail, silver over-ear headphones on, bare arms holding the handrails, the console readouts and a dark gym wall ahead, a rack of dumbbells at the edge, flat overhead gym light, motion softness on her legs, slight tilt, shot on iPhone main 24mm, Smart HDR, 9:16, no film grain, no DSLR look, no readable brand logos, no watch
- Text placement: line 1 large, top 12%, 4 lines over the wall above her head; bracket smaller under it.
