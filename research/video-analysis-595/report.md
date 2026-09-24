# Video creative research report — 540 long-running Meta creatives + 55 TikToks over 10,000 views

Date: 2026-09-15 (UTC). Worker: PKG-D synthesis. Spend: **USD 0.00** — no Gemini/API submissions, no paid calls of any kind. This synthesis reads only the signed validated records, not raw output.

## 0. How to read this report (evidence ranks — do not collapse them)

Every finding below carries one of three evidence ranks. They answer different questions and must never be converted into each other:

- **ORGANIC (31 unpromoted TikToks)** — the only genuine organic signal. These 31 posts earned their views without paid distribution (per TikTok's own `isAd` flag, verified 55/55 against local `post.json`). Engagement counts (plays/likes/comments/shares/saves at 2026-09-12 capture) are stated as supporting context only.
- **PROMOTED (24 TikToks with `isAd=true`)** — paid-format patterns only. Several have huge view counts because of paid distribution (e.g. `tiktok-joinladder-7673987790429768974`, 9.8M plays; three sibling Ladder posts at 1.8M–7.4M). Those counts say nothing about creative quality. What transfers is the *format*: what a brand chose to pay to put in front of people.
- **LONGEVITY/REUSE (540 Meta rows)** — longevity/reuse signals only. Each creative's associated ad ran ≥30 full days (median 79d, mean 127d, max 649d). A long run means an advertiser kept spending on or reusing the creative — it does **not** prove performance, ROAS, or conversion. Never read "ran 500+ days" as "worked." The value here is volume and repetition: what structures advertisers return to again and again.

Two further honesty notes that apply throughout:

- **No comment text exists in this corpus.** TikTok hides comment text behind login; the captain confirmed "ok its fine no commets needed." Collection (PKG-B) verified logged-out sessions return counts only: 47/55 rows are `unavailable` with live UI counts, and the 8 `collected` rows all read **0 comments** at collection time (six girlwalk.app posts, two sweatapp posts — likes but no comment threads to capture). There are therefore **zero audience quotations** in this report. Live engagement counts and clearly labeled video-design inferences appear as supporting context. Nothing is presented as comment evidence.
- **46 Meta rows rest on thinner independent support.** They lack pre-existing local frame/transcript corroboration (validator §7/§12); their content is Gemini-direct evidence — accurate per spot-checks, but cross-checked against file existence/duration/pack data rather than transcripts. They are weighted normally for structure counts but are not cited as sole support for any claim below. The 39 stratum spot-checked rows (every advertiser/category + both TikTok classes) carry the most weight; 6 opening frames were read directly as images and matched exactly.

Timestamp normalization: raw records mix `MM:SS`, `M:SS`, and range formats (`00:00-00:03`). This report normalizes to `MM:SS` in prose without editing the records.

---

## 1. Methods (what was actually done)

1. Read the complete validated corpus: `data/gemini-video-batch/records.validated.jsonl` — 595/595 lines, 595 unique stable IDs, 0 schema errors, 0 `pending` validators.
2. Read the validation log (`validation.md`, PKG-C, 2026-09-15): schema checks, ffprobe audio audit (2 silent WalkingPad files corrected), TikTok `isAd`↔evidence-class agreement 55/55, duration agreement, cross-platform exact-duplicate check (md5 of 55 TikTok clips vs 2,330 Meta md5s → **0 overlaps**; near-duplicate templates kept as separate records), transcript spot-checks with word-overlap scores, and the multilingual wins (Spanish/Arabic rows where Gemini beat whisper tiny.en).
3. Read `comments.jsonl` (55/55 valid; 47 `unavailable`, 8 `collected`-but-empty) and `usage.json` (spent USD 6.100442 / cap 10.00; model `models/gemini-3.8-flash`; all 595 standard-run complete).
4. Ran local-only aggregation over the validated file (hook-category normalization, duration/shot/CTA/voice/pacing distributions, verbatim/OST repetition counts, run-day distributions) and deep-read ~30 representative records end to end across every advertiser cluster and both TikTok evidence classes.
5. Synthesized with Muse Spark reasoning into this single report. No footage, scripts, likenesses, or music were copied; all applications are structural principles and transpositions.

## 2. Corpus accounting

| Stratum | N | Source of count |
|---|---|---|
| Meta paid, ad ran ≥30 full days | 540 | Verified manifest (brief-implied 477 was not reproducible from source records; discrepancy documented in `failures.jsonl`, manifest carries verified 540) |
| TikTok unpromoted, >10k views (organic signal) | 31 | senada.greca 16, whitneyysimmons 6, weward 5, naughtygirl.fitness 3, gymnadz 1 |
| TikTok promoted `isAd=true`, >10k views (paid-format patterns) | 24 | girlwalk.app 10, strava 5, joinladder 4, sweatapp 2, whitneyysimmons 1 (brand partnership), liftoff_app 1, abszones 1 |
| **Total** | **595** | 595/595 validated, zero defects outstanding |

Advertiser weight (Meta): Fitbod 182, MyFitCoach 68, Gymverse 40, LazyFit 39, WeRise 30, Conqueror 27, Fabulous 21, Liftoff 21, DAWG 14, Sweat 13, VYBS 13, Pilates Class 11, WalkingPad+ 10, AbMaxx 7, BodyApp 7, Workout Locker 7, Simple 6, Unrot 6, Setgraph 5, WalkUp 5, Muscle Monster 5, Naughty Girl 1, Gymdesk 1, Rate My Physique 1, Winwalk 1. Fitbod alone is 31% of the corpus — its patterns dominate Meta counts and are flagged as such below rather than treated as cross-market truth.

Durations: overall median 28s, mean 34s (Meta median 28.6s; organic TikTok median 31s; promoted TikTok median 12.5s — paid TikTok skews short). Range 5s–590s. Shot counts: median 8, mean 9.2, max 42. Zero slideshows (`slide_count` null everywhere — every record is real video).

Meta run days: median 79d, mean 127d; 211 rows in 30–59d, 72 in 60–89d, 68 in 90–119d, and a long tail past a year (longest: `meta-setgraph-u04` 649d, `meta-fitbod-u35/u40` 569d). Again: reuse signal, not performance proof.

---

## 3. ORGANIC findings — 31 unpromoted TikToks (the genuine signal)

Ranked internally by plays at capture (2026-09-12). Counts are context, not verdicts.

### 3a. The heavyweights: what the most-watched organic posts do

**`tiktok-whitneyysimmons-7675901648090303757` — 4.3M plays / 421.6k likes / 930 comments / 14.2k saves.** The corpus's biggest organic post. What happens: opens on Whitney by a leg press machine answering an on-screen comment sticker ("Where does baby go when you're at the gym?") with a sarcastic one-liner ("the baby has a dad"), then runs a full leg-day tutorial — high-stance leg-press setup with foot-placement coaching, rep counters ticking over working sets with audible strain commentary ("I'm in danger"), then cable step-ups with form cues to cutoff at 60s. Devices: comment-sticker reply as hook (borrowed conflict + permission to be blunt), then genuine expertise delivery; the strain is audible and unpolished. No product, no CTA. Transferable: *reply-to-a-real-question cold open → single-session expert execution with visible effort.* The 14.2k saves (highest save count in the corpus) fit a saveable-workout design inference — labeled inference, not comment evidence.

**`tiktok-whitneyysimmons-7675153986411842829` — 520k plays / 58.7k likes / 428 comments.** GRWM-for-the-gym chit-chat: bathrobe, energy-drink can crack at chest level in frame 0 (audio ASMR hook), then jump-cut makeup routine while monologuing postpartum inconsistency ("four months postpartum… not been able to stay consistent one time") and a psoriasis flare-up shown on camera. 13 shots, fast jump cuts, no music — just can-fizz and voice. Transferable: *sensory micro-action in frame 0 (crack/open/pour) + vulnerable life update + routine the viewer can half-watch.* Note the loop behavior: mid-sentence 60s cutoff, typical multi-part retention design.

**`tiktok-senada.greca-7673974690288897294` — 486.7k plays / 18.4k likes / 145 comments / 7.0k saves.** 18 seconds, no voice, 5 shots: plate swings → lateral lunges → reverse-lunge-to-high-knee → bear-stance reaches → squat jumps, one top-centered exercise label per move, beat-synced cuts over house music. Caption carries the program ("12-16 reps x 3 sets") and the reply prompt ("Drop your questions in the comments"). Transferable and the most repeatable organic structure in the corpus: *5 moves, 1 implement, labels burned in, 3–4s per move, specs in caption, explicit question prompt.* Saves-per-play is the highest ratio among workout posts — consistent with a save-to-try-later design (inference).

**`tiktok-weward-7683637216987434253` — 427.1k plays / 30.9k likes / 181 comments / 2.3k shares.** The best walking-native organic post. A host does a "REALISTIC Walk in Times Square": selfie-handheld alternating with POV walking shots, 27 fast cuts across ~57s, narrating micro-moments (photographer hustle, NYE ball, mascot shakedowns, smells, fake-AirPods seller, TKTS stairs), then overlays the WeWard step count (5,707 steps) and asks "Where should we walk next?" — a destination question that gives viewers a five-word reply action. Transferable: *named-place walk + 5–7 pointed micro-observations + step-count reveal as payoff + next-destination question.* Shares (2.3k) fit send-to-a-friend NYC content (inference).

**`tiktok-senada.greca-7675115917260442894` — 123k plays / 8.3k likes / 82 comments.** "No excuses" travel workout: posing intro in a raw concrete warehouse in Albania, then 6 heavy moves (straddle squats, Zercher lunges, RDLs, hamstring curls, reverse froggers, hip thrusts) with burned-in labels, no voice, Latin-pop track. The setting *is* the message — unfinished room as proof of discipline. Transferable: *ugly/location-truth setting + heavy execution + minimal text.*

### 3b. Organic formats that repeat (with traceability)

- **Comment/critique rebuttal as structure** — `tiktok-senada.greca-7673598666157968653` (24.8k plays): overlay "More of the same! 😂😂😂" while performing the *same* sit-up-to-squat across 10 settings (beach rock, patio turf, paddleboard on ocean, poolside, gym turf, rainy deck, mat…) under a consistency voiceover. Turning a repetitiveness critique into the concept is the device.
- **Gatekeeping-challenge monologue** — `tiktok-weward-7681774599473843469` (76.3k plays, 158 comments, 1.2k shares): rain, umbrella, low selfie angle: "If you're in NYC and a 30-minute walk is too far, you're not ready… 10k steps is not the goal, it's the bare minimum." 12s single idea, no product, no CTA — and the highest comment rate in the walking cluster. The device is mild in-group gatekeeping with a quotable line. Ethical line: pride/challenge transfers; punching down at beginners does not.
- **Series framing** — `tiktok-weward-7679114146603945230` ("Rating Walkers in NYC part 95"): the "part N" device manufactures expected continuation; 95 parts is itself the hook.
- **Dance-fitness instruction** — `tiktok-naughtygirl.fitness-7680273719587097886` (85.2k plays, 2.7k likes, 1.6k saves): "13-MINUTE BANDS WORKOUT" with rhythmic instructor callouts ("three, two, drop, push your knees out"; "drop, get your money, pick it up") over dance instrumentals, ending in celebratory groove. Fun-first cueing with money/phrasing jokes baked into reps.
- **Teaser/lens-cover reveal** — `tiktok-senada.greca-7676202089147682062` (19.3k plays): plate squat → 3-panel split-screen lifting montage → walks to lens, covers it whispering "Time for a new look" → black-card "werise" reveal. Nine seconds. The lens-touch is the attention spike.
- **Kitchen protein content** — senada.greca breakfast jars (`…-7683986955415129357`, `…-7678079928402840845`, `…-7675469642885860621`): sports-bra-to-kitchen whiplash opening (hold jar to camera in frame 0), recipe in caption/comments, 10–16k plays each with healthy save ratios. Food is the rest-day reach vehicle.
- **Arabic-language arm/posture routine** — `tiktok-gymnadz-7678466296706501895` (16.8k plays, 405 shares, 575 saves — the corpus's highest save *ratio*): wrist weights in frame 0, spoken Arabic hook promising 5 simple moves for arms/chest/posture, numbered moves with rep counts burned in Arabic script. Proof that the 5-move labeled structure travels across languages.

### 3c. Organic craft norms (counts, not claims)

- Voice in 20/31 (65%); the 11 no-voice posts are all music-driven workout demos with burned-in labels.
- CTA present in only 14/31 (45%) — and when present it is usually a caption question ("Drop your questions", "Where should we walk next?"), not a download push.
- Pacing: 15 fast / 10 moderate-medium / 6 other; single-take vlogs (Whitney GRWMs, weward walks) run 29–60s; demos run 9–31s.
- Opening images: human mid-action or mid-speech in 29/31 — plate swing, can crack, umbrella in rain, robe + drink, band dance. No logo-first or product-first organic open.

---

## 4. PROMOTED findings — 24 TikToks with `isAd=true` (paid formats, not performance)

### 4a. The view counts are distribution, not verdicts

Four JoinLadder/Hilary Duff posts hold 1.8M–9.8M plays with like rates far below organic peers (e.g. 7.4M plays / 5.3k likes). Read them as *celebrity-format case studies*, never as "celebrity creative outperforms."

### 4b. What the promoted formats do

- **Celebrity-curiosity gap (Ladder × Hilary Duff, 4 posts):** `…-7673987790429768974` (9.8M plays): Duff straps on a pink weighted vest in a dressing room under "what's hilary training for? 🤔" → squats in vest → stage footage in a heavy beaded gown → holds the gown up ("Weighted dress > weighted vest"). 11s, no voice, hip-hop bed. The joke resolves the gap. Sibling `…-7673979617341984014` milks the same shoot. Transferable: *backstage access + question banner + punchline payoff*; the weakness to avoid is zero product linkage (no app shown, no CTA in any of the four).
- **Timestamped redemption arc (Strava, 5 posts):** `tiktok-strava-7673919321160142094` (505.6k plays): groggy 3:30 AM bed selfie ("Why are we doing this?") → car park → friend dancing on car hood → trailhead permit → steep hike → alpine-lake plunge → McDonald's with Strava stats card overlaid. On-screen clock stamps (3:30 AM → 10:04 AM) are the structural spine; suffering-early/joy-late is the arc; the product appears once, at 00:21, as a stats card. `…-7674035073485769998` ("MY ZONE 2 RUN" phone-to-forehead jog) and `…-7674037002651651341` (sunlit selfie run) are thinner siblings. Transferable: *clock-stamp spine + delayed product card as receipt, not pitch.*
- **Girlwalk paid wall (10 posts, 10–30k plays, 0–2 comments each):** the account is the corpus's cautionary tale. Openings are strong — mirror-side-eye, treadmill POV ("THE YOU IN 6 MONTHS IS ALREADY THANKING YOU"), sweat close-up ("no excuses. 10k. every day."), "my 2 obsessions lately: walk 10K steps / beating my last walk" (`…-7675742150465785101`, validated against the actual frame). But every post ends on invitation without a reply action ("let's hit that 10k!", "keep pushing"), and collection found **zero comments on all six girlwalk posts checked**. Likes without replies (up to 440) = approval without a conversation on-ramp. Transferable lesson, stated as design inference: *every list/invitation post needs one fill-in-the-blank reply action (number, place, time) or approval never converts to conversation.*
- **Abszones anatomy-templating:** `tiktok-abszones-7680163481974263062` (11k plays, 101 likes, 3 comments): white 3D male ab model on dark background with "Your abs aren't growing"-style script — byte-distinct from but structurally identical to AbMaxx Meta creatives (§5e). Evidence that a template (3D-anatomy hook → UGC interruption → scan demo → score) runs unchanged across TikTok-paid and Meta-paid.
- **Novelty-pattern break (Liftoff):** `tiktok-liftoff_app-7681371226593398032` (16.6k plays): hydraulic press descending on a decorated watermelon ("Fooled ya 😆"). Pure scroll-stop spectacle with near-zero product linkage — the extreme case of hook/product decoupling.
- **Sweat promoted pair:** clone-comparison ("Glutes vs Quads", `…-7675247743572430100`) and treadmill affirmation (`…-7675248158854614292`); both earned likes, zero comments. Clone/split-screen comparison is the reusable device; affirmation-without-question is the failure mode (design inference).

Promoted craft norms: no-voice in 15/24 (62% — music/text-led), CTA present in only 10/24, median duration 12.5s (shortest stratum). The promoted set is where the hook/product decoupling problem is worst: spectacle opens with no bridge to any action.

---

## 5. LONGEVITY findings — 540 Meta creatives (reuse signals, not performance)

Grouped by advertiser cluster. Run-day figures are reuse facts, not efficacy claims.

### 5a. Fitbod (182 rows; the corpus's gravitational center)

Fitbod's sheer volume means its devices dominate aggregate counts — reported here as house style, not universal law. Longest runs in the corpus: `meta-fitbod-u35` (569d: concert-dancing → falling-off-mat gag → nightclub resolve → heavy bench "With Fitbod"), `meta-fitbod-u40` (569d: phone demo held in front of dumbbell rack), `meta-fitbod-u78` (549d: 48s gym-bro skit — annotated red arrows on a struggling lifter, "let's go help this guy out," trainer-invoice pain ($400/week bills), UI demo, "315K 5-star reviews"), `meta-fitbod-u02` (517d: "If a man used AI to work out for five months straight…" month-by-month transformation), `meta-fitbod-u01` (457d: the female mirror, "If a woman used Fitbod for 5 weeks straight…" week-by-week with Pinterest-workout callout). The **"If [avatar] used [method] for [X weeks], here's what happens" episodic timeline** is the single most-reused long-run structure in the corpus — week/month markers as chapter titles, pain → soreness → confidence → validation → mastery, social proof + trial CTA to close. Also reused: man-on-the-street rating (`meta-fitbod-u12`, 500d: trainers 2/10 vs Fitbod 10/10), Google-search screen-record hook (`meta-fitbod-u61`, 495d), quote-reframe ("You're so lucky you have that body" → "The luck: firing my $400/week trainer", `meta-fitbod-u116`, 248d), party-lifestyle contrast (`meta-fitbod-u105`, 496d). Verbatim repetition shows the machine: "Bro, download Fitbod" ×6, "If you feel lost at the gym, seriously, get Fitbod" ×4, "FITBOD BUILT FOR BETTER." ×37 OST.

### 5b. MyFitCoach (68 rows; multilingual callout machine)

House formula, run in Spanish/Polish/Portuguese: conditional audience callout over a live set ("Si entrenas en el gimnasio, deberías descargar MyFitCoach", `meta-myfitcoach-u01`, 235d, single continuous leg-press shot with PIP app overlay at 00:03) → feature callouts (personalized plan, optimal exercises, real-time weight recommendations) → "Descarga la app ahora." Variants: regret hook ("2 años en el gimnasio… ¿sin saber que ESTO existe?!"), physique-point ("¿Quieres ganar músculo? ¡Entonces haz esto!"), #1-app UI showcase. The device is *callout + matching-exercise PIP + one feature per rep.* Note the policy edge: "Najlepsza aplikacja treningowa" (best training app) superlatives without substantiation recur.

### 5c. Gymverse (40 rows; reframe + adaptability)

`meta-gymverse-u01` (39d, representative of the cluster): kinetic word-by-word captions ("It's only August, and I've already started over three times") → reframe ("I was never the problem. My plan just wasn't built around my life" — repeated verbatim ×7 corpus-wide) → adaptive-plan demo (skip days without losing momentum) → "Stop starting over. Download Gymverse now." The objection it answers (restart shame) and the reframe (blame the plan, not the person) are the transferable assets; the exact lines stay behind.

### 5d. LazyFit (39 rows; printable + 7-minute + timeline)

`meta-lazyfit-u02` (107d): parchment "PRINTABLE BED PILATES — How to lose 30 lbs in 28 days" 9-pose sheet → demographic slice ("for women over 50 who haven't exercised in years") → calendar page-peels (Day 1/2/3/4 with muscle callouts) → weekly promise ladder ("After 1 week you'll feel the difference / 2 weeks you'll see the change / 3 weeks everyone else will notice" — ×8–11 repetitions corpus-wide) → app challenge-lock UI demo → "Download this app!" ("The secret? Download this app!" ×21 — the corpus's most-repeated line). **Flag:** extreme speed/weight claims; several rows carry AI-actor disclaimers that invite FTC/Meta scrutiny. Transferable minus the claims: *cheat-sheet visual + day-peel progression + tiny-commitment framing (7 min) + lock-UI demo.*

### 5e. AbMaxx/BodyApp/RateMyPhysique/MuscleMonster/Setgraph (scan-and-score cluster)

Shared template: 3D-anatomy or photo-scan hook → abrupt UGC interruption ("This is just ridiculous") → app photo-scan demo → gamified score breakdown (89 vs 59) → before/after stats → comment-score CTA ("Let me know what you guys get", `meta-abmaxx-u04`, 54d). BodyApp rows (`meta-bodyapp-u01` et al., 40–79d) demo waist/reshape/height sliders live on photos — the product demo *is* the entertainment. **Flags:** body-warping-as-enhancement, "genetic ceiling"/body-fat-precision claims, body-image policy risk. The score-and-compare mechanic transfers; the warping and precision claims do not.

### 5f. WeRise/Senada (30 Meta + 16 organic TikToks; founder-led universe)

Long-form credibility: `meta-werise-u01` (30d, 106s): podcast clip ("I started dealing with depression and anxiety…") → host endorsement → marathon-to-strength B-roll → short-workout mental-health pitch → app/nutrition/onboarding demo → "Take the free assessment." Short-form: myth-busts, mistake callouts, founder intros, "we rise — Lift weights. Lift your mood." The organic TikToks (§3) are the top of this funnel. Transferable: *vulnerability-first founder story banked in long form, cut down into single-idea shorts.*

### 5g. Conqueror (27 rows; tangible-reward hook)

Most consistent product-hook fit in Meta: hands + collectible medal in frame 0 (Van Gogh `meta-conqueror-u01` 84d; Harry Potter, LOTR, Star Wars/Grogu, Frida Kahlo, Great Barrier Reef variants, 36–105d) → simple rules (walk N miles, solo or with friend, at your pace) → feature close-ups (folding panels, paint tubes) → "Sign up for the [X] Virtual Challenge." Variants: split-screen treadmill-over-fantasy-map, gift-angle ("3 reasons why every…"), comment-reply unboxing. The device — *physical milestone object as proof of intangible effort* — is directly relevant to ExcerLock's lock-in mechanic (see §8). One caution in records: vendors/sellers called "scams" on camera in adjacent walking content — avoid.

### 5h. WalkingPad/Winwalk/WalkUp/VYBS (walking + rewards cluster)

- **WalkingPad (10):** setup-demo arc — unfold in a real room (`meta-walkingpad-u13`: mom, playroom, toddler, "I stopped waiting until nap time…") → lock rail → walk/jog + desk-work multi-scenario → display close-up (steps/time/speed) → fold away. The *foldaway* is the payoff shot. (Two rows, `meta-walkingpad-u18/u19`, are silent video-only files — records corrected.)
- **Winwalk (1, but 263d):** `meta-winwalk-u01` — comment-reply sticker ("Earning rewards while tracking steps? Whaaat?") → grocery-bag walk selfie → coin-tap screen record → gift-card store (Nike/Adidas/Amazon) → cartoon outro. The comment-sticker + reward-store proof is the reusable skeleton.
- **WalkUp (5):** problem-led walking (cellulite-pinch lymphatic hook `meta-walkup-u26` — flagged: lymphatic-drainage/menopause claims), dance-walking social proof, Tai-Chi-walking splits.
- **VYBS (13):** earn-rewards skepticism-reversal ("OK, WAIT!"), Cash-App-balance proof shots, haul reveals, one shock-pattern interrupt. Proof-shot grammar (balance screen, gift cards) repeats across the rewards niche.

### 5i. DAWG/Fabulous/Simple/Unrot/Liftoff/Sweat/Pilates/NaughtyGirl/Gymdesk (remaining clusters)

- **DAWG (14):** anime-montage discipline codes (Tanjiro/Aki/Mob with "No alcohol / No processed food / Movement everyday", `meta-dawg-u09` 147d) → RPG stat dashboard + rank-up (Gold IV → Diamond I) → "The Path" walk challenge. **Flag:** unlicensed anime footage + voice lines = copyright risk. Gamified rank mechanics transfer; the footage does not.
- **Fabulous (21):** single-take scenic selfie + rut callout ("If you're in a procrastination-depression hole…", `meta-fabulous-u06` 91d) + authority mechanism (Duke neuroscientists — flagged, unsubstantiated medical/neuroscience claim) + "game changer" verdict. The *If-you're-in-[rut] try [mechanism]* sentence transfers with a substantiated mechanism.
- **Simple (6):** longest narrative in corpus (`meta-simple-u07`, 88s, Spanish, AI-disclosed actors): construction-worker opener → sauna struggler/master dialogue → objection handling (joints, beer belly, over-50) → weekly timeline → 7-min habit stack → CTA. AI-disclaimer present; 4-week halving claims flagged.
- **Unrot (6):** clone A/B day-in-life (`meta-unrot-u01`, 102d: 38m vs 8h41m screen time, failed Apple Screen-Time bypass → app-enforced blocking → brain-credits). The clone-comparison grammar also appears in Sweat-promoted TikTok — a cross-corpus device.
- **Liftoff/Gymdesk/Setgraph:** testimonial + data-proof (Liftoff), action-metaphor gag ("gym software choking you" choke-hold visual, `meta-gymdesk-u01` 55d) → triple "No more…" cuts → desk demo, notebook-shame hook ("Still counting reps in your notebook?", `meta-setgraph-u04` 649d — the longest run in the corpus at 11 seconds: hook → 3 machine cuts → POV tap-log → walk-with-phone → split-screen pose).
- **NaughtyGirl (`meta-naughty-girl-u04`, 53d):** founder direct-challenge ("You are now b!%#$") → UGC video wall → vulnerability → UI + trial → price reframe ($15/mo < 3 Starbucks). The *daily-cost reframe* is the portable device.

---

## 6. Cross-corpus synthesis — what repeats, and where it holds

### 6a. Hooks (first 3 seconds)

Normalized hook leaderboard (595): problem_solution 33, visual_demonstration 15, audience_callout 15, visual_spectacle 14, problem 14, transformation 11, problem_agitation/demographic_callout 9 each, product_demo/comment_reply/relatable_problem/physique_showcase 8 each, then a long tail of 100+ raw labels (curiosity_gap, challenge, quote, POV, myth-bust, gatekeep, teaser…). Organic TikTok skews visual_demonstration/spectacle/story-lead; promoted TikTok skews curiosity/celebrity/lifestyle-obsession; Meta skews problem/callout/transformation. Three hook grammars cover ~70% of the corpus:

1. **Name the pain + promise the mechanism** ("Your abs aren't growing. Build a deeper core…"; "Still counting reps in your notebook?"; "Feeling swollen, sluggish…?"). Dominant in Meta; rare in organic.
2. **Do the thing on screen before explaining** (plate swing under "Plate Swings"; medal in hands; waist slider moving; hydraulic press). Dominant in organic; present in Meta product demos.
3. **Call out the viewer conditionally** ("If a woman used Fitbod for 5 weeks…"; "Si entrenas en el gimnasio…"; "If you're in NYC and a 30-min walk is too far…"). Cross-corpus; strongest per-effort ratio in the data.

Burned-in text in frame 0–1 appears in the large majority of Meta rows and most TikToks; organic exceptions (Whitney GRWMs) substitute a sensory action (can crack) or a face-to-camera confession.

### 6b. Opening images

The corpus opens on: (a) human mid-exertion (hip thrust, leg press, plate swing, cable row from behind — the single most common Meta open, and the 649-day `meta-setgraph-u04` open); (b) object-as-promise (medal, printable sheet, phone UI, waist slider, Google search); (c) face + confession (robe GRWM, rainy umbrella selfie, Santorini rut-callout); (d) spectacle interrupt (anime boulder, hydraulic press, concert fall). Logo-first opens are near-absent outside 5s end cards. People-first or object-first; never brand-first.

### 6c. Avatars and characters

Meta is male-heavy overall (male/men mentions ~2× female/woman — driven by Fitbod/DAWG/Setgraph gym-bro creative), but the female-led rows concentrate in the ExcerLock-relevant niches (Sweat, Pilates Class, WeRise/Senada, WalkingPad moms, WalkUp, girlwalk, Whitney, NaughtyGirl). Recurring cast: the expert trainer (Senada, Whitney, Sweat instructors), the relatable struggler (postpartum mom, restart-every-August lifter, nap-time mom), the founder-confessor (NaughtyGirl Janelle, WeRise Senada), the animated/AI demonstrator (LazyFit pink-set figure, 3D anatomy torsos, Simple AI actors — "AI" appears 187× in avatar text), the hands-only presenter (Conqueror medals — no face needed), the clone pair (Unrot, Sweat, Fitbod triptych), the celebrity guest (Duff), the man-on-the-street interviewer. Settings: gym floor 394 mentions (dominant), home/bedroom/kitchen ~170 combined, outdoor/street/park/beach ~150, studio ~74, car/office/bathroom scattered. Props that recur: phone with app UI, weight plate/dumbbell (single-implement demos), resistance bands, medals/boxes, printed sheets/calendars, energy-drink cans, mirrors, umbrellas (weward rain-walk identity).

### 6d. Story structures (arcs)

Five arcs cover nearly everything, with representative walkthroughs in §7:

1. **Episodic timeline** (Fitbod 5-week/5-month; LazyFit 28-day; Simple sauna weeks) — chapter markers, escalating payoff.
2. **Problem → reframe → mechanism → proof → CTA** (Gymverse restart-shame; MyFitCoach callout+PIP; Fabulous rut-callout).
3. **Demo chain** (Senada 5-move; Gymnadz 5-move; WalkingPad setup→use→fold; BodyApp slider tour) — N labeled steps, no argument needed.
4. **Skits and comparisons** (gym-bro rescue; Google search; clone A/B; man-on-street ratings; comment-reply rebuttals).
5. **Vlog/credibility pieces** (GRWM chit-chat; realistic walk; podcast founder story; backstage celebrity).

Product-reveal timing is early: ≤3s in 228 rows, 4–10s in 176, 11–20s in 101, 21s+ in only 56. The corpus shows the product (or its promise-object) fast, then spends the middle on mechanism/proof.

### 6e. Shot/slide patterns and pacing

Median 8 shots; demos 5–6 brisk cuts (one per move, 3–4s each); vlogs 13–27 jump/POV cuts; narratives up to 42. No slideshows anywhere. Pacing: fast ~55% (276 Meta + 15 organic + 15 promoted), moderate/medium ~30%, slow ~7% (Spanish AI narratives, GRWM chatter, single-take UGC). Cuts land on beat drops, rep changes, page peels, and clock stamps — transitions are *motivated* (exercise change, day change, location change), not decorative.

### 6f. Caption systems

Three systems: (1) **burned-in hook + chapter cards** — big center/top sans-serif, 1–5 words per card, changing per beat (Fitbod kinetic words, Gymverse AUGUST/ALREADY/OVER/TIMES, Conqueror rule cards); (2) **exercise-label overlays** — top-centered move names + rep schemes (Senada, Gymnadz, NaughtyGirl); (3) **auto-caption transcription** — bottom-center per-phrase subs on talking-head/UGC rows (Whitney, Gymdesk, MyFitCoach). Density rule of thumb: ≤7 words on screen at once; cadence 2–4s per card in demos, per-phrase in dialogue.

### 6g. Voice and audio

Voice in ~65% of Meta and organic, only ~38% of promoted (music/text-led). Speaker counts: 1 speaker 309, 2 speakers 50, 3+ speakers 20, none 215. Delivery: AI/female-commercial narration (LazyFit, MyFitCoach dubs, Winwalk), UGC conversational (Whitney, Gymdesk presenter, Duff backstage), coach callouts (NaughtyGirl), whisper-tease (Senada lens-cover), sung/rap beds counted as no-voice with vocals disclosed in `music_sfx` (convention, kept). Music: upbeat electronic/pop/house beds dominate (~70% of music tags); lo-fi under vlogs; ambient-only (rain, gym noise, breeze) on the most "real" posts; paper-flip/coin-tap/can-crack SFX as punctuation. Silence as design appears only in the 2 corrected silent WalkingPad files — genuine silence is otherwise absent; quiet *relative* passages (whisper, rain) do the same job intentionally.

### 6h. CTAs

Present in 87% of Meta (trial/download badges, "Download this app!", week-5 end cards, comment-score prompts) but only 45% organic / 42% promoted — and organic CTAs are overwhelmingly *reply prompts* ("Drop your questions", "Where should we walk next?"), not install pushes. Loop behavior: hard-cut end cards dominate Meta; organic favors natural loops (workout circuit back to move one; walk ending on a next-destination question). The girlwalk-zero-comments pattern (§4b) is the CTA caution: invitations without a reply action earn approval, not conversation.

### 6i. Objections answered (explicitly, in-copy)

Most-handled: no time (7-min framing ×14+ OST, nap-time mom, desk-walking), gym intimidation/confusion (Pinterest-workout wandering, notebook shame, "lost at the gym"), restart shame (Gymverse), cost (trainer-bill invoices, $15<3-coffees, free-trial ladders), inconsistency/boredom (party contrast, anime discipline codes), age/joints (over-50 bed pilates, Tai-Chi knees, 75-year-old testimonial ×6), postpartum reality (Whitney ×2 posts), weather (treadmill "without relying on the weather"), distrust ("You're so lucky" envy-reframe, skepticism-reversal VYBS, "doctors hate me" — flagged). Un handled white space for ExcerLock: phone-distraction-in-gym is named as pain but never solved by a lock/focus mechanic — no competitor occupies it (§8).

### 6j. Emotional triggers and payoffs

Recurring pairs: intimidation → belonging (week-1 confusion to week-5 mastery); shame → absolution (restart reframe); envy → method ("lucky body" → fired trainer); overwhelm → tiny commitment (7 min, 1 implement, 10-min walk); boredom → game (ranks, medals, streaks); invisibility → recognition ("in 3 weeks everyone will notice"); guilt → permission (nap-time mom, postpartum honesty); cynicism → delight (realistic-walk micro-moments, weighted-dress punchline). Payoffs are near always *social or visible* (compliments, scores, medals, step counts) rather than private health metrics.

### 6k. Attention devices (why each may work — labeled inferences)

Devices are recorded per-row in the validated records (`attention_analysis`, 1,674 device notes); the cross-corpus winners: kinetic chapter text (resets attention per beat), single-implement constraint (comprehension in one glance), PIP proof (claim + evidence same frame), comment-sticker conflict (borrowed drama), clock stamps (curiosity about the endpoint), lens touch/cover (pattern break), audible strain/effort (authenticity cue), can-crack/food-present sensory opens, split-screen before/after or A/B, rank/score overlays (game loop), foldaway/unboxing payoff (completion satisfaction). Each is structural and reproducible without copying any specific execution.

---

## 7. Representative walkthroughs (what happens throughout, beat by beat)

Timestamps normalized to MM:SS. Stable IDs trace every claim to the validated records.

**R1. `meta-fitbod-u01` (paid, 457d, 52s, 17 shots).** 00:00 hook triple-channel (seen: barbell hip thrust; heard + read: "If a woman used Fitbod for 5 weeks straight, here's what would happen"). 00:03 Week 1: packing bag, wandering between machines ("Pinterest workouts"), phone reveals Fitbod plan at 00:09. 00:13 Week 2: lat pulldown, soreness, app auto-adjusts at home. 00:22 Week 3: leg extension + deadlifts, confidence visibly up. 00:31 Week 4: app review, barbell squat, external validation. 00:38 Week 5: cable work, mastery, recovery UI. 00:45 rapid UI demos (curls, flys, step-ups). 00:47 "Try it free for 7 days" + logo card. Arc: episodic timeline; product at 00:09; proof stacked at the end.

**R2. `meta-lazyfit-u02` (paid, 107d, 38s, 8 shots).** 00:00 parchment cheat-sheet ("PRINTABLE BED PILATES / How to lose 30 lbs in 28 days", 9 poses). 00:03 demographic slice (women over 50). 00:07–00:17 calendar page-peels Day 2/3/4 with muscle callouts + promise ladder (feel/see/noticed). 00:20 app icon + "Download this app!". 00:22 challenge-lock UI, tapping days opens demonstrator clips. 00:34 end card + store badges. Arc: object-hook → slice → timeline → lock-UI demo. (Claims flagged; structure transfers.)

**R3. `meta-conqueror-u01` (paid, 84d, 11s, 5 shots).** 00:00 hands unfold Van Gogh medal over wood table ("Earn this Vincent van Gogh medal. Walk 56 miles solo or with a friend…"); 00:03 macro detail + sliding panels; 00:07 full medal + presentation box + "Sign up for the Vincent van Gogh Virtual Challenge." Arc: tangible reward → rules → craft proof → register. The densest 11 seconds in the corpus.

**R4. `meta-setgraph-u04` (paid, 649d, 11s).** 00:00 lifter on cable row from behind, "Still counting reps and sets in your notebook?" over hip-hop drums, no voice. 00:02 loading T-bar row. 00:04 lat pulldown, text flips to "Log your workouts with Setgraph to speed up your gains." 00:05 POV tap-log in UI. 00:07 walking with phone → shoulder press. 00:08 split-screen back-pose montage. Arc: shame-hook → 3 machine cuts → POV proof → identity payoff. Longest run, shortest lesson: one pain, one thumb-tap, one physique.

**R5. `meta-abmaxx-u04` (paid, 54d, 29s, 5 shots).** 00:00 3D ab anatomy, staccato OST (ABS/BUILD/MORE/CORE/TRAIN), "Your abs aren't growing." 00:07 hard cut to shirtless UGC creator: "This is just ridiculous." 00:10 app photo-scan overlay, "89 Overall Score." 00:18 before/after (59 → 89). 00:21 diet plan + leaderboard. 00:27 "Let me know what you guys get in the comments." Arc: the scan-and-score template in full.

**R6. `meta-walkingpad-u13` (paid, 33d, 18s, 6 shots, no voice).** 00:00 mom unfolds treadmill on playroom rug ("My Biggest Mom Hack Lately: I stopped waiting until nap time…"). 00:04 rail lock. 00:06 walk/jog beside toddler. 00:09 display close-up (steps/time/speed). 00:12 desk pulled over pad, typing while walking. 00:15 fold deck in half. Arc: reframe → setup → multi-scenario → quantified proof → disappear. The foldaway is the period at the end.

**R7. `tiktok-weward-7683637216987434253` (organic, 427k plays, 57s, 27 shots).** 00:00 "Here's a realistic walk through Times Square" + title card. 00:02–00:51 micro-moment chain (photographer, promoter, NYE ball, mascots, smells, AirPods seller, billboards, photoshoot, TKTS stairs) alternating selfie/POV. 00:52 WeWard overlay: 5,707 steps. 00:56 "Where should we go next?" Arc: place promise → pointed observations → counted receipt → reply question.

**R8. `tiktok-senada.greca-7673974690288897294` (organic, 486k plays, 18s, 5 shots, no voice).** 00:00 plate swings/"Plate Swings". 00:02 lateral lunges. 00:06 reverse-lunge-to-high-knee. 00:10 bear reaches. 00:14 squat jumps. Labels top-center, cuts on the beat, specs + question in caption. Arc: pure demo chain — the corpus's most portable 18 seconds.

**R9. `tiktok-whitneyysimmons-7675901648090303757` (organic, 4.3M plays, 60s, 13 shots).** 00:00 comment-sticker reply ("the baby has a dad"). 00:09 leg-press setup tutorial. 00:21 working sets with counters + strain. 00:40 cable step-ups + cues. 00:52 fatigue to cutoff. Arc: conflict-hook → expertise → visible effort. No product, no CTA; saves carry it.

**R10. `tiktok-strava-7673919321160142094` (promoted, 505k plays, 26s).** 00:00 3:30 AM bed groan. 00:04 car park. 00:06 friend on car hood. 00:09 trailhead. 00:10 climb. 00:15 lake plunge. 00:20 McDonald's + Strava card. Arc: timestamped suffering-to-reward with product as receipt at 00:21.

**R11. `meta-gymdesk-u01` (paid, 55d, 22s, 6 shots).** 00:00 choke-hold gag behind presenter: "Do you feel like your gym software is choking you?" 00:05 "ENTER GYMDESK." 00:06–00:13 triple "NO MORE…" (late payments, no-shows, belt promotions). 00:14 desk demo (billing/bookings/check-ins). 00:19 kiosk + "See for yourself." Arc: physical-metaphor gag → triple-pain cuts → demo → CTA. The "No more [X]" triple-cut is directly reusable.

**R12. `meta-naughty-girl-u04` (paid, 53d, 49s).** 00:00 founder dance-challenge ("You are now b!%#$"). 00:04 UGC video wall. 00:10 tearful testimonial. 00:21 founder vulnerability (excluded from fitness). 00:27 UI + 7-day trial. 00:33 price reframe (3 Starbucks). 00:43 encouragement close. Arc: objection-breaker → community proof → founder empathy → trial → cost reframe.

---

## 8. Repeated creative structures (generalized, traceable, copy-principles-only)

T1. **Episodic timeline** — "If [avatar] did [protocol] for [N weeks]…" with chapter cards, escalating payoff, social-proof + trial close. Sources: R1, `meta-fitbod-u02`, `meta-lazyfit-u02`, `meta-simple-u07`.
T2. **Callout + PIP proof** — conditional viewer callout over a live set; app overlay appears doing exactly what the VO claims; one feature per rep; direct download line. Sources: `meta-myfitcoach-u01/u02/u40`, `meta-gymverse-u01`.
T3. **Five-move demo chain** — one implement, burned-in labels, 3–4s cuts on music, specs + question in caption. Sources: R8, `tiktok-gymnadz-7678466296706501895`, `tiktok-senada.greca-7675115917260442894`.
T4. **Tangible-reward hook** — physical object in frame 0 → simple rules → craft/feature close-ups → signup. Sources: R3 + 20 Conqueror siblings, Winwalk gift-card store, VYBS balance shots.
T5. **Setup → multi-scenario → disappear** — unfold/demo in a real room → 2–3 use contexts → quantified close-up → foldaway/storage payoff. Sources: R6, `meta-walkingpad-u20/u12/u90`.
T6. **Comment-sticker drama** — real question/critique on screen → blunt or playful answer → content that proves the answer. Sources: R9, `meta-winwalk-u01`, `tiktok-senada.greca-7673598666157968653`, `meta-conqueror-u04`.
T7. **Reframe triple-cut** — metaphor gag or shame line → three rapid "No more / Turns out…" pain cuts → desk/UI demo → CTA. Sources: R11, `meta-gymverse-u01`, `meta-setgraph-u04`.
T8. **Timestamped redemption** — clock stamps from suffering to reward; product appears once as the receipt. Sources: R10, `tiktok-strava-7674035073485769998`, Simple sauna timeline.
T9. **Cheat-sheet + day-peel progression** — printable/chart hook → demographic slice → day-by-day reveals → lock/challenge UI demo. Sources: R2, LazyFit cluster, DAWG rank-ups.
T10. **Founder vulnerability + community wall** — cheeky objection-breaker → UGC montage → founder empathy → trial + cost reframe. Sources: R12, `meta-werise-u01`, Whitney GRWMs.
T11. **Realistic place-walk** — named location → 5–7 pointed micro-observations → step-count reveal → next-destination question. Sources: R7, weward rain/gatekeep/series rows.
T12. **Sensory GRWM chit-chat** — drink crack/garment/micro-action in frame 0 → jump-cut routine → vulnerable monologue → mid-routine interruption. Sources: `tiktok-whitneyysimmons-7675153986411842829/7683309004952472846`.

All twelve transpose structure, never footage, scripts, likenesses, or music.

---

## 9. Ethical ExcerLock applications by audience

ExcerLock's unoccupied position (white space verified across 595 records): **the phone is named as a gym problem (distraction, doomscrolling, "8h41m screen time") but no competitor sells focus/lock-in as the mechanism.** Every application below routes an existing corpus structure into that gap using ExcerLock's own lock/session/streak mechanics, real users, and substantiated claims only.

### 9a. Gym girls (primary: 385/595 adaptations point here)

- **Episodic lock-in timeline (T1):** "If she locked her phone for every session for 5 weeks…" — Week 1 wandering/Pinterest chaos → Week 5 routine mastery, chapter cards, session-count UI as the chapter receipts. Trace: R1/`meta-fitbod-u02`.
- **Callout + session-PIP (T2):** hip-thrust/squat set with ExcerLock session tracker overlay logging sets/Volume while the creator lifts undistracted; VO: focus-without-phone line in original words. Trace: `meta-myfitcoach-u01`.
- **Five-move one-dumbbell chain (T3):** single-implement routine, labels burned in, "lock in, 5 moves, phone down" framing; specs + save prompt in caption. Trace: R8.
- **Notebook-shame 11s (T7):** "Still tracking lifts in your notes app — on the same phone that keeps pulling you out of your sets?" → POV tap-to-lock → lift → streak screen. Trace: R4.
- **Comment-sticker replies (T6):** answer real follower training questions with locked-session demos; strain audible. Trace: R9.
- **Reframe triple-cut (T7):** "Feel trapped by messy workouts?" under a loaded barbell → three "No more…" cuts (no more mid-set scrolling, lost PRs, skipped accessories) → lock demo → CTA. Trace: R11.

### 9b. Fitness girls (beginner/returner/general: 122/595 point here)

- **Cheat-sheet + challenge-lock (T9):** printable starter calendar (glute-activation or walk-to-run), day-peels, in-app guided clips behind a lock UI, tiny-commitment framing with *honest* timelines (no 30-lbs/28-days language — see §10). Trace: R2.
- **Restart reframe (T7):** "Started over three times this year? …the plan wasn't built around your life" structure with original wording; adaptability = streakpauses/lock scheduling. Trace: `meta-gymverse-u01`.
- **GRWM-to-gym chit-chat (T12):** pre-workout prep + candid consistency talk + lock-tap as the "leaving for the gym" beat. Trace: Whitney GRWMs.
- **Kitchen protein reach (organic food rows):** rest-day recipe content with session-streak overlay as soft branding, no hard pitch. Trace: senada.greca breakfast jars.
- **Founder story bank (T10):** one vulnerability-first story asset, cut into single-idea shorts; trial + honest daily-cost framing. Trace: R12/`meta-werise-u01`.

### 9c. Walking girls (72/595 point here — thinnest stratum, highest whitespace)

- **Realistic place-walk (T11):** "realistic hot-girl walk" through a local park/strip — dogs, eye contact, coffee run — step count + locked-focus session as the receipt, next-route question to drive replies. Trace: R7.
- **Reward-hook open (T4):** streak badge/milestone merch in hands frame 0 ("walk 50k this month with me, solo or with a friend") → rules → progress close-ups → challenge join. Trace: R3.
- **Mom-hack setup arc (T5):** stop-waiting-for-nap-time reframe → setup → toddler/desk multi-scenario → stats close-up → session-complete screen. Trace: R6.
- **Gatekeep-challenge 12s (organic weward):** one quotable walking-standard line + rain/street texture; keep it invitational ("bare minimum" aimed at the self, not at beginners). Trace: `tiktok-weward-7681774599473843469`.
- **Comment-proof skeleton (T6):** reply-sticker ("Earning rewards for steps?") → walk selfie → streak/reward screen record → store/benefit proof → outro. Trace: `meta-winwalk-u01`.
- **Every walking post gets a reply action** (the girlwalk lesson): number/place/time fill-in-the-blank burned into the end card — never a bare invitation. Trace: §4b.

---

## 10. Claim and brand-safety risks (what NOT to carry over)

Frequent in long-run Meta, never to be imitated: extreme speed/weight transformations (LazyFit 30-lbs/28-days; Simple 4-week halving; "melt fat in 9 minutes"; "shed your first 15 pounds"); precision-body claims (AI body-fat/symmetry/genetic-ceiling from one photo); body-warping filters presented as enhancement (BodyApp rows); unsubstantiated authority ("Duke neuroscientists", "doctors hate me", "#1/best app" superlatives ×multiple); medicalized shortcuts (lymphatic-drainage/menopause/cortisol explanations); AI actors + "hypothetical story" disclaimers as claim cover (Simple/LazyFit — invites FTC/Meta scrutiny); unlicensed footage/music (DAWG anime; Solo Leveling row; cover songs); sensitive imagery (hematoma close-up); gatekeeping/elitist tone and vendor-"scam" labels (weward-adjacent). ExcerLock rule: mechanism claims it can prove (sessions locked, streaks kept), timelines it can defend, costs it can itemize, real people, licensed audio.

## 11. Limitations

- Meta longevity ≠ performance; promoted views ≠ quality; organic counts are single-capture snapshots (2026-09-12) that decay with post age.
- Fitbod's 182-row weight skews every aggregate; advertiser-cluster sections (§5) exist to contain that skew.
- 46 Meta rows are Gemini-direct with thinner independent corroboration (§0); 6 frames were image-verified; full-playback verification of 595 videos was out of scope for a no-spend scout.
- Hook categories, timestamp formats, and `flag_unsupported` typing were normalized only at cluster time in this report; records are untouched.
- No comment text, no Meta-library comments (out of scope — not exposed), no YouTube (excluded per brief), no spend/impression data from either ad library.

## 12. Evidence and traceability

- Exhaustive appendix: `records.validated.jsonl` (595 per-video records; stable IDs cited throughout this report) + `comments.jsonl` (55 TikTok comment-evidence rows; 47 unavailable / 8 empty-at-capture) + `validation.md` (PKG-C methods, corrections, spot-check scores) + `failures.jsonl` (count discrepancy, missing-media accounting) + `usage.json` (spend/model accounting).
- No separate playbook, hook worksheet, campaign plan, or strategy deliverable was produced — per the captain's correction, this report is the deliverable; §8–§9 carry the transferable structures inside it.
- Commands run (this task, local-only): `wc -l` counts; python `json` aggregations (hook normalization, duration/shot/CTA/voice/pacing splits, run-day distribution, verbatim/OST repetition, caption/setting/avatar/camera keyword censuses, TikTok engagement table); full reads of ~30 representative validated records; reads of `validation.md`, `comments.jsonl` samples, `usage.json`, `failures.jsonl`.
- Prior deliverable note: the pre-existing `report.md` in this folder (71-line coordinator preflight, $0-spend planning note) is superseded by this synthesis report as the captain-facing final.

## 13. Recommendation

Ship this report as the final word on the 595-video corpus: the twelve structures (§8) with their source IDs are the reusable output; the audience applications (§9) route them into ExcerLock's unoccupied focus/lock-in position; the safety list (§10) bounds them. If follow-up work is commissioned, the highest-value next step is original production (not more analysis): shoot T3 + T11 + T6 first — cheapest to produce, strongest organic traceability, native to all three audiences — with one burned-in reply action per post and substantiated claims only.
