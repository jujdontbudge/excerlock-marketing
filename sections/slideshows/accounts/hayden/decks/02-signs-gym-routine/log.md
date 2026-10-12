# Deck 02 image build log

2026-09-28. Hayden signs deck 02: "7 signs you could be burning more fat easily".
Built following captain's explicit authorization in `raw/hayden-signs-build/brief.md`: all slides EXCEPT CTA slide 8 built in exactly one concurrent batch on Nano Banana 2 (`gemini-3.1-flash-image`), one call per slide, lowest-quality setting (`512`, `9:16`). No retries or second batch. Slide 8 CTA was excluded by design (captain will shoot organic photo later).

Approved copy promoted from `raw/script-comparison/captain-hook/gemini-3.8/script.md` to `script.md` after backing up original script to `raw/hayden-signs-build/old-canonical-script.md`.

All seven style digests derive from source TikTok post `7404352814291488032` (signs-list-diagnostic skeleton), mapped directly to signs 1–6. Source JPEGs: `raw/tag-run/posts/7404352814291488032/01.jpg` through `07.jpg`. No source creator photo was attached to an image model; the digests supplied only camera, place, light and composition traits.

Prompt builder: `raw/hayden-signs-build/prepare-prompts.py`; JSON prompts: `raw/hayden-signs-build/prompts/s1.json` through `s7.json`. Each passed `python3 core/skills/image-prompt/check.py check raw/hayden-signs-build/prompts/s*.json --rules sections/slideshows/image-rules.json`. Slide 1 attached approved dark-haired Hayden reference `accounts/hayden/assets/hayden-ref-approved.png`. Slides 2 through 7 attached no character images to maintain focus on the scene and hand/POV perspectives. Slide captions were not burned into generated images.

Model execution:
- Exactly 1 concurrent batch of 7 calls via `raw/hayden-signs-build/run-nano-group.py` using `ThreadPoolExecutor(max_workers=7)`.
- Model: `gemini-3.1-flash-image`, `imageConfig: {"aspectRatio": "9:16", "imageSize": "512"}`.
- Total batch execution time: 9.06s.
- Token totals: 15,330 prompt tokens, 7,664 candidate tokens (22,994 total tokens).
- Per-slide usage metadata saved in `raw/hayden-signs-build/generated/s*-v1.usage.json`.

| Deck slide | Role | Source photo | Style digest | Model | Calls | Generated image | Review | Final export (1080×1920) |
|---|---|---|---|---|---:|---|---|---|
| 1 | Title | `01.jpg` | `s1-bright-gym-mirror-bright-tee` | Nano Banana 2 | 1 | `raw/hayden-signs-build/generated/s1-v1.jpg` | PASS | `raw/hayden-signs-build/final/s1.png` |
| 2 | Sign 1 | `02.jpg` | `s2-market-grapes-display` | Nano Banana 2 | 1 | `raw/hayden-signs-build/generated/s2-v1.jpg` | PASS | `raw/hayden-signs-build/final/s2.png` |
| 3 | Sign 2 | `03.jpg` | `s3-hand-bowl-over-floor` | Nano Banana 2 | 1 | `raw/hayden-signs-build/generated/s3-v1.jpg` | PASS | `raw/hayden-signs-build/final/s3.png` |
| 4 | Sign 3 | `04.jpg` | `s4-fruit-wash-bowl-counter` | Nano Banana 2 | 1 | `raw/hayden-signs-build/generated/s4-v1.jpg` | PASS | `raw/hayden-signs-build/final/s4.png` |
| 5 | Sign 4 | `05.jpg` | `s5-yogurt-bowl-hand-hallway` | Nano Banana 2 | 1 | `raw/hayden-signs-build/generated/s5-v1.jpg` | PASS | `raw/hayden-signs-build/final/s5.png` |
| 6 | Sign 5 | `06.jpg` | `s6-fruit-cutting-board-counter` | Nano Banana 2 | 1 | `raw/hayden-signs-build/generated/s6-v1.jpg` | PASS | `raw/hayden-signs-build/final/s6.png` |
| 7 | Sign 6 | `07.jpg` | `s7-berry-yogurt-bowl-hand` | Nano Banana 2 | 1 | `raw/hayden-signs-build/generated/s7-v1.jpg` | PASS | `raw/hayden-signs-build/final/s7.png` |

Slide 8 (Sign 7 CTA): Excluded by design per captain's explicit instructions (organic photo will be produced later).

Captions applied via deterministic PIL script `raw/hayden-signs-build/overlay.py` to produce final 1080×1920 exports in `raw/hayden-signs-build/final/`.
Full review verdicts: `review.md`.
Contact sheet and slide viewer: `raw/hayden-signs-build/index.html`.
Completion summary: `raw/hayden-signs-build/completion.json`.
