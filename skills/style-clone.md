# Style clone — standing workflow

The standing procedure whenever someone asks to "copy the style of this
image". Three steps produce a style digest; generation then follows
`skills/organic-json-image-prompting.md`, where the digest is text inside the
JSON prompt and the inspiration image is never sent to the generator. Method adapted from
https://x.com/EXM7777/status/2094848009477685681 (2026-09-01): extract the
style as structured data, save it, inject it whenever the look is needed again.

## Step 1 — Fetch

```bash
agent-web gallery <post-url> --out raw/<name>          # TikTok photo posts, X posts
agent-web gallery <post-url> --out raw/<name> --metadata-only   # text-only need
```

Note in the raw output which slide indexes were requested (1-based,
top-left first as TikTok numbers them). Copy nothing into the repo from here —
reference images stay in `raw/` (gitignored) or another folder outside the
repository.

## Step 2 — Extract

Give the image to a vision-capable model (the Gemini CLI subscription or the
worker's own model; never Grok and never an image generator) with this prompt (adapted from the
source post's wording: "extract this visual style as JSON structured data:
colors, typography, composition, effects…"):

```
Extract this visual style as JSON structured data: colors, lighting, camera,
composition, effects, typography overlay — photography style only.

- Describe what a photographer would see: palette as hex reads taken from the
  image itself (no default palettes), white balance, contrast, saturation,
  colour casts; light sources, direction, hardness, time of day, artifacts;
  implied device and focal length, angle, distance, orientation, aspect ratio,
  depth of field; framing, subject placement, tilt, foreground, background,
  negative space, reflections.
- Catalogue every visible imperfection under effects_imperfections (noise,
  blown highlights, glare, smudges, motion blur, cropped edges, colour casts).
- Describe any burned-in caption separately under typography_overlay: exact
  text, font look, weight, relative size, colour, position, shadow/stroke,
  line count, emoji.
- Style is the photo's treatment only; it never records or caps how attractive
  anyone is (casting is set in the prompt's `appeal`, at or above the source).
- People stay generic: pose type, wardrobe category, face visibility. Never
  record anything identifying — facial features, body marks, tattoos,
  jewellery. Props and equipment keep their natural branding: note the kind of
  branding a real scene shows ("plate-loaded machines with the maker's logo",
  "supermarket protein tub") so the new scene keeps brands.
- End with mood, a one-line reusable_prompt_fragment (a comma-separated
  summary of the look, used as raw material for the JSON prompt), an avoid list (what would break the
  look), and excerlock_fit (which slideshow slot this frame serves).
- Output exactly the schema below and nothing else.

<schema>
{
  "name": "…", "slug": "…",
  "source": { "url": "…", "creator_handle": "…", "platform": "…",
    "slide_index": 1, "captured_at": "YYYY-MM-DD",
    "observed_metrics": { "plays": "…", "likes": "…", "saves": "…",
      "shares": "…", "comments": "…" } },
  "summary": "…",
  "polish_level": "polished | plandid | raw | jagged",
  "colors": { "palette": ["#…"], "white_balance": "…", "contrast": "…",
    "saturation": "…", "notable_casts": ["…"] },
  "lighting": { "sources": ["…"], "direction": "…", "hardness": "…",
    "time_of_day": "…", "artifacts": ["…"] },
  "camera": { "implied_device": "…", "focal_length_equiv": "…", "angle": "…",
    "distance": "…", "orientation": "vertical", "aspect_ratio": "9:16",
    "depth_of_field": "…" },
  "composition": { "framing": "…", "subject_placement": "…", "tilt": "…",
    "foreground": "…", "background": "…", "negative_space": "…",
    "reflections": "…" },
  "subject_treatment": { "pose_type": "…", "face_visibility": "…",
    "gaze": "…", "wardrobe_category": "…", "props": ["…"] },
  "environment": "…",
  "effects_imperfections": ["…"],
  "typography_overlay": { "present": true, "text_style": "…", "weight": "…",
    "relative_size": "…", "color": "#…", "position": "…",
    "shadow_or_stroke": "…", "lines": 1, "emoji": [] },
  "mood": "…",
  "reusable_prompt_fragment": "…",
  "avoid": ["…"],
  "excerlock_fit": "…"
}
</schema>
```

## Step 3 — Save

Write the JSON to `content/styles/<slug>.json` (it must parse:
`python3 -m json.tool content/styles/<slug>.json`) and add one row to
`content/styles/README.md` (slug, one-line summary, polish level, source link,
slide, captured date).

- Reference images stay OUT of the repository: the JSON carries the source
  link, creator handle, and slide index — that is the pointer, not a copy.
- Style describes photography, never identity (see the extraction prompt rules).
- `captured_at` and `observed_metrics` are observed metrics only — what the
  public counters showed at capture time. They are not evidence of conversion
  or performance and must not be cited as such, matching the repo method rule
  that separates observed metrics from conclusions.

## Step 4 — Use it in a JSON prompt

The digest is never pasted, appended or attached as-is. Follow
`skills/organic-json-image-prompting.md`:

- **W1 style clone, new scene** (`style_clone_new_scene`) or **W3 character
  replaces a person** (`character_replaces_person`): copy the digest's palette,
  lighting, camera, composition habits and imperfections into the matching
  fields of the prompt JSON, rewritten for the new scene. List the digest in
  `references.manifest` as a `style_digest` with `sent_to_generator: false`.
- The digest's `reusable_prompt_fragment` and `avoid` list are raw material for
  those fields and for `exclusions`; they are no longer appended as prose.
- Validate and wrap with `python3 scripts/image-prompt.py check|wrap`.

## Current saved styles

See `content/styles/README.md` for the index.
