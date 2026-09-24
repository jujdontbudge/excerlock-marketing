# Deck 02 image log

Built 2026-09-19 to 2026-09-20. Everything is in the archive at `data/slideshows-02-05-images/` (see `AGENTS.md`): `out/02/sN.png` with `.prompt.txt`, `.digest.json` and `.usage.json` beside each, reference slides in `out/refs/`, verdicts in `verdicts/02-sN.txt`, and the review pages `review.html`, `review.md`, `review.json`. Runners in the same archive folder: `data/slideshows-02-05-images/tools/gpt2_batch.py` (GPT Image 2), `data/slideshows-02-05-images/tools/nb_batch.py` (Nano Banana 2.5), `data/slideshows-02-05-images/tools/build_prompts.py`. Costs are estimates from token counts.

| Slide | Model and settings | Calls | Est. cost (USD) | Outcome |
|---|---|---|---|---|
| s1 | `gemini-2.5-flash-image`, 9:16, Gemini Batch, character references attached | 3 in rounds 1 to 3; then 1 regeneration and 1 Nano Banana 2 edit in rounds 3 to 6 | 0.12 for rounds 1 to 3; later rounds only in the build totals | Round 1 PASS, superseded by the physique redo; round 2 (text-only physique block) still slim; round 3 with the physique anchor PASS. Rounds 3 to 6: twisted back leg and owl neck fixed, pose pinned, written PASS. Became the body benchmark. |
| s2 | none | 0 | 0 | `steps-final-16349.png` and `screentime-final.png` side by side, unedited. |
| s3 | `gemini-2.5-flash-image`, batch | 4 in rounds 1 to 3; then 1 regeneration and 3 Nano Banana 2 edits in rounds 3 to 6; more in rounds 10 to 14 (not split per slide) | 0.16 for rounds 1 to 3; later rounds only in the build totals | v1 matched the coastal reference but had text on her head; v2 residential dusk street PASS; round 2 turned the head to a partial face; round 3 back of the head only PASS. Rounds 10 to 14 failed it for a hidden body, regenerated within the cap of two, then PASS. |
| s4 | none | 0 | 0 | The blocker screen, unedited. |
| s5 | `gpt-image-2`, quality low, 1024x1536 | 3 | 0.033 | v1 failed (a 37:56 readout and a person), v2 carried her leopard phone (captain's rejection), v3 PASS. |
| s6 | `gpt-image-2`, quality low | 1 | 0.011 | PASS. |

Build totals for decks 02 to 05: GPT Image 2, 21 calls, about USD 0.23; Nano Banana 2.5, 41 calls, about USD 1.64; Nano Banana 2 (`gemini-3.1-flash-image`) edits, 32, about USD 2.24; about USD 4.11 in all. Gemini credits ran out once mid-build and the captain topped them up.

Batch notes: `batchGenerateContent` on `gemini-2.5-flash-image` with inline requests worked on the paid tier. Every image call was made before the 2026-09-22 rule that makes regular Nano Banana 2 at 512 the default; a regeneration today follows `core/skills/image-prompt/SKILL.md`.
