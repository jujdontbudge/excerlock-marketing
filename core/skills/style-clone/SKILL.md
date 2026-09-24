---
name: style-clone
description: Turn a liked photo into a saved, non-identifying style digest (JSON) in `library/styles/`. Use whenever someone asks to "copy the style" of an image, before writing a W1 or W3 image prompt.
---
# Style clone

Three steps produce a style digest. Generation then follows `core/skills/image-prompt/SKILL.md`,
where the digest is text inside the JSON prompt and the inspiration image is never sent to the
generator. Method adapted from https://x.com/EXM7777/status/2094848009477685681 (2026-09-01):
extract the style as structured data, save it, inject it whenever the look is needed again.

## Inputs

- The post URL and the slide indexes wanted (1-based, top-left first as TikTok numbers them).

## Step 1: Fetch

```bash
agent-web gallery <post-url> --out raw/<name>                   # TikTok photo posts, X posts
agent-web gallery <post-url> --out raw/<name> --metadata-only   # text-only need
```

Note in the raw output which slide indexes were requested.

## Step 2: Extract

Give the image to a vision-capable model (the Gemini CLI or your own model) with this prompt (adapted
from the source post's wording: "extract this visual style as JSON structured data: colors,
typography, composition, effects..."):

```
Extract this visual style as JSON structured data: colors, lighting, camera,
composition, effects, typography overlay. Photography style only.

- Describe what a photographer would see: palette as hex reads taken from the
  image itself (no default palettes), white balance, contrast, saturation,
  colour casts; light sources, direction, hardness, time of day, artifacts;
  implied device and focal length, angle, distance, orientation, aspect ratio,
  depth of field; framing, subject placement, tilt, foreground, background,
  negative space, reflections.
- Catalogue every visible imperfection under effects_imperfections (noise,
  blown highlights, glare, smudges, motion blur, cropped edges, colour casts).
- Describe any burned-in caption separately under typography_overlay: exact
  text, font look, weight, relative size, colour, position, shadow or stroke,
  line count, emoji.
- Style is the photo's treatment only; it never records or caps how attractive
  anyone is (casting is set in the prompt's `appeal`, at or above the source).
- People stay generic: pose type, wardrobe category, face visibility. Never
  record anything identifying: facial features, body marks, tattoos,
  jewellery. Props and equipment keep their natural branding: note the kind of
  branding a real scene shows ("plate-loaded machines with the maker's logo",
  "supermarket protein tub") so the new scene keeps brands.
- End with mood, a one-line reusable_prompt_fragment (a comma-separated
  summary of the look, used as raw material for the JSON prompt), an avoid
  list (what would break the look), and excerlock_fit (which post slot, such
  as hook, value or proof, this frame could serve).
- Output exactly the schema below and nothing else.

<schema>
{
  "name": "...", "slug": "...",
  "source": { "url": "...", "creator_handle": "...", "platform": "...",
    "slide_index": 1, "captured_at": "YYYY-MM-DD",
    "observed_metrics": { "plays": "...", "likes": "...", "saves": "...",
      "shares": "...", "comments": "..." } },
  "summary": "...",
  "polish_level": "polished | plandid | raw | jagged",
  "colors": { "palette": ["#..."], "white_balance": "...", "contrast": "...",
    "saturation": "...", "notable_casts": ["..."] },
  "lighting": { "sources": ["..."], "direction": "...", "hardness": "...",
    "time_of_day": "...", "artifacts": ["..."] },
  "camera": { "implied_device": "...", "focal_length_equiv": "...", "angle": "...",
    "distance": "...", "orientation": "vertical", "aspect_ratio": "9:16",
    "depth_of_field": "..." },
  "composition": { "framing": "...", "subject_placement": "...", "tilt": "...",
    "foreground": "...", "background": "...", "negative_space": "...",
    "reflections": "..." },
  "subject_treatment": { "pose_type": "...", "face_visibility": "...",
    "gaze": "...", "wardrobe_category": "...", "props": ["..."] },
  "environment": "...",
  "effects_imperfections": ["..."],
  "typography_overlay": { "present": true, "text_style": "...", "weight": "...",
    "relative_size": "...", "color": "#...", "position": "...",
    "shadow_or_stroke": "...", "lines": 1, "emoji": [] },
  "mood": "...",
  "reusable_prompt_fragment": "...",
  "avoid": ["..."],
  "excerlock_fit": "..."
}
</schema>
```

## Step 3: Save

1. Write the JSON to `library/styles/<slug>.json` and confirm it parses: `python3 -m json.tool library/styles/<slug>.json`.
2. Add one row to `library/styles/README.md` (slug, one-line summary, polish level, source link, slide, captured date) and one entry to `library/styles/index.json`.

The JSON carries the source link, creator handle and slide index. That is the pointer to the image, not a copy.

## Step 4: Use it in a JSON prompt

Follow `core/skills/image-prompt/SKILL.md`:

- **W1 style clone, new scene** (`style_clone_new_scene`) or **W3 character replaces a person** (`character_replaces_person`): copy the digest's palette, lighting, camera, composition habits and imperfections into the matching fields of the prompt JSON, rewritten for the new scene. List the digest in `references.manifest` as a `style_digest` with `sent_to_generator: false`.
- The digest's `reusable_prompt_fragment` and `avoid` list are raw material for those fields and for `exclusions`.
- Validate and wrap with `python3 core/skills/image-prompt/check.py check|wrap`.

## Outputs

- `library/styles/<slug>.json`, plus its row in `library/styles/README.md` and entry in `library/styles/index.json`.

## Don'ts

- Don't copy the reference image into the repository. Why: it shows a real person; it stays in `raw/` (gitignored) or outside the repo.
- Don't record anything identifying (face, body marks, tattoos, jewellery) in the digest. Why: a reference gives style, never identity.
- Don't record how attractive the person is, or cap it. Why: casting is set in the prompt's `appeal`, at or above the source, and a digest that says "ordinary" drags the new person down.
- Don't write "no brand names" or "no logos" into a digest. Why: natural branding makes the new scene look organic; older digests that say this are outdated.
- Don't give the image to an image generator for extraction. Why: extraction needs a vision model that returns text; a generator returns a new image.
- Don't paste, append or attach the digest as-is to a generation. Why: its fields are rewritten into the prompt JSON so the new scene stays new and the checker can validate it.
- Don't cite `observed_metrics` as evidence of conversion or performance. Why: they are the public counters at capture time, not results.
