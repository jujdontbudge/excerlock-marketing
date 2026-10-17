# App UA mechanics: buying customers for an iOS subscription app

Research captured **2026-10-16**. Lane: `app-ua-mechanics`. No ad accounts were accessed or changed; no ads were launched and no paid scraping was used.

The practical starting point is a measurable app funnel, a tested subscription-event connection, and a concentrated test on one network. Buying cheap installs is useful only if enough of those people activate, pay, and stay. Web-to-app can improve education and measurement, but adds another product funnel to build and operate. It is a separate experiment, not an automatic upgrade.

**Evidence:** 31 substantive public sources read: official Apple, Meta and TikTok material; AppsFlyer, Adjust and Singular documentation; RevenueCat and Adapty reports; Superwall’s experiment summary; and a historical Jon Loomer explanation. Their individual URLs, dates, limitations and archive locations are below. Search snippets were discovery aids, not counted as full reads. An additional AppsFlyer benchmark page returned no numeric data and is recorded as missing coverage. Product facts come from the local `core/product.md`, whose current-build verification limits still apply.

**How to read this:** “Official” describes a platform’s own rules or supported behavior. “Dataset” describes observed customers of a vendor, not a universal market sample. “Judgment” and “illustration” are my recommendations and calculations, dated 2026-10-16, not measured ExcerLock results. Undated live docs carry their capture date rather than an invented publication date.

## The 18 things that matter most

### 1. Separate the route people take from the event the network optimizes

An app campaign generally sends people toward the App Store and optimizes against app installs or eligible in-app events. A web-to-app campaign starts on your website: education or quiz, offer, perhaps web payment, then installation and account/entitlement handoff. A web landing page that merely forwards to the store is another route again; it does not create a measurable web purchase by itself. TikTok explicitly says Traffic campaigns can reach newer iOS devices but have incomplete app conversion reporting. A click objective is therefore not a substitute for a properly connected App Promotion campaign. **Official:** [TikTok dedicated-campaign setup](https://ads.tiktok.com/resources/help/article/how-to-create-an-ios-14-5-dedicated-campaign?lang=en), captured 2026-10-16.

Choose the route according to what the audience needs to understand before buying, then choose the deepest useful event you can deliver and measure. RevenueCat’s current web-funnel guide starts with audience, promise, proof, offer and primary outcome. **Practitioner/vendor guide:** [campaign design](https://www.revenuecat.com/guides/web-to-app-funnels/campaign), undated, captured 2026-10-16. **Judgment:** ExcerLock’s selected-app lock/unlock demonstration is simple enough to test direct-to-app first.

### 2. ATT, Apple attribution, Meta AEM and an MMP solve different problems

ATT is permission for tracking across other companies’ properties and access to the advertising identifier. It is not the subscription permission, Screen Time permission, or Health permission. Apple’s privacy-preserving attribution does not itself require an ATT prompt; other tracking in the same app still can. **Official:** [Apple privacy and data use](https://developer.apple.com/app-store/user-privacy-and-data-use/) and [ad attribution](https://developer.apple.com/app-store/ad-attribution/), undated live docs, captured 2026-10-16.

SKAdNetwork (SKAN) and AdAttributionKit (AAK) report privacy-limited attribution signals. Meta’s Aggregated Event Measurement (AEM) is Meta’s separate measurement system. An MMP is a service that assembles attribution, cost and event data across networks. None of these means every individual non-consenting user becomes traceable. **Vendor documentation:** [AppsFlyer AEM](https://support.appsflyer.com/hc/en-us/articles/19228737402129-Meta-Ads-Aggregate-Event-Measurement-AEM-for-iOS), updated 2026-05-25; [Singular MMP definition](https://www.singular.net/glossary/mobile-measurement-partner-mmp/), modified 2026-06-23.

### 3. Apple attribution is delayed and sometimes deliberately incomplete

SKAN’s conversion windows are days **0–2, 3–7 and 8–35** after first launch. Postbacks arrive after a further randomized **24–48 hours** for the first window and **24–144 hours** for later windows. Fine conversion values are limited to the first postback; later ones use coarse values. The lowest privacy tier receives only the first postback and no conversion value. A null value therefore means information was withheld or unavailable, not necessarily that the user did nothing. **Official:** [Apple multiple conversion windows](https://developer.apple.com/documentation/storekit/receiving-postbacks-in-multiple-conversion-windows), undated, captured 2026-10-16; full Apple documentation JSON archived as source 03.

**Judgment:** Same-day SKAN cost-per-trial is an incomplete observation. Wait for the relevant reporting window, then wait separately for the actual trial to finish before evaluating paid conversion. Faster platform reporting does not make a future subscription charge happen sooner.

### 4. A conversion schema is a compressed description of user quality

The app encodes useful early behavior into conversion values; the network cannot receive the full product analytics history through an Apple postback. At small volume, coarse states need to remain interpretable when detailed values disappear. AppsFlyer supports event, engagement and revenue schemas and warns that only one SDK should control conversion-value updates. **Vendor documentation:** [SKAN solution guide](https://support.appsflyer.com/hc/en-us/articles/360011420698-SKAdNetwork-SKAN-solution-guide), updated 2026-06-11.

**Judgment:** Design a small schema around generic onboarding and subscription states, then validate what the chosen network actually consumes. Do not let the Meta SDK, TikTok SDK and MMP independently write competing values. RevenueCat explicitly does not configure SKAN/AEM or update these values for you. **Vendor documentation:** [RevenueCat Meta integration](https://www.revenuecat.com/docs/integrations/attribution/meta-ads), undated, captured 2026-10-16.

### 5. AAK builds on SKAN; it has not made all SKAN setup advice disappear

Apple describes AAK as building on SKAN, with installation attribution on supported operating systems and click-through re-engagement support beginning with **iOS 18**. Apple tells advertisers to ask networks whether they support AAK. That is different from assuming every Meta/TikTok optimization path has migrated. **Official:** [Apple ad attribution](https://developer.apple.com/app-store/ad-attribution/), captured 2026-10-16.

**Judgment:** Ask the selected MMP and network which protocol, SDK version and conversion schema apply to the campaign you can actually create. Avoid rebuilding around an acronym alone. Existing SKAN troubleshooting remains relevant where the network still documents a SKAN route.

### 6. Meta AEM and SKAN can coexist

AppsFlyer says an eligible Meta app campaign selecting AEM can use AEM and SKAN together; selecting SKAN alone limits it to SKAN. Event eligibility must be checked in Meta Events Manager. AppsFlyer also documents data-sharing prerequisites and warns that sharing must comply with platform policies. **Vendor implementation documentation:** [AppsFlyer AEM](https://support.appsflyer.com/hc/en-us/articles/19228737402129-Meta-Ads-Aggregate-Event-Measurement-AEM-for-iOS), 2026-05-25.

**Judgment:** “RevenueCat sent the event successfully” is only the first check. Confirm receipt, matching, AEM eligibility, availability as an optimization event, and eventual campaign attribution separately. Do not copy data-sharing toggles blindly: the implementation must respect actual consent and Apple’s rules. **Vendor documentation:** [RevenueCat integration](https://www.revenuecat.com/docs/integrations/attribution/meta-ads), captured 2026-10-16.

### 7. TikTok now has an eligible real-time iOS reporting path

TikTok’s **August 2026** documentation lists real-time iOS reporting through major MMPs, including AppsFlyer, Adjust and Singular, and through its App Events SDK **1.5.0 or above**. Its App Events API is listed as unavailable for this feature. App eligibility depends on sufficient signals. Eligible apps can opt out of SKAN reporting to remove the SKAN campaign quota, but then lose SKAN data in TikTok and MMP reporting for that route. **Official:** [iOS real-time reporting](https://ads.tiktok.com/resources/help/article/about-ios-real-time-conversion-reporting), updated August 2026.

This makes “TikTok iOS always means waiting only for SKAN” outdated. It does not establish that a brand-new ExcerLock app qualifies, or that modeled results equal independently verified incremental customers. **Judgment:** Keep Apple reporting as a comparison where supported; quota removal is not a reason for a small app to create more campaigns.

### 8. SDK-only is a real starting option; an MMP buys coordination

Meta documents direct SDK event collection. RevenueCat can forward subscription events to Meta while the Meta SDK supplies device-side install/activation signals. TikTok’s newer real-time documentation also explicitly supports its own SDK. An MMP is therefore not a universal prerequisite for buying an app ad. **Official/vendor:** [Meta iOS App Events](https://developers.facebook.com/docs/app-events/getting-started-app-events-ios/) and [RevenueCat](https://www.revenuecat.com/docs/integrations/attribution/meta-ads), captured 2026-10-16; [TikTok real-time](https://ads.tiktok.com/resources/help/article/about-ios-real-time-conversion-reporting), August 2026.

An MMP becomes useful when comparing channels, aggregating costs, operating deep links and managing Apple conversion schemas. It still applies attribution rules and models; “single source of truth” is a vendor description, not proof of causality. **Vendor:** [Singular MMP explanation](https://www.singular.net/glossary/mobile-measurement-partner-mmp/), modified 2026-06-23.

**Judgment:** With a small single-network test, use existing working infrastructure before buying another tool. Before sustained Meta-plus-TikTok spend, compare AppsFlyer, Adjust and Singular on actual required integrations, exportability, cost, support and privacy controls. Their live commercial quotes were not verified here.

### 9. Delivery, attribution and accounting need separate checks

RevenueCat forwards lifecycle events after receiving the provider identifiers it needs; it is not automatically the cross-network acquisition source. Its current guide recommends testing with a fresh customer after all identifiers and settings are present. A historical purchase made before setup is a poor integration test. **Vendor:** [getting started with attribution](https://www.revenuecat.com/docs/integrations/attribution/getting-started), captured 2026-10-16.

RevenueCat’s default Meta mapping sends `StartTrial` for trial starts and `Subscribe` for trial conversions, initial purchases **and renewals**. It warns that the Meta SDK and RevenueCat do not coordinate a shared event ID; sending the same purchase through both can double-count it. **Vendor:** [Meta event mapping and deduplication](https://www.revenuecat.com/docs/integrations/attribution/meta-ads), captured 2026-10-16.

**Judgment:** Assign one delivery owner per lifecycle event. Count unique first-time payers separately from renewal events. Check revenue, currency, trial price, refunds and restores before trusting ROAS. A free-trial start must not masquerade as cash collected.

### 10. Optimize for the deepest reliable event your budget can support

Install optimization finds likely installers; trial optimization finds likely trial starters; purchase optimization aims at eligible purchasers. These groups can overlap without being economically equivalent. TikTok supports Start Trial, Subscription and Purchase among its app events, and its SKAN AEO path unlocks after a corresponding event is received. That technical unlock is not evidence that there is enough volume for stable results. **Official:** [TikTok iOS bidding and optimization](https://ads.tiktok.com/resources/help/article/bidding-optimization-considerations-ios14?lang=en), August 2026. Meta’s SDK separately defines `StartTrial`, `Subscribe` and purchase events. **Official code:** [event names](https://github.com/facebook/facebook-ios-sdk/blob/main/FBSDKCoreKit/FBSDKCoreKit/AppEvents/FBSDKAppEventName.m), current branch captured 2026-10-16.

**Judgment:** Prefer trial optimization if trials are eligible, frequent enough, and predictive of payment. If they are too sparse, a tightly capped install test can reveal App Store and onboarding problems while still measuring downstream outcomes. Do not buy engagement merely to obtain a reassuring learning label. Purchase/value optimization becomes a stronger candidate once paid events and revenue are reliable and frequent.

### 11. There is no single “minimum budget to exit learning”

Three different constraints get confused:

| Constraint | Evidence and implication |
|---|---|
| Platform input minimum | TikTok’s live budget doc says daily campaign budget must exceed **$50**, and ad-group budget must exceed **$20**. These are interface floors, not proof of sufficient subscription conversions. [Official budget doc](https://ads.tiktok.com/resources/help/article/budget?lang=en), captured 2026-10-16. |
| Event-learning guidance | TikTok’s general learning doc says volatility typically declines after about **25 campaign results or 7 days**. Its Smart+ App best-practices page instead describes **7 days**, up to **50 conversion events**, and recommends Maximum Results daily budget of at least **10× historical CPA**. Different product documents do not give one universal exit guarantee. [General](https://ads.tiktok.com/resources/help/article/learning-phase?lang=en), June 2026; [Smart+ App](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en), undated in local extraction, captured 2026-10-16. |
| SKAN information density | TikTok recommends roughly **90 daily installs per SKAN AEO campaign** to reduce withheld conversion information. This is TikTok operational advice, not Apple publishing a fixed universal anonymity threshold. [AEO](https://ads.tiktok.com/resources/help/article/best-practices-for-app-event-optimization?lang=en), February 2025; [iOS considerations](https://ads.tiktok.com/resources/help/article/bidding-optimization-considerations-ios14?lang=en), August 2026. |

For Meta, Jon Loomer’s historical explanation describes approximately **50 desired actions per ad set in 7 days**. The official Meta learning page returned a title-only body in this research; I cannot certify that historical threshold as a universal October 2026 rule. **Historical practitioner:** [Loomer](https://www.jonloomer.com/facebook-ads-learning-phase/), 2020-era article, captured 2026-10-16; [official page, unreadable body](https://www.facebook.com/business/help/112167992830700).

**Illustration, 2026-10-16:** At an assumed $20 cost per trial, 50 weekly trials imply $1,000/week, about $143/day. At an assumed $80 per new payer, the same count implies $4,000/week. At an assumed $3 CPI, TikTok’s 90-install guidance implies $270/day. These are arithmetic scenarios, not recommended spend commitments. Consolidating is often more sensible than funding many separate learning pools.

### 12. Onboarding is part of the acquisition system

RevenueCat’s 2026 sample reports that **82.1% of Health & Fitness trial starts happen on day zero**. That is a share of eventual trial starts, not a share of all installs. **Dataset:** [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/), captured 2026-10-16.

**Judgment:** An ad promising app blocking must lead to a clear explanation of selected apps, required permissions, the movement condition and the paid offer. Measure where people abandon. Distinguish a permission refusal, a failed lock setup, an unexplained paywall and a payment failure. They require different fixes. Because the current product record lists multiple permission dependencies, a convincing ad can still acquire people who never reach usable setup. Product behavior and permission flow need current-build verification (`core/product.md`, read 2026-10-16).

### 13. Paywalls can move CAC as much as the ad does

Holding CPI constant, a better install-to-paid rate lowers acquisition cost per payer. RevenueCat’s 2026 report observes higher early paid conversion for hard-paywall apps than freemium apps, but these are different populations, not random assignment of one app’s users. Treat that as an experiment hypothesis. **Dataset:** [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/), captured 2026-10-16.

Superwall’s year-end review says multi-page paywalls and trial-explanation designs performed well in its experiments, while app-to-web checkout generally hurt initial conversion. It provides no common effect size or reproducible trial-level dataset. **Vendor observation:** [Superwall review](https://superwall.com/blog/superwall-ships-recap/), Jordan Morgan, 2025-12-05.

**Judgment:** First explain value and recurring terms clearly. Test one meaningful change when traffic allows: demonstration before offer, trial explanation, or price/plan presentation. Judge net proceeds per new user and payer quality, not trial-start lift alone.

### 14. Benchmarks are useful only with their denominator and population

| Metric | Observed benchmark | What it does and does not tell us |
|---|---|---|
| Download → trial | Health & Fitness median **6.9%**, trial starts measured within **30 days**. | Vendor subscription-app sample, not a Meta/TikTok-only US iOS cohort. [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/), captured 2026-10-16. |
| Trial → paid | Health & Fitness median **37.7%**; upper quartile above **51.4%**. | Compare completed/matured trial cohorts with similar plan, geography and duration. [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/), captured 2026-10-16. |
| Download → paid | Health & Fitness median **2.9%** by **day 35**, upper quartile above **6.2%**. | Includes paths beyond the trial funnel. Do not manufacture a forecast by multiplying unrelated medians. [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/), captured 2026-10-16. |
| Previous-year comparison | Health & Fitness trial → paid median **39.9%**. | A different report/sample; not evidence that an unchanged app’s performance necessarily declined. [RevenueCat 2025](https://www.revenuecat.com/state-of-subscription-apps-2025/), captured 2026-10-16. |
| Matched CPI / cost per trial | **Not established in this pass.** | AppsFlyer’s public US paid Health & Fitness page exposed a no-platform-data state rather than values. That is missing coverage. [Benchmark page](https://www.appsflyer.com/benchmarks/health___fitness/health/health___overall/united-states/paid/), read 2026-10-16. |

RevenueCat’s methodology includes apps using its platform with active subscription revenue and minimum activity thresholds. Platform, geography, price and access method matter; this is not a random sample of every launched app. **Dataset methodology:** [2026 report](https://www.revenuecat.com/state-of-subscription-apps/), captured 2026-10-16.

### 15. Translate CPI into payer economics before deciding it is cheap

**Illustration / planning sensitivity, 2026-10-16. All inputs below are assumptions, not market benchmarks:**

| Assumed CPI | Assumed install → trial | Assumed trial → paid | Derived cost/trial | Derived cost/new payer |
|---:|---:|---:|---:|---:|
| $2 | 5% | 30% | $40 | $133 |
| $3 | 10% | 40% | $30 | $75 |
| $5 | 15% | 50% | $33 | $67 |
| $8 | 5% | 30% | $160 | $533 |

`Cost/trial = CPI ÷ install-to-trial rate`. `Cost/payer = CPI ÷ (install-to-trial × trial-to-paid)`. These assume the same complete cohort, no direct purchases, and aligned attribution. They show why even a higher CPI can buy better customers. They are deliberately broad sensitivity cases, not a claim that ExcerLock should expect $2–$8 CPI.

**Illustration:** If net contribution per new payer within the chosen payback horizon were $40, and 10% started trials with 40% converting, break-even CPI would be $1.60 before any profit cushion. Change the assumed contribution or conversion rate and the ceiling changes. Without ExcerLock’s price, fees, refunds and retention, no honest profitable CPI target can be supplied.

### 16. Net contribution and payback matter more than dashboard ROAS

RevenueCat can forward gross or fee/tax-adjusted revenue. Apple’s Small Business Program offers an eligible, enrolled developer a **15%** commission rate; it is not automatic for every app. **Vendor/official:** [RevenueCat attribution setup](https://www.revenuecat.com/docs/integrations/attribution/getting-started) and [Apple Small Business Program](https://developer.apple.com/app-store/small-business-program/), captured 2026-10-16.

**Judgment:** Set a payback horizon and calculate collected proceeds minus refunds, store/payment charges and variable costs. Keep creative production and tooling costs visible alongside media CAC. Do not treat annual cash collected as monthly recurring cash, or projected renewals as already available ad budget. Early D7/D35 proceeds can help decisions; mature cohorts are needed for longer LTV estimates. An apparently strong gross ROAS can still be cash-negative.

### 17. Web funnels trade commission and measurement advantages for friction

Nathan Hudson’s guide describes more control over education, offer and checkout, plus web conversion measurement, but also installation handoff and additional funnel complexity. Some blanket language in this older article, such as app campaigns being unable to deep link to different journeys, needs qualifying against current Apple custom-product-page capabilities. **Practitioner:** [web-to-app pros and cons](https://www.revenuecat.com/blog/growth/the-pros-and-cons-of-web-to-app-funnels/), published 2024-07-23, modified 2026-09-11.

RevenueCat’s Dipsea experiment tested checkout choices **inside an existing app**. Its updated report says adding a web option produced roughly **93 cents per IAP-only dollar**, despite a **30%** store-fee comparison. That is evidence that payment friction can outweigh fee savings, not a direct test of cold-ad web quizzes. **First-party experiment:** [RevenueCat web versus IAP test](https://www.revenuecat.com/blog/growth/iap-vs-web-purchases-conversion-test/), published 2025-05-14, experiment update 2025-05-28.

Current Apple guidelines contain US-storefront exceptions for external purchase links; other storefront rules differ. **Official:** [App Review Guidelines, purchase-method sections](https://developer.apple.com/app-store/review/guidelines/), captured 2026-10-16. **Judgment:** If testing web later, measure web buyer → successful app login → entitlement active → retained payer. Count buyers who never install. Web payment is not equivalent to product activation.

### 18. Reconcile reports; do not add overlapping claims together

Adjust explains that attribution windows and attribution methods are configurable. RevenueCat’s Initial Conversion chart groups users by first-seen cohort and includes trial starts and some non-subscription purchases; it is not simply “cash-paying customers today.” **Vendor docs:** [Adjust windows](https://help.adjust.com/en/article/attribution-windows) and [RevenueCat Initial Conversion](https://www.revenuecat.com/docs/dashboard-and-metrics/charts/initial-conversion-chart), captured 2026-10-16.

**Judgment:** Keep separate columns for network-attributed, MMP-attributed, Apple aggregate and all-app financial results. Document date basis, timezone, click/view windows, event definition and gross/net basis before comparing. Never add Meta and TikTok’s self-attributed customers to claim unique acquired customers. A customer can be claimed by both. Blended proceeds are a useful business check, but organic activity makes before/after comparisons imperfect. Incrementality asks whether advertising caused additional customers; attribution asks who receives credit under a rule.

## Disagreements and changes to carry into a launch review

- **Learning guidance is product-specific and inconsistent.** TikTok’s June 2026 general doc uses approximately 25 results/7 days for reduced volatility, while its Smart+ App page still describes up to 50 events. The Smart+ page says iOS Target Cost per Result is “coming soon,” whereas August 2026 iOS docs describe support in relevant paths. Check available campaign settings before choosing a bid strategy; do not reconcile these into an invented universal rule. [General learning](https://ads.tiktok.com/resources/help/article/learning-phase?lang=en), June 2026; [Smart+ App guidance](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en), captured 2026-10-16; [iOS bidding](https://ads.tiktok.com/resources/help/article/bidding-optimization-considerations-ios14?lang=en), August 2026.
- **Smart+ no longer means only one rigid campaign structure.** TikTok’s upgraded experience permits different automation levels, multiple ad groups and different budget strategies. Old tutorials can describe a different interface. This does not mean a small app should use every structural option. [Official upgraded Smart+](https://ads.tiktok.com/resources/help/article/about-updates-to-smart-plus?lang=en), captured 2026-10-16.
- **SDK-only advice has to distinguish server events from installation measurement.** Current RevenueCat docs explicitly retain the Meta SDK and warn about duplicate subscriptions and one conversion-value updater. A subscription webhook alone is not an install-measurement system. [RevenueCat Meta](https://www.revenuecat.com/docs/integrations/attribution/meta-ads), captured 2026-10-16.
- **Weekly plans are a dataset trend, not ExcerLock’s prescription.** Adapty’s 2026 article reports weekly-plan growth and a positive trial LTV association in Health & Fitness, but a negative one in Productivity. ExcerLock spans these use cases. Vendor populations and category definitions differ from RevenueCat’s; neither establishes that changing this app to weekly causes higher profits. The Adapty page also contains differing LTV figures between body text and image description, so I have not used those exact LTV values. [Victoria Kharlan, Adapty](https://adapty.io/blog/mobile-app-monetization-2026/), published 2026-03-12, modified 2026-03-13.
- **Web checkout is an option, not universally superior economics.** Current Apple rules are storefront-dependent, and an app-to-web checkout experiment cannot settle a cold web-to-app acquisition question. [Apple guidelines](https://developer.apple.com/app-store/review/guidelines/), captured 2026-10-16; [RevenueCat experiment](https://www.revenuecat.com/blog/growth/iap-vs-web-purchases-conversion-test/), May 2025.
- **A new Apple protocol does not certify network implementation.** AAK’s existence and availability do not establish the campaign-specific Meta/TikTok support, schema or eligibility for ExcerLock. [Apple](https://developer.apple.com/app-store/ad-attribution/), captured 2026-10-16.

## What I would do for ExcerLock — judgment, 2026-10-16

### First make the test measurable

Verify release availability, actual price/trial terms, selected-app blocking and permission flow in the current build. Use a tested store listing with real screenshots. For a walking ad and a gym ad, consider matched custom product pages rather than a web quiz first. Apple supports unique URLs and feature-specific pages, with deep-link destinations on supported iOS versions; confirm network routing actually preserves the intended page. **Official:** [custom product pages](https://developer.apple.com/app-store/custom-product-pages/), captured 2026-10-16. No page publication is authorized by this report.

Instrument a first-party funnel: first open → onboarding completed → generic setup success → paywall viewed → trial started → first paid charge → renewal/refund. Keep payment state in the subscription backend and acquisition attribution in the selected measurement system. Keep identifiers in place before test purchases, establish event-delivery ownership, and verify both consent-granted and consent-denied paths. Confirm test and restore transactions cannot inflate live acquisition metrics.

**Specific product constraint:** do not send step counts, gym coordinates, HealthKit/Motion fitness data, or health-derived activation events to ad networks. Keep behavior needed for product diagnosis in the appropriate first-party system and review even derived event definitions before advertising use. Apple restricts advertising/marketing uses of health and fitness data; consent alone is not a blanket exception. **Official:** [App Review Guidelines 5.1.2/5.1.3](https://developer.apple.com/app-store/review/guidelines/), captured 2026-10-16. Use generic commercial subscription signals for optimization.

### Concentrate the first media test

**My proposed range is $1,000–$5,000 total media, released in stages; production and tools are separate.** Start on Meta as a judgment about conserving limited test volume, not a sourced claim that Meta has lower CPI. Use one iOS App Promotion campaign, one initial country/language cohort, one main prospecting ad set and a small set of materially different creatives. Use broad delivery within the chosen demographic controls rather than many interest cells. Start with adults 18–30 so the first test has one simpler audience scope; that is an operating choice, not a statement about rules for the brief’s younger audience.

If trial optimization is eligible and functioning, test it. If it is not, run a capped install diagnostic with a stated downstream success criterion, resolve eligibility, and then reassess. Begin with a volume-oriented bid strategy; a speculative tight cost cap can prevent a new campaign from delivering. Avoid simultaneous install-versus-trial-versus-purchase tests at this budget.

| Media envelope | Proposed execution | What it can reasonably establish |
|---|---|---|
| $1,000 | About $100/day for 10 days on one network, then allow trial/reporting maturation. | Instrumentation failures, broad funnel losses, directional creative signal. At the illustrative $3 CPI / 10% trial / 40% paid assumptions: about 333 installs, 33 trials and 13 payers. Too few for precise LTV or many experiments. |
| $3,000 | First $1,000 as above; reserve $2,000 for one correction and another concentrated run. | Whether a corrected creative, store or onboarding problem improves the same cohort economics. Do not automatically spend the reserve. |
| $5,000 | Stage the same way; reserve roughly $1,000–$1,500 for a later TikTok test only if measurement and sufficient daily delivery are feasible. | A preliminary second-channel test, not a statistically conclusive network ranking. If TikTok SKAN AEO needs a volume the reserve cannot support, keep the money unspent or postpone that comparison. |

Every budget, duration and forecast in this table is my 2026-10-16 planning judgment or arithmetic, not an industry benchmark or spending authorization. Actual delivery and conversion can be far worse. The earlier learning-volume calculations show why a small test should not promise to exit purchase learning.

### Make these creatives first

Produce a small set of concepts with the same honest offer and verified product behavior:

- A real phone demonstration: a selected app is blocked, the demonstrated movement condition is met, then access changes.
- A creator explaining a specific failed routine, followed by the same product proof.
- A walking-use-case variant and a gym-use-case variant, each showing only the condition it actually uses.
- A clear screen recording with narration explaining selection of apps and setup, to test comprehension without relying on lifestyle footage.

My suggested opening batch is **4–6 distinct assets**, an operating choice consistent with [TikTok’s Smart+ App guidance](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en), captured 2026-10-16. These are concept directions, not invented captain hooks or scripts. Do not promise weight loss, a fabricated unlocking latency or whole-phone locking. Optimize creative decisions against mature payer economics as well as trial cost.

### Read the result in the right order

Daily: delivery/spend, event failures, click-to-store/first-open gaps, onboarding abandonment and trial starts. Treat CTR and video engagement as diagnostic signals. After maturity: trials converted, unique new payers, direct purchases, refunds, net proceeds per first-open cohort, acquisition cost per payer and chosen payback horizon. Keep D7/D35 and later cohort views clearly labeled; never compare an incomplete trial cohort to a mature one. RevenueCat’s cohort definitions explain why chart dates and daily event totals differ. **Vendor:** [Initial Conversion](https://www.revenuecat.com/docs/dashboard-and-metrics/charts/initial-conversion-chart), captured 2026-10-16.

Before launch, set the economic stop condition from actual price and contribution. Stop immediately for broken events, payment/entitlement failures or material product mismatch. Otherwise review after the preset media tranche and mature trial window; do not keep spending solely to satisfy a learning label. Keep the onboarding/paywall fixed during the first creative comparison, log changes, and fix one diagnosed bottleneck at a time.

### Connect the result to the existing operations system

Propose an independent paid-acquisition module with its own campaign/cohort data and decision logic. A composition adapter outside the sections would join stable creative/deliverable IDs to existing creator records and the dashboard’s generic inbox extension. A scheduled read-only job could import spend exports and aggregate subscription cohorts, then show “creative to repeat / revise / insufficient evidence,” with maturity and attribution confidence displayed. Budget increases and launches would remain captain approvals. No live services or ad integrations were changed for this research.

Reuse the existing approval inbox and creator deliverable IDs; do not add a separate creator tracker. Keep paid-performance data owned by the new module, creator contracts/deliverables owned by creator operations, and the join in the adapter. Initial ingestion can be CSV exports before any API integration. This follows the existing generic extension seam documented in `sections/creators/README.md`, read 2026-10-16.

## Open questions and missing coverage

1. What are the actual subscription prices, trial lengths, annual/monthly mix, refunds, net proceeds and retention? Without them, target CPA and allowable CPI remain unknown.
2. Is the app released and is each advertised condition working in the current build? What does usable setup completion look like?
3. Which analytics, subscription SDK, ad SDK and MMP integrations already exist in the separate app repository? This research did not inspect that repository or any account.
4. Are Meta trial/purchase events AEM-eligible? Is TikTok real-time iOS reporting available for this specific app? Public documentation cannot answer account-specific eligibility.
5. What is a current, matched US iOS Meta/TikTok Health & Fitness subscription CPI or cost-per-trial distribution? The public AppsFlyer page yielded no values. No defensible matched benchmark was obtained; the sensitivity table is not a replacement claim.
6. Which protocol and postback windows do each network/MMP actually use for these campaigns? Which first-charge events fall within eligible optimization/reporting windows for the chosen trial?
7. What is the current Meta learning-volume requirement in the campaign interface? The official help page body could not be read; the historical practitioner rule is explicitly qualified.
8. How would web purchasers identify their app account and recover access? What are support, cancellation, chargeback and storefront obligations for that route?
9. Which geographic and demographic segment has sufficient willingness to pay? Cross-category report medians do not settle ExcerLock’s screen-time-plus-fitness positioning.
10. How many genuinely incremental payers does paid media create alongside organic creators? Small preliminary cohorts will not settle that causal question.

## Source table and raw archive

All sources were captured/read on **2026-10-16**. “High” means authoritative for its own implementation or directly observed data, not universal causality. “Medium” usually means commercial interpretation or a limited experiment. Raw source paths are relative to `../raw/app-ua-mechanics/`; successful agent-web folders contain original response bytes (`source.bin`), extracted `content.md`, and retrieval metadata (`result.json`). A successful fetch is not an endorsement of the page’s claims.

| ID / raw folder | Source URL | Author / publisher | Publication or update date | Type | Trust and use |
|---|---|---|---|---|---|
| 01 `01-apple-attribution` | [Ad attribution](https://developer.apple.com/app-store/ad-attribution/) | Apple Developer | Undated live doc | Official platform doc | High for Apple behavior; does not certify any network’s integration. |
| 02 `02-apple-privacy` | [User privacy and data use](https://developer.apple.com/app-store/user-privacy-and-data-use/) | Apple Developer | Undated live doc | Official platform doc | High for ATT requirements; this page also includes future EU OS provisions, which are not treated as current deployed behavior here. |
| 03 `03-apple-skan-windows` | [Multiple conversion windows](https://developer.apple.com/documentation/storekit/receiving-postbacks-in-multiple-conversion-windows) | Apple Developer | Undated live doc | Official platform doc | High for windows/privacy tiers. JS page was thin in web reader; substantive Apple documentation JSON was retrieved and read locally. |
| 04 `04-tiktok-aeo` | [AEO best practices](https://ads.tiktok.com/resources/help/article/best-practices-for-app-event-optimization?lang=en) | TikTok for Business | February 2025 | Official platform doc | High for TikTok’s stated SKAN guidance; predates real-time route. |
| 05 `05-tiktok-realtime` | [iOS real-time reporting](https://ads.tiktok.com/resources/help/article/about-ios-real-time-conversion-reporting) | TikTok for Business | August 2026 | Official platform doc | High for listed support; actual eligibility unverified. |
| 06 `06-tiktok-ios-bidding` | [iOS bidding/optimization](https://ads.tiktok.com/resources/help/article/bidding-optimization-considerations-ios14?lang=en) | TikTok for Business | August 2026 | Official platform doc | High for stated options; path-specific and partly inconsistent with older guides. |
| 07 `web-read-01.txt` | [Meta AEM integration](https://support.appsflyer.com/hc/en-us/articles/19228737402129-Meta-Ads-Aggregate-Event-Measurement-AEM-for-iOS) | AppsFlyer support | 2026-05-25 | Vendor implementation doc | High for AppsFlyer’s path; secondary to Meta/Apple policy. Local direct fetch 403; substantive web-reader response read and archived. |
| 08 `web-read-01.txt` | [SKAN solution guide](https://support.appsflyer.com/hc/en-us/articles/360011420698-SKAdNetwork-SKAN-solution-guide) | AppsFlyer support | 2026-06-11 | Vendor implementation doc | High for schema ownership/setup. Local 403; substantive web-reader response archived. |
| 09 `09-rc-2026` | [State of Subscription Apps 2026](https://www.revenuecat.com/state-of-subscription-apps/) | RevenueCat research team | 2026 edition; exact publication day not established | Data report | High for its disclosed customer sample; selection and cohort mixing limit portability. Read methodology and relevant conversion sections. |
| 10 `10-rc-2025` | [2025 report](https://www.revenuecat.com/state-of-subscription-apps-2025/) | RevenueCat research team | 2025 edition | Data report | High within its sample; used to identify outdated benchmark reuse. |
| 11 `11-adapty-2026` | [2026 monetization findings](https://adapty.io/blog/mobile-app-monetization-2026/) | Victoria Kharlan / Adapty | Published 2026-03-12; modified 2026-03-13 | Data-report interpretation | Medium-high; first-party dataset but promotional conclusions and inconsistent body/chart LTV figures. |
| 12 `12-superwall-review` | [2025 year in review](https://superwall.com/blog/superwall-ships-recap/) | Jordan Morgan / Superwall | 2025-12-05 | Vendor experiment summary | Medium; useful test hypotheses, no reproducible aggregate experiment data. |
| 13 `13-rc-meta` | [Meta Ads integration](https://www.revenuecat.com/docs/integrations/attribution/meta-ads) | RevenueCat documentation team | Undated live doc | Vendor implementation doc | High for current event mapping/delivery and deduplication warnings. Not proof of campaign attribution. |
| 15 `15-rc-attribution` | [Attribution setup](https://www.revenuecat.com/docs/integrations/attribution/getting-started) | RevenueCat documentation team | Undated live doc | Vendor implementation doc | High for its integration architecture and fresh-customer testing. |
| 16 `16-rc-web-pros` | [Web-to-app pros/cons](https://www.revenuecat.com/blog/growth/the-pros-and-cons-of-web-to-app-funnels/) | Nathan Hudson, Perceptycs founder; RevenueCat guest author | Published 2024-07-23; modified 2026-09-11 | Practitioner article | Medium; specific operator reasoning, some categorical language needs current-doc qualification. |
| 17 `17-rc-web-test` | [Web vs IAP experiment](https://www.revenuecat.com/blog/growth/iap-vs-web-purchases-conversion-test/) | Jacob Eiting, Rik Haandrikman / RevenueCat | Published 2025-05-14; experiment update 2025-05-28 | First-party experiment | High for this app/test; medium for generalization. App-to-web is not cold web-to-app. |
| 18 `18-rc-web-strategy` | [Define web campaign](https://www.revenuecat.com/guides/web-to-app-funnels/campaign) | RevenueCat guide team; individual byline not established | Undated live guide | Practitioner/vendor guide | Medium-high for planning sequence; no causal performance evidence. |
| 19 `19-singular-mmp` | [MMP definition](https://www.singular.net/glossary/mobile-measurement-partner-mmp/) | Singular | Published 2024-06-28; modified 2026-06-23 | Vendor technical explainer | Medium-high for functions; “single truth” and superiority claims are sales language. |
| 21 `21-tiktok-budget` | [Budget](https://ads.tiktok.com/resources/help/article/budget?lang=en) | TikTok for Business | Undated in local extraction | Official platform doc | High for published floors, not sufficient statistical budget. |
| 22 `22-tiktok-smart` | [Upgraded Smart+](https://ads.tiktok.com/resources/help/article/about-updates-to-smart-plus?lang=en) | TikTok for Business | Undated in local extraction | Official platform doc | High for stated structure changes; rollout/account availability can differ. |
| 23 `23-apple-small` | [Small Business Program](https://developer.apple.com/app-store/small-business-program/) | Apple Developer | Undated live doc | Official platform doc | High for eligibility and commission; ExcerLock enrollment unknown. |
| 24 `24-apple-guidelines` | [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Apple Developer | Undated live rules | Official platform doc | High for current written rules; purchase and health-data sections read. Storefront differences matter. |
| 26 `26-meta-events` | [iOS App Events setup](https://developers.facebook.com/docs/app-events/getting-started-app-events-ios/) | Meta for Developers | Undated live doc | Official platform doc | High for direct SDK collection and automatic purchase logging; does not prove AEM eligibility. |
| 27 `27-rc-initial` | [Initial Conversion chart](https://www.revenuecat.com/docs/dashboard-and-metrics/charts/initial-conversion-chart) | RevenueCat documentation team | Undated live doc | Vendor implementation doc | High for chart/cohort definitions; includes trials and other purchases. |
| 28 `28-tiktok-ios-create` | [Create dedicated iOS campaign](https://ads.tiktok.com/resources/help/article/how-to-create-an-ios-14-5-dedicated-campaign?lang=en) | TikTok for Business | Undated in local extraction | Official platform doc | High for documented flow; some older MMP wording must be read alongside newer SDK support. |
| 30 `30-meta-sdk` | [SDK event-name definitions](https://github.com/facebook/facebook-ios-sdk/blob/main/FBSDKCoreKit/FBSDKCoreKit/AppEvents/FBSDKAppEventName.m) | Meta SDK maintainers | Live main branch, snapshot 2026-10-16 | Official platform source code | High for exact event distinctions; no delivery/performance claims inferred. Raw GitHub response saved. |
| 31 `31-tiktok-learning` | [Learning phase](https://ads.tiktok.com/resources/help/article/learning-phase?lang=en) | TikTok for Business | June 2026 | Official platform doc | High for current general guidance; stabilization statement is not an exit guarantee. |
| 32 `32-apple-cpp` | [Custom product pages](https://developer.apple.com/app-store/custom-product-pages/) | Apple Developer | Undated live doc | Official platform doc | High for feature URLs and deep links; selected success stories do not predict ExcerLock lift. |
| 33 `33-adjust-windows` | [Attribution windows](https://help.adjust.com/en/article/attribution-windows) | Adjust documentation team | Undated live doc | Vendor implementation doc | High for configurable windows; avoids assuming dashboards use matching definitions. |
| 35 `35-jon-learning` | [Facebook learning phase](https://www.jonloomer.com/facebook-ads-learning-phase/) | Jon Loomer | 2020-era article; exact day not verified | Historical practitioner explanation | Medium for arithmetic and his own examples; low as sole evidence of a 2026 Meta threshold. |
| 36 `36-tiktok-smart-budget` | [Smart+ App best practices](https://ads.tiktok.com/resources/help/article/best-practices-for-smart-plus-app-campaigns?lang=en) | TikTok for Business | Undated in local extraction | Official platform doc | High for what this page recommends; bidding availability wording conflicts with newer iOS docs. |

### Failed, thin or incomplete fetches — not counted as substantive sources

| Attempt | Result and treatment |
|---|---|
| `S01` original TikTok AEO URL | 403. Recovered substantive page through canonical `/resources/help/` path and web reader; not an extra source. |
| `07-appsflyer-aem`, `08-appsflyer-skan` | Direct 403. Recovered through web reader; API responses stored in `web-open-01.txt` and `web-read-01.txt`. |
| `14-rc-tiktok` | Guessed RevenueCat TikTok integration URL returned 404. No conclusion that an integration does not exist; TikTok SDK/MMP official docs supply the covered routes. |
| `20-adjust-fitness` | Direct 429. No findings attributed to the unread page; Adjust technical coverage comes from source 33. |
| `25-meta-learning` | Retrieved title but readability failed and original body contained only the title. Official learning threshold remains unverified. |
| `29-apple-interoperability` | Guessed Apple documentation JSON route returned 404. AAK coverage rests on source 01; detailed interoperability implementation remains a question. |
| `34-appsflyer-benchmarks` | Page was readable, but numeric benchmark data absent. Also confirmed in `web-open-02.txt`. No CPI value inferred. |

`collect.py` and `fetch-manifest.json` preserve the initial retrieval list and outcomes. Numbered source folders added afterward retain their own retrieval metadata. Web-reader API-response files preserve the recovered pages. No account credentials, API keys or customer-level analytics were collected.
