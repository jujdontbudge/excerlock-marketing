# Meta ads fundamentals for ExcerLock

Captured 2026-10-16. Lane: `meta-fundamentals`. Audience: a founder who has never bought ads. The decision this report supports is how to design a first, bounded Meta experiment and interpret its results before committing more money.

Meta sells access to opportunities to influence people. Its system chooses among eligible ads, predicts which people will take the action an advertiser requests, and allocates delivery accordingly. The founder's work is to choose a useful outcome, supply trustworthy measurement, make persuasive and genuinely different ads, and decide whether the acquired customers repay their cost. A clever account structure cannot substitute for those things. This is my synthesis of the evidence below, not a promise of performance.

## Coverage and evidence limits

This report uses **38 substantive sources**, listed individually below: official Meta documentation, engineering articles and announcements; first-person practitioner articles and published podcast transcripts; an agency data report; and a Meta-branded creative playbook hosted by a practitioner. Additional Blueprint course descriptions and a current Tinuiti landing page were read but are explicitly separated from substantive research. Repeated captures and alternate fetch methods do not count as extra sources.

All dates and capabilities are as captured on **2026-10-16**, unless a publication or update date is given. Undated Help Center pages are snapshots, not proof of when a feature launched. Portuguese and Spanish Meta newsroom pages were read in their original text and paraphrased into English. Podcast evidence comes from the publisher's on-page transcripts, not an inference from a video title. This lane did not inspect any ad account, launch ads, obtain account-specific eligibility, or use paid scraping, platform access tokens or the Gemini API key. Paid scraping spend: **$0**.

Raw material is in [`../raw/meta-fundamentals/`](../../../raw/paid-ads-research-2026-10-16/raw/meta-fundamentals/). Each successful capture has `source.bin`, extracted `content.md` and `result.json` with URL, capture time and hash. Failed direct reads are retained. Rendering recovered the important Help Center pages; a direct-read failure is not evidence that a product does not exist. Some retrieved pages retain navigation or related articles: only the named article's relevant body is evidence.

Evidence labels used here:

- **Official:** Meta's description of its product, system or policies. Strong for documented behavior; platform performance claims still have selection and commercial incentives.
- **Practitioner:** what an identifiable operator observed, recommends or says they did. Useful hypotheses; not universal causal proof.
- **Data:** a report's measured sample, with its population and time window preserved.
- **Judgment / arithmetic:** my recommendation or worked example. These are not observed ExcerLock results or industry benchmarks.

## The 20 most important things to understand

### 1. The auction rewards expected value, not simply the highest bid

**Official.** When an impression opportunity occurs, eligible ads compete. Meta's current auction page names bid, estimated action rate and ad quality as the main inputs, with a price floor also affecting delivery and price. Its earlier explanation expresses advertiser value as bid multiplied by estimated action rate, with ad quality added to form total value. Better relevance can beat a higher bid. [Meta auction, undated; read 2026-10-16](https://www.facebook.com/business/help/430291176997542); [Meta's machine-learning explanation, 2020-06-11](https://www.facebook.com/business/news/good-questions-real-answers-how-does-facebook-use-machine-learning-to-deliver-ads).

Why this matters: a higher willingness to pay does not repair an ad that people ignore or dislike. Creative and the likelihood of the requested action affect competitiveness. Conversely, an unusually low CPM is not proof that an ad persuades buyers. The public formula is an explanation of the system, not enough information to calculate an actual auction clearing price yourself.

### 2. Your optimization event tells Meta what kind of success to search for

**Official.** Meta predicts the particular action the advertiser requests, and its app product can seek installs or in-app actions. An install, a trial and a paid subscription are different instructions, even if the same person could eventually do all of them. [Meta machine learning, 2020-06-11](https://www.facebook.com/business/news/good-questions-real-answers-how-does-facebook-use-machine-learning-to-deliver-ads); [Advantage+ app campaigns, undated; read 2026-10-16](https://www.facebook.com/business/help/309994246788275).

**Judgment.** Optimize toward the deepest economically useful event that is correctly instrumented, available in the chosen campaign and frequent enough to evaluate. If paid subscriptions are too sparse, trial starts may be a workable intermediate signal. Then explicitly measure whether those trials become paying customers. An install experiment can answer whether a message earns installs; it cannot, by itself, validate subscription acquisition. Buying cheap clicks to build up a counter is a different experiment again.

### 3. Andromeda retrieves candidates; it is not the whole delivery algorithm

**Official.** Andromeda is the retrieval stage that reduces tens of millions of candidate ads to a few thousand candidates for later ranking. Meta described it publicly in December 2024. The company separately described GEM's learning and knowledge transfer across recommendation models in November 2025, and Adaptive Ranking Model in March 2026. [Andromeda, 2024-12-02](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/); [GEM, 2025-11-10](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/); [Adaptive Ranking Model, 2026-03-31](https://engineering.fb.com/2026/03/31/ml-applications/meta-adaptive-ranking-model-bending-the-inference-scaling-curve-to-serve-llm-scale-models-for-ads/).

The useful implication is that Meta has improved its ability to match ads and people at scale. None of these engineering articles establishes that a small advertiser must publish a fixed weekly number of ads, that every decline is caused by Andromeda, or that an ad set must contain a full scripted funnel. Calling every change “Andromeda” makes diagnosis less precise. Loomer also argues against those explanations, but that is his interpretation, not proof that retrieval changes can never affect an individual advertiser. [Practitioner transcript, 2025-12-03](https://pubcast.jonloomer.com/stop-blaming-andromeda-for-your-results/).

### 4. Creative diversification means different reasons to care, expressed differently

**Official.** Meta distinguishes iteration from diversification. Changing a CTA on otherwise identical visuals is iteration; different customer situations, messages, visuals and formats provide genuinely different options. Meta also says it groups ads with similar visual and thematic attributes and shares learning and delivery optimization at the creative level. [Demystifying Creative Diversification, 2025-12-16; read 2026-10-16](https://www.facebook.com/business/news/demystifying-creative-diversification).

Why it works: people can buy the same app for different reasons. Someone who wants to leave the couch and someone who keeps missing planned gym visits may respond to different demonstrations. Broad delivery can exploit those differences only if the creative portfolio contains them.

**Practitioner.** Foxwell's “same message, new format” approach preserves a promising benefit while changing how it is demonstrated. Treat claims that Meta mechanically suppresses every similar edit as stronger than the evidence supports. Meta confirms grouping; it does not publish a universal similarity cutoff or a guaranteed penalty. [Courtney Fritts, 2025-06-30; page modified 2026-07-07](https://www.foxwelldigital.com/blog/what-counts-as-a-real-iteration).

### 5. Advantage+ is a family of tools, not a single on/off strategy

**Official.** Advantage+ app campaigns automate bidding, audiences and placements. Advantage+ campaign budget allocates money among ad sets. Advantage+ placements chooses inventory. Creative automation changes how assets can be presented. These controls solve different problems. Meta began testing a streamlined campaign setup in February 2025 and reported completing its sales and app rollout in Q2 2025. [Meta announcement, 2025-02-06](https://about.fb.com/br/news/2025/02/impulsione-o-desempenho-da-sua-campanha-com-os-novos-recursos-de-ia-do-advantage-e-recomendacoes-testadas-e-comprovadas/); [Q2 prepared remarks, 2025-07-30, PDF p. 7](https://s21.q4cdn.com/399680738/files/doc_downloads/2025/META-Q2-2025-Prepared-Remarks.pdf).

Why it matters: “Advantage+ worked” is incomplete unless someone says which objective, optimization event, controls, audience and measurement they used. Recommendations for an ecommerce sales campaign do not automatically describe the app campaign interface. A high opportunity score is also not a profit score: Meta explicitly says it does not guarantee actual or future performance. [App campaign documentation, read 2026-10-16](https://www.facebook.com/business/help/309994246788275).

### 6. Understand the hierarchy before deciding how much structure you need

**Practical interpretation of the documented controls.** A campaign holds the overall objective and can hold a shared budget. An ad set groups delivery choices such as optimization, schedule, audience and placements; some app controls instead live at account or app level. Ads supply the message, asset and destination. Exact fields depend on the campaign path. [Campaign budget documentation, read 2026-10-16](https://www.facebook.com/business/help/153514848493595); [App campaign documentation, read 2026-10-16](https://www.facebook.com/business/help/309994246788275); [Loomer's illustrated control comparison, 2025-05-05](https://www.jonloomer.com/advantage-plus-campaign-setup-targeting/).

**Judgment.** Add a separate campaign or ad set when a business decision requires separate treatment: a different objective, event, geography with different economics, hard spending commitment, or a controlled experiment. Different creative motivations alone do not require separate interest audiences. Structure should express decisions you actually intend to make.

### 7. Consolidation and broad targeting reduce artificial fragmentation

**Official.** Meta warns that many ads and ad sets leave less learning for each, and recommends combining similar ad sets. [Learning phase, undated; read 2026-10-16](https://www.facebook.com/business/help/112167992830700).

**Practitioner.** Loomer argues that audience expansion makes many interest and lookalike splits overlap, reducing the value of elaborate audience testing. His preferred default is simple structure, with exceptions for genuine business constraints. [Defaults guide, 2025-02-17; updated 2026-01-02](https://www.jonloomer.com/break-from-meta-advertising-defaults/).

Why it matters: splitting a small pool of spending and conversions among many units makes each unit harder to evaluate. “Broad” still requires a relevant market, compatible device and truthful creative. It does not mean all geographies are equally valuable or that every account will outperform interests. A claimed broad-versus-interests result also needs scrutiny if the “interest” arm was allowed to expand beyond that interest.

### 8. Audience suggestions are different from enforceable controls—and app campaigns have their own limits

**Official, particularly important for ExcerLock.** The current Advantage+ app page lists gender, demographics, interests, behaviors, custom audience inclusions and lookalikes as unsupported targeting options. It describes country, language and operating system targeting, account-level minimum age and location controls, and app-level custom audience exclusions and attribution settings. [Advantage+ app campaigns, read 2026-10-16](https://www.facebook.com/business/help/309994246788275).

**Practitioner, different product path.** Loomer's general Advantage+ Audience guide distinguishes hard controls from suggestions; his later sales setup walkthrough shows ways to make some demographic inputs restrictive. Those screenshots do **not** establish that the same switches exist in Advantage+ app campaigns. [Audience guide, 2024-02-26; updated 2025-03-06](https://www.jonloomer.com/advantage-plus-audience-best-practices-guide/); [Setup comparison, 2025-05-05](https://www.jonloomer.com/advantage-plus-campaign-setup-targeting/).

**Judgment.** “Women aged 18–30” can describe whom the ads speak to without being an enforceable delivery boundary in the automated app path. If exclusive delivery to that group is essential, verify an eligible alternative setup and its tradeoffs before proposing a campaign. Do not silently treat a suggestion as a restriction.

### 9. Placements are a portfolio of opportunities, not a popularity contest

**Official.** Advantage+ placements searches across eligible inventory for cost-effective delivery. The general documentation lists Facebook, Instagram, Messenger, WhatsApp, Audience Network and Threads; the app-specific page lists a narrower set. Availability depends on the actual campaign path, so a general list is not a promise that all surfaces support an iOS app ad. [Placements, read 2026-10-16](https://www.facebook.com/business/help/196554084569964/); [App campaigns, read 2026-10-16](https://www.facebook.com/business/help/309994246788275).

**Judgment.** Start with eligible automatic placements and prepare assets that remain readable in the actual previews. Do not choose Instagram-only simply because the intended audience sounds like Instagram users. Conversely, investigate placements producing cheap intermediate actions but poor downstream customers. A placement breakdown is descriptive: people, prices and auction conditions differ, so removing the apparently weakest placement is not automatically a controlled improvement. Loomer emphasizes that placement choices become especially sensitive when the objective is a cheap click rather than a meaningful conversion. [Practitioner defaults guide, updated 2026-01-02](https://www.jonloomer.com/break-from-meta-advertising-defaults/).

### 10. CBO and ABO answer a budget-allocation question, not a creative-quality question

**Official.** Advantage+ campaign budget—commonly called CBO—moves one shared budget among ad sets in real time. Meta explicitly says it need not split spending equally and recommends evaluating its combined campaign result. Ad set budgets—commonly called ABO—give separate spending allocations. There is also ad set budget sharing: up to **20%** of daily ad set budget can move among ad sets when campaign budget is not used. [Campaign budget](https://www.facebook.com/business/help/153514848493595); [Budget sharing](https://www.facebook.com/business/help/1388266028979935), both undated and read 2026-10-16.

**Judgment.** CBO fits when the outcomes have comparable value and allocation can be flexible. ABO fits a requirement to reserve spending for a market or test. If protected allocation matters, inspect whether sharing is enabled. With only one ad set, the allocation debate is largely irrelevant. Neither ABO nor CBO guarantees equal spending among the individual ads inside that set.

### 11. A daily budget is an average target, not a hard daily spending ceiling

**Official.** Meta's daily-budget page allows spending up to **75% above** the daily amount on a favorable day. For an unchanged budget running a full calendar week, the normal weekly limit is **7 times** the daily amount. Budget sharing can further change an individual ad set's limits; partial weeks and midweek changes have special calculations. [Daily budgets, read 2026-10-16](https://www.facebook.com/business/help/190490051321426); [Budget sharing, read 2026-10-16](https://www.facebook.com/business/help/1388266028979935).

**Arithmetic, not a result:** without sharing, an unchanged **$100/day** setting can mean **$175** on a particular day and **$700** over a full calendar week under those documented conditions. That does not authorize a founder's intended total experiment budget to be exceeded.

**Judgment.** Define both the total amount at risk and the pacing plan. For a bounded experiment, prefer a lifetime budget with a fixed schedule if supported by the chosen setup, or an explicit compatible spending limit. An alert is a notification, not a spending cap. Verify how all active campaigns and ad sets contribute to the total before eventual launch.

### 12. Learning is the search for stable delivery, not a certificate of profitability

**Official.** Meta currently says stability usually occurs after about **50 results in the week after an ad set's last significant edit**. It says learning-period CPA is usually higher and less stable, warns against excessive fragmentation, and says the system continues learning afterward. This is approximately **50 per ad set**, not a pool shared by every campaign in the account. [Learning phase, read 2026-10-16](https://www.facebook.com/business/help/112167992830700).

**Arithmetic.** A planning estimate is `weekly spend ≈ 50 × expected cost per optimization event`. At an assumed **$10/trial**, that is **$500/week**, about **$71/day**. At **$20/trial**, it is **$1,000/week**, about **$143/day**. These are hypothetical trial costs used to apply Meta's guideline, not ExcerLock forecasts or a mandatory platform minimum.

**Judgment.** A learning-limited label is a reason to examine signal volume and structure. It is not, by itself, a reason to abandon profitable delivery or optimize for irrelevant cheap events. Reaching the guideline does not prove a campaign is statistically significant or commercially viable.

### 13. Edits have costs, but freezing a bad experiment forever also has costs

**Official.** Meta lists targeting changes, creative changes, optimization-event changes, adding an ad, changing bid strategy and a pause of at least **7 days** among significant edits. Budget, bid-control and spending-limit changes depend on magnitude. Normal CBO redistribution does not itself restart learning. [Significant edits, read 2026-10-16](https://www.facebook.com/business/help/316478108955072).

Why it matters: repeatedly changing the question makes observed results hard to interpret. But learning is not something to avoid at any price; Meta's learning page explicitly says creative and strategy testing remain necessary. [Learning phase, read 2026-10-16](https://www.facebook.com/business/help/112167992830700).

**Judgment.** Separate operational checks from strategic decisions. Fix a broken destination, misfired event or wrong product claim promptly. Batch elective changes after a planned review. Keep a dated edit log. “Increase by 20% and you can never reset learning” is not a guarantee established by the current significant-edits page.

### 14. Bidding controls trade delivery freedom for cost or value constraints

**Official.** Highest volume seeks the most results from the budget; highest value focuses on purchase value. Cost per result goal and ROAS goal target average efficiency, with adherence explicitly not guaranteed. Bid cap limits an individual auction bid, not the final reported cost per customer. Meta recommends **50–100 or more weekly conversions** for best performance with goal-based bidding and advises establishing a baseline first when history is absent. [Bid strategies, read 2026-10-16](https://www.facebook.com/business/help/1619591734742116).

**Judgment.** Start with the available highest-volume/lowest-cost app option, while controlling financial exposure through the experiment budget. Tight cost goals can stop delivery if opportunities do not meet the target; typing a desirable CPA is not how you manufacture it. The general bid menu is not proof that every strategy is available for every app event. The app-specific page still uses “lowest cost” wording and lists a bid-cap option; verify actual eligibility later. [App campaign documentation, read 2026-10-16](https://www.facebook.com/business/help/309994246788275).

### 15. Normal delivery is not an equal-opportunity test of every ad

**Official.** Creative testing is a separate feature designed to give test ads delivery within an existing campaign; normal campaign budget allocation is explicitly unequal. Meta also groups similar creative and shares learning between it. [Creative testing](https://www.facebook.com/business/help/1423851372208214); [Campaign budget](https://www.facebook.com/business/help/153514848493595); [Diversification](https://www.facebook.com/business/news/demystifying-creative-diversification), all read 2026-10-16.

**Judgment.** If an ad receives little spend, the conclusion is “little delivery evidence,” not “customers rejected it.” If an ad receives most of the spending, that is Meta's allocation decision, not independent proof of incremental superiority. Distinguish finding an effective portfolio from answering a specific causal question. Those jobs can require different methods.

Loomer's July 2025 transcript argued against rigidly finding one winning copy/asset combination because ads have many placement and text variations. His January 2026 account then described testing and expanding in stages. These are useful operating approaches, not mutually exclusive laws. [2025-07-16 transcript](https://pubcast.jonloomer.com/its-time-to-revisit-creative-testing/); [2026-01-20 transcript](https://pubcast.jonloomer.com/stack-creative-diversity-in-phases/).

### 16. Choose a test method that can actually answer the question

**Official, current snapshot.** The creative-testing Help page describes **2–7 copies**, use of **Highest volume**, a test allocation from the existing budget, and a suggestion to use no more than **20%** of the existing budget to reduce disruption. If the only active ads are test ads, they may receive more. It says results have **no confidence level**, and ads keep running afterward unless stopped or their schedule ends. [Creative testing, read 2026-10-16](https://www.facebook.com/business/help/1423851372208214).

For a controlled strategy comparison, Meta's separate A/B testing page describes non-overlapping audience segments, recommends equal budgets and warns against informal on/off comparisons. [A/B testing, read 2026-10-16](https://www.facebook.com/business/help/1738164643098669).

**Judgment.** Use ordinary delivery to find whether a small portfolio can acquire useful customers. Use creative testing when delivery to a promising new concept is the unresolved question. Use an eligible Experiments A/B test for a sufficiently funded, clearly specified strategy comparison. Write the hypothesis, primary outcome, planned spending, duration and stopping rules first. Do not label a low-volume creative-test ranking “statistically proven.” Do not promise creative-test availability for this app setup: no account was inspected.

### 17. Creative fatigue is a diagnosis to establish, not a calendar deadline

**Practitioner disagreement.** Foxwell emphasizes sustained creative production and larger visual or structural changes. Loomer's July 2026 transcript argues that apparent fatigue can instead be a shift from easier remarketing conversions toward harder prospecting. Neither provides a controlled, representative study establishing how often each explanation is right. [Foxwell systems, 2025-08-25; modified 2026-08-04](https://www.foxwelldigital.com/blog/creative-velocity-amp-systems-how-to-keep-your-ads-fresh-without-burning-everyone-out); [Loomer fatigue transcript, 2026-07-01](https://pubcast.jonloomer.com/why-you-are-misdiagnosing-creative-fatigue/).

**Judgment.** Suspect saturation when comparable cohorts show worsening customer acquisition cost alongside repeated exposure, weaker response and limited new reach. Check auction prices, placement mix, audience mix, recent edits, product changes and reporting delay before assigning the cause. Frequency alone does not identify which person is tired of which message. Maintain a creative backlog; replace or supplement ads because the evidence and business result justify it, not because a universal expiry date passed. Audience-segment reporting described for sales campaigns may not be available in the same form for app campaigns.

### 18. Read metrics as connected stages, with explicit denominators

**Definitions and arithmetic used in this report, not benchmark claims.** The decision is where the cost of a useful customer is being created. These equations are bookkeeping identities when the inputs use the same compatible cohort, window and event definition; they are not a claim that privacy-limited Meta app reporting supplies a perfectly observed funnel.

| Metric | Definition used here | Question it helps answer |
|---|---|---|
| CPM | Spend ÷ impressions × 1,000 | What did access to attention cost? |
| Link CTR | Link clicks ÷ impressions | Did the ad motivate a destination click? Keep “all clicks” separate. |
| Outbound CTR | Outbound clicks ÷ impressions | Did the click leave Meta? Check the field's actual definition in the chosen report. |
| Hook rate | For our internal video diagnostic: 3-second video plays ÷ impressions | Did the opening hold attention? This is an operator-defined ratio, not a universal success threshold. |
| Hold rate | State the chosen numerator and denominator, such as 15-second plays ÷ 3-second plays | Did viewers keep watching? Compare compatible video lengths. |
| CPI | Spend ÷ attributed installs | What does the campaign/report call an acquired install? |
| Cost per trial | Spend ÷ attributed trial starts | What does acquisition of a trial cost? |
| Trial-to-paid | Mature trials converting to paid ÷ trials in that same cohort | Are we acquiring subscribers rather than only free users? |
| Paid CAC | Spend ÷ new paid subscribers in the defined cohort | Does a new paying customer cost less than their contribution? |
| ROAS | Attributed revenue ÷ spend, with revenue basis and horizon stated | How much credited revenue has returned so far? This is not automatically profit or incrementality. |
| Frequency | Impressions ÷ reached accounts for the selected window | How concentrated is exposure? It is an average. |

**Worked example, invented solely to explain the arithmetic:** **$20 CPM**, **1% link CTR**, **30% click-to-install**, and **20% install-to-trial** imply approximately **$2/click**, **$6.67/install**, and **$33.33/trial**. At an assumed mature **40% trial-to-paid**, that becomes about **$83.33 per payer**. Doubling CTR halves those downstream costs only if all subsequent rates and the audience mix remain unchanged. None of those inputs is an ExcerLock result or an industry norm. In actual reporting, view-attributed installs and delayed or modeled events can break that simple click funnel.

### 19. Diagnose where the funnel changed before changing the campaign

**Judgment, grounded in the auction, optimization and testing mechanics above.** Use the following as a sequence of questions, not one-to-one causal rules. Several problems can occur together.

| Observation | Plausible explanations to check | Useful next action |
|---|---|---|
| Little or no spend | Review/preparing status, billing restriction, incompatible event/setup, small eligible audience, restrictive bid target, schedule | Verify eligibility and delivery diagnostics before rewriting the ad. |
| Higher CPM; downstream rates stable | Auction competition, inventory or audience mix, relevance changes | Compare like-for-like periods and placements; calculate the actual effect on trial cost. |
| Plenty of impressions; weak link response | Unclear value, weak opening, wrong message or inadequate demonstration | Test a meaningfully different concept with the same destination. |
| Strong early video attention; weak destination response | Entertaining opening with little product relevance; unclear next step | Make the product's mechanism and reason to install clearer. |
| Clicks; few installs | Broken or mismatched destination, unsupported device, store listing mismatch, low-intent clicks, attribution gaps | Exercise the whole destination flow and inspect store analytics. |
| Installs; few trials | Misleading ad promise, permission friction, onboarding/paywall problem, missing events | Compare app analytics and the actual onboarding before blaming targeting. |
| Cheap trials; expensive paid customers | Low-quality intent, trial cancellation, pricing, product disappointment or immature cohorts | Wait for the defined cohort to mature and compare paid conversion and refunds. |
| Meta conversions change; backend does not | Attribution window/category change, delayed reporting, SDK/MMP event issue, double counting | Reconcile definitions and timestamps before making a budget decision. |
| CPA rises after scaling | More expensive marginal customers, audience/placement shift, fatigue, tracking change | Examine the extra spend and extra mature customers, not just the old blended average. |

Use external price benchmarks as context, not targets. In Tinuiti's **Q2 2025** managed-advertiser sample, Facebook CPM fell **5% year over year** while Instagram CPM rose **12%**; combined Meta CPM was roughly flat. The platform mix can therefore change the account average without a uniform change in the auction. This is a historical agency sample, not a US iOS fitness CPI benchmark. [Tinuiti Q2 2025 report, read 2026-10-16](https://tinuiti.com/research-insights/research/digital-ads-benchmark-report-q2-2025/).

### 20. Attribution helps steer delivery; incremental contribution decides whether growth pays

**Official.** Meta calls incrementality experiments such as Conversion Lift the best way to answer which outcomes would otherwise not have happened. Its March 2026 measurement announcement says click-through attribution for **website and in-store conversions** is changing to link clicks only; shares, saves and other non-link actions move into a renamed engage-through category. Do not extend that stated scope into a blanket claim about all iOS app attribution. [Meta measurement announcement, 2026-03-03](https://about.fb.com/ltam/news/2026/03/simplificando-la-medicion-de-anuncios-para-un-mundo-social-first/).

**Judgment.** Keep Meta reporting, app/store or subscription reporting, and any eventual MMP comparison side by side with attribution window, timezone, currency and cohort maturity stated. Do not add conversions credited by multiple platforms as though they were distinct people. Use net contribution after store fees, refunds and variable costs when deciding affordable acquisition, and choose a payback horizon the business can fund. A larger account can investigate lift experiments; a small first test should not pretend a noisy before/after revenue change proves incrementality.

Foxwell's operating advice is to plan spending increases and maintain a creative pipeline rather than reactively raising and cutting spend. The transferable lesson is disciplined decisions. Specific ecommerce scale claims do not establish app economics. [Scaling discipline, 2025-08-26; modified 2026-08-04](https://www.foxwelldigital.com/blog/scaling-isnt-about-hacks-its-about-discipline).

## What changed, what conflicts, and what advice to stop repeating

| Issue | Evidence and timing | How to use it now |
|---|---|---|
| “Andromeda launched last month and changed everything” | Engineering publication: [2024-12-02](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/). Other ranking improvements followed in [2025](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/) and [2026](https://engineering.fb.com/2026/03/31/ml-applications/meta-adaptive-ranking-model-bending-the-inference-scaling-curve-to-serve-llm-scale-models-for-ads/). | Treat a claimed universal account-level switchover date as unverified unless evidence establishes it. |
| Separate “manual vs Advantage+” tutorials | Meta announced streamlined setup testing [2025-02-06](https://about.fb.com/br/news/2025/02/impulsione-o-desempenho-da-sua-campanha-com-os-novos-recursos-de-ia-do-advantage-e-recomendacoes-testadas-e-comprovadas/) and completion for sales/apps in [Q2 2025](https://s21.q4cdn.com/399680738/files/doc_downloads/2025/META-Q2-2025-Prepared-Remarks.pdf). | Learn the controls and objective, not only the old button sequence. |
| “Broad” vs interest targeting | [Loomer, 2025-05-05](https://www.jonloomer.com/advantage-plus-campaign-setup-targeting/) explains expansion and suggestions; [current app docs, read 2026-10-16](https://www.facebook.com/business/help/309994246788275) list interests as unsupported in that path. | Check whether a proposed interest test is available and actually restrictive. |
| A quota of creatives is the key | [Meta diversification, 2025-12-16](https://www.facebook.com/business/news/demystifying-creative-diversification) recommends a portfolio reflecting different people and needs. The [Meta-branded playbook, hosted 2025-10](https://perpetualtraffic.com/wp-content/uploads/2025/10/Creative-Diversification-Playbook-Practitioner-Guidance.pdf) contains example production cadences and an expansion matrix. [Loomer, 2026-01-20](https://pubcast.jonloomer.com/stack-creative-diversity-in-phases/) argues for phased output on smaller budgets. | The PDF's example cadence is not a platform prerequisite. Also, the current [learning page, read 2026-10-16](https://www.facebook.com/business/help/112167992830700) still warns against excessive ads/ad sets. Diversity and signal concentration must be balanced. |
| “Every small edit is worthless” | [Foxwell, 2025-06-30](https://www.foxwelldigital.com/blog/what-counts-as-a-real-iteration) strongly favors new format/visual structure; [Meta, 2025-12-16](https://www.facebook.com/business/news/demystifying-creative-diversification) says iteration can inform diversification. | Preserve purposeful iteration; do not count minor edits as new strategic concepts or infer a universal suppression rule. |
| “The creative test supports five ads” | [Loomer's illustrated article, 2025-10-13; updated 2026-01-02](https://www.jonloomer.com/meta-creative-testing/) describes an older limit. The [official page read 2026-10-16](https://www.facebook.com/business/help/1423851372208214) says up to seven and no confidence level. | Current official wording wins; actual availability still needs account verification. |
| “Always begin every ad with a creative test” | Loomer's [January 2026](https://pubcast.jonloomer.com/stack-creative-diversity-in-phases/) process shifts in his [2026-05-04 transcript](https://pubcast.jonloomer.com/dont-get-attached-to-your-ad-process/) toward possible Push Delivery and a new creative workflow. He explicitly did not yet have Push Delivery. | An account rollout observation and intended future workflow are not proof of universal availability or tested success. |
| “You must refresh every few days” | [Foxwell systems, 2025-08-25](https://www.foxwelldigital.com/blog/creative-velocity-amp-systems-how-to-keep-your-ads-fresh-without-burning-everyone-out) stresses a production system; [Loomer, 2026-07-01](https://pubcast.jonloomer.com/why-you-are-misdiagnosing-creative-fatigue/) argues fatigue is often misdiagnosed. | Keep a backlog and review comparable business outcomes. Neither source establishes a universal expiry period. |
| “A daily budget cannot exceed its face value” | [Daily budget docs, read 2026-10-16](https://www.facebook.com/business/help/190490051321426) describe flexibility and special calculations; [Loomer, 2023-11-01; updated 2025-03-01](https://www.jonloomer.com/updates-to-meta-ads-budgeting/) documents the earlier rollout. | Use current official limits and an explicit total experiment cap. |
| “ABO guarantees each set stays at its chosen allocation” | [Budget sharing, read 2026-10-16](https://www.facebook.com/business/help/1388266028979935). Launch date not established. | Inspect sharing; do not assume ABO means completely isolated allocations. |
| “Switch to engagement to exit learning” | The older [Loomer learning article, 2020-01-08; updated 2025-03-01](https://www.jonloomer.com/facebook-ads-learning-phase/) suggests lighter events and includes an illustrative audience-size allocation model. Current [Meta learning docs, read 2026-10-16](https://www.facebook.com/business/help/112167992830700) describe stability and consolidation. | Do not adopt the older article's shortcut as subscription strategy or treat its audience-size arithmetic as Meta's CBO allocation algorithm. |
| Historical ROAS comparisons | [Meta, 2026-03-03](https://about.fb.com/ltam/news/2026/03/simplificando-la-medicion-de-anuncios-para-un-mundo-social-first/) announces changed website/store attribution categories. | Record whether the reported series has comparable definitions; distinguish accounting shifts from demand shifts. |
| “Everything announced is already in every account” | [Meta's 2026-10-06 update](https://about.fb.com/ltam/news/2026/10/advertising-week-new-york-2026-nuevas-capacidades-de-ia-para-guiar-campanas-y-llegar-a-los-clientes/) mixes broader Ads Creative Studio rollout, tested assistant functions, general availability of Customer Lifecycle Strategy, and audience discovery planned later in the year. | Preserve the words testing, rolling out and coming later. Do not design the first experiment around an unverified feature. |

## What this means for ExcerLock — my judgment, dated 2026-10-16

These are proposed decisions for review, not an instruction to spend or a benchmark-derived guarantee.

### Start with the business question and the actual app

The initial question should be: **Can a truthful demonstration of movement-gated access acquire trials that become paying subscribers at a sustainable cost?** Before eventual launch, verify store availability, target market, price, trial duration and usable instrumentation. The canonical product description says ExcerLock restricts selected apps under distinct exercise conditions, and explicitly leaves current build/release status unverified. Demonstrate one working condition at a time. [Local product source, read 2026-10-16](../../../core/product.md).

Propose an **adult-only initial test**, with **18 as the enforceable minimum age** where the account/app setup permits it. This narrows the captain's wider 16–30 audience for the first experiment; it is my recommendation, not a reinterpretation of the brief. Meta's teen policy removes gender and interest-based teen targeting and prohibits weight-loss ads to under-18s. An adult movement/follow-through proposition is a cleaner first question than combining adult and teen acquisition with fat-loss messaging. [Meta teen announcement, 2023-01-10; updated 2023-01-18; read 2026-10-16](https://about.fb.com/news/2023/01/age-appropriate-ads-for-teens/). This is a documented platform restriction, not a claim about the legal classification of ExcerLock.

### Proposed structure and initial budget

| Decision | Starting proposal and reason |
|---|---|
| Market | One commercially relevant, supported country, initially the US **if** the store listing, product and price support it. Do not mix cheap countries into the test to make CPI look better. |
| Campaign | One app-promotion acquisition campaign, using an eligible Advantage+ app path as the starting candidate. Record the exact event, attribution and available controls before approval. |
| Ad sets | One initial delivery pool/ad set where the interface allows it. Do not split walking, gym and screen-time motivations into separate low-budget audiences. |
| Targeting | Broad eligible iOS audience in that country; adult minimum enforced through the supported control. Creative speaks to women, but the automated app path does not promise women-only or a hard maximum age of 30. |
| Optimization | Prefer a verified trial event if available and sufficiently frequent. Use an install-only pilot only if the stated learning goal is installs and all downstream rates are still measured. Resolve purchase-versus-trial eligibility with the app-UA lane. |
| Bid strategy | Available highest-volume/lowest-cost option initially. Add cost/value constraints only after a credible baseline and confirmed support. |
| Placements | Eligible automatic placements, with previews checked for readable product proof. |
| Creative starting set | **4–6** genuinely different concepts ready; run a small initial portfolio rather than every possible variant. Proposed production scope, not Meta's required count. |
| First spending envelope | Propose **$50–$100/day equivalent for 14 days**, with a total media ceiling of **$700–$1,400** using a supported lifetime budget or compatible spending limit. Production and measurement costs are separate. These are my risk-sizing choices; no ExcerLock CPA is known. |
| If funds are smaller | Make it one narrow hypothesis, a smaller portfolio and explicit directional learning. Do not call a handful of trials a validated scalable acquisition channel. |
| Further spending | A separate decision after mature paid conversion and contribution are visible. A second tranche should follow evidence, not automatically follow the first schedule. |

At an assumed trial cost of **$10**, the proposed daily range buys an expected **35–70 trials/week**; at an assumed **$20**, about **18–35/week**. These are simple spend/cost scenarios, not forecasts. They show why even this range may remain below Meta's approximate learning guideline. If trial cost is much higher, reduce the claims the experiment can answer before increasing risk. [Guideline: Meta learning phase, read 2026-10-16](https://www.facebook.com/business/help/112167992830700).

### The creative concepts to make first

These are concept briefs, not finished hooks, scripts or claims of observed winners. They need current-build proof and the normal creative approval workflow.

| Concept | What the viewer sees | What we learn |
|---|---|---|
| Walking changes selected-app access | A real selected app blocked while stationary, then the verified walking condition demonstrated on the same phone | Whether the core mechanism is immediately understandable and desirable. |
| Step target and follow-through | A real step-goal condition, progress and the verified unlock state | Whether a concrete finish line is more motivating than active walking. |
| Gym routine | A creator demonstrates one working gym condition without exposing personal location | Whether gym follow-through recruits different useful customers. |
| Ordinary creator experience | A creator explains a real situation in which scrolling displaced movement, then demonstrates their actual setup and use | Whether personal context improves qualified response beyond a standalone demo. No invented transformation or testimonial. |
| Product-first static | A readable real app screen plus a simple explanation of selected-app blocking and the exercise condition | Whether a low-cost image can communicate the proposition without a talking head. |
| Objection answered with proof | Demonstrate one verified setup question, such as selecting which apps are restricted | Whether clarity about control and setup removes adoption friction. Do not invent override or safety features. |

The selection follows Meta's distinction between customer motivations, visuals and formats, and Foxwell's use of real objections to create clearer concepts. It does not import Foxwell's anonymous outcome claims as forecasts. [Meta, 2025-12-16](https://www.facebook.com/business/news/demystifying-creative-diversification); [Courtney Fritts, 2025-06-30; modified 2026-07-07](https://www.foxwelldigital.com/blog/mapping-objections-into-ad-angles).

**Proposed production specification:** make vertical **9:16** videos suitable for Reels/Stories, then prepare placement-appropriate crops and a static option as needed. Keep the essential product proof and captions visible in preview. Begin with concise demonstrations and creator explanations; test length based on whether the story earns the extra time. There is no evidence here for a universal ideal duration. Review automatic enhancements so they do not fabricate UI, alter the demonstrated access rule or imply unsupported results. The Meta-branded playbook supports mixing formats and levels of polish, but its example asset matrix is not a quota for this budget. [Playbook, undated; hosted 2025-10, pp. 2–8](https://perpetualtraffic.com/wp-content/uploads/2025/10/Creative-Diversification-Playbook-Practitioner-Guidance.pdf).

### What to measure and when to decide

**My proposed operating cadence:** check delivery, spend and event health daily; make elective creative/structure decisions at a planned weekly review; evaluate paid conversion only after the relevant trial cohort matures and the chosen reporting lag has passed. A two-week media schedule does not imply a two-week final payback verdict if the trial or refund window is longer.

Record campaign/ad/asset IDs, creative motivation, spend, impressions, reach, frequency, placement, link/outbound clicks, video diagnostic rates with named denominators, attributed installs and trials, and the exact attribution setting. Separately retain backend install/onboarding/trial counts where available, mature new paid subscribers, net revenue, refunds and the payback horizon. Preserve unknown matches instead of pretending every subscription can be joined to an individual Meta ad.

Set allowable acquisition cost from contribution economics. **Arithmetic illustration only:** if an acquired payer contributes **$40** over the chosen payback window, allocating **$25** as the desired maximum paid CAC leaves **$15** for uncertainty and other costs. If mature trial-to-paid is **40%**, a **$25** paid-CAC target implies approximately **$10 allowable cost per trial** before accounting for mismatches and other adjustments. All values are hypothetical; ExcerLock pricing, fees, retention and trial quality must supply the real inputs.

Pre-agree a financial loss limit and pause on broken tracking, an unusable destination or a false product claim. Otherwise review comparable, matured cohorts before making changes. Do not use “pause after exactly this many clicks” or “kill at exactly this CPM” rules without connecting the spending and uncertainty to the business outcome. A concept that receives little delivery remains unresolved. Where a controlled test is justified and available, fund it explicitly rather than repeatedly relaunching the same ad to force exploration. [Meta A/B testing, read 2026-10-16](https://www.facebook.com/business/help/1738164643098669).

### Connect the feedback to the existing operations system

**Proposal only; nothing implemented or scheduled.** Reuse the creator dashboard's generic inbox-extension seam for a weekly paid-creative review. A small independent paid-media module would own campaign configuration, raw spend snapshots, attributed outcome definitions and cohort maturity. A composition adapter outside the sections would attach approved creative IDs to read-only performance summaries and create review items for the captain: keep, revise, investigate measurement, or propose a new test.

The dashboard should show the approved source asset, its motivation, spending and mature trial/paid outcome with evidence labels. A scheduled job could draft the weekly summary; budget or publication decisions remain in the approval inbox. This avoids a second creative tracker and avoids making the creators section depend on a paid-ads section. Keep paid outcomes distinct from the existing organic view/comment verdicts: paid and organic distribution answer different questions. Existing seams: [creator operations README, read 2026-10-16](../../../sections/creators/README.md).

## Source table

Every source below was captured/read on **2026-10-16**. “High” means trustworthy for the stated use, not proof of guaranteed results. Unknown publication dates remain unknown. Raw folder names refer to `../raw/meta-fundamentals/`. A page's capture is independent of any claimed launch date.

| # | Source and URL | Author; publication/update date | Type; trust and limits | What it contributes; raw folder |
|---|---|---|---|---|
| 1 | [About ad auctions](https://www.facebook.com/business/help/430291176997542) | Meta; undated | Official platform doc; **high** for current documented auction inputs; no proprietary weights disclosed | Auction, price floor, relevance; `02-auction-render` |
| 2 | [How Does Facebook Use Machine Learning to Deliver Ads?](https://www.facebook.com/business/news/good-questions-real-answers-how-does-facebook-use-machine-learning-to-deliver-ads) | Facebook for Business; 2020-06-11 | Official platform explanation; **high** for conceptual formula, **historical** for surrounding targeting/quality examples | Expected action and total value; `04-ml-auction` |
| 3 | [Meta Andromeda](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/) | Chonglin Sun, Nancy Yu, Haiyu Lu, Liang Wang, Yunchen Pu, Gaoxiang Liu, Neeraj Bhatia, GP Musumeci; 2024-12-02 | Official engineering article; **high** for architecture; performance lifts are Meta's own selected/system results | Retrieval versus ranking; `01-andromeda` |
| 4 | [GEM](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/) | Huayu Li et al.; 2025-11-10 | Official engineering article; **high** for system role; own performance claims | Foundation model and knowledge transfer; `23-gem` |
| 5 | [Adaptive Ranking Model](https://engineering.fb.com/2026/03/31/ml-applications/meta-adaptive-ranking-model-bending-the-inference-scaling-curve-to-serve-llm-scale-models-for-ads/) | Xi Chen et al.; 2026-03-31 | Official engineering article; **high** for described architecture, not a buyer's account-level causal diagnosis | Ranking development after Andromeda; `24-ranking-2026` |
| 6 | [Advantage+ features and opportunity score](https://about.fb.com/br/news/2025/02/impulsione-o-desempenho-da-sua-campanha-com-os-novos-recursos-de-ia-do-advantage-e-recomendacoes-testadas-e-comprovadas/) | Krassimir Karamfilov and Guillermo Spiller; 2025-02-06 | Official announcement, Portuguese; **high** for announced testing, promotional for performance claims | Streamlined setup chronology; `05-meta-advantage-announcement` |
| 7 | [Q2 2025 prepared remarks](https://s21.q4cdn.com/399680738/files/doc_downloads/2025/META-Q2-2025-Prepared-Remarks.pdf) | Meta; Mark Zuckerberg and Susan Li prepared remarks; 2025-07-30 | Official investor document; **high** for Meta's stated rollout completion; not independent ad-return evidence | Relevant advertising section, especially p. 7; `06-q2-2025-remarks` |
| 8 | [Demystifying Creative Diversification](https://www.facebook.com/business/news/demystifying-creative-diversification) | Meta for Business; 2025-12-16 | Official platform article; **high** for its guidance and stated similarity grouping; no public suppression threshold | Diversification vs iteration; `25-diversification-official` |
| 9 | [About Advantage+ app campaigns](https://www.facebook.com/business/help/309994246788275) | Meta; undated | Official platform doc; **high** for snapshot, but names/controls can vary and this account was not checked | App-specific automation, targeting limits, settings locations; `42-app-campaigns` |
| 10 | [About Advantage+ placements](https://www.facebook.com/business/help/196554084569964/) | Meta; undated | Official platform doc; **high** for generic placement guidance, not proof every placement supports every objective | Inventory choices; `29-placements-render` |
| 11 | [About Advantage+ campaign budget](https://www.facebook.com/business/help/153514848493595) | Meta; undated | Official platform doc; **high** for budget-allocation behavior | Unequal spending, campaign evaluation; `45-campaign-budget` |
| 12 | [About ad set budget sharing](https://www.facebook.com/business/help/1388266028979935) | Meta; undated | Official platform doc; **high** for current mechanism; launch date not stated | Sharing and spending calculations; `38-budget-sharing-render` |
| 13 | [About daily budgets](https://www.facebook.com/business/help/190490051321426) | Meta; undated | Official platform doc; **high** for spending limits, with special cases preserved | Pacing, weekly limits, lifetime-budget distinction; `39-daily-budget-render` |
| 14 | [About bid strategies](https://www.facebook.com/business/help/1619591734742116) | Meta; undated | Official platform doc; **high** for generic strategies, not app-specific eligibility | Spend-based, goal-based, manual bidding; `43-bid-strategies` |
| 15 | [About the learning phase](https://www.facebook.com/business/help/112167992830700) | Meta; undated | Official platform doc; **high** for current guideline; approximate stability reference, not a performance guarantee | Signal concentration and learning; `03-learning-render` |
| 16 | [Significant edits and learning phase](https://www.facebook.com/business/help/316478108955072) | Meta; undated | Official platform doc; **high** for named edits; no universal safe budget-change percentage | Edit costs and CBO exceptions; `41-significant-edits-render` |
| 17 | [Set up a creative test](https://www.facebook.com/business/help/1423851372208214) | Meta; undated | Official platform doc; **high** for captured limits and no-confidence-level wording; account availability unknown | Current creative-test mechanics; `40-creative-test-render` |
| 18 | [About A/B testing](https://www.facebook.com/business/help/1738164643098669) | Meta; undated | Official platform doc; **high** for controlled comparison design | Non-overlap and informal-test limitations; `44-ab-test` |
| 19 | [Simplifying measurement for a social-first world](https://about.fb.com/ltam/news/2026/03/simplificando-la-medicion-de-anuncios-para-un-mundo-social-first/) | Meta; no named editorial byline; 2026-03-03 | Official announcement, Spanish; **high** for announced change and stated scope, rollout/account timing unverified | Website/store click and engage-through attribution; `16-attribution-change` |
| 20 | [Advertising Week New York 2026](https://about.fb.com/ltam/news/2026/10/advertising-week-new-york-2026-nuevas-capacidades-de-ia-para-guiar-campanas-y-llegar-a-los-clientes/) | Meta; no named editorial byline; 2026-10-06 | Official announcement, Spanish; **high** for announced status; future/tested features are not universal availability | Most recent feature/rollout distinctions; `37-october-update` |
| 21 | [Age-appropriate ads for teens](https://about.fb.com/news/2023/01/age-appropriate-ads-for-teens/) | Meta; 2023-01-10; updated 2023-01-18 | Official policy announcement; **high** for the stated teen restrictions; not a complete fresh policy audit | Teen targeting and weight-loss ad restriction; `27-teens` |
| 22 | [Does Advantage+ setup impact targeting control?](https://www.jonloomer.com/advantage-plus-campaign-setup-targeting/) | Jon Loomer; 2025-05-05 | Respected practitioner; **medium-high**, illustrated first-person product walkthrough, primarily generic/sales setup | Controls versus suggestions and interface changes; `10-targeting-controls` |
| 23 | [When to break from Meta defaults](https://www.jonloomer.com/break-from-meta-advertising-defaults/) | Jon Loomer; 2025-02-17; updated 2026-01-02 | Respected practitioner; **medium-high** for reasoned exceptions, not controlled universal evidence | Structure, placement, event-quality and bidding tradeoffs; `11-defaults` |
| 24 | [Meta's Creative Testing Tool](https://www.jonloomer.com/meta-creative-testing/) | Jon Loomer; 2025-10-13; visible update 2026-01-02, metadata UTC 2026-01-03 | Respected practitioner; **medium-high**, screenshots and own test; older limits superseded by official snapshot | Test workflow and limits of portability; `09-creative-test` |
| 25 | [Stop Blaming Andromeda](https://pubcast.jonloomer.com/stop-blaming-andromeda-for-your-results/) | Jon Loomer; 2025-12-03 | Published podcast transcript; **medium**, reasoned interpretation; categorical causal dismissal goes beyond evidence | Misconceptions and volume myth; `12-andromeda-myths` |
| 26 | [Stack Creative Diversity in Phases](https://pubcast.jonloomer.com/stack-creative-diversity-in-phases/) | Jon Loomer; 2026-01-20 | Published podcast transcript; **medium**, own lead-generation workflow rather than app experiment | Budget-aware phased testing; `17-stack-creative` |
| 27 | [Don't Get Attached to Your Ad Process](https://pubcast.jonloomer.com/dont-get-attached-to-your-ad-process/) | Jon Loomer; 2026-05-04 | Published podcast transcript; **medium**, explicitly partial-rollout and partly intended future use | Process evolution; unverified availability of Push Delivery; `14-testing-evolution` |
| 28 | [Misdiagnosing Creative Fatigue](https://pubcast.jonloomer.com/why-you-are-misdiagnosing-creative-fatigue/) | Jon Loomer; 2026-07-01 | Published podcast transcript; **medium**, useful alternative diagnosis, anecdotes not prevalence research | Remarketing/prospecting mix and frequency caveats; `13-fatigue` |
| 29 | [Time to Revisit Creative Testing](https://pubcast.jonloomer.com/its-time-to-revisit-creative-testing/) | Jon Loomer; 2025-07-16 | Published podcast transcript; **medium**, dated opinion; later tools change the workflow | Portfolio versus a single fixed asset winner; `33-testing-2025` |
| 30 | [What Counts as a Real Iteration?](https://www.foxwelldigital.com/blog/what-counts-as-a-real-iteration) | Courtney Fritts / Foxwell Digital; 2025-06-30; article metadata modified 2026-07-07 | Respected practitioner; **medium**, concrete framework but asserted algorithmic mechanisms lack controlled proof | Same benefit in a different format; `18-real-iteration` |
| 31 | [Creative Velocity & Systems](https://www.foxwelldigital.com/blog/creative-velocity-amp-systems-how-to-keep-your-ads-fresh-without-burning-everyone-out) | Andrew Foxwell; 2025-08-25; article metadata modified 2026-08-04 | Respected practitioner article summarizing operator discussion; **medium**; cadence is an example | Ownership, backlog, creative review and landing-page match; `19-creative-systems` |
| 32 | [Scaling Isn't About Hacks](https://www.foxwelldigital.com/blog/scaling-isnt-about-hacks-its-about-discipline) | Andrew Foxwell; 2025-08-26; article metadata modified 2026-08-04 | Respected practitioner; **medium**, qualitative operator advice, ecommerce context | Planned pacing and decision rules; `20-scaling-discipline` |
| 33 | [Mapping Objections Into Ad Angles](https://www.foxwelldigital.com/blog/mapping-objections-into-ad-angles) | Courtney Fritts; 2025-06-30; article metadata modified 2026-07-07 | Respected practitioner; **medium** for process, **low** for unnamed outcome anecdotes | Research questions for new concepts; `34-objections` |
| 34 | [Digital Ads Benchmark Report Q2 2025](https://tinuiti.com/research-insights/research/digital-ads-benchmark-report-q2-2025/) | Tinuiti research team; data period Q2 2025; no article publication date established; modified 2026-01-26 | Data report; **medium-high** for its managed-client, same-client trends; selection bias, not subscription-app norms | Platform CPM divergence, relevant paid-social section and methodology read; `21-tinuiti-q2-2025` |
| 35 | [Creative Diversification Playbook](https://perpetualtraffic.com/wp-content/uploads/2025/10/Creative-Diversification-Playbook-Practitioner-Guidance.pdf) | Meta-branded material; no named author/date in PDF; host path 2025-10 | Platform-branded practitioner-hosted PDF; **medium**, provenance weaker than a first-party URL; selected case study | Entire 12-page playbook read; motivators, exploration/expansion, formats; `35-creative-playbook` |
| 36 | [Facebook Ads and the Learning Phase](https://www.jonloomer.com/facebook-ads-learning-phase/) | Jon Loomer; 2020-01-08; updated 2025-03-01 | Respected practitioner; **historical/medium**; some tactics and illustrative allocation assumptions should not be adopted today | Identifies stale advice, not a subscription optimization prescription; `30-learning-practitioner` |
| 37 | [Updates to Meta Ads Budgeting](https://www.jonloomer.com/updates-to-meta-ads-budgeting/) | Jon Loomer; 2023-11-01; updated 2025-03-01 | Respected practitioner; **medium-high** for screenshots of earlier rollout, not current account eligibility | Historical daily-budget flexibility; `15-daily-budgets` |
| 38 | [Advantage+ Audience Best Practices Guide](https://www.jonloomer.com/advantage-plus-audience-best-practices-guide/) | Jon Loomer; 2024-02-26; updated 2025-03-06 | Respected practitioner; **medium-high** for the illustrated historical interface, not current app-specific controls | Earlier control/suggestion distinction; `31-advantage-audience` |

### Additional pages read, not counted toward the substantive-source total

| Source and URL | Author/date/type/trust | Exactly what was accessible; raw folder |
|---|---|---|
| [Performance 5](https://www.facebookblueprint.com/student/path/253157-performance-5) | Meta Blueprint; undated; official course listing; **high** for outline only | Public page/HTML outline: simplification, automation, creative diversification, data quality, validation. Lessons not completed; `07-blueprint-performance5` |
| [Grow your audience with app campaigns](https://www.facebookblueprint.com/student/activity/580818-grow-your-audience-with-advantage-app-campaigns) | Meta Blueprint; undated; official course overview; **high** for syllabus only | Public description only; no claim to having watched the training; `08-blueprint-app` |
| [Buying type and bid strategy](https://certifications.facebookblueprint.com/student/collection/606095/path/607444) | Meta Blueprint; undated; official course listing; **high** for outline only | Public course outline, not underlying lesson content; `26-blueprint-bidding` |
| [Optimize Campaign Performance with A/B Testing](https://www.facebookblueprint.com/student/activity/639591-optimize-campaign-performance-with-ab-testing) | Meta Blueprint; 2025-03-18; official webinar overview; **high** for description only | Public learning objectives, no replay/transcript reviewed; `28-blueprint-ab` |
| [Current Digital Ads Benchmark Report landing page](https://tinuiti.com/research-insights/research/digital-ads-benchmark-report/) | Tinuiti; current page says Q3 2026; modified 2026-10-15; data-report landing page; **medium**, limited access | Search cache called this Q2; the actual retrieved page is Q3. Read the landing page only; report behind email form not obtained. No current-quarter CPM/CPI conclusions taken from it; folder retains discovery name `22-tinuiti-q2-2026` |
| [Toward fairness in personalized ads](https://about.fb.com/wp-content/uploads/2023/01/Toward_fairness_in_personalized_ads.pdf) | Meta; January 2023 host path; official technical report; **high** for stated system explanation | PDF downloaded; only auction-relevant material inspected. Not counted as a full report read and not needed to establish current buyer controls; `36-auction-pdf` |

The search result pages and practitioner indexes were discovery aids, not substantive evidence. `discovery-foxwell` and `discovery-loomer` preserve those reads. The alternate budget-sharing hostname returned failed extraction; canonical rendering supplied the evidence instead (`32-budget-sharing`, `38-budget-sharing-canonical`, `38-budget-sharing-render`).

## Open questions and missing coverage

1. **What is actually available in this ad account and app integration?** The documented app path and general Advantage+ controls differ. No account was opened to verify event eligibility, age controls, exclusions, creative testing, bidding options, new creative workflow, or placement inventory. These are setup questions to resolve before approval, not grounds for assuming all menus exist.
2. **What is the real allowable trial cost?** Price, trial duration, mature conversion, refunds, store proceeds, retention, contribution and cash payback are not established by this lane. An external CPM or another founder's revenue cannot answer it.
3. **Which attribution/event architecture will the first test use?** SDK, MMP, SKAdNetwork/AdAttributionKit, AEM and subscription revenue reconciliation require the app-UA lane and current implementation evidence. This lane intentionally does not substitute generic website attribution for iOS attribution.
4. **Can we observe new acquisition separately from existing users?** App exclusions and privacy constraints may make this imperfect. Sales-specific audience-segment advice must not be represented as verified app reporting.
5. **How much creative variety can this budget evaluate?** There is no supported universal creative quota, fatigue frequency, profitable CTR, or winning video length in these sources. Test capacity depends on event cost and uncertainty.
6. **What caused an individual advertiser's 2025–2026 performance decline?** Public engineering rollouts and practitioner anecdotes do not establish account-specific causation. We need the account's actual edit, delivery, cohort and event history.
7. **How do the newest features behave for subscription apps?** Meta's October announcement is recent and mixes availability states. It does not establish that automated assistant recommendations improve ExcerLock's contribution or that an assistant should control spending.
8. **What are the latest representative app benchmarks?** The current Tinuiti report was email-gated and its live page differed from the search cache. The historical report is general managed-advertiser evidence. No current-quarter subscription-app CPA number was inferred from either.
9. **Policy detail beyond the documented teen restrictions remains unreviewed.** The initial recommendation avoids fat-loss promises and uses adult movement demonstrations, but this lane did not complete a full current ad-policy review of copy, personal-attribute wording, landing page or app data classification.

Direct HTML extraction initially failed for several Help Center URLs; browser rendering recovered the auction, learning, placements, sharing, daily-budget, significant-edit, creative-test, app, bid, A/B and campaign-budget pages used here. Blueprint extraction yielded course descriptions or outlines, not completed lessons. The current Tinuiti full report and the Blueprint replays remain missing coverage. All these boundaries are kept separate from “nothing found.”
