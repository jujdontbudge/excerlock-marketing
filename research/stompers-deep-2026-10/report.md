# Stompers: how it markets (captured 2026-10-12)

[Stompers: Walking Step Counter](https://apps.apple.com/us/app/stompers-walking-step-counter/id6477849675) is a social walking game: friends race each other on daily steps, with power-ups, sabotage and cartoon avatars. This report covers organic TikTok, organic Instagram, TikTok ads and Meta ads, plus the company, the store pages and how the app spreads. Collected by three Codex research agents. Their full per-video records, data and media are in `raw/stompers-deep/{organic-tiktok,instagram-web,ads}/findings.md`, which is gitignored.

## Coverage
- **TikTok:** 422 post records across 11 accounts: the brand, founders, a brand-owned creator, ambassadors and an employee. Plus caption, hashtag and comment discovery. 32 videos were analysed with frames, OCR and transcripts, and 28 comment threads were sampled.
  - The history is incomplete:
    - the main account is 55 of 64 posts, and the sample starts in July 2024;
    - creator accounts were sampled, not exhausted.
  - TikTok's `isAd` flag separates Promoted from Organic.
- **Instagram:** 61 rows. 23 reels were analysed, ranked by likes because Instagram hides views from logged-out tools.
  - Full history and view counts were blocked:
    - Instaloader returned 401;
    - ScrapeCreators returned 402 (0 credits);
    - Apify returned 401;
    - Tagged posts need a login.
- **Meta Ad Library:** page ID `300104169862080`, all countries, active and inactive, all media. 5 ads, pagination exhausted.
  - Spend, reach and impressions are not exposed (null), so they can't be ranked.
  - Ads that expired or were never eligible aren't in the library, so earlier history may be missing.
- **TikTok Commercial Content Library:** all regions, 2024-01-01 to 2026-10-12, 7 pages exhausted. 82 "Stompers" ads, none for this app.
  - The library keeps ads only 1 year after their last delivery, so the 2024 promoted posts below no longer appear.
  - The Creative Center returned no results for the US over 180 days. The all-region request was rate-limited.
- **Other ad libraries:**
  - Google Ads Transparency and Apple's ad repository (EU storefronts): 0 ads. US Apple Search Ads keywords are not public.
  - Snapchat: no match.
  - Reddit: needs an ads account, so it wasn't checked.
- **Off-platform:**
  - both stores' listings and Apple's in-app purchase list;
  - 416 Apple written reviews;
  - the website, help pages and blog;
  - LinkedIn, Reddit (r/stompers), YouTube (3 reviews), press, and a Superwall case study.
  - Founder X timelines were not fully readable.
- The September reports' "0 Meta ads" came from narrow US-only keyword searches. That result fits with these findings: all 5 ads started on Oct 6–7.

## The company
- **Who:** Stompers, LLC, with 2–10 staff. Co-founders:
  - Soren Iverson, design. He is known for satirical app-concept posts, and that audience seeded the launch.
  - Josh Rozin, engineering and product, based in Toronto.

  Illustration is by Jim Soper. Sources: [LinkedIn launch](https://www.linkedin.com/posts/soreniverson_a-step-tracking-app-where-you-walk-with-friends-activity-7199408955763146752-O4df), [The Verge 2024-06-01](https://www.theverge.com/24167330/stompers-ios-walking-app-soren-iverson).
- **Launch and scale:** launched on iOS on 2024-05-22.
  - **11,483 US ratings, 4.77**, captured 2026-10-12 from the [Apple lookup](https://itunes.apple.com/lookup?id=6477849675&country=us).
  - Google Play: 10K+ installs, 733 reviews, 4.5.
  - The founder claims 100K monthly active users in 2024 with no fundraising ([Intro](https://intro.co/SorenIverson)).
  - Third-party revenue models range from $20K to $100K a month. These are unreliable and are not used here.
- **Shipping pace:** 25 iOS releases between 2026-07-18 and 2026-10-10, about two a week.
- **Money:** "Super Stompers" costs $4.99 a week, $9.99 a month, or $39.99 or $59.99 a year. Coin packs cost $1.99–$13.99.
  - The [Superwall case study](https://superwall.com/case-studies/stompers) says a single-page paywall beat a multi-page flow by more than 16%.
  - Earlier paywalls showed a 7-day trial with the annual plan selected by default.
- **Paid growth intent:** a Stompers testimonial on [AppCap](https://www.useappcap.com/) says paid acquisition was profitable but limited by Apple's payout timing. It doesn't give CAC or ROAS.

## How it spreads (the engine)
1. **The product recruits.** A race needs friends.
   - Older reviews say it wouldn't start until 4 friends joined (2024-06-25), and earlier results were blurred until another friend was invited (2025-05-13).
   - Invites use a [custom App Store page](https://apps.apple.com/us/app/stompers-walking-step-counter/id6477849675?ppid=9f2c5ac8-34df-4b48-b393-17d5d5079e54) telling the recipient they have an invite to claim before it expires.
   - Sharing to Instagram Stories, Snapchat and X is built into the app.
2. **Accounts the brand owns or controls.**
   - [@anaswalks3](https://www.tiktok.com/@anaswalks3) says in its bio that Stompers owns it.
   - Five ambassadors say so in their bios: @jocelynwalking, @chanwalks, @walkingwithkat, @walkwithmichy and @walk.with.jules (Instagram).
   - @likeag.six belongs to an employee.
   - Ambassadors reuse the same app screens: Jules always shows 34,664 steps.
   - @jocelynwalking asks "what app is this?" under other ambassadors' posts, which looks like coordinated seeding.
   - An [Upwork job](https://www.upwork.com/freelance-jobs/apply/TikTok-Creator-Researcher-Walking-Habit-Social-Fitness-Content-hrs-week_~022107596515755677545/) hires a researcher to find TikTok creators and formats.
3. **Founder-led and earned distribution.**
   - The founders' TikToks: Josh's dad video (730K views) was promoted.
   - LinkedIn posts, a podcast, the Mixpanel blog, and mentions by The Verge, InsideHook and Sports Illustrated.
   - r/stompers, where users find strangers to race.
   - YouTube is negligible: 3 reviews under 2K views.
4. **Paid.**
   - 2024: promoted TikToks of the brand's stunt videos (below).
   - October 2026: a new Meta push using the creator format.

## Findings by evidence rank

### Organic (unpromoted TikTok)
Top unpromoted posts, captured 2026-10-12:

| Post | Who | Views | Shares | Hook |
|---|---|---:|---:|---|
| [7692866211423472910](https://www.tiktok.com/@jocelynwalking/video/7692866211423472910) | @jocelynwalking, ambassador | 2.2M | 83.2K | POV: fourth walk of the day because the loser of the friends' step competition buys coffee |
| [7419547771599899935](https://www.tiktok.com/@paintmeballs/video/7419547771599899935) | @paintmeballs | 991K | 424 | "I don't think anyone actually understands how hard this is" (paintball rant, app as the punchline) |
| [7639913402143395102](https://www.tiktok.com/@anaswalks3/video/7639913402143395102) | @anaswalks3, brand-owned | 467K | 9.9K | "pov you and your friends get on a step competition…" |
| [7492735924732824854](https://www.tiktok.com/@chanwalks/video/7492735924732824854) | @chanwalks, ambassador | 212K | 3.3K | "new obsession = checking how lazy my friends have been" |
| [7545332844034395422](https://www.tiktok.com/@anaswalks3/video/7545332844034395422) | @anaswalks3, brand-owned | 210K | 6.8K | "this is my sister trying to get more steps…" |

- **A social stake beats generic walking.** Examples: coffee for the loser, a $100 group-chat pot, a sister, a boyfriend.
  - The coffee post has a 3.78% share rate and the sister post 3.25%. People send these to the exact friend they'd race.
- **The structure is behaviour first, the app second.** A walking selfie, feet, a treadmill or a sibling, with the hook as on-screen text. Then a full-screen app shot as proof: leaderboard, friend names, step total.
  - The videos are music-only with no speech. A transcript misses the whole pitch.
- **What the low-view posts have in common:** the app is a small association rather than a demonstration (a shopping collage); the phone is angled and buried under text; or the screen is far away and the joke unclear.
- **The brand account itself is weak now.** Its last five posts (2026-09-22 to 10-07) got 572–1,128 views.
- **Comments ask:**
  - the app's name;
  - whether it's free or has a trial;
  - Android;
  - watch and Health sync;
  - and often *who to compete with*. That last one is a demand for people to race, not for fitness in general.

### Promoted (TikTok `isAd=true`)
All are from 2024. These are the account's biggest numbers:

| Post | Views | Hook |
|---|---:|---|
| [spaghetti](https://www.tiktok.com/@stompersapp/video/7411278946873904415) | 24.7M | "How many spaghetti noodles can hold me?" |
| [Crumbl cookie](https://www.tiktok.com/@stompersapp/video/7430974825117519134) | 13.0M | eat a 1,000-calorie cookie, then count the steps to burn it off |
| [spaghetti walk](https://www.tiktok.com/@stompersapp/video/7411441470105767198) | 4.4M | beating friends' steps by only walking on spaghetti |
| [@sonnystomps](https://www.tiktok.com/@sonnystomps/video/7375357925188963627) | 3.2M | "If you're trying to lose weight, you need this new app" |
| [foil](https://www.tiktok.com/@stompersapp/video/7410864646636178718) | 2.6M | steps on 10 pieces of aluminum foil |

- These are spectacle stunts with the app as the punchline. Most of the views came from paid distribution: the same cookie footage posted unpromoted got 16K views, against 13.0M promoted.
- The spaghetti post's share rate is 0.017%, and its comments are about wasted food, counting noodles and spotting an ad. The attention is on the stunt, not on recruiting friends.
- The monthly mix moved from product and friend content to stunts (September 2024), then food and calories (October), then doorbell-camera skits (November). Posting was sparse after December 2024.

### Meta longevity
All 5 ads are from page `300104169862080`. They started on Oct 6–7 2026 and were still active at capture. None reaches the 30-day threshold, and no spend or reach is shown.

| Ad | Hook (on-screen) |
|---|---|
| [1862363221794777](https://www.facebook.com/ads/library/?id=1862363221794777) | "Ngl I'm getting like 10k+ steps every single day because of this…" → app at 11,641 |
| [2570723496685708](https://www.facebook.com/ads/library/?id=2570723496685708) | "i think i found the cheat code to making a calorie deficit easy???" → "got this app that lets YOU COMPETE on your step count" |
| [1086160377464342](https://www.facebook.com/ads/library/?id=1086160377464342) / [1127032963455179](https://www.facebook.com/ads/library/?id=1127032963455179) | "POV everyone in the group chat put in $100 and whoever gets the most steps by end of September/August WINS IT ALL" (one concept, two versions) |
| [28597744929883096](https://www.facebook.com/ads/library/?id=28597744929883096) | "My boyfriend thinks he walks more than me so I had to humble him" (a July 2025 brand TikTok reused) |

What the 5 ads share:
- A person and a real scene come first. The app appears at about 4.3–5.4 seconds as a numeric receipt.
- On-screen text with music, no voiceover.
- 4 of the 5 are built on rivalry.
- All 5 link to the iOS App Store with "Install now" as the button and the headline "Stompers: Steps with Friends".
- None shows a price, trial or promo code.
- Two still say "end of August/September" in October, so the footage was reused from organic posts.

### Organic Instagram (provisional: likes only; promotion status not verified)
- The standout is [@walk.with.jules, Dd7KauSTryk](https://www.instagram.com/p/Dd7KauSTryk/): **91.8K likes, 341 comments** (2026-09-30).
  - Hook: "pov you're on your 4th walk of the day bc your friends thought it'd be a good idea to start a weekly step competition where loser buys coffee on Monday".
  - The app screen comes next: 32,733 steps, "im def not losing".
  - Commenters ask the app's name and tag friends, sisters and coworkers.
- Jules's later versions of the same idea got 37–56 likes.
- The official account's posts get 8–18 likes.
- A [brand-supported six-couple September challenge](https://www.instagram.com/p/Dcu83NbzXsw/) had a prize added by the brand.

## What this means for ExcerLock (principles, not copies)
- **Lead with a human reason to move, then show the app as proof.** For ExcerLock the proof is apps unlocking after the walk.
- **Their organic strength is a social stake.** ExcerLock's own stake is the user's own phone: being locked out until they walk. That is the equivalent "consequence" to put in the hook.
- **A controlled-creator network is how they do it:** a brand-owned walking account plus self-declared ambassadors posting near-identical walk-POV formats, several a day. This matches the creator system's plan.
- **Promoted stunts bought views, not friend recruitment.** Don't read 24.7M as an organic signal.

## Connecting this to the creator system
Proposal only, nothing built. Add the walking creators who are *not* Stompers-affiliated (@paintmeballs, @noiseywashere, @kel.fitxo, @dv16_xo, @step.with.stef, @prsuit, @kylie.barone) as candidates with `sections/creators/creators add`. The affiliated ambassadors are reference examples, not outreach targets.

For ExcerLock's own posts, split the existing "what app is this?" comment count in performance tracking into app-name, price, device and wants-someone-to-compete. That would show whether a social-stake hook brings the same companion demand.
