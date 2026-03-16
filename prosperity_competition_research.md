# IMC Prosperity competitive dossier for Prosperity 4 readiness

## Signal map and evidence grading

This report is optimised for one purpose: helping you make the right build/no-build decisions so you can be genuinely dangerous in Prosperity 4.

### Evidence tags used throughout

Every major competition-specific claim is tagged:

- **[Official P4]** Confirmed by official Prosperity 4 materials published in 2026.
- **[Official prior edition]** Confirmed by official Prosperity materials from earlier editions (for example, official wiki pages or official IMC announcements).
- **[Community/top-team evidence]** Strong evidence from top public teams’ repos/writeups, widely used open-source tooling, or credible postmortems.
- **[Inference]** My best reasoned estimate based on the above, with uncertainty called out.
- **[Official P4 unknown]** Public Prosperity 4 materials do not currently disclose this detail.

### What is confirmed right now about Prosperity 4

The public official Prosperity 4 landing page is, as of March 16, 2026 in Australia, essentially a teaser plus signup capture: it explicitly says the challenge “is taking off this April” and frames the winner as “IMC Trading Talent of 2026,” but does not disclose rules, rounds, products, data formats, or environment constraints. **[Official P4]** [1]

Official IMC social media teaser copy (Instagram) states “Signups open 16 March” and “Round 1 begins 14 April” (and mentions a Sydney in-person event). This is the most concrete public timing hook visible without the wiki/login. **[Official P4]** [2]

**Implication:** nearly all actionable detail for Prosperity 4 is currently **not** publicly confirmed; preparation must therefore be built around (1) stable mechanics from prior official docs, and (2) the strongest repeated patterns from Prosperity 1–3 top teams.

## Competition mechanics and scoring reality

This section answers your “SECTION 1 — What Prosperity actually is” requirements, but keeps Prosperity 4 claims clearly separated as requested.

### Structural shape across editions

Official IMC announcements confirm that Prosperity has been run as a multi-round, mixed algorithmic + manual competition:

- Prosperity 1 (announced 2023): described as a “10-day market simulation” combining algorithmic and “positional” skills. **[Official prior edition]** [3]
- Prosperity 2 (announced 2024): ran April 8–23 with “five trading rounds.” **[Official prior edition]** [4]
- Prosperity 3 (announced 2025): ran April 7–22 with “five trading rounds,” with a mix of algorithmic and manual exercises. **[Official prior edition]** [5]

Public top-team repos consistently describe an additional **tutorial** / “round 0” preceding Round 1. **[Community/top-team evidence]** [6], [14], [30]

#### Round duration: the key conflict you must internalise

- Multiple top-team repos and writeups describe **5 rounds over roughly 15 days**, i.e. roughly **3 days per round**. **[Community/top-team evidence]** [6], [17], [30]
- A third-party career forum post claims **48 hours per round** while also calling the overall competition “10-day.” This conflicts with both the 15-day framing and the April 8–23 / April 7–22 official date ranges. **[Community/top-team evidence]** [8], [4], [5]

**Best reasoned estimate for Prosperity 4:** expect the “five rounds across roughly two weeks” structure to persist, with a tutorial beforehand, because it is consistent with official date windows for 2024 and 2025 and repeated by several top teams. **[Inference]** [4], [5], [6], [30]

### What is revealed each round and when it matters

Across multiple credible sources, the operational rhythm is:

- New products are introduced as rounds progress; earlier products remain tradable. **[Community/top-team evidence]** [6], [17], [30]
- Participants receive **historical/sample data** for new products and use it to tune strategies and study bot behaviour. **[Official prior edition]** [11]
- A strong community observation from an early Prosperity writeup is that teams often got new-asset historical data roughly **72 hours** before the new round, so the “build window” is extremely tight. **[Community/top-team evidence]** [8]

### Scoring: what actually decides the leaderboard

Official announcements describe the winner as the team with the highest profit in the island’s in-game currency (seashells / SeaShells). **[Official prior edition]** [3], [4], [5]

Top-team writeups are consistent on the mechanism:

- You submit an algorithm each round.
- It is evaluated independently against a marketplace of bot participants; that PnL is ranked globally. **[Community/top-team evidence]** [6], [14], [17], [30]

This matters because it implies: your edge is not “out-latency other students”; it is to (a) model and exploit the simulation/bot ecology, and (b) produce robust PnL under fixed constraints.

### Manual trading: how important was it historically?

Official announcements for Prosperity 2 and 3 explicitly include a dedicated prize for “Best Manual Trader.” **[Official prior edition]** [4], [5]

Top teams repeatedly say manual is a **small fraction** of total PnL. **[Community/top-team evidence]** [14], [17], [30]

You can quantify “small but non-zero” from a strong individual datapoint: in Jasper van Merle’s Prosperity 2 public results table (9th overall), manual PnL is material but not dominant relative to overall (for example, Round 5 manual is about 115k vs overall about 1.7M). **[Community/top-team evidence]** [18]

**Practical conclusion:** treat manual as (1) not your main path to elite rank, but (2) a meaningful incremental edge if you can solve quickly and avoid blunders—especially because it has its own prize incentive and can break ties. **[Inference]** [4], [5], [18], [68]

### What you are actually trading against

The most direct accessible official description is that your algorithm receives a state containing bot quotes and trades, and you can place orders that interact with those quotes. **[Official prior edition]** [11]

Top-team repos describe the evaluation explicitly as being against bot participants in the marketplace. **[Community/top-team evidence]** [6], [14], [17], [30]

**Best reasoned interpretation:** Prosperity is a **multi-agent simulated exchange** (bots quoting/trading, plus your agent), not a historical replay of real markets—although some editions appear to have reused datasets or mechanics in ways that participants exploited. **[Inference]** [11], [18], [30]

## Exchange microstructure, data interface, and constraints

This section answers your “SECTION 2” and “SECTION 3” requirements, with explicit known vs inferred boundaries.

### The exact shape of what your bot receives

The official “Writing an Algorithm in Python” wiki page describes the core interaction:

- Your method is called each iteration with a `TradingState`.
- `TradingState` includes: `timestamp`, `listings`, `order_depths`, `own_trades`, `market_trades`, `position`, `observations`. **[Official prior edition]** [11]
- The submission environment is implemented as a stateless container (backed by serverless infrastructure), and you should not rely on persistent global variables; use the provided `traderData` string to persist state across calls (for example, serialise with JSON or `jsonpickle`). **[Official prior edition]** [11]

### Data classification: L1/L2/L3?

Based on the official description and the ubiquitous `OrderDepth` pattern used in participant code:

- The visible order book is best described as **L2-style depth by price level** (aggregated volume at price levels), not per-order queue (L3). **[Inference]** This is supported by the “outstanding buy and sell orders” being delivered as a product-level overview rather than as individual order IDs. [11], [28]
- You also receive prints (`market_trades`), which is additional information beyond a pure L2 snapshot. **[Official prior edition]** [11]

### Matching and order lifetime: what’s known, what’s not

The official wiki describes several core mechanics that are unusually important for strategy design:

| Mechanic | What we can say precisely | Evidence tag |
|---|---|---|
| Partial fills | If you submit size larger than available opposing quotes, a remaining quantity can stay outstanding and potentially be traded later. | **[Official prior edition]** [11] |
| Order persistence (your orders) | If no bots trade with your remaining outstanding quote, it is cancelled at the end of the iteration (effectively a “1-tick time-in-force” for unfilled remainder). | **[Official prior edition]** [11] |
| Who you match against | Orders can be matched against the bot order book; you also observe market trades each iteration. | **[Official prior edition]** [11] |
| Queue position / order IDs | Not documented as visible; typical data models provide no queue position or IDs. | **[Inference]** [11], [28] |
| Priority / “price improvement” | The widely used backtester reports market-trade matching occurs at **your order price** even if the market trade is at a more favourable level; it states this appears consistent with the official environment. | **[Community/top-team evidence]** [23] |
| Event-driven vs step-based | Everything described is per-iteration / per-timestamp; strategies are naturally step-based rather than true event-driven continuous time. | **[Official prior edition]** [11] |

**Strategy implication:** you are not designing a “set-and-forget passive quoting engine”; you are designing a **recompute-every-tick quoting + taking policy** where unfilled remainder is short-lived. That pushes you toward robust fair-value estimation and strict position control over fancy queue microstructure. **[Inference]** [11], [30]

### Position limits and the “all orders cancelled” trap

The official wiki states a harsh constraint:

> If the aggregated quantity of your orders would exceed the position limit, **all** orders for that product are cancelled by the exchange. **[Official prior edition]** [11]

This is a massive “silent zero-fill” failure mode. It also explains why top teams talk obsessively about position management and “clearing” logic to free capacity. **[Community/top-team evidence]** [14], [30], [6]

### Runtime, environment quirks, and logging constraints

Concrete official statements you can bank on:

- The trading container is stateless (serverless-style); do not rely on globals for persistence. **[Official prior edition]** [11]
- Python tooling guidance historically referenced Python 3.9 installation for local development. **[Official prior edition]** [26]

High-confidence community evidence you should treat as “real until proven otherwise”:

- AWS/serverless execution errors and logging limits are recurring pain points; top teams explicitly cite AWS Lambda errors from verbose logs. **[Community/top-team evidence]** [17], [31]
- Many participants implement log truncation systems (for example, capping total output length and truncating `state.traderData` and logs), indicating a strict output-size constraint in the official runner. **[Community/top-team evidence]** [17], [30]

### Conversions and exogenous observations: what’s confirmed vs patchy

The official `TradingState` contains `observations`, but the accessible public official page does **not** fully specify their structure. **[Official prior edition]** [11]

Strong community evidence across years indicates that some rounds include **conversion / location arbitrage** products and exogenous variables (for example, “sunlight index,” “humidity,” tariffs, transport), and that backtesting these correctly is non-trivial. **[Community/top-team evidence]** [17], [29], [30]

A critical realistic take from top teams is that multiple years included exogenous variables that were suspected to be a false lead, or at least not easily monetisable. **[Community/top-team evidence]** [14], [30]

## Historical product archetypes and the edges that repeat

This section compresses your “SECTION 4,” “SECTION 6,” and “SECTION 9” requirements into an archetype-first map.

### The meta-pattern: IMC reuses archetypes, not necessarily products

Across Prosperity 1–3, publicly documented products differ (bananas vs kelp vs starfruit), but the **tradable structure** repeats:

- Stable “true value” product around 10,000 (pearls / amethysts / resin). **[Community/top-team evidence]** [6], [30], [31]
- A drift/noise product where fair value is inferred (bananas / starfruit / kelp). **[Community/top-team evidence]** [6], [14], [31]
- A chaos product that punishes overtrading (often described as “pure chaos”). **[Community/top-team evidence]** [17], [30]
- Basket/ETF stat-arb round (picnic baskets / gift basket). **[Community/top-team evidence]** [6], [30], [31]
- Options-like derivative round (coconut coupon / volcanic rock vouchers). **[Community/top-team evidence]** [17], [29]
- Conversion/location arbitrage round (orchids, macarons; “location arbitrage”). **[Community/top-team evidence]** [17], [18], [30]
- Identity / “informed trader” / copy-trading round (Olivia appears across years as a signal). **[Community/top-team evidence]** [17], [18], [30], [31]

### Archetype playbook table (what strong teams actually did)

| Archetype | Market structure | Typical edge | What strong public teams did | Common traps | Simplest viable strategy | “Top-team” approach |
|---|---|---|---|---|---|---|
| Fixed fair-value MM product | Price anchored near ~10,000 with occasional mispriced best bid/ask | Capture spread + take mispriced quotes; inventory-dependent skew; “clear” at fair | Market-take if best bid > FV or best ask < FV; market-make around FV; explicitly use FV-level orders to rebalance inventory. **[Community/top-team evidence]** [6], [14], [30], [31] | Hitting position limits → order cancellations; over-quoting without clearance; assuming FV is exactly static if a micro-edge exists | FV = 10,000; place bid = 9,999 and ask = 10,001; take obvious mispricings | Inventory-skewed quoting + systematic “capacity freeing” trades at/near FV; microstructure-informed sizing, not symmetric sizing. **[Community/top-team evidence]** [14], [30] |
| Forecastable/drifting product | Locally stable, mild drift; fair inferred from order book or short history | Estimate fair from dominant MM mid or rolling average; earn spread with low directional risk | Identify persistent market maker; treat its mid as fair; market-make/take around it; validate by controlled “buy 1 & hold” experiments. **[Community/top-team evidence]** [6], [14], [30], [31] | Overfitting regression; using noisy mid; allowing drift to accumulate inventory | Rolling mid-price average-based fair; quote around fair | “WallMid” / dominant-liquidity mid feature + robust filters that ignore small noisy orders; inventory-aware spread control. **[Community/top-team evidence]** [14], [30] |
| Chaotic/volatile product | Frequent spikes and reversals; “no structure” for many | Volatility spike mean reversion, size control, or avoid | Many scaled down exposure (for example, 10% allocation); some used rolling standard-deviation thresholds and then traded opposite spikes. **[Community/top-team evidence]** [17], [29], [30] | Treating it like stable MM; full-size inventory accumulation; trusting backtest too much | Either do not trade, or run tiny-size spread capture with hard stop-outs | Regime detection (spike vs normal) + position timeouts + asymmetric sizing; sometimes accept “gamble” risk early then stabilise later. **[Community/top-team evidence]** [17], [30] |
| Basket / ETF stat-arb | Basket price vs constituents; mean-reverting premium/spread | Trade premium divergence, ideally market-neutral | Compute basket premium (basket − weighted sum of components − constant premium); z-score; enter/exit with thresholds; adjust for position limits by trading premium *differences* when multiple baskets exist. **[Community/top-team evidence]** [6], [30], [31] | Inability to fully hedge due to position limits; component liquidity/limits; over-levering into mean reversion | Trade basket only vs synthetic; ignore components | Multi-instrument limit-aware optimisation: choose the trade that maximises premium exposure per unit of scarce position limit; layer in execution logic that avoids limit-triggered full cancellation. **[Community/top-team evidence]** [6], [14], [31] |
| Options / vol products | Underlying + option-like vouchers/coupons; implied-vol structure | Model fair with Black–Scholes-style pricing; exploit mispriced IV; sometimes “options scalping” | Implement BSM + implied vol; experiment with smile/hedging; many reported delta hedging or smile fitting as too complex or not worth it under time/limits. **[Community/top-team evidence]** [17], [29], [30] | Complex models without robustness; hedging that burns PnL under limits; assuming real-market microstructure | Price with simple BSM using estimated vol; trade clearly mispriced options | Practical “competition BSM”: focus on a stable vol estimator, enforce risk caps, and exploit repeated bot behaviour; accept that “proper hedging” may be suboptimal here. **[Inference]** [17], [30] |
| Conversion / location arbitrage | Two “venues” + conversion step with costs/constraints | Lock in spread via convert-buy-sell loops | Aggressive exploitation: repeatedly short to the limit at a level where conversion back to flat is profitable; learn that some environments allow convert-to-flat then re-short in the same iteration. **[Community/top-team evidence]** [17], [18], [30] | Misunderstanding conversion costs; backtester unsupported; eating friction | Only trade obvious venue spread when huge | Build a conversion engine with explicit cost accounting and a “cycle detector”; treat conversions as a constrained optimisation each tick. **[Inference]** [17], [18] |
| Identity / insider / bot-exploitation | Counterparty IDs become visible late; some agents appear informed | Copy trading / signal extraction from a consistently profitable trader | Identify “Olivia” as buying low/selling high; use her to trade certain products; compute “good trade rate” per trader to mechanise insider detection. **[Community/top-team evidence]** [17], [18], [30], [31] | False positives; chasing noise traders; over-allocating without confirmation | Manual eyeballing: find best trader and mirror | Systematic pipeline: per-trader performance scoring in rolling windows, trade-size filters, and controlled copy sizing tied to your remaining capacity. **[Inference]** [17], [31] |
| Meta/mechanics exploitation | Data leaks, reruns, reused datasets | Exploit non-market artefacts | Teams observed sample data matching live early ticks (then reruns; hardcoding ruled cheating), and reused datasets enabling arbitrage across years. **[Community/top-team evidence]** [6], [18], [30] | Getting banned / disqualified; overfitting to quirks that disappear | Ignore entirely | Build detection tooling (not hardcoded trading): quickly test whether sample/live overlap, whether bot parameters changed, and whether prior-year data repeats—then adapt legitimately. **[Inference]** [6], [30] |

## Public corpus: best repos, writeups, and tools you should study first

This section answers your “SECTION 5” requirement and ranks resources for *speed-to-edge*.

### Ranked table of the strongest public resources

**Ranking criteria:** (1) top-placement credibility, (2) depth of microstructure + mechanics insight, (3) reusable tooling, (4) round-by-round specifics that map to repeatable archetypes.

| Rank | Resource | Edition | Team / author | Reported placement | Credibility assessment | What it contains | Important strategy ideas revealed | Tooling value | Still worth studying for Prosperity 4? |
|---:|---|---:|---|---|---|---|---|---|---|
| 1 | [Frankfurt Hedgehogs repo][30] | 2025 | Timo Diehm, Arne Witt, Marvin Schuster | 2nd global | Extremely strong: top-2 finish + detailed structural overview and tooling philosophy | Polished final algorithm file + long writeup including tools, round archetypes (MM / ETF stat-arb / options / location arb / trader IDs), manual breakdown, and mechanics FAQ topics | “WallMid” / order-book-driven fair value; strong emphasis on microstructure visualisation; warns about false leads (for example, indices) and about hardcoding drama | High: explains dashboard design, backtesting workflow, and how to analyse traders/groups | Yes — best single “mental model” builder because it is archetype-structured. |
| 2 | [Linear Utility repo][14] | 2024 | Eric, Jerry, Nathan, Sreekar | 2nd global | Extremely strong: top-2 + unusually transparent tooling + grid-search backtesting description | Round-by-round research + in-house backtester + dashboard; clear explanation of position-limit clearing and identifying dominant MM quotes | Position-limit “capacity management” as first-class alpha; extracting fair from large MM quotes; local mean reversion | Very high: shows how to build a real workflow (backtester → dashboard → param search) | Yes — best blueprint for what to build before Day 1. |
| 3 | [CMU Physics repo][6] | 2025 | Chris, Nirav, Aditya, Timur | 7th global, 1st USA | Very strong: top-10 + practical, implementation-level round notes | Round folders with EDA + strategy writeups; candid notes on sample-data controversy and rerun | Volatility scaling for chaos product; z-score basket premium with limit-aware hedge; “persistent MM defines fair”; operational lessons about cheating/hardcoding vs reruns | Medium-high: lots of notebooks + a realistic “what we actually did” narrative | Yes — excellent for pragmatic constraints and risk-management instincts. |
| 4 | [Alpha Animals repo][17] | 2025 | UCSD team | 9th global, 2nd USA | Strong: top-10 + clear postmortem on mistakes | Strategy summaries + “other things we tried”; explicit warning about conversion backtesting pitfalls | Volatility spike mean reversion; options modelling attempts (smile, delta hedge) and why they failed; insider/copy-trading methodology | Medium: less tooling, more strategic notes; valuable “don’t do this” list | Yes — particularly valuable for avoiding rabbit holes and conversion-cost disasters. |
| 5 | [Jasper van Merle Prosperity 2 repo][18] | 2024 | Jasper van Merle (“camel_case”) | 9th overall | Strong: top-10 + rare transparency on manual vs algo PnL and bot exploitation | Round summaries, PnL table, and multiple open-source tools | Conversion-arb exploitation description; bot-specific directional signals; notes on data reuse across years as a structural edge | Very high: created the toolchain many teams used | Yes — best “mechanics + tooling” anchor. |
| 6 | [Stanford Cardinal repo][31] | 2023 | Shubham, Konstantin, Parth | 2nd of 7007 | Strong: top-2; shows early-edition archetypes that still recur | Round-wise details: stable FV product, regression product, pairs/ETF premiums, exogenous signals, and copy trading “Olivia” | “Olivia” as informed trader; pair trading; practical backtester integration to avoid duplicating sims; warns about runtime/Lambda issues | Medium: fewer reusable tools, more strategy narrative | Yes — proves archetype persistence across years. |
| 7 | [prosperity2bt backtester][23] and [prosperity3bt][93] | 2024–25 | jmerle tooling | N/A (tooling) | Very strong: widely used; strives to match official output format | Local backtester that matches order depths + market trades; compatible log output for visualisers | Key insight: how trades are matched in practice; highlights unsupported conversion rounds; encourages realism testing | Extremely high: fast iteration, regression testing, reproducible logs | Yes — this should be Day 0 tooling. |
| 8 | [Prosperity 3 visualiser][66] | 2024–25 | jmerle | N/A (tooling) | Strong: widely used | Log visualisation of PnL, positions, and order book over time | Helps you see microstructure patterns and debug risk | Very high: accelerates intuition, speeds iteration | Yes — non-negotiable if you want to be fast. |
| 9 | [Manual-challenge solutions repo][68] | 2024 | Gabriel Romon | 30th / 9139 (manual) | Strong: focused and measurable | Self-contained notebooks solving each manual round | How manual problems are structured (probability / optimisation) and how to solve quickly | Medium: reusable templates for “manual speed” | Yes — if you want free expected value in manual rounds. |
| 10 | [Official “Writing an Algorithm in Python” page][11] | N/A | IMC Prosperity wiki | N/A | Highest authority for mechanics among accessible docs | Definitive on `TradingState` fields, statelessness, order persistence, and the position-limit cancellation rule | The exact “shape of the game” that strategy must respect | Foundational: informs any backtester/dashboard build | Yes — and you should diff the Prosperity 4 wiki against it on Day 1. |

## What has actually worked before and what’s overrated

This section gives you the synthesis you asked for (why it worked in Prosperity specifically, and what not to waste time on).

### Strategy family synthesis table

| Strategy family | Why it worked in Prosperity (not generic finance reasons) | Products/archetypes | Robust across years? | Minimal implementation | Advanced/top-team version | What failed / was overrated |
|---|---|---|---|---|---|---|
| Fair-value market making + taking | The environment repeatedly includes a “stable true value” product with frequent small mispricings; L2-style snapshots and short-lived orders make spread capture reliable if you manage limits. | Fixed-FV products | Yes | Take quotes beyond FV; quote around FV; simple position caps | Inventory skew + clearance trades at FV to free capacity; microstructure tooling to see fills and bot behaviour | Pure symmetric MM without clearance → you hit limits and get orders cancelled. **[Community/top-team evidence]** [14], [30], [31] |
| “Dominant MM mid” fair estimation | Many products are noisy *except* for a predictable large market maker whose quotes are more informative than small orders; filtering out noise improves fair-value estimation. | Forecastable/drifting products | Yes | Rolling mid-price average | Identify and track the consistent large MM; use its mid as fair (“WallMid” appears explicitly) | Heavy ML/regression often is not worth it versus a robust microstructure fair proxy. **[Community/top-team evidence]** [6], [14], [30], [31] |
| Volatility spike mean reversion (small size) | “Chaos” products create huge one-tick swings; if bots are mean-reverting or if spikes revert frequently, contrarian entries can work — *but only with strict sizing*. | Chaotic/volatile products | Mixed | Rolling standard-deviation threshold; trade opposite spike | Regime model + timeouts + allocation caps; integrate into global risk budget | Overtrading the chaos product at full size destroys PnL; many teams “couldn’t find structure.” **[Community/top-team evidence]** [17], [29], [30] |
| Basket premium z-score stat-arb | Basket premiums in Prosperity tend to mean-revert; when components/weights are known, you can isolate the premium and trade it. | Basket/ETF products | Yes | Compute premium, z-score it, trade with thresholds | Position-limit-aware optimisation across multiple baskets; trade premium differences to fit limits | Trying to fully hedge everything without regard to limits leads to cancellations or under-hedging. **[Community/top-team evidence]** [6], [30], [31] |
| Simple pairs/spread trading | Some products are mechanically linked (production relationships or synthetic relationships), and the sim often rewards exploiting stable ratios. | Spread/pair products | Yes | Hardcoded ratio spread + threshold | Adaptive parameter tuning + limit-aware routing (trade only one leg when it dominates capacity) | Momentum-only strategies are unstable unless the product is structurally trending. **[Community/top-team evidence]** [29], [31] |
| Options fair-value / IV mispricing | The game introduces options-like instruments; simple BSM-style modelling catches blatant mispricing if bots are simplistic. | Options/derivatives | Likely | Compute BSM fair; trade mispricings | Robust vol estimator + risk controls; exploit repeated bot-quoting behaviours | Volatility-surface fitting and delta hedging are repeatedly cited as too complex / unreliable under time constraints. **[Community/top-team evidence]** [17], [29], [30] |
| Conversion/location arbitrage loops | Conversion rounds appear intentionally arbitrageable if you understand the mechanics; repeated conversion loops can mint PnL if costs allow. | Conversion/location | Yes (appears in multiple editions) | Buy / convert / sell if spread > cost | Full conversion engine with explicit friction model; exploit same-iteration cycles when permitted | Backtesters often do not support conversions; misunderstanding costs can wipe out profit. **[Community/top-team evidence]** [17], [18], [23] |
| Bot behaviour / insider copy trading | When counterparty IDs exist, some agents are systematically better (“Olivia” is named in multiple years); copying converts their hidden signal into your PnL. | Trader-ID round / meta | Yes (at least P1 and P3; likely P2) | Mirror Olivia’s trades when she appears | Automated “good-trade rate” scoring to detect insiders and filter false positives | Chasing random traders; not building the analytics pipeline in time. **[Community/top-team evidence]** [17], [18], [30], [31] |

## Prosperity 4 build recommendations: what to prototype and what to avoid

This section answers your “SECTION 7” and also gives you the mission-critical tooling stack.

### First principles for Prosperity 4, given what is (not) confirmed

- Prosperity 4 public materials do not confirm environment differences yet. **[Official P4]** [1]
- The safest assumption is that the **core `TradingState` + discrete iteration** mechanics persist until the Prosperity 4 wiki proves otherwise. **[Inference]** [11], [30]

### What you should realistically prototype (grouped A–D)

#### A — Highest expected value, fastest to get working

| Prototype | Why likely viable in Prosperity 4 | Assumptions | Data required | Tooling required | Competition-specific vs transferable |
|---|---|---|---|---|---|
| “FV MM engine” + capacity clearing | Stable-FV product archetype appears across years and is explicitly documented by multiple top teams. | There is at least one stable product near constant FV | L2 book + your position | Backtester + visualiser + basic param sweep | Highly transferable (market-making fundamentals), but with Prosperity-specific cancellation/limit rules. **[Inference]** [6], [11], [30], [31] |
| Dominant-MM fair estimator (“WallMid”-style) | Repeated pattern: one large MM defines the “real” fair in noisy products; teams repeatedly exploit it. | Presence of a persistent large quoting bot | L2 book, plus identification of largest volume levels | Visual order-book tooling to detect the bot; feature extraction | Transferable microstructure intuition; implementation is Prosperity-shaped. **[Inference]** [6], [14], [30], [31] |
| Limit-safe order generator | The “all orders cancelled if they could breach limit” rule is catastrophic if ignored. | Same limit enforcement persists | Position + outstanding orders | Unit tests + worst-case fill checks in code | Mostly competition-specific detail, but it teaches real risk thinking. **[Inference]** [11], [14] |

#### B — Strong medium-complexity ideas

| Prototype | Why likely viable | Assumptions | Needs | Tooling | Notes |
|---|---|---|---|---|---|
| Basket premium stat-arb module | Basket/ETF rounds are documented in multiple editions. | One round introduces a basket + components | Precise weights; stable premium mean reversion | Backtester with multi-product support; param sweep; limit-aware sizing | Implement “position-budget optimisation” early; it is not optional. **[Inference]** [6], [30], [31] |
| Conversion engine with explicit cost model | Conversion/location arb has appeared repeatedly; teams lose money when they mis-model costs. | Prosperity 4 includes a conversion product | Observation parsing; conversion constraints and costs | A conversion-capable simulator, or at least a post-trade cost-audit tool | If the public backtester lacks conversion support again, you need your own patch. **[Inference]** [17], [18], [23] |
| Volatility-spike “chaos” risk module | Chaos products repeatedly exist; controlling exposure is itself an edge. | A high-vol product exists | Rolling volatility features | Visualiser + robust logging controls | Focus on *not losing* more than on winning big. **[Inference]** [17], [30] |

#### C — High-upside advanced ideas for top competitors

| Advanced build | Upside | Key risk | Evidence anchor |
|---|---|---|---|
| Automated “insider detection” + copy-trading pipeline | Can convert hidden bot signal into top-tier PnL in ID-revealed rounds; appears in multiple years with “Olivia.” | False positives and overfitting; needs fast analytics infrastructure | **[Community/top-team evidence]** [17], [30], [31] |
| Mechanics probing suite (environment tests) | Frankfurt Hedgehogs explicitly emphasise controlled tests to understand environment behaviour; this is a meta-edge. | Time cost; can distract from shipping strategies | **[Community/top-team evidence]** [30] |
| “Competition BSM” options engine | Options rounds are high-PnL potential if you can exploit bot mispricings quickly. | Realistic hedging may be suboptimal; model risk | **[Community/top-team evidence]** [17], [29], [30] |

#### D — Low-value rabbit holes to avoid (unless Prosperity 4 rules force them)

- High-frequency queue-position modelling / latency games: the environment is discrete-time and does not expose queue microstructure the way real venues do. **[Inference]** [11], [23]
- Complex ML models that require long training cycles: multiple top teams describe success coming from microstructure + robust heuristics rather than heavy modelling, and time per round is short. **[Inference]** [6], [14], [30]
- Full volatility-surface fitting and “proper” delta hedging as your first-line approach: repeatedly attempted and often abandoned in public top-team writeups. **[Community/top-team evidence]** [17], [29]

### The tooling stack you should build before Day 1

Top teams converge on the same philosophy: **tooling is compounding advantage**.

**Minimum viable stack (must-have):**

- Local backtester compatible with official log format (either fork jmerle’s or build your own). **[Community/top-team evidence]** [14], [23], [30], [93]
- Visualiser / dashboard to inspect order book + trades + position + PnL per timestamp. **[Community/top-team evidence]** [30], [66]
- Parameter sweep / grid-search harness (even basic), because many profitable strategies are “simple + tuned.” **[Community/top-team evidence]** [14], [30]
- State persistence + logging discipline aligned with stateless execution and log limits. **[Official prior edition]** [11]; **[Community/top-team evidence]** [17], [30]

**Competitive stack (what separates top-200 from top-20 in public evidence):**

- Microstructure feature extraction: dominant-MM detection, “WallMid,” liquidity-weighted mid, trade-size filters. **[Community/top-team evidence]** [6], [14], [30]
- Automated PnL attribution and “why did we trade here?” audit views (to kill bad fills fast). **[Community/top-team evidence]** [14], [30]
- Trader-ID analytics pipeline (if and when IDs appear). **[Community/top-team evidence]** [17], [31]

## Prosperity vs real markets and the deliverables you asked for

### How Prosperity differs from real electronic trading

| Dimension | Prosperity (best-supported description) | Real venues | What transfers |
|---|---|---|---|
| Order book realism | L2-like snapshots + printed trades; discrete iteration and unusual order lifetime (your unfilled remainder cancels at end-of-iteration). **[Official prior edition]** [11] | Continuous-time matching engines; rich order types; queue priority matters | Fair-value estimation from order book, inventory/risk thinking, basic execution logic |
| Participant behaviour | You are evaluated vs bots; edges often come from predictable bot ecology and mechanics. **[Community/top-team evidence]** [6], [14], [30] | Adversarial humans/algos; strategic interaction and toxicity | “Model the other side,” but in Prosperity it is bot modelling, not market-impact modelling |
| Latency importance | Not framed as a latency war in any official doc; tools + strategy dominate. **[Inference]** [11], [30] | Latency dominates many HFT contexts | Low — focus on correctness and robustness |
| Transaction costs | Often implicit (spread) plus explicit conversion frictions; fees are not clearly documented in accessible official sources. **[Inference]** [11], [17] | Fees, rebates, slippage, market impact | Cost-accounting intuition, but the details differ |
| Adverse selection & impact | Exists in a stylised sense (bots can trade against your quotes), but impact is not like real markets. **[Inference]** [11], [30] | Central; your trades move the market, informational asymmetry is real | Risk management and “do not accumulate toxic inventory” still transfer conceptually |

**Blunt classification:** Prosperity is best viewed as a **stylised but meaningful trading simulation with strong bot-exploitation and mechanics-exploitation components** — not a pure toy, but also not a faithful reproduction of professional electronic markets. **[Inference]** [11], [14], [30]

**Most transferable real trading skills:**

- Market making with inventory control, and building fair value from microstructure. **[Community/top-team evidence]** [6], [14], [30]
- Turning a trading hypothesis into a backtest + calibration workflow under time pressure. **[Community/top-team evidence]** [14], [30]
- Recognising when to stop trading a product (risk budgeting). **[Community/top-team evidence]** [6], [17]

**Most competition-specific skills:**

- Reverse-engineering bot ecology and mechanics through controlled experiments. **[Community/top-team evidence]** [30]
- Tooling speed: building dashboards/backtesters that match the environment quickly. **[Community/top-team evidence]** [14], [23], [30]

### Arbitrage and structural edges: what has existed historically?

| Edge type | Did it exist historically? | What kind of “arbitrage” is it? | Notes for Prosperity 4 |
|---|---|---|---|
| Static mispricing vs fixed FV | Yes | Genuine financial-style (in a stylised market) | Assume it returns as an onboarding archetype; build the FV MM engine first. **[Inference]** [30], [31] |
| Pair mispricing (ratio spread) | Yes | Genuine-ish financial-style | Repeats via mechanically related products. **[Community/top-team evidence]** [29], [31] |
| Basket / NAV mispricing | Yes | Genuine-ish financial-style | Often mean-reverting premiums; position limits turn it into constrained optimisation. **[Community/top-team evidence]** [6], [30], [31] |
| Conversion / location | Yes | Stylised contest arb with explicit friction | Backtesting it wrong is a known failure mode. **[Community/top-team evidence]** [17], [18] |
| Options fair-value | Yes | Stylised fair-value / IV arb | Keep it simple and robust; complexity kills under time pressure. **[Community/top-team evidence]** [17], [30] |
| Predictable-agent exploitation | Yes | Mostly contest exploitation | “Olivia” / informed trader and named bots show repeated signal opportunities. **[Community/top-team evidence]** [17], [30], [31] |
| Rule / mechanics exploitation | Yes | Contest exploitation | Sample-data/live-overlap drama and reused datasets were exploited in some years (with risk of being ruled cheating). **[Community/top-team evidence]** [6], [18], [30] |

## Preparation blueprint and required deliverables

### Bottom line in 10 bullets

- Prosperity 4 public info is currently *teaser-level*; assume core mechanics persist until the Prosperity 4 wiki says otherwise. **[Official P4]** [1]
- The algorithm runs in a discrete iteration loop with a `TradingState` that includes L2-like order depth + trades + positions + observations; state persistence is via a string, not globals. **[Official prior edition]** [11]
- The **position-limit cancellation rule** (“all orders cancelled”) is a top-1% mechanic: you must design limit-safe order generation and capacity freeing. **[Official prior edition]** [11]
- Every year features at least one stable ~10k fair-value product; winning is not fancy — robust market making + inventory management is table stakes. **[Community/top-team evidence]** [6], [30], [31]
- A persistent large market maker often defines the real-time fair value for a drifting product; “filter the noise” beats complicated forecasting. **[Community/top-team evidence]** [6], [14], [30]
- “Chaos products” are where good teams die; size down, add spike/regime logic, or do not trade. **[Community/top-team evidence]** [17], [30]
- Basket/ETF stat-arb is a repeat archetype; the real difficulty is position-limit-aware hedging and execution, not the z-score. **[Community/top-team evidence]** [6], [30], [31]
- Options and conversion rounds exist because IMC wants you to model explicit mechanics; keep models robust and prioritise correct cost accounting. **[Community/top-team evidence]** [17], [18], [30]
- Manual trading is usually a small share of total PnL, but it has its own prize incentive and can be meaningful incremental EV. **[Official prior edition]** [4], [5]
- Tooling is compounding alpha: the strongest public teams either built or heavily relied on backtesters + dashboards + parameter sweeps. **[Community/top-team evidence]** [14], [23], [30]

### Best 10 resources to study first

1. [Frankfurt Hedgehogs][30] (Prosperity 3)
2. [Linear Utility][14] (Prosperity 2)
3. [CMU Physics][6] (Prosperity 3)
4. [Alpha Animals][17] (Prosperity 3)
5. [Jasper van Merle][18] (Prosperity 2 writeup + tools list)
6. [prosperity2bt backtester][23]
7. [prosperity3bt][93]
8. [Prosperity 3 visualiser][66]
9. [Stanford Cardinal][31] (Prosperity 2023)
10. [Official “Writing an Algorithm in Python” page][11]

### Best 5 strategy directions to prototype first

1. **Stable-FV market making engine + capacity clearing** (foundation and repeat archetype). **[Inference]** [11], [30], [31]
2. **Dominant-liquidity fair-value estimator (“WallMid”-style) + inventory-skew quoting** for the drifting product. **[Inference]** [6], [14], [30]
3. **Basket premium stat-arb module** with position-limit-aware hedging (single-basket and two-basket variants). **[Inference]** [6], [30], [31]
4. **Conversion arbitrage engine** that can model explicit costs and constraints and survives without an official backtester. **[Inference]** [17], [18], [23]
5. **Trader-ID analytics + copy-trading pipeline** (because “Olivia” / informed traders recur). **[Inference]** [17], [30], [31]

### Best tooling stack to build before Day 1

- **Fork/clone a backtester that matches official logs**, and add: (a) fast parameter sweeps, (b) per-product risk-budget checks, and (c) support for conversions if absent. **[Inference]** [14], [17], [23]
- **Order book + trades + position dashboard** (either jmerle’s visualiser or your own), with timestamp sync and filters by trader/size if IDs exist. **[Inference]** [30], [66]
- **A strict logging system** that keeps you under output limits and survives stateless execution by serialising state in `traderData`. **[Inference]** [11], [30]
- **Mechanics test harness**: scripts that deliberately probe matching rules, cancellation timing, and conversion accounting using controlled orders. **[Inference]** [30]

### Biggest unknowns about Prosperity 4

- Whether the Prosperity 4 wiki changes **`TradingState` structure** or order-persistence semantics. **[Official P4 unknown]** [1]
- Whether conversions exist, and if so, what the observation schema and friction model are. **[Official P4 unknown]** [1]
- Whether trader IDs (or an “Olivia”-like informed agent) appear again and when. **[Official P4 unknown]** [1]
- Any changes to allowed libraries, runtime limits, and log-size limits in the runner. **[Official P4 unknown]** [1]
- Round durations and deadlines (there is conflicting community chatter; official Prosperity 4 rules are not public yet). **[Official P4 unknown]** [1], [8]

### What I would do in my first 20 hours of prep

**Hours 0–4: Mechanics and tooling base**

- Read the official “Writing an Algorithm in Python” page end-to-end and implement a minimal trader that logs safely and persists state correctly. **[Official prior edition]** [11]
- Install and run `prosperity2bt` / `prosperity3bt` and confirm you can generate logs that open cleanly in a visualiser. **[Community/top-team evidence]** [23], [66], [93]

**Hours 4–10: Build the repeatable engines**

- Implement a robust FV-MM module (pricing, quoting, taking, limit-safe sizing, clearance). Validate it on a stable 10k product from prior data. **[Inference]** [30], [31]
- Implement dominant-MM fair estimation and plug it into the same MM/taking scaffold. **[Inference]** [6], [30]

**Hours 10–15: Archetype module #3 and risk discipline**

- Implement a basket-premium z-score module with position-limit-aware hedging (start with “basket only,” then add components). **[Inference]** [6], [30], [31]
- Add global risk budgeting: per-product max allocation, kill-switches for chaos products, and detection of implicit “all orders cancelled” events. **[Inference]** [11], [30]

**Hours 15–20: Study the top teams surgically**

- Read Frankfurt Hedgehogs’ structural overview and tools section; replicate their “dashboard must-have” features in your own workflow. **[Community/top-team evidence]** [30]
- Read Linear Utility’s explanation of backtester construction and capacity-clearing; implement the exact pattern, not the vibe. **[Community/top-team evidence]** [14]
- Skim CMU Physics and Alpha Animals specifically for “what went wrong” and “what we abandoned,” and write an explicit do-not-build list before Prosperity 4 starts. **[Community/top-team evidence]** [6], [17]

## References

[1]: https://prosperity.imc.com/
[2]: https://www.instagram.com/reel/DVgOlYnErjO/
[3]: https://www.imc.com/us/corporate-news/Prosperity-the-world%27s-most-elaborate-trading-challenge
[4]: https://www.prnewswire.com/apac/news-releases/imc-trading-invites-top-stem-students-to-compete-in-global-trading-challenge-302070557.html
[5]: https://www.imc.com/us/corporate-news/prosperity-3-IMCs-global-trading-challenge-returns
[6]: https://github.com/chrispyroberts/imc-prosperity-3
[8]: https://forum.prosple.com/t/imc-trading-prosperity-global-trading-challenge/151
[11]: https://imc-prosperity.notion.site/Writing-an-Algorithm-in-Python-658e233a26e24510bfccf0b1df647858
[14]: https://github.com/ericcccsliu/imc-prosperity-2
[17]: https://github.com/CarterT27/imc-prosperity-3
[18]: https://github.com/jmerle/imc-prosperity-2
[23]: https://github.com/jmerle/imc-prosperity-2-backtester
[26]: https://imc-prosperity.notion.site/Programming-resources-c7daa5e7e73644ef80319019e9554f44
[28]: https://github.com/jmerle/imc-prosperity-2/blob/master/src/submissions/round1.py
[29]: https://gitee.com/yiyan-duck/prosperity3
[30]: https://github.com/TimoDiehm/imc-prosperity-3
[31]: https://github.com/ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal
[66]: https://jmerle.github.io/imc-prosperity-3-visualizer/
[68]: https://github.com/gabsens/IMC-Prosperity-2-Manual
[93]: https://pypi.org/project/prosperity3bt/