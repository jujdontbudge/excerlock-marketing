# Style clone — standing workflow

The standing procedure whenever someone asks to "copy the style of this
image". Three steps, then injection. Method adapted from
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

Give the image to a vision-capable model with this prompt (adapted from the
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
- People stay generic: pose type, wardrobe category, face visibility. Never
  record anything identifying — facial features, body marks, tattoos,
  jewellery, brand names or logos on props or equipment. Describe branded
  objects generically ("cream strength machines", never a brand).
- End with mood, a one-line reusable_prompt_fragment (comma-separated, ready
  to append to a scene description), an avoid list (what would break the
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

## Step 4 — Inject

Two ways to use a saved block:

1. **Full prompt build** — paste the whole style JSON into the
   `<visual_analysis_reference>` slot of `skills/organic-iphone-photo.md`,
   set `polish_level`, and have the model produce the generation JSON.
2. **Quick append** — append the style's `reusable_prompt_fragment` to the
   scene description and let `codex_image` pass the combined string verbatim:

```
<scene description>. <reusable_prompt_fragment>, vertical 9:16 photo,
no film grain, no DSLR look, no readable brand logos
```

(The trailing "no …" clauses come from the style's `avoid` list plus the
standard iPhone-look exclusions; GPT-image-class models take no separate
negative prompt, so they ride inside the prompt string.)

## Current saved styles

See `content/styles/README.md` for the index.
