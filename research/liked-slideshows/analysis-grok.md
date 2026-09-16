# Liked slideshows analysis (Grok lane)

**Scope:** 12 liked TikTok photo posts (54 slides), captured 2026-09-16 from the account Liked tab. Sources: private corpus `manifest.json` (not committed), `transcript.md`, and direct reads of slide JPGs under `private corpus (images not committed)/<post-id>/tiktok/`. Rejected script: `content/slideshows/01-lose-weight-6-months/script.md`.

**Method:** Cleaned on-image caption text from OCR (pipes treated as line breaks; product labels, watermarks, machine UI, App Store chrome ignored unless the creator is clearly pointing at that product). Word counts use alphanumeric tokens only. Image types come from opening the JPGs, not from OCR alone.

**Caveat (once):** Public counters on each post are a single capture. They are not evidence that a caption style converts or performs. This report is about what the account owner liked in writing and framing, not about ranking.

**Image access:** Model can read images. Sampled all 12 hooks plus story, food, product, machine-console, and App Store payoff slides.

---

## 1. Per-post breakdown

| post id | creator | hook (slide 1) | structure | slides | words/slide (min-max, typical) | what slides give | image types | text vs image |
|---|---|---|---|---|---|---|---|---|
| 7530050457604050181 | bodybymij | 8 things I wish I knew as a beginner in the gym | numbered list | 9 | 3-29, typ ~12 | tip/rule each; #8 vitamins+water | gym selfies / gym backdrop; product clutter on last | mostly vibe gym backdrop; tip is text-first |
| 7581568072968981793 | yermospam | 6 rules for gym motivation and gains that actually get results. | numbered list + closer | 7 | 10-27, typ ~16 | rule + short reason; last = feeling/memory | gym / physique vibe shots | text carries; image is lock-in aesthetic |
| 7597280332546673975 | haifa.munster | how i stay disciplined as a gym girl | how-I list | 6 | 8-13, typ ~9 | habit tip each; last = why/feeling | locker-room / gym mirror selfies | related: she is the gym-girl proof |
| 7660406966996471070 | bymaddiefit | I've been consistent in the gym for 6 years & here's what no one tells you: | how-I essay tips + product | 6 | 15-45 on text slides; slide 6 is App Store UI | long reason/reframe; product Hevy on 5-6 | gym selfies; slide 6 screenshot | text heavy; product UI is the proof |
| 7455384522960440608 | mostofmeg | incorporating steps into a busy lifestyle / how to walk 10k steps a day | how-to + numbers | 2 | 13-38 | slide 2 = concrete schedule with step counts | lifestyle / walk vibe | text is the value; image supports busy life |
| 7441340934559943982 | autumn.wlf | "i want to walk 10k steps a day but idk what to do" | problem quote + cheat sheet | 2 | 13-69 | slide 2 = numbers, times, mph, example blocks | gym mirror crop + bottle | hook is problem; payoff is text card density |
| 7663840390155341069 | gabylrei | going 5/5 on gym essentials worth the money | numbered product picks | 7 | 7-39, typ ~31 | named tool + why; last = diet rule | mirror selfie hook; product photos; step watch UI | image = the thing named; text = why |
| 7662638384740928781 | www.reesey | plan a - lose the weight - get my life together | 2-beat story / sign | 2 | 6-9 | goal list then resolve | bedroom full-body then gym mirror (different body as contrast) | image sells before/after fantasy; text is short |
| 7662601047931768095 | myspacegym | I didn't feel like doing cardio today | story beat | 3 | 5-8 | feeling -> proof action -> rule | home mirror selfie; Matrix treadmill console; close face | image proves the claim (console time) |
| 7663689734497111310 | makk.liftss | How fast my problems fade away once I step foot in the gym | single-image | 1 | 13 | feeling only | gym mirror selfie | related vibe |
| 7668802012561034526 | liftwithhannahh | what i eat in a day | meal log | 5 | 5-11 | named food each meal | food in car / real packaging | image is the meal; labels name brands |
| 7673709531523730719 | myspacegym | I didn't have time to go to the gym today :( | story beat | 4 | 3-10, typ ~6 | excuse -> action -> action -> rule | home selfie; gym exterior/app time; console; sweaty close-up + 5:30 AM | image proves early gym; text stays tiny |

### Short notes per post (value + image)

**bodybymij 7530050457604050181**  
- Value: discrete gym beginner tips. Shortest tip is slide 2: `1. Progressive overload` (3 words). Longest useful tip is slide 7 routine (~29 words). Slide 8 `7.888 method always!!!` is slang/method name only.  
- Image: gym girl content; last slide OCR floods with energy-drink and vitamin bottle labels (ignore as product noise except the vitamins line).

**yermospam 7581568072968981793**  
- Value: discipline rules in short stacks (`One more rep. One more kilo.`). Closer is emotional, not a tip: `Remember who you were before the discipline. Remember the doubt.`  
- Image: gym aesthetic backdrops; text-first.

**haifa.munster 7597280332546673975**  
- Value: first-person habits, all under ~13 words. Tone markers: `gym girl`, `locked in`, `no excuses.`, lowercase hook.  
- Image: DFYNE gym fit mirror selfies; text and fit are related on purpose.

**bymaddiefit 7660406966996471070**  
- Outlier long copy (30-45 words). One clear metaphor: `swimming against the tide`. Product named in body: `That's why I log every workout in Hevy.` Slide 6 is pure App Store screenshot for Hevy.  
- Image: gym selfies + store UI.

**mostofmeg 7455384522960440608**  
- Value is a step math recipe: `40 min morning walk (4,000 steps)` etc.  
- Two slides only: title then list.

**autumn.wlf 7441340934559943982**  
- Hook is a quoted complaint with slang `idk`. Payoff is dense numbers (miles, mph, minutes, step ranges). Highest word count in corpus on slide 2 (~69).  
- Image: overhead gym mirror crop with water bottle.

**gabylrei 7663840390155341069**  
- Value: named SKUs (`food scale`, `lifting straps`, `Ninja creami`) + blunt first-person reason. Slide 2 is credibility filler: `and I KNOW what i'm talking about` (little new info).  
- Product sits mid-deck as the list items; last slide pivots to `a healthy diet` rule, not a sixth gadget.

**www.reesey 7662638384740928781**  
- Minimal story: plan bullets then `there was never a plan b.`  
- Images are full-body bedroom then polished gym mirror (transformation fantasy pairing).

**myspacegym 7662601047931768095**  
- Story: no feel -> did it -> rule. Slide 2 image is the treadmill console showing ~59:20 (proof). Mild idea echo: slides 2 and 3 both land on `anyways` / do it anyway.

**makk.liftss 7663689734497111310**  
- One feeling line only. No tip, no product.

**liftwithhannahh 7668802012561034526**  
- Pure specificity: brand + food names, meal labels (`breakfast`, `snack`, `dinner`). Almost no verbs.

**myspacegym 7673709531523730719**  
- Clean story arc: excuse with `:(` -> `so I woke up earlier` -> `and made time` -> `stop making excuses start making solutions`. Proof images (early time, sweat, console). Best model for short human story captions in this set.

---

## 2. Cross-post patterns (counts)

Corpus for counts: 53 caption-bearing slides after dropping pure App Store chrome as "caption" on bymaddiefit slide 6 (UI only). Total JPGs still 54.

### Words per slide
| bucket | count | share |
|---|---|---|
| 1-5 | 6 | 11% |
| 6-10 | 17 | 32% |
| 11-15 | 11 | 21% |
| 16-25 | 6 | 11% |
| 26-40 | 10 | 19% |
| 41+ | 3 | 6% |

- Min 3 (`1. Progressive overload`; `and made time`), max ~69 (autumn cheat sheet), median **12**, mean ~17.  
- **Typical liked multi-slide body copy sits 6-15 words** when the post is story or how-I. Long essays cluster in bymaddiefit + gabylrei product why-paragraphs + the two 10k cheat sheets.

### Sentence count per slide
| sentences (by `.!?`) | slides |
|---|---|
| 1 (or fragment with no terminal punct) | ~40 |
| 2 | 5 |
| 3+ | 8 |

Most slides are one breath: a fragment, one line, or a short stack of fragments without full essay grammar.

### Casing
- Lowercase start / casual lower: ~20 slides (haifa hooks and tips, autumn hook, many myspacegym lines, food labels).  
- Sentence / title mix: ~33.  
- Full caps rare; used as section headers inside cheat sheets (`WALKING 10K STEPS`) or emphasis words (`MOST`, `KNOW`, `PROMISE`).

### Punctuation used
- Periods: common on list rules and story closers.  
- Commas: moderate.  
- Colons: titles and cheat-sheet headers.  
- Quotes: problem-as-quote hooks; dialogue (`"I want to train."`).  
- Parentheses: tip asides (`way better after your workout...`).  
- Exclamation: rare (`always!!!`).  
- Equals: casual equations (`look good= feel good`, `10k steps = 4 to 5 miles`, `No sleep = no progress`).  
- Ampersand: occasional (`Rest & recovery`, `6 years & here's`).  
- Emoji in on-image text: almost none on captions; `:(` text emoticon on 7673709531523730719 slide 1. Profile captions use hearts outside the burn-in.

### Punctuation NOT used
- **Em dashes: 0** in cleaned on-image corpus.  
- **Semicolons: 0.**  
- Ellipsis rare/absent as a style mark.  
- No polished "balanced contrast" punctuation theater.

### Numbering style
- `1.` / `2.` arabic with period (bodybymij, yermospam, gabylrei).  
- Sometimes title promises a count (`8 things`, `6 rules`, `5/5`) then body numbers.  
- Bullet hyphens for plans and step blocks (`- lose the weight`, `- 40 min morning walk`).  
- haifa how-I list: **no numbers**, just parallel short lines.

### Idea repeat across two slides
- **Hard duplicate of the same tip:** none like rejected script 4+5.  
- **Soft echo:** myspacegym 7662601047931768095 slide 2 `so I did it anyways` and slide 3 `who cares how you feel do it anyways` restate the same rule; slide 3 is the abstract version of slide 2.  
- gabylrei slide 2 is hype, not a second essential, before the real list starts.

### Where payoff / product sits
- Mid or late list item with a **named tool** and a plain reason (Hevy on bymaddiefit 5; food scale / straps / Creami / step watch on gabylrei 3-6).  
- Final slide sometimes App Store screenshot (bymaddiefit 6) or a non-product closer (diet rule, remember your why, stop excuses).  
- Product is shown as something already in use, not a pitch deck.

### How last slides end
| ending type | examples |
|---|---|
| Rule / command | `stop making excuses start making solutions`; `who cares how you feel do it anyways` |
| Feeling / identity | `Remember the doubt.`; `remember my "why"...` |
| Practical tip | vitamins/water; healthy diet investment |
| Product UI | Hevy store page |
| Resolve line | `there was never a plan b.` |
| Meal name | `kombucha` / `potato taco bowl` |
| Nothing extra / single slide | makk.liftss ends on the only line |

CTA-as-install is rare on-image. Save/lock-in language lives more in profile captions than burn-in. Reply prompts do not appear in this liked set.

### Top 5 caption shapes (templates + real example)

1. **`[n]. [short tip or name]`**  
   Example: bodybymij slide 2: `1. Progressive overload`

2. **`[n]. [imperative / tip] - [one plain reason]`**  
   Example: bodybymij slide 5: `4. Rest & recovery is key - muscles also grow when you sleep not just when you train`

3. **First-person feeling or excuse (story open)**  
   Example: myspacegym 7673709531523730719 slide 1: `I didn't have time to go to the gym today :(`

4. **`so I [simple past action]` / `and [simple past]` (story hinge)**  
   Example: slide 2-3: `so I woke up earlier` / `and made time`

5. **Named object + blunt why (product/food)**  
   Example: gabylrei on Creami intent: `literally have no urge too Cheat on my diet because of this thing` (OCR typos kept); food log: `okios pro yogurt smoothie` / `nature valley protein bar`

Honorable sixth: **quoted desire + idk**  
`i want to walk 10k steps a day but idk what to do`

---

## 3. Human-statement rules

### DO (write like the liked set)

1. **Budget most body slides at ~5-15 words.**  
   Example: haifa slide 3: `plan the gym into my daily schedule no excuses.`

2. **One job per slide: tip OR proof OR feeling OR named thing, not all four.**  
   Example: myspacegym slide 2 is only the hinge + console proof: `so I did it anyways`

3. **Prefer plain verbs: do, walk, eat, sleep, stick, plan, wake, make, log.**  
   Example: `so I woke up earlier`

4. **Put numbers on the slide when the value is practical.**  
   Example: mostofmeg: `40 min morning walk (4,000 steps)`

5. **Name real foods, methods, apps, tools.**  
   Example: `Hevy`; `Ninja creami`; `oikos pro yogurt smoothie`; `888 method`

6. **How-I voice for lifestyle posts: lowercase i, gym-girl slang OK.**  
   Example: `how i stay disciplined as a gym girl`

7. **Story posts: admit the weak feeling first in plain speech.**  
   Example: `I didn't feel like doing cardio today`

8. **Let the photo carry proof so the caption can stay tiny.**  
   Example: console showing `59:20` under `so I did it anyways`

9. **Close with a short rule or resolve, not a paragraph.**  
   Example: `there was never a plan b.`

10. **Use casual markers sparingly and only if natural: idk, locked in, gym girl, anyways, :(, &.**  
    Example: `if i stay locked in`

11. **Stack fragments more than full essays.**  
    Example: yermospam: `One more rep. One more kilo. One more second.`

12. **Hook slide states problem, count, or identity; it does not explain the system.**  
    Example: `8 things I wish I knew as a beginner in the gym`

13. **When a brand appears, speak like a user: why it stays in the routine.**  
    Example: bymaddiefit: `That's why I log every workout in Hevy. Small improvements add up.`

14. **Typos and messy grammar appear in real posts; polish is not the signal. Clarity is.**  
    Example OCR-real: `your see your progress`; `excercises`; `urge too Cheat`

15. **Parallel list items must differ in content, not just wording.**  
    Example: gabylrei 1 food scale vs 2 straps vs 3 step tracker: different jobs.

### DON'T (and the AI-sounding twin)

1. **Don't burn 25-40 words explaining a vibe the photo already shows.**  
   Liked: `and made time`  
   AI twin: `so i redesigned my morning around intentional movement and protected my training window`

2. **Don't run two slides that restate the same mechanism.**  
   Liked contrast: autumn slide 1 problem vs slide 2 full numbers (new info)  
   AI twin: slide 4 lock rule + slide 5 same lock rule with brand name

3. **Don't use em dashes or semicolon essay glue.**  
   Liked: periods, short lines, occasional hyphen lists  
   AI twin: `the gym was fine [em dash] my phone wasn't`

4. **Don't do clever balanced contrasts as the whole caption.**  
   Liked blunt: `I didn't feel like doing cardio today`  
   AI twin: `the gym was fine. my phone wasn't`

5. **Don't reframe with coach-speak: never the problem, the real enemy, silent killer.**  
   Liked: names the behavior (`cardio`, `time`, `excuses`)  
   AI twin: `the weights were never the problem`

6. **Don't stack corny metaphors (tide, journey, monster, unlock your potential as poetry).**  
   Liked mostly literal; the rare metaphor (bymaddiefit tide) sits inside a long outlier essay, not the short story posts this account should copy for hooks.  
   AI twin: `i stopped swimming against the tide of my notifications`

7. **Don't write job-interview "non-negotiable / flow state / compounds over time" unless matching a long essay creator (and even then the owner rejected AI tone).**  
   Liked short closer: `no excuses.`  
   AI twin: `movement became a non-negotiable identity practice`

8. **Don't explain the product architecture in caption.**  
   Liked product speak: named tool + one user reason  
   AI twin: `selected scrolling apps stay blocked until an active walking condition resolves`

9. **Don't force you-path CTA essays on every closer.**  
   Liked: rule, feeling, or food  
   AI twin: `ready to reclaim your steps? drop a goal and start your journey today`

10. **Don't synonym-pad (`actually`, `simply`, `truly`, `just` piled for rhythm).**  
    Occasional `actually` exists in long tips; short posts skip filler.  
    AI twin: `i simply made walking the thing that actually unlocks my apps`

11. **Don't use title-case poetic lines.**  
    Liked: `stop making excuses start making solutions` (two short commands)  
    AI twin: `Stop Making Excuses. Start Designing Solutions For Your Future Self.`

12. **Don't hide specificity behind abstract nouns (consistency, discipline, intention) with no object.**  
    Liked: `stick to workouts and excercises that i actually enjoy`  
    AI twin: `align your routine with sustainable discipline`

13. **Don't open slide 2 with a thesis about society or phones.**  
    Liked slide 2 after a pain hook is usually first tip or first action.  
    AI twin: `in a world of endless scrolling our recovery is broken`

14. **Don't make every slide a complete grammatical paragraph with subject-verb polish.**  
    Liked food slide: `snack` + `chicken salad on a croissant`  
    AI twin: `For my afternoon snack I enjoy a measured portion of chicken salad served on a flaky croissant.`

15. **Don't add brand voice adjectives (seamless, effortless, powerful, game-changing).**  
    Liked: `worth the money`, `I KNOW what i'm talking about`  
    AI twin: `a seamless system that effortlessly locks distracting apps`

---

## 4. AI tells in the rejected script (slides 2-5 + alternates)

Rejected source: `content/slideshows/01-lose-weight-6-months/script.md`. Hook on slide 1 is owner-chosen and fine as a problem line. Issues start after.

### Slide 2: `the gym was fine. my phone wasn't`
- **Why it fails the corpus:** Clever antithesis / chiasmus. Liked pain lines name a feeling or excuse in first person (`I didn't feel like...`, `I didn't have time...`), not a witty split grade of gym vs phone.  
- **Also:** Zero concrete next fact; pure reframe.  
- **Human-ish single-line example (not a full rewrite of the deck):** `i'd train then sit on my phone for hours`

### Alternate 2a: `lifting didn't fix the hours i sat scrolling`
- Closer to human (plain verbs, specific behaviors) but still a bit thesis-like and long for a story beat. Would sit nearer gabylrei/yermospam explanation length than myspacegym hinges.  
- Better direction already than the main slide 2.

### Alternate 2b: `i trained hard then undid it on my phone`
- More corpus-like: first person, sequence, no metaphor. Still slightly slogan-smooth; liked speech is bumpier (`did it anyways`, `idk`).

### Slide 3: `so i made walking unlock my apps`
- **Good:** `so i` hinge matches `so I woke up earlier` / `so I did it anyways`.  
- **Weak:** "made walking unlock" is product-mechanism poetry. Liked product lines name the object and the user outcome (`log every workout in Hevy`, `no urge to cheat... because of this thing`), not the abstract unlock grammar.  
- **Human-ish example:** `so i locked my apps until i walk`

### Slide 4: `tiktok stays locked till i'm actually walking`
- Specific app name is good (corpus loves names).  
- **Problem with pair 4+5:** Same idea as slide 5 (lock until walk). That is the exact failure mode the owner called out and the soft-echo we only barely saw once in liked data.  
- Slide 4 should have been new value (proof UI, step number, time of day, what she does while locked), not a restatement.

### Slide 5: `excerlock just locks mine till i walk. your daily step goal?`
- Brand drop is fine if late and user-voiced.  
- **Tells:** `just` softener; second clause is a research-style reply CTA not seen on-image in this liked set; repeats slide 4 mechanism.  
- Liked closers prefer command or resolve without survey prompt.  
- **Human-ish example of the brand clause only:** `i use excerlock so tiktok stays locked till i walk`

### Alternate 5a: `found excerlock mid-walk. drop your step goal`
- `found ... mid-walk` is slightly ad-story. `drop your step goal` is platform-CTA voice absent from liked burn-ins.

### Alternate 5b: `apps unlock only while i walk. your step goal?`
- Again mechanism + CTA; same idea third time.

### Cross-cutting AI patterns in this script
| pattern | where | corpus conflict |
|---|---|---|
| Contrast couplet | slide 2 | not how liked pain is phrased |
| Mechanism narration | 3-5 | product shown as used tool, not explained system |
| Duplicate idea | 4 and 5 (+ alt 5) | lists and stories advance |
| Reply CTA on-image | 5 | not in liked burn-in endings |
| Over-clean parallel grammar | 2, 5 | liked fragments and messy speech |
| No number on a steps/fat-loss story | whole deck | 10k posts and meal posts lead with numbers/names |
| Mood-only middle without tip or proof | 2 | middle slides usually tip, number, or proof photo |

---

## 5. What the 6-month hook should look like (shape only)

**Hook (given):** `I couldn't lose weight for 6 months in the gym then I started doing this`  
Fits corpus hooks that open unresolved effort + curiosity (`8 things I wish...`, `I've been consistent... here's what no one tells you`, problem quotes). Keep as slide 1. Do not explain the product on slide 1.

### Recommended 5-slide shape

| slide | job | word budget | value the viewer must get |
|---|---|---|---|
| 1 | hook only | already set (~16 words) | unresolved gym story |
| 2 | concrete failure mode after gym (behavior, not clever contrast) | 6-12 | one clear leak: scrolling, snacking, zero steps, sitting; first person |
| 3 | first action she started (walk / steps), still pre-brand or light | 5-12 | what she did, maybe a number (steps, minutes) |
| 4 | proof or rule that is NEW vs 3 (UI lock screenshot, named app blocked, or time she walks) | 5-12 | evidence; not a second explanation of the same lock sentence |
| 5 | user-voiced product + hard close (rule or resolve). Optional soft ask only if needed for comments; prefer rule | 6-14 | name ExcerLock once as something she uses; do not restate slide 4 |

**Where product appears:** Once, late (slide 4 image proof and/or slide 5 one clause), like Hevy or Creami: used tool, not lecture.

**Last slide ending:** Prefer command/resolve in the myspacegym / reesey family (`stop making excuses...`, `there was never a plan b.`) over `your daily step goal?` unless comment strategy demands a fill-in. If asking, keep it three words max and after the human rule.

**Voice:** First person, mostly lowercase ok, plain verbs, no em dashes, no metaphors, no "the X was never the problem."

### Closest liked models
1. **myspacegym 7673709531523730719** (primary): excuse -> small actions -> short rule; tiny word counts; photos prove the claim. Best template for "I couldn't... then I started doing this" as a lived sequence.  
2. **myspacegym 7662601047931768095**: feeling -> proof console -> rule. Shows how slide 2 image can do heavy lifting.  
3. **autumn.wlf / mostofmeg**: if a slide must teach steps, put **numbers** on that one slide only, dense and practical.  
4. **gabylrei / bymaddiefit product beats:** one named tool + one selfish reason, not architecture.  
5. **haifa.munster:** word budget and how-I tone for any habit lines.

**Avoid modeling the whole deck on bymaddiefit essay length** even though it was liked; those 40-word slides are the opposite of the owner's "minimal words" rejection notes.

---

## Evidence index

- Transcript path: private corpus `transcript.md` (not committed)  
- Manifest path: private corpus `manifest.json` (not committed) (12 posts, 54 slides)  
- Rejected script path: `content/slideshows/01-lose-weight-6-months/script.md`  
- Commands: Python word/punct pass over cleaned OCR; direct image reads of hooks and story/product/food slides under `(local sample copies)/` copies from manifest paths  
- Background files named in the task notes were not re-summarized; product truth assumed from the task notes (apps unlock under gym / time / walking / steps conditions)

---

## Recommendations for the script-writing task

1. Keep slide 1 hook unchanged.  
2. Rewrite 2-5 under the DO/DON'T lists; kill slide 4/5 duplication.  
3. Target median ~8-12 words on story slides; allow one denser slide only if it is pure numbers.  
4. Show lock UI in the image; say almost nothing about how the system works in text.  
5. Prefer myspacegym story rhythm over yermospam motivational essay rhythm for this hook.  
6. Treat counters as non-evidence. Treat this liked set as a taste board for human caption voice.

---

## Completion

Analysis-only deliverable. No script rewrite. No product-policy choice is blocked; the downstream writing task can apply these rules as-is.
