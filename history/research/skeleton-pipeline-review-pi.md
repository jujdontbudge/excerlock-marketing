# Skeleton Pipeline Review: Finalization, Standardization, and Full Automation Design

## Executive Summary

This survey analyzes the complete decision record, code artifacts, and editorial iterations that produced our first fully approved and published TikTok slideshow: the **joke-tip-list-twist** format (Zoey deck 06, recast to Hayden deck 01). 

Using the factual timeline preserved in `log/LOG.md`, `log/events.jsonl`, and related transcripts, this review establishes:
1. Exactly how the `joke-tip-list-twist` skeleton was conceived, rejected, rebuilt, tested, corrected by the captain, and finalized.
2. The generalized checklist of requirements that any slideshow skeleton must satisfy to yield a passing deck.
3. The specific structural, syntactic, and prompt-engineering gaps in the other four existing skeletons (`contrarian-study-explainer`, `do-vs-dont-blunt-coach`, `hook-plus-dense-card`, and `signs-list-diagnostic`).
4. Concrete, slide-by-slide rebuild plans for each of those four skeletons to bring them to the production standard.
5. An end-to-end automation design translating `skeleton + account + topic` into validated prompt JSONs, batch generation, and deterministic text overlay.
6. An iteration and adaptability framework covering write-backs (`make-universal`), intake protocols for new source posts, semantic versioning, decision-log telemetry, and post-publishing performance feedback loops.

---

## 1. How joke-tip-list-twist was finalized

The finalization of `joke-tip-list-twist` was an empirical, feedback-driven process that progressed through five distinct phases: source identification, blueprint drafting, structural expansion, scripting failure and captain correction, and production validation across two accounts.

### Factual Timeline and Decision-Log Citations

#### Phase A: Redefining Skeletons from Real Posts (Sep 24 – Sep 25)
* **E058 (Sep 24 16:17)**: The captain discarded earlier abstract, goal-driven format taxonomies in favor of skeletons extracted directly from proven TikTok slideshows:
  > *"i want to get rid of this goal shit forget amoutn the CTA well jstu intset the CTA so leavea blank for the CTA i want to redo this entire rpocess. forget all the format we have i want a rebuild a bunch of them with a skeleton that i can then craete viration from with our charters."*
* **E064 (Sep 24 17:25)**: The captain defined a skeleton strictly as an adaptable, versatile photo-slideshow format:
  > *"photolo slideshows only. remove everything you think you know about skeletons. simply just a a vid that is repeatable and with variations and somewhat versitile."*
* **E090, E097 (Sep 25 13:55 – 14:29)**: The captain weeded out inflexible candidate posts, ruling that short textless memes or narrow workout listings were not repeatable skeletons:
  > *"i missed those short mems they shoudl not be skeletons"* (E097).
* **E144 (Sep 26 12:48)**: Hermes applied 58 removals from candidate posts, leaving 80 viable skeleton posts across 15 formats.

#### Phase B: Extraction and the First Blueprints (Sep 26 13:29 – 14:26)
* **The Source Post**: Selected as candidate post `@gazellleee/photo/7549800558354271504` (2.6M views, 82.7K saves; recorded as entry #18 in `research/tagged-hooks/hooks.md`). The source featured a 7-slide deadpan sequence: a sincere beginner gym-tips title, two ordinary gym tips, an abrupt heartbreak line as tip 3, followed by three straight tips as if nothing happened.
* **E154 (Sep 26 13:36)**: The captain established the core rule of portability across niches:
  > *"for the slide by slide make it as open as psosible while narrowing down what aspect of it makes it engaging for exmaples the image or how the informaotin is worded. tyr not to narrow down something that is specif to that video like it says \"Move more.\" don tmake it sya this lisde need to be able moving unless that slide is has a specif enaging part that is sepcifly about moving... remmber alot of these video are about food or soemthing that is non targgin our auidence in teh first place so we need to be able to port this to out audience"*
* **E156 (Sep 26 13:39)**: The captain explicitly forbade CTA content in the skeleton blueprints:
  > *"no for skeleton dont wrory about or have anything about CTA at all. for all the skeltons make them off the one vidoe shown in the html rn. all other answers confirm"*
* **E159 (Sep 26 13:42)**: Claude generated the first five skeleton blueprints.
* **E160 (Sep 26 13:49) — Captain Correction (Blueprint too thin)**: The captain rejected the initial blueprints for lacking per-slide operational detail:
  > *"these skeltons are no where near enough each skeleton shoudl have a vertain amount of slides what to put on every slide at for eahc slide the style clone json of the image to then clone that style of image. everyhting else is find jsut a bit more deitra on aobut of slides and wehre informaotin is places and the images"*
* **E165 (Sep 26 14:22)**: Claude expanded all five skeletons to fixed slide-by-slide plans and created style-clone JSON digests in `library/styles/` for all 33 source slides (reusing 1, creating 32 new).
* **E166 (Sep 26 14:26)**: The captain required visual verification:
  > *"please put the final slideshow at hte bottom of each md"*
  Hermes embedded the source link and ordered slide photos in all skeleton files (E167).

#### Phase C: Refining Over-Specification and Twist Placement (Sep 26 14:31)
* **E168 (Sep 26 14:31) — Captain Correction (Twist definition & position)**:
  > *"for a the joke one make the heart break tweit s bit more speciff say it need ot be about a heart break worded in the wya of the orgnial video. then move it to the 4th slide."*
* **E169 (Sep 26 14:31) — Captain Correction (Over-prescriptive wording)**: The captain heavily penalized the agent for specifying syntactic formulas and connecting words for ordinary slides:
  > *"also the text and rol for eveyr slide is way to specifc. i told you not to do this you put \" Role and why it's engaging: ends on the scariest, most visible sign, the one that makes people comment asking for the fix. No fix follows. Text: \"7.\" then a noun phrase joining two related worries with \"and\". 5-6 words, 2 lines.\" this is wayy too specif please undesrtand why are you littlery writing down the word and and deisbing the setcne formaotin. this is way too much. only detail the text on sldie if geneiuly somehting out of hte ogdinayr rathe rhtna 5-7 word tip."*
* **E170, E171 (Sep 26 14:33)**: Hermes revised the skeleton descriptions to short, portable tip descriptions, while moving the heartbreak twist to slide 4.

#### Phase D: The Scripting Test and the Three Fundamental Rules (Sep 26 15:34 – 16:50)
* **E189 (Sep 26 15:34)**: The captain initiated the first live test run:
  > *"ok now i want to make our first slideshow it will be joke tip list skeleton and be scripted by geminie pelas make the script \n\n gtarging gym girls fitness girl gilr who want to lock in or insuce about their bodies"*
* **E191 (Sep 26 15:40)**: The captain assigned Zoey, ordered no CTA for this initial test, and instructed the hook to draw inspiration from the hook database.
* **E192 (Sep 26 15:40)**: The captain paused scripting to mandate the creation of a dedicated hook bank:
  > *"infact right now befor enaythign build a hook md with the hooks of all the posts i tagged iwth hook simply jsut contina lal the next on teh first slide"*
  Claude and Hermes generated `research/tagged-hooks/hooks.md` with 207 tagged hooks (E193, E194).
* **E196, E197 (Sep 26 15:46 – 15:47)**: Gemini generated the first script (`sections/slideshows/accounts/zoey/decks/06-joke-tip-list/script.md`). It immediately exposed fatal weaknesses in the skeleton: the title was generic, and the AI hallucinated a diluted, cheesy heartbreak line.
* **E201 (Sep 26 16:04) — Captain Correction (Rigid Hook Template)**:
  > *"for the hook slide and slide one the sketon ned to be a bit more ridgit forample the orginal vide hook was 6 gyms itps for begging the eksleotn shoudl spefic the hook need to be something like # tips for blank"*
* **E202 (Sep 26 16:04) — Captain Correction (Verbatim Emotional Copy)**:
  > *"also for the heatr break with twist you ai model suck at this so legit jsut copy word for word what she said."*
* **E203 (Sep 26 16:04) — Captain Correction (Vetted Demographic Subgroups)**:
  > *"also the hook when copying a hook of tyring to narrow down the hook make sure it nail down that it tagring a speci demo graphic for this it says begging so fo rhte skeotn it shoud say tips for or adive for tehen demo graphic like broke gym girls or beggingers or gym girilies. not jsut gym girls it can look tohught he tnire hook bank to find what other dmeogrphics are out there by looking at what other hooks are targing."*
* **E207, E208, E209 (Sep 26 16:04 – 16:14)**: The captain ordered Gemini to rebuild the skeleton blind of the conversational critique, following Hermes's structural brief. Gemini encoded these corrections into `sections/slideshows/skeletons/README.md` (rules E204, E205, E206) and `joke-tip-list-twist.md`.
* **E217 (Sep 26 16:35) — Captain Correction (No "Anxious" Labels)**: Gemini generated a script addressing "anxious gym beginners." The captain rejected the term:
  > *"soryr edit skelton to now allow anxious i dont like that"*
  The skeleton was updated to rule out emotional labels for the viewer, requiring recognizable gym identities or experience stages instead (E219).
* **E221, E223, E224 (Sep 26 16:39 – 16:45)**: The script was regenerated with Gemini 3.8 Flash, yielding an approved script.
* **E225 (Sep 26 16:48) — Captain Correction (Injecting the CTA)**:
  > *"this is hoesnlty pretty good. i want ot hcange slide 5 to be double your step count by using excerlock to block ur apps unless your moving"*
* **E226 (Sep 26 16:48) — Captain Correction (Rhythm Calibration)**: The captain recognized that injecting a 14-word product tip into a list of 5-word tips made the CTA obvious:
  > *"also edit teh skelton so a few of the slide have tips upt o 10-12 words to that this CTA lside doesnt look off"*
  Hermes updated the tip-length ranges in `joke-tip-list-twist.md` (E227, E228) so the surrounding tips naturally matched the CTA's cadence.

#### Phase E: Image Production, Account Recasting, and Approval (Sep 26 16:58 – 21:52)
* **E235 (Sep 26 18:03)**: The captain approved the model architecture: Nano Banana 2 (`gemini-3.1-flash-image`) for character-visible slides; GPT Image 2 (`gpt-image-2`) for non-person/object slides.
* **E238, E239 (Sep 26 18:17 – 18:18)**: Prompts were built via `raw/zoey-06/prepare-prompts.py` and executed via `raw/zoey-06/run-nano-group.py`.
* **E240, E242, E243 (Sep 26 18:24 – 18:41)**: Review flagged likeness and hand drift on slides 4, 5, and 7; corrective edit passes were run.
* **E252 (Sep 26 20:09) — Captain Direction (Account Switch)**: Upon reviewing the full contact sheet, the captain switched accounts:
  > *"oh osryr. i jsut realized i want to make this with haydeen not zoey"*
* **E253, E256, E257, E260, E264 (Sep 26 20:09 – 21:20)**: Hermes located the approved dark-haired Hayden character reference and 8 scene benchmarks in the archive, populated `accounts/hayden/account.md`, and prepared `raw/hayden-06/prepare-prompts.py`.
* **E265 (Sep 26 21:21)**: All seven Hayden slides were generated in a single Nano Banana 2 batch.
* **E267, E268 (Sep 26 21:32 – 21:33)**: Hermes assembled a side-by-side comparison between the source `@gazellleee` slides and Hayden's slides in Orca.
* **E269, E270 (Sep 26 21:35)**: The captain approved the images:
  > *"looks good want to post"* -> *"get ready to post"*
* **E271, E272 (Sep 26 21:37)**: The Zoey script was mapped 1:1 to Hayden (`sections/slideshows/accounts/hayden/decks/01-joke-tip-list/script.md`); `raw/hayden-06/overlay.py` rendered 1080x1920 PNGs into `raw/hayden-06/final/`.
* **E273 (Sep 26 21:52)**: The captain inspected the final captioned slides and signed off:
  > *"ok looks good"*

---

## 2. What is required to finalize ANY skeleton

Based on the empirical breakdown of `joke-tip-list-twist`, a slideshow skeleton cannot be considered finalized until it satisfies a strict two-tier contract.

### Must be true of the Skeleton file itself (`sections/slideshows/skeletons/<name>.md`)

1. **Single Proven Source Post**: Derived from exactly one high-performing TikTok post (>10K saves, verified organic engagement). Must record creator handle, post URL, view count, and save count.
2. **Fixed Slide Count**: Slide count is rigidly fixed to the source post's count. No variable or optional slide ranges.
3. **Mandatory 10-Section Structure**: Must contain all 10 standard sections in exact sequence:
   `Structure` -> `Slide count` -> `Slide by slide` -> `Hook` -> `Images` -> `Text style` -> `Fixed vs open` -> `Why it works` -> `Porting` -> `Source slideshow`.
4. **Per-Slide Specification Block**: Every slide must specify five mandatory fields:
   - **Role**: Transferable engagement mechanism (why the slide exists in the viewer journey).
   - **Text**: Explicit length, formatting, or verbatim content.
   - **Placement**: Exact vertical and horizontal layout zone (e.g. "centred, upper third, small, on empty space above the subject").
   - **Image**: Concrete visual concept, framing, angle, and lighting mood.
   - **Digest Link**: Explicit markdown relative link to a validated JSON style digest in `library/styles/<slug>.json`.
5. **The Three-Level Text Taxonomy**:
   - **Level 1 (Rigid Hook)**: Syntactic template with bracketed variable slots (e.g. `[topic]`, `[demographic]`). Must define slot constraints and list approved demographic options curated directly from `research/tagged-hooks/hooks.md`. Must explicitly document forbidden labels (e.g. no "anxious" or emotional viewer insults).
   - **Level 2 (Fixed Verbatim Lines)**: Any emotionally critical line, confession, joke punchline, or diagnostic pivot must be transcribed word-for-word, retaining original punctuation, casing, and colloquialisms.
   - **Level 3 (Open Lines)**: Specified strictly by word-count ranges (e.g. "an 8-12 word tip") and functional purpose. Never specify sentence structure, parts of speech, line breaks, or connecting words.
6. **Negative Caption-Space Constraint**: Every slide's image description must explicitly specify the negative compositional space (dark car bonnet, plain wall band, out-of-focus background) required to host the text overlay without obscuring the subject or clashing with high-frequency details.
7. **Pure, Product-Free Blueprint**: Strictly zero mentions of ExcerLock, app features, CTAs, accounts (Zoey/Hayden), or character props.
8. **Rhythm Calibration for CTA Insertion**: Open slide length ranges must be calibrated to provide a natural home for a future 10-14 word CTA line, preventing the product slide from standing out as an obvious promotional anomaly.
9. **Curated Porting Examples**: 4 to 5 distinct topical adaptations within the target niche (walking, gym routines, fat loss, physique goals) demonstrating how the slots are filled.
10. **Embedded Source Slideshow Gallery**: Must include direct markdown links displaying every slide image of the source post from `raw/` in sequential order.

### Must be true of the Deck built from it (`sections/slideshows/accounts/<name>/decks/NN-<name>/`)

1. **Pre-Confirmed Scope**: Built only after scope confirmation (`H-scope-confirm`) specifying account, title, and skeleton format.
2. **Account Persona Isolation**: Character description, physique benchmark, approved reference images, wardrobe, and phone case drawn exclusively from `accounts/<name>/account.md`.
3. **Rigid Slot Compliance**: Script hook matches the skeleton's template syntax; demographic chosen from the approved bank; zero unapproved emotional labels.
4. **Verbatim Preservation**: Fixed emotional/punchline slides copied with zero AI paraphrasing.
5. **Calibrated CTA Injection**: Exactly one CTA slide placed at the strategic slot (slide 4 or 5) adhering to the skeleton's typography and word length.
6. **Standard 3-File Deck Artifact**:
   - `script.md`: Clean copy with one-line image ideas and digest links.
   - `review.md`: Written pass/fail verdicts evaluating script rules, image likeness, physique anchors, hands, and negative space.
   - `log.md`: Detailed audit tracking prompts, models used, API calls, costs, and output paths.
7. **Negative Space Verification**: Prompts explicitly carry negative space directives in composition fields; generated images verified to have clean caption zones.
8. **Deterministic Text Overlay**: Rendered via deterministic PIL/script tools (e.g. `overlay.py`) matching the skeleton's specified font, casing, outline, and placement, outputting clean 1080x1920 PNGs.

---

## 3. Gaps in the other four skeletons

Reviewing `contrarian-study-explainer.md`, `do-vs-dont-blunt-coach.md`, `hook-plus-dense-card.md`, and `signs-list-diagnostic.md` against `sections/slideshows/skeletons/README.md` and the `joke-tip-list-twist` standard reveals critical deficiencies. None of the four are currently complete enough to produce a passing deck automatically.

### Summary Gap Matrix

| Requirement | joke-tip-list-twist (Standard) | contrarian-study-explainer | do-vs-dont-blunt-coach | hook-plus-dense-card | signs-list-diagnostic |
|---|:---:|:---:|:---:|:---:|:---:|
| **Source Post Cited** | Yes (7549800558354271504) | Yes (7626326802511727886) | Yes (7677448535113108738) | Yes (7441340934559943982) | Yes (7404352814291488032) |
| **Slide Count Lock** | 7 slides | 8 slides *(Conflicts H-slide-count)* | 8 slides *(Conflicts H-slide-count)* | 2 slides *(Under H-slide-count)* | 8 slides *(Conflicts H-slide-count)* |
| **Rigid Hook Slot Syntax** | Full bracketed template | Missing (loose description) | Incomplete (raw blank `___`) | Missing (narrative description) | Incomplete (raw blanks `___`) |
| **Vetted Demographic Options** | 5 curated bank options | None listed | None listed | None listed | None listed |
| **Negative Constraints** | Explicit (no "anxious") | None | None | None | None |
| **Fixed Verbatim Declarations** | Explicit (Slide 4 exact) | Vague / unquoted | Incomplete (only "Do/Don't") | None (generalized description) | None |
| **Open Word-Count Bounds** | Explicit on all tips | Partial | Present | Word count given, but dense | Present |
| **Caption-Space Specification** | Explicit per slide | General placement only | General placement only | General placement only | General placement only |
| **Style Digest Links** | 7 valid links | 8 valid links | 8 valid links | 2 valid links | 8 valid links |
| **Embedded Source Gallery** | 7 slide images | 8 slide images | 8 slide images | 2 slide images | 8 slide images |
| **Rhythm Calibrated for CTA** | Slide 5/7 calibrated | Uncalibrated | Uncalibrated | Uncalibrated | Uncalibrated |

---

### Detailed File-by-File Deficiencies

#### 1. `contrarian-study-explainer.md` (Source: `@brownricebandit`, 8 slides)
* **Slide Count vs. House Rules**: Uses 8 slides. This directly breaches `H-slide-count` (`sections/slideshows/rules.md`: *"A deck has 5 to 7 slides. Never 8 or more. Why: the captain found 8 too long"*). The skeleton does not provide a 7-slide trim or an approved house-rule override.
* **No Rigid Hook Slot Syntax**: Slide 1 states: `a "STOP doing X to get Y" command, all caps. 8-10 words.` It lacks a formal slotted template (e.g. `STOP [habit] TO [goal]`), defines no slot rules, provides no audience options from `research/tagged-hooks/hooks.md`, and specifies no negative constraints.
* **Missing Fixed Verbatim Specifications**: Slide 2 (promise), Slide 4 (proof), and Slide 7 (recap) describe functional needs but do not specify whether the study citation format or transition phrases are fixed formulas or open copy.
* **No Caption-Space Directives**: Placement is vaguely given as "centred, middle, medium." There is no guidance on where image generation must reserve clean, negative background space to keep the white text legible over complex foliage or trails.
* **Missing CTA Accommodation**: No guidance exists on where ExcerLock can be introduced as the contrarian solution without breaking the academic/habit study framing.

#### 2. `do-vs-dont-blunt-coach.md` (Source: `@charlesjr_fit`, 8 slides)
* **Slide Count vs. House Rules**: Specifies 8 slides, violating `H-slide-count`.
* **Incomplete Hook Template**: Slide 1 states: `"DOs and DON'Ts to ___". 6-7 words.` A raw blank `___` is provided instead of a structured slot definition (`[outcome] for [demographic]`), with zero curated options from the hook bank.
* **Ambiguous Credibility Slot**: Slide 2 allows `1-3 words` over a "before" picture. While "trust me" or "proof" is implied, no approved phrases or verbatim lines are locked, leaving AI free to generate weak or corny phrases.
* **Weak Framing and Negative Space Guidance**: Alternating Do/Don't slides require high text legibility for multi-line commands and reasons, but the skeleton lacks concrete negative-space layout instructions for prompt generation (e.g. top 25% clear for header label, lower third clear for rationale).
* **CTA Conflict**: Lacks calibration for how ExcerLock fits as a "Do" or a solution to a "Don't" without reading like a jarring sponsor segment.

#### 3. `hook-plus-dense-card.md` (Source: `@autumn.wlf`, 2 slides)
* **Extreme Slide Count Violation**: Consists of only 2 slides. `H-slide-count` strictly mandates 5 to 7 slides. In its current form, this format is an anomaly that cannot pass deck review without a formal override in `sections/slideshows/rules.md`.
* **No Rigid Hook Template**: Slide 1 states: `a first-person wish in quotes, the goal with a number, then "but idk…". Lowercase, texting style. 9-13 words.` It relies on informal description rather than an explicit syntax: `"[desire/goal with number] but idk [point of failure]"` with approved target goals drawn from `research/tagged-hooks/hooks.md`.
* **Card Formatting Lacks Machine-Readable Layout**: Slide 2 requires a dense 75-90 word dark notes-app breakdown. The skeleton describes this visually but provides no structural JSON/schema breakdown (Title, 3 Section Headers, Dash Bullets, Numbered Metrics) needed for prompt generation or programmatic canvas rendering.
* **No Product/CTA Strategy**: Fails to define how ExcerLock integrates into the card (e.g. as bullet #2 in daily execution) without violating `H-no-cheat-sheet`.

#### 4. `signs-list-diagnostic.md` (Source: `@babystepsfitness2`, 8 slides)
* **Slide Count vs. House Rules**: Uses 8 slides (Title + 7 signs), violating `H-slide-count`.
* **Incomplete Hook Template**: Slide 1 provides `"N ways you know your ___ is ___", naming a hidden problem without explaining it. 7-9 words.` This contains raw underscores without defining the syntax (`[number] ways you know your [biological/lifestyle factor] is [state]`), missing demographic/subgroup anchors from the hook bank.
* **Missing Emotional/Diagnostic Anchors**: Slides 6 and 8 represent peak emotional resonance ("the most specific sign" and "the most worrying sign"), but provide no verbatim phrasing guidelines, leaving AI vulnerable to producing clinical, bland symptoms.
* **Missing Caption-Space Rules**: The original post uses large, bold text with heavy outlines across the lower third. The skeleton lacks prompt directives ensuring generated food/POV images reserve clean bottom thirds free of visual clutter.

---

## 4. Recommended rebuild

To bring all four skeletons up to the production standard established by `joke-tip-list-twist`, the following concrete modifications must be made to each file.

```
+---------------------------------------------------------------------------------------------------+
|                                  THE SKELETON REBUILD STANDARD                                    |
|                                                                                                   |
|  1. Fixed Slide Count: Lock to 7 slides (reconciling with H-slide-count) or formal override       |
|  2. Rigid Hook Template: "[template]" with explicit [slots] + bank options + negative rules      |
|  3. Verbatim Declarations: Lock emotional, punchline, or diagnostic pivot copy word-for-word      |
|  4. Open Line Calibration: Strict word count bounds (e.g. 8-12 words); zero sentence formulas    |
|  5. Negative Caption-Space: Dedicated prompt-engineering guidance per slide for text clearing    |
|  6. Injected CTA Compatibility: Calibrated rhythm ensuring product slide matches native cadence   |
+---------------------------------------------------------------------------------------------------+
```

### 1. Rebuild Plan for `contrarian-study-explainer.md`

1. **Reconcile Slide Count to 7 Slides**: Merge Slide 5 and Slide 6 (Benefit 1 & 2) into a single high-impact "real-world effect" slide, or eliminate the quiet sign-off slide (Slide 8) in favor of ending on the strong Slide 7 recap. This creates a compliant 7-slide deck:
   - Slide 1: Contrarian Command (Hook)
   - Slide 2: The Promise
   - Slide 3: The Method
   - Slide 4: The Study Proof
   - Slide 5: The Real-World Benefit (ExcerLock CTA slot)
   - Slide 6: The Full Protocol Recap
   - Slide 7: The Final Takeaway / Bookmark Call
2. **Standardize Rigid Hook Template**:
   - **Template**: `STOP [habit] TO [outcome]`
   - **Slot `[habit]`**: A widely accepted, high-effort fitness habit (e.g., `doing 10k steps in one go`, `going to the gym 6 days a week`, `doing hours of fasted cardio`).
   - **Slot `[outcome]`**: A primary aesthetic/health goal (e.g., `lose belly fat`, `grow glutes`, `build your dream body`).
   - **Demographic Anchors from Hook Bank**: Target beginner lifters, desk-job workers, girls with stubborn fat.
   - **Negative Constraints**: No insulting labels; no obscure exercise acronyms.
3. **Specify Caption-Space Directives**:
   - Slide 1: Upper-middle clear sky/fog band reserved for 3-line bold caps header.
   - Slides 2–6: Centre 50% vertical frame reserved for clean, low-contrast background (mist, blurred trail, minimal bokeh) to support white sans-serif text.
4. **Calibrate CTA Slot (Slide 5)**:
   - Frame Slide 5 as the practical execution mechanism (14–18 words): explaining how automating walking consistency or app blocking enforces the protocol without relying on motivation.

---

### 2. Rebuild Plan for `do-vs-dont-blunt-coach.md`

1. **Reconcile Slide Count to 7 Slides**: Contract the sequence from 8 to 7 slides by structuring as:
   - Slide 1: Title / Result Hook
   - Slide 2: Credibility / Before Proof
   - Slide 3: The Non-Negotiable Ground Rule
   - Slide 4: "Do." (Simple positive habit)
   - Slide 5: "Don't." (Common mistake / ExcerLock CTA slot)
   - Slide 6: "Do." (Surprising high-leverage replacement)
   - Slide 7: "Don't." (Over-relied-on trap & exit rule)
2. **Standardize Rigid Hook Template**:
   - **Template**: `DOs and DON'Ts to [outcome] for [demographic]`
   - **Slot `[outcome]`**: `lose stubborn fat`, `tone your body`, `build glutes without getting bulky`.
   - **Slot `[demographic]`**: Options from hook bank: `beginners`, `busy girls`, `lazy girls`, `girls starting from zero`.
   - **Negative Constraints**: Do not use vague clinical terms; keep the tone grounded and conversational.
3. **Lock Fixed Verbatim Formats**:
   - Slide 2 Credibility: Lock to exact, blunt proof lines: `"proof this works"`, `"trust me on this"`, or `"from someone who was stuck for years"`.
   - Slides 4–7: Require rigid uppercase labels `"Do."` and `"Don't."` followed by a command line (4–7 words) and a reason line (8–12 words).
4. **Specify Caption-Space Directives**:
   - Upper 20% reserved for 60pt `"Do."` / `"Don't."` bold label.
   - Lower 35% reserved for command and explanation over clean foreground elements (flat floor, grass, uncluttered clothing).

---

### 3. Rebuild Plan for `hook-plus-dense-card.md`

1. **Reconcile Structural Anomaly**:
   - **Option A (House Override)**: Formally record an explicit override in `sections/slideshows/rules.md` under `H-slide-count` creating a sanctioned 2-slide "Card Breakdown" format exception.
   - **Option B (Expansion to 5 Slides)**: Break the card into a narrative progression: Slide 1 (Quoted Wish), Slide 2 (The Calorie/Step Math), Slide 3 (The Workout Split), Slide 4 (The Consistency Lock / ExcerLock CTA), Slide 5 (The Summary Blueprint Card).
2. **Standardize Rigid Hook Template (Slide 1)**:
   - **Template**: `"[desire/goal] but idk [stumbling block]..."`
   - **Approved Slots from Hook Bank**:
     - `"i want to lose 5kg before summer but idk where to start..."`
     - `"i want to start going to the gym 4 times a week but idk what to do..."`
     - `"i want to walk 15k steps a day but idk how with my job..."`
   - **Negative Constraints**: Lowercase only; quotation marks mandatory; must sound vulnerable, never confident.
3. **Standardize Structured Card Schema (Slide 2)**:
   - Machine-readable layout specification:
     - Header: All-caps bold goal title (`[TARGET GOAL] BREAKDOWN:`).
     - Section 1 (Diet/Steps): 2 dash bullets with exact numerical targets.
     - Section 2 (Training): 2 dash bullets with split/frequency.
     - Section 3 (Rule of Thumb): 1 concluding takeaway bullet.
4. **Specify Caption-Space Directives**:
   - Slide 1: Candid, off-centre selfie reserving middle third (over torso/clothing) for dark or light clean captioning.
   - Slide 2: 100% black digital canvas (`#0F0F0F`) rendered directly via PIL, bypassing image generator hallucination.

---

### 4. Rebuild Plan for `signs-list-diagnostic.md`

1. **Reconcile Slide Count to 7 Slides**: Contract from 8 to 7 slides (Title + 6 Signs) to comply with `H-slide-count`.
2. **Standardize Rigid Hook Template**:
   - **Template**: `[N] ways you know your [biological factor/lifestyle] is [unfavourable state]`
   - **Approved Slots**:
     - `[N]`: Rigid integer matching slide count (`6`).
     - `[biological factor]`: `cortisol`, `metabolism`, `daily routine`, `step count`.
     - `[unfavourable state]`: `wrecked`, `high`, `holding you back`, `keeping you bloated`.
   - **Negative Constraints**: Do not diagnose clinical diseases; focus on lifestyle-relatable symptoms.
3. **Lock Fixed Diagnostic Tone**:
   - Slide 2 (Sign 1): Immediate physical identification (5–7 words).
   - Slide 4 (Sign 3): Mental/cognitive symptom (4–5 words).
   - Slide 6 (Sign 5): Hyper-specific daily habit moment (10–14 words).
   - Slide 7 (Sign 6 / Final): The unresolved sign that drives comments/saves (5–7 words, no solution).
4. **Specify Caption-Space Directives**:
   - Lower 35% of the 3:4/9:16 frame reserved for high-contrast, large TikTok-caption text over dark tables, simple floors, or neutral countertops.

---

## 5. Automation design

The manual prompt assembly and PIL overlay workflow implemented in `raw/zoey-06/prepare-prompts.py`, `raw/hayden-06/prepare-prompts.py`, and `raw/hayden-06/overlay.py` proved that production can be deterministic, repeatable, and fast. To eliminate custom per-deck scripting, we design a unified, machine-readable pipeline.

```
+--------------------------------------------------------------------------------------------------------+
|                                  THE END-TO-END AUTOMATION PIPELINE                                    |
|                                                                                                        |
|  [skeleton.json] + [account.md] + [topic/demographic]                                                 |
|                           |                                                                            |
|                           v                                                                            |
|               1. Script-Filler (fill-script.py)                                                        |
|                           |                                                                            |
|                           v                                                                            |
|                      script.md                                                                         |
|                           |                                                                            |
|                           v                                                                            |
|               2. Prompt-Builder (build-prompts.py) <--- library/styles/*.json                          |
|                           |                                                                            |
|                           v                                                                            |
|                     prompts/s*.json                                                                    |
|                           |                                                                            |
|                           v                                                                            |
|               3. Validator (check.py --rules image-rules.json)                                         |
|                           |                                                                            |
|                           v                                                                            |
|               4. Batch Runner (run-deck-batch.py)                                                      |
|                   /               \                                                                    |
|                  v                 v                                                                   |
|          Nano Banana 2         GPT Image 2                                                             |
|          (Character)           (Still Life)                                                            |
|                  \                 /                                                                   |
|                   v               v                                                                    |
|               5. Image Review & Crop Panels                                                            |
|                           |                                                                            |
|                           v                                                                            |
|               6. Overlay Engine (overlay-captions.py)                                                  |
|                           |                                                                            |
|                           v                                                                            |
|                   Final 1080x1920 PNGs                                                                 |
+--------------------------------------------------------------------------------------------------------+
```

### 1. Machine-Readable Skeleton Schema (`skeleton.json`)

Every skeleton will be represented as a structured JSON/YAML file alongside its markdown documentation:

```json
{
  "$schema": "https://json-schema.excerlock.com/v1/slideshow-skeleton.json",
  "id": "joke-tip-list-twist",
  "version": "1.1.0",
  "source": {
    "creator": "@gazellleee",
    "post_url": "https://www.tiktok.com/@gazellleee/photo/7549800558354271504",
    "metrics": { "views": 2600000, "saves": 82700 }
  },
  "slide_count": 7,
  "aspect_ratio": "9:16",
  "slides": [
    {
      "slide_number": 1,
      "role": "Title hook, sincere appearance",
      "text_tier": "rigid_hook",
      "text_spec": {
        "template": "{count} {topic} tips for {demographic}",
        "default_count": 6,
        "demographic_options": ["beginners", "beginner gym girls", "girls starting from zero", "lazy girls", "tall girls"],
        "forbidden_labels": ["anxious", "sad", "insecure", "depressed"],
        "case": "lower",
        "punctuation": "none"
      },
      "layout": {
        "placement": "upper_third",
        "alignment": "center",
        "font_size_pt": 66,
        "outline_width": 4
      },
      "composition": {
        "capture_type": "mirror_selfie",
        "framing": "full-body mirror selfie framed by squat rack uprights",
        "face_visibility": "covered_by_phone",
        "body_visible": true,
        "phone_visible": true,
        "caption_space": "uncluttered pale wall band above head reserved for one-line title"
      },
      "style_digest": "gazellleee-1504-s1-squat-rack-mirror-title"
    },
    {
      "slide_number": 4,
      "role": "Heartbreak twist interruption",
      "text_tier": "fixed_verbatim",
      "text_spec": {
        "verbatim_text": "3. remember how you felt the night you found out everything",
        "case": "lower",
        "punctuation": "none"
      },
      "layout": {
        "placement": "lower_third",
        "alignment": "center",
        "font_size_pt": 52,
        "outline_width": 3
      },
      "composition": {
        "capture_type": "front_camera_selfie",
        "framing": "tilted close selfie inside dark car at night",
        "face_visibility": "clearly_visible_first_time",
        "body_visible": false,
        "phone_visible": false,
        "caption_space": "dark lower-left area kept open for caption"
      },
      "style_digest": "gazellleee-1504-s7-night-car-selfie-tilt"
    }
  ]
}
```

### 2. The Core Pipeline Modules

1. **`fill-script.py` (Script Filler)**:
   - Takes `--skeleton`, `--account`, `--topic`, `--demographic`, and optional `--cta-text`.
   - Validates that the hook template matches the skeleton schema and does not use forbidden labels.
   - Enforces verbatim strings on `fixed_verbatim` slides.
   - Verifies open tip word counts against min/max ranges.
   - Injects the CTA into the designated slot (slide 4 or 5) ensuring word length matches surrounding tips.
   - Outputs `sections/slideshows/accounts/<account>/decks/<NN-slug>/script.md`.

2. **`build-prompts.py` (Generalized Prompt Builder)**:
   - Replaces the hardcoded `raw/*/prepare-prompts.py` scripts.
   - Ingests `script.md`, `skeleton.json`, `accounts/<account>/account.md`, and the style digests from `library/styles/`.
   - Dynamically constructs prompt JSONs for each slide:
     - Merges account identity, hair, skin, appeal, and physique specs for character slides.
     - Maps `caption_space` from `skeleton.json` directly into the prompt's `composition.space` constraint.
     - Assembles reference manifests (character ref, physique anchor, case ref) dynamically based on `slide.composition.body_visible` and `slide.composition.phone_visible`.
   - Emits `raw/<deck>/prompts/s1.json` through `sN.json`.

3. **`validate-deck.py` (Schema & Rule Validator)**:
   - Runs `core/skills/image-prompt/check.py check` with `--rules sections/slideshows/image-rules.json` across all prompt JSONs.
   - Verifies reference image existence on disk.
   - Validates compliance with `H-no-watch`, `H-phone-case`, and brand consistency rules before a single dollar is spent.

4. **`run-deck-batch.py` (Batch Runner)**:
   - Replaces ad-hoc `run-nano-group.py`.
   - Inspects each prompt: routes slides with character presence (`body_visible=true` or `face_visibility!=none`) to Nano Banana 2 (`gemini-3.1-flash-image`), and object/food slides to GPT Image 2 (`gpt-image-2`).
   - Executes calls concurrently using `ThreadPoolExecutor`.
   - Decodes base64 candidate parts, saves standard JPEGs to `raw/<deck>/generated/`, and logs token/call usage metadata.

5. **`overlay-captions.py` (Deterministic Overlay Engine)**:
   - Generalizes `raw/hayden-06/overlay.py`.
   - Ingests generated images and `skeleton.json` typography specifications.
   - Executes deterministic PIL rendering:
     - Loads approved system font (Arial/Helvetica Bold).
     - Calculates safe word wrap (max width 86% of frame).
     - Renders TikTok Classic style: crisp white text with dynamic black stroke outlines.
     - Calculates precise vertical anchor (`top` at 7% frame height, `lower` at 66% frame height).
   - Exports pristine 1080x1920 PNGs into `raw/<deck>/final/`.

### 3. Tracked Files vs. Scratch Artifacts

To preserve repository hygiene while maintaining full auditing capabilities:

* **Tracked under `sections/slideshows/` (Committed to Git)**:
  - `skeletons/*.json`: Machine-readable skeleton definitions.
  - `tools/fill-script.py`, `tools/build-prompts.py`, `tools/run-deck-batch.py`, `tools/overlay-captions.py`: The universal pipeline scripts.
  - `accounts/<account>/decks/<NN-slug>/script.md`: The approved text script.
  - `accounts/<account>/decks/<NN-slug>/review.md`: Written review verdicts and crop validations.
  - `accounts/<account>/decks/<NN-slug>/log.md`: Build audit log (prompts, models, costs, references).
* **Scratch under `raw/<deck-slug>/` (Gitignored)**:
  - `prompts/s*.json`: Concrete prompt instances.
  - `generated/s*-v*.jpg`: Raw, uncaptioned generator outputs.
  - `review-panels/`: 2x zoom crop grids evaluating face, hands, physique, and negative space.
  - `preview.html`: HTML review sheets for side-by-side captain evaluation.
  - `final/s*.png`: Rendered, full-resolution 1080x1920 captioned PNGs ready for TikTok posting.

---

## 6. Iteration & adaptability

To ensure the slideshow production system scales smoothly, handles model deprecations, adapts to new feed trends, and systematically learns from captain feedback, five key feedback and governance mechanisms are established.

### 1. `make-universal` Feedback Ingestion
* **Mechanism**: When the captain rejects a script line, layout, prompt detail, or image aesthetic and issues a correction, the `make-universal` workflow (`core/skills/make-universal/SKILL.md`) routes the rule back to the exact root file responsible.
* **Architecture**:
  - Script text or rhythm errors -> Updated in `sections/slideshows/skeletons/<name>.json` and `.md`.
  - Image prompt defects (e.g., unwanted smartwatch, bad camera angle) -> Updated in `sections/slideshows/image-rules.json` and `core/skills/image-prompt/SKILL.md`.
  - Persona or wardrobe errors -> Updated in `accounts/<name>/account.md`.
  - Broad format constraints -> Updated in `sections/slideshows/rules.md`.
* **Rationale**: This prevents recurrent mistakes across independent agent sessions, guaranteeing that every captain critique permanently improves the automated pipeline.

### 2. Standardized 5-Step Skeleton Intake Protocol
* **Mechanism**: A formal workflow for converting newly discovered, high-performing TikTok posts into production skeletons:
  1. *Screening*: Verify organic performance (>10K saves, verified repeatable structure; reject textless memes or narrow workout routines).
  2. *Slide Extraction*: Download all slide images to `raw/skeletons/<source-id>/`.
  3. *Style Cloning*: Run `core/skills/style-clone/SKILL.md` to produce standalone JSON digests in `library/styles/` for every slide.
  4. *Schema & Doc Drafting*: Author `sections/slideshows/skeletons/<slug>.json` and `<slug>.md`, establishing rigid hook slots, verbatim lines, open length ranges, and caption-space rules.
  5. *Test Deck Verification*: Run a test script and batch image generation to confirm prompt stability and text legibility before certifying the skeleton for production use.
* **Rationale**: Standardizing intake ensures new formats enter the library at the high quality level of `joke-tip-list-twist` rather than requiring multiple rounds of corrective refactoring.

### 3. Semantic Versioning and Deck Lineage
* **Mechanism**: Every skeleton carries an explicit semantic version (e.g. `v1.0.0`, `v1.1.0`), tracked in its JSON schema and Markdown header. When a deck is scripted, its `script.md` and `log.md` record the exact skeleton version used:
  `Skeleton: joke-tip-list-twist@1.1.0`
* **Rationale**: Skeletons will evolve as TikTok trends shift (e.g. caption placement changes, hook templates adjust). Explicit version lineage ensures that older decks remain reproducible and allows retrospective performance analysis to tie success or failure to specific skeleton iterations.

### 4. Continuous Decision-Log Telemetry (`declog.py`)
* **Mechanism**: The repository's background watcher (`tools/decision-log/declog.py`) runs every 30 minutes, archiving agent transcripts into `log/transcripts/` and extracting tasks, decisions, corrections, and artifacts into `log/events.jsonl` and `log/LOG.md`.
* **Integration**: Automated pipeline scripts (`build-prompts.py`, `run-deck-batch.py`) will automatically query the latest decision event ID and stamp it into the deck's `log.md`.
* **Rationale**: This guarantees an unbroken audit trail connecting high-level captain instructions directly to code commits, prompt adjustments, and image generations without requiring manual note-taking by human operators or agent wrappers.

### 5. Post-Publishing Performance Analytics Loop
* **Mechanism**: A dedicated post-performance tracker in `research/performance/deck-metrics.csv` recording:
  `deck_id, skeleton_id, account, views_24h, views_7d, saves_7d, save_ratio_per_1k, comments, completion_rate`
* **Feedback Integration**: Decks achieving save ratios above 25 per 1K views automatically promote their underlying skeleton to "Tier 1 Preferred" status in `sections/slideshows/skeletons/README.md`. Skeletons yielding below 10 saves per 1K across three consecutive executions are flagged for structural review or retirement.
* **Rationale**: Marketing research requires closing the loop between creative generation and distribution metrics. Tying live feed analytics directly back to skeleton definitions ensures resources are continuously focused on the formats that drive the lowest customer acquisition costs.

---

## Conclusion & Next Steps

The `joke-tip-list-twist` skeleton succeeded because it was forced through rigorous operational constraints: a rigid hook template derived from real feed data, word-for-word preservation of human emotional copy, strictly bounded open tips, explicit negative caption-space planning, and deterministic text overlay.

By updating `contrarian-study-explainer`, `do-vs-dont-blunt-coach`, `hook-plus-dense-card`, and `signs-list-diagnostic` to this standard, establishing machine-readable `skeleton.json` specifications, and unifying generation via a centralized CLI pipeline, the repository can achieve reliable, push-button slideshow production across all active and future character accounts.
