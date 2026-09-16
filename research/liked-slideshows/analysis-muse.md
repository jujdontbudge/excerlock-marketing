# Liked slideshows analysis (Muse Spark analyst)

## What was done

Studied the 12 liked TikTok photo posts in `private corpus (images not committed)/` (manifest + transcript, captured 2026-09-16), 54 slides total. Ran word and sentence counts over the manifest OCR text with a small Python script, read the rejected script at `content/slideshows/01-lose-weight-6-months/script.md` (slides 1-5 plus alternates), and viewed 3 slide images directly to confirm the visual language (mirror selfie, machine screenshot, food photo). This model does accept image input; the 3 viewed images matched what the OCR implies, and the remaining image types below are inferred from OCR text plus those views.

Note on evidence: public counters in the manifest are single-capture observations, not evidence that a caption style performs. Nothing below claims a style works because of views or likes.

No em dashes appear in this report, per the task notes.

## 1. Per-post breakdown

| Post (handle / id) | Hook (slide 1) | Structure | Slides | Words/slide (typical) | Image types / text-image relation |
|---|---|---|---|---|---|
| @bodybymij 7530050457604050181 | "8 things I wish I knew as a beginner in the gym" | numbered list | 9 | 3 to 29, typical 13 to 20 | gym selfies, vibe backdrops; text carries the value, image is backdrop |
| @yermospam 7581568072968981793 | "6 rules for gym motivation and gains that actually get results." | numbered rules list | 7 | 10 to 26, typical 16 to 25 | dark gym photos, vibe backdrops; text carries the value |
| @haifa.munster 7597280332546673975 | "how i stay disciplined as a gym girl" | how-I list, unnumbered | 6 | 8 to 14, typical 9 to 12 | mirror selfies in gym (viewed slide 1: full body mirror selfie, headphones, black outfit); text is overlay on selfie, loosely related |
| @bymaddiefit 7660406966996471070 | "I've been consistent in the gym for 6 years and here's what no one tells you:" | how-I story with long slides | 6 | 16 to 45 (slide 6 is an app screenshot, product labels excluded), typical 32 to 45 | gym selfies plus one app store screenshot; screenshot is proof for the Hevy tip |
| @mostofmeg 7455384522960440608 | "incorporating steps into a busy lifestyle / how to walk 10k steps a day" | single tip, 2 slides | 2 | 13 and 39, typical n/a | outdoors walk photo; slide 2 is a schedule that matches the walking photo |
| @autumn.wlf 7441340934559943982 | "i want to walk 10k steps a day but idk what to do" | single tip, 2 slides | 2 | 13 and 69, typical n/a | text card style; slide 2 is a dense cheat sheet |
| @gabylrei 7663840390155341069 | "going 5/5 on gym essentials worth the money" | numbered product list | 7 | 7 to 46 (slide 6 has heavy product label noise), typical 28 to 49 | product photos (food scale, straps, watch, Ninja Creami, groceries); text names the exact item in the photo, related |
| @www.reesey 7662638384740928781 | "plan a / - lose the weight / - get my life together" | story, 2 beats | 2 | 9 and 6 | gym mirror selfie; text is a feeling overlay, image is vibe |
| @myspacegym 7662601047931768095 | "I didn't feel like doing cardio today" | story, 3 beats | 3 | 7 to 9, typical 8 | gym plus stair machine screen photo; slide 2 photo is the proof of doing it anyway |
| @makk.liftss 7663689734497111310 | "How fast my problems fade away once I step foot in the gym" | single image feeling | 1 | 15 | gym selfie video still; text is pure feeling overlay |
| @liftwithhannahh 7668802012561034526 | "what i eat in a day" | meal log | 5 | 6 to 25 (labels excluded), typical 6 to 10 of real caption | food photos (viewed slide 2: car lap with Oikos Pro smoothie and Nature Valley bar, caption labels each item); text names what is pictured, fully related |
| @myspacegym 7673709531523730719 | "I didn't have time to go to the gym today :(" | story, 4 beats | 4 | 6 to 15, typical 6 to 10 | gym plus machine screen photos (viewed slide 3: Matrix display 37:26, 5:28 AM overlay, "and made time"); photo is the proof |

What each slide gives the viewer, post by post:

* bodybymij: each slide one gym rule plus a short reason in parentheses or after a hyphen. Slides 2-9 all deliver a tip.
* yermospam: each slide one rule plus 2-4 short supporting lines. Slide 7 gives a feeling ("Remember who you were before the discipline. Remember the doubt.") instead of a tip.
* haifa.munster: each slide one short discipline habit. All feeling or habit, no numbers.
* bymaddiefit: slides 2-5 each give one reframe plus explanation (consistency, people, perspective, tracking). Slide 6 is product proof (Hevy screenshot).
* mostofmeg: slide 2 gives the whole schedule with minutes and step counts. Pure numbers value.
* autumn.wlf: slide 2 gives baseline math (miles, mph, minutes) plus examples. Pure numbers value.
* gabylrei: slides 3-7 each name one product plus why it is worth it. Slide 2 ("and I KNOW what i'm talking about") gives nothing, it is a credibility beat.
* www.reesey: slide 1 states the plan, slide 2 closes it. Feeling only, no tip.
* myspacegym (cardio): slide 2 is proof (machine screen), slide 3 is the moral. Feeling plus proof.
* makk.liftss: single feeling line, nothing actionable.
* liftwithhannahh: slides 2-5 each name the exact foods for one meal. Pure specificity value.
* myspacegym (time): slides 2-3 are proof (4:49 wake, 5:28 AM machine screen), slide 4 is the moral. Proof plus feeling.

## 2. Cross-post patterns with counts

Counts below are over all 54 slides, using cleaned OCR text (product labels, watermarks, UI junk excluded where obvious; garbled tokens marked).

Words per slide (caption words only): 1 slide at 3 words (bodybymij slide 2, "1. Progressive overload"); short story beats of 6 to 10 words on 12 slides (both myspacegym posts, haifa slides, reesey, hannah food labels); mid tips of 11 to 20 words on about 20 slides (bodybymij, yermospam, haifa); long explainers of 25 to 45 words on about 10 slides (bymaddiefit slides 2-5, gabylrei product slides); dense cheat sheets of 40 to 70 words on 3 slides (mostofmeg slide 2 at 39, autumn.wlf slide 2 at 69, gabylrei slide 6 with label noise). Typical liked slide: 8 to 20 words. Only the long-form explainers and cheat sheets pass 30 words, and those are the posts with the most concrete numbers.

Sentence count per slide: 1 sentence on roughly 30 of 54 slides (all story beats, all food labels, most haifa slides, hooks); 2 sentences on roughly 12 slides (bodybymij tips with reason after hyphen); 3-4 short fragments on roughly 10 slides (yermospam rules, bymaddiefit explainers). Fragments joined by periods dominate: "Meal prep. Enough variety. Water daily." (yermospam slide 5).

Casing: sentence case or normal capitalization on about 30 slides; full lowercase on about 12 slides (haifa "how i stay disciplined as a gym girl", "wear a cute gym fit", autumn hook "i want to walk 10k steps a day but idk what to do", hannah "what i eat in a day", "chicken salad on a croissant"); ALL CAPS emphasis on about 6 slides or headers (autumn slide 2 "WALKING 10K STEPS:", yermospam "Eat Clean", "Sleep Like It Is Your Job", gabylrei "I KNOW", "PROMISE"). Mixed case inside one post is normal.

Punctuation used: periods (fragment separators, everywhere); commas (bymaddiefit, gabylrei); colons (autumn "baseline:", "time required:", hannah "breakfast" implied); parentheses for asides (bodybymij "way better after your workout for muscle growth", "it'll create the hourglass shape illusion"); quotes (yermospam 'Do not say "I want to train." Say "I train."', haifa 'remember my "why"'); exclamation (bodybymij "7.88 method always!!!"); emoji/symbols (":(" on myspacegym time slide 1, "=" in "look good= feel good", bullets on step schedules); digits and units everywhere (10k, 4,000 steps, 7 to 8 hours, 6 reps, 3.0 mph). NOT used: em dashes appear on zero slides; semicolons appear on zero slides. Hyphens are list dashes or plain joins ("Rest and recovery is key - muscles also grow", "plan a - lose the weight"). The corpus never uses contrast colons or literary punctuation.

Numbering style: numbered lists on 4 of 12 posts (bodybymij "1. 2. 3.", yermospam "1. 3. 4. 5.", gabylrei "1. 2. 3. 4. 5."). Numbers are plain digits with a period. No post numbers every slide with fancy formatting.

Repeated ideas: yes, one clear case. In the rejected script slides 4 and 5 overlap, and inside the liked corpus the closest repeat is bymaddiefit slides 2 and 4 (both say consistency as identity: slide 2 "getting back to it regardless" vs slide 4 "non negotiable, part of your life"), but they frame different angles (recovery vs identity) so they pass. The gabylrei post keeps all 5 products distinct. Rule from the corpus: numbered siblings must each add a new noun or number; no two slides share the same payload.

Where the payoff or product sits: late and small. Hevy appears only on bymaddiefit slide 5 as one clause ("That's why I log every workout in Hevy") plus a slide 6 screenshot, never as the point. Products in gabylrei and hannah are the content itself, named plainly with no pitch verbs. No post opens with a product.

How the last slide ends: sign-off or moral on 5 posts (yermospam "Remember the doubt.", haifa "feel more confident", myspacegym cardio "do it anyways", myspacegym time "stop making excuses start making solutions", gabylrei "no excuses"); pure value with no closer on 4 posts (bodybymij water tip, mostofmeg schedule, autumn cheat sheet, hannah dinner); feeling line on 2 posts (reesey "there was never a plan b.", makk single slide); app screenshot with no caption close on 1 post (bymaddiefit slide 6). Zero posts end with a question or a reply CTA. Zero posts ask the viewer to comment a number.

Top 5 caption shapes with real examples:

1. "[number]. [imperative verb] [object]" -> "3. Prioritize your eating" (bodybymij slide 4, post 7530050457604050181)
2. "[imperative]. [imperative]. [imperative]." (fragment chain) -> "Meal prep. Enough variety. Water daily." (yermospam slide 5, post 7581568072968981793)
3. "[how-I statement, lowercase]" -> "wear a cute gym fit" (haifa slide 2, post 7597280332546673975)
4. "[minutes] [walk slot] ([steps])" schedule line -> "40 min morning walk (4,000 steps)" (mostofmeg slide 2, post 7455384522960440608)
5. "[meal word] + [exact food names]" -> "chicken salad on a croissant" (hannah slide 4, post 7668802012561034526)

## 3. Human-statement rules

### DO (12 rules)

1. DO keep story beats at 6 to 10 words. Example: "who cares how you feel do it anyways" (myspacegym 7662601047931768095 slide 3).
2. DO keep tip slides at roughly 8 to 20 words with one reason attached. Example: "Don't skip cardio (way better after your workout for muscle growth)" (bodybymij 7530050457604050181 slide 3).
3. DO put one idea and one noun per slide. Example: "1. Progressive overload" (bodybymij slide 2) is a full slide with 3 words.
4. DO use plain imperative verbs: eat, sleep, walk, prep, log, wear, plan, stick, stop, start. Example: "Sleep Like It Is Your Job" (yermospam slide 6).
5. DO name exact numbers with units. Example: "40 min morning walk (4,000 steps)" (mostofmeg slide 2); "7 to 8 hours" (yermospam slide 6); "Minimum 6 reps with clean form" (yermospam slide 3).
6. DO name exact foods and products with brand names, no pitch verbs. Example: "okios pro yogurt smoothie" and "nature valley protein bar" as plain labels next to the photo (hannah slide 2); "1. a food scale" (gabylrei slide 3).
7. DO name exact apps as plain nouns late in the post. Example: "That's why I log every workout in Hevy." (bymaddiefit slide 5).
8. DO mix voices: first person for story ("I didn't feel like doing cardio today"), imperative for rules ("Eat Clean"), "you" only inside reasons ("what you eat is way more important"). Example set: myspacegym 7662601047931768095 slide 1 vs yermospam slide 5 vs bodybymij slide 4.
9. DO use the account's tone markers sparingly: lowercase ("how i stay disciplined as a gym girl"), "girl" ("gym girl"), "lock in" / "locked in" ("stay locked in", haifa slide 4), "idk" ("but idk what to do", autumn slide 1), "no excuses" (haifa slide 3, gabylrei slide 7). One marker per slide max.
10. DO state feelings in flat short lines with zero decoration. Example: "there was never a plan b." (reesey slide 2); "so I did it anyways" (myspacegym cardio slide 2).
11. DO let the photo prove the claim instead of explaining it. Example: "and made time" over a 5:28 AM machine screen showing 37:26 (myspacegym time slide 3, post 7673709531523730719); "breakfast" over the pictured foods (hannah slide 2).
12. DO make slide 1 a plain promise or a raw feeling, longer or shorter than the rest. Example list style: "8 things I wish I knew as a beginner in the gym" (bodybymij); feeling style: "I didn't have time to go to the gym today :(" (myspacegym time). Slide 1 never contains the mechanism.

### DON'T (12 rules)

1. DON'T use em dashes or semicolons. They appear on zero of 54 slides. AI version: "Walking fixed everything; my discipline followed." Human version: "I started walking every day. It stuck."
2. DON'T write contrast reframes ("The X was fine, the Y wasn't" / "X was never the problem"). Zero liked slides use this shape. AI version: "The gym was never the problem." Human version: "I trained 4 days a week. Still no change."
3. DON'T use metaphors, analogies, or sayings. Zero liked slides compare anything to anything else (no tides, journeys, locks as metaphors; the one "swimming against the tide" line in bymaddiefit slide 3 is the single exception and it is quoted, not the point). AI version: "Your phone is an anchor on your fat loss." Human version: "I scrolled 2 hours after every workout."
4. DON'T stack two clauses that say the same thing in one slide. AI version: "tiktok stays locked till i'm walking, my apps unlock only while i walk." Human version: "tiktok stays locked till i walk."
5. DON'T give two slides the same payload. Corpus rule: every numbered sibling adds a new noun. AI version: slide 4 states the lock rule, slide 5 restates the lock rule with the brand. Human version: slide 4 the rule, slide 5 the proof (a morning step count).
6. DON'T explain the mechanism. Liked slides give the rule plus at most one short reason, never how it works. AI version: "it locks your apps until your pace sensor confirms active walking." Human version: "it stays locked till i walk."
7. DON'T pitch the product with verbs like unlock, transform, supercharge, or found. Products appear as nouns ("Hevy", "a food scale", "Ninja creami"). AI version: "found excerlock mid-walk." Human version: "i use excerlock."
8. DON'T end with a question or a comment CTA. Zero liked posts end with one. AI version: "your daily step goal?" Human version: "10k a day. no excuses."
9. DON'T write more than 20 words on a story or rule slide. Typical liked slide is 8 to 20 words; only schedules and long explainers go longer. AI version: a 25 word slide with setup plus payoff. Human version: cut to the rule plus one number.
10. DON'T use all-lowercase activism or all-caps preaching for more than a word or two. Markers like "PROMISE" and "KNOW" work once per post (gabylrei), never as the whole voice. AI version: "stop making excuses and start making solutions every single day." Human version: "stop making excuses start making solutions" (myspacegym time slide 4).
11. DON'T open slide 1 with the product or the trick. Every liked slide 1 is a promise ("6 rules", "what i eat in a day") or a feeling, never a mechanism. AI version: "so i made walking unlock my apps" as slide 2 is fine; as slide 1 it would break the pattern.
12. DON'T decorate with quotes around plain words or stack emoji. Quotes in the corpus mark spoken lines or a real "why", not emphasis. AI version: '"discipline" days'. Human version: "no excuses."

## 4. AI tells in the rejected script (slides 2-5 plus alternates)

Slide 2: "the gym was fine. my phone wasn't." This is the contrast reframe shape. Zero of 54 liked slides use "X was fine, Y wasn't". Liked feelings are flat statements ("I didn't feel like doing cardio today", "I didn't have time to go to the gym today :("). Human version of this line: "i trained 5 days a week. scrolled all night."

Slide 3: "so i made walking unlock my apps." Two problems. First, "so I" plus a mechanism reveal reads as a setup line; liked posts never narrate the trick, they state the rule ("40 min morning walk (4,000 steps)", "3. Prioritize your eating"). Second, it carries no number or noun the viewer can copy. Human version: "i walk 40 min every morning."

Slide 4: "tiktok stays locked till i'm actually walking." The word "actually" is filler no liked slide uses for emphasis; liked emphasis is caps on one word ("KNOW", "PROMISE") or nothing. Also this slide plus slide 5 restate one idea (the lock rule twice), which breaks the corpus rule that numbered siblings each add a new noun. Human version: "tiktok stays locked till i walk."

Slide 5: "excerlock just locks mine till i walk. your daily step goal?" Two problems. "just" minimizes in a way no liked product line does (liked lines: "That's why I log every workout in Hevy", "1. a food scale"). The trailing question is a reply CTA; zero liked posts end with a question. Human version: "i use excerlock. 10k a day."

Alternate slide 2a: "lifting didn't fix the hours i sat scrolling." Contrast shape again, plus the vague noun "hours" where the corpus demands a number. Human version: "i lifted 4 days a week. sat 10 hours a day."

Alternate slide 2b: "i trained hard then undid it on my phone." "Undid it" is a metaphor-flavored summary verb; liked slides use concrete verbs ("skip", "eat", "sleep", "walk", "log"). Human version: "i trained hard. then scrolled 2 hours."

Alternate slide 5a: "found excerlock mid-walk. drop your step goal." "Found" as a discovery verb plus an imperative CTA; no liked post narrates finding a product or orders a reply. Human version: "excerlock on. 10k a day."

Alternate slide 5b: "apps unlock only while i walk. your step goal?" Same double problem as slide 5: restates slide 4's rule, then ends with a question. Human version: "apps stay locked till i walk."

## 5. Shape for the 6-month hook (describe, do not write)

Hook: "I couldn't lose weight for 6 months in the gym then I started doing this". This matches the liked hook pattern: first person, plain past tense, a time span plus a promise, no mechanism (closest models: bymaddiefit "I've been consistent in the gym for 6 years and here's what no one tells you", bodybymij "8 things I wish I knew as a beginner in the gym", myspacegym time "I didn't have time to go to the gym today :(").

Slides 2-5 for a 5-slide version, one payload each:

* Slide 2: the old routine as flat facts with numbers (days trained, what happened anyway). Value: recognition. Budget 8 to 12 words. Model: myspacegym story beats.
* Slide 3: the one new walking rule with minutes and steps. Value: a copyable rule. Budget 8 to 15 words. Models: mostofmeg slide 2, autumn slide 2 (numbers only, no mechanism).
* Slide 4: the product as a plain noun inside the rule, or the proof photo (morning screen, step count). Value: proof. Budget 6 to 12 words. Models: bymaddiefit slide 5 plus 6 (one clause plus screenshot), myspacegym time slide 3 ("and made time" over the screen).
* Slide 5: close with a flat moral or sign-off, no question. Value: feeling. Budget 6 to 10 words. Models: "do it anyways" (myspacegym cardio), "stop making excuses start making solutions" (myspacegym time), "there was never a plan b." (reesey).

Product placement: slide 4 only, named once as a noun ("excerlock"), never as the opener and never with pitch verbs. No step totals shown unless from a real capture; no weight figures.

Closest overall models: mostofmeg 7455384522960440608 (walk schedule with minutes and steps, the exact value type this script needs), myspacegym 7673709531523730719 (failed feeling plus timestamped proof plus flat moral, the exact story shape), bymaddiefit 7660406966996471070 (how a product sits in one clause plus a screenshot without becoming the point).

## Evidence and files

* Corpus: private corpus `manifest.json` (not committed) (12 posts, 54 slides) and private corpus `transcript.md` (not committed) (same content, human readable).
* Rejected script: `content/slideshows/01-lose-weight-6-months/script.md` in this the repo copy.
* Counts produced with: `python3` over manifest OCR text (word regex `[A-Za-z0-9']+`, sentence split on `.`/`!`/`?`, manual exclusion of obvious product label and UI tokens). Slide image views: 3 images read directly (haifa.munster slide 1 mirror selfie; myspacegym 7673709531523730719 slide 3 machine screen at 5:28 AM; liftwithhannahh slide 2 food photo); remaining image types inferred from OCR plus those views.
* This analyst runs on Muse Spark. Image input was available and used; no image claim above goes beyond the 3 viewed images plus OCR-implied content.

