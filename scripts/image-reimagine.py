#!/usr/bin/env python3
"""image-reimagine: one new photo in the SAME style and concept as a style digest, but a different scene.

Usage: OPENAI_API_KEY in ~/excerlockmarketing/.env
  python3 scripts/image-reimagine.py <digest-slug> [take-number]
  REIMAGINE_DIGESTS=<dir of <slug>.json>  (default content/styles)
  REIMAGINE_OUT=<output dir>              (default content/generated/reimagine)
  Optional <out>/<slug>.pin.txt: one line of "the scene MUST contain ..." to pin key objects.
Rules baked in (captain, 2026-09-17): gpt-image-2, quality LOW, ONE image per run, text-only from the digest
(never feed the source photo), keep brands, physically logical scene, place type and core subject never change.
See skills/image-reimagine.md.
"""
import base64, json, os, sys, requests
KEY = [l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/excerlockmarketing/.env")) if l.startswith("OPENAI_API_KEY=")][0]
DIG = os.environ.get("REIMAGINE_DIGESTS", "content/styles"); OUT = os.environ.get("REIMAGINE_OUT", "content/generated/reimagine")
os.makedirs(OUT, exist_ok=True)
slug = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 1
PIN_FILE = f"{OUT}/{slug}.pin.txt"
d = json.load(open(f"{DIG}/{slug}.json")); L=d["lighting"]; C=d["colors"]; cam=d["camera"]; comp=d["composition"]
cat = d["excerlock_fit"]
prompt = f"""A brand-new candid iPhone snapshot in the SAME photographic style as a reference style digest, but a DIFFERENT scene, place, and objects. Do not reproduce any known photo.

CONTENT IDEA (keep the category, invent the specifics): {d['summary']} -> make a different real-life scene in the same category ({cat.split('(')[-1].rstrip(')')}): a different home or place, different specific food or objects that a normal person doing a fitness routine would actually have, a different surface, different containers and clutter. Same story, entirely different picture. HARD CONSTRAINT: the TYPE of place and the core subject stay the same as the reference - environment is "{d['environment']}" and must remain that exact kind of place (a commercial gym stays a commercial gym, never a home or garage gym; a home kitchen stays a home kitchen); the main subject stays the same kind of thing ({props.split(',')[0] if False else d['subject_treatment']['props'][0]}). Only the specific room, layout, and individual items change.

STYLE - copy exactly (this is what must match):
- polish level: {d['polish_level']}, unstyled candid smartphone photo, zero styling pass
- lighting: {', '.join(L['sources'])}; {L['direction']}; {L['hardness']}; {L['time_of_day']}; artifacts: {', '.join(L['artifacts'])}
- colour: palette {', '.join(C['palette'])}; white balance {C['white_balance']}; contrast {C['contrast']}; saturation {C['saturation']}; casts: {', '.join(C['notable_casts'])}
- camera: {cam['implied_device']} ~{cam['focal_length_equiv']}, {cam['angle']}, about {cam['distance']} away, vertical 9:16, {cam['depth_of_field']}
- composition habits: {comp['framing']}; subject {comp['subject_placement']}; {comp['tilt']}; {comp['negative_space']}; something cluttered in the background like {comp['background']} but with different items
- mood: {d['mood']}
- imperfections: {', '.join(d['effects_imperfections'])}; plus older-iPhone jagged realism: flat focus with slight overall softness, handheld motion softness, Smart HDR sheen with locally blown highlights on shiny surfaces, luminance noise in shadows, slight colour cast from room lights, smudged-lens haze, JPEG compression softness, off-centre crooked framing.

BRANDS: keep real-looking brand names and logos on equipment, plates, shoes, supplements and packaging wherever they would naturally appear - branding makes it look organic. Everything must be physically logical (a barbell is loaded with matching plates on both sides, objects rest naturally).

MUST NOT: any text captions or watermarks; people, hands, faces, or body parts; styled, commercial, editorial, cinematic, or DSLR look; bokeh, depth-of-field separation, dramatic light, film grain, vignette, colour grading.
Avoid: {', '.join(d['avoid'])}."""
r = requests.post("https://api.openai.com/v1/images/generations", headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={"model": "gpt-image-2", "prompt": prompt, "size": "1024x1536", "quality": "low", "n": 1}, timeout=400)
if r.status_code != 200: print(r.status_code, r.text[:500]); sys.exit(1)
out = f"{OUT}/{slug}-gpt2-low-{k:02d}.png"
open(out, "wb").write(base64.b64decode(r.json()["data"][0]["b64_json"])); open(f"{OUT}/{slug}.prompt.txt", "w").write(prompt)
print("wrote", out, r.json()["usage"]["total_tokens"], "tok")
