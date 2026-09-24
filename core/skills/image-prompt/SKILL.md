---
name: image-prompt
description: Write, validate and wrap the JSON prompt for every generated or edited image, so the result reads as an ordinary organic phone photo. Use whenever an image, an image edit or a video first frame is about to be generated.
---
# Organic JSON image prompting

Every image this project generates or edits starts from one JSON document that follows
`core/skills/image-prompt/schema.json` (`organic-image-prompt/1`). The goal above everything else:
the result must look like an ordinary, organic phone photo, not an AI image.

## Inputs

- The section's rules (for example `sections/<section>/rules.md`) and its image rules file, if it has one (`sections/<section>/image-rules.json`).
- The account's character from `accounts/<name>/account.md` (`## Character`), with its reference images in `accounts/<name>/assets/`. Read it before writing any prompt with a person in it.
- Any organic reference or style digest (`library/styles/<slug>.json`), product or edit target the workflow needs.

## Files

| Path | What it is |
|---|---|
| `core/skills/image-prompt/schema.json` | The strict schema. Every key is required; use `null`, `false`, `0` or `[]` when a field does not apply. |
| `core/skills/image-prompt/check.py` | `check FILE... [--rules sections/<section>/image-rules.json]` validates the schema, the universal contract and the section's image rules. `wrap FILE --target openai\|gemini\|codex` prints the exact request without sending it. No network, no generation. |
| `core/skills/image-prompt/examples/` | One valid example per workflow and per scene class (index at the end). |
| `core/skills/style-clone/SKILL.md` | Step 1 of style work: digest an inspiration image into non-identifying style JSON in `library/styles/`. |
| `core/skills/review-images/SKILL.md` | The separate reviewer every generated image goes through. |
| `core/skills/image-prompt/sources.md` | The vendor docs and X research behind this skill, with coverage limits. |

## 1. What always holds

1. **The prompt sent to the model is JSON.** `wrap` sends one JSON document: `{instruction, attached_images, image}`. The only prose is the one-sentence `instruction` inside it.
2. **Organic realism beats everything else**: ordinary phone optics and processing, imperfect framing, mixed light, noise, compression, real skin texture, flyaways, clutter, plausible anatomy and geometry.
3. **Organic means the photo, never a plainer person.** Organic is camera behaviour, lighting, environment, texture, framing, processing, compression, clutter and imperfections. Every person is cast exceptionally attractive or aspirational, as attractive as or more attractive than the organic inspiration, and still looks organic. Attractiveness (`appeal`) and photographic rawness (`polish_level`) are independent axes: a `jagged` photo of a stunning woman is correct. `check` enforces this.
4. **Style, never identity.** A reference photo gives the look (camera, light, place, framing), never the person. The person comes from the account's `## Character` section.
5. **Adults only, fictional only.** Every person is a stated adult and `identity.fictional` is always `true`. `check` enforces the age.
6. **Apply the section's rules and the account's character.** Run `check` with the section's `--rules` file, and copy the account's character into the JSON (W2 step 3).
7. **Keep the place type and the scene concept.** State them in `intent.place_type` and `intent.must_stay_true`.
8. **Physically logical scenes**: loaded bars are loaded equally, one pair of headphones, cables run to pulleys, reflections obey the mirror.
9. **Every reference gets a manifest entry** (section 8), attached or not. `check` enforces it.
10. **A separate reviewer judges every image** with its reference and prompt JSON beside it: `core/skills/review-images/SKILL.md`.

## 2. The pipeline

```
organic/inspiration photo ──► vision model (style-clone) ──► library/styles/<slug>.json (non-identifying)
                                                                   │  text only
account character + approved refs ───────────────────────────┐     ▼
                                                              ├─► prompt JSON (this schema) ──► check.py check --rules
product / wardrobe / edit target / organic scene source ─────┘         │
          (attached only when the workflow says so, each with a        ▼
           manifest entry)                                     check.py wrap ──► ONE generation (see Generating)
                                                                                                   │
                                                         separate reviewer (review-images) ◄───────┘
```

The style digest is text inside the JSON; it is never attached. When an image is attached, the JSON
still describes the whole intended image, as if no image were attached. References reinforce the
description; they never replace it.

## 3. Pick the workflow (`mode`)

| Situation | `mode` | Images attached to the generator |
|---|---|---|
| No style or organic reference | `first_principles` (W4) | none |
| Copy a liked photo's style into a new scene | `style_clone_new_scene` (W1) | none (digest as text) |
| The account's character, new image | `character_new_image` (W2) | approved character refs (+ physique anchor or body benchmark for body shots) |
| Put the account's character in place of the person in an organic photo | `character_replaces_person` (W3) | the organic photo + character refs (+ physique anchor) |
| Create a new character and her reference pack | `character_creation` | none for the first casting image |
| Fix a detail of an already generated image | `surgical_edit` | the image being fixed (`edit_target`) |
| Put a specific product, prop or garment into a scene | `insertion` | the product, prop or wardrobe reference (+ `edit_target` when inserting into an existing image) |
| Still that a video model will animate | `video_first_frame` | as the underlying workflow requires |

Multi-person scenes, series continuity, before/after pairs, no-person scenes and exact text are
handled inside these modes (sections 4.5 to 4.12).

## 4. Workflows

### W1: style clone, new substance (`style_clone_new_scene`)

1. Run `core/skills/style-clone/SKILL.md` on the liked image: fetch to `raw/`, digest with a vision model, save `library/styles/<slug>.json`.
2. Brainstorm a genuinely new scene in the same place type and concept: a different spot, outfit, objects and moment.
3. Write the full prompt JSON. Copy the digest's palette, lighting, camera, composition habits and imperfection catalogue into the matching fields, rewritten for the new scene.
4. Manifest: one `style_digest` entry with `sent_to_generator: false`, the source URL, and `must_not_transfer` naming the source person, outfit, exact layout and case pattern.
5. `check`, `wrap`, one generation, separate review.

Example: `examples/10-style-clone-new-scene.json`.

### W2: the account's character, new image (`character_new_image`)

1. Read the account's `## Character` section in `accounts/<name>/account.md`. Its reference images live in `accounts/<name>/assets/`.
2. Brainstorm the new scene. If it is based on an organic photo's style, style-clone it first (W1 steps 1 and 2). The organic photo itself is not attached in W2.
3. Copy the character's identity, appeal and physique word for word into `identity`, `appeal` and `physique`, and set `identity.character_sheet` to the account file. Describe the whole image fully.
4. Attach the approved `character_reference` images. For body-visible shots, also attach the account's `physique_anchor` or `body_benchmark` and state the body in words.
5. Add the character's own props (such as a phone case) only when they are really in frame.

Example: `examples/12-character-new-image.json`.

### W3: character replaces the person in an organic photo (`character_replaces_person`)

1. Style-clone the organic photo first (W1 step 1) and keep the digest.
2. Analyse the original scene and write the complete JSON of the final image as if the organic photo were absent: place, equipment and positions, camera, light, colour, imperfections, pose, and the character's own identity, physique, outfit and props.
3. Fill `intent.person_replacement`: who is replaced (`source_person`), by whom (`replace_with`), what is kept from the source (pose, position, distance, light on the body) and what never is (face, body shape, skin, hair, tattoos, jewellery, outfit, phone case).
4. Manifest: the organic photo as `organic_scene_source` (sent; `must_not_transfer` names at least the face and the body, which `check` enforces), the `style_digest` (not sent), the `character_reference` images and the `physique_anchor` (sent).
5. `priority` puts `prompt_json` first, then the character references, then the scene source.
6. The `wrap` instruction tells the model to replace the person and forbids any carry-over of the original person's identity or body.

W3 is the only workflow that attaches an organic photo for a body shot; the manifest fences the body.
For body-visible W3 shots, still attach the physique anchor or body benchmark and state the body in
words. If the reviewer finds the source body leaking in, redo the image as W2 with the organic photo
digested as text only.

Example: `examples/13-character-replaces-person.json`.

### W4: no style or organic reference (`first_principles`)

Build the realism from first principles. Fill every section with concrete, mundane specifics:

- **Real brands where natural**: a drugstore sunscreen, a supermarket bag, a treadmill maker's logo.
- **Clutter**: charger cables, hair ties, a mug in the sink.
- **An imperfect camera**: a named older iPhone, lens, distance, a tilt, a cropped limb.
- **Mixed light** and a white-balance cast.
- **Phone processing**: HDR, sharpening, noise reduction, compression.
- **At least three imperfections**, plus the physics and anatomy constraints.

Examples: `examples/01` to `07`, `examples/20-no-person-object-scene.json`.

### 4.5 Create a character and her reference pack (`character_creation`)

1. Write the identity, appeal and physique in full in a casting prompt (`examples/14-character-creation.json`): a clear front-camera daylight selfie that is still an organic phone photo. Cast her exceptionally attractive; the casting image sets the ceiling every later image must match.
2. Generate one image at a time and review it. The captain approves the casting.
3. Build the pack from the approved casting with W2 prompts: a three-quarter face, a full-body mirror selfie (physique anchor), and one different lighting condition. Each is approved before joining the pack.
4. Write the character into the account's `account.md` (`## Character`) and store the images in `accounts/<name>/assets/`. An account may also keep a structured sheet (`organic-character/1`, see `examples/character-sheet-example.json`); `check` validates it.

### 4.6 Surgical edit of a generated image (`surgical_edit`)

Use this to fix one reviewer finding, such as a wrong readout, an extra headphone set or a garbled
label, without regenerating. Attach exactly one `edit_target`. `change_only` lists each change
precisely, and `must_stay_true` lists what must not move. The JSON still describes the full final
image. If a region must stay pixel-identical, composite it back in afterwards (OpenAI guidance).
Example: `examples/15-surgical-edit.json`.

### 4.7 Product, prop or wardrobe insertion (`insertion`)

Attach the product, prop or wardrobe reference, with `may_copy` limited to the object's shape, colour
and exact branding, and `must_not_transfer` covering its studio background and lighting. Describe
scale, placement, contact shadow and perspective. Insert into an existing image with an
`edit_target`, or into a new image without one. Example: `examples/16-product-insertion.json`.

### 4.8 Multi-person scenes

`subject.count` = 1 + `len(other_people)` (`check` enforces it). `identity` holds person A. Each
extra person is an `other_people` entry with their own description and account file. Every character
reference's `must_not_transfer` forbids transfer onto the other person, and `exclusions` forbid
swapped features and duplicated faces. Nano Banana 2 holds at most 4 characters per request (official
limit). Example: `examples/18-multi-character.json`.

### 4.9 Series continuity and before/after

Fill `continuity`: series, position, `state` (`current`/`before`/`after`), `carry_over` (face, hair
colour, marks, phone and case) and `allowed_changes`. A before picture is told by setting, outfit,
posture and light, with the same body as every other picture. Previous frames go in the manifest as
`previous_frame` (usually not sent; the reviewer uses them). Example: `examples/19-continuity-before.json`.

### 4.10 Video first frame (`video_first_frame`)

Fill `video_handoff`: the target model, the planned motion, and first-frame rules. Use a neutral start
(mouth closed), a readable face for lip sync, no motion blur the video model must invent through,
space for movement, and no text to keep stable. Then use `core/skills/fal-video/SKILL.md` for the
video step and keep the video prompt simple and continuous (one take, no zoom, no cuts). Example:
`examples/17-video-first-frame.json`.

### 4.11 Exact typography and overlays

- Keep `typography.overlay_text: null` by default; captions are added in the editor.
- Set `overlay_text` only when burned-in text is explicitly wanted. Quote the exact words, describe the font look, size, colour, position and effect, and check the spelling in the output.
- `scene_text` states every piece of readable text in the scene, in quotes, or says that none is legible. Text in mirrors reads mirrored.

### 4.12 Multi-reference conflicts

`references.priority` orders `prompt_json` and every `reference_id` (`check` enforces it). The
default order is: the prompt JSON, then identity references (character ref, then physique anchor or
benchmark), then product references, then the edit target or scene source, then style. Each entry's
`must_not_transfer` resolves overlaps; for example, a scene source never supplies the body, and a
product reference never supplies the lighting. When two references show the same thing, keep only the
better one: every attached image costs attention.

## 5. The schema, field by field

Write every value as a descriptive sentence, not a tag list. Google's guidance is to describe the
scene, not list keywords, and OpenAI explicitly accepts JSON-like structure.

| Field | Content |
|---|---|
| `mode`, `intent` | Workflow; purpose; `scene_concept`; locked `place_type`; `must_stay_true`; `change_only` (edits); `person_replacement` (W3 only). |
| `polish_level`, `aspect_ratio` | See section 6; the ratio is repeated in the API call. |
| `appeal` | The casting axis, independent of `polish_level`: `level` (`exceptional` or `aspirational`; there is no plain level), `relative_to_inspiration` (at least as attractive as the inspiration or benchmark), positive `face` and `physique`, and `independent_of_polish: true`. `null` only when no person is in frame. Character workflows copy it from the account's character. |
| `subject` | Count, description, action, pose, gaze, expression, face visibility. |
| `identity`, `other_people` | Fictional adult identity: age, presentation, skin, hair, face, marks, `character_sheet` (the account file). |
| `physique` | Build, proportions and detail, stated in plain words. |
| `wardrobe` | Items and their fit and condition (creases, pilling, sweat). |
| `environment` | Setting, foreground and background lists, clutter, time of day. |
| `camera` | Device (a named phone), `capture` type, lens, `focal_length_equiv_mm`, position, distance, orientation, focus, depth of field. |
| `composition` | Framing, placement, crop, tilt, headroom. |
| `lighting`, `color` | Sources, direction, quality, exposure; white balance, palette, saturation, contrast, casts. |
| `processing` | Phone pipeline, HDR, sharpening, noise reduction, compression; `beauty_filter` and `grading` are normally "none". |
| `imperfections`, `texture`, `motion` | At least three imperfections; skin, hair, fabric, surfaces; subject, camera, blur. |
| `geometry` | Anatomy counts, physics, reflection logic, perspective. |
| `phone` | Whether it is visible, its case, how it is held, the screen. |
| `typography` | `overlay_text` (normally null) and `scene_text`. |
| `brands_and_props` | Branding policy, brands and props. |
| `exclusions` | Targeted failure modes only (section 7), always as "no ...". |
| `references` | The manifest and priority (section 8). |
| `continuity`, `video_handoff` | Series state; first-frame handoff. |

Copy `examples/01-night-bedroom-selfie.json` (text only) or the example for your workflow, then rewrite every value.

## 6. Organic realism

**Polish level:**

| level | lighting | framing | imperfection dose |
|---|---|---|---|
| `polished` | soft window light or golden hour | deliberate, comfortable crops | token: a touch of noise, skin texture kept |
| `plandid` | bright even ambient (gym LED, open shade) | straight-on snapshot, level or slightly tilted | honest: HDR sheen, slight clipping, a stray object |
| `raw` | harsh direct sun or bare artificial light | off-centre, tilted, cropped limbs | heavy: hard shadows, blown highlights, mixed white balance |
| `jagged` | worst-case fluorescent mix, patchy pools | cramped, cluttered, mirror edges intruding | maximal: noise, glare, smudges, colour casts, no styling |

`plandid` is the default. `polished` needs a reason, because it is closest to the AI look.

**Phone optics.** Name an ordinary (preferably older) iPhone, and use the lens that capture would
really use: the front camera at about 23 mm, the rear main at about 26 mm, or the ultra-wide at about
13 mm. Depth of field is deep. Camera specs are appearance cues, not physics simulation (OpenAI
guidance).

**Processing.** Use stock camera-app processing: Smart HDR, crunchy sharpening, noise reduction that
smears shadows, social-media compression, `beauty_filter: "none"` and `grading: "none"`.

**Imperfection menu.** Pick at least three per image: luminance or chroma noise, clipped highlights,
mixed white balance, lens smudge haze, mirror fingerprints, tilt, cropped limb or head, motion
softness, flyaways, sweat, fine pores, freckles or a small mole, creased or pilled fabric, and
background people mid-motion.

**Imperfections go on the photo.** Skin texture means fine pores, a natural flush, freckles, sweat and
shine. Clutter, noise, tilt and mixed light make the image organic.

## 7. Failure modes and their JSON fixes

| Symptom | Usual cause | Fix in the JSON |
|---|---|---|
| Glossy, poreless, beauty-filtered skin | mood words ("glam", "luxury"), high quality | `texture.skin` lists pores, marks and shine; `processing.beauty_filter: "none"`; exclusion "no airbrushed skin"; quality low |
| Cinematic or editorial look | lens and lighting words from film; "4K", "ultra" | name a phone and a capture type; `grading: "none"`; ordinary light sources |
| Creamy bokeh | the model's default portrait look | `depth_of_field: "deep ..."`; exclusion "no portrait-mode blur" |
| Perfect centred framing | no composition constraints | `composition.tilt`, `crop` and off-centre placement |
| Staged, empty rooms | no clutter | `environment.clutter` and named mundane objects |
| Warped hands, extra limbs, two headphone sets | unconstrained anatomy | `geometry.anatomy` counts; one of each prop; exclusion "no second pair of headphones" |
| Impossible mirror or reflections | no reflection logic | `geometry.reflections`: phone hand, reversed text, case facing the mirror |
| Bent tiles, doors and equipment | wide-angle drift | `geometry.perspective` and `physics`: straight lines, correct machine geometry |
| Garbled or invented words | text left undefined | `scene_text` states all readable text in quotes; exclusion "no invented or garbled text" |
| Brands scrubbed, generic-looking props | a blanket "no logos" exclusion | `brands_and_props` names the natural brands |
| Case pattern painted on screens, phone forced into every scene | the case treated as part of the character | `phone.visible` false unless her phone is really in frame |
| Wrong place type (a gym turns into a home gym) | loose concept | `intent.place_type` and `must_stay_true` |
| Source person's identity or body leaks | lazy replacement, or the organic photo attached in W2 | W3 manifest `must_not_transfer`; W2 never attaches it |
| Body drifts from the character | text-only physique | attach the physique anchor or benchmark and state the body in words |
| Person comes out plainer, heavier, boxier or less attractive than the inspiration | "organic", "raw", "real", "normal" read as casting words; face or body described by flaws; appeal left implicit | fill `appeal` with positive face and physique wording at or above the inspiration; keep anti-polish words on the photo |

Keep `exclusions` short and targeted. Google recommends describing what you want rather than listing
negatives, so fix most problems with a positive field and keep "no ..." for the known failure modes
above and the ones the section's rules require.

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
give every reference a number and a purpose), and the instruction tells the model to honour each
entry's lists and the `priority`. Attached images live outside the repo or in a gitignored folder
(`raw/`, `accounts/<name>/assets/`, `sections/<section>/assets/`).

## 9. Serialising and wrapping for each vendor

Universal (all vendors, and part of the JSON): subject, composition, light, texture, exact text,
changes versus constraints, reference roles, and exclusions. Vendor fields (API parameters, never
inside the prompt): model, quality, size or image_size, aspect_ratio, n, output format, moderation,
thinking level. `wrap` produces both.

- **OpenAI GPT Image** (`--target openai`): Image API `POST /v1/images/generations`, or `/v1/images/edits` when images are attached. Body: `model` (default `gpt-image-2`; `--model gpt-image-2.5-flare` or `gpt-image-2.5-sunburst` only when asked), `prompt` = the JSON document, `size` = the smallest valid exact-ratio size (`720x1280` for 9:16), `quality: "low"`, `n: 1`.
- **Nano Banana** (`--target gemini`): Interactions API `POST https://generativelanguage.googleapis.com/v1beta/interactions`, `model: "gemini-3.1-flash-image"`, `input: [{type: "text", text: <JSON>}, {type: "image", ...}...]`, `response_format: {type: "image", aspect_ratio, image_size: "512"}`; thinking stays at the default `minimal`. Official examples only show `"1K"` literally; confirm `"512"` in the API reference on first use.
- **codex-image bridge** (`--target codex`): prints the JSON prompt for `codex-image`. The bridge has no quality or size control.

## 10. Checklists

**Before writing**
- [ ] Workflow chosen (section 3).
- [ ] Section rules and the account's `## Character` section read.
- [ ] Style digest exists (W1, W3); the account's approved refs are at hand (W2, W3, 4.8).
- [ ] No reference shows anything the section's rules forbid; reference images are in a gitignored folder or outside the repo.

**Before submitting**
- [ ] Every field is filled with concrete, mundane, physically possible specifics; place type locked.
- [ ] `appeal` casts every person exceptional or aspirational, at least as attractive as the inspiration.
- [ ] Identity, appeal and physique copied word for word from the account's character (character workflows).
- [ ] Manifest complete, with `must_not_transfer` on every scene or style source.
- [ ] `python3 core/skills/image-prompt/check.py check FILE --rules sections/<section>/image-rules.json` passes; `wrap` output inspected.

**After generation**
- [ ] A separate reviewer runs `core/skills/review-images/SKILL.md` with the reference and the prompt JSON beside the image.
- [ ] A FAIL becomes a `surgical_edit` JSON or a corrected prompt.
- [ ] Prompt JSON saved next to the output (outside the repo), with its usage and cost.

## Don'ts

- Don't send a prose prompt, prose inside a JSON field, or a one-line "just change X" edit. Why: prose loses the field-by-field contract that `check` validates and the reviewer compares against.
- Don't fix a reviewer FAIL with a prose patch. Why: the fix must be a `surgical_edit` JSON or a corrected prompt so it stays checkable.
- Don't use "organic", "raw", "real", "normal", "plain" or "average" to describe a person's face or body. Why: models read them as casting words and return a plainer, heavier or less attractive person; organic is the photo's treatment only.
- Don't describe a face or body by its flaws (acne, puffiness, a worse body). Why: imperfections belong on the photo, and flaw wording lowers the appeal.
- Don't make a person more attractive with retouching, beauty filters, grading or studio light. Why: that is the AI look; appeal comes from casting, not from polish.
- Don't tell a before picture with a worse body. Why: the story works with the same body, and a worse body breaks the character.
- Don't write a lazy "replace this person with her" prompt. Why: the model keeps the source person's identity and body unless the JSON describes the whole final image and the manifest fences them off.
- Don't attach the organic photo in W2. Why: an attached body outweighs any words in the prompt.
- Don't attach a style digest or an inspiration image in W1. Why: the generator copies the person and layout; only the non-identifying digest text should reach it.
- Don't reproduce a real person's face, body, tattoos or identifying marks. Why: a reference gives style, never identity.
- Don't commit reference images to the repository. Why: they show real people and belong in `raw/`, `accounts/<name>/assets/` or outside the repo.
- Don't write "4K", "ultra", "cinematic", "glam" or "luxury", film lens names, portrait-mode blur, film grain, halation or vignettes. Why: they push the output toward a polished AI or editorial image.
- Don't rebuild a whole reference "as closely as possible". Why: the goal is a new scene in the same style, not a copy of someone's photo.
- Don't add a phone where the scene has none, or treat the phone case as part of the character. Why: a forced phone repeats across images and its case pattern gets painted onto screens and bezels.
- Don't pile on `exclusions`. Why: vendors recommend describing the wanted state positively; long negative lists get ignored or backfire.
- Don't burn slide or caption text into the image by default. Why: generated text is the least reliable part of both vendors' output.
- Don't use the OpenAI Responses image tool. Why: its mainline model rewrites the prompt (`revised_prompt`) and discards the JSON contract; the Image API sends it unchanged.
- Don't attach two references that show the same thing. Why: every attached image costs attention, and duplicates fight each other.

## Generating

- Generate at the lowest quality, one image at a time. Why: low quality reads as a real phone photo; high quality reads as professional or AI and was rejected.
- Nano Banana means regular Nano Banana 2, `gemini-3.1-flash-image`, at `image_size: "512"` (0.5K). Why: it is the standing model and lowest setting; never the legacy 2.5, Lite or Pro unless the captain names it.
- OpenAI means `gpt-image-2`, `quality: "low"`, `n: 1`, the smallest valid size for the ratio (`wrap` computes it). Why: lowest setting, one image.
- Use `codex-image` only when asked. Why: it has no quality or size control.
- Don't batch unless the captain asks for one. Why: each image is reviewed before the next one is made, and a batch multiplies a bad prompt.
- Don't submit paid video, a higher quality setting or any other spend without the captain's approval, with the cost stated first. Why: spend is his decision.

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
| `10-style-clone-new-scene.json` | W1 from `library/styles/gym-mirror-selfie-budget-night.json` |
| `character-sheet-example.json` | Optional structured character sheet (`organic-character/1`) |
| `12-character-new-image.json` | W2 with character refs and physique anchor |
| `13-character-replaces-person.json` | W3 person replacement |
| `14-character-creation.json` | Casting image for a new character |
| `15-surgical-edit.json` | Fixing a readout and removing a stray phone |
| `16-product-insertion.json` | Inserting a product into an existing image |
| `17-video-first-frame.json` | First frame for a talking walk clip |
| `18-multi-character.json` | Two characters, one phone |
| `19-continuity-before.json` | Series continuity, "before" state |
| `20-no-person-object-scene.json` | No-person scene with exact scene text |

The example paths (accounts/example/..., raw/...) and the example character are illustrative, not a real account.
