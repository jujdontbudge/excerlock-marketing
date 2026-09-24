# Deck 01 image log

All paths are in the archive, `data/slideshow-01-final/images/` (see `AGENTS.md`). The built slides (`data/slideshow-01-final/build/slide-01..07.jpg`, with `slide-05-old-generated.jpg` and `slide-07-old-generated.jpg`) are referenced by the script but missing from the archive backup. The prompts in `script.md` are the legacy prose records.

| Folder | What happened |
|---|---|
| `round2/`, `round3/` | Early model comparison on the hook picture: Nano Banana, GPT Image 2.5 "sunburst" and "flare" and GPT Image 2, prompts `v1.txt` to `v3.txt`, contact sheets. |
| `round4-character/`, `round5-nano/` | Character trials for the budget-gym, couch-scroll and walk scenes on GPT Image 2.5 sunburst, then Nano Banana 2.5, Nano Banana 2 and Nano Banana 2 Lite. |
| `round6-lite/`, `round7-character/` | Hook mirror-selfie trials (sage-green set, upscale gym) on Nano Banana 2.5, Nano Banana 2 Lite and Nano Banana 2. |
| `round8-grace/` | Her approved picture (2026-09-17, `gemini-2.5-flash-image`, 4 images). v1 and v2 were deleted because they copied the creator's likeness; v3 mixed backgrounds; v4 used the person-masked scene of @graceelizabethlifts 7662822176965266701 slide 1 plus a tight crop of the girl and got "correct girl, exact gym". Then case trials (white, light beige, leopard) and a case swap to the leopard case: `grace-final-leopard-case.png` (identical to `grace-remake-11-swap31.png`). References in `ref/`. |
| `round9-lockin/` | 12 lock-in shots of her on `gemini-2.5-flash-image` (13 calls with one retry) from `grace-final-leopard-case.png`, `girl-crop.jpg` and `case-leopard.png`; shot 01 got its case through a `gemini-3.1-flash-image` swap (original kept as `-nocase`). |
| `round10-before/` | Slide 2's before picture: a style digest of the source's slide 5 (`style-before-hallway-flash.json`), then about 11 prompt versions on 2.5 and 3.1. "Overweight" or "fat" wording was refused (`IMAGE_OTHER`); "plus-size, curvy, fuller figure" passed. Final: `before-final.png`. |
| `reimagine/` | Text-only GPT Image 2 low reimagines: slide 4's meal prep from @gabylrei 7663840390155341069 slide 4 (`gabylrei-1069-s4-gpt2-low-01..04.png`), the yermospam slide 5 take, the walk and StairMaster candidates (`slide6-walk-01.png`, `slide7-stairmaster-01.png`, `stairmaster-phone-down-gpt2-low-01..02.png`). |
| `remakes/`, `nonhuman-variants/` | Remakes and no-person variants of the bodybymij, bymaddiefit, gabylrei, liftwithhannahh, myspacegym and yermospam source slides for slides 3 and 4. |

2026-09-20: slide 5 was rebuilt as the full-frame steps receipt and slide 7 as the full-frame blocker screen, both fitted by height on black (`sections/slideshows/assets.md`). No image calls.

Costs for this deck were not logged per image.
