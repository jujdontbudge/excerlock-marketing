# Every image with a person is a real photo with the person swapped

On 2026-10-02 the captain retired the JSON image pipeline: style digests (the library/styles folder and the style-clone skill), JSON image prompts and their checker (the image-prompt skill and `image-rules.json`), physique anchors, body benchmarks and per-character signature props such as the phone case. Its images were built from descriptions of real photos instead of from the photos themselves, and they read as AI.

The replacement is Kristian Jennings' AI UGC method (`research/ai-ugc-reference-first/video.md`). Every image copies one real organic photo someone else posted. One short plain-text prompt on Nano Banana Pro keeps the photo and swaps the person for our character, with the character's master reference attached for her face and hair. The method lives in `core/skills/reference-swap/SKILL.md`; images are judged with `core/skills/review-images/SKILL.md`.

The retired digests are kept, untracked, in `raw/retired/library/`. Don't bring back JSON prompts, digests, physique anchors or signature props.
