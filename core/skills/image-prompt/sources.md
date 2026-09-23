# Sources, coverage and prompt audit

Research date: 2026-09-22. This file records the evidence behind `skills/organic-json-image-prompting.md`
and states where that evidence stops. Raw captures are kept in the gitignored `raw/ojip/`, not in the repo.

## 1. Official vendor documentation

| Source | What it says that we use |
|---|---|
| OpenAI, Image prompting guide: https://developers.openai.com/api/docs/guides/image-prompting | Structure the prompt as background/scene → subject → details → constraints; **"JSON-like structures"** are an acceptable format; be specific about materials, texture and light; photographic terms (lens, framing, light) are appearance cues, not physics simulation; for edits, say what changes and what must stay identical, and repeat the constraints on each turn; label multiple reference images by number and give each a role; put exact text in quotes and spell out unusual words; set model, size and quality as API parameters, not in the prompt text; consistency across generations is a known limitation. |
| OpenAI, Image generation guide: https://developers.openai.com/api/docs/guides/image-generation | Models `gpt-image-2`, `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst`. `quality` from `low` upward (low is fastest and cheapest). Custom sizes: multiples of 16, ratio ≤ 3:1, 655,360–8,294,400 pixels, longest edge ≤ 3840. Image API `/v1/images/generations` and `/v1/images/edits` (reference images and masks). In the Responses API the mainline model **rewrites** the prompt (`revised_prompt`), while the Image API sends it unchanged; a `moderation` parameter exists. |
| Google, Gemini API image generation: https://ai.google.dev/gemini-api/docs/image-generation | Nano Banana 2 = `gemini-3.1-flash-image`. Interactions API `POST https://generativelanguage.googleapis.com/v1beta/interactions` with `input` parts and `response_format {type: "image", aspect_ratio, image_size}`. Sizes use uppercase K; 3.1 Flash adds a 512 px tier. `thinking_level` defaults to minimal. Up to 14 reference images; 3.1 Flash handles up to 10 object images and 4 characters. Best practices: be hyper-specific, give context and intent, iterate, go step by step, use **semantic negative prompts** (describe the wanted state positively), and control the camera explicitly. Output carries a SynthID watermark. |
| Google Cloud blog, Ultimate prompting guide for Nano Banana: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana | Formulas: subject + action + location/context + composition + style, and for references: reference images + relationship instruction + new scenario; exact text goes in quotes; outputs carry SynthID and C2PA provenance. |
| Google Cloud blog, Nano Banana 2 for enterprise: https://cloud.google.com/blog/products/ai-machine-learning/bringing-nano-banana-2-to-enterprise | Positioning and availability of Nano Banana 2 (3.1 Flash Image). No prompt-format rules. |
| Google Developers blog (2025), How to prompt Gemini 2.5 Flash Image: https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/ | "Describe the scene, don't just list keywords"; photorealistic template that names camera, lens, lighting and aspect ratio. Written for the older model, but the principle still holds. |
| Google, Gemini app image tips: https://blog.google/products/gemini/image-generation-prompting-tips/ | Consumer-app tips (be specific, iterate, give context). No API fields. |

**Universal principles** (both vendors, part of our JSON):
- Be specific and descriptive.
- Separate the scene, subject, details and constraints.
- State edits as "change X, keep Y".
- Give every reference image a role.
- Quote exact text.
- Describe the wanted state positively, and keep negatives short.
- Iterate one change at a time.

**Vendor fields** (API parameters, never in the prompt):
- OpenAI: `model`, `size`, `quality`, `n`, `output_format`, `moderation`, and the edits endpoint.
- Gemini: `model`, `response_format.aspect_ratio`, `response_format.image_size`, `thinking_level`, and image parts.

Neither vendor defines a JSON prompt schema. The JSON structure is our house format; the vendors
accept it as a string prompt, and OpenAI explicitly lists JSON-like structure as acceptable.

Gap: the Gemini page's examples show only `"1K"` and `"2K"` literals. The 512 value is taken from
the captain's standing Nano Banana setting and must be confirmed on first use.

## 2. The six linked posts

Fetched through the public fxtwitter API on 2026-09-22. Metrics are as observed on that date and do
not show that a prompt converts.

| # | Linked URL | Posted (UTC) | Observed | What the post actually contains | Match with the brief's description |
|---|---|---|---|---|---|
| 1 | https://x.com/brainextends/status/2102101151894458867 | 2026-09-21 | 82 likes, 5,020 views | Long JSON (`prompt_type`, `objective`, scene, identity "original fictional adult woman", camera, lighting, imperfections, negative prompt). Warm, dim bedroom selfie, used as a first frame for Seedance/OmniHuman video. 2 images. | Matches. |
| 2 | https://x.com/sixugc/status/2102378446366114190 | 2026-09-22 | 74 likes, 3,943 views | JSON with `meta` (9:16, "ultra_photorealistic", "4K", iPhone front camera ~24 mm), scene (lying on a white towel on a public beach), subject with "Reproduce their appearance precisely." | Matches (beach-towel selfie). |
| 3 | https://x.com/theinsiderzclub/status/2102241592606101861 | 2026-09-22 | 1 like, 269 views | JSON reference reconstruction: close front-camera selfie, strapless satin top, dim luxury living room. | Matches the scene, but the prompt text is a near copy of @noneugc https://x.com/noneugc/status/2102097905771270286 (the original, ~1.09M views). Treat it as a repost. |
| 4 | https://x.com/Kel_vinleven/status/2102357613073596909 | 2026-09-22 | 23 likes, 1,084 views | JSON `photorealistic_image_recreation`: seated stretch on a platform in a modern gym, `identity_handling`. The post text says to make one character and move it across scenes and outfits. 3 images. | Matches. |
| 5 | https://x.com/noneugc/status/2102447818786930793 | 2026-09-22 | 28 likes, 1,486 views | JSON `…_with_product_replacement`: recreate a **bedroom** selfie and swap the skincare tube in her hand for another product. | **Mismatch.** The brief describes a reclined outdoor fitness selfie with identity variation; that is @noneugc https://x.com/noneugc/status/2102372927123407043 (turf). Both were studied. |
| 6 | https://x.com/filipugc/status/2102400193681403931 | 2026-09-22 | 131 likes, 9,295 views | JSON `…_with_targeted_modifications`: high-angle bathroom selfie; "subtly alter the woman's facial identity" and recolour the outfit. | **Partial.** Only the bathroom selfie is here; the close leaning portrait is @filipugc https://x.com/filipugc/status/2102336604652159180. Both were studied. |

**Shared template.** Five of the six posts use one template family: `prompt_type`, `objective`,
`reference_fidelity`, `canvas`, scene / subject / camera / lighting / imperfections blocks,
`negative_prompt`, `final_generation_instruction`. Several of the accounts are affiliated with
@affiliatenw and share and recycle prompts.

**Adopted:**
- Structured JSON with separate camera, lighting, imperfection and negative blocks.
- Ordinary phone optics.
- Explicit imperfection lists.
- Fictional adult identity stated outright.
- Still images used as video first frames.
- Change-only edits for product swaps.
- The reference photo drives the realism, which in our workflows becomes style digests plus manifest-fenced scene sources.

**Rejected:**
- "Reproduce their appearance precisely" and "subtly alter facial identity". Both derive a person from a real person's likeness; our W3 replaces the person with a fictional character and fences off the source identity.
- "4K", "ultra photorealistic" and maximum quality. Captain rule: lowest quality.
- Blanket "no logos / no brand names" negatives. Captain rule: keep natural brands.
- Beauty processing ("flawless", "glowing").
- Recreating a reference "as closely as possible" as a whole, instead of describing a new scene.

## 3. Account audit

The public fxtwitter timeline API was paged newest-first, with a 15-page cap per account.
"Own fetched" counts the account's own posts that were returned; replies, threads beyond the first
post, deleted posts, and most attached media were **not** covered. X history is truncated, so none of
these counts is complete coverage.

| Account | Profile post count | Own posts fetched | Oldest fetched | Stop reason | JSON image prompts found |
|---|---|---|---|---|---|
| @brainextends https://x.com/brainextends | 502 | 116 | 2026-05-08 | timeline exhausted | 1 (the linked post) |
| @sixugc https://x.com/sixugc | 315 | 110 | 2026-07-18 | exhausted | 1 JSON; prose prompts in 2101008502487429596 and 2098443522646974529 |
| @theinsiderzclub https://x.com/theinsiderzclub | 6,191 | 144 | 2025-07-20 | page cap | 1 (the linked repost) |
| @Kel_vinleven https://x.com/Kel_vinleven | 12,324 | 215 | 2025-10-23 | page cap | 2 (linked post; video JSON 2099043573760934227) |
| @noneugc https://x.com/noneugc | 28 | 10 | 2026-09-11 | exhausted | 3 (2102097905771270286, 2102372927123407043, 2102447818786930793) |
| @filipugc https://x.com/filipugc | 248 | 84 | 2026-03-29 | exhausted | 2 (2102336604652159180, 2102400193681403931) |
| @jasonugc https://x.com/jasonugc | 1,443 | 256 | 2026-07-09 | page cap | 8 (2101021087278543040 gym recreation; 2099547856486989951 not parseable; 2101933444376781043; 2102063569349013925; 2101372937353965940 two women; 2101727704378659179 kitchen, 227K views; 2102329429875724480 gym modifications; 2102447417194877159 car) |

Status links are `https://x.com/<account>/status/<id>`.

Tip posts that shaped the doctrine:
- @brainextends 2099941049800315216: the reference is the key; keep the image "really normal"; imperfections matter; keep the video prompt simple.
- @sixugc 2098047399264469048: analyse a photo into JSON, then generate from it; the AI tells are flat colour and plastic grain.
- @sixugc 2098448587533205861: more references give better consistency.
- @sixugc 2100680487958098317 and 2098443407647498280: character consistency.
- @jasonugc 2090447117668298922: the reference image drives the realism.

## 4. Audit of image prompts already in this project

Classification: **true JSON** (a structured prompt sent as JSON), **prose in a JSON envelope** (the
API body is JSON but the prompt is a prose string; not acceptable), or an **ad-hoc edit instruction**
(a one-off "change X" sentence).

| Location | Classification | Notes |
|---|---|---|
| `content/slideshows/01-*.md` … `05-*.md` ("Prompt:" lines, 21 in total) | prose | Written per slide; no manifest. |
| `skills/organic-iphone-photo.md` (before this change) | prose in a JSON envelope | JSON wrapper whose `full_prompt_string` was one prose string. Now superseded. |
| `skills/style-clone.md` Step 4 "quick append" (before this change) | prose | Appended digest fragments to a prose prompt. Now replaced by the JSON workflow. |
| `scripts/image-reimagine.py` | prose in a JSON envelope | Builds prose and posts it inside an OpenAI request body. Legacy; migrating it to `scripts/image-prompt.py wrap` is follow-up work. |
| `research/slideshows/image-build-log.md` | prose + ad-hoc edits | Prompts were built as prose by an external `tools/build_prompts.py`; the 3.1 fixes were one-line edit instructions. |
| `content/styles/*.json` | true JSON, but **inputs** | Style digests, not prompts. They feed W1/W3 as text. |
| Firstmate data (outside the repo): `data/hayden-character-options/*.prompt.json` | true JSON, ad-hoc schema | `json.dumps` of an unversioned schema; no manifest or house-rule check. |
| Firstmate data: Hayden Nano Banana anchor and strict-edit prompts | prose + ad-hoc edits | — |
| Firstmate data: `slideshows-02-05-images` (44 `prompt.txt`) and `slideshow-01-final` (18) | prose | — |

Gaps found and closed by this change:
- **No reference-role manifest.** Attached images had no stated role or no-transfer list. Closed by `references.manifest`.
- **No canonical character JSON in the repo.** Closed by `organic-character/1` and `content/characters/`.
- **Blanket logo negatives**, for example "no readable brand logos" and the reviewer's "unbranded" cup. Replaced with natural branding.
- **No validation.** Closed by `scripts/image-prompt.py check`.
- **A reference image that shows an Apple Watch** (the leopard-case "our girl" reference in Firstmate data). The manifest checklist now forbids attaching such a reference.

## 5. Reconciliation log

| File | Change |
|---|---|
| `skills/organic-iphone-photo.md` | Retired to a pointer; its polish-level table moved to the book. |
| `skills/style-clone.md` | Stays as the digest step. Digests record natural brands; vision runs via the Gemini CLI or the worker's own model (never Grok); Step 4 now hands off to the JSON workflow; "no readable brand logos" removed. |
| `skills/image-reimagine.md` | Marked legacy (prose runner); new work uses W1 or W3. |
| `content/styles/README.md` | Digests feed the JSON prompt as text and are never attached. |
| `AGENTS.md`, `README.md`, `skills/fal-video.md` | Point to the book and `scripts/image-prompt.py`. |
| `research/slideshows/script-writing-guide.md`, `reviewer-checks.md`, `content/slideshows/README-02-05.md` | Point to the book; natural branding replaces "unbranded"; the reviewer receives the prompt JSON and manifest; W3 is the only workflow that attaches an organic photo for a body shot, fenced by `must_not_transfer`. |
| Captain correction, 2026-09-22 | "Organic" is the photo's treatment only, never plainer casting. Added the `appeal` axis (schema, character sheet, examples), appeal-lowering wording checks, a wrap note, a failure-mode row, and a positive reviewer check (`reviewer-checks.md` Step 1b). |
