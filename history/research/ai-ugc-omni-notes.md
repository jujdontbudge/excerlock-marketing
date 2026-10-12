# AI UGC with Omni: working notes (not yet a skill)

Lessons from the first Hayden phone-walk tests, 2026-09-28. Test files are in `raw/ai-ugc/pasta/wf2/` (gitignored). These are notes, not rules yet. Promote them into a skill once they've held up on more videos.

## What worked
- The approved 8 s clip (`omni2_rental_1x.mp4`): Gemini Omni 1.1 Flash through the Gemini API, 720p. The source video was the FLUX phone edit of the real clip at normal speed. It had two reference images, in this order: the character alone on a plain wall, then the room with nobody in it. The prompt was `omni_prompt2.txt`. It cost about $0.91.
- Make clips at normal walking speed and speed them up afterwards. Both runs that fed Omni the sped-up clip drifted off her real path.

## Changing an approved recipe
- Once the captain approves a result, change only what he names for the next test. Show him approved vs new inputs before paying. Why: after he criticised a result, the agent dropped the white kitchen and rewrote the prompt without being asked, and that wasted a paid run.
- After a bad result, explain it and propose a fix. Don't redesign and run.

## Two women in one video
- Each time, Omni was given two different places for her. Examples: a scene image with her in it plus the video's path, or "exactly as before" plus the woman already on screen. It drew both.
- Every duplicate so far appeared when she walked into or back into the frame.
- "There is only ever one woman" does not prevent it.

## Extending a clip (multi-turn, `previous_interaction_id`)
- Extension adds about 10 s: 8 s in gave 18 s out. It cost about $1.10, and the join was seamless.
- In the prompt, describe only what happens next, starting from where she is in the last frame. Example: "She continues from where she is now, walks along the back of the island to the right end, comes around the front and keeps circling. She stays in frame the whole time."
- Never write "same laps", "exactly as before", "repeat", or anything that refers back to the source clip. That wording made the model replay the old lap, with her walking in from the left, while it kept the woman already on screen.

## Checking before handing over
- Compare the output with its source at the same timestamps, not just by counting people. The second 8 s half only looked right in a people count: it matched the source's walk at just 1 of 8 checked seconds.
- Before trimming to avoid a duplicate, crop the frame edges and check every frame near the cut. A sliver of leg at 11.46 s was missed at contact-sheet size. The safe cut was 11.25 s.

## Limits
- FLUX 3 edit-video: under 15 s per clip.
- Omni: input video 10 s or less. fal's Omni endpoint blocked the identity-swap prompt, so use the Gemini API.
- Separately generated clips don't join cleanly: she jumps position and props change.
