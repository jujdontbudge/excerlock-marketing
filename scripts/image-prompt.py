#!/usr/bin/env python3
"""image-prompt: check and wrap organic JSON image prompts (no network, no generation).

Usage:
  python3 scripts/image-prompt.py check FILE...
  python3 scripts/image-prompt.py wrap FILE --target openai|gemini|codex [--model M] [--size WxH]

check  validates FILE against skills/organic-json-image-prompting/schema.json plus the
       captain's standing rules, and exits non-zero on any error.
wrap   prints what would be sent: the request body for the OpenAI Image API or the Gemini
       Interactions API, or the exact prompt text for codex-image. It never calls an API;
       submitting is a separate approval-gated step. See skills/organic-json-image-prompting.md.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "skills", "organic-json-image-prompting", "schema.json")

PREAMBLE = {
    "generate": "Create one real, unedited smartphone photograph that satisfies every field of the JSON "
                "specification in `image`. It must read as an ordinary phone photo from someone's camera roll, not an "
                "illustration, render, studio shoot, advert or film still. Treat every field as a requirement; "
                "`image.exclusions` lists what must not appear.",
    "edit": "Edit the attached edit_target image according to the JSON specification in `image`. Change only what "
            "`image.intent.change_only` lists; keep everything in `image.intent.must_stay_true` and every other detail of the "
            "image exactly as it is, including identity, camera angle, framing, lighting, noise and image quality. "
            "`image.exclusions` lists what must not appear.",
    "replace": "Create one real, unedited smartphone photograph that satisfies every field of the JSON "
               "specification in `image`. The JSON describes the complete final image on its own. The attached "
               "organic_scene_source photo supplies only what its manifest entry allows; replace the person in it "
               "with the fictional character described in `image.identity` and shown in the character_reference images, "
               "as `image.intent.person_replacement` specifies. Nothing about the original person's face, body, skin, "
               "hair, tattoos or other identifying marks may carry over. `image.exclusions` lists what must not appear.",
}
REFERENCES_NOTE = ("`attached_images` maps each attached image, in order, to its `image.references.manifest` entry. "
                   "Use each one only for its may_copy and must_preserve lists and never for its must_not_transfer "
                   "list; resolve conflicts with `image.references.priority`.")
PEOPLE_ROLES = {"character_reference", "physique_anchor", "body_benchmark"}


def smallest_size(ratio):
    """Smallest WIDTHxHEIGHT with the exact ratio, both edges multiples of 16 and at least
    655,360 pixels (OpenAI GPT Image custom-size constraints)."""
    w, h = (int(x) for x in ratio.split(":"))
    m = 1
    while True:
        k = 16 * m
        if (w * k) * (h * k) >= 655360 and max(w, h) * k <= 3840:
            return f"{w * k}x{h * k}"
        m += 1


def validate(value, schema, path, errors):
    """Minimal JSON Schema subset: type, const, enum, required, properties,
    additionalProperties false, items, minItems, minLength, minimum, maximum."""
    types = schema.get("type")
    if types is not None:
        names = types if isinstance(types, list) else [types]
        py = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
        ok = False
        for n in names:
            if n == "integer":
                ok |= isinstance(value, int) and not isinstance(value, bool)
            elif n == "number":
                ok |= isinstance(value, (int, float)) and not isinstance(value, bool)
            else:
                ok |= isinstance(value, py[n])
        if not ok:
            errors.append(f"{path}: expected {types}, got {type(value).__name__}")
            return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{path}: empty string")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above {schema['maximum']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: missing required key")
        for key, sub in value.items():
            if key in props:
                validate(sub, props[key], f"{path}.{key}", errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}.{key}: unknown key")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for i, sub in enumerate(value):
                validate(sub, schema["items"], f"{path}[{i}]", errors)


def house_rules(p, errors):
    """The captain's standing rules and the workflow contracts a schema alone cannot express."""
    mode, refs = p["mode"], p["references"]["manifest"]
    sent = [r for r in refs if r["sent_to_generator"]]
    roles = {r["role"] for r in refs}
    sent_roles = [r["role"] for r in sent]
    people = p["subject"]["count"] > 0
    excl = " | ".join(p["exclusions"]).lower()
    body = json.dumps({k: v for k, v in p.items() if k not in ("exclusions", "references")}).lower()
    ident = p["identity"]

    if people and "adult" not in (ident["age"] or "").lower():
        errors.append("identity.age: every person must be stated as an adult")
    if p["subject"]["count"] != (1 if people else 0) + len(p["other_people"]):
        errors.append("subject.count must equal 1 (identity) + len(other_people), or 0 with no people")
    if p["phone"]["visible"] and not re.search(r"\bcase\b", p["phone"]["case"] or ""):
        errors.append("phone.case: a visible phone always has a described case")
    if "apple watch" in body:
        errors.append("Apple Watch mentioned outside exclusions (captain: never)")
    if people and "apple watch" not in excl:
        errors.append("exclusions: must exclude an Apple Watch when a person is in frame")
    for item in p["exclusions"]:
        low = item.lower()
        if re.search(r"\b(brand|logo)", low) and not re.search(
                r"invent|fake|made.up|misspell|garbled|extra|mirror|new|added|overlay|watermark", low):
            errors.append(f"exclusions: blanket brand/logo removal {item!r} (captain: keep natural branding)")

    ids = [r["reference_id"] for r in refs]
    if len(set(ids)) != len(ids):
        errors.append("references.manifest: reference_id values must be unique")
    missing = [i for i in ids if i not in p["references"]["priority"]]
    if missing or "prompt_json" not in p["references"]["priority"]:
        errors.append("references.priority: list every reference_id and 'prompt_json'")
    for r in refs:
        if r["sent_to_generator"] and not r["source"].startswith(("/", "~", "raw/")):
            errors.append(f"{r['reference_id']}: images sent to a generator live outside the repo or in gitignored raw/")
        if r["sent_to_generator"] and r["role"] == "style_digest":
            errors.append(f"{r['reference_id']}: a style digest is text inside the JSON, never an attached image")
        if r["role"] in ("organic_scene_source", "style_digest", "previous_frame") and not r["must_not_transfer"]:
            errors.append(f"{r['reference_id']}: {r['role']} needs a must_not_transfer list")
        if r["role"] == "organic_scene_source":
            text = " ".join(r["must_not_transfer"]).lower()
            if not ("face" in text and "body" in text):
                errors.append(f"{r['reference_id']}: organic_scene_source must_not_transfer names the face and body")

    character_modes = ("character_new_image", "character_replaces_person")
    if mode in character_modes or (mode in ("surgical_edit", "insertion", "video_first_frame") and ident["character_sheet"]):
        if not ident["character_sheet"]:
            errors.append(f"{mode}: identity.character_sheet names the canonical character JSON")
        if "character_reference" not in sent_roles:
            errors.append(f"{mode}: attach the approved character_reference images")
    if mode in character_modes + ("character_creation",) and not all(
            ident[k] for k in ("age", "presentation", "skin", "hair", "face")):
        errors.append(f"{mode}: identity is written out in full even when references are attached")
    if mode == "first_principles" and refs:
        errors.append("first_principles: no references at all")
    if mode == "style_clone_new_scene":
        if "style_digest" not in roles:
            errors.append("style_clone_new_scene: needs a style_digest manifest entry")
        if sent:
            errors.append("style_clone_new_scene: sends no images to the generator")
    if mode == "character_new_image" and "organic_scene_source" in sent_roles:
        errors.append("character_new_image: never attach an organic photo (its body outweighs the words)")
    if mode == "character_replaces_person":
        if sent_roles.count("organic_scene_source") != 1:
            errors.append("character_replaces_person: attach exactly one organic_scene_source")
        if "style_digest" not in roles:
            errors.append("character_replaces_person: style-clone the organic photo first (style_digest entry)")
        if not p["intent"]["person_replacement"]:
            errors.append("character_replaces_person: intent.person_replacement is required")
    elif p["intent"]["person_replacement"]:
        errors.append("intent.person_replacement is only for character_replaces_person")
    if mode == "surgical_edit":
        if sent_roles.count("edit_target") != 1:
            errors.append("surgical_edit: attach exactly one edit_target")
        if not p["intent"]["change_only"] or not p["intent"]["must_stay_true"]:
            errors.append("surgical_edit: name change_only and must_stay_true")
    if mode == "insertion" and not {"product_reference", "wardrobe_reference", "prop_reference"} & set(sent_roles):
        errors.append("insertion: attach the product, wardrobe or prop reference being inserted")
    if "edit_target" in roles and mode not in ("surgical_edit", "insertion"):
        errors.append("edit_target is only valid in surgical_edit or insertion")
    if not people and PEOPLE_ROLES & set(sent_roles):
        errors.append("character references are attached but subject.count is 0")
    if (mode == "video_first_frame") != (p["video_handoff"] is not None):
        errors.append("video_handoff: required for video_first_frame and null otherwise")


def check(path):
    errors = []
    try:
        with open(path, encoding="utf-8") as f:
            prompt = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return [f"cannot parse: {e}"], None
    if isinstance(prompt, dict) and prompt.get("schema_version") == "organic-character/1":
        check_character(prompt, errors)
        return errors, None
    with open(SCHEMA, encoding="utf-8") as f:
        validate(prompt, json.load(f), "$", errors)
    if not errors:
        house_rules(prompt, errors)
    return errors, prompt


def check_character(c, errors):
    """Canonical character sheet (organic-character/1): the source every character prompt copies from."""
    for key in ("character_id", "status", "fictional", "identity", "physique", "signature_props",
                "wardrobe_defaults", "reference_pack", "rules"):
        if key not in c:
            errors.append(f"$.{key}: missing required key")
    if c.get("fictional") is not True:
        errors.append("$.fictional: must be true")
    for key in ("age", "presentation", "skin", "hair", "face", "distinguishing_marks"):
        if not (c.get("identity") or {}).get(key):
            errors.append(f"$.identity.{key}: required")
    if "adult" not in ((c.get("identity") or {}).get("age") or "").lower():
        errors.append("$.identity.age: must state adult")
    if not re.search(r"\bcase\b", (c.get("signature_props") or {}).get("phone_case") or ""):
        errors.append("$.signature_props.phone_case: describe the phone case")
    for ref in c.get("reference_pack") or []:
        if not str(ref.get("path", "")).startswith(("/", "~", "raw/")):
            errors.append(f"reference {ref.get('reference_id')}: images live outside the repo or in gitignored raw/")


def prompt_text(p):
    """The exact prompt string: one JSON document (instruction, attachment order, full image spec)."""
    sent = [r for r in p["references"]["manifest"] if r["sent_to_generator"]]
    edit = "edit_target" in [r["role"] for r in sent]
    envelope = {
        "instruction": PREAMBLE["replace" if p["mode"] == "character_replaces_person" else "edit" if edit else "generate"],
        "attached_images": [f"image {n} = {r['reference_id']} ({r['role']})" for n, r in enumerate(sent, 1)],
        "image": p,
    }
    if sent:
        envelope["instruction"] += " " + REFERENCES_NOTE
    return json.dumps(envelope, indent=2, ensure_ascii=False)


def wrap(p, target, model, size):
    text = prompt_text(p)
    sent = [r for r in p["references"]["manifest"] if r["sent_to_generator"]]
    if target == "codex":
        return text
    if target == "openai":
        body = {"model": model or "gpt-image-2", "prompt": text, "size": size or smallest_size(p["aspect_ratio"]),
                "quality": "low", "n": 1}
        if sent:
            return json.dumps({"endpoint": "POST https://api.openai.com/v1/images/edits (multipart)", "fields": body,
                               "image[]": [r["source"] for r in sent]}, indent=2, ensure_ascii=False)
        return json.dumps({"endpoint": "POST https://api.openai.com/v1/images/generations", "body": body},
                          indent=2, ensure_ascii=False)
    parts = [{"type": "text", "text": text}] + [
        {"type": "image", "mime_type": "image/jpeg", "data": f"<BASE64 of {r['source']} ({r['reference_id']})>"}
        for r in sent]
    body = {"model": model or "gemini-3.1-flash-image", "input": parts,
            "response_format": {"type": "image", "aspect_ratio": p["aspect_ratio"], "image_size": size or "512"}}
    return json.dumps({"endpoint": "POST https://generativelanguage.googleapis.com/v1beta/interactions", "body": body},
                      indent=2, ensure_ascii=False)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("check", "wrap"):
        sys.exit(__doc__)
    if argv[0] == "check":
        bad = 0
        for path in argv[1:]:
            errors, _ = check(path)
            print(("ok   " if not errors else "FAIL ") + path)
            for e in errors:
                print("     - " + e)
            bad += bool(errors)
        sys.exit(1 if bad else 0)
    opts = dict(zip(argv[2::2], argv[3::2]))
    if opts.get("--target") not in ("openai", "gemini", "codex"):
        sys.exit("wrap needs --target openai|gemini|codex")
    errors, prompt = check(argv[1])
    if prompt is None and not errors:
        sys.exit("a character sheet is not an image prompt; wrap an organic-image-prompt/1 file")
    if errors:
        sys.exit("refusing to wrap an invalid prompt:\n  - " + "\n  - ".join(errors))
    print(wrap(prompt, opts["--target"], opts.get("--model"), opts.get("--size")))


if __name__ == "__main__":
    main(sys.argv[1:])
