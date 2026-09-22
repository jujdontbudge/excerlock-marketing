# Organic JSON image prompting — the one image-prompting path

Every image this project generates or edits starts from one JSON document that follows
`skills/organic-json-image-prompting/schema.json` (`organic-image-prompt/1`). Loose prose prompts,
prose inside a JSON field, and ad-hoc "just change X" edit instructions are not allowed. The goal
above everything else: the result must look like an ordinary, organic phone photo, not an AI image.

Files:

| Path | What it is |
|---|---|
| `skills/organic-json-image-prompting/schema.json` | The canonical strict schema. Every key is required; use `null`, `false`, `0` or `[]` when a field does not apply. |
| `scripts/image-prompt.py` | `check FILE...` validates schema and house rules; `wrap FILE --target openai\|gemini\|codex` prints the exact request that would be sent. No network, no generation. |
| `skills/organic-json-image-prompting/examples/` | One valid example per workflow and per source scene class (index at the end). |
| `skills/style-clone.md` | Step 1 of style work: digest an inspiration image into non-identifying style JSON in `content/styles/`. |
| `skills/organic-json-image-prompting/sources-and-audit.md` | Research behind this book: official docs, the X posts and accounts studied, coverage limits, and the audit of past prompts in this repo. |

## 1. Standing rules (captain)

These hold in every workflow. `scripts/image-prompt.py check` enforces the ones marked ✓.

1. **The prompt sent to the model is JSON.** ✓ `wrap` sends one JSON document: `{instruction, attached_images, image}`. The only prose is the one-sentence `instruction` inside it.
2. **Organic realism beats everything else**: ordinary phone optics and processing, imperfect framing, mixed light, noise, compression, real skin, flyaways, clutter, plausible anatomy and geometry. Never optimise for clean, cinematic or beautiful.
3. **Lowest quality setting, one image at a time.** OpenAI `quality: "low"`, `n: 1`, and the smallest valid size that keeps the ratio (`wrap` computes `720x1280` for 9:16). Nano Banana 2 (`gemini-3.1-flash-image`) at `image_size: "512"` with the default `minimal` thinking. No batch unless the captain asks for one, and state the per-image cost first. Low quality is the goal, not a compromise: high quality reads as professional or AI and was rejected.
4. **Keep natural brands.** ✓ Where a real scene would show a brand (plates, shoes, supplements, packaging, machines, cars), keep real-looking branding. Never add blanket "no logos" exclusions. Still exclude invented words, garbled labels, captions and watermarks.
5. **No Apple Watch**, anywhere. ✓ A person in frame requires an Apple Watch exclusion; mentioning one anywhere else fails the check.
6. **A visible phone always has a case.** ✓ Do not add a phone where none belongs: a front-camera selfie shows no phone, a mirror selfie shows the case facing the mirror, and a scrolling scene shows the phone edge-on.
7. **Keep the place type and the scene concept.** A commercial gym stays a commercial gym; a home kitchen stays a home kitchen. State this in `intent.place_type` and `intent.must_stay_true`.
8. **Physically logical scenes**: loaded bars are loaded equally, one pair of headphones, cables run to pulleys, and reflections obey the mirror.
9. **Adults only, fictional only.** ✓ Every person is a stated adult (`identity.fictional` is always `true`). Never reproduce a real person's face, body, tattoos or identifying marks.
10. **Inspiration images go to a vision model, not to the generator.** Only the non-identifying style JSON reaches generation. An original image goes to the generator only when a workflow below says so (surgical edit, insertion, person replacement), and each attached image carries a manifest entry. ✓
11. **Reference images stay out of the repository**: they live in the gitignored `raw/` or outside the repo. ✓
12. **Generation is approval-gated** and runs through the API keys (OpenAI Image API, Gemini API), not through subscription tools, unless the captain says otherwise. Vision and style-digest work uses the Gemini CLI subscription or the worker's own model, never Grok and never the Gemini API key.
13. **A separate reviewer judges every image** with its reference beside it: `research/slideshows/reviewer-checks.md`.

## 2. The pipeline

```
organic/inspiration photo ──► vision model (style-clone) ──► content/styles/<slug>.json (non-identifying)
                                                                   │  text only
character sheet + approved refs ─────────────────────────────┐     ▼
                                                              ├─► prompt JSON (this schema) ──► image-prompt.py check
product / wardrobe / edit target / organic scene source ─────┘         │
          (attached only when the workflow says so, each with a        ▼
           manifest entry)                                     image-prompt.py wrap ──► approval ──► ONE generation
                                                                                                        │
                                                         separate reviewer (reviewer-checks.md) ◄───────┘
```

Boundary rule: **the style digest is text inside the JSON; it is never attached.** The inspiration
image never reaches the generator in the style-clone workflow. When an image is attached, the JSON
still describes the whole intended image, as if no image were attached. References reinforce the
description; they never replace it.

## 3. Pick the workflow (`mode`)

| Situation | `mode` | Images attached to the generator |
|---|---|---|
| No style or organic reference | `first_principles` (W4) | none |
| Copy a liked photo's style into a new scene | `style_clone_new_scene` (W1) | none (digest as text) |
| Established fictional character, new image | `character_new_image` (W2) | approved character refs (+ physique anchor / body benchmark for body shots) |
| Put our character in place of the person in an organic photo | `character_replaces_person` (W3) | the organic photo + character refs (+ physique anchor) |
| Create a new character and her reference pack | `character_creation` | none for the first casting image |
| Fix a detail of an already generated image | `surgical_edit` | the image being fixed (`edit_target`) |
| Put a specific product, prop or garment into a scene | `insertion` | the product/prop/wardrobe reference (+ `edit_target` when inserting into an existing image) |
| Still that a video model will animate | `video_first_frame` | as the underlying workflow requires |
| Real screenshot, receipt, CTA image | **no generation** | none: use the real asset, unedited |

Multi-person scenes, slideshow continuity, before/after pairs, no-person scenes and exact text are
handled inside these modes (sections 4.5–4.9).

## 4. Workflows

### W1 — Style clone, new substance (`style_clone_new_scene`)

1. Run `skills/style-clone.md` on the liked image: fetch to `raw/`, digest with a vision model, save `content/styles/<slug>.json`.
2. Brainstorm a **genuinely new** scene in the same place type and concept: a different spot, outfit, objects and moment. Not a re-shoot.
3. Write the full prompt JSON. Copy the digest's palette, lighting, camera, composition habits and imperfection catalogue into the matching fields, and rewrite them for the new scene.
4. Manifest: one `style_digest` entry with `sent_to_generator: false`, the source URL, and `must_not_transfer` naming the source person, outfit, exact layout and case pattern.
5. `check`, `wrap`, approval, one generation, separate review.

Example: `examples/10-style-clone-new-scene.json`.

### W2 — Established character, new image (`character_new_image`)

1. Load the character's canonical sheet (`organic-character/1`, see `examples/character-sheet-example.json`). Production sheets live in `content/characters/<id>.json`; their reference images live outside the repo.
2. Brainstorm the new scene. If it is based on an organic photo's style, style-clone it first (W1 steps 1–2); the organic photo itself is **not** attached in W2.
3. Copy `identity` and `physique` from the sheet word for word into the JSON, and set `identity.character_sheet`. Describe the whole image fully.
4. Attach the approved `character_reference` images. For body-visible shots, also attach the `physique_anchor` / `body_benchmark` and state the body in words. An attached organic photo's body would outweigh the words, which is why it is never attached here.
5. Phone case from `signature_props`, only when her phone is visible.

Example: `examples/12-character-new-image.json`.

### W3 — Character replaces the person in an organic photo (`character_replaces_person`)

Never write a lazy "replace this person with her" prompt.

1. Style-clone the organic photo first (W1 step 1) and keep the digest.
2. Analyse the original scene and write the complete JSON of the final image **as if the organic photo were absent**: place, equipment and positions, camera, light, colour, imperfections, pose, and the character's own identity, physique, outfit and phone case.
3. Fill `intent.person_replacement`: who is replaced (`source_person`), by whom (`replace_with`), what is kept from the source (pose, position, distance, light on the body) and what never is (face, body shape, skin, hair, tattoos, jewellery, outfit, phone case).
4. Manifest: the organic photo as `organic_scene_source` (sent; `must_not_transfer` names at least the face and the body ✓), the `style_digest` (not sent), the `character_reference` images and the `physique_anchor` (sent).
5. `priority` puts `prompt_json` first, then the character references, then the scene source.
6. The `wrap` instruction tells the model to replace the person and forbids any carry-over of the original person's identity or body markers.

This supersedes the older "never attach the organic reference for body shots" rule (captain, 2026-09-20) for this workflow only, because the manifest boundary now fences the body. For body-visible W3 shots, still attach the physique anchor and body benchmark and state the body in words. If the reviewer finds the source body leaking in, redo the slide as W2 with the organic photo digested as text only. For W2 that rule applies unchanged.

Example: `examples/13-character-replaces-person.json`.

### W4 — No style or organic reference (`first_principles`)

Build the realism from first principles, because generic prompts drift toward polished AI images.
Fill every section with concrete, mundane specifics:

- **Real brands where natural**: a drugstore sunscreen, a supermarket bag, a treadmill maker's logo.
- **Clutter**: charger cables, hair ties, a mug in the sink.
- **An imperfect camera**: a named older iPhone, lens, distance, a tilt, a cropped limb.
- **Mixed light** and a white-balance cast.
- **Phone processing**: HDR, sharpening, noise reduction, compression.
- **At least three imperfections**, plus the physics and anatomy constraints.

Examples: `examples/01`–`07`, `examples/20-no-person-object-scene.json`.

### 4.5 Create a character and her reference pack (`character_creation`)

1. Write the identity and physique in full in a casting prompt (`examples/14-character-creation.json`): a clear front-camera daylight selfie that is still an organic phone photo.
2. Generate one image at a time and review it. The captain approves the casting.
3. Build the pack from the approved casting with W2 prompts: a three-quarter face, a full-body mirror selfie (physique anchor), and one different lighting condition. Each is approved before joining the pack.
4. Write `content/characters/<id>.json` (`organic-character/1`) and run `image-prompt.py check` on it. Images are stored outside the repo.

### 4.6 Surgical edit of a generated image (`surgical_edit`)

Use this to fix one reviewer finding, such as a wrong readout, an extra headphone set or a garbled label,
without regenerating. Attach exactly one `edit_target`. `change_only` lists each change precisely,
and `must_stay_true` lists what must not move. The JSON still describes the full final image. If a
region must stay pixel-identical, composite it back in afterwards (OpenAI guidance). Example:
`examples/15-surgical-edit.json`.

### 4.7 Product, prop or wardrobe insertion (`insertion`)

Attach the product, prop or wardrobe reference, with `may_copy` limited to the object's shape, colour
and exact branding, and `must_not_transfer` covering its studio background and lighting. Describe
scale, placement, contact shadow and perspective. Insert into an existing image with an
`edit_target`, or into a new image without one. Example: `examples/16-product-insertion.json`.

### 4.8 Multi-person scenes

`subject.count` = 1 + `len(other_people)` ✓. `identity` holds person A. Each extra person is an
`other_people` entry with their own description and sheet. Every character reference's
`must_not_transfer` forbids transfer onto the other person, and `exclusions` forbid swapped
features and duplicated faces. Nano Banana 2 holds at most 4 characters per request (official limit).
Example: `examples/18-multi-character.json`.

### 4.9 Slideshow continuity and before/after

Fill `continuity`: series, position, `state` (`current`/`before`/`after`), `carry_over` (face, hair
colour, marks, phone and case) and `allowed_changes`. A **before** picture is told by setting,
outfit, posture and light, never by a worse body, unless the captain marks that slide exempt.
Previous frames go in the manifest as `previous_frame` (usually not sent; the reviewer uses them).
Example: `examples/19-continuity-before.json`.

### 4.10 Video first frame (`video_first_frame`)

Fill `video_handoff`: the target model, the planned motion, and first-frame rules. Use a neutral start
(mouth closed), a readable face for lip sync, no motion blur the video model must invent through,
space for movement, and no text to keep stable. Then use `skills/fal-video.md` for the video step and
keep the video prompt simple and continuous (one take, no zoom, no cuts). Example:
`examples/17-video-first-frame.json`.

### 4.11 Exact typography and overlays

- **Slide captions are added in the editor, not generated.** Keep `typography.overlay_text: null` by default. Generated text is the least reliable part of both vendors' output.
- Set `overlay_text` only when the captain explicitly wants burned-in text. Quote the exact words, describe the font look, size, colour, position and effect, and check the spelling in the output.
- `scene_text` states every piece of readable text in the scene, in quotes, or says that none is legible. Text in mirrors reads mirrored.

### 4.12 Real screenshots, receipts and CTA assets: no generation

The steps receipt, screen-time receipt and the CTA blocker screen
(`data/cta-shield/shield-1080x2340.png`) are used real and unedited: no generation, no edit and no
crop beyond the layout. Never regenerate an app UI or a statistic.

### 4.13 Multi-reference conflicts

`references.priority` orders `prompt_json` and every `reference_id` ✓. The default order is:
the prompt JSON, then identity references (character ref, then physique anchor or benchmark),
then product references, then the edit target or scene source, then style. Each entry's
`must_not_transfer` resolves overlaps; for example, a scene source never supplies the body, and a
product reference never supplies the lighting. When two references show the same thing, keep only the
better one: every attached image costs attention.

## 5. The schema, field by field

Write every value as a descriptive sentence, not a tag list. Google's guidance is to describe the
scene, not list keywords, and OpenAI explicitly accepts JSON-like structure. The schema gives the
structure; the sentences give the description.

| Field | Content |
|---|---|
| `mode`, `intent` | Workflow; purpose; `scene_concept`; locked `place_type`; `must_stay_true`; `change_only` (edits); `person_replacement` (W3 only). |
| `polish_level`, `aspect_ratio` | See section 6; the ratio is repeated in the API call. |
| `subject` | Count, description, action, pose, gaze, expression, face visibility. |
| `identity`, `other_people` | Fictional adult identity: age, presentation, skin, hair, face, marks, `character_sheet`. |
| `physique` | Build, proportions and detail, stated in plain words. |
| `wardrobe` | Items and their fit/condition (creases, pilling, sweat). |
| `environment` | Setting, foreground/background lists, clutter, time of day. |
| `camera` | Device (a named phone), `capture` type, lens, `focal_length_equiv_mm`, position, distance, orientation, focus, depth of field. |
| `composition` | Framing, placement, crop, tilt, headroom. |
| `lighting`, `color` | Sources, direction, quality, exposure; white balance, palette, saturation, contrast, casts. |
| `processing` | Phone pipeline, HDR, sharpening, noise reduction, compression; `beauty_filter` and `grading` are normally "none". |
| `imperfections`, `texture`, `motion` | At least three imperfections; skin/hair/fabric/surfaces; subject/camera/blur. |
| `geometry` | Anatomy counts, physics, reflection logic, perspective. |
| `phone` | Whether it is visible, its case, how it is held, the screen. |
| `typography` | `overlay_text` (normally null) and `scene_text`. |
| `brands_and_props` | Branding policy (keep natural), brands and props. |
| `exclusions` | Targeted failure modes only (section 7), always as "no …". |
| `references` | The manifest and priority (section 8). |
| `continuity`, `video_handoff` | Series state; first-frame handoff. |

Copy `examples/01-night-bedroom-selfie.json` (text only) or the example for your workflow, then rewrite every value.

## 6. Organic realism

**Polish level** (carried over from the retired `organic-iphone-photo.md` template):

| level | lighting | framing | imperfection dose |
|---|---|---|---|
| `polished` | soft window light or golden hour | deliberate, comfortable crops | token: a touch of noise, skin texture kept |
| `plandid` | bright even ambient (gym LED, open shade) | straight-on snapshot, level or slightly tilted | honest: HDR sheen, slight clipping, a stray object |
| `raw` | harsh direct sun or bare artificial light | off-centre, tilted, cropped limbs | heavy: hard shadows, blown highlights, mixed white balance |
| `jagged` | worst-case fluorescent mix, patchy pools | cramped, cluttered, mirror edges intruding | maximal: noise, glare, smudges, colour casts, no styling |

`plandid` is the slideshow default. `polished` needs a reason, because it is closest to the AI look.

**Phone optics.** Name an ordinary (preferably older) iPhone, and use the lens that capture would
really use: the front camera at about 23 mm, the rear main at about 26 mm, or the ultra-wide at about
13 mm. Depth of field is deep. Portrait-mode blur appears only when asked for. There is no anamorphic flare,
halation, film grain or vignette. Camera specs are appearance cues, not physics simulation (OpenAI
guidance).

**Processing.** Use stock camera-app processing: Smart HDR, crunchy sharpening, noise reduction that
smears shadows, social-media compression, no beauty filter and no grade.

**Imperfection menu.** Pick at least three per image: luminance/chroma noise, clipped highlights,
mixed white balance, lens smudge haze, mirror fingerprints, tilt, cropped limb or head, motion
softness, flyaways, sweat, pores/freckles/blemishes, creased or pilled fabric, and background people
mid-motion.

## 7. Failure modes and their JSON fixes

| Symptom | Usual cause | Fix in the JSON |
|---|---|---|
| Glossy, poreless, beauty-filtered skin | mood words ("glam", "luxury"), high quality | `texture.skin` lists pores, marks and shine; `processing.beauty_filter: "none"`; exclusion "no airbrushed skin"; quality low |
| Cinematic / editorial look | lens and lighting words from film; "4K", "ultra" | name a phone and a capture type; `grading: "none"`; ordinary light sources |
| Creamy bokeh | the model's default portrait look | `depth_of_field: "deep …"`; exclusion "no portrait-mode blur" |
| Perfect centred framing | no composition constraints | `composition.tilt`, `crop` and off-centre placement |
| Staged, empty rooms | no clutter | `environment.clutter` and named mundane objects |
| Warped hands, extra limbs, two headphone sets | unconstrained anatomy | `geometry.anatomy` counts; one of each prop; exclusion "no second pair of headphones" |
| Impossible mirror / reflections | no reflection logic | `geometry.reflections`: phone hand, reversed text, case facing the mirror |
| Bent tiles, doors and equipment | wide-angle drift | `geometry.perspective` and `physics`: straight lines, correct machine geometry |
| Garbled or invented words | text left undefined | `scene_text` states all readable text in quotes; exclusion "no invented or garbled text" |
| Brands scrubbed, generic-looking props | old blanket "no logos" rule | `brands_and_props` names the natural brands; no blanket exclusion |
| Case pattern painted on screens, phone forced into every scene | case treated as part of the character | `phone.visible` false unless her phone is really in frame |
| Watch appears | reference or default styling | exclusion "no Apple Watch or any smartwatch"; never attach a reference that shows one |
| Wrong place type (gym turns into a home gym) | loose concept | `intent.place_type` and `must_stay_true` |
| Source person's identity or body leaks | lazy replacement or attaching the organic photo in W2 | W3 manifest `must_not_transfer`; W2 never attaches it |
| Body drifts softer or wiry | text-only physique | attach the physique anchor or benchmark and state the body in words |

Keep `exclusions` short and targeted. Google recommends describing what you want rather than listing
negatives, so fix most problems with a positive field and keep "no …" for the known failure modes
above.

## 8. Reference-role manifest

Every reference the prompt relies on, whether attached or text only, gets one `references.manifest` entry:

```json
{
  "reference_id": "O1",
  "role": "organic_scene_source",
  "source": "raw/refs/<file>.jpg",
  "sent_to_generator": true,
  "may_copy": ["room and equipment positions", "camera position and tilt", "lighting"],
  "must_preserve": ["place type and layout"],
  "must_not_transfer": ["the original person's face and identity", "her body shape", "her tattoos, jewellery, outfit and phone case"]
}
```

Roles: `style_digest`, `organic_scene_source`, `character_reference`, `physique_anchor`,
`body_benchmark`, `product_reference`, `wardrobe_reference`, `prop_reference`,
`phone_case_reference`, `edit_target`, `previous_frame`. `wrap` lists attached images in manifest
order as `attached_images` (`image 1 = O1 (organic_scene_source)`, following OpenAI's guidance to
assign every reference a number and a purpose), and the instruction tells the model to honour each
entry's lists and the `priority`.

## 9. Serialising and wrapping for each vendor

Universal (all vendors, and part of the JSON): subject, composition, light, texture, exact text,
changes versus constraints, reference roles, and exclusions. Vendor fields (API parameters, **never**
inside the prompt): model, quality, size / image_size, aspect_ratio, n, output format, moderation,
thinking level. `wrap` produces both.

- **OpenAI GPT Image** (`--target openai`): Image API `POST /v1/images/generations`, or `/v1/images/edits` when images are attached. Body: `model` (default `gpt-image-2`, the captain-approved model; `--model gpt-image-2.5-flare` or `gpt-image-2.5-sunburst` when asked), `prompt` = the JSON document, `size` = the smallest valid exact-ratio size, `quality: "low"`, `n: 1`. Use the Image API, not the Responses tool: in Responses the mainline model rewrites the prompt (`revised_prompt`), which would discard the JSON contract.
- **Nano Banana** (`--target gemini`): Interactions API `POST https://generativelanguage.googleapis.com/v1beta/interactions`, `model: "gemini-3.1-flash-image"` (regular Nano Banana 2; never the legacy 2.5, Lite or Pro unless the captain names it), `input: [{type: "text", text: <JSON>}, {type: "image", …}…]`, `response_format: {type: "image", aspect_ratio, image_size: "512"}`; thinking stays at the default `minimal`. Official examples only show `"1K"` literally; confirm `"512"` in the API reference on first use.
- **codex-image bridge** (`--target codex`): prints the JSON prompt for `codex-image`/`codex_image`. The bridge has no quality or size control, so it is not the default for generation (rule 12).

## 10. Checklists

**Before writing**
- [ ] Workflow chosen (section 3); real assets identified and excluded from generation.
- [ ] Style digest exists (W1, W3), and the character sheet and approved refs are at hand (W2, W3, 4.8).
- [ ] No reference shows an Apple Watch; reference images are in `raw/` or outside the repo.

**Before submitting**
- [ ] Every field is filled with concrete, mundane, physically possible specifics; place type locked.
- [ ] Identity and physique copied word for word from the sheet (character workflows).
- [ ] Manifest complete, with `must_not_transfer` on every scene or style source.
- [ ] `python3 scripts/image-prompt.py check <file>` passes; `wrap` output inspected.
- [ ] Approval obtained and the per-image cost stated. One image, lowest setting.

**After generation**
- [ ] Separate reviewer runs `research/slideshows/reviewer-checks.md` with the reference and the prompt JSON beside the image.
- [ ] A FAIL becomes a `surgical_edit` JSON or a corrected prompt; never a prose patch.
- [ ] Prompt JSON saved next to the output (outside the repo), with its usage and cost.

## 11. Examples

| File | Workflow / scene class |
|---|---|
| `01-night-bedroom-selfie.json` | W4, warm night bedroom front-camera selfie |
| `02-beach-towel-candid.json` | W4, prone beach-towel selfie in hard sun |
| `03-living-room-beauty-selfie.json` | W4, window-lit living-room beauty selfie |
| `04-gym-stretch.json` | W4, friend-shot seated stretch in a commercial gym |
| `05-reclined-outdoor-fitness-selfie.json` | W4, reclined top-down selfie on turf |
| `06-close-leaning-portrait.json` | W4, close leaning kitchen selfie |
| `07-high-angle-bathroom-selfie.json` | W4, high-angle bathroom selfie |
| `10-style-clone-new-scene.json` | W1 from `content/styles/gym-mirror-selfie-budget-night.json` |
| `character-sheet-example.json` | Canonical character sheet (`organic-character/1`) |
| `12-character-new-image.json` | W2 with character refs and physique anchor |
| `13-character-replaces-person.json` | W3 person replacement |
| `14-character-creation.json` | Casting image for a new character |
| `15-surgical-edit.json` | Fixing a readout and removing a stray phone |
| `16-product-insertion.json` | Inserting a product into an existing image |
| `17-video-first-frame.json` | First frame for a talking walk clip |
| `18-multi-character.json` | Two characters, one phone |
| `19-continuity-before.json` | Series continuity, "before" state |
| `20-no-person-object-scene.json` | No-person scene with exact scene text |

Example reference paths (`~/excerlock-private/...`, `raw/...`) are illustrative. The example character is not an approved production character.
