# Image reimagine - a different photo in the same style and concept

Turn one liked slide into a new slide image that shares its **style and concept** but is
**not the same picture**: same kind of place, same kind of subject, same shooting habits
and imperfections, different room, layout, and individual objects.

**Legacy.** The runner below sends a prose prompt inside the API body, which the current rule forbids. New work uses workflow W1 (`style_clone_new_scene`) in `skills/organic-json-image-prompting.md`, which keeps this skill's concept rules: the digest is text only, the place type is locked, brands are kept, and the scene is physically logical. Migrating the runner to `scripts/image-prompt.py wrap` is open follow-up work.

Runner: `scripts/image-reimagine.py <digest-slug> [take]` (reads `OPENAI_API_KEY` from
`~/excerlockmarketing/.env`). Approved 2026-09-17 on slideshow 01 slides 3 and 4.

## Inputs

1. A style digest JSON produced by `skills/style-clone.md` (palette, lighting, camera,
   composition, props, mood, imperfections, `avoid`, `excerlock_fit`).
2. Optional `<slug>.pin.txt` next to the output: one line naming objects the scene MUST
   contain (e.g. "loaded barbell with matching coloured plates both sides, pink belt").

The **source photo is never sent to the model**. Feeding it produced near-copies (a "re-shoot"),
which the captain rejected. Text-only from the digest is what gives a new scene.

## Prompt shape (what the runner builds)

1. Task line: brand-new candid low-quality iPhone snapshot, same style as the digest,
   different scene, do not reproduce any known photo.
2. Content idea: the digest `summary` as the reference, then "same category, different
   specifics".
3. **Hard constraint**: `environment` type and the primary prop never change - a commercial
   gym stays a commercial gym (never home/garage), a home kitchen stays a home kitchen.
4. Optional pin line.
5. Style block copied from the digest: polish level, lighting, colour, camera, composition
   habits, mood, imperfections, plus the older-iPhone realism list (flat focus, motion
   softness, HDR sheen, shadow noise, colour cast, smudged lens, JPEG softness, crooked framing).
6. **Brands: keep them.** Real-looking branding on plates, shoes, supplements, packaging makes
   it organic. Scene must be physically logical (barbell loaded equally both sides).
7. Must not: text captions or watermarks; people, hands, faces, body parts; styled /
   commercial / cinematic / DSLR look; bokeh, dramatic light, grain, vignette, grading.

## Generation rules (captain, standing)

- Model `gpt-image-2` on the OpenAI **API key**, `quality: "low"`, `1024x1536`. Low quality
  is the goal: cheaper (~1k tokens, about a cent) and it looks like a real phone photo.
  High quality was rejected as professional-looking. Never use high.
- **One image per run.** No batches unless the captain asks; state the cost first.
- Images go through the API key; Gemini *LLM* work (vision, digests) goes through the Gemini
  CLI subscription, never the Gemini API.
- Show the result beside the source in Chrome (`open -a "Google Chrome" <html>`) and wait for
  the captain's call before generating again.

## Known failure modes

- Drift to a different place type (gym -> home gym): fixed by the hard constraint line.
- Colour loss (coloured plates -> black): pin the colour in `<slug>.pin.txt`.
- Uneven barbell loading: ask for "matching plates both sides"; still check by eye.
