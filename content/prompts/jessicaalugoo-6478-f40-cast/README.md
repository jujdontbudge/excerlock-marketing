# Frame 40 cast: four new characters in the hallway propped-phone style

Source: [@jessicaalugoo, "walking + mat pilates combo"](https://www.tiktok.com/@jessicaalugoo/video/7525097279968136478) (shared as https://www.tiktok.com/t/ZP8TfEWa3/), posted 2025-07-09.
This is a 6.1 s video (1080x1920 HEVC, 29.97 fps, 183 frames).
Observed on 2026-09-22: 122,000 plays, 14,200 likes, 1,225 saves, 172 shares, 72 comments. These are public counters, not evidence of conversion.

- **Frame:** decoded frame 40 (1-indexed; pts 1.301 s) was extracted as a lossless PNG at full resolution with composition unchanged.
  It is saved outside the repository at `raw/tiktok-frame40/frame-040.png`, next to `video.mp4` and `meta.json`.
  Command: `ffmpeg -i video.mp4 -vf "select=eq(n\,39)" -fps_mode passthrough -frames:v 1 frame-040.png`.
- **Style digest:** `content/styles/jessicaalugoo-6478-f40-hallway-propped-body-check.json`.
  It is non-identifying and carries the photo's treatment only.
- **Prompts:** the four JSON files here use workflow W1 (`style_clone_new_scene`).
  Each has the digest as a text-only `style_digest` entry, no attached images, and `overlay_text: null`, because captions are added in the editor.
  Each passes `python3 scripts/image-prompt.py check`.
- **Not done:** no image was generated and no paid call was made.
  Generation needs approval under the house rules: one image at the lowest quality, with the cost stated first.

## The frame, in one line

A phone propped low on a kitchen counter films a woman about two metres away in a narrow apartment hallway.
The low angle leaves a big band of ceiling above her and cuts her off at the upper thigh.
The light is soft off-camera window daylight, the palette is muted warm off-white, her hands blur mid-swing, and the frame has video softness.
The hook caption sits in the empty ceiling band.
It fits as a hook or proof slide for a "walking changed my body" slideshow.

## The four characters

All four are fictional adult women, cast at or above the source's appeal.
They were made distinct in complexion, hair, build, age and routine so they can anchor separate slideshows without looking like one person.
Each scene keeps the place type (a lived-in apartment) and the concept (a propped-phone, talk-to-camera body check) but moves to a new spot with a new outfit and moment.

| # | Character | Look | Build | Walking story angle | Scene | Prompt |
|---|---|---|---|---|---|---|
| 1 | **Tessa, 29**, remote product designer | Fair, freckled; copper-auburn hair in a claw clip; green-hazel eyes | Tall, long-legged, lean-toned | Walks on her lunch break to get away from the laptop | Entryway just inside the front door, back from a walk, with bags on hooks and sneakers on the rack | `01-tessa-entryway.json` |
| 2 | **Amara, 24**, nursing student | Deep brown skin; knotless box braids in a half-up bun; bright smile | Athletic hourglass, defined shoulders and abs | Walks to clinical placements instead of taking the bus | Hallway by an open laundry closet with a stacked washer and dryer, between loads | `02-amara-laundry-hall.json` |
| 3 | **Mei, 31**, accountant | Light warm ivory skin; sleek black high ponytail with curtain bangs | Petite, sculpted | Early walk before work, so the steps are done before emails start | Short hall between the kitchen and bedroom, early-morning blind light | `03-mei-kitchen-hall.json` |
| 4 | **Priya, 28**, hospital pharmacist on rotating shifts | Medium-brown, golden undertone; long dark waves, middle part | Curvy, toned hourglass | Afternoon walk after a shift to reset | Hallway by the linen closet with a vacuum dock and slides by the baseboard, overcast afternoon | `04-priya-linen-hall.json` |

Outfits deliberately avoid the source's two-tone sports bra and dark leggings:

- Tessa wears a sage ribbed crop tank with charcoal flares.
- Amara wears a black longline bra with olive bike shorts.
- Mei wears a cream ribbed matching set.
- Priya wears a wine-red sports bra with black flared yoga pants.

## Next steps if the captain picks one

1. Approve and run one generation of that character's prompt (`image-prompt.py wrap FILE --target openai|gemini`), then have a separate reviewer check it against the digest with `research/slideshows/reviewer-checks.md`.
2. To make her a recurring character, follow `skills/organic-json-image-prompting.md` section 4.5.
   That means a `character_creation` casting selfie, the reference pack, and `content/characters/<id>.json`, with the identity and appeal wording here copied word for word.
