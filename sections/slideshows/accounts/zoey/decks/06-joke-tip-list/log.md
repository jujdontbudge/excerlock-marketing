# Deck 06 image build log

2026-09-26. One seven-slide Zoey joke-tip-list deck; captain approved the model split and the initial paid generation. The script is `script.md`. All seven existing style digests derive from seven distinct photos of source TikTok post `7549800558354271504`, with the source's slide 7 mapped to the deck's slide 4 heartbreak interruption. Source JPEGs: `raw/tag-run/posts/7549800558354271504/01.jpg` through `07.jpg`. No source creator photo was attached to an image model; the digests supplied only camera/place/light/composition traits.

Prompt builder: `raw/zoey-06/prepare-prompts.py`; JSON prompts: `raw/zoey-06/prompts/s1.json` through `s7.json`. Each passed `python3 core/skills/image-prompt/check.py check raw/zoey-06/prompts/s*.json --rules sections/slideshows/image-rules.json`. Zoey calls attached the watch-free character reference; body-visible shots also attached the physique anchor and benchmark; mirror selfies additionally attached the leopard-case reference. The food shot attached no character image. Slide captions were not sent as burned-in image text.

Model groups (initial calls only, no automatic retries):
- Slides 1, 2, 4, 5, 6, 7: six concurrent standard `gemini-3.1-flash-image` generateContent calls, `imageSize=512`, `aspectRatio=9:16`; runner `raw/zoey-06/run-nano-group.py`. This is one simultaneously launched model group, not Google's asynchronous Batch API. Each returned a JPEG at 384×688, with usage saved beside it. Six outputs at Google's published standard rate are about $0.27, plus approximately $0.012 in prompt/reference input tokens and any other metered output; the invoice was not checked.
- Slide 3: one separate `gpt-image-2` Image API call through the bundled imagegen CLI, `quality=low`, `size=720x1280`, `n=1`, prompt in `raw/zoey-06/prompts/s3.wrapped.txt`. One GPT job is not a multi-item batch. The CLI returned a 720×1280 PNG; it did not save billable usage, so an exact cost is not claimed.

| Deck slide | Source photo | Style digest suffix | Model | Calls | First-pass image | Review | Final |
|---|---|---|---|---:|---|---|---|
| 1 | `01.jpg` | `s1-squat-rack-mirror-title` | Nano Banana 2 | 1 | `raw/zoey-06/generated/s1-v1.jpg` | PASS | pending text overlay |
| 2 | `02.jpg` | `s2-car-hood-pov-drink` | Nano Banana 2 | 1 | `raw/zoey-06/generated/s2-v1.jpg` | PASS | pending text overlay |
| 3 | `03.jpg` | `s3-overhead-plate-counter` | GPT Image 2 | 1 | `raw/zoey-06/generated/s3-v1.png` | PASS | pending text overlay |
| 4 | `07.jpg` | `s7-night-car-selfie-tilt` | Nano Banana 2 | 1 | `raw/zoey-06/generated/s4-v1.jpg` | FAIL: identity/mood | pending correction |
| 5 | `04.jpg` | `s4-dark-gym-mirror-cable` | Nano Banana 2 | 1 | `raw/zoey-06/generated/s5-v1.jpg` | FAIL: body/hands/lettering | pending correction |
| 6 | `05.jpg` | `s5-bedroom-mirror-closet` | Nano Banana 2 | 1 | `raw/zoey-06/generated/s6-v1.jpg` | PASS | pending text overlay |
| 7 | `06.jpg` | `s6-bright-cardio-floor-mirror` | Nano Banana 2 | 1 | `raw/zoey-06/generated/s7-v1.jpg` | FAIL: hands/bottle/body/geometry | pending correction |

Full verdicts: `review.md`. First-pass images and exact script text (shown below each image, not overlaid): `raw/zoey-06/preview.html`. No final slides, publishing, or commits yet.

## GPT Image 2 corrections (two concurrent groups)

The captain asked for failed slides 4, 5 and 7 to be fixed only with GPT Image 2, together as a batch. These were simultaneous low-quality Image API edit calls through the bundled `imagegen/scripts/image_gen.py` CLI, not one atomic vendor Batch API job. Each call used `gpt-image-2`, `quality=low`, `size=720x1280`, `n=1`, and `--no-augment`. Prepared by `raw/zoey-06/prepare-gpt-corrections.py` and `raw/zoey-06/prepare-gpt-v3.py`; the JSON prompt for every version passed `check.py check --rules`. The `*.wrapped.txt` files are the exact strings sent to the API. The CLI did not save billable token usage, so exact cost is unknown; no unapproved higher-quality setting or model was used.

| Slide | GPT calls | v2 image | v3 image | Latest review |
|---|---:|---|---|---|
| 4 | 2 | `raw/zoey-06/generated/s4-gpt2-v2.png` | `raw/zoey-06/generated/s4-gpt2-v3.png` | FAIL: hair/face still not recognisably Zoey |
| 5 | 2 | `raw/zoey-06/generated/s5-gpt2-v2.png` | `raw/zoey-06/generated/s5-gpt2-v3.png` | PASS: three-quarter benchmark body, room for CTA |
| 7 | 2 | `raw/zoey-06/generated/s7-gpt2-v2.png` | `raw/zoey-06/generated/s7-gpt2-v3.png` | FAIL: hip/thigh proportions still drift from benchmark |

Draft of the latest seven images with exact script captions below them: `raw/zoey-06/preview-gpt-v3.html`. This is an inspection page, not final overlaid slides. No further paid retries are being run; two slides still need the captain's decision or another correction pass.
