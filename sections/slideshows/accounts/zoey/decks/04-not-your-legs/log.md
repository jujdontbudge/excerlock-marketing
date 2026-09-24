# Deck 04 image log

Built 2026-09-19 to 2026-09-20. Everything is in the archive at `data/slideshows-02-05-images/` (see `AGENTS.md`): `out/04/sN.png` with `.prompt.txt`, `.digest.json` and `.usage.json` beside each, earlier versions as `sN-vK.png`, reference slides in `out/refs/`, the verdict in `verdicts/04-s1.txt`, review pages `review.html`, `review.md`, `review.json`. Costs are estimates from token counts.

| Slide | Model and settings | Calls | Est. cost (USD) | Outcome |
|---|---|---|---|---|
| s1 | `gemini-2.5-flash-image`, batch | 3 in rounds 1 to 3; 2 Nano Banana 2 edits in rounds 3 to 6 | 0.12 for rounds 1 to 3; later rounds only in the build totals | Round 1 PASS, superseded; round 2 slim; round 3 with the physique anchor PASS (a small swoosh on the socks noted), then edits to a written PASS. |
| s2 | none | 0 | 0 | `steps-final-16349.png` full-bleed. |
| s3 | `gpt-image-2`, quality low | 1 | 0.011 | PASS. |
| s4 | none | 0 | 0 | The blocker screen, unedited. |
| s5 | `gpt-image-2`, quality low | 2 | 0.022 | v1 added a Life Fitness logo the reference lacks, v2 unbranded PASS. |
| s6 | `gpt-image-2`, quality low | 2 | 0.022 | v1 put a side mirror at the rear window, v2 PASS. |

Build totals for decks 02 to 05: about USD 4.11 (GPT Image 2 about 0.23, Nano Banana 2.5 about 1.64, Nano Banana 2 edits about 2.24).

Every image call was made before the 2026-09-22 rule that makes regular Nano Banana 2 at 512 the default; a regeneration today follows `core/skills/image-prompt/SKILL.md`.
