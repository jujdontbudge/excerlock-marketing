# App geo targeting: where ExcerLock should buy its first users

Research date: **16 October 2026, America/Chicago**. Raw captures use UTC, so some are dated 17 October. No accounts were accessed, campaigns changed, ads published or paid scraping services used. Research-tool spend: **$0**.

**My recommendation:** start with the US, on one platform, with one country-wide acquisition audience. Learn what an American paying user costs before adding cheaper countries. Later, give another country a protected test budget and compare mature subscription cohorts. Worldwide targeting can be useful for an established business; it is a poor first experiment when country economics are unknown.

This is a judgment, not a platform rule. The evidence below explains the tradeoffs. I read **34 substantive web sources**, plus the relevant acquisition and Health & Fitness pages of the 2025 RevenueCat PDF. The PDF and HTML are the same underlying report, not independent corroboration. Failed pages and incomplete benchmark interfaces are listed separately and excluded from that count.

Evidence labels: **Official** means platform documentation; **Data** means a vendor's aggregate observations; **Practitioner** means an identified operator's advice or reported experience; **Judgment** means my recommendation or inference. Vendor case studies and reported lifts are not independently audited. Dates beside links are publication/update dates where visible; otherwise they are capture dates. Source IDs match the raw capture folders.

## The 18 most important things to understand

### 1. A country is a different set of unit economics, not just a different media price

**Judgment / arithmetic:** an inexpensive install can become an expensive subscriber. For a trial-only funnel:

`paid subscriber CAC = CPI / (install-to-trial rate × trial-to-paid rate)`

CAC is customer acquisition cost. CPI is ad spend divided by attributed installs. The equation assumes matching acquisition cohorts and mature outcomes, and excludes direct purchases. Compare net revenue per acquired user against acquisition cost; include refunds, store deductions and the time it takes to recover the spend. A lower CPI alone answers none of those questions.

**Practitioner evidence:** Mojo's team reports using country-level revenue per user, pricing experiments and cohorts to guide acquisition, including blended cohorts where attribution is incomplete. That is a concrete app operator's practice, rather than a generic recommendation to find cheap traffic. [Mojo case study, undated; read 16 Oct 2026](https://www.revenuecat.com/customers/mojo-case/).

### 2. US-only, English-speaking countries and worldwide answer different questions

| Choice | What you can learn | Main tradeoff | My use for ExcerLock |
|---|---|---|---|
| US only | Whether the US audience buys this offer | No evidence about other countries | First commercial test |
| US, UK, Canada, Australia together | Whether the platform can find results somewhere in this English-speaking group | Spend allocation is part of the result; this is not an equal country comparison | Later, if country-level economics justify pooling |
| US separate; UK/Canada/Australia grouped | US economics plus an expansion pool | The expansion pool still needs country breakdowns | Reasonable intermediate structure |
| Worldwide / broad international pool | Whether results can be found across many eligible markets | More variation in price, language, funnel quality and measurement | After establishing country-level economics and support |

**Practitioner:** Jon Loomer describes a core-country group and a separate worldwide-excluding-core group to protect core-market spending. This is older Meta lead-generation practice, not an iOS subscription experiment. Its useful lesson is explicit budget protection. His example allocation is not an ExcerLock prescription. [Loomer, 23 Dec 2022](https://pubcast.jonloomer.com/videos/how-to-address-location-targeting-for-facebook-ads-when-you-have-a-worldwide-audience/).

### 3. “Tier 1” is shorthand, not an official universal country list

**Data:** RevenueCat's current regional definitions put the US and Canada in North America, the UK in Western Europe, Australia in Asia-Pacific, and Singapore in India/Southeast Asia. Consequently, an Asia-Pacific benchmark is not a Southeast Asia benchmark. These groups are analytical buckets, not guarantees about every country. [RevenueCat 2026, methodology and regional definitions; 2025 data, read 16 Oct 2026](https://www.revenuecat.com/state-of-subscription-apps/).

**Judgment:** decide on individual countries. Brazil and Mexico need different language work; Singapore and Indonesia should not inherit the same acquisition or pricing assumption; Eastern Europe is not one uniform market. Use “US/UK/CA/AU” when that is what you mean, rather than letting “Tier 1” conceal the actual targeting.

### 4. Health & Fitness conversion really does differ by region, but the best usable evidence here is regional, older and mixed-platform

**Data:** the Health & Fitness appendix of RevenueCat's **2025** report gives the following medians. I checked the rendered charts, their category divider and the report's unusual box-plot legend: the lower edge of the box is the median. These are separate app-level distributions; **do not multiply the two median columns to manufacture a measured install-to-paid rate**. [RevenueCat 2025 PDF, printed pp. 164–165 / PDF pp. 165–166; report based primarily on 2024 data](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf).

| User region | Health & Fitness trial-start median | Health & Fitness trial-to-paid median | Source/date for both values |
|---|---:|---:|---|
| North America | 8.7% | 41.0% | [RevenueCat 2025, pp. 164–165](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) |
| Western Europe | 6.0% | 37.0% | [RevenueCat 2025, pp. 164–165](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) |
| Asia-Pacific | 5.3% | 39.9% | [RevenueCat 2025, pp. 164–165](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) |
| Latin America | 3.6% | 30.9% | [RevenueCat 2025, pp. 164–165](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) |
| India / Southeast Asia | 2.5% | 18.9% | [RevenueCat 2025, pp. 164–165](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) |
| Middle East / Africa | 3.6% | 24.9% | [RevenueCat 2025, pp. 164–165](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) |

These are **not** US-versus-UK results, Meta/TikTok-only cohorts, iOS-only cohorts or a study of women interested in walking. The category also includes Medical. Treat them as evidence that geography matters, not as ExcerLock targets. The current all-category geography sections also show substantial variation, but cannot replace this category-specific table. [RevenueCat 2026, conversion sections; read 16 Oct 2026](https://www.revenuecat.com/state-of-subscription-apps/).

### 5. There is no defensible country-by-country Meta/TikTok fitness CPI and CPM price list in this research

**Data:** AppsFlyer's contribution to the RevenueCat **2025** PDF reports Health & Fitness CPI of **$9.07 for iOS globally**, **$4.53 for Google Play North America**, and **$2.09 for Google Play Western Europe**. Its contribution describes acquisition data from **October 2023–December 2024**. The chart mixes global iOS with regional Android, so it does **not** establish a US/UK iOS cost difference. It also does not isolate Meta or TikTok. [AppsFlyer in RevenueCat 2025, printed pp. 98–99](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf).

**Data, different denominator:** Adjust reports Health & Fitness **eCPI** of **$1.19 in North America, $0.82 in Europe and $0.45 in APAC** for **H1 2024**. Its article explicitly includes methods that count paid and organic installs. Those figures are not interchangeable with paid-only CPI, or the AppsFlyer numbers above. [Prashansa Shrestha, Adjust, 30 Jul 2024](https://www.adjust.com/blog/ecpi-benchmarks/).

**Judgment:** use these as historical context only. Do not budget a new iOS campaign using a low all-platform, all-network or organic-inclusive number. I did not find readable, methodologically clear current CPM comparisons for this exact app/channel/country combination. Cheap-geo claims without those dimensions are incomplete.

### 6. Worldwide delivery follows the event you ask for; install and trial objectives leave monetization risk with you

**Practitioner:** Loomer explains that cheap countries can dominate worldwide lead or engagement campaigns when the algorithm is rewarded for the initial action rather than a customer. He separately argues that purchase optimization could allocate better because purchase rates differ by country; he presents that as a hypothesis to experiment with, not a proven worldwide-app result. [Loomer, country strategy, 26 Jun 2023; updated 1 Mar 2025](https://www.jonloomer.com/strategically-target-countries-for-quality-leads-with-meta-ads/), [purchase discussion, 1 Jul 2023](https://www.jonloomer.com/qvt/target-all-countries-for-a-purchase/).

**Judgment:** the analogous risk for ExcerLock is optimizing for installs or free trials whose paid conversion and renewal value vary across countries. Purchase-count optimization still does not necessarily maximize net value when plan prices differ. Broad international targeting is more defensible when the chosen signal has a demonstrated relationship to net revenue across the included markets.

### 7. Cheap countries can screen ideas, but a US creative winner must win in the US

**Judgment:** a low-cost geo experiment can reveal whether a demonstration is understandable, whether the app link works, or which concept merits a US test. It cannot directly establish US CPI, US willingness to pay, or even the order in which creatives will perform there. Language, the people responding, the auction, the store page and price all change together.

**Practitioner evidence:** Cedric Yarish's subscription-app testing interview favors testing on the destination platform where possible and checking user quality when falling back to install optimization. It does not provide a controlled country-transfer study. [Daphne Tideman interviewing Yarish, 19 Jun 2025](https://www.revenuecat.com/blog/growth/7-meta-ad-testing-frameworks-for-subscription-apps/).

**What I could not verify:** a credible controlled estimate that a winner in Brazil, the Philippines or Eastern Europe has a particular probability of winning in US iOS fitness subscription acquisition. No universal transfer multiplier is justified here. A fair transfer check would hold creative, objective and funnel constant, compare performance within each market, and spend a protected amount validating shortlisted concepts in the actual destination market.

### 8. Buying cheap events to “exit learning” is not proof of better economics elsewhere

**Official, current:** TikTok says volatility typically starts declining after about **25 campaign results or 7 days**. That wording describes stabilization, not a guaranteed learning completion threshold. It warns against pauses, edits that retrigger learning and unreasonable budgets or creative volumes. [TikTok learning phase, updated Jun 2026](https://ads.tiktok.com/help/article/learning-phase).

**Practitioner, older Meta reference:** Loomer's article describes about **50 optimization actions in 7 days per ad set**, and the fragmentation caused by separate country groups. It is not fresh official confirmation of every current app campaign type. [Loomer, published 8 Jan 2020; updated 1 Mar 2025](https://www.jonloomer.com/facebook-ads-learning-phase/).

**Judgment:** cheap-country trials may satisfy a campaign's event-volume requirement, but they do not demonstrate US subscription demand. Do not assume learned performance survives changing the country. Prefer an affordable structure that buys relevant signals; judge a campaign on actual acquisition economics rather than the delivery label alone.

### 9. Group countries when you accept the allocator's choice; split them when you need protected evidence

**Judgment:** a grouped audience lets the platform choose both the person and the country. That can be efficient, but a country receiving little spending has not failed a meaningful test. Separate ad sets/ad groups with their own budgets can protect evidence without necessarily requiring separate campaigns. A campaign-level shared budget can still concentrate spend in one country's ad set.

Use a separate campaign when you need a separate budget envelope, objective, bid strategy, schedule, or materially different funnel. Group countries when language, offer and observed net economics are similar and you accept unequal allocation. Country splits become a liability when they leave too little data in every group.

**Practitioner basis:** Loomer's country-grouping experiment monitors spend distribution, regroups countries and explicitly discusses the budget cost of isolating every country. It is lead-generation evidence, not a validated subscription structure. [Loomer, 26 Jun 2023; updated 1 Mar 2025](https://www.jonloomer.com/strategically-target-countries-for-quality-leads-with-meta-ads/).

### 10. A country and a language are separate targeting decisions

**Official:** TikTok's upgraded Smart+ documentation lists location under audience controls and preserves location when duplicating an App Promotion campaign. Its current Smart+ overview also describes audience automation using inputs such as location, age and language. Those controls still require an explicit market choice. [TikTok duplication guide, updated Oct 2026](https://ads.tiktok.com/help/article/how-to-duplicate-campaigns-into-smart-plus), [Smart+ overview, updated 5 Oct 2026](https://ads.tiktok.com/business/en-US/blog/smart-plus-ai-performance-solution).

**Practitioner, not freshly verified Meta documentation:** Loomer describes location as an Advantage+ audience control and language as a separate control, with a recommendation to leave language blank when the ad uses a common language of the selected market. [Loomer, updated 1 Mar 2025](https://www.jonloomer.com/how-advantage-plus-audience-works/).

**Judgment:** US targeting is not shorthand for an English-language audience, and English language is not shorthand for US residence. Choose eligible countries first; use language filters deliberately when needed to keep the ad and product experience coherent. Current Meta help pages were blocked, so verify the actual app campaign controls before implementation.

### 11. TikTok's account registration country can limit the countries you can advertise to

**Official:** available target markets depend on the country or region used to register the TikTok Ads Manager account. The public page requires selecting the registration market to see availability. It does not justify assuming that every account can reach every country. [TikTok available location targeting options, updated Jun 2025](https://ads.tiktok.com/help/article/placements-available-locations).

**Official:** TikTok supports country and various subnational location types, but does **not** support location or ZIP-code exclusions. Its guidance is to select desired locations. [TikTok location targeting, live page updated Oct 2026](https://ads.tiktok.com/help/article/location-targeting).

**Judgment:** translate a Meta “worldwide excluding core countries” strategy into a positive list of eligible expansion countries for TikTok. Check country and placement availability before commissioning a localized batch. I did not verify the registration country or entitlements of any ExcerLock account.

### 12. Localization is the whole path from ad to successful payment

**Official:** Apple distinguishes App Store metadata localization from localizing the app binary. Metadata can fall back to the primary or another relevant language. Adding a language initially inherits screenshots from the primary language, so a translated description does not establish a translated listing. [Apple, Localize app information, undated; read 16 Oct 2026](https://developer.apple.com/help/app-store-connect/manage-app-information/localize-app-information/).

**Judgment:** check the ad's spoken and on-screen language, store screenshots, onboarding, permission explanations, units, paywall, local currency and support. For ExcerLock, understanding why selected apps are blocked and what movement unlocks them is part of the sale. A localized ad pointing to an English permission flow can produce a misleading “country doesn't convert” verdict.

**Practitioner:** RevenueCat's localization article recommends testing geographic demand and localizing the store listing before committing to full expansion. Its historical market-growth numbers are not current market forecasts. [Peter Meinertzhagen, published 1 Mar 2023; updated 6 Jun 2024](https://www.revenuecat.com/blog/growth/is-localization-the-next-great-growth-opportunity-for-subscription-apps/).

### 13. Currency conversion is not price optimization

**Official:** Apple supports subscription pricing by country or region and country-specific introductory-offer availability. The app's availability and the purchasable offer must both be correct. [Apple pricing and availability reference, undated; read 16 Oct 2026](https://developer.apple.com/help/app-store-connect/reference/pricing-and-availability/in-app-purchase-and-subscriptions-pricing-and-availability/).

**Practitioner, self-reported:** Mojo raised annual prices for new users in markets including the US and Germany by **50%**, while lowering prices in Brazil. It reports different benefits by market rather than one universal low-price strategy. [Michal Parizek, published 12 Oct 2023; visible update 6 Jun 2024](https://www.revenuecat.com/blog/growth/mojo-60-percent-arpu-growth-five-months/).

**Judgment:** first establish a functioning local offer. Then test price within a country while holding acquisition reasonably stable. If a cheaper offer lifts conversion but lowers net revenue per acquired user, the price change may still be a loss. Do not simultaneously change country, price, trial and creative and attribute the outcome to geography.

### 14. The paywall and product promise may need adaptation even when the words translate correctly

**Practitioner:** Parizek describes different paywall responses in Latin America and Japan, and recommends country-level funnel analysis. These are observations from his work, not universal cultural laws. [Paywall guide, published 5 Dec 2024; updated 21 Nov 2025](https://www.revenuecat.com/blog/growth/guide-to-mobile-paywalls-subscription-apps/).

**Practitioner/vendor examples:** RevenueCat's Targeting article includes a Headspace example where lower prices did not resolve cultural barriers; messaging and feature emphasis mattered too. Country-based offerings can adapt more than currency. [RevenueCat, published 6 Dec 2023; updated 15 Jul 2024](https://www.revenuecat.com/blog/growth/offering-customization-examples-targeting/).

**Judgment:** ExcerLock should validate whether “use your attachment to apps to help you move” is understood before interpreting low subscriptions as price resistance. Keep any successful price framing truthful and the total billed amount clear. Apple's subscription guidance is the canonical reference for presentation, rather than an old growth screenshot. [Apple subscription guidance, undated; read 16 Oct 2026](https://developer.apple.com/app-store/subscriptions/).

### 15. US state/city targeting is available, but there is no evidence here that it is a better starting strategy

**Official:** TikTok supports states, cities, DMAs and eligible ZIP codes. It warns that small geographical areas can reduce delivery and raise CPA; location matching is based on multiple signals and is not guaranteed accurate in every case. [TikTok location targeting, updated Oct 2026](https://ads.tiktok.com/help/article/location-targeting).

**Judgment:** ExcerLock is not inherently restricted to one city. Starting with “walking cities” or “fitness states” imposes a theory before seeing customer economics, and subdivides the data. Begin nationwide; inspect geography afterward. Restrict when there is an actual operational limit, a local partnership or a repeatable economic difference with enough data to support it.

Do not confuse the app's gym-location feature with a need to target ads around gyms. A state-level difference in observed conversions also does not prove the state caused the difference: creative delivery, audience mix and small samples can explain it. A geographic holdout for incrementality is a separate experimental design, not a cheap-CPI targeting trick.

### 16. Time zones affect reporting and scheduling; dayparting needs subscription evidence

**Official:** TikTok says the account time zone affects delivery settings, reporting and billing. Its May 2025 page also describes a time-zone converter introduced in March 2025, including target-market scheduling and daylight-saving adjustments. The account clock and scheduling conversion are distinct; do not interpret the converter as changing the account time zone. [TikTok time-zone documentation, updated May 2025](https://ads.tiktok.com/help/article/time-zone).

**Judgment:** initially run throughout the day. “People go to the gym in the morning” is not evidence that morning ad impressions produce the best subscribers. If later testing dayparting, use mature purchase cohorts, record the account/reporting time zone, and account for multiple US time zones and daylight saving. A trial started in the evening can become revenue on another date. I could not freshly verify current Meta app-campaign scheduling options without account access; I make no claim that every campaign supports the same scheduling controls.

### 17. Your ad platform's country, the user's IP country and the App Store country may disagree

**Official:** Apple says the customer's Apple Account country or region determines the storefront where they acquire an app. App availability must be checked for each intended storefront. [Apple app availability, undated; read 16 Oct 2026](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/manage-availability-for-your-app-on-the-app-store/).

**Vendor documentation:** Adapty distinguishes IP-inferred country from store-account country and explains that installs, transaction dates, time zones and cohorts can differ across systems. RevenueCat's conversion chart likewise cohorts customers rather than simply counting payments made on a calendar day. [Adapty discrepancies guide, undated; read 16 Oct 2026](https://adapty.io/docs/discrepancies-and-troubleshooting), [RevenueCat conversion chart, undated; read 16 Oct 2026](https://www.revenuecat.com/docs/dashboard-and-metrics/charts/conversion-to-paying-chart).

**Judgment:** retain these country definitions separately. Compare identical elapsed cohort windows. Do not sum platform and SKAN installs without understanding overlap: AppsFlyer describes how partial attribution can inflate apparent acquisition cost. [Naval Handa, AppsFlyer, visible update 27 Nov 2025; underlying examples concern 2022](https://www.appsflyer.com/blog/trends-insights/ssot-data-revealed/).

### 18. Geography cannot rescue an offer that does not monetize, and a country should not be rejected on attribution noise

**Practitioner:** Thomas Petit describes the limits of asking every audience to buy the same recurring offer; his anecdote about very large traffic with few payers is unverified and does not identify a repeatable cheap-country strategy. [Petit, published 19 Jan 2026; updated 19 Mar 2026](https://www.revenuecat.com/blog/growth/hybrid-monetization-techniques/).

**Practitioner:** Faith Price's soft-launch interview explains checking comparable titles, selected geos and media-partner estimates, then revising assumptions when real costs differed. This is historical gaming experience, not a current subscription benchmark. [Price / Shamanth Rao, 20 Jan 2022](https://mobileuseracquisitionshow.com/episode/how-to-run-a-soft-launch-in-a-post-att-world-with-faith-price-doubledown-interactive/).

**Practitioner:** Lucas Moscon's subscription SKAN guide explains that available country granularity depends on the postback source and enrichment; do not assume every campaign-country-revenue cell is observed directly. [Moscon, 12 Dec 2024](https://www.revenuecat.com/blog/growth/skadnetwork-guide-subscription-apps/).

**Judgment:** before deciding “the US is too expensive,” check the demonstration, permission completion, paywall exposure, pricing, event delivery and cohort maturity. Before declaring a new country profitable, check net receipts and the attribution basis. Cheap traffic and incomplete reporting can each give false confidence.

## Disagreements, recent changes and advice that has aged

| Issue | What the evidence actually supports | What to do now |
|---|---|---|
| Worldwide is bad / worldwide is efficient | Loomer's separate articles distinguish shallow events from purchases; his worldwide-purchase discussion is explicitly exploratory. Neither proves worldwide iOS subscription profit. [2023 discussion](https://www.jonloomer.com/qvt/target-all-countries-for-a-purchase/) | Choose an objective and country mix whose downstream economics you can observe. |
| Split every country / consolidate everything | Country budget protection improves interpretability, but splitting reduces events per delivery unit. Loomer's own grouping experiment recognizes both. [2023, updated Mar 2025](https://www.jonloomer.com/strategically-target-countries-for-quality-leads-with-meta-ads/) | Start with fewer markets. Separate when a business or measurement requirement earns the extra complexity. |
| Every platform needs the same learning-event threshold | Current TikTok language says stabilization around **25 results or 7 days**, while older Meta practitioner guidance describes **50 actions over 7 days**. These are different statements. [TikTok, Jun 2026](https://ads.tiktok.com/help/article/learning-phase), [Loomer, updated Mar 2025](https://www.jonloomer.com/facebook-ads-learning-phase/) | Do not turn an old universal threshold into a reason to buy irrelevant cheap events. |
| Smart+ means the countries no longer matter | TikTok's current upgrade documentation retains location controls, including for app promotion. [Oct 2026](https://ads.tiktok.com/help/article/how-to-duplicate-campaigns-into-smart-plus) | Automation works inside the eligible market choices; check controls in the chosen campaign version. |
| An old article's “APAC” or “Europe” equals a precise country | Reports have different region definitions and platform mixes. RevenueCat distinguishes user geography from developer HQ. [2026 methodology](https://www.revenuecat.com/state-of-subscription-apps/) | Record both definitions before comparing any numbers. |
| Last year's conversion median proves the market improved or worsened | RevenueCat's **2024**, **2025** and **2026** reports use evolving samples and methodology. Cross-year differences are not a controlled panel. [2024](https://www.revenuecat.com/state-of-subscription-apps-2024/), [2025](https://www.revenuecat.com/state-of-subscription-apps-2025/), [2026](https://www.revenuecat.com/state-of-subscription-apps/) | Use the closest relevant cohort; do not infer a market trend by subtracting headline medians. |
| One authoritative 2026 fitness conversion number | RevenueCat's current category commentary gives **37.7%** median trial-to-paid; Adapty's public 2026 report page gives **35.0%** for Health & Fitness. These are different vendor samples and potentially definitions. [RevenueCat 2026](https://www.revenuecat.com/state-of-subscription-apps/), [Adapty 2026](https://adapty.io/state-of-in-app-subscriptions/) | Use a range as context, not a promise; neither is a country/channel-specific launch target. |
| Cheap Android traffic predicts an iOS country's economics | RevenueCat's 2026 analysis shows platform differences are not uniform across funnel stages and warns about trial-starter selection. [Jaewoong Eum, 25 Mar 2026](https://www.revenuecat.com/blog/engineering/android-paywall-gap/) | Compare countries within iOS for this iOS app. |
| The time-zone page says DST is unsupported, so scheduling conversion cannot handle it | TikTok's page distinguishes its account-clock limitations from the newer converter's DST adjustments. [May 2025](https://ads.tiktok.com/help/article/time-zone) | Record the account zone and check converted start/end times, especially across clock changes. |

**A problem inside the current RevenueCat page:** the 2026 conversion section and its chapter summary contain inconsistent download-to-paid geographic figures. The methodology also has an explicit developer-HQ dimension that is easy to confuse with user geography. I have therefore not used those conflicting D35 values as budget inputs. This is a source limitation, not permission to select the most convenient number. [RevenueCat 2026, methodology, conversion section and chapter summary; read 16 Oct 2026](https://www.revenuecat.com/state-of-subscription-apps/).

## What this means for ExcerLock — my starting plan, not authorization to spend

### Structure and sequence

**Judgment, 16 Oct 2026:** begin with **US-only iOS on one platform**. My default would be Meta first for a clean initial commercial test, then TikTok with the same country; this lane does not establish that Meta will be cheaper. Do not launch both platforms and several countries at once and expect to diagnose the result on a small budget.

Use one acquisition campaign and one broad, country-wide ad set/ad group initially, subject to the app-campaign setup lane's measurement requirements. If a properly tracked trial event is sufficiently frequent, use it as the first commercial optimization signal and audit paid quality. An install-only stage can check the route and collect early signals, but cannot establish subscription viability. Yarish's practitioner example supports a simple trial-focused structure for small subscription advertisers; it is not official platform guidance. [Tideman/Yarish, 19 Jun 2025](https://www.revenuecat.com/blog/growth/7-meta-ad-testing-frameworks-for-subscription-apps/).

**Judgment:** keep the first paid pilot to adults, provisionally women **18–30**, with exact enforceable controls resolved in the targeting-setup lane. This is a narrower pilot than the brief's full audience, not a product audience change. Avoid state/city and interest subdivisions at the outset. Do not assume automated targeting treats every age or gender input as a strict limit; TikTok's current app-upgrade documentation distinguishes controls from suggestions. [TikTok, Oct 2026](https://ads.tiktok.com/help/article/how-to-duplicate-campaigns-into-smart-plus).

Before any launch, verify the actual iOS build, available countries, subscription purchase path and event reporting. The repository's [product record](../../../core/product.md) explicitly leaves current release status and some permission behavior unverified. This research does not establish that ExcerLock is currently downloadable.

### Budget: a learning allowance and a stop condition

**My proposed media allowance:** **$1,000–$2,000 total**, released in reviewed stages. An initial **10–14-day** run at roughly **$70–$100/day** costs **$700–$1,400**; the balance is reserved for a repair/retest or a promising extension. These are planning choices, not benchmark-derived minimums or a promise of sufficient purchases. Creative production and tooling are outside that allowance.

For TikTok, do not confuse platform budget floors with adequate statistical power: current docs say a campaign daily budget, when set, must exceed **$50**, and an ad-group daily budget must exceed **$20**. Available campaign-specific requirements still need checking before setup. [TikTok budgets, updated Jul 2026](https://ads.tiktok.com/help/article/budget).

**Illustration only, all values invented:** at **$5 CPI**, **10% install-to-trial** and **30% mature trial-to-paid**, a **$1,000** test buys about **200 installs, 20 trials and 6 payers**, or roughly **$167 per payer**. That is thin evidence, even after all trials resolve. At a different CPI or funnel, the same budget buys a very different amount of learning. Set the maximum affordable loss before launch, inspect event delivery early, and stop spending if the measured path cannot plausibly meet the economic ceiling.

**Judgment:** define that ceiling from expected net subscription receipts within an agreed payback window, less variable service costs and a margin for uncertainty. Do not substitute a headline annual sticker price for allowable CAC. If even an optimistic, credible funnel cannot justify US acquisition cost, improve the product/offer/creative before calling a cheaper geo the solution.

### Creatives to make first

**Judgment:** make **four distinct concepts**, using real current product behavior, each with the same US offer and destination so country and funnel remain stable:

1. **Active walking proof:** chosen social app blocked, then available while the user walks. Show the exact selected condition clearly.
2. **Step-goal proof:** a selected app becomes available after the chosen step target; use verified UI rather than invented progress graphics.
3. **Gym-arrival proof:** the gym condition and the chosen app's unlock, with private location details concealed.
4. **Creator explanation plus demo:** explain the personal problem and show one actual lock/unlock condition, with captions readable without sound.

These are concepts, not finished hooks or scripts. They should follow the repository's creative workflow. Their purpose is to test which use case earns subscriptions; minor caption variants should not consume the entire initial test. Hook-plus-demo is consistent with Yarish's small-advertiser advice, although it does not prove any ExcerLock concept will win. [Tideman/Yarish, 19 Jun 2025](https://www.revenuecat.com/blog/growth/7-meta-ad-testing-frameworks-for-subscription-apps/).

### Country expansion after the first credible US cohort

**Judgment:** shortlist **Canada or the UK** as the next single-country test if the app, offer and support are ready; choose using existing organic users' paid conversion and net receipts, if available. This is an operational preference for reusing English assets, not evidence that either country is cheaper or more profitable. Australia is another candidate after checking eligibility, offer, season and time-zone handling.

Preserve the US baseline and protect the new country's budget. On Meta, separate ad-set budgets may suffice; on TikTok, check the selected Smart+ version's actual controls and use a separate campaign if required for a protected budget. Compare the same creative concepts and offer first. Only then test a local price or message. Pool countries later if observed economics are sufficiently alike and unequal spend is acceptable.

For Brazil, Mexico, SEA or Eastern European expansion, require a named country and a complete localized route. If commissioning a cheap-country concept screen later, ring-fence it as research and include the destination-market validation cost in the decision. Do not count it as evidence of US commercial performance.

### What to measure and review

**Judgment:** maintain one acquisition-cohort view by channel, country and creative, with clear source definitions:

| Stage | Fields to retain | Decision it supports |
|---|---|---|
| Delivery | Spend, impressions, CPM, clicks, CTR, eligible country list, actual spend distribution | Was the country meaningfully tested? |
| Acquisition | Attributed installs, CPI, attribution source/window, unknown/unassigned share | Did delivery produce app users, and how complete is attribution? |
| Product | Onboarding and relevant permission completion, paywall exposure, first successful movement/unlock | Is the advertised route understandable and working? |
| Monetization | Trial starts, cost per trial, mature trial-to-paid, direct purchases, plan/price, refunds | Did cheap trials become paying users? |
| Economics | Payer CAC, net revenue per install, net cohort ROAS, renewals and payback | Can the acquisition be sustained? |
| Geography | Ad-reported country, analytics/IP country, purchase storefront, language/offer version | Are country comparisons using the same definition? |

Read fixed elapsed windows such as **D7, D14 and D30**, and later renewals; those are my proposed operating windows. Leave cohorts pending until the trial, reporting and refund windows needed for the decision have elapsed. Keep modeled/estimated country revenue distinct from observed transactions. Do not sum attribution systems as if they identify disjoint users. [Moscon, 12 Dec 2024](https://www.revenuecat.com/blog/growth/skadnetwork-guide-subscription-apps/), [Adapty discrepancies, read 16 Oct 2026](https://adapty.io/docs/discrepancies-and-troubleshooting).

### Connect this to the existing operations system

**Concrete proposed extension, not implemented:** add a **geo-test review card** to the existing dashboard approval inbox, backed by a separate acquisition-results module. A composition adapter outside sections would import campaign/cohort summaries and link them to existing creative/deliverable IDs. The acquisition module owns spend, attribution and cohort decisions; creator operations continues owning creators and deliverables.

The card should show the approved loss limit, countries, spend distribution, creative links, pending/mature cohort status, net economics and a continue/fix/stop recommendation. A scheduled read-only import can refresh it and feed results back into future creator briefs. Budget increases remain explicit captain approvals. This uses the existing generic inbox-extension seam described in [creator operations](../../../sections/creators/README.md), rather than creating a parallel creator tracker or coupling sections directly.

## Source table and reading ledger

All sources were read on **16 Oct 2026 local time**. “High” means suitable authority for the stated scope, not independently guaranteed truth. The archive contains `content.md`, `source.bin` and `result.json` where local extraction succeeded. “Read” means the substantive source content was inspected; a successful HTTP response alone did not qualify.

| ID | Source / URL | Author | Publication or visible update | Type | Trust and limits / use |
|---|---|---|---|---|---|
| 01 | [Location targeting](https://ads.tiktok.com/help/article/location-targeting) | TikTok for Business | Oct 2026 live capture; search cache showed an older date | Official platform doc | High for supported controls and geographic limitations; not a performance guarantee. |
| 02 | [Available location targeting options by market](https://ads.tiktok.com/help/article/placements-available-locations) | TikTok for Business | Jun 2025 | Official platform doc | High for account-registration dependency; exact eligible-country matrix was not extracted. |
| 03 | [Time zones](https://ads.tiktok.com/help/article/time-zone) | TikTok for Business | May 2025 | Official platform doc | High for clocks/converter; distinguish account time from DST scheduling conversion. |
| 04 | [Build campaigns with Smart+](https://ads.tiktok.com/business/en-US/blog/smart-plus-ai-performance-solution) | TikTok for Business | Published 13 May 2026; updated 5 Oct 2026 metadata | Official platform blog | High for product description; promotional performance claims were not adopted. |
| 05 | [State of Subscription Apps 2026](https://www.revenuecat.com/state-of-subscription-apps/) | RevenueCat research team; Jacob Eiting foreword | 2026; primarily 2025 observations | Data report | High for sample-specific descriptive patterns; selection bias, aggregation and internal text inconsistencies limit precision. |
| 06 / 39 | [State of Subscription Apps 2025 HTML](https://www.revenuecat.com/state-of-subscription-apps-2025/) and [PDF](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) | RevenueCat; AppsFlyer acquisition contribution by Shani Rosenfelder | 2025; core data primarily 2024; acquisition Oct 2023–Dec 2024 | Data report | High for historical, correctly labeled tables. Fitness appendix and acquisition charts visually checked. Same report, counted once. |
| 07 | [State of Subscription Apps 2024](https://www.revenuecat.com/state-of-subscription-apps-2024/) | RevenueCat | 2024 | Data report | High as historical evidence; read methodology/pricing/trial sections to check how stale benchmarks differ. Not a current forecast. |
| 08 | [Mojo's ARPU and country-price experiments](https://www.revenuecat.com/blog/growth/mojo-60-percent-arpu-growth-five-months/) | Michal Parizek, Mojo growth practitioner | 12 Oct 2023; visible update 6 Jun 2024 | Respected practitioner, hosted by vendor | Medium-high for described procedure; lifts are self-reported and not audited. |
| 09 | [Mojo customer case](https://www.revenuecat.com/customers/mojo-case/) | RevenueCat, quoting Michal Parizek and Bernard Bontemps | Undated; discusses 2023 results | Practitioner/vendor case study | Medium-high for operational detail; selected customer success story. |
| 10 | [Localization growth opportunity](https://www.revenuecat.com/blog/growth/is-localization-the-next-great-growth-opportunity-for-subscription-apps/) | Peter Meinertzhagen | 1 Mar 2023; updated 6 Jun 2024 | Practitioner/vendor article | Medium; useful demand-testing sequence, dated market figures. |
| 11 | [Country and audience offering customization](https://www.revenuecat.com/blog/growth/offering-customization-examples-targeting/) | RevenueCat editorial; named operator examples | 6 Dec 2023; updated 15 Jul 2024 | Practitioner/vendor article | Medium; implementation ideas and illustrative cases, not comparative experiments. |
| 12 | [Hybrid monetization](https://www.revenuecat.com/blog/growth/hybrid-monetization-techniques/) | Thomas Petit | 19 Jan 2026; updated 19 Mar 2026 | Respected practitioner | Medium-high for economic reasoning; anonymous app anecdote unverified. |
| 13 | [Target all countries for a purchase?](https://www.jonloomer.com/qvt/target-all-countries-for-a-purchase/) | Jon Loomer | 1 Jul 2023 | Respected practitioner | Medium; explicitly exploratory, not a validated worldwide-app case study. |
| 14 | [Worldwide versus core country structure](https://pubcast.jonloomer.com/videos/how-to-address-location-targeting-for-facebook-ads-when-you-have-a-worldwide-audience/) | Jon Loomer | 23 Dec 2022 episode; hosting metadata also contains a later update | Practitioner video page with readable explanation | Medium; read page explanation, not separately transcribed video. Lead-generation transfer limits apply. |
| 15 | [How Advantage+ Audience works](https://www.jonloomer.com/how-advantage-plus-audience-works/) | Jon Loomer | 30 Aug 2023; updated 1 Mar 2025 | Respected practitioner | Medium-high for demonstrated controls then; not current official app-specific verification. |
| 16 | [In-app purchase/subscription pricing and availability](https://developer.apple.com/help/app-store-connect/reference/pricing-and-availability/in-app-purchase-and-subscriptions-pricing-and-availability/) | Apple | Undated live doc | Official platform doc | High for storefront/offer configuration, not optimal price. |
| 17 | [Auto-renewable subscriptions](https://developer.apple.com/app-store/subscriptions/) | Apple | Undated live doc | Official platform doc | High for presentation and subscription operation; account-specific commercial terms still matter. |
| 18 | [Manage app availability](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/manage-availability-for-your-app-on-the-app-store/) | Apple | Undated live doc | Official platform doc | High for country availability/storefront; ExcerLock configuration not inspected. |
| 19 | [Localize app information](https://developer.apple.com/help/app-store-connect/manage-app-information/localize-app-information/) | Apple | Undated live doc | Official platform doc | High for metadata/binary distinction and screenshot inheritance. |
| 22 | [Learning phase](https://ads.tiktok.com/help/article/learning-phase) | TikTok for Business | Jun 2026 | Official platform doc | High for current wording; stabilization language is not an unconditional event requirement. |
| 23 | [Budgets](https://ads.tiktok.com/help/article/budget) | TikTok for Business | Jul 2026 | Official platform doc | High for generic budget floors; campaign-specific requirements may differ. |
| 25 | [Conversion to Paying chart](https://www.revenuecat.com/docs/dashboard-and-metrics/charts/conversion-to-paying-chart) | RevenueCat | Undated live doc | Official vendor documentation | High for its own cohort definition; other dashboards can define conversion differently. |
| 26 | [Android paywall conversion gap](https://www.revenuecat.com/blog/engineering/android-paywall-gap/) | Jaewoong Eum | 25 Mar 2026 | Vendor analysis of own report | Medium-high; explains funnel selection, not an isolated country experiment. |
| 27 | [Guide to mobile paywalls](https://www.revenuecat.com/blog/growth/guide-to-mobile-paywalls-subscription-apps/) | Michal Parizek | 5 Dec 2024; updated 21 Nov 2025 | Respected practitioner | Medium-high for operator process; regional observations are not universal cultural facts. |
| 28 | [Meta learning phase](https://www.jonloomer.com/facebook-ads-learning-phase/) | Jon Loomer | 8 Jan 2020; updated 1 Mar 2025 | Respected practitioner | Medium; historical explanatory reference, not verified 2026 app-campaign threshold. |
| 29 | [eCPI benchmarks](https://www.adjust.com/blog/ecpi-benchmarks/) | Prashansa Shrestha, Adjust | 30 Jul 2024; H1 2024 data | Data report/article | Medium for historical direction; organic-inclusive denominator and broad platform mix prevent direct paid-iOS comparison. Full page read through web fallback. |
| 30 | [Country grouping for quality leads](https://www.jonloomer.com/strategically-target-countries-for-quality-leads-with-meta-ads/) | Jon Loomer | 26 Jun 2023; updated 1 Mar 2025 | Respected practitioner | Medium-high for transparent firsthand setup; lead optimization, not subscription-app evidence. Hypothetical CPM examples not adopted as benchmarks. |
| 31 | [Post-ATT soft launch interview](https://mobileuseracquisitionshow.com/episode/how-to-run-a-soft-launch-in-a-post-att-world-with-faith-price-doubledown-interactive/) | Shamanth Rao interviewing Faith Price, DoubleDown Interactive | 20 Jan 2022 | Practitioner podcast with full transcript | Medium-high for firsthand process; gaming and early-ATT mechanics are dated. |
| 32 | [Analytics discrepancies](https://adapty.io/docs/discrepancies-and-troubleshooting) | Adapty | Undated live doc | Official vendor documentation | High for its own IP/store, cohort and reporting definitions. |
| 34 | [State of In-App Subscriptions 2026](https://adapty.io/state-of-in-app-subscriptions/) | Adapty | 5 Mar 2026 metadata; modified 31 Mar 2026 | Data report public overview | Medium-high for disclosed headline findings; full gated report not read and country tables not recovered. |
| 35 | [Duplicate into upgraded Smart+](https://ads.tiktok.com/help/article/how-to-duplicate-campaigns-into-smart-plus) | TikTok for Business | Oct 2026 | Official platform doc | High for documented App Promotion controls; rollout/account availability qualified in page. |
| 36 | [Meta testing frameworks for subscription apps](https://www.revenuecat.com/blog/growth/7-meta-ad-testing-frameworks-for-subscription-apps/) | Daphne Tideman interviewing Cedric Yarish | 19 Jun 2025 | Respected practitioners | Medium-high: named subscription-app spend experience; results and spend reported by interview, not audited. Software-vendor interest present. |
| 37 | [SKAdNetwork for subscription apps](https://www.revenuecat.com/blog/growth/skadnetwork-guide-subscription-apps/) | Lucas Moscon | 12 Dec 2024 | Practitioner technical guide | Medium-high for granularity caveats; current partner support still requires verification. |
| 38 | [SSOT attribution and apparent eCPI](https://www.appsflyer.com/blog/trends-insights/ssot-data-revealed/) | Naval Handa | Visible update 27 Nov 2025; examples refer to 2022 | Vendor data analysis | Medium for demonstrating denominator/deduplication risk; stale examples and product promotion limit use as a current forecast. |

### Missing coverage and fetch failures

| Attempt | What happened | What it does not establish |
|---|---|---|
| [Meta Advantage+ help](https://www.facebook.com/business/help/1362234537597370), [ad targeting](https://www.facebook.com/business/ads/ad-targeting), [additional help page](https://www.facebook.com/business/help/202297959811696) | Local extraction failed; web fallback showed login / temporarily blocked pages. Archived failure responses. | Current official Meta app-specific location, expansion and scheduling controls were not verified. No ad account was opened. |
| [AppsFlyer US paid Health benchmark](https://www.appsflyer.com/benchmarks/health___fitness/health/health___overall/united-states/paid/) | Extracted page returned “No platform data available” in chart areas. | This is missing chart coverage, not evidence that the US lacks fitness data or acquisition opportunity. |
| [TikTok app-promotion best-practices URL](https://ads.tiktok.com/help/article/best-practices-for-app-promotion-campaigns) | HTTP/extraction succeeded but body was an article-not-found message. | Excluded from the substantive source count. |
| [Adjust eCPI](https://www.adjust.com/blog/ecpi-benchmarks/) | Local request returned 429; full article readable through web research fallback and archived in `official-fallback.web.json`. | Not a missing source after fallback; do not count the fallback as a second source. |
| [Adjust Mobile App Trends 2026](https://www.adjust.com/resources/ebooks/mobile-app-trends-2026) | Local request failed; web discovery exposed report overview only. | Full report/country tables not read, not counted and no numeric results adopted. |
| [RevenueCat 2025 PDF](https://www.revenuecat.com/pdf/state-of-subscription-apps-2025.pdf) | `agent-web` exceeded its size limit and web PDF open also failed. A direct public download succeeded; text extracted and relevant charts rendered locally. | Initial fetch failure was recovered; PDF evidence above was actually inspected. |
| [Adapty 2026 full report](https://adapty.io/state-of-in-app-subscriptions/) | Public overview read; full report requires a form. No form submitted. | Public headline figures do not imply access to the full country breakdowns. |

## Open questions

1. What are ExcerLock's live countries, supported languages, minimum iOS version, actual trial, plans and local prices? What subscription/attribution stack is already working? The repository does not resolve current release readiness.
2. Does existing organic data show paying-user concentration or unusually strong net receipts in Canada, the UK, Australia or another country? That could change the expansion order.
3. What are the current **iOS-only, paid-only, Health & Fitness subscription** CPI, CPM, trial and net-revenue distributions for each channel in each named country? No fully comparable public dataset was recovered.
4. Is ExcerLock's audience better benchmarked against Health & Fitness, screen-time utilities or a combination? The Medical-inclusive fitness bucket is imperfect.
5. How predictive are trials, selected plan and early successful use of later net receipts within each country? Until observed, a global cost-per-trial target is weak.
6. Does a creative ranking learned in a cheaper country persist in US acquisition after equalizing objective, language, app route and sufficient spending? No controlled transfer study was found in the sources read.
7. Which Meta app-campaign location/expansion controls and TikTok upgraded Smart+ controls are actually available to the intended account? Public docs and rollout descriptions cannot answer account-specific availability.
8. What fraction of each channel-country cohort can be observed directly versus modeled or unassigned, and how long must trials/reports mature before a reliable decision?
9. What is the captain's maximum acceptable test loss and desired net-revenue payback window? The proposed allowance is a reviewable research recommendation, not a spending approval.

Raw archive: [`../raw/app-geo-targeting/`](../../../raw/paid-ads-research-2026-10-16/raw/app-geo-targeting/). It includes page captures, failure records, web fallback responses, the public PDF, extracted text, rendered chart pages and the capture script.
