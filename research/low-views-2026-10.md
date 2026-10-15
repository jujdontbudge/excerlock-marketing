# Why posts stall under 50 views

Captured 2026-10-14, when Zoey's and Hayden's posts were getting under 50 views. TikTok's own Community Guidelines (2026 H2 version) are the only primary source. Everything else is from tool vendors and creator blogs, so treat it as anecdote, often written to sell something. None of these sources has a controlled test.

## What TikTok's rules say ([Community Guidelines](https://www.tiktok.com/community-guidelines/en/fyf-standards))

| Rule | Status | Why it matters to us |
|---|---|---|
| "Trading, marketing, or providing access to products or services that are promoted in the context of weight loss or muscle gain, with low associated health risks" | **Age-restricted** | A post that sells the app as a way to lose weight ("you can't be lazy and lose weight", "this to this", and a CTA naming ExcerLock) fits this. It's hidden from users under 18 and probably shown less overall. |
| "Diets, exercises, products, or services that include exaggerated or harmful claims, such as those promising fast or dramatic results" | **Not eligible for For You, and age-restricted** | A before/after with a product and a big change is the risky case. |
| "We require clear labeling when AI or editing is used to realistically depict people or scenes" | Required, and unlabeled posts can be removed | Our characters are realistic AI people. Gemini images carry SynthID, and TikTok also runs AI-image classifiers ([Billo](https://billo.app/?p=52174), [Search Engine Journal](https://searchenginejournal.com/google-lets-you-turn-off-visible-watermarks-in-gemini/586145)). No source shows whether the AI label itself cuts reach. |
| "Unoriginal or reused material without anything new"; "clips that show someone else's watermark or logo" | Not eligible for For You | Pinterest or TikTok-archive filler photos with a watermark, or the same deck posted on two accounts. |
| "Directing people off-platform" | Restricted as trade | A link or "link in bio" pushing people to an app. |

## What operators say about new accounts

Sources: [Post Bridge](https://www.post-bridge.com/blog/why-is-my-tiktok-not-getting-views), [Multilogin](https://multilogin.com/blog/tiktok-views-stuck/), [SlideStorm](https://www.slidestorm.ai/articles/how-to-warm-up-new-tiktok-account), [Shortimize](https://www.shortimize.com/blog/why-is-my-tiktok-video-getting-0-views), and our own `android-vs-iphone-tiktok.md`.

- **The same few views on every post is an account or device problem, not a hook problem.** A weak hook usually stalls at 200–300 views, not under 50.
- **Check TikTok's own notices first:**
  - TikTok Studio → Account check.
  - Settings → Account → Account status.
  - On each post, More insights, which shows "not eligible for For You" or "age-restricted" and why.
- **Warm the account up before posting:**
  - 3–7 days of scrolling and liking only in the niche, about 30 minutes a day.
  - Then about one post a day for two weeks.
  - The first 5–7 posts getting very few views is normal.
- **Device and network:** at most two accounts per phone. Use real phones, not emulators, and no VPN or datacenter IP. A SIM-card connection is safest. Accounts on one device or one IP can be linked, so a flag on one hits the others.
- **Posting method:** posting through a scheduler or the API on a new account is reported to get about a tenth of the views. Post from the phone, by hand.
- **Recovering a flagged account:**
  - Pause for 24–48 hours.
  - Delete the flagged posts.
  - Post clean original content for 2–4 weeks.
  - If nothing improves after about 15 posts, start a fresh account on a clean device.
- **Don't repost a flop unchanged,** and don't buy views.

## Coverage limits

- No Reddit first-hand threads were found with these searches.
- No source measures AI-label reach.
- We don't yet know how the captain posts: phone, number of accounts per phone, VPN, account age, warm-up, or whether he posts in the app or through a scheduler.
