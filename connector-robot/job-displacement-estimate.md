# How Many Jobs Will Home-Labor Robots / Self-Maintaining Homes Replace?

**Created:** May 31, 2026

Estimate produced via multi-agent research workflow with independent verification of headline numbers. Companion to [the design doc](../../../../.gstack/projects/Robotics/skyler-main-design-20260530-152518.md). Numbers are ranges, not forecasts; read the "Why these numbers are soft" section.

---

I'll write the labor economics estimate now. The data and verdicts are all provided, so I can produce this directly without tools.

## Scope

This estimate covers paid US occupations a home-labor robot or self-maintaining-home product would target: residential and building cleaning, general home maintenance/repair, landscaping, and the chore (not care) fraction of home/personal-care aide work. The displacement engine here is a general-purpose, home-capable physical robot — not the floor-only robot vacuum that already exists. That distinction drives every number below: the most-cited timelines put economically viable *consumer/home* humanoid applications at 2030-2035 ([Goldman Sachs](https://www.goldmansachs.com/insights/articles/humanoid-robots)), so the horizon of interest is ~2040.

## (a) Gross jobs exposed — US occupation table

These are occupations whose core tasks overlap with what a home robot could do. "In-scope share" is the fraction of each occupation's employment whose work is plausibly home-chore-automatable (vs. commercial settings, personal care, or skilled judgment the robot cannot do); these shares are my analytic estimates, not BLS figures, and are flagged as soft.

| Occupation (SOC) | US employment | Median annual wage | In-scope share (est.) | In-scope jobs |
|---|---|---|---|---|
| Maids & housekeeping cleaners (37-2012) | 1,356,800 ([BLS OOH](https://www.bls.gov/ooh/about/data-for-occupations-not-covered-in-detail.htm)) | $34,660 ([BLS OOH](https://www.bls.gov/ooh/about/data-for-occupations-not-covered-in-detail.htm)) | 60-80% | ~0.8-1.1M |
| Janitors & cleaners, exc. maids (37-2011) | ~2.2M (≈2,199,900) ([BLS OEWS, May 2024 release](https://www.bls.gov/news.release/archives/ocwage_04022025.pdf)) | $35,930 ([BLS OOH](https://www.bls.gov/ooh/building-and-grounds-cleaning/janitors-and-building-cleaners.htm)) | 15-30% (mostly commercial, not "home") | ~0.3-0.7M |
| General maintenance & repair workers (49-9071) | ~1.6M ([BLS OOH](https://www.bls.gov/ooh/installation-maintenance-and-repair/general-maintenance-and-repair-workers.htm)) | $48,620 ([BLS OOH](https://www.bls.gov/ooh/installation-maintenance-and-repair/general-maintenance-and-repair-workers.htm)) | 15-35% | ~0.2-0.6M |
| Landscaping & groundskeeping (37-3011) | ~1.3M (low confidence) ([EB-3/BLS](https://eb3.work/the-growing-labor-shortage-facing-landscaping-companies/)) | $38,090 (medium confidence) ([BLS-derived](https://willrobotstakemyjob.com/landscaping-and-groundskeeping-workers)) | 20-40% | ~0.3-0.5M |
| Home health + personal care aides (31-1120) | ~4.0M (May 2024 OEWS) / ~4.3M (2024 OOH base) ([BLS OEWS](https://www.bls.gov/news.release/archives/ocwage_04022025.htm)) | $34,900 ([BLS OOH](https://www.bls.gov/ooh/healthcare/home-health-aides-and-personal-care-aides.htm)) | 5-15% chore-only (rest is care) | ~0.2-0.6M |

Notes on the table:
- The 37-2012 employment figure (1,356,800) is the BLS Employment Projections base, which is larger than the OEWS May 2024 survey count (~860,670) for the same occupation; the verification confirmed both exist and that the OOH/EP number is correctly cited ([BLS verdict basis](https://www.bls.gov/ooh/about/data-for-occupations-not-covered-in-detail.htm)).
- 37-2011's headline is the BLS-confirmed ~2.2M ([May 2024 OEWS release](https://www.bls.gov/news.release/archives/ocwage_04022025.pdf)); the exact "2,209,760" string from search was a later May 2025 vintage and is not used. Its title is "Janitors and Cleaners, Except Maids and Housekeeping Cleaners," and most of it is commercial, so its in-scope share for *home* automation is low.
- Aides (31-1120) are the largest US occupation, but their work is overwhelmingly personal *care* (bathing, mobility, medical, companionship) — only a small chore slice maps to home automation. The combined wage/employment is well-sourced; the 31-1121 / 31-1122 split could not be isolated and is **not** reported here.
- Laundry & dry-cleaning workers (51-6011): neither employment nor wage could be isolated from the source data, so this occupation is **omitted from the totals** rather than guessed.

**Gross in-scope total (sum of ranges, US): roughly 1.8-3.5 million jobs** with task overlap. This is exposure, not displacement.

## (b) Plausibly replaced under realistic adoption (to ~2040)

Two layers shrink the gross figure: how much of the work is *technically* automatable, and how fast home-capable robots actually get adopted.

**Automatable-task share (the upper physical ceiling):**
- Frey & Osborne put "Maids and Housekeeping Cleaners" at a 0.69 probability of computerisation (canonical appendix value; an aggregator lists 0.78, but 0.69 is the source figure) ([Frey & Osborne 2017](https://ideas.repec.org/a/eee/tefoso/v114y2017icp254-280.html)).
- McKinsey rates technical feasibility of automating *predictable physical activities* at 78% — its highest of seven categories ([McKinsey](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/where-machines-could-replace-humans-and-where-they-cant-yet)).
- An AI-expert panel estimated ~39% of time on unpaid domestic work could be automated within ~10 years (often rounded to ~40%), but only ~28% of *care* work ([PLOS ONE 2023](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0281282); [Guardian](https://www.theguardian.com/technology/2023/feb/23/almost-40-of-domestic-tasks-could-be-done-by-robots-within-decade)).

These ~40-78% figures are *technical-task* ceilings, not job-loss rates. A job disappears only when nearly all of its tasks are automated *and* a robot is deployed; partial task automation augments the worker instead.

**Adoption is the binding constraint to 2040.** Goldman's base case is 250k+ humanoid shipments by 2030 (almost all industrial) and 1.4M units / $38B TAM by 2035, with consumer a majority only in some mid-2030s scenarios ([Goldman Sachs](https://www.goldmansachs.com/insights/articles/the-global-market-for-robots-could-reach-38-billion-by-2035)). Morgan Stanley sees home/consumer adoption "relatively slow until the mid-2030s," accelerating late-2030s/2040s ([Morgan Stanley](https://www.morganstanley.com/insights/articles/humanoid-robot-market-5-trillion-by-2050)). Even cumulative units in the low millions by ~2035 are a fraction of US households, and most go to factories first.

Applying realistic home-robot adoption (single-digit to low-double-digit percent of in-scope work actually performed by robots by 2040) to the gross in-scope pool yields **plausibly displaced US jobs on the order of 0.2-1.0 million by 2040** — concentrated in residential cleaning, with thinner contributions from maintenance and landscaping.

## (c) Net of jobs created

Displacement is partly offset by new roles: robot manufacturing, fleet maintenance/repair, software, remote teleoperation and exception-handling, deployment/installation, and the redeployment of cleaning crews to higher-value, customer-facing tasks. The robot-vacuum precedent is the cleanest evidence here: vacuums are the best-selling consumer robot in the world, yet cleaning/housekeeping remains a multi-million-worker occupation, and commercial robots offload only ~30% of vacuuming time — augmenting, not eliminating, the role ([SoftBank/Frontiers](https://www.frontiersin.org/journals/electronics/articles/10.3389/felec.2022.895001/full)). The PLOS panel similarly estimated domestic automation could free only ~5.8% of UK / ~9.3% of Japan women into the labor market — a single-digit shift, not occupational collapse ([Tech. Forecasting & Social Change](https://www.sciencedirect.com/science/article/pii/S0040162523001282)).

I do not have a sourced US count of robotics jobs created, so I will not invent one. Directionally, **net US job loss to 2040 is materially smaller than gross displacement — plausibly ~0.1-0.7 million** — and could be near the low end if augmentation dominates, as the vacuum precedent suggests.

## Three scenarios to ~2040 (arithmetic shown)

Arithmetic: **gross in-scope jobs × automatable-task share × home-robot adoption share = displaced jobs.** Using a gross in-scope pool of ~2.5M (midpoint of the 1.8-3.5M range).

| Scenario | In-scope pool | × Automatable share | × Adoption (to 2040) | = Gross displaced | Net (after creation) |
|---|---|---|---|---|---|
| Conservative | 2.5M | 0.40 | 0.05 | ~0.05M | ~0.03M |
| Mid | 2.5M | 0.55 | 0.25 | ~0.34M | ~0.2M |
| Aggressive | 3.0M | 0.70 | 0.50 | ~1.05M | ~0.6-0.7M |

The conservative case assumes home robots stay near-niche through 2040 (timelines slip again); the mid case assumes Morgan Stanley's "accelerating late-2030s" curve reaches a quarter of in-scope work; the aggressive case assumes Goldman's faster scenario plus broad consumer uptake. Net columns apply a 30-50% offset from job creation/augmentation.

## Why these numbers are soft

- **Timeline slippage is the rule, not the exception.** Tesla Optimus' Gen-3 target slid from 2024 to early-then-mid 2026; Musk's "~10,000 robots in 2025" goal was missed entirely (zero built, admitted Jan 2026), and the separate 5,000-unit target was abandoned ([Electrek](https://electrek.co/2026/04/22/tesla-optimus-production-fremont-model-sx-line/)). Amazon discontinued and remotely bricked its Astro for Business robot under a year after launch ([The Verge](https://www.theverge.com/2024/7/3/24190410/amazon-astro-business-robot-discontinued-refunds)). CNN (Dec 2025) calls home robotics a "limbo," with a general-purpose domestic bot "more Musk-ian fantasy than reality" ([CNN](https://www.cnn.com/2025/12/17/business/robotics-ai-limbo)). Even Goldman's bear case only bakes in a ~2-year delay ([Finimize](https://finimize.com/content/goldman-sees-the-humanoids-rising-sooner-than-you-think)) — arguably optimistic given the track record.
- **The home is an unpredictable environment.** McKinsey's high feasibility (78%) is specifically for *predictable, structured* physical work; homes are cluttered, variable, and unstructured — the hardest case for robotic manipulation, which is why factories come first (2025-2028) and homes last (2030-2035) ([Goldman Sachs](https://www.goldmansachs.com/insights/articles/humanoid-robots)).
- **The robot-vacuum precedent caps optimism.** The single most successful home robot automated one narrow task and did not eliminate the occupation. Extrapolating from a vacuum to a robot that scrubs bathrooms, folds laundry, and fixes a leaking faucet is a large, unproven leap.
- **The physical-world verification-oracle problem.** Unlike software, a home robot's success is not cheaply checkable — "is the kitchen actually clean and nothing broken?" has no automatic oracle, demanding human inspection, raising real-world reliability bars, and slowing the safe, unsupervised autonomy that mass home displacement would require.
- **Wage/employment confidence varies.** Cleaning and maintenance figures are high-confidence BLS; landscaping employment is low-confidence and its wage medium; laundry workers could not be sourced and were dropped. The automatable-task shares (40-78%) are technical ceilings, not job-loss rates, and the in-scope shares in the table are my estimates.

## Global gloss and unpaid labor

Globally, the ILO counts **75.6 million domestic workers aged 15+** (≈4.5% of all workers, ~76% women) ([ILO](https://www.ilo.org/topics-and-sectors/domestic-workers)) — the single largest paid pool a home robot would target, concentrated in regions where low wages make robots economically *uncompetitive* for decades, which suppresses near-term displacement there. The professional cleaning industry adds >4M contracted workers worldwide (low confidence, industry-sourced) on a ~$182B market ([Zion Market Research](https://www.zionmarketresearch.com/report/commercial-cleaning-services-market)).

Critically, **most home labor is unpaid**, so any job count *undercounts* the labor a self-maintaining home would displace. The PLOS panel estimated ~39% of time on *unpaid* domestic work is automatable within a decade ([PLOS ONE 2023](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0281282)). That unpaid labor — overwhelmingly performed by women — would be "displaced" as *time saved*, not jobs lost, and dwarfs the paid figures. A pure job count therefore understates the true scale of home-labor automation.

## Bottom line

Honest US headline: of roughly **1.8-3.5 million paid jobs with task overlap**, a realistic **0.2-1.0 million are plausibly displaced by ~2040**, netting to perhaps **0.1-0.7 million** after job creation and augmentation — with the low end favored by every precedent (robot vacuums augment rather than replace) and by the repeated slippage of home-robot timelines into the 2030s, and the high end requiring Goldman's faster consumer-adoption curve to materialize on schedule. Globally the exposed paid pool is far larger (~75.6M domestic workers), but low wages in most of that pool push robotic displacement well past 2040; and because the bulk of home labor is unpaid, the real automation story is measured in *hours of household time saved*, where a job count is a structural undercount.