# Kristian Jennings: "Your AI UGC looks fake cause you're missing this extra step"

- **Source:** https://x.com/kristian_jennin/status/2101352217089282066, posted 2026-09-19. 31:13, 4K. 228,744 views and 1,114 likes at capture (2026-10-02).
- **Who:** a video editor and coach at Ecom Talent who makes DTC ads for an agency. The examples are hair-loss, TRT and dog-product ads.
- **How it was analysed:** the full audio was transcribed with Whisper large-v3-turbo. 468 frames (one every 4 s) were reviewed on 30 contact sheets, and the before/after reference frames were checked at higher resolution. Video, transcript and frames are in `raw/kj-ugc/` (gitignored); `raw/kj-ugc/transcript_timed.txt` has a timestamp every 30 s.
- **Limits:** the cheat sheet and prompt file he links "below" were not in the X post; only the `t.co` link to the video itself was. The prompt below is read off the screen. He shows no image-generation prompt, and says he doesn't use a master prompt for that step.

## The thesis in one line

AI UGC looks fake because the avatar image was **born inside a generator**. Start from a **real iPhone frame of a real person**, keep its pixels (noise, pores, grain, micro-texture), and change only who the person is. The video model animates whatever texture the image has. If the texture isn't there, nothing animates it, viewers hit the uncanny valley, and they stop trusting the person.

## Setup (before any AI), 02:40 to 06:00

1. **Script beats format.** "The format can't save a bad script." Even real UGC fails with a bad message.
2. **Storyboard first, in a doc.** The doc has a **Rules** block at the top, then two columns: the script line and what's on screen during it. His real rules for one ad (frame 4:16): *relaxed pacing; conversational AF; slower cuts (1.5 s hook vs 2 s hold); the guy is present throughout (lots of touch points); filming himself on location to give proof; his UGC uses a DJI mic mini; HE introduces the product; B-roll feels real, not TikTok-meme or studio; animations share one art style; show what he's saying, KISS.* He writes the rules by analysing the winner he's iterating on first.
3. **KISS.** The best ads deliver the message clearly. They aren't hyper-edited brain-rot.
4. **Avatar logic.** Pick who the avatar is from the product and angle. The avatar is someone who has **already solved** the problem, which gives quiet authority, not someone still struggling with it. Never deepfake a real professional.

## Step 1: find the reference (the step "everyone misses"), 06:00 to 15:00

- **Why:** a generator's photo can pass as real when it's still, but once animated it shows waxy skin, a poorly defined mouth and a too-perfect look. A real iPhone photo carries noise, grain, pores, under-eye lines and micro-expressions that AI can't invent. The video model animates what's there.
- **Where:** not Pinterest any more ("full of AI slop"). Go where the target audience posts: **TikTok for young**, Instagram for millennials, Facebook for older. Download the real video and take a still from it (Premiere Shift+E).
- **What to judge in a candidate:**
  1. **Framing.** Commit to a body position on purpose: leaning toward or away from the camera, table in front or not, camera at eye level or looking up or down. Pick the frame where the hands look natural (ideally both visible).
  2. **Light, with no blown highlights.** Shine is fine. Clipped white patches (forehead, cheeks, nose) are not, because "there is no data there", so the animation turns glossy and waxy. You can go right up to that line but not over it (13:00, 18:00).
  3. **Background.** Not busy, but with personality: "a blank wall *and* a photo frame". Ideally some depth behind the person, for varied light and points of interest. Real creators have usually solved this already.
  4. **No captions over the frame** if you can avoid it. Each thing the model has to remove is "another step closer to the uncanny valley". Don't agonise over it if every frame has captions.
- **Blend in.** The goal is to look like one of the creators in the feed, "not the black sheep". A small oddity is fine (a mic taped to a rose).
- **Reality check:** about 1 in 10 perfect references still animate fake. **Drop that reference and find a new one; don't fight the model** (25:00).

## Step 2: create the avatar from the reference, 15:00 to 20:30

Only **framing, lighting and background** carry over from the reference. In his before/after (14:28), the real East Asian man in a bedroom became a light-skinned man with brown wavy hair, bigger glasses, a white AirPod and a gold pendant. The bedroom, wood-slat wall, navy top, handheld mic, pose and eye-level framing stayed. In the woman's example (17:40), a dark-haired woman with a cross necklace and a ThinkPad became a blonde in a messy bun with black glasses, layered necklaces, a MacBook and one wired earbud. Room, light, pose and framing stayed.

**Model:** **Nano Banana Pro** (the original Pro, not Nano Banana 2), because "a slightly older model with more baked-in imperfections". **Avoid GPT Image 2**: it's "too good at making everything look too perfect". He adds that the model matters less than the process, and that this is the September 2026 state of things.

**The four things he changes:**
1. **Identity, genetically.** It's illegal to deepfake. Change eye colour, nose and skin pigmentation, not just hair and clothes: "impossible that without plastic surgery they could be the same person". Gender and race can stay.
2. **Background (optional).** Add a pop of colour or interest, ideally greenery. The avatar "has their own life": look around your own room for things to add.
3. **Accessories (outlier details).** AI produces the aggregate person (plain tee, common hair). Add specific, slightly unusual personal details: jewellery, earrings, one earbud in instead of two, a MacBook instead of a generic laptop. Each one is "another defence against the uncanny valley".
4. **Audio logic.** AI audio comes out clean, so the scene has to explain the clean audio: a DJI-style mic, a mic on wired headphones, a handheld interview mic, or the face very close to the phone.

**The prompting rule:** no master prompt. **One-shot all the changes in one prompt and keep pressing generate until it's right.** Never stack edits (identity, then accessories, then background, then mic). Each edit is "an overlay with feathered edges", and those hidden seams show up once the image is animated.

## Step 3: prompt the video, 20:30 to 29:30

**Model:** **Gemini Omni** (not Omni Flash), used pay-as-you-go through **KIE** (`gemini-omni-video`, reference image in `image_urls`). He rates Omni above FLUX 3 for visuals and good enough on voice for DTC.

**Three-part prose prompt** (labels on screen: PART 1 Set the scene, PART 2 Avatar dialogue, PART 3 fixed rules). The prompt he shows, verbatim:

> Static locked-off shot, UGC iPhone footage of a confident American man in his bedroom. He stays still, mouth moving naturally as he speaks, direct eye contact with camera, no camera movement. He has SUPER high energy as this is for a youtube video. The man says:
>
> "so weak follicles wake back up and stay in the growth phase longer instead of shedding early!"
>
> Pace: SUPER high energy, confident tone. Fast pacing. Smiling at the camera, he seems very friendly. One take, no jump cuts. Same avatar, same location, same camera framing. Do not recompose the shot

- **Part 1, the scene:** always state the camera movement, even "static locked-off" (otherwise it drifts or hallucinates). Handheld means "handheld UGC iPhone shot". Then the camera type ("UGC iPhone footage"; Omni matches the look to the named gear), what's happening, and what the avatar does (still, mouth natural, eye contact, no camera movement). Add an energy line: without it the delivery was flat.
- **Part 2, the dialogue:** just the script line in quotes. It's the only thing that changes between clips.
- **Part 3, the fixed rules:** built by **critiquing early takes harshly** and adding each fix (energy too low, too slow, not smiling, not confident). Always include "one take, no jump cuts".
- **Lock the prompt, then swap only the dialogue.** Spend time getting one line right, then run the whole script through the locked prompt.
- **Intonation through CAPS:** writing a word in capitals makes the model stress it.
- **Duration padding:** Omni makes 4, 6, 8 or 10 s clips. If a line needs 7 s, add throwaway words at the end, generate 8 s and cut the extra. Otherwise it either cuts off at 6 s or drags at 8 s.
- **Known quirk:** Omni gives every avatar the same set of teeth.
- **Scene changes:** he changes the avatar's position or location partway through an ad (02:40).

## Time budget (26:00)

**50%** perfecting the reference image (framing, background, accessories, imperfections, grain, pores), **25%** perfecting the prompt on the same line of dialogue, **25%** generating the rest of the script, which goes fast once the first two are locked. "The second you accept whatever quality the output is, you are locked in at that standard."

## The principles underneath

1. **Real pixels beat described pixels.** Realism is inherited from a real capture, not prompted into existence.
2. **Every generator pass costs realism.** One pass from a real frame is better than many stacked edits.
3. **Specific beats average.** Odd, personal details hold up the illusion that this is a real person with a real life.
4. **Everything in the frame needs a reason:** audio device, setting, accessories, who the avatar is.
5. **Lock the inputs, vary one thing.** A fixed reference and a fixed prompt, with only the dialogue changing.
6. **Throw away bad inputs.** Start again from a new reference rather than fixing a broken one in later steps.
