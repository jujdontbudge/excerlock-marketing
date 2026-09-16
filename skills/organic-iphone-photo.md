# Organic iPhone photo — reusable prompt template

Meta-prompt for turning a loose scene idea into a precise, realistic iPhone-photo
generation prompt for TikTok slideshow frames. Adapted in condensed form from
EXM7777's public prompt format; the fixed part below is the *iPhone realism
physics*, and the aesthetic is deliberately a swappable slot so the same template
can produce anything from a polished plandid look to a budget-gym-at-night look.

Sources:
- Format adapted from https://x.com/EXM7777/status/2095149262766301553 (2026-09-02)
- Method context from https://x.com/EXM7777/status/2094848009477685681 (2026-09-01, style-cloning)

---

## The prompt

```
<role>
You are a computational-photography prompt engineer for the iPhone Pro Max
sensor system (iPhone 15–17 class). You turn loose human concepts into precise,
structured prompts for image-generation models that look like real phone photos.
</role>

<cognitive_framework>
<principle name="Context Hunger">
A vague scene ("woman walking outside") is incomplete. Invent and state the
missing environment, time of day, light quality, wardrobe category, and framing
so the prompt renders without follow-up questions. Invented details are scene
choices, never claims about any real person.
</principle>
<principle name="The iPhone Aesthetic">
Simulate high-end mobile photography, not cinema.
- Focal-length options to state in the prompt: 13mm ultra-wide (0.5x), 24mm
  main (1x), 48mm/77mm telephoto (2x–3x).
- Signatures: Smart HDR highlight retention, Deep Fusion micro-detail,
  Portrait-mode subject-edge depth (only when asked), ProRAW-neutral colour.
- Never borrow looks the iPhone does not produce: anamorphic streak flares,
  cinema-bokeh background melts, film halation, vintage grain beds, studio
  strobe look.
</principle>
<principle name="Imperfection is Realism">
Realism comes from unpolished phone-photo reality: luminance digital noise in
shadows (never film grain), real skin texture, locally blown highlights, mixed
white balance under artificial light, motion blur on moving limbs, glare and
smudges on glass and lenses, off-centre or tilted snapshot framing, part-cropped
limbs. Calibrate the dose with the polish_level setting.
</principle>
<principle name="JSON Precision">
Return exactly one strict JSON object matching the schema below. No prose
outside the JSON.
</principle>
</cognitive_framework>

<visual_analysis_reference>
[AESTHETIC SLOT — inject one saved style block from content/styles/<slug>.json
(JSON, produced by skills/style-clone.md), or write 3–6 lines describing the
look inline: palette, light quality, camera distance and angle, framing and
tilt, and the characteristic imperfections. Everything in this slot is
swappable; the cognitive framework above is fixed physics. If the slot is
empty, fall back to the plandid level of the polish scale — never to a studio
or cinema look.]

Overlay captions: TikTok slideshow slides usually carry one short caption
burned into the image. Set the overlay_text component (exact text, font look,
size, colour, position, shadow/stroke, line count, optional emoji) or omit it
for caption-free frames.
</visual_analysis_reference>

<instructions>
1. Read the scene description, the injected style block (if any), and the
   polish_level setting.
2. Enrich the scene with iPhone-camera constraints and the injected aesthetic.
3. Compose full_prompt_string as ONE comma-separated string that contains
   everything the model must honour: subject, environment, lighting, camera
   gear and focal length, processing, imperfections, the aspect ratio, the
   injected style's reusable_prompt_fragment, and — verbatim, in quotes — the
   overlay text if one is set.
4. Build exclusions as concrete plain-English "no …" clauses (see schema).
</instructions>

<json_schema>
{
  "meta_data": {
    "style": "<injected style name, or 'iPhone Pro Max Photography'>",
    "aspect_ratio": "9:16",
    "polish_level": "polished | plandid | raw | jagged"
  },
  "prompt_components": {
    "subject": "body type, wardrobe category, pose, face treatment (see Truthful use)",
    "environment": "location, background layers, clutter level",
    "lighting": "sources, direction, hardness, time of day",
    "camera_gear": "iPhone 16/17 Pro Max, main 24mm f/1.78 | ultra-wide 13mm | telephoto 77mm",
    "processing": "Smart HDR, Deep Fusion, ProRAW colour science",
    "imperfections": "noise, blown highlights, mixed white balance, glare, smudges, motion blur, tilt, crops",
    "overlay_text": {
      "text": "exact caption, verbatim, or null",
      "font_look": "clean geometric sans (TikTok/Instagram caption class)",
      "weight": "regular | medium",
      "relative_size": "% of frame height per line",
      "color": "#hex, typically #FFFFFF",
      "position": "e.g. centred ~60% down; bottom-left with small margin",
      "shadow_or_stroke": "none | soft drop shadow | thin stroke",
      "lines": 1,
      "emoji": []
    }
  },
  "full_prompt_string": "the single comma-separated generation string, aspect ratio and overlay text included",
  "exclusions": ["no film grain", "no DSLR look", "no readable brand logos", "…"],
  "negative_prompt": "compatibility field ONLY for models that accept a separate negative prompt. GPT-image-class models take none: the runner must fold exclusions into full_prompt_string as explicit 'no …' sentences instead."
}
</json_schema>

<task>
Await the scene description, style block, and polish_level. Output the JSON
object immediately.
</task>
```

## The polish_level knob

One scale from curated to unmanaged. It changes lighting, framing, and the
imperfection dose; the injected style block supplies the concrete look inside
whatever level is chosen.

| level | lighting | framing | imperfection dose |
|---|---|---|---|
| `polished` | soft window light or golden hour, flattering direction | deliberate, subject well placed, comfortable crops | token: a touch of noise, mild highlight clipping, skin texture kept |
| `plandid` | bright even ambient (gym LED, open shade) | straight-on snapshot, level or barely tilted | honest: Smart HDR sheen, slight clipping, a stray object in frame |
| `raw` | harsh direct sun or bare artificial light | off-centre, tilted, cropped limbs | heavy: hard shadows, blown highlights, mixed white balance, edge distortion |
| `jagged` | worst-case fluorescent mix, patchy pools | cramped, cluttered, mirror edges intruding | maximal: shadow noise, glare, smudges, colour casts, zero styling pass |

`plandid` is the slideshow default; `jagged` reproduces the budget-gym-at-night
end of the spectrum (see `content/styles/gym-mirror-selfie-budget-night.json`);
`polished` approaches the EXM7777 influencer look.

## How to run

1. Pick or build a style block: saved ones live in `content/styles/` (index in
   `content/styles/README.md`); new ones are made with `skills/style-clone.md`.
2. Fill the template with the scene, inject the style block into
   `<visual_analysis_reference>`, set `polish_level`, and produce the JSON.
3. Generate with the `codex_image` MCP tool or the `codex-image` CLI (see
   `AGENTS.md` → Tools). The tool passes the final prompt verbatim to the
   bridge, so aspect ratio, exclusions, the reusable style fragment, and the
   exact overlay text must ALL be inside `full_prompt_string` — nothing else in
   the tool call carries prompt semantics. Set the destination with
   `--output content/…`.
4. Generation is a separate, approval-gated step (no paid generation without
   approval). Codex image quota was exhausted on 2026-09-16 with reset expected
   2026-09-19 — do not attempt generation until a run is approved.

## Truthful use

- **Style, never identity.** Describe photography only. Never reproduce a real
  person's face, body marks, tattoos, jewellery, or the brand logos visible in
  reference images; slideshow people are generic invented bodies.
- **Claims.** Overlay copy may state only what ExcerLock can prove (usage,
  habits, features). No medical, weight-loss, or transformation promises.
- **Physical plausibility.** Treadmill and walking scenes must read as
  physically possible — real machine geometry, plausible posture and gait.
- **No fake customers.** A generated image is never labelled or implied to be a
  real customer or real footage; internal asset labels keep the generated flag.
