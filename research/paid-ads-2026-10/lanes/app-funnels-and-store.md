# App funnels and the App Store: the path from an ad to a paying ExcerLock user

Research captured **2026-10-16**. My recommendation is to establish a working **ad → relevant App Store page → focused onboarding → Apple subscription purchase → successful app setup** before adding a web checkout. A web funnel is a worthwhile later experiment when it has a specific job, such as explaining the product or qualifying intent. It is not an automatic improvement in acquisition economics.

## Coverage and how to read the evidence

I read **33 distinct primary-source pages or published video transcripts**, including Apple documentation, TikTok documentation, RevenueCat's subscription reports and experiment, Adapty's report, and Superwall's testing guidance and case study. These are documents, not 33 independent studies: related Apple pages overlap, and vendors have commercial incentives. The source table identifies each one. Video evidence means the published transcript was read; I did not watch the footage.

Raw HTML, extracted text/transcripts, URLs, timestamps, and fetch results are saved under `../raw/app-funnels-and-store/`. Folder numbers match source IDs below. The old Apple analytics URL failed extraction; its embedded redirect led to a readable current overview. The failed original is excluded from the read count and preserved under limitations. No accounts were accessed or changed, no ads were launched, no paid scraping was used, and no image-generation API was used.

Labels distinguish **Official** rules/features, **Data** from observational vendor datasets, **Experiment** from an individual reported test, **Practitioner** interpretation, and **Judgment** for my recommendations. A publication year is not necessarily the data year. Undated live documentation is cited with its read date; that is not a claimed publication date.

## The 20 things that matter most

### 1. Buy paying users, then work backward through the funnel

**Judgment / arithmetic.** An ad's installation cost is only the entry price. The economics also depend on whether people understand the app, finish setup, start a trial, pay, renew, and obtain a useful result. A screenshot change that increases downloads can lose money if it attracts people expecting a free product.

Use an explicitly defined chain:

`ad click → store exposure → first-time download → first open → onboarding → offer → trial or direct payment → first charge → renewal`

Not every download requires a product-page visit, and not every payer takes a trial. Keep those branches separate rather than forcing every user into a neat but false sequence. Apple's acquisition presentation explains downloads, redownloads and store impressions as different measures; its subscription definitions separately identify trial starts, paid starts, and renewals. **Official, read 2026-10-16:** [Apple acquisition transcript](https://developer.apple.com/videos/play/tech-talks/110365/), [subscription metric definitions](https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions).

**Illustration, not benchmark:** spend $1,000 for 200 first opens; 20 start trials and 8 eventually pay. Cost per open is $5, cost per trial $50, and paid-user acquisition cost $125. Improving trial starts alone is insufficient if fewer trials become paid subscriptions.

### 2. The store page should finish the particular promise the ad makes

**Official.** Apple recommends UI-based screenshots, allows up to **10**, and says the first **one to three** can appear in search results when there is no preview, depending on orientation. Each later image should communicate a benefit or feature. **Live documentation read 2026-10-16:** [Creating your product page](https://developer.apple.com/app-store/product-page/).

**Judgment.** Someone who clicked a walking demonstration should immediately recognize that same mechanism on the store page. “Fitness motivation” is too vague to establish why this app is different. Show the selected apps, the chosen movement condition, and the resulting access behavior. Put proof ahead of a collage of secondary features. Screenshots must reflect the actual build, including any limitation that would change the purchase decision.

For ExcerLock, a walking page and a gym page can share the brand while explaining different conditions. Do not show an invented rule that combines multiple conditions merely because it makes a more exciting diagram.

### 3. An App Store preview is a product demonstration with different constraints from a social ad

**Official.** Apple permits up to **three previews per supported language**, each up to **30 seconds**. They autoplay muted; a poster frame covers cases where autoplay does not occur. Apple's guidance says to use on-device footage, remain inside the app rather than filming hands using a phone, avoid regional prices, and disclose subscriptions or login when required. **Read 2026-10-16:** [App previews](https://developer.apple.com/app-store/app-previews/).

**Judgment.** Reuse the explanation from a good creator ad, but make a separate store asset. Start with a readable product state and show the causal sequence. Test screenshots alone against screenshots plus a preview; video production quality is not evidence of a conversion lift. For ExcerLock, confirm which lock screen and system interfaces are acceptable preview footage before submitting them. A creator walking outside belongs naturally in the ad; a store preview must satisfy Apple's preview requirements.

### 4. Product Page Optimization is a controlled experiment; comparing two unrelated pages is not

**Official.** Apple's Product Page Optimization overview supports **up to three treatments** against the original, using icons, screenshots and previews. It describes random allocation, persistent treatment exposure, **one test at a time**, a **90-day** maximum, and a **90% confidence** recommendation before adopting a result. Alternate icons require inclusion in the app binary. **Read 2026-10-16:** [Product Page Optimization overview](https://developer.apple.com/app-store/product-page-optimization/).

**Judgment.** Start with the control and one substantially different screenshot proposition. Low traffic divided among many treatments creates more uncertainty, not more learning. Keep the advertising mix stable enough to understand the result. A test estimates the effect on the audience included in it; it does not certify every future campaign.

A newer Apple analytics help page describes Bayesian reasoning and confidence intervals, but also contains conflicting instructions about simultaneous tests and extending duration. Do not reconcile that by inventing capabilities. See the documentation conflict below. **Official, read 2026-10-16:** [PPO analytics help](https://developer.apple.com/help/app-store-connect-analytics/acquisition/product-page-optimization/).

### 5. Custom Product Pages carry different ad promises to different store experiences

**Official.** Apple's current setup guide allows **70 Custom Product Pages (CPPs)** with unique URLs and localized screenshots, previews, promotional text and keywords. Pages require approval; analytics become available after **five first-time downloads**. Keywords can route relevant organic searches to a CPP. An approved deep link can take people pressing Open into specific app content on **iOS/iPadOS 18 or later**. **Read 2026-10-16:** [CPP configuration](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions).

**Judgment.** Create a small number of meaningfully different pages. A walking ad should lead to the walking page, then walking setup; a gym ad should lead to gym setup. The destination must retain required permissions and purchase disclosures. A deep link is not permission to skip essential setup, nor proof that every installation/open path preserves context.

Do not create a separate page for every tiny hook variation. Use a stable page identifier for each product promise and preserve the mapping in your research and campaign records.

### 6. CPP support and a CPP conversion lift are different claims

**Official.** Apple supports sharing CPP URLs in social ads and using page identifiers in StoreKit-rendered ads. It reports an average **2.5 percentage-point** conversion increase over a **1.6%** default-page average, described as **156% relative improvement**. The page does not establish a randomized causal estimate for ExcerLock. **Read 2026-10-16:** [Apple CPP overview](https://developer.apple.com/app-store/custom-product-pages/).

**Official.** TikTok documents CPPs for App promotion campaigns, including install, registration and retargeting, and specified Smart+ configurations. The URL contains a **PPID**, the product-page identifier. **Page dated April 2025, read 2026-10-16:** [TikTok iOS custom product pages](https://ads.tiktok.com/help/article/about-ios-custom-product-pages?lang=en).

**Judgment.** Test the destination from the rendered ad and verify the actual page, country and language. For Meta, this research establishes Apple's capability, but does not verify the current Meta account's field names or campaign eligibility. Do not convert a CPP URL into a generic website campaign just to force a destination. Validate the relevant app-ad destination settings before spending.

### 7. CPPs and Product Page Optimization solve different problems

**Official.** Apple's CPP Tech Talk explains that referrals sent to a custom page do not enter the default page's Product Page Optimization test. CPPs segment the destination; PPO randomizes alternate default-page assets. That older transcript also contains outdated page limits and referral-only positioning, so use current setup documentation for current capabilities. **Read 2026-10-16:** [Get started with custom product pages](https://developer.apple.com/videos/play/tech-talks/10886/).

**Judgment.** “Walking CPP converted better than gym CPP” may simply mean the walking ad attracted better prospects. To test a destination, compare equivalent traffic and record the split method. If the ad and page change together, call it a test of the whole journey. It cannot tell you which component caused the difference.

Keep the default page strong too. People who remember the name and search later may encounter a different experience from those who tap the original ad.

### 8. Onboarding should build confidence and help people reach a real outcome

**Practitioner.** Superwall's Clear 30 case study says a paywall changed from a feature carousel to a preview of the first week, with reported conversion moving from **20% to 30%**. The article also reports monthly revenue moving from **$10,000 to $30,000 over eight weeks** while several funnel elements changed. These are founder/vendor-reported results, not audited evidence that one screen tripled revenue. **Jordan Morgan, 2025-11-19:** [Clear 30 case study](https://superwall.com/blog/how-two-founders-tripled-their-app-revenue-in-8-weeks).

**Judgment.** ExcerLock's first experience should answer: What will be restricted? What movement makes it available? Why does this permission matter? What happens if setup fails? Then demonstrate a feasible success. Asking about goals helps only if the answer changes setup or the explanation. Long onboarding is neither inherently better nor inherently worse; a question earns its place by helping the user or improving a measured outcome.

### 9. Hard paywalls are worth testing, but cross-app benchmarks do not prescribe the answer

**Data.** RevenueCat's **2026** report covers **115,000+ apps and $16 billion+ revenue**, principally **2025** performance. Median download-to-paid conversion by day **35** is **10.7% for hard-paywall apps versus 2.1% for freemium**. That is download-to-paid, not trial-to-paid. The dataset excludes apps without sufficient activity and compares different apps rather than randomized monetization models. **Read 2026-10-16:** [RevenueCat 2026 report and methodology](https://www.revenuecat.com/state-of-subscription-apps/).

**Judgment.** Test an understandable offer near the end of onboarding against a brief, useful demonstration before the offer. Decide what access a non-subscriber retains. A hard paywall can still offer a free trial; “hard” describes access gating, not whether there is a trial. Judge the result by retained net revenue per acquired user and successful setup, not merely more taps on Subscribe.

### 10. Trial length trades time to experience value against time to collect and learn

**Data.** RevenueCat 2026 reports median trial-to-paid conversion of **25.5% for trials of four days or less**, **37.4% for five–nine days**, and **42.5% for 17–32 days**. Those are observational groups. It also says **55% of cancellations of three-day trials happen on day zero**; that is a share of cancellations, not all trial users. **Read 2026-10-16:** [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/).

**Official.** Apple's introductory offers include free trials of **three days, one week and two weeks**, among other supported durations; a person can redeem only **one introductory offer per subscription group**. Check eligibility when displaying the offer. **Read 2026-10-16:** [Introductory offers](https://developer.apple.com/help/app-store-connect/manage-subscriptions/set-up-introductory-offers-for-auto-renewable-subscriptions).

**Judgment.** Begin with a one-week trial if the build can show meaningful benefit during ordinary walking and gym routines. Test three days later against that baseline. A longer trial may make the product easier to evaluate but delays cash and mature purchase cohorts. Do not declare the shorter trial a winner while the longer trial is still running. Existing users who have exhausted trial eligibility need an accurate alternative offer.

### 11. Pricing tests should optimize money retained per acquired user

**Data.** Adapty's **2026** report analyzes **2025** activity from **16,000+ apps and $3 billion+ gross revenue**, mostly iOS. It reports annual trials associated with better subscriber LTV in Health & Fitness, while direct buyers are worth more in some other categories. It also finds weekly-with-trial offers strong on payer LTV. These comparisons are not proof that switching billing frequency causes the result. Its methodology excludes insufficient-data apps, making this a selected sample. **Read 2026-10-16:** [Adapty report](https://adapty.io/state-of-in-app-subscriptions-report/).

**Judgment.** A higher payer LTV can coexist with fewer payers. Test price with the same offer layout and audience, then calculate revenue per assigned new user after fees/refunds. ExcerLock sits across fitness and app-blocking utilities, so neither category is an exact benchmark. Start with a clear annual and monthly choice. Weekly billing deserves a test only if its retention, refund, support and customer-value results justify it; an attractive first-charge metric is not enough.

### 12. Paywall timing, copy, price, packaging and design are separate experimental levers

**Practitioner.** Superwall's framework separates price/packaging, design, messaging, placement/frequency and personalization. It recommends isolating a broad lever rather than changing everything simultaneously. Its illustrative test prices are examples, not benchmarks. **Jordan Morgan, 2025-05-22:** [How Superwall tests paywalls](https://superwall.com/blog/how-we-test-paywalls-at-superwall-and-how-you-can-too/).

**Judgment.** First fix comprehensibility: what starts now, when payment occurs, how much is billed, and how cancellation works. Then test a large proposition difference, placement, trial length, or price in a deliberate order. Assign users persistently and retain the original assignment for analysis, including users who abandon before seeing the offer. Otherwise an apparently stronger paywall can merely be receiving a more selected audience.

Do not change screenshots, onboarding, trial length, annual price and ad audience in the same week and attribute the improvement to button color.

### 13. Subscription clarity is part of the funnel, not fine print after the sale

**Official.** Apple requires clear subscription duration and benefits, prominent full renewal price, a sign-in/restore path, and Terms of Use and Privacy Policy links. The billed amount should be the most prominent pricing element; the annual total should not be obscured by a monthly equivalent. Apple also describes **70% developer proceeds in the first paid subscription year and 85% afterward**, before applicable taxes, under the standard structure. **Read 2026-10-16:** [Apple subscription guidance](https://developer.apple.com/app-store/subscriptions/).

**Judgment.** The offer should say the trial duration, the actual renewal amount and period, and what happens after cancellation. Show trial messaging only to eligible people. A trial-start lift earned through confusion can turn into early cancellations, refunds, bad reviews and expensive support. Verify restore, cancellation management, payment failure and entitlement expiry on a real device before paying to acquire more users.

### 14. “Web-to-app” can mean three materially different journeys

**Practitioner.** Daphne Tideman's guide distinguishes payments made before installation from payments made after users arrive in the app, and discusses storytelling, experimentation, attribution and operational trade-offs. **Published 2025-12-11; page visibly updated 2026-05-01; read 2026-10-16:** [Web-to-app guide](https://www.revenuecat.com/blog/growth/web-to-app-funnels/).

**Judgment.** Name the route explicitly:

| Journey | What you are testing | Main risk to measure |
|---|---|---|
| Ad → web explanation → store → in-app purchase | Whether more education improves downstream conversion | Extra web abandonment outweighs better qualification |
| Ad → web quiz/offer → web payment → install/redeem | Whether pre-selling improves contribution per ad click | People pay but fail to install, redeem or activate |
| Ad → store → app → external web checkout → app | Whether a different checkout improves contribution | Existing purchase intent is lost during the handoff |

A successful route in one row does not establish the others. Web checkout also needs subscription identity, receipt/entitlement reconciliation, refunds, tax handling, support and recovery from a closed browser. These are part of the experiment's costs.

### 15. A quiz is useful when answers change the experience or help the user decide

**Practitioner.** Tideman's teardown describes Calm's goal-based quiz, with deeper personalization for sleep, and Photoroom's alternative: deliver a useful free web result before offering an account/trial. The article is an observed funnel analysis, not access to those companies' conversion experiments. **Published 2026-01-12; visibly updated 2026-05-01; read 2026-10-16:** [Five funnel examples](https://www.revenuecat.com/blog/growth/web-to-app-funnel-examples/).

**Judgment.** For ExcerLock, a short selector could distinguish walking, a step target and gym use, explain the chosen condition, and carry that intent into setup. Ask only questions that support a decision. Do not copy a long weight-loss questionnaire when the product cannot prescribe a weight-loss plan. Demonstrating blocking requires native capabilities; the web should explain them honestly rather than pretending to run the actual lock mechanism.

### 16. Saving a store commission does not guarantee more take-home revenue

**Experiment.** RevenueCat's Dipsea experiment assigned approximately **3,100 new US users per main variant**. Its later table reports **27.0% initial conversion for IAP-only versus 18.1% for web-only**, and **6.3% versus 5.3% paid-user conversion**. The take-home table estimates **$2.09 per assigned user for IAP-only versus $1.96 for web-only**, modeling **30% Apple and 6% web costs**; the Small Business scenario favors IAP more strongly. These are short-window results in one reader app, published initially **2025-05-14**, with a later three-week update; read **2026-10-16**. [Full experiment](https://www.revenuecat.com/blog/growth/iap-vs-web-purchases-conversion-test/).

**Judgment.** This is app-to-web checkout evidence, not a cold web quiz experiment. The article's headline, summary and tables use slightly different rounded comparisons; use the named variant and table rather than repeating one universal “web loses X%” claim. Actual net contribution depends on your fee status, price, conversion, renewals and service costs.

### 17. Check Apple's storefront rules and your actual commission before designing web payments

**Official.** Apple's **2025-05-01** guideline update changed US-storefront external-purchase links. The current guidelines say external purchase-link entitlements are not required for US-storefront buttons/links/calls to action. Other storefronts have different restrictions and programs. Guideline **3.1.3(b)** permits access to externally acquired subscriptions for multiplatform services subject to its IAP condition. **Read 2026-10-16:** [Dated change](https://developer.apple.com/news/?id=9txfddzf), [current rules, sections 3.1.1 and 3.1.3](https://developer.apple.com/app-store/review/guidelines/).

**Official.** The Small Business Program offers a **15% commission** to eligible enrolled developers, with a **$1 million proceeds** threshold and associated-account conditions. Enrollment is not assumed. **Read 2026-10-16:** [Program rules](https://developer.apple.com/app-store/small-business-program/).

**Judgment.** US ad geography and App Store storefront are different concepts. Make purchasing behavior depend on the permitted storefront implementation, not merely where the ad ran. Do not infer ExcerLock qualifies as a reader app because Dipsea does. Keep native IAP as the baseline and verify applicable agreements, fees and rules again immediately before implementation.

### 18. Make onboarding editable and measurable, but do not buy tools instead of fixing a broken journey

**Official vendor documentation.** Superwall supports branching onboarding, permission steps, paywalls and flow analytics. **Read 2026-10-16:** [Onboarding Flows](https://superwall.com/docs/dashboard/guides/using-superwall-for-onboarding-flows). RevenueCat's Funnels launch describes web journeys, checkout and Redemption Links that connect a web purchase to app access; its launch roadmap is historical, not proof of today's feature availability. **Niklas Winkels, 2026-03-17:** [Funnels launch](https://www.revenuecat.com/blog/company/funnels-public-beta).

**Vendor observational claim.** Superwall reports **40 million+ paywall opens, February–May 2026**, with multi-page onboarding paywalls converting **12.41% versus 9.07%** for single-page. Assignment and audience equivalence are not established on the sales page. **Undated page read 2026-10-16:** [Onboarding optimization](https://superwall.com/solutions/onboarding-flow-optimization).

**Judgment.** Use the app's existing subscription infrastructure first. Pick tools for reliable assignment, events, rollback and entitlement handling. Do not install several overlapping paywall products just to reproduce a vendor screenshot. Validate redemption and restore failures as carefully as the happy path.

### 19. In-App Events can support a real scheduled experience; they are not spare advertising space

**Official.** Apple defines In-App Events as timely experiences discoverable on product pages, search and editorial surfaces. Events can last up to **31 days** and be promoted up to **14 days** in advance; the event deep link should reach the experience while preserving necessary onboarding. **Read 2026-10-16:** [In-App Events](https://developer.apple.com/app-store/in-app-events/).

**Judgment.** A genuine scheduled walking challenge could connect creator content with returning-user engagement. It requires an actual in-app experience; changing the store card to “download today” does not create an event. Treat events as a later retention/discovery experiment after the ordinary acquisition path works. Count new users, returning users and revenue separately; avoid presenting reactivated subscribers as entirely new paid acquisition.

### 20. Apple Search Ads can capture intent created elsewhere, but its install metric is not a paid-user metric

**Official.** Apple's manual campaign guidance separates brand, category, competitor and discovery themes, using exact match for the first groups and broad/Search Match for discovery with negative keywords. CPPs can provide keyword-aligned ad variations. **Read 2026-10-16:** [Campaign structure](https://ads.apple.com/app-store/best-practices/campaign-structure), [ad variations](https://ads.apple.com/app-store/help/ads/0077-create-ad-variations).

**Official, changed recently.** Apple announced **Maximize Conversions on 2026-02-25**. The current guide defines its target CPA as cost per **install**, uses automated bids and Search Match, and recommends budget for at least **five conversions daily**. It charges for taps. This does not mean the system optimizes subscription profit. **Read 2026-10-16:** [Dated announcement](https://ads.apple.com/news), [current bidding guide](https://ads.apple.com/app-store/best-practices/maximize-conversions).

**Judgment.** Use search as a complementary intent test. Social ads may cause people to search later; branded search can capture that demand and then claim the last measurable touch. Keep brand and non-brand results separate and assess total new payers rather than adding every platform's claimed conversions together.

## What changed, what conflicts, and what is easy to misread

| Issue | Current evidence and interpretation |
|---|---|
| Old CPP limit and referral-only advice | Apple's older Tech Talk says **35** and positions CPPs around referrals. Its current guide says **70**, while WWDC25 introduced keyword-based search discovery. Use the current guide for capability; use the older talk for conceptual distinctions. **Read 2026-10-16:** [older talk](https://developer.apple.com/videos/play/tech-talks/10886/), [current guide](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions), [WWDC25 transcript](https://developer.apple.com/videos/play/wwdc2025/328/). |
| “Apple always bans external purchase links” | Outdated for the US storefront after the **2025-05-01** update. It is also wrong to treat that update as worldwide permission. **Read 2026-10-16:** [Apple announcement](https://developer.apple.com/news/?id=9txfddzf), [live review rules](https://developer.apple.com/app-store/review/guidelines/). |
| “Apple always takes 30%” | The actual rate depends on enrollment, subscription tenure, storefront and applicable agreements. Use the relevant rules, not the maximum rate in a web-funnel pitch. **Read 2026-10-16:** [Small Business Program](https://developer.apple.com/app-store/small-business-program/), [subscription economics](https://developer.apple.com/app-store/subscriptions/). |
| Trial-duration fashion changed | RevenueCat **2025**, describing **2024**, says **52%** of trials were five–nine days. The newer report describes a shift toward shorter trials; sample changes limit year-to-year comparisons. Popularity does not establish optimality. **Read 2026-10-16:** [2025 report](https://www.revenuecat.com/state-of-subscription-apps-2025/), [2026 report](https://www.revenuecat.com/state-of-subscription-apps/). |
| “Use weekly plans” versus “annual fits fitness” | Adapty's strong weekly payer-LTV comparisons coexist with category differences and annual-trial findings. This is not a controlled switch test. Acquisition conversion and payer LTV need to be combined before choosing a billing model. **2026 report, read 2026-10-16:** [Adapty](https://adapty.io/state-of-in-app-subscriptions-report/). |
| Short onboarding versus more explanation | Superwall's multi-page association and Clear 30's reported success support hypotheses about explanation, not a rule to add screens. Both have selection and reporting limitations. **Read 2026-10-16:** [2026 vendor observation](https://superwall.com/solutions/onboarding-flow-optimization), [2025-11-19 case](https://superwall.com/blog/how-two-founders-tripled-their-app-revenue-in-8-weeks). |
| Apple documentation conflicts with itself | The PPO overview says **one test**, up to **90 days**. The newer analytics FAQ says separate tests can run simultaneously and suggests extending duration, while also mentioning descriptions among testable elements. These instructions conflict. Use the dedicated setup/overview constraints for planning and verify the actual UI before implementation; no UI was accessed here. **Read 2026-10-16:** [overview](https://developer.apple.com/app-store/product-page-optimization/), [analytics FAQ](https://developer.apple.com/help/app-store-connect-analytics/acquisition/product-page-optimization/). |
| Apple Ads instructions written before automation | Manual keyword structure remains documented, but **2026-02-25** introduced Maximize Conversions. A current plan must state which bidding model it assumes. Apple's **2026-06-08** creative-freedom announcement says “later this year”; it does not by itself verify rollout to this account. **Read 2026-10-16:** [Apple news](https://ads.apple.com/news). |
| Article update dates are ambiguous | RevenueCat's web guide visibly says updated **2026-05-01**, while downloaded structured metadata says modified **2026-09-11**. Several articles share that metadata date. Treat it as a site modification timestamp, not proof every claim was revalidated then. **Read 2026-10-16:** [guide](https://www.revenuecat.com/blog/growth/web-to-app-funnels/); both representations are preserved in raw HTML. |

## What I would do for ExcerLock

Everything in this section is **my judgment as of 2026-10-16**, a proposed starting experiment rather than a benchmark, spending authorization or an assertion about the current app build.

### Establish the product and store baseline first

The repository's `core/product.md` describes selected-app blocking and several distinct movement conditions, but does not freshly verify release status, prices, the permission flow or unlock timing. Obtain those facts from the app owner/build before making a download promise. Never advertise that the entire phone locks, or promise a particular fat-loss result.

Build a strong default page and two CPPs: **walking** and **gym**. For each, prepare roughly five screenshots in this order: the central mechanism, choosing apps, choosing the condition, reaching the condition/access state, and an honest explanation of setup/control. Adapt to the real interface. Make one short, silent-readable preview per proposition if accurate footage is available; test its contribution later rather than holding launch research hostage to elaborate production.

Keep a direct native-purchase journey as control. Introduce the condition the visitor came for, explain the relevant permissions, show enough product value to make the offer understandable, present the subscription, then complete required setup and confirm success. Test offer placement relative to a real demonstration; do not charge people for a misleading impression that setup already succeeded.

Apple restricts use of HealthKit and health/fitness data for advertising and marketing. **Official, read 2026-10-16:** [Review Guidelines 5.1.2–5.1.3](https://developer.apple.com/app-store/review/guidelines/). Consequently, review the event payload design before implementation: do not export step totals, Health-derived goal completion, gym coordinates, camera data, or selected-app identities to ad networks or marketing dashboards. Product success can be investigated in the app's own appropriately governed product analytics; even derived health signals should not automatically become marketing conversion events.

### Make these creatives and their destinations first

These are concept briefs, not finished scripts or new house hooks:

| Asset to produce | Promise to substantiate | Destination |
|---|---|---|
| Creator demonstrates selected apps restricted, then available while walking | Active-walking behavior, if verified in the build | Walking CPP and walking explanation |
| Creator demonstrates reaching a chosen step goal | A separate goal-completion condition | Walking CPP with the step-goal condition clearly distinguished |
| Creator shows the configured gym condition and resulting access | Exactly the gym condition the build supports | Gym CPP |
| Clean screen recording with concise captions | What the user chooses and what ExcerLock changes | Matching CPP; separate compliant edit for a store preview |
| Founder explains why they built the app, followed by product proof | The mechanism and the intended habit benefit | Strong default page or best-matched CPP |

Use real proof and truthful customer experiences. Do not copy a competitor's success percentage, fabricate testimonials, or imply that a web quiz diagnoses someone's health or prescribes weight loss.

### Budget and sequence

I would ring-fence an initial **$1,000–$3,000 media learning budget**, approximately **$50–$100 a day** while spending, with a pre-agreed stop point. These are planning amounts I recommend, not platform minimums and not a promise of statistically conclusive results. Creative production and software costs are additional.

Concentrate the social portion on one platform and one country first so it feeds the same funnel. Coordinate the exact campaign settings with the targeting/UA lanes. Do not divide this small budget among Meta, TikTok, multiple countries, several paywalls and a web funnel simultaneously.

If additional search learning is useful, reserve **$200–$500 within that total**, or run it sequentially after social. Start with narrow category intent and a separate brand bucket if there is meaningful search demand. Treat phrases such as “app blocker” and “screen time blocker” as keyword hypotheses, not verified search-volume findings. Add competitor and broad discovery testing only when you can interpret search terms and paid-user outcomes. A small manual search test may be more diagnostic than an automated install campaign; neither is guaranteed cheaper.

A practical test order:

1. Fix broken links, availability, payments, restore and permissions before paid traffic.
2. Send a coherent ad proposition to its matching page and establish baseline funnel counts.
3. Test one substantial store proposition or onboarding improvement. Use PPO for default-page assets and equivalent traffic for a CPP comparison.
4. Test trial length, then pricing/packaging, with stable assignment and mature cohorts.
5. Only then test a web explanation or web checkout against the native control. Start with the simplest web route that answers a demonstrated objection.

The test period should include full trial maturation and a defined renewal observation window. Exhausting a daily budget or seeing an attractive install cost does not make the cohort mature.

### Measure and diagnose the whole path

Store daily counts and user-cohort outcomes with `source`, `campaign/ad ID`, `creative ID`, `CPP ID`, `country/storefront`, `onboarding variant`, `paywall variant`, `product/price`, `trial eligibility` and `cohort start date`, where reliably available. Do not invent a user-level CPP attribution bridge when the platform provides only aggregate page reporting.

| Stage | Measurement and denominator | What a weak result suggests |
|---|---|---|
| Ad → destination | Clicks and verified destination arrivals, within each system's measurement limits | Delivery, redirect, availability or link issue |
| Store exposure → download | Apple's reported conversion definition, plus first-time downloads and page views separately | Message mismatch, unclear proof, unsuitable audience or store availability |
| First open → onboarding completion | Completed users / first opens assigned to that experience | Confusing explanation, technical issue or excessive setup |
| Offer exposure → trial/direct purchase | Separate eligible trial starts, direct paid starts and offer views | Value, trust, price, eligibility or checkout friction |
| Trial → first charge | First charges / trials whose evaluation window has elapsed | Value not demonstrated, wrong audience, cancellation or billing failure |
| Acquired user → retained proceeds | Net receipts and refunds per original acquisition cohort | Weak recurring value or misleading acquisition/offer |
| Web payer → app access | Redemption and access success / web payers | Broken identity, install handoff or entitlement fulfillment |

Apple's acquisition transcript defines headline store conversion as **total downloads / unique impressions**, with total downloads including redownloads; that differs from a manually computed page-view-to-download ratio. **Official, read 2026-10-16:** [Acquisition definitions](https://developer.apple.com/videos/play/tech-talks/110365/). The current overview confirms that denominator and says usage/engagement reporting includes only users who opted into sharing diagnostics and usage information. Treat engagement comparisons as a measured subset. **Official, read 2026-10-16:** [Current Analytics overview](https://developer.apple.com/app-store-connect/analytics/). Label the denominator on every chart. Use counts as well as rates, distinguish new and returning users, and reconcile finances against actual subscription receipts rather than merely summing platform-reported purchases.

For a web experiment, compare net contribution **per original assigned visitor or ad click**, including people who never pay or install. Track processor costs, taxes where borne by the business, refunds, chargebacks, software and support. Report cash received alongside subscription revenue and renewals. A higher checkout conversion among the few people who reach checkout does not establish a better funnel.

### Connect this to the existing operations system

Propose a small acquisition-results module owning experiment definitions and aggregated funnel/cohort outcomes. A composition adapter outside the sections can attach a creator deliverable ID to a creative ID, destination/CPP and experiment ID, then expose the result through the creators dashboard's existing generic inbox extension.

The approval card would show the proposed creative, its exact destination, the trial/price being promised, budget cap and decision rule. A scheduled import would attach available store/subscription aggregates and show “waiting for trial cohort” rather than declaring an early winner. Creator renew/fix/cut decisions could then consider paid-user results alongside views, with attribution confidence and missing data visible. Keep sensitive product data out of this dashboard. This is a proposal only; no integration or scheduled job was created in this research lane.

## Open questions and missing coverage

- Is ExcerLock currently live and approved in the intended storefronts? What are the actual paid products, trial eligibility rules, supported devices and demonstrated movement conditions?
- What happens when users deny or later revoke Screen Time, Health, motion, location or camera permissions? Where do actual users abandon, and can the offer precede permission failure without misleading them?
- Is the developer enrolled in the Small Business Program? What commission, processor costs, tax responsibilities and external-purchase terms actually apply to the intended implementation/storefronts?
- What baseline first-open, offer, paid conversion, refund and renewal counts exist? None of the external medians establishes an ExcerLock CAC ceiling or optimal price.
- Does the existing app stack preserve campaign context, experiment assignment and web entitlement identity reliably? Can it restore access after reinstall, account changes and interrupted redemption?
- Which current Meta app-campaign types support the intended CPP destination in this account? No authenticated Ads Manager inspection or live click test was performed. TikTok support was read in official docs, not exercised.
- Will the same page/onboarding improvements hold for cold paid traffic, younger users and the intended female audience? The aggregate reports do not isolate ExcerLock's audience.
- What is the incremental value of branded Apple search after social exposure? Attribution reports alone cannot resolve it.
- Which Apple PPO interface constraints currently apply? The official pages conflict, as recorded above. Also, the CPP overview mentions pre-order support while the setup help describes a Ready for Distribution prerequisite; verify the actual eligibility if this app is pre-release. **Read 2026-10-16:** [CPP overview](https://developer.apple.com/app-store/custom-product-pages/), [setup help](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions).
- Apple's `https://developer.apple.com/app-store/measuring-app-performance/` failed Readability extraction from a very short response, and returned empty content to the browser reader. Search snippets were not counted as a full read. Inspection of the saved HTML revealed a meta/JavaScript redirect to `/app-store-connect/analytics/`; that destination was fetched and read successfully as source 34. The original failure is retained, not counted as a read.
- No live competitor onboarding/paywall purchases, independently audited web-funnel profitability study, or long-term follow-up to the Dipsea test was obtained. This lane uses primary published material, not private cohort exports. The Adapty report's text was readable, but I did not manipulate its interactive chart filters; no selected-filter results are claimed. Paid-report PDFs were not required or purchased.

## Source table

All sources below were read **2026-10-16**. “Undated” means no reliable article publication date was visible. Raw folders contain `source.bin`, `content.md` and `result.json`; video folders contain the page's published transcript in `content.md`. IDs identify the corresponding raw folder, not a separate source-count multiplier. High trust in a platform rule does not imply high trust in its marketing uplift claims.

| ID | Source / URL | Author / publisher | Publication or update date | Type | Trust and use |
|---|---|---|---|---|---|
| 01 | [State of Subscription Apps 2026](https://www.revenuecat.com/state-of-subscription-apps/) | RevenueCat; Jacob Eiting introduction | 2026; primarily 2025 data | Data report | Strong aggregate subscription evidence; selected customer sample, observational comparisons. |
| 02 | [State of Subscription Apps 2025](https://www.revenuecat.com/state-of-subscription-apps-2025/) | RevenueCat | 2025; principally 2024 performance | Data report | Strong historical comparison; different sample/year limits trend comparisons. |
| 03 | [Creating your product page](https://developer.apple.com/app-store/product-page/) | Apple Developer | Undated live doc | Official platform doc | High for asset guidance and limits; recommendations do not guarantee conversion. |
| 04 | [App previews](https://developer.apple.com/app-store/app-previews/) | Apple Developer | Undated live doc | Official platform doc | High for preview requirements, presentation and production constraints. |
| 05 | [Product Page Optimization](https://developer.apple.com/app-store/product-page-optimization/) | Apple Developer | Undated live doc | Official platform doc | High for dedicated setup constraints; conflicts with ID 33 preserved. |
| 06 | [In-App Events](https://developer.apple.com/app-store/in-app-events/) | Apple Developer | Undated live doc | Official platform doc | High for event purpose, timing, links and reporting; no guaranteed distribution. |
| 07 | [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Apple Developer / App Review | Live version; no single section date assigned | Official platform doc | Highest-priority source for platform review rules; agreements/storefront exceptions still matter. |
| 08 | [Updated guidelines now available](https://developer.apple.com/news/?id=9txfddzf) | Apple Developer | 2025-05-01 | Official platform announcement | High for date and geographic scope of US change; use ID 07 for current wording. |
| 09 | [Auto-renewable subscriptions](https://developer.apple.com/app-store/subscriptions/) | Apple Developer | Undated live doc | Official platform doc | High for offer presentation, subscription economics and implementation guidance. |
| 10 | [Small Business Program](https://developer.apple.com/app-store/small-business-program/) | Apple Developer | Undated live doc | Official platform doc | High for eligibility/commission; ExcerLock enrollment unknown. |
| 11 | [Configure CPP versions](https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions) | Apple App Store Connect Help | Undated live doc | Official platform doc | High for current CPP mechanics; eligibility conflict with overview noted. |
| 12 | [Create ad variations](https://ads.apple.com/app-store/help/ads/0077-create-ad-variations) | Apple Ads | Undated live doc | Official platform doc | High for CPP-backed ad variations and fallback behavior. |
| 13 | [Web-to-app complete guide](https://www.revenuecat.com/blog/growth/web-to-app-funnels/) | Daphne Tideman / RevenueCat | 2025-12-11; visible update 2026-05-01; metadata 2026-09-11 | Respected practitioner / vendor-hosted guide | Useful detailed trade-offs; not independent of a web-billing vendor. |
| 14 | [Five web-to-app examples](https://www.revenuecat.com/blog/growth/web-to-app-funnel-examples/) | Daphne Tideman / RevenueCat | 2026-01-12; visible update 2026-05-01; metadata 2026-09-11 | Practitioner teardown | Useful documented journeys; not verified company conversion results or current live walkthroughs by this researcher. |
| 15 | [Web versus IAP conversion experiment](https://www.revenuecat.com/blog/growth/iap-vs-web-purchases-conversion-test/) | Jacob Eiting / RevenueCat | Initial 2025-05-14; later three-week update; metadata 2026-09-11 | Vendor-run experiment | Stronger than anecdote: assignments/counts/tables. Single owned app, short horizon, variant/pricing and summary inconsistencies limit generalization. |
| 16 | [How Superwall tests paywalls](https://superwall.com/blog/how-we-test-paywalls-at-superwall-and-how-you-can-too/) | Jordan Morgan / Superwall | 2025-05-22 | Practitioner / vendor playbook | Useful test framework; advertised average uplift not adopted as benchmark. |
| 17 | [State of In-App Subscriptions 2026](https://adapty.io/state-of-in-app-subscriptions-report/) | Adapty; Vitaly Davydov introduction | 2026; 2025 data | Data report | Useful second provider; mostly iOS, gross revenue, sufficient-data selection and correlation caveats. |
| 18 | [Apple Ads campaign structure](https://ads.apple.com/app-store/best-practices/campaign-structure) | Apple Ads | Undated live doc | Official platform doc | High for manual structure; vendor best practices, not a minimum setup for every budget. |
| 19 | [TikTok iOS CPPs](https://ads.tiktok.com/help/article/about-ios-custom-product-pages?lang=en) | TikTok for Business | Updated April 2025 | Official platform doc | High for published support; account configuration not exercised; performance language is aspirational. |
| 21 | [Apple Ads news](https://ads.apple.com/news) | Apple Ads | Entries include 2026-02-25 and 2026-06-08 | Official platform announcements | High for announcement timing; future-tense releases do not establish account rollout. |
| 22 | [Set up introductory offers](https://developer.apple.com/help/app-store-connect/manage-subscriptions/set-up-introductory-offers-for-auto-renewable-subscriptions) | Apple App Store Connect Help | Undated live doc | Official platform doc | High for supported durations, setup and subscription-group eligibility. |
| 23 | [Clear 30 funnel case](https://superwall.com/blog/how-two-founders-tripled-their-app-revenue-in-8-weeks) | Jordan Morgan; Asher Hurstman and Thatcher Kloff interview / Superwall | 2025-11-19 | Practitioner interview recap / vendor case | Medium: concrete reported changes; results self-reported, unaudited, several simultaneous changes. |
| 24 | [Using Flows for onboarding](https://superwall.com/docs/dashboard/guides/using-superwall-for-onboarding-flows) | Superwall Docs | Undated live doc | Official vendor product doc | High for vendor's described capabilities; no outcome guarantee. |
| 25 | [Onboarding flow optimization](https://superwall.com/solutions/onboarding-flow-optimization) | Superwall | Undated; observations February–May 2026 | Vendor data claim / product page | Medium: large exposure count, but assignment, denominator and controls not fully established. |
| 26 | [RevenueCat Funnels beta launch](https://www.revenuecat.com/blog/company/funnels-public-beta) | Niklas Winkels / RevenueCat | 2026-03-17; visible update 2026-03-19; metadata 2026-09-11 | Official vendor launch / product doc | High for launch description; roadmap and beta availability are historical. |
| 27 | [Subscription metric definitions](https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions) | Apple App Store Connect Analytics Help | Undated live doc | Official platform doc | High for distinctions among offers, paid starts and renewals; not the acquisition denominator reference. |
| 28 | [What's new in App Store Connect](https://developer.apple.com/videos/play/wwdc2025/328/) | Apple App Store Connect Engineering; Chinedu and Michael | WWDC25, June 2025 | Official video, published transcript read | High for what changed in that release; current doc supersedes launch-time wording. |
| 29 | [CPP overview](https://developer.apple.com/app-store/custom-product-pages/) | Apple Developer | Undated live doc | Official platform doc / platform marketing data | High for feature descriptions; medium for uplift claims without experimental methodology. |
| 30 | [Get started with CPPs](https://developer.apple.com/videos/play/tech-talks/10886/) | Savannah Wu and Michelle Van Regenmorter / Apple | Historical Tech Talk; exact publication day not established | Official video, published transcript read | High for conceptual distinction; outdated limit/search statements explicitly superseded. |
| 31 | [Measure acquisition with App Analytics](https://developer.apple.com/videos/play/tech-talks/110365/) | Nick, App Analytics product manager / Apple | Historical Tech Talk; exact publication day not established | Official video, published transcript read | High for metric reasoning; not used for current store/device reach counts. |
| 32 | [Maximize Conversions](https://ads.apple.com/app-store/best-practices/maximize-conversions) | Apple Ads | Undated live doc; launch dated by ID 21 | Official platform doc | High for install objective, bidding and target CPA definition; not paid-user optimization. |
| 33 | [PPO analytics and FAQ](https://developer.apple.com/help/app-store-connect-analytics/acquisition/product-page-optimization/) | Apple App Store Connect Analytics Help | Undated live doc | Official platform doc | Mixed: helpful statistical definitions, conflicting setup claims; do not use alone for test constraints. |

| 34 | [Current Analytics overview](https://developer.apple.com/app-store-connect/analytics/) | Apple Developer | Undated live doc | Official platform doc | High for current acquisition definitions and opt-in usage-data limitation; recovered destination of ID 20. |

**Failed original fetch, excluded from source count:** ID 20, [Apple measuring app performance](https://developer.apple.com/app-store/measuring-app-performance/), Apple, undated official overview; raw Readability extraction failure and empty browser extraction on 2026-10-16. The embedded redirect was followed successfully as ID 34. The failure record is preserved. No conclusion of “no guidance exists” is drawn from it.
