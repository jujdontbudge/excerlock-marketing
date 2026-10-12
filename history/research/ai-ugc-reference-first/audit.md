# Audit: our AI image and UGC workflow against the reference-first method

Compares how this repo makes characters, images and video (as of 2026-10-02) with the method in `video.md`. Each finding gives what we do, where it lives, why it conflicts, and the proposed fix. **Nothing here has been changed yet.** These are proposals for the captain.

Files audited: `core/skills/image-prompt/` (SKILL.md, schema, check.py, examples), `core/skills/style-clone/`, `core/skills/review-images/`, `sections/slideshows/workflows/make-slideshow.md`, `sections/slideshows/rules.md`, `sections/slideshows/image-rules.json`, `accounts/{zoey,hayden}/account.md` and `assets.md`, `research/ai-ugc-omni-notes.md`, `raw/ai-ugc/pasta/wf2/omni_prompt2.txt`.

## Verdict

Our pipeline is the inverse of his. We **remove the real photo and rebuild the image from words**: the style digest is text only, the inspiration is never attached in W1/W2, and the JSON "describes the whole image as if no image were attached". We then try to add realism back with written imperfections (noise, pores, HDR, tilt). He **keeps the real photo's pixels and changes only the person**. His central point is that written imperfections are exactly what generators can't produce convincingly. That fits the captain's repeated "looks AI" rejections.

## Findings

### 1. Both characters were born in a generator. Severity: high.
- **Zoey:** her reference started as a real photo (@graceelizabethlifts), was regenerated on Nano Banana 2.5, then edited three times: case swap, watch removal, and a body edit for the physique anchor (`accounts/zoey/assets.md`). That is the stacked-edit chain he warns against: each pass adds hidden seams and loses real texture.
- **Hayden:** a text-only casting with no image attached (`account.md`: "describe her in words only"), then a dark-hair edit. That is the "generate a nice photo in ChatGPT" route he says always lands in the uncanny valley.
- **Fix:** recast both characters from a real TikTok frame, in one pass of identity change on Nano Banana Pro (Step 2 in `video.md`). The approved result becomes the canonical reference because it carries real iPhone pixels.

### 2. The style-clone pipeline throws away the thing that makes images real. Severity: high.
- `style-clone` turns the photo into JSON text. `image-prompt` W1 says "Don't attach a style digest or an inspiration image", and W2 says "Don't attach the organic photo". The digest only describes the noise and light, so the generator invents both.
- **Fix:** make **character into a real scene** the default for every person slide: the real organic photo plus the character reference go in, and only the person changes. That is today's W3 `character_replaces_person` promoted from exception to default, with a much simpler prompt (finding 3). Keep style-clone as an optional note for picking references, not something the generator ever reads.
- **Tension to resolve (Zoey's body rule):** W2 bans the attached photo because the source girl's flat or wiry body leaked in four times (`accounts/zoey/account.md`, "Body versus the organic reference"). His method keeps pose and framing from the reference, so the body mostly comes with it. The fix is in **choosing references**: only accept organic photos where the person's build, pose and outfit already fit the character's body rule. The body-rule fight then happens when picking the photo, not inside the generator. The captain should decide whether that replaces the W2 ban.

### 3. JSON prompts are the opposite of his prompting. Severity: high.
- `image-prompt` requires a JSON document of about 25 fields, every key required, and `wrap` sends the JSON as the prompt. It forbids prose. It fills camera, processing, imperfections and texture with written detail.
- He uses **short prose, one shot, all the changes in one prompt, and regenerates until it's right**. Image step: say only what changes (identity, accessories, background addition, audio device). Video step: three parts (scene, dialogue, fixed rules), locked except for the dialogue.
- Writing camera and imperfection detail for an image that already has real camera and real imperfections makes the generator redraw them, which is where the AI look comes from.
- **Fix:** replace the JSON schema with two short prose templates, sketched below. Keep a small written checklist so the reviewer can still check the work. The manifest idea (which image is which, what must not transfer) becomes one or two sentences in the prompt instead of a JSON block.

**Image (character into a real scene), sketch:**
```
Image 1 is a real phone photo. Keep everything about it exactly: the framing, camera angle, lighting, background, room, pose, outfit, grain and noise.
Change only the person into the woman in image 2: her face, eyes, nose, skin tone, hair <colour/style>, and <account's body line>.
Add: <1–3 outlier details, e.g. tiny gold hoops, a claw clip, one AirPod in>.
Do not add text, captions or watermarks. Nothing else changes.
```
**Video (Omni), his three parts:**
```
[Scene] Static locked-off shot, UGC iPhone footage of <who> in <where>. <what she does>. <energy line>.
[Dialogue] She says: "<line, with ONE word in CAPS for stress>"
[Fixed rules] One take, no jump cuts. Same person, same location, same framing. Do not recompose the shot. <fixes found in test takes>
```

### 4. Model choice. Severity: medium. Needs the captain's approval and a cost decision.
- **Ours:** Nano Banana 2 (`gemini-3.1-flash-image`) at 512, or `gpt-image-2` at low. **His:** Nano Banana Pro, and he says avoid GPT Image 2 because it's too perfect.
- **Our history:** Hayden Pro v1 on NB Pro was rejected as "the ugliest girl", but that was **text-only** casting, which this method doesn't use. Pro v2 on NB Pro was "closest to the target". So NB Pro hasn't been tested the way he uses it.
- **Video:** our approved Omni clip used **Omni 1.1 Flash**. He uses **Omni (not Flash)** through KIE.
- **Fix:** run a cheap A/B on the same real frame and character: NB2 at 512 versus NB Pro at 1K. For video, Omni Flash versus Omni. The captain approves the spend first (AGENTS.md money rule). Note that 512 is probably too small to carry real grain into an animated first frame.

### 5. Edits are stacked. Severity: medium.
- `surgical_edit` (4.6) and the reviewer's "a FAIL becomes a surgical_edit" make edit-on-edit chains normal. Zoey's watch and case fixes are examples.
- **Fix:** if an output is wrong, **regenerate from the original real frame with a corrected one-shot prompt**. Keep `surgical_edit` only for tiny fixes on stills that will never be animated. If one reference keeps failing, drop it and pick another (his "about 1 in 10" rule).

### 6. Reference selection checks the wrong things. Severity: medium.
- Our checks today: place type, no watch, not reused, matches the slide's picture line, and real brands kept.
- Missing from his list: **no blown highlights on skin** (shine is fine, clipped white isn't); **no captions over the frame**; **natural hands**; **a background with personality and some depth**; a **source platform that matches the audience** (TikTok for Zoey's 16–26 audience); and, for us, a **body and pose that already fit the character** (finding 2).
- **Fix:** add these as reference-pick checks in the image skill and the slideshow workflow step 6.1.

### 7. Characters are built toward the average. Severity: medium.
- `image-prompt` rule 3 and the `appeal` field cast everyone as "exceptionally attractive" in positive words. That's correct for the captain, but on its own it pulls toward the generator's aggregate pretty face. Our props work goes the other way: we removed props (the watch, the forced phone) instead of adding personal outlier details.
- **Fix:** keep the appeal bar, and give each character 2–4 fixed **outlier details** in `account.md` that show up across images (for example a specific claw clip, small hoops, one earbud in, a scrunchie on the wrist), checked against the existing bans (no watch, no tattoos, one pair of headphones). Real people repeat their own items, and the repetition sells "same person".

### 8. Audio logic is missing from talking video. Severity: low now, high once we make talking UGC.
- Our approved Omni work is silent walking ("Nobody speaks"), so it doesn't apply yet. Nothing in `fal-video` or the Omni notes says the scene must explain clean audio.
- **Fix:** for any talking clip, the frame shows a reason for clean audio (a mini mic, a mic on wired earphones, or the face close to the phone). Add CAPS-for-stress and the 4/6/8/10 s padding trick to the video notes.

### 9. Video prompt is not locked. Severity: low.
- `omni_prompt2.txt` is good prose and already close to his style, but it's rewritten per run. The notes already say "change only what he names", which agrees with him.
- **Fix:** keep one locked prompt per video series, change only Part 2, and build Part 3 from harsh critique of the first takes.

### 10. Review doesn't check whether an image will animate. Severity: low.
- `review-images` checks anatomy, appeal, the body and the reference, but not the things that break animation: waxy or poreless skin, blown highlights, smooth skin with no grain, or an AI-perfect mouth and teeth.
- **Fix:** add a "texture survives" check: zoom to 2x on cheek, forehead and lips, and fail any frame whose skin has lost the reference's grain or pores. For stills it's the same check, and it's also a test for "looks organic".

## What stays

- **Captain-facing process:** scope confirmation, script review and showing him finished slides only. The method doesn't touch these.
- **The appeal bar and Zoey's body rule.** They become reference-selection criteria (finding 2) instead of prompt fields.
- **Adults only, fictional identity, no real person's face.** His "genetic change" rule (eye colour, nose and skin pigmentation, so that without plastic surgery they couldn't be the same person) makes our identity fence stricter. Add it to the character step.
- **The slideshow house rules** (H-no-watch, H-keep-brands, H-place-type and the rest). Keeping the real scene satisfies place-type and brands almost automatically.

## Proposed order of work (waiting for the go-ahead)

1. **Recast tests (cheap, needs approval):** pick 3 real TikTok frames per character that fit her look and body rule. One-shot identity change on NB Pro (1K) and NB2 (512) side by side, then the captain picks.
2. **Background test:** using the approved recast reference, put her into 4 to 6 new real organic photos (gym mirror, treadmill, walk, bedroom) with the prose template. Check identity consistency across them; his method doesn't solve that because he makes a new avatar per ad.
3. **Rewrite the skills:** `image-prompt` (prose templates replace the JSON schema; reference-in becomes the default), `style-clone` (becomes a reference-pick checklist), `review-images` (texture-survives check), `make-slideshow` step 6, both `account.md` files (new canonical refs and outlier details), and promote `ai-ugc-omni-notes.md` plus his video rules into a video skill.
4. **Rebuild assets:** re-render existing deck slides with the new pipeline, deck by deck, only where the captain wants it.
