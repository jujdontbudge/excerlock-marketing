# Paid ads research brief (Meta + TikTok), 2026-10-16

## The goal
The captain wants to start running Meta (Facebook/Instagram) and TikTok ads for ExcerLock. ExcerLock is an iOS app that locks the apps you pick until you walk, hit a step goal or go to the gym (`core/product.md`). Our audience: girls and women 16–30 into walking, the gym and fat loss.

He wants to deeply **understand** paid ads before spending, not just get a list of tips. Half the research is general: how Meta and TikTok ads actually work today, how to run them, how to reason about them, and how good operators succeed. The other half is specific to mobile apps: how subscription apps scale with paid ads, and which ad formats and creatives work for apps.

## Your output
You own one lane (below). Write `lanes/<lane>.md` in this folder, in plain English, for a smart founder who has never run ads:
1. **The 10–20 most important things to understand in your lane**, each explained with the reasoning (why it works), not just the rule.
2. **Source table**: every source you used with its URL, author, date, and type (official platform doc / respected practitioner / data report / video / X post / forum). Mark how trustworthy each is and why.
3. **Disagreements and things that changed recently** (2024–2026). Ads advice goes stale fast, so say what's current and what's outdated.
4. **What this means for ExcerLock**: concrete starting recommendations (structure, budget range, creatives to make first, what to measure), clearly marked as your judgment.
5. **Open questions** you couldn't answer.

Also save raw pages, transcripts and API responses under `raw/<lane>/` in this folder.

## Rules
- Every number or claim keeps its source URL and date next to it. Separate what platforms officially say, what data reports show, and what people claim about themselves (revenue claims on X are unverified; say so).
- Prefer high-quality sources: official Meta/TikTok docs and blogs, Apple docs (SKAdNetwork/AdAttributionKit), well-known practitioners and agencies, data reports (AppsFlyer, Adjust, Sensor Tower, RevenueCat State of Subscription Apps, Liftoff, data.ai), long-form podcasts and YouTube from people who have managed real spend. Avoid SEO spam and course sellers with nothing verifiable.
- A failed or blocked fetch is missing coverage, not "nothing found". Say what you couldn't read.
- Tools: `core/skills/web-research/SKILL.md` (agent-web, scrape-web, Jina, Firecrawl), `core/skills/ad-research/SKILL.md` (Meta Ad Library, TikTok Creative Center), `core/skills/video-analysis/SKILL.md` and `yt-dlp` for YouTube transcripts (YouTube API key in `.env`), ScrapeCreators and Apify (keys in `.env`) for X/Twitter profiles and posts. Keep paid scraping modest (well under $5 for your lane).
- Never print keys. Never log into or change any ad account, never spend money, never post anything. `META_ACCESS_TOKEN`/`TIKTOK_ACCESS_TOKEN` are read-only research use at most (e.g. Ad Library API). Do not use `GEMINI_API_KEY`.
- Write like `research/low-cost-ios-marketing-x.md`: plain, specific, sourced.

## Lanes
**General understanding (half)**
- `meta-fundamentals`: how Meta ads work in 2025–2026: auction and delivery, the Andromeda retrieval system and what it means for creative, Advantage+ (app campaigns, audience, placements), campaign/ad set structure, broad targeting vs interests, budgets (CBO/ABO), learning phase, creative testing methods, creative fatigue and volume, what metrics to read (CPM, CTR, hook rate, CPI, cost per trial, ROAS) and how to diagnose. Use Meta's own docs and the most respected Meta buyers and agencies.
- `tiktok-fundamentals`: the same for TikTok ads: auction, Smart+ / app campaigns, Spark Ads, creator content and TikTok One/Creator Marketplace, bidding (lowest cost, cost cap, VBO), creative testing, Creative Center and Top Ads, what makes native-feeling ads work, metrics, common mistakes. Official TikTok docs plus respected practitioners.
- `best-videos-and-teachers`: find the overall best YouTube videos, podcasts, courses and long-form posts on Meta and TikTok ads (not app-specific is fine), ranked. For each top pick: who the person is, why they're credible (real spend managed, results), and a summary of the key lessons from the transcript. Aim for the 15–25 best, and say which 5 the captain should watch first.

**Apps specifically (half)**
- `x-app-scalers`: on X, find people with large followings (roughly 10k+, smaller only if very specific) who have scaled apps (ideally consumer/subscription mobile apps) past about $20k/month using paid ads on Meta and/or TikTok. For each: handle, followers, which app(s), their stated revenue/spend, their playbook (structure, budgets, creatives, funnels, paywalls, tools) with links to the actual posts and threads. Then pull what repeats across them. Also include their linked blogs, newsletters or podcasts.
- `app-ua-mechanics`: paid user acquisition for iOS subscription apps on Meta and TikTok: app campaigns vs web-to-app funnels, SKAdNetwork/AdAttributionKit and AEM after iOS 14.5, MMPs (AppsFlyer, Adjust, Singular) vs SDK-only, optimizing for install vs trial vs purchase events, onboarding and paywall's effect on ad results (RevenueCat, Adapty, Superwall data), realistic CPI / cost-per-trial / trial-to-paid benchmarks for health & fitness apps, minimum budgets to exit learning, and how small apps start (first $1k–$5k).
- `app-ad-creatives`: which ad formats and creatives work for consumer apps on Meta and TikTok right now: UGC talking head, green screen, slideshow/carousel, screen-recording demo, "POV"/skits, founder ads, AI UGC, static images; hooks, length, captions, the role of the app demo. Look hardest at fitness, habit, screen-time and productivity apps (e.g. Opal, one sec, Brick, Clearspace, StepUp/WeWard-style step apps, Ladder, Strava, Cal AI-style viral apps): use the Meta Ad Library and TikTok Creative Center/Top Ads to find their long-running ads (long run = likely profitable) and describe them with links. End with the 5–10 ad concepts ExcerLock should make first.

**More app lanes (added 2026-10-16)**
- `app-geo-targeting`: how app advertisers choose and run countries/regions on Meta and TikTok: US-only vs tier-1 (US, UK, CA, AU) vs worldwide; using cheap geos (e.g. LATAM, SEA, Eastern Europe) to test creatives or exit learning, and whether those learnings transfer to the US; how CPI, CPM and trial-to-paid differ by country for health & fitness subscription apps; separate campaigns per country vs grouped; localisation (language, prices/paywall per country, App Store availability); time zones and dayparting; state/city-level targeting inside the US and whether it's worth it. Ground it in data reports and practitioners who actually ran it.
- `app-targeting-setup`: how to set up app campaigns step by step on both platforms: objectives (app installs vs app events vs value; app promotion vs web conversions), audience choices for apps (broad vs interests vs lookalikes vs Advantage+ audience; age/gender targeting for a women 16–30 app and whether to restrict it), iOS-only vs iOS+Android, OS version and device targeting, placements, exclusions, the SDK/MMP/App Events setup that must exist before spending, and the exact settings respected practitioners use for a first app campaign.
- `app-funnels-and-store`: everything between the ad and the paying user: App Store product page conversion (screenshots, preview video, Custom Product Pages tied to ads, In-App Events), web-to-app funnels and web paywalls (pros/cons, Apple rules, quiz funnels), onboarding and paywall design that lift ad ROI (RevenueCat, Superwall, Adapty data), free trial length and pricing tests, and how Apple Search Ads fits alongside Meta/TikTok.
- `app-scaling-and-measurement`: how app advertisers decide what's working and when to scale: LTV, payback period, ROAS windows, cohort analysis, blended CAC, incrementality and why platform-reported numbers lie after iOS 14.5; when and how to scale budgets (vertical vs horizontal), creative refresh cadence, killing ads, and the common ways small apps burn money. Include real case studies with numbers where possible.
