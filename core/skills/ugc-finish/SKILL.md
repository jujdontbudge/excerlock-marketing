---
name: ugc-finish
description: Make a finished image or video look like real phone UGC before it is posted: 2-3% film grain, 1080p export, one round of messaging-app compression with metadata stripped. Use on every final slide and every final video, right before upload.
---
# UGC finish

The last step before anything reaches TikTok or Instagram. Every final slide image and every final video goes through it, on every account and every section.

Why: generated files look clean and digital and carry editor metadata. Real UGC has a little grain, is 1080p, and has been through at least one messaging app's compression, which also strips metadata. The captain's operators report this consistently helps distribution for about two extra minutes per post (captain, 2026-10-04).

## What it does

`core/skills/ugc-finish/finish.py`, in this order:

1. **Grain: 2-3%.** The same light film texture as CapCut's Grain slider at 2-3. Default 2.5; the script refuses anything outside 2-3.
2. **Cap the short side at 1080.** Preserve smaller files without upscaling. This is the export rule, not a claim about every phone upload.
3. **One round of compression, metadata stripped.**
   - Actual round trip: `--telegram --chat-id <authorized-destination>`. Uses a bot credential from the environment. Destination is explicit, with no fallback to another bot's private chat. Sending requires authorization; validate downloaded media before handoff.
   - No-send local preview: omit Telegram. JPEG quality 82/4:2:0 or H.264 CRF 26/AAC with source metadata stripped is a **local approximation**, not verified messaging-app compression. If the assignment requires an actual messaging pass, this route is only a preview.

## Steps

1. Use the final, approved files only: after the captain's OK, after any overlay or App Store card.
2. Run:
   `.venv/bin/python core/skills/ugc-finish/finish.py <files...> --out <new-dir> [--telegram --chat-id <authorized-destination>]`
3. Open one output and check the grain is visible but subtle, and nothing is cut off.
4. Record outputs and their `.finish.json` receipts in the assets manifest. Existing outputs, basename collisions and already-finished inputs are rejected. Use only authorized final files for handoff; publication is separately authorized.

## Don'ts

- Don't run it twice on the same file. Why: a second grain-and-compress round reads as a bad repost, not as UGC.
- Don't run it before overlays or edits. Why: anything added afterwards is clean again and the file gets a second compression round.
- Preserve receipts when moving files; they prevent ordinary repeat processing, not renamed copies stripped of provenance. The grain mapping is an approximation, not calibrated equivalence to CapCut.

## Runner verification

`scripts/test` exercises real JPEG/MP4 output, no-upscale behavior, preserved EXIF display orientation before metadata stripping, receipts, overwrite/repeat/collision rejection and missing Telegram-destination rejection. It never sends a Telegram message; a local preview is not proof of a messaging round trip.
