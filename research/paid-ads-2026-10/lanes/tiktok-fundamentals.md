# TikTok paid ads fundamentals for ExcerLock

Researched and captured 2026-10-16. This is a learning document and proposed starting plan, not authorization to launch or spend.

## Coverage and confidence

The source register below contains **37 distinct substantive pages read**, with full extracted text, original responses and retrieval metadata saved under `../raw/tiktok-fundamentals/`. Redirects and repeat captures are not counted twice. Most evidence is official TikTok documentation; three pages are from operating agencies. No paid scraper, ad account, private analytics or Gemini API was used. Research spend: $0.

Official documentation is strong evidence for available settings and stated platform behavior. Its performance recommendations and promotional averages are not independent experiments. Agency writing is useful for reasoning about creative operations, but ecommerce experience is not evidence of subscription-app profitability. No independent, representative TikTok iOS fitness-subscription benchmark was established in this lane. No videos were watched or transcribed; practitioner video landing pages are identified as such, not passed off as transcript research.

Some `/help/article/` requests returned HTTP 403. Public canonical `/resources/help/article/` pages subsequently supplied most missing content. Failure metadata remains alongside successful captures. Several guessed or old article routes failed or returned an error shell; those are missing coverage, not sources. `spark-ads-faq` redirected to Spark Ads; `learning-phase-faq` redirected to Learning Phase. Both duplicates are excluded from the count. Search-index versions sometimes disagree with the captured live page; dates below come from the saved page wherever available.

## The 20 things to understand

### 1. You buy opportunities to reach people, not a fixed price for customers

TikTok runs a real-time auction. Its stated ranking considers the bid and the ad's relevance to the viewer; creative, targeting and account organization influence delivery. TikTok does not publish a complete reproducible ranking equation here. A stronger ad can improve the economic outcome, but no creative trick guarantees a cheap customer. An impression still has to turn into an install, activation and eventually payment. [TikTok, Auction Ads, April 2025](https://ads.tiktok.com/resources/help/article/about-auction-ads?lang=en); [Bidding methods, August 2025](https://ads.tiktok.com/resources/help/article/bidding-methods?lang=en).

**Operator inference:** Fixing a weak product demonstration can be more valuable than searching for a new interest audience. The auction and the conversion funnel both affect acquisition cost.

### 2. The optimization event tells the machine which people to find

An install campaign looks for likely installers; app event optimization (AEO) looks for people likely to complete the selected in-app action. Value-based optimization (VBO) seeks greater reported purchase or ad-revenue value. Those are different learning tasks. A cheap installer is not necessarily a subscriber. Smart+ App lists install and in-app-event optimization; VBO has separate availability limits. [Smart+ App, August 2026](https://ads.tiktok.com/resources/help/article/about-smart-plus-app-campaigns); [App VBO, October 2026](https://ads.tiktok.com/resources/help/article/value-based-optimization-app?lang=en).

**Judgment:** ExcerLock should choose the deepest correctly measured event that its budget can generate regularly. Installs can establish a baseline, but the decision to continue spending must depend on downstream activation, trials and paid customers.

### 3. Campaign, ad group and ad are different levels of decision

In a manual setup, the campaign establishes the objective and optionally shares a budget; ad groups contain delivery decisions such as audience, optimization and bidding; ads supply the content. Campaign Budget Optimization (CBO) distributes a shared budget toward campaign results. An ad-group budget gives that group its own allocation. Neither guarantees equal exposure to every creative. TikTok's CBO documentation requires a shared optimization goal and says CBO does not function with only one active ad group. [CBO setup, August 2026](https://ads.tiktok.com/resources/help/article/campaign-budget-optimization?lang=en).

**Inference:** Separate groups only when they represent a useful delivery or experimental distinction. A complicated account splits limited evidence across too many places.

### 4. Smart+ automates delivery; it does not decide whether the business works

Smart+ App automates campaign setup and optimization, creative combinations and allocation. The advertiser still supplies an app, goal, budget and content. Features include recommended existing ads, automatic creative additions, translation and App2Carousel, which can derive carousel assets from App Store imagery. Review automation against the actual app and language quality. Automation increases the importance of truthful inputs. [Smart+ App, August 2026](https://ads.tiktok.com/resources/help/article/about-smart-plus-app-campaigns).

**Judgment:** Use Smart+ when the app is eligible and the available controls fit the approved experiment. A manual campaign remains useful for control and a clearer test. Do not run both simultaneously on a tiny budget just to compare dashboards.

### 5. iOS Smart+ is not Android Smart+ or Smart+ Web

The captured Smart+ App matrix lists iOS install/AEO, **Maximum Results**, and TikTok plus Lemon8 where available; it does not support manually selecting placements or Search. It lists **VBO as Android-only within Smart+ App** and disallows mixing Spark and non-Spark ads in one campaign. The broader VBO documentation supports iOS app campaigns, which is a different statement. [Smart+ App, August 2026](https://ads.tiktok.com/resources/help/article/about-smart-plus-app-campaigns); [App VBO setup, October 2026](https://ads.tiktok.com/resources/help/article/how-to-promote-an-app-using-value-based-optimization?lang=en).

**Implication:** A tutorial showing Android cost control, web retargeting or Shop revenue optimization may be accurate and still unusable for ExcerLock's initial iOS setup. Confirm the available campaign path before budgeting around it.

### 6. Lowest cost, Maximum Delivery and Maximum Results describe a volume-first idea

Older material uses Maximum Delivery; the captured general bidding documentation uses Maximum Results. It tries to get the most selected results within the budget, without optimizing to an advertiser's target CPA. The budget controls expenditure, not the price of each customer. [Bidding strategies, September 2026](https://ads.tiktok.com/resources/help/article/bidding-strategies?lang=en).

**Judgment:** This is the clearest initial option when there is no reliable CPA history, provided the experiment has an explicit total loss limit. “It spent the budget” is not evidence that it worked.

### 7. Cost Cap is a cost target, not insurance against an expensive conversion

Current general docs call the goal-based option Target Cost per Result. TikTok says actual CPA can be above or below the target. A low target can cause insufficient delivery because too few auctions look achievable. The AEO page distinguishes iOS dedicated campaigns from regular iOS/Android and contains an App Profile Page qualification; it should not be read as universal iOS cost-cap access. [Bidding strategies, September 2026](https://ads.tiktok.com/resources/help/article/bidding-strategies?lang=en); [Bidding best practices, August 2026](https://ads.tiktok.com/resources/help/article/best-practices-for-bidding-strategies?lang=en); [AEO bidding, August 2026](https://ads.tiktok.com/resources/help/article/available-bid-strategies-for-app-event-optimization?lang=en).

**Judgment:** Set targets from observed economics and comparable historical delivery, not a wished-for number. When it does not spend, investigate eligibility, bid realism, creative and signals before declaring TikTok unviable.

### 8. VBO needs useful value signals and the right time horizon

Highest Value is the spend-oriented VBO strategy; Target ROAS prioritizes a return target, accepting variable delivery. TikTok requires value-bearing purchase or ad-revenue signals for eligibility. A formal unlocking requirement is not proof that there is enough data to optimize reliably. [VBO strategies, October 2026](https://ads.tiktok.com/resources/help/article/available-bidding-strategies-for-value-based-optimization-for-app?lang=en); [VBO setup, October 2026](https://ads.tiktok.com/resources/help/article/how-to-promote-an-app-using-value-based-optimization?lang=en).

**Inference:** For a subscription app, later renewal value is not automatically visible to a campaign optimizing an earlier value window. Model renewal and refunds separately. A target ROAS entered into Ads Manager cannot make a poor subscription cohort profitable.

### 9. Budget minimums and sensible learning budgets answer different questions

The platform's stated creation thresholds are **more than $50 at campaign level and more than $20 daily at ad-group level**. That is not a promise of useful learning. The budget guide recommends **20× current CPI for install campaigns**, or **$200 when no current CPA exists**, while Smart+ Maximum Results guidance recommends **at least 10× historical CPA daily**. These are recommendations with different contexts, not identical requirements. [Budget, July 2026](https://ads.tiktok.com/resources/help/article/budget?lang=en); [Budget best practices, August 2026](https://ads.tiktok.com/resources/help/article/budget-best-practices?lang=en); [Smart+ best practices, August 2026](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en).

**Inference:** A small founder can run a smaller bounded experiment, but must accept slower learning and weaker conclusions. Do not silently multiply a small budget across many groups.

### 10. Learning is exploration, not a ritual conversion threshold

The live Learning Phase page says volatility often starts declining after **about 25 results or 7 days**. The troubleshooting page still advises **7 days to reach 50 conversions**, while Smart+ guidance also references **up to 50 events**. These are not a single consistent exit rule. Pauses, material edits and unsuitable budgets can disrupt learning. [Learning Phase, June 2026](https://ads.tiktok.com/resources/help/article/learning-phase?lang=en); [Troubleshooting, August 2026](https://ads.tiktok.com/resources/help/article/troubleshooting-auction-ad-delivery-solutions?lang=en); [Smart+ best practices, August 2026](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en).

**Judgment:** Plan an uninterrupted observation period within a preapproved spending ceiling, allowing conversion delays. Never keep spending solely to earn a “learning complete” label. Broken links, incorrect events and an exhausted loss limit justify stopping.

### 11. Broad targeting is a starting hypothesis, not an ideology

TikTok recommends avoiding unnecessary restrictions so delivery can explore. It still offers interest targeting and even recommends relevant interests when little is known about an audience. The two approaches are compatible: broad discovery first, a purposeful constrained test later. [Broad targeting, April 2025](https://ads.tiktok.com/resources/help/article/broad-targeting?lang=en); [Interest targeting, July 2025](https://ads.tiktok.com/resources/help/article/interest-targeting?lang=en).

**Judgment:** Constrain ExcerLock to its available country, language, iOS and adult audience; avoid stacking walking, fitness, productivity and other interests into a tiny initial audience. In manual delivery, women can be a deliberate starting segment. Check which demographic controls are strict versus automated before claiming the campaign targets an exact founder persona.

### 12. Native creative still needs to explain a reason to install

TikTok recommends people, a DIY aesthetic, sound, vertical framing and safe-zone awareness. The official recommendation is **9:16 and at least 720p**, introducing the proposition in the **first 3 seconds** and prioritizing the hook within **6 seconds**. These are production starting points, not a guaranteed conversion formula. [Creative best practices, June 2025](https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en).

**Inference:** A creator showing the selected app blocked, then the demonstrated exercise condition unlocking access, explains ExcerLock faster than a general motivational montage. Native means understandable in the feed, with credible human delivery; it does not mean hiding the product indefinitely or making the screen recording illegible.

### 13. Test different arguments before polishing tiny variants

TikTok explicitly favors materially different creative when testing. Its current creative page and Smart+ App guide recommend different asset counts for their respective structures; the latter suggests **4–6 starting assets**. An automated allocator chooses where to spend, so lack of spend is not a controlled finding that a concept cannot work. [Creative best practices, June 2025](https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en); [Smart+ best practices, August 2026](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en).

**Judgment:** First compare a relatable routine problem, a direct product demonstration and a creator's honest experience. Once an argument works, iterate its opening, pacing and proof. Keep concept and variant labels so a winning edit teaches the next brief something specific.

### 14. A real experiment differs from putting several ads in one group

TikTok's split tests separate audiences so each sees one test group and other variables can remain stable. The platform reports a **90% confidence criterion** for selecting a statistically significant winner. That is its test design, not a guarantee of business impact or future performance. [Split Testing, January 2026](https://ads.tiktok.com/resources/help/article/split-testing?lang=en).

**Inference:** Use routine delivery to find promising candidates. Use a funded split test for a consequential question, such as whether a creator demonstration beats the strongest brand demonstration. Preselect the outcome and test duration. Do not compare different audiences, events and offers and attribute the entire result to a hook.

### 15. Fatigue is a performance pattern, not a fixed expiration date

TikTok recommends refreshing when results consistently decline and adding creative to the existing group rather than automatically rebuilding it. Smart+ guidance recommends trying new creative before relaunching. Rising costs may also reflect auction conditions or funnel changes. [Creative best practices, June 2025](https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en); [Smart+ best practices, August 2026](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en).

**Judgment:** Watch acquisition cost alongside destination CTR, conversion rate, frequency and acquisition quality. Keep producing new concepts, but do not delete an effective ad simply because it has been running for a week. Avoid reactive daily rebuilding.

### 16. Spark Ads license an existing post and its identity

Spark Ads use a brand's or authorized creator's organic post; paid engagement accumulates on that post. The format supports app promotion. It changes identity and interaction paths, not the underlying requirement to buy useful customers. A large creator following does not mean paid delivery is restricted to those followers. [Spark Ads, June 2026](https://ads.tiktok.com/resources/help/article/spark-ads?lang=en).

Authorization can use linked accounts or a creator-provided post code. The manual creation guide says the caption cannot be changed after authorization, and a private video becomes public when used in a campaign. The overview contains looser wording about text edits, so finalize captions and verify the exact creation path. [Spark creation guide, June 2026](https://ads.tiktok.com/resources/help/article/spark-ads-creation-guide?lang=en).

**Judgment:** Negotiate paid usage, term, territory, editing permission and renewal before selecting a creator asset. Keep a rights record and expiry reminder. A Spark code is a technical authorization, not a complete commercial agreement.

### 17. TikTok One is a sourcing and production system, not a substitute for a good brief

TikTok One supports creator discovery, production and campaign collaboration. The project flow includes requirements, ad authorization, reviews, payment choices and optional syncing for Spark Ads. It requires verified business access and is region-dependent. Creator eligibility also depends on regional availability and adulthood. [TikTok One for advertisers, June 2026](https://ads.tiktok.com/resources/help/article/about-tiktok-one?lang=en); [Project creation, March 2026](https://ads.tiktok.com/resources/help/article/how-to-create-a-new-creator-marketing-project-in-tiktok-one?lang=en); [For creators, April 2026](https://ads.tiktok.com/resources/help/article/about-tiktok-one-for-creators?lang=en).

**Practitioner perspective:** CTC advocates a repeatable creator briefing and production system; its public episode page is a summary and sales page, not a read transcript. House of Marketers describes demonstrating an unfamiliar consumer product and scaling selected creative across platforms; its results are self-reported, blended, and do not prove TikTok-only subscription economics. [CTC, date not shown; captured 2026-10-16](https://commonthreadco.com/blogs/tactics/build-creator-content-system); [House of Marketers, modified 2026-04-27](https://houseofmarketers.com/stickerbox-ai-influencer-marketing-case-study/).

### 18. Creative Center is a research tool with selection bias

Creative Center provides inspiration, trends and production tools. Top Ads is an advertiser-authorized selection, not an exhaustive view of all running ads. Its desktop tools let you filter by region, industry and objective and inspect relative performance over a video's timeline. Logged-out access is limited to **five ads**, according to the usage guide. [Creative Center, July 2026](https://ads.tiktok.com/resources/help/article/creative-center?lang=en); [Top Ads, May 2025](https://ads.tiktok.com/resources/help/article/top-ads?lang=en); [Usage guide, May 2025](https://ads.tiktok.com/resources/help/article/how-to-use-the-top-ads-dashboard?lang=en).

**Inference:** Record the problem, opening, demonstration, proof and CTA, then form a hypothesis to test. Neither a long-running ad nor high public engagement reveals spend, net revenue or profitability. This lane read the research-tool documentation; it did not collect a competitor-ad sample.

### 19. Read the funnel, and define every denominator

TikTok distinguishes all clicks from destination clicks. Its plain CVR is conversions divided by impressions; **CVR (clicks)** uses destination clicks. Its standard **6-second video views** can include a qualifying engagement before that duration, so the metric is not a pure watch-time count. [Basic metrics, October 2025](https://ads.tiktok.com/resources/help/article/basic-data?lang=en); [Video metrics, November 2025](https://ads.tiktok.com/resources/help/article/video-play?lang=en).

**Analyst definitions for ExcerLock, 2026-10-16:** CPM = spend/impressions × 1,000; destination CTR = destination clicks/impressions; CPI = spend/attributed installs; cost per trial = spend/attributed trial starts; paid CAC = spend/attributed new payers; cohort ROAS = attributed revenue for a stated cohort age/spend. Label any “hook rate” by the exact view metric and denominator used. Revenue must specify gross versus net and observed versus predicted. These are calculation conventions, not benchmark targets.

TikTok's iOS real-time reporting requires eligibility and compatible data sharing; its page distinguishes this reporting from SKAN and says disabling SKAN removes that campaign's SKAN data from TikTok and MMP reporting. Faster numbers are not automatically independently verified incremental customers. [iOS real-time reporting, August 2026](https://ads.tiktok.com/resources/help/article/about-ios-real-time-conversion-reporting?lang=en).

### 20. The audience brief needs an adult paid-acquisition interpretation

The brief includes girls and women aged 16–30, but TikTok restricts detailed targeting for minors, including gender and interests, across listed markets. Its weight-management policy restricts weight-loss and muscle-gain claims to adults and prohibits body shaming and guaranteed transformations. The minors policy adds category restrictions. [Under-18 targeting, October 2026](https://ads.tiktok.com/resources/help/article/about-advertising-to-people-under-the-age-of-18?lang=en); [Weight and body image, September 2026](https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-weight-management?lang=en); [Protecting minors, October 2026](https://ads.tiktok.com/resources/help/article/protecting-minors-on-tiktok-advertising-initiatives?lang=en).

**Judgment:** Start adult-only, emphasizing consistency, chosen-app boundaries and moving more. Do not promise fat loss, an ideal body or improved worth. This follows both campaign constraints and the app's actual demonstrated mechanism; audience interest in fat loss is not evidence the app causes a weight outcome.

## Disagreements and changes to keep in view, 2024–2026

| Advice or change | What the evidence actually supports | How to act |
|---|---|---|
| “Lowest cost” / Maximum Delivery versus Maximum Results; Cost Cap versus Target Cost per Result | The September 2026 general bidding page uses the newer labels, while older indexed versions use the older ones. The volume-versus-cost-target distinction persists. [Current bidding](https://ads.tiktok.com/resources/help/article/bidding-strategies?lang=en), September 2026. | Read the strategy description and campaign eligibility rather than assuming a tutorial's button labels are current. This research did not establish the exact global rollout date for each rename. |
| “Every campaign needs 50 conversions to exit learning” | The live generic page says volatility often declines after about 25 results or 7 days; the August troubleshooting and Smart+ pages retain 50-event language. These statements concern different indicators and may also reflect uneven documentation updates. [Learning](https://ads.tiktok.com/resources/help/article/learning-phase?lang=en), June 2026; [troubleshooting](https://ads.tiktok.com/resources/help/article/troubleshooting-auction-ad-delivery-solutions?lang=en), August 2026. | Use the actual campaign status, event volume and mature economics. Do not promise a fixed exit or stable CPA after a calendar deadline. |
| “Always set daily budget to this one CPA multiple” | TikTok's general budget table distinguishes installs and deeper events. Another August page says 10 conversions and then describes that same formula as reaching 50, without explaining the time basis. [Budget tips](https://ads.tiktok.com/resources/help/article/bidding-budget-solutions-drive-tiktok-auction-ad-performance?lang=en), August 2026. | Treat the inconsistent sentence as a documentation defect; do not turn it into a mathematical rule. Match guidance to the actual campaign type. |
| “Raise budgets by exactly 20%” | General bidding guidance says increases of at least 20% after learning; July Budget says no more than 30% after learning and 40% during learning; August budget tips allow a 50% range after learning. [Bidding best practices](https://ads.tiktok.com/resources/help/article/best-practices-for-bidding-strategies?lang=en), August 2026; [Budget](https://ads.tiktok.com/resources/help/article/budget?lang=en), July 2026; [Budget tips](https://ads.tiktok.com/resources/help/article/budget-best-practices?lang=en), August 2026. | There is no well-supported universal magic increment here. Prefer modest, infrequent changes and watch cohort economics, within the authorized ceiling. |
| “Use many groups to test creative” | The June 2025 creative guide recommends diversified groups. Current delivery troubleshooting recommends consolidating groups with similar targeting. Smart+ changes who allocates and tests. [Creative](https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en), June 2025; [troubleshooting](https://ads.tiktok.com/resources/help/article/troubleshooting-auction-ad-delivery-solutions?lang=en), August 2026. | Distinct groups can answer distinct questions; duplicates on a small budget mostly fragment evidence. |
| “iOS cannot use VBO” / “Smart+ iOS supports all VBO features” | October 2026 VBO docs support iOS, but the August Smart+ App matrix still lists VBO only for Android. [VBO](https://ads.tiktok.com/resources/help/article/value-based-optimization-app?lang=en), October 2026; [Smart+ App](https://ads.tiktok.com/resources/help/article/about-smart-plus-app-campaigns), August 2026. | Distinguish broader app-campaign support from the Smart+ path; verify current app/account eligibility before choosing a strategy. |
| “All iOS results are only delayed SKAN totals” | August 2026 documentation describes eligible iOS real-time reporting through listed MMPs or the TikTok SDK. It does not guarantee a cold-start app is eligible. [iOS reporting](https://ads.tiktok.com/resources/help/article/about-ios-real-time-conversion-reporting?lang=en), August 2026. | Record the reporting source and compare mature cohorts; do not combine incompatible reporting views. |
| “Creator Marketplace instructions are the current workflow” | Current advertiser and creator documentation centers TikTok One. This lane did not establish a single worldwide retirement date for all older Marketplace interfaces. [Advertisers](https://ads.tiktok.com/resources/help/article/about-tiktok-one?lang=en), June 2026; [creators](https://ads.tiktok.com/resources/help/article/about-tiktok-one-for-creators?lang=en), April 2026. | Use TikTok One's current regional project flow. Keep contractual usage rights and authorization records independently. |
| “A respected agency article must have current prices and product settings” | CTC's legacy guide still states a $500 campaign minimum and discusses older product surfaces. The current official budget page instead gives the creation thresholds discussed above. [CTC guide](https://commonthreadco.com/blogs/coachs-corner/tiktok-ecommerce-business-strategy), publication date not established, captured 2026-10-16; [official Budget](https://ads.tiktok.com/resources/help/article/budget?lang=en), July 2026. | Keep the useful native-content reasoning, discard the legacy pricing as a setup authority. This is why a recently crawled article is not necessarily recently written. |

## What this means for ExcerLock

The recommendations and all proposed quantities in this section are **my judgment as of 2026-10-16**, not a platform guarantee or a measured ExcerLock result. The starting geography below assumes US availability; replace it with the actual launch market if necessary.

### Prepare one measurable experiment

Before approving spend, verify App Store availability, pricing and trial terms, creator access and the specific behavior that can be filmed. The repository's [product record](../../../core/product.md) says these need current-build verification. Show selected apps being restricted, not the whole phone. Do not imply the different walking and gym conditions can all be combined.

Validate the install/first-open path and useful in-app events: authorization completed, first restriction configured, first successful exercise-based unlock, trial started, purchase and refund. The unlock is a candidate activation event, not proof of revenue. The app-implementation and privacy decisions belong in the app/measurement lane; this report does not certify tracking readiness.

Use a single initial acquisition setup:

- **Objective:** App promotion for the actual iOS app; one supported optimization event.
- **Structure:** one Smart+ App campaign if eligible and its controls fit the plan; otherwise one manual campaign with one broad acquisition ad group. Do not add a separate retargeting or CBO structure at the outset.
- **Audience:** US, English, adult-only. In manual delivery, initially test women in the available age bands closest to the adult audience brief; document the actual bands rather than claiming an exact 18–30 boundary. With automation, verify which restrictions are binding.
- **Bidding:** Maximum Results initially. Reconsider Target Cost per Result or value optimization after establishing historical acquisition economics and confirming iOS eligibility.
- **Identity:** select Spark or non-Spark for the initial Smart+ campaign, since its captured matrix disallows mixing them. Use authorized creator posts if available; otherwise start with truthful brand content. Do not double the campaign count merely to test identity immediately.

The settings rationale comes from [Smart+ App, August 2026](https://ads.tiktok.com/resources/help/article/about-smart-plus-app-campaigns), [AEO bidding, August 2026](https://ads.tiktok.com/resources/help/article/available-bid-strategies-for-app-event-optimization?lang=en), and [broad targeting, April 2025](https://ads.tiktok.com/resources/help/article/broad-targeting?lang=en). The proposed structure is deliberately a small experiment, not compliance with every larger-account volume recommendation.

### Budget a test whose limitations are explicit

**Proposed exploratory range:** $75–$150/day for 7 days, or $525–$1,050 media spend. If the captain wants to follow the general no-history install recommendation more closely, propose $200/day for 7 days, or $1,400, instead. These are alternatives for approval, not instructions to spend. Creator fees and production are separate. The $200 official recommendation comes from [budget best practices, August 2026](https://ads.tiktok.com/resources/help/article/budget-best-practices?lang=en); the other amounts and durations are my proposed planning scenarios, 2026-10-16.

**Illustrative arithmetic, not benchmarks:** If CPI were $3–$8, a $100 daily budget would yield roughly 12–33 installs/day. If trial CPA were $15–$30, it would yield roughly 3–7 trials/day. Those hypothetical inputs show why a small test may reveal creative and activation problems without resolving purchase profitability. They are not observed TikTok fitness-app prices. Increasing the budget to force learning is inappropriate if the business cannot afford the experiment.

Before launch, the captain should approve both a total spending ceiling and the acceptable mature acquisition cost. Calculate allowable CAC from conservative net subscription receipts after platform fees, refunds and variable costs over a chosen payback period. Derive allowable trial CPA by multiplying that CAC by the observed trial-to-paid rate. Treat predicted renewals conservatively until there is cohort history. This is my economic decision framework, 2026-10-16.

### Make a small set of genuinely different demonstrations first

**Proposed production batch:** six usable assets from three concepts, with two executions of each; hold additional edits in reserve. These are concept directions, not finished hooks or scripts:

| Concept | What the viewer needs to understand | Useful execution contrast |
|---|---|---|
| Chosen-app restriction leads into a walk | The tempting app is selected by the user; the verified walking condition changes access. | Creator with readable phone proof versus direct screen demonstration with narration. |
| Step-goal follow-through | The app links a chosen step target to access to selected apps. | An ordinary routine diary versus a concise explanation of the same real mechanism. |
| Gym follow-through | One verified gym condition, such as arrival, changes access. | Creator explaining their use case versus visible product proof in the gym routine. |

Choose only mechanisms confirmed in the current build. Use commercially cleared audio, readable captions, safe framing and real product footage. Ask creators for honest demonstrations and raw footage rather than invented success stories. Do not make body-transformation promises. The production quantity is my proposal; the underlying platform direction is supported by [Smart+ best practices, August 2026](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en) and [body-image policy, September 2026](https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-weight-management?lang=en).

### Read results as a chain

This diagnostic table is **analyst judgment, 2026-10-16**. Each row is a hypothesis to investigate, not a single-cause diagnosis.

| Pattern | First investigation | Decision implication |
|---|---|---|
| Little or no spend | Approval status, dates, app/campaign eligibility, signal setup, bid realism, audience constraints | Fix delivery before judging the product or creative. |
| Spend and impressions, weak early attention | Opening visual, comprehensibility, creator delivery, relevance | Replace the opening or test a different concept. |
| Good attention, few destination clicks | Whether the mechanism and benefit are clear; CTA; profile versus destination interactions | More entertainment alone may not increase installs. |
| Destination clicks, few installs | App Store link, country/device availability, store page, message match | Inspect the store path and measurement. |
| Installs, little setup or first unlock | Permission friction, onboarding, product reliability, expectation mismatch | Do not celebrate CPI while activation fails. |
| Activated users, few trials | Paywall timing, price, explanation of value | Investigate the product funnel before changing targeting. |
| Trials, few mature paid conversions | Trial eligibility, duration, cohort age, cancellation, billing | Wait for maturity and calculate paid CAC. |
| Improving platform ROAS, weak receipts or cohort retention | Attribution windows, view-through contribution, duplicate claims, modeled values, gross/net definition | Reconcile reporting before scaling. |

Record spend, reach, impressions, frequency, destination clicks, the precisely defined video metrics, installs, activations, trials and purchases by date and creative. Keep both ad-platform and subscription/backend views with their reporting basis. Review cohort ages at day 1, 3 and 7, plus a later checkpoint after the actual trial and payment cycle mature; those checkpoints are my proposal, not an assumption about ExcerLock's trial length. Compare creatives using comparable settings and exposure; mark those with insufficient delivery as inconclusive. Definitions: [basic metrics, October 2025](https://ads.tiktok.com/resources/help/article/basic-data?lang=en); [video metrics, November 2025](https://ads.tiktok.com/resources/help/article/video-play?lang=en).

### Connect this to the existing creator dashboard

**Concrete proposed extension, not implemented:** Add a paid-usage review card to the existing approval inbox. Link the creator and deliverable IDs to the asset, post URL, authorization period, usage agreement, approved claims and the captain's creative verdict. A scheduled job should flag upcoming rights expiry and missing measurement snapshots. Store campaign/ad IDs and paid-performance snapshots in an independent paid-media module, then connect them through an adapter under `integrations/`, outside both sections. The creator section continues owning creator relationships and deals; the paid-media module owns spend and experiment decisions.

Start with read-only CSV imports if an API adds unnecessary work. Show mature trial and payer costs beside the creator asset, and feed the winning problem/proof pattern into the next brief. Keep organic and paid outcomes separate. This reuses the dashboard's generic inbox extension and existing approval workflow described in [creator operations](../../../sections/creators/README.md), while preserving the repository's module boundaries. No new tracker, job, deployment or account connection was created in this research task.

## Open questions and missing coverage

- Is ExcerLock currently installable in the intended market, and what are its actual subscription, trial and refund economics?
- Which activation and revenue events are already implemented, validated and available to TikTok? What reporting and attribution setup will the app-UA lane recommend?
- Does this app qualify for iOS real-time reporting? Which cost controls and value options appear for its actual campaign path? The public docs cannot establish account-specific eligibility, and no account was accessed.
- Does Smart+ App's iOS VBO limitation still apply to this account despite the broader October VBO changes? The captured documentation has different scopes and update dates.
- Which exact learning criterion and budget-change guidance applies in the live interface? Public documents disagree; the report does not invent a universal reconciliation.
- Which creator assets already include suitable paid rights, usable authorization and cleared audio? Is the creator's approved caption final?
- What share of attributed results would be incremental? No holdout, lift experiment or independent ExcerLock paid data exists in this lane.
- What cost per mature payer is attainable for an iOS app with this precise offer? Public creative-tool metrics and agency ecommerce case studies do not answer that.
- What is the current prevalence of each creative pattern among direct competitors? This lane covers fundamentals and tool interpretation; it did not inspect an ad-library sample or watch competitor videos.
- How do the proposed concepts perform when adequately funded? They remain hypotheses, not “winning ads.”

## Source register

All sources below were read on 2026-10-16. **O = official platform documentation**, strong for settings and definitions, moderate for generalized performance advice; **P = practitioner/agency**, useful operational perspective, lower confidence for self-reported outcomes. “Last updated” is a page label, not proof of the date a feature launched. Where no publication date was established, that uncertainty is retained. Raw folder names are relative to `../raw/tiktok-fundamentals/`.

| ID | Source URL / title | Author | Date | Type | Trust and limitation | Raw folder |
|---|---|---|---|---|---|---|
| S01 | [About Smart+ App Campaigns — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/about-smart-plus-app-campaigns) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `01-smart-app/` |
| S02 | [About Auction Ads — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/about-auction-ads?lang=en) | TikTok for Business | April 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `02-about-auction-ads/` |
| S03 | [Available bidding methods — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/bidding-methods?lang=en) | TikTok for Business | August 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `03-bidding-methods/` |
| S04 | [Available Bidding Strategies — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/bidding-strategies?lang=en) | TikTok for Business | September 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `04-bidding-strategies/` |
| S05 | [Best practices for bidding strategies — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/best-practices-for-bidding-strategies?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `05-best-practices-for-bidding-strategies/` |
| S06 | [About Budget — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/budget?lang=en) | TikTok for Business | July 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `06-budget/` |
| S07 | [Tips to select your budget  — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/budget-best-practices?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `07-budget-best-practices/` |
| S08 | [About Learning Phase — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/learning-phase?lang=en&redirected=2) | TikTok for Business | June 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `08-learning-phase-faq/` |
| S09 | [Troubleshooting Auction Ad Delivery — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/troubleshooting-auction-ad-delivery-solutions?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `09-troubleshooting-auction-ad-delivery-solutions/` |
| S10 | [Best practices Smart+ App — TikTok for Business](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `10-best-practices-for-smart-plus-app-campaigns/` |
| S11 | [About Value-based Optimization for app — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/value-based-optimization-app?lang=en) | TikTok for Business | October 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `11-value-based-optimization-app/` |
| S12 | [Bidding strategies for app VBO — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/available-bidding-strategies-for-value-based-optimization-for-app?lang=en) | TikTok for Business | October 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `12-available-bidding-strategies-for-value-based-optimization-for-app/` |
| S13 | [Available bid strategies for App Event Optimization — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/available-bid-strategies-for-app-event-optimization?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `13-available-bid-strategies-for-app-event-optimization-canonical/` |
| S14 | [About Spark Ads](https://ads.tiktok.com/resources/help/article/spark-ads?lang=en) | TikTok for Business | June 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `14-spark-ads-canonical/` |
| S16 | [How to create Spark Ads for Manual and Search Campaigns in TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/spark-ads-creation-guide?lang=en) | TikTok for Business | June 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `16-spark-ads-creation-guide-canonical/` |
| S17 | [About Top Ads](https://ads.tiktok.com/resources/help/article/top-ads?lang=en) | TikTok for Business | May 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `17-top-ads-canonical/` |
| S18 | [How to use the Top Ads Dashboard](https://ads.tiktok.com/resources/help/article/how-to-use-the-top-ads-dashboard?lang=en) | TikTok for Business | May 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `18-how-to-use-the-top-ads-dashboard-canonical/` |
| S19 | [About Creative Center](https://ads.tiktok.com/resources/help/article/creative-center?lang=en) | TikTok for Business | July 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `19-creative-center-canonical/` |
| S20 | [Creative best practices for performance ads](https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en) | TikTok for Business | June 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `20-creative-best-practices-canonical/` |
| S21 | [About Split Testing — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/split-testing?lang=en) | TikTok for Business | January 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `21-split-testing-canonical/` |
| S22 | [About TikTok One for advertisers](https://ads.tiktok.com/resources/help/article/about-tiktok-one?lang=en) | TikTok for Business | June 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `22-about-tiktok-one-canonical/` |
| S23 | [How to create a new Creator marketing project in TikTok One](https://ads.tiktok.com/resources/help/article/how-to-create-a-new-creator-marketing-project-in-tiktok-one?lang=en) | TikTok for Business | March 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `23-how-to-create-a-new-creator-marketing-project-in-tiktok-one-canonical/` |
| S24 | [iOS real-time reporting — TikTok for Business](https://ads.tiktok.com/resources/help/article/about-ios-real-time-conversion-reporting?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `24-about-ios-real-time-conversion-reporting-canonical/` |
| S29 | [Bidding & Budget Tips for Performance — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/bidding-budget-solutions-drive-tiktok-auction-ad-performance?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `29-bidding-budget-solutions-drive-tiktok-auction-ad-performance-canonical/` |
| S30 | [Business Resource Center](https://ads.tiktok.com/resources/help/article/about-advertising-to-people-under-the-age-of-18?lang=en) | TikTok for Business | October 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `30-minors/` |
| S32 | [Your TikTok Ecommerce Guide: Tactics + Examples to Succeed](https://commonthreadco.com/blogs/coachs-corner/tiktok-ecommerce-business-strategy) | Nay Cook / Common Thread Collective | Date not established; captured 2026-10-16 | P · practitioner guide | Medium for creative reasoning; legacy prices and interfaces are outdated. | `32-practitioner-ctc/` |
| S34 | [About Interest Targeting — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/interest-targeting?lang=en) | TikTok for Business | July 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `34-interest/` |
| S35 | [How to promote an app using Value-based Optimization — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/how-to-promote-an-app-using-value-based-optimization?lang=en) | TikTok for Business | October 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `35-vbo-setup-canonical/` |
| S37 | [Weight Management — TikTok Advertising Policies](https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-weight-management?lang=en) | TikTok for Business | September 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `37-weight-policy/` |
| S38 | [Business Resource Center](https://ads.tiktok.com/resources/help/article/protecting-minors-on-tiktok-advertising-initiatives?lang=en) | TikTok for Business | October 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `38-minor-policy/` |
| S39 | [Stickerbox Paid Social Campaign Drives a Revenue Surge](https://houseofmarketers.com/stickerbox-ai-influencer-marketing-case-study/) | House of Marketers (no individual byline established) | Modified 2026-04-27 (metadata); publication date not established | P · agency case study | Medium for described process; low for unaudited, blended commercial results. Physical consumer device, not a subscription app. | `39-house-app/` |
| S40 | [How to Build a Creator Content System for Your Brand](https://commonthreadco.com/blogs/tactics/build-creator-content-system) | Common Thread Collective | Date not established; captured 2026-10-16 | P · practitioner video summary page | Medium for production workflow; promotional summary only, no transcript read. | `40-ctc-creator/` |
| S41 | [Basic metrics and definitions in TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/basic-data?lang=en) | TikTok for Business | October 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `41-metrics/` |
| S42 | [Video play metrics](https://ads.tiktok.com/resources/help/article/video-play?lang=en) | TikTok for Business | November 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `42-video-metrics/` |
| S43 | [About TikTok One for creators](https://ads.tiktok.com/resources/help/article/about-tiktok-one-for-creators?lang=en) | TikTok for Business | April 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `43-one-transition/` |
| S45 | [Business Resource Center](https://ads.tiktok.com/resources/help/article/broad-targeting?lang=en) | TikTok for Business | April 2025 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `45-broad/` |
| S46 | [How to set up Campaign Budget Optimization — TikTok Ads Manager](https://ads.tiktok.com/resources/help/article/campaign-budget-optimization?lang=en) | TikTok for Business | August 2026 | O · official platform doc | High for stated mechanics; recommendations are platform guidance. | `46-cbo/` |
