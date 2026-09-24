# Deck 03 image log

Built 2026-09-19 to 2026-09-20. Everything is in the archive at `data/slideshows-02-05-images/` (see `AGENTS.md`): `out/03/sN.png` with `.prompt.txt`, `.digest.json` and `.usage.json` beside each, earlier versions as `sN-vK.png`, reference slides in `out/refs/`, verdicts in `verdicts/03-sN.txt`, review pages `review.html`, `review.md`, `review.json`. Costs are estimates from token counts.

| Slide | Model and settings | Calls | Est. cost (USD) | Outcome |
|---|---|---|---|---|
| s1 | `gemini-2.5-flash-image`, batch, then edit passes | 4 generations and 3 edits in rounds 1 to 3; 3 Nano Banana 2 edits in rounds 3 to 6 | 0.34 for rounds 1 to 3; later rounds only in the build totals | v1 and v2 both rendered two pairs of headphones; a 2.5 edit removed both, a 3.1 edit on v2 removed only the on-ear pair: PASS, superseded. Round 2 slim. Round 3 with the physique anchor rendered two pairs again plus a "HYDRATE" word on the tumbler; one 3.1 edit fixed both: PASS. |
| s2 | `gemini-2.5-flash-image`, batch; one 3.1 edit | 1 and 1 edit; then 3 regenerations and 4 Nano Banana 2 edits in rounds 3 to 6 | 0.11 for the first build; later rounds only in the build totals | Rebuilt as the before picture (reference @iliana.rdz96 7654815554305363218 slide 3, 2.4M plays, found by a scanner sub-agent over the hunts). Invented readable packet names were made plain with one 3.1 edit: PASS. Rebuilt from across the table with no phone. The old steps slide is kept as `out/03/s2-old-steps.png`. |
| s3 | `gpt-image-2`, quality low | 4 | 0.044 | v1 text fit, v2 phone and towel added (captain's rejection), v3 wrong brand (Life Fitness instead of Primal), v4 PASS. |
| s4 | none | 0 | 0 | The blocker screen, unedited. |
| s5 | `gpt-image-2`, quality low | 2 | 0.022 | v1 a near copy of the reference, v2 PASS. |
| s6 | `gpt-image-2`, quality low | 3 | 0.033 | v1 turned the iPad into a leopard phone (captain's rejection), v3 a tablet but a black pad, v4 a pink YAGUD pad PASS. |

Build totals for decks 02 to 05: about USD 4.11 (GPT Image 2 about 0.23, Nano Banana 2.5 about 1.64, Nano Banana 2 edits about 2.24).

The worked example `core/skills/image-prompt/examples/15-surgical-edit.json` was modelled on this build's failures: it removes a leopard-print phone and fixes a "37:56" readout in `raw/generated/03-s3-v3.png`. That file never existed. In the build, this deck's s3 v2 added a phone and a towel, the leopard phone appeared in deck 02's s5 v2 and this deck's s6 v1, and the 37:56 readout was deck 02's s5 v1.

Every image call was made before the 2026-09-22 rule that makes regular Nano Banana 2 at 512 the default; a regeneration today follows `core/skills/image-prompt/SKILL.md`.
