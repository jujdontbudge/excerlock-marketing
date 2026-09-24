# Hayden's assets

**None of these is approved as her character reference.** Her design is not approved yet (`account.md`). The copied files live in `accounts/hayden/assets/` (gitignored; copied from the archive, which stays untouched). Archive paths are written `data/...` for `~/firstmate-decommission-backup-2026-09-23-v2/quarantine-firstmates/excerlock-marketing-firstmate/data/`, and `worktree/...` for `~/firstmate-decommission-backup-2026-09-23-v2/quarantine-worktrees/excerlock-marketing-da80f6/3/excerlock-marketing/`.

## Copied

| File | What it is | Archive origin | When to use it |
|---|---|---|---|
| `candidate-d-04-honey-blonde-bluegrey.png` | Candidate D (941x1672), the design the captain selected on 2026-09-22: bedroom mirror selfie, long honey-blonde hair with darker roots, big smile, faded raspberry cropped tank, navy gym shorts, white socks and grey trainers, dark phone case, messy bed and laundry behind. Made with the Codex image route (GPT-6 Astra, low effort), one of four casting options. | `worktree/content/characters/hayden/candidates/04-honey-blonde-bluegrey.png` | The reviewer's benchmark for her casting appeal and look. Never attach it to a generation. |
| `candidate-d-04-honey-blonde-bluegrey.prompt.md` | The exact prose prompt candidate D was made from. | `worktree/content/characters/hayden/candidates/04-honey-blonde-bluegrey.prompt.md` | History only; new prompts are JSON. |
| `hayden-regular-nb2-05k-v3.jpg` | A 416x624 edit of candidate D on regular Nano Banana 2 (`gemini-3.1-flash-image`, image size 512, minimal thinking): the same bedroom, pose and outfit, slightly slimmer. | `data/hayden-character-options/nanobanana/hayden-regular-nb2-05k-v3.jpg` (script `regular-nb2-edit.py`, usage `hayden-regular-nb2-05k-v3.usage.json`) | Not approved. A record of the regular Nano Banana 2 route; don't use it as a reference until the captain approves it. |
| `hayden-pro-v2.jpg` | The latest casting render (768x1376), Nano Banana Pro at its lowest 1K, text only, from the corrected target: bedroom mirror selfie, voluminous honey-blonde waves, baby-blue cropped scoop tank, black shorts, exposed narrow waist, hand in her hair, white socks and sneakers. Her phone carries Zoey's leopard case. | `data/hayden-character-options/nanobanana/hayden-pro-v2.jpg` | Closest to the target, not canonical because of the leopard case. Don't attach it until the captain accepts it and her own case replaces the leopard one. |
| `hayden-pro-v2.prompt.json` | The JSON prompt behind Pro v2 (`organic-image-prompt/1`, `character_creation`, no references attached). | `data/hayden-character-options/nanobanana/hayden-pro-v2.prompt.json` | The starting point for her next casting prompt: keep the identity, appeal and physique fields, remove the leopard case. |

## Archive only (not copied)

| Item | Archive path | Status |
|---|---|---|
| Four casting prompts A to D (`01-dark-brunette-hazel`, `02-auburn-green-freckles`, `03-olive-dark-eyes`, `04-honey-blonde-bluegrey`) | `data/hayden-character-options/*.prompt.json`; the four images and a README in `worktree/content/characters/hayden/candidates/` | Options A to C were not chosen. |
| Nano Banana 2.5 repaint of D and its prompt | `data/hayden-character-options/nanobanana/hayden-final-anchor-v1.png`, `final-anchor.prompt.txt`, `generate.py` | Rejected as "not realistic what so ever". Never a reference. |
| Legacy Nano Banana 2.5 strict edit of D and its prompt | `data/hayden-character-options/nanobanana/hayden-strict-edit-2.5-v2.png`, `strict-edit-2.5.prompt.txt`, `strict-edit-2.5.py` | Rejected: legacy 2.5 was the wrong model family. Never a reference. |
| Nano Banana Pro v1 and its prompt, request and response | `data/hayden-character-options/nanobanana/hayden-pro-v1.jpg`, `hayden-pro-v1.prompt.json`, `.request.json`, `.response.json` | Rejected as extremely unattractive. A failure example only, never a reference. |
| Non-identifying bedroom style digest used for Pro v1 and v2 | `data/hayden-character-options/style/organic-bedroom-video-frame.json` | Style only; usable for a new casting prompt. |
| Hayden image preferences and reviewer checks | `data/hayden-character-options/image-prefs.md`, `reviewer-checks.md`; the reanalysis checklist in `data/hayden-reference-appearance-reanalysis/report.md` section 9 | Folded into `account.md`. |
