# Zoey
<!-- lint-names: Zoey, Grace, our girl, @gabymsanchezz -->

Zoey is the existing TikTok account. Its character is called "our girl" in the deck scripts and "Grace" in old file names. Slideshow decks 01 to 05 are hers, made with the retired JSON pipeline (`docs/adr/0004-reference-swap-images.md`).

## Audience

Gym girls, about 16 to 26, who save and share "dream body" posts. The account sells a body result, and she is the result.

## Character

Her face and hair are her master reference, `accounts/zoey/assets/master.png` (`assets.md`), attached as image 2 to every swap that shows her. Approved by the captain on 2026-10-04.

- The captain's description: a young blonde girl, conventionally very pretty with a sharp jawline, fair skin (not tanned) and natural golden blonde hair, never platinum. A gym girl. She looks 19 to 20: grown, but still youthful.
- Body (captain, 2026-10-06, replacing the softer 2026-10-04 body): unrealistically skinny and toned, the "dream body" the account sells. A tiny, very narrow waist, a flat stomach with clearly defined abs and visible ab lines, slim toned thighs, slim arms with no bulk, and a full chest. Why: the captain wants her noticeably skinnier and more toned than the girls in the reference photos, and sent a mirror selfie of a very lean girl with visible abs as the target.
- Makeup: natural (see the makeup line).

**Body line.** Paste this into every swap prompt that shows her, because the model otherwise keeps the reference woman's body:

> She is 20, clearly a grown woman but still youthful, conventionally very pretty, with natural golden blonde hair, not platinum. She is extremely skinny and toned, much leaner than the woman in image 1: a tiny, very narrow waist, a completely flat stomach with clearly defined abs and visible ab lines, slim toned thighs, slim arms with no bulk, and a full C-cup chest.

**Identity line.** Paste this too. It names her own traits from the master reference so her face holds from slide to slide (written 2026-10-04 from `master.png`):

> Keep her exactly as in image 2: fair skin with a warm peach undertone, visible pores and a light natural flush on her cheeks and nose, pale blue-grey eyes, soft straight dark-blonde brows, a slim straight nose, natural rosy lips, and dark ash-blonde roots blending into medium golden blonde lengths, fine and straight, with a few fine flyaways at her temples.

**Makeup line.** Paste this too:

> She wears natural no-makeup makeup: her real skin texture and pores show through a sheer skin tint, with a soft natural flush on her cheeks, brushed-up natural brows, a little brown mascara and a tinted balm close to her own lip colour. No contour, no false lashes, no eyeliner, no lip gloss.

### Don'ts

- Don't swap her into a reference whose girl hides the body the hook sells, or whose body is flat, wiry or heavier. Pick another reference. Why: the model keeps the reference body, and the captain rejected "fat and wiry" deck 05 slide 1 four times; a girl who looks worse than the viewer makes the deck a lie.
- Don't give her bulky or veiny arms, or tattoos. Her arms are slim and toned (captain, 2026-10-04, replacing "no muscular arms" from 2026-09-20). Why: a lifter look and a visible vein were rejected, and tattoos aren't hers. Remove the reference's tattoos in the prompt.
- Don't show a worse body on a before slide. The before is told by the setting, outfit, posture, light and caption. Why: the story works with the same body.
- Don't render two sets of headphones. Why: the generator kept adding a second pair.
- Don't crop tighter than the reference. Why: a closer crop was rejected as "too close to screen" (captain, 2026-09-17).
- Don't describe her face trait by trait in a prompt; attach the master reference. Why: long face lists came out uncanny (G66 v4, 2026-10-02).

## Voice

- Lowercase, casual and spoken, with her typos kept: "your" for "you're", "ur", "im", "cant", "heres", "legit", "ez".
- One word in caps for emphasis: "i KNOW", "NOTHING was moving", "cardio AFTER".
- First person for proof ("heres proof", "this was me"), second person for instructions ("your parking as close as you can").
- A short pointer line ending in `>>>` leads into the value slides ("what actually worked >>>").
- An aside is its own short line with "!!" ("free steps!!!"), used rarely.
- The captain writes her titles, and his words are final. His style: one spoken lowercase sentence, a concrete noun (steps, legs, fat), often a twist at the end: "i didn't want to get 10k steps today but...", "why you're not hitting your steps (it's not your legs)", "want to lose fat but nothing is working? this is what i did", "how i get my steps in as a phone addict".
- The CTA lines are his too, and may keep his brackets: "use excerlock to make your phone block apps if your not moving. i legit cant scroll unless im walking around (works on the treadmill!!)".
- Deck 01 is in sentence case because it predates this voice; new decks are lowercase.

## Assets

Her master reference: `accounts/zoey/assets.md`.

## Platform accounts and profile setup

Updated 2026-10-09 after the captain authorized creation and the YouTube Create clicks. Keep the existing TikTok account unchanged.

- Display name: **Zoey**.
- Bio: `gym days, 10k steps + getting out of my own way`.
- YouTube profile picture: her approved master reference from `assets.md`, uploaded and saved.
- Instagram profile configuration remains pending because the account is restricted.
- YouTube banner, if wanted: `gym days + everyday movement`. Proposed copy; no banner asset exists.

| Platform | Handle | Verified status |
|---|---|---|
| Instagram | `@zoey.fitness__` | Registered; email and fresh NYC SMS verified. Captain-provided selfie submitted on 2026-10-09; appeal under review. Instagram says review usually takes about an hour. Still restricted and not fully configured. |
| TikTok | Existing `@zoey54411` | Preserved; no rename or replacement account created. |
| YouTube | [`@zoey.fitness`](https://www.youtube.com/@zoey.fitness) | Created and usable. Portrait, bio and contact email saved in Studio. |

YouTube channel ID: `UCiBNbGhOHZ9lEO-zU_D5bjg`. This is a separately managed Brand Account channel under the captain's existing Google login, with no independent Google password.

Receiving alias and YouTube contact email: **`zoey@excerlock.com`**. Instagram confirmation mail arrived through Namecheap's existing catch-all forwarding to the captain's Gmail. No mailbox purchase or DNS change was needed; the alias is not a separate mailbox or sending identity.

The verification screen asked for a photo clearly showing the account operator's face. The captain supplied his own selfie and authorized upload; the original file was submitted without alteration on 2026-10-09. No generated character portrait was submitted. One $0.80 NYC 917 verification expired unused and was refunded; a fresh $0.80 verification succeeded on 2026-10-09. The captain approved up to $1.60 in existing credits for the two pending Instagram verifications; no top-up or recurring rental was authorized in this continuation.

Evidence: `raw/profile-plans-2026-10-08/youtube-three-channels-created.png`, `zoey-youtube-configured.png`, `zoey-youtube-contact-saved.png`, `zoey-instagram-selfie-required.png`, and `zoey-instagram-appeal-submitted.png`. The next required step is Instagram's appeal decision. Handles follow the [complete-word username rules](../../core/workflows/new-account.md#handles-and-platform-accounts).
