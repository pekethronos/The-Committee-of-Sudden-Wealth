# Implementation-focused mining of top public IMC Prosperity repos

## Evidence rules and scope boundaries

This report is intentionally narrow: it mines a small set of **high-signal public repos and tooling** from prior Prosperity editions and extracts **concrete, implementable patterns**: what top public teams actually coded, which edges recurred, what tooling mattered, and what looks like a time-sink. [1], [2], [5], [6], [10]

All strategy claims below are explicitly labelled as either:

- **[Directly visible in public repo/writeup]** = stated in README/writeup or visible in code.
- **[Reasonable inference from public evidence]** = inferred from file structure, config constants, or code patterns, but not explicitly stated as intent.

Because you asked to avoid broad overviews, I do **not** re-explain the competition basics except where required to interpret implementation decisions (for example, conversions, the “informed trader” motif, position limits, backtester mechanics). [2], [5], [10], [17]

## Repo-by-repo extraction of what strong public teams built

### Ranked “study first” list of top public resources

| Priority | Resource | Edition | Public rank / credibility | Why it’s worth your time |
|---:|---|---|---|---|
| 1 | `TimoDiehm/imc-prosperity-3` | Prosperity 3 (2025) | 2nd globally, detailed writeup + full final algo. **Very high credibility**. [1] | Most complete public articulation of: wall-mid fair value, basket arb + informed tilt, IV scalping workflow, hidden conversion/taker edge, and a production-grade internal architecture (per-product trader classes + shared utilities). [1], [32] |
| 2 | `chrispyroberts/imc-prosperity-3` | Prosperity 3 (2025) | 7th globally, 1st USA; round-by-round EDA + strategy breakdown. **Very high credibility**. [5] | Strongest public “what broke in prod” evidence (Lambda/memory failure mode), plus very specific parameterisations for z-score basket arb and options IV modelling, and a clear rationale for going unhedged when hedging costs dominate. [5] |
| 3 | `CarterT27/imc-prosperity-3` | Prosperity 3 (2025) | 9th globally, 2nd USA; writeup + full algo. **High credibility**. [6] | Great for “how to structure a configurable monolith”: per-product toggles, parameter knobs, inventory/time-in-position controls, and practical copy-trading/insider-regime logic with code-level thresholds. [6], [7] |
| 4 | `ericcccsliu/imc-prosperity-2` | Prosperity 2 (2024) | 2nd-place team writeup + code/tools. **Very high credibility**. [2] | Best public writeup on: building a backtester + dashboard quickly, grid-searching parameters, discovering “mark-to-market fair” quirks, and recognising when exogenous data is bait vs when mechanics create free money (conversion/taker arb). [2] |
| 5 | `ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal` | Prosperity (2023) | 2nd of 7007 teams; concise round notes; full algo file. **High credibility**. [10] | Earlier-edition but still valuable templates: regression fair, pair trading implementation, and exogenous-threshold triggers (dolphin sightings) with a single Trader class and per-product compute functions. [10], [11] |
| 6 | `jmerle/imc-prosperity-3-backtester` + PyPI `prosperity3bt` | Prosperity 3 tooling | Widely used public backtester. **High credibility**. [12] | The fastest way to iterate: CLI backtests by round/day, `--merge-pnl`, `--vis`, output compatible with a visualiser. Also provides packaged round data sets (prices + anonymised trades). [12] |
| 7 | `jmerle/imc-prosperity-3-visualizer` | Prosperity 3 tooling | Widely used visualiser. **High credibility**. [13] | Debugging edge: step-through, PnL and position inspection (teams repeatedly cite “visual inspection” as decisive early-round). [2], [13] |
| 8 | `jmerle/imc-prosperity-3-submitter` / `imc-prosperity-2-submitter` | Submit tooling | Automation CLI. **High credibility**. [15], [16] | Shrinks the submit → monitor → download logs → open visualiser loop into one command (high leverage when rounds are short and you’re iterating often). [15], [16] |
| 9 | `jmerle/imc-prosperity-2` | Prosperity 2 (2024) | Solo team “camel_case” finished 9th overall; lists tooling. **High credibility**. [17] | Useful primarily as a stable reference implementation + a map of the open-source tool ecosystem. [17] |
| 10 | PyPI / release notes for `imc-prosperity-2-backtester` | Prosperity 2 tooling | Backtester limitations are explicitly documented. **Credible**. [18] | Saves you from believing a backtest that can’t model key mechanics (for example, when only prices/order-depth are used, not full trade matching). [18] |

### What each top repo actually did (strategies + “stealable” implementation patterns)

The table below is the core competitive extraction: per repo, what the team built, which products it targeted, what type of edge it appears to be, and what’s worth replicating.

| Repo / team | What they did that mattered | Products targeted | Complexity | Edge type | Replicate vs avoid |
|---|---|---|---|---|---|
| `TimoDiehm/imc-prosperity-3` (Frankfurt Hedgehogs) | **Wall-mid microstructure fair**: detect deep “walls” and use their midpoint as stable fair; then (i) take obvious mispricings vs fair, (ii) quote inside the spread with inventory-aware unwinds. **[Directly visible]** [1], [32] | Rainforest Resin, Kelp. [1], [32] | Medium | Structural + microstructure | **Replicate**: wall-mid estimator + generic “take then make then flatten” engine. **Avoid**: product-specific hardcoding without detection fallbacks. [1], [32] |
|  | **Informed-trader exploitation**: detect a trader buying daily lows / selling daily highs (later identified as “Olivia”), then trade directionally / regime-following rather than market-make on the chaotic product. **[Directly visible]** [1], [32] | Squid Ink (+ later Croissants influence). [1], [32] | Medium | Bot exploitation / signal extraction | **Replicate**: generic “extrema-trader detector” + “copy/tilt” framework. **Avoid**: brittle pattern matching without invalidation logic. [1], [32] |
|  | **ETF/basket arb**: trade basket vs constituents spread with fixed thresholds (robust plateau > peak), subtract running premium bias, and **tilt thresholds based on informed signal from a constituent**. **[Directly visible]** [1], [32] | Picnic Baskets + Croissants / Jams / Djembes. [1], [32] | Medium | Structural stat-arb + bot-signal tilt | **Replicate**: spread engine + premium estimator + signal-conditioned thresholds. **Avoid**: chasing optimal grid-search peaks. [1], [32] |
|  | **Options IV scalping**: fit a parabola to IV vs moneyness, detrend, trade IV deviations; supplement with simple underlying mean-reversion hedge (EMA thresholds). **[Directly visible]** [1], [32] | Volcanic Rock + vouchers. [1], [32] | Advanced | Structural pricing + mean reversion | **Replicate**: implied-vol surface *baseline* + deviation trading. **Be cautious**: full smile fitting can fail out-of-sample; keep a rolling-window fallback. [1], [5], [32] |
|  | **Conversion arb + hidden taker**: standard cross-market arb, but they also discovered a “taker bot” that fills attractive prices near an unobserved fair (for example, execute at about `int(externalBid + 0.5)` with partial fill probability). **[Directly visible]** [1], [32] | Magnificent Macarons. [1], [32] | Medium | Structural + bot exploitation | **Replicate**: conversion break-even calculator + “probabilistic taker capture” module. **Avoid**: relying on a backtester that can’t model conversions. [1], [13], [32] |
|  | **Architecture**: per-product trader classes (`StaticTrader`, `DynamicTrader`, etc.) plugged into one `Trader.run`; shared `ProductTrader` utilities; explicit config constants (thresholds, premiums, limits), plus `traderData` persistence. **[Directly visible]** [32] | Whole stack | Medium | Engineering edge | **Replicate**: this is a near-ideal time-constrained architecture (modular without over-engineering). |
| `chrispyroberts/imc-prosperity-3` (CMU Physics) | **Round-1 MM with balance via “fair-level” standing orders**; **Kelp fair from persistent MM mid** validated by “buy 1 and hold” PnL reasoning. **[Directly visible]** [5] | Resin, Kelp. [5] | Medium | Structural | **Replicate**: “fair-level inventory reset” trick (do not just stop trading when capped). |
|  | **Controlled handling of chaos product**: moved from naive MM to **size reduction (10%) + spike detection** using rolling std of price diffs; contrarian entry when std exceeds a threshold. **[Directly visible]** [5] | Squid Ink. [5] | Medium | Product-dependent mean reversion | **Replicate**: “risk throttle + event trigger” pattern. **Avoid**: full-size MM on high-jump series. |
|  | **Basket arb under position constraints**: hardcoded mean premium, rolling std for z-score; when limits prevent full hedge, trade **premium difference** between Basket1 and Basket2; deploy leftover capacity into low-risk basket MM. **[Directly visible]** [5] | Picnic Baskets + constituents | Medium | Structural stat-arb | **Replicate**: “hedge under limits” playbook (difference-of-premiums + leftover-capacity deployment). |
|  | **Options**: initially fit a quadratic smile, aggressively market-made, and auto-hedged after every timestamp; they later diagnosed hedging cost (about 40k in spread) and moved toward **unhedged** when upside exceeded realistic downside. They also found a rolling-mid-IV mean beat the quadratic fit on submission day. **[Directly visible]** [5] | Volcanic Rock + vouchers | Advanced | Structural pricing vs friction | **Replicate**: always compute hedging transaction cost and compare it to alpha. **Avoid**: committing to one IV model without a rolling-window fallback. |
|  | **Production failure mode**: visualiser instrumentation caused memory blow-up and Lambda restarts that wiped rolling state, breaking window-based strategies. **[Directly visible]** [5] | Whole stack | High impact | Engineering risk | **Replicate**: minimal logging mode + state continuity checks. **Avoid**: heavy debug tooling inside the submission payload. |
|  | **Conversion arb**: break-even formula includes tariffs/transport; negative import tariff meant being paid to do certain conversions; storage fees discouraged long holds. **[Directly visible]** [5] | Magnificent Macarons | Medium | Structural | **Replicate**: deterministic break-even and a “don’t hold” policy under storage fees. |
| `CarterT27/imc-prosperity-3` (Alpha Animals) | **Kelp MM using large MM quotes as fair**; **Resin hardcoded fair 10k**; **Squid Ink** short-horizon 3-sigma spike mean reversion. **[Directly visible]** [6], [7] | Kelp, Resin, Squid Ink | Medium | Structural + product-dependent | **Replicate**: big-quote fair estimator + configurable spike mean reversion. |
|  | **Basket arb attempt + failure**: a bug that caused orders beyond the position limit broke the strategy; they chose not to fix it mid-round. **[Directly visible]** [6], [7] | Baskets | — | — | **Key lesson**: build guardrails so one invalid order does not nullify a whole product’s logic. |
|  | **Options**: Black–Scholes pricing with rolling vol; cross-strike arbitrage when voucher spreads deviate from strike differences; they also attempted to use average IV to judge the underlying. **[Directly visible]** [6], [7] | Volcanic Rock + vouchers | Advanced | Structural | **Replicate**: cross-strike consistency checks (cheap, robust) before fancy fitting. |
|  | **Copy trading / insider detection**: compute “good trade” rate per trader over rolling windows; identify “Olivia”; copy trades on selected products and treat this as a regime signal. **[Directly visible]** [6], [7] | Squid Ink, Croissants | Medium | Bot exploitation | **Replicate**: generic counterparty analysis module + selective copy-trade execution. |
|  | **Parameterised monolith**: a single Trader with a config dict, per-product widths (`make_width`, `take_width`), active product toggles, time-in-position controls, and explicit limits; insider regime gates entries/exits. **[Directly visible]** [6], [7] | Whole stack | Medium | Engineering edge | **Replicate**: a config-first codebase; it is how you iterate fast without refactors. |
|  | **Tooling warnings**: open-source backtester logging was too verbose and caused AWS Lambda errors; conversions were unsupported, which led them to misread mechanics and lose profit. **[Directly visible]** [6], [7], [12] | Macarons | High impact | Tooling gap | **Replicate**: build a conversion simulator early, or validate with official testing if the backtester cannot. |
| `ericcccsliu/imc-prosperity-2` (Linear Utility) | **Backtester + dashboard built in-house**, including: reconstructing state, matching orders to the order book, attributing bot trades “worse than our quotes” to ourselves to simulate market making; grid-search by passing a parameter dict to the trader; dashboard with timestamp sync for deep debugging. **[Directly visible]** [2] | Whole stack | Medium | Engineering edge | **Replicate**: parameter sweep harness + time-synced visual debugging. |
|  | **Fixed-fair product template**: trade against bids above fair / asks below fair; quote around fair; implement **position clearing via 0-EV trades** to unlock more positive-EV trades under tight limits. **[Directly visible]** [2] | Amethysts | Simple | Structural | **Replicate**: the 0-EV clearing trick is high-leverage in limit-capped games. |
|  | **Fair-from-dominant-MM**: they discovered a large MM quote midpoint that was less noisy than the ordinary mid-price; they also observed the website marked PnL to this MM mid, so aligning on it improved results. **[Directly visible]** [2] | Starfruit | Medium | Structural + contest-specific quirk | **Replicate**: detect dominant-liquidity fair. **Treat as contest-specific**: marking to MM mid might not repeat. |
|  | **Exogenous data as distraction**: they tried correlations / regressions on sunlight, humidity, tariffs, etc., and concluded the signals were likely spurious; the real edge came from mechanics: a massive local taker for sells slightly above best bid plus foreign implied asks, creating a conversion arb. They later improved this with adaptive pricing based on fill volume. **[Directly visible]** [2] | Orchids | Medium | Structural + bot exploitation | **Replicate**: a mechanics-first, model-second workflow; implement adaptive edge search (fill-responsive). |
|  | **Basket spread mean reversion**: trade `basket - synthetic`; hardcode the mean, use rolling std with a small window, then use modified z-score triggers timed closer to turning points. **[Directly visible]** [2] | Gift Baskets | Medium | Structural stat-arb | **Replicate**: small-window vol estimator + robust mean. |
|  | **Options**: implied-vol mean reversion (about 16%); delta hedging was limited by position limits, so they accepted residual delta risk and later flagged it as potentially too much risk. **[Directly visible]** [2] | Coconuts / Coupon | Medium | Pricing + risk trade-off | **Replicate**: always map hedge feasibility to limits; prefer lower variance when leading. |
|  | **Cross-year “predict the future” hack**: regress last year’s products vs this year’s, find near-perfect predictors (`R² ≈ 0.99`), and exploit them. **[Directly visible]** [2] | Round 5 | Advanced | Contest-specific / brittle | **Avoid as a default**: only attempt this if Prosperity 4 obviously reuses latent seeds in a way that is (a) allowed and (b) stable. |
| `IMC-Prosperity-2023-Stanford-Cardinal` (Stanford Cardinal) | **Round-wise templates**: fixed-fair MM (Pearls), simple regression predictor (Bananas), pair trading `pina - 15/8 * coco`, exogenous-threshold trigger for Diving Gear when dolphin sightings jump. **[Directly visible]** [10], [11] | Multiple | Simple → Medium | Structural | **Replicate**: the code patterns are reusable even if the products differ. |
|  | **Code structure**: single `Trader` with per-product compute methods; caches for predictors; explicit `POSITION_LIMIT` dict; pair trading executes at worst prices when residual exceeds threshold. **[Directly visible]** [11] | Whole stack | Medium | Engineering baseline | **Replicate**: per-product function decomposition + shared helpers; modernise it with config + guardrails. |
| `prosperity3bt` backtester + `jmerle` visualiser/submitter tools | **Iteration-speed stack**: CLI backtest by round/day, merge PnL, open visualiser, write logs; packaged round data includes prices + anonymised trades. **[Directly visible]** [12], [13], [15], [16] | Tooling | High leverage | Tooling edge | **Replicate**: adopt early; then patch the gaps (conversions, bot-behaviour nuances). |
|  | **Known limitation example**: some releases include only prices/order-depth data, not full market trades, meaning matches can differ significantly. **[Directly visible]** [18] | Tooling | — | — | **Replicate**: treat the backtester as a fast filter, not as ground truth when behaviour matters. |

## Reusable strategy templates distilled from top public evidence

Below are strategy templates you can implement as **drop-in modules**. Each template includes: minimal viable version, stronger version seen in top repos, required inputs, key parameters, failure modes, and the “should I use this” rule.

### Strategy template matrix

| Template | Core idea | Simplest viable implementation | Stronger “top-team” version | Data inputs | Parameters that matter | What breaks / traps | Robustness classification |
|---|---|---|---|---|---|---|---|
| Fixed-fair market making + taker | If fair is effectively constant (about 10,000), harvest mispricings + quote around fair. **[Directly visible]** [1], [2], [5] | `fair = 10000`; take any asks `< fair` and bids `> fair`; post bid at `fair - 1`, ask at `fair + 1` until limits. [2], [5] | Add **inventory-clearing via 0-EV trades** to reset capacity; also use wall-mid detection if fair is not perfectly fixed. [2], [11], [32] | L2 book (best levels), position, limits | Quote width, unwind policy, max inventory, when to cross the spread | “Limit locked”: you stop earning because you hit the cap, or you bleed by holding inventory when fair drifts. [2], [5] | **Robust recurring edge** (when a fixed-fair product exists) |
| Dominant-liquidity fair (“wall mid” / MM mid) | Identify large, stable quotes that reveal a cleaner fair than the raw mid-price. **[Directly visible]** [1], [2], [5], [32] | Pick the price levels with the largest depth on each side; set fair = `(bid_wall + ask_wall) / 2`. [1], [32] | Add filters: only treat walls as valid if persistent through time; normalise plots by wall-mid; integrate informed-trader checks for short windows. [1], [32] | Full depth-by-level snapshots (even if only 1–4 meaningful levels) | Wall threshold (minimum depth), persistence window, fallback fair | If walls are spoofed or disappear, you anchor to noise; contest marking rules might also change. [1], [2] | **Robust recurring edge** (microstructure-aware fair estimation) |
| Inventory-skew market making | Quote tighter on the side that reduces inventory, wider on the side that increases it. **[Reasonable inference]** [7], [11], [32] | `bid = fair - w - k * pos`; `ask = fair + w - k * pos` (`pos > 0` ⇒ lower ask, lower bid). | Add discrete modes: normal MM, inventory-unwind mode that crosses to flatten, and risk-off mode for volatile regimes. CMU used explicit size throttling on Squid Ink. [5], [7] | Fair estimate + inventory + limits | `k` (skew), base width, when to cross for unwind | Over-skew causes you to stop trading; under-skew leaves you stuck at the cap | **Robust recurring edge** |
| Spread / basket statistical arbitrage | Trade deviation between basket and synthetic constituents (or basket-premium differences) expecting mean reversion. **[Directly visible]** [1], [2], [5], [32] | Compute `spread = basket_mid - Σ(coeff_i * mid_i) - premium0`; if spread > `+T`, short basket / long constituents; if spread < `-T`, do the opposite. [2], [32] | Use rolling `σ` (small window) with hardcoded mean premium; if limits prevent full hedge, trade `(premium1 - premium2)` or partially hedge and deploy leftover capacity into low-risk MM. Frankfurt also tilts thresholds by informed-trader direction. [1], [5] | Best bid/ask per asset; ability to trade multiple products in the same timestep | Thresholds, rolling-σ window length, hedge ratios under limits, premium estimator | Overfitting thresholds; assuming mean = 0 when premium is biased; slippage vs backtest can be large. [1], [2] | **Robust recurring edge** (but product-dependent coefficients/limits) |
| Mean reversion with volatility trigger (event MR) | Only mean-revert when the volatility regime indicates overshoot (spike); otherwise stay small / risk-off. **[Directly visible]** [5], [6], [7] | Rolling mean + rolling std over a short window; if move > `z * std`, fade the move with capped size; exit when the mean is re-touched or on timeout. [6], [7] | Add size throttle (for example, 10% of max), time-in-position cap, and an insider-regime gate to avoid fading when an insider is bullish or bearish. [5], [7] | Price series (mid), maybe trader IDs | z-threshold, window sizes, timeouts, max exposure fraction | Without a kill-switch you get steamrolled by jumps; with too strict gating you never trade | **Good but product-dependent** (works on chaos products when reversion exists) |
| Options implied-volatility trading | Convert option prices into implied vol; trade IV deviations (across strikes or through time) instead of raw price. **[Directly visible]** [1], [5], [6], [7], [32] | For each strike, compute IV from the mid; track rolling mean IV; go long/short the option when IV deviates beyond a threshold; hedge delta if feasible. [5], [6] | Use an IV-smile baseline (quadratic / parabolic fit) to detrend IV vs moneyness; trade residual IV; keep a rolling-window mean fallback because the baseline can break on the live day. [1], [5], [32] | Underlying + option order books; time-to-expiry; strikes | IV window, open/close thresholds, smile-fit stability, hedge policy | Biggest trap: **hedging costs** can exceed alpha; CMU quantified spread cost and went unhedged. [5] | **Good but product-dependent** (high upside, higher implementation risk) |
| “Don’t hedge when hedging is the trade” | If hedging burns spread every tick, accept controlled exposure (or cap size) when downside bound is smaller than hedging cost. **[Directly visible]** [2], [5] | Compute hedge cost as `#hedge_trades * half_spread`; compare it to expected alpha. If hedging cost dominates, reduce hedge frequency or size. | CMU’s approach: estimate worst-case step move vs average delta exposure; choose unhedged if expected benefit exceeds realistic downside. [5] | Underlying spread, hedging trade count, option deltas | Hedge frequency, max delta exposure, kill-switch thresholds | Catastrophic if the underlying has a trend / regime not in the backtest; must have stop-loss / limit | **Situational niche edge** (but can be decisive in options rounds) |
| Conversion / location arbitrage + break-even engine | Profit when local vs foreign (after tariffs / transport / storage) is mispriced; execute conversions up to the per-tick cap. **[Directly visible]** [1], [2], [5], [32] | Compute `break_even_sell_local` and `break_even_buy_local` from foreign bid/ask ± fees; take the arb when the spread is positive; convert in chunks up to the limit. [5], [32] | Add hidden-taker capture: post at a special rounded level near foreign fair, model fill probability, and adapt the edge based on realised fill volume. [1], [2], [32] | Conversion observations: foreign bid/ask + fees; local book; conversion cap | Fee-model correctness, order-price offsets, conversion scheduling | Trap: backtester mismatch (conversions unsupported) and you misread the mechanics. [6], [12], [13] | **Robust recurring edge** when conversions exist (mechanics-driven alpha) |
| Counterparty / insider exploitation via copy trading | Detect a consistently informed counterparty and follow their trades; optionally treat this as a regime label. **[Directly visible]** [1], [6], [7], [32] | If counterparty IDs are available: when the insider buys, you buy; when they sell, you sell; size within limits. [6], [7] | If IDs are hidden: infer via extrema prints (daily low / high) or “good trade rate” (profitability vs future). Frankfurt used extrema logic; Alpha Animals used rolling good-trade scoring. [1], [6], [7], [32] | Market trades with buyer/seller IDs, or enough structure to infer them | Definition of “good trade”, lookahead horizon, invalidation rules | Trap: false positives, copying noise, overtrading. Frankfurt explicitly mentions reducing false positives once IDs were visible. [1], [32] | **Robust recurring edge** (if the game includes an exploitable informed agent) |
| Exogenous observation threshold triggers | Ignore noisy exogenous signals; act only on large jumps that plausibly represent true events. **[Directly visible]** [10], [11] | For example, if `Δobs > +5`, buy; if `Δobs < -5`, sell. [11] | Add hysteresis + position gating; incorporate into fair value rather than using direct directional entries. | Observation feed (for example, dolphin sightings) [10], [11] | Jump threshold, cooldown, max position | Trap: using small observation moves that are just noise; Stanford explicitly filters for big changes. [10], [11] | **Good but product-dependent** |

## Tooling patterns that repeatedly showed up in strong teams

Tooling is where top competitors consistently created separation: not via exotic ML, but by having a fast loop for **hypothesis → backtest → visual diagnosis → parameter sweep → safe deploy**. [2], [5], [12], [13]

### Tooling components and whether top teams actually had them

| Tool type | Why it matters in Prosperity specifically | Evidence top teams used it | Build complexity | Build timing recommendation |
|---|---|---|---|---|
| Backtester / replay engine | Lets you iterate on parameters and logic faster than the website; enables sweep testing and regression checks. [2], [12] | Linear Utility built a comprehensive backtester and used it for grid-search. [2] Frankfurt relied on a fork of an open backtester + website validation. [1], [32] Alpha Animals relied heavily on an open backtester. [6] | Medium | **Before competition**. A working backtester is the single highest-leverage item. [2], [12] |
| Visualiser / order-book playback | Converts mystery PnL into actionable fixes: you see missed fills, bad quotes, and bot fingerprints. [2], [13] | Frankfurt built a custom dashboard with order-book scatter + trade markers + log sync. [1] Linear Utility built a dashboard with timestamp syncing. [2] Alpha Animals cite the open visualiser as very helpful. [6], [13] | Medium | **Before Day 1** if possible; otherwise build a minimal viewer early in Round 1. |
| Log parser with minimal logging mode | Prevents AWS / Lambda crashes and keeps stateful strategies viable; also keeps logs within size limits. [5], [6] | CMU explicitly reports a memory / Lambda restart wiping rolling windows. [5] Alpha Animals report verbose logging causing AWS Lambda errors. [6] | Low → Medium | **Before competition**: implement log levels and hard caps from day zero. |
| Parameter sweep harness (grid/random search) | Many Prosperity alphas are threshold-based; you win by finding stable plateaus and not overfitting. [1], [2] | Linear Utility modified the trader to accept a parameter dict to grid-search fast. [2] Frankfurt emphasised choosing stable parameter regions over peaks. [1] | Low | **Before competition**: you can build this in a few hours; it pays back immediately. |
| Conversion simulator | Backtesters commonly lag here, but conversion rounds can dominate PnL. [1], [6], [32] | Frankfurt: conversion logic + hidden taker; also notes the backtester cannot reproduce conversions / taker nuance. [1], [32] Alpha Animals: conversions unsupported → misunderstood mechanics and lost profit. [6] | Medium → High | **Before the conversion round** at the latest. If you cannot build it, validate strategies with official tools. [1], [6], [32] |
| Submission automation (CLI submitter) | The submit-loop cost is real: downloading logs, tracking runs, and opening in the visualiser — automation compounds. [15], [16] | `jmerle` provides CLI submitters that upload, monitor, download logs, and optionally open the visualiser. [15], [16] | Low | **Before competition**. Pure quality-of-life that increases iteration count. |
| PnL decomposition (by product / by strategy / by action) | Reveals whether profits come from taking, making, conversion, or copy trades; prevents you from deluding yourself with aggregate PnL. **[Reasonable inference]** built from teams’ emphasis on dashboards. [1], [2], [6], [13] | Teams explicitly cite dashboards used to find undesirable trades and optimise alphas. [1], [2], [6] | Medium | **Before competition** if possible; a minimum viable version can be built during Round 1. |

## Coding and architecture patterns extracted from public repos

### What architectures strong teams actually used (and what that implies)

| Pattern | Public evidence | What it buys you | Risks / failure modes |
|---|---|---|---|
| Modular per-product strategy classes plugged into one `Trader.run` | Frankfurt Hedgehogs: `StaticTrader`, `DynamicTrader`, `InkTrader`, `EtfTrader`, `OptionTrader`, `CommodityTrader` selected inside `Trader.run`, with shared `ProductTrader` utilities and central constants. **[Directly visible]** [32] | Fast parallel development; easier to disable a broken product; natural place for shared risk + logging | If interfaces are inconsistent, refactors become painful mid-round; you need a consistent `orders + conversions + state` contract |
| Parameterised monolith (single Trader with rich config dict and helpers) | Alpha Animals: single Trader with `active_products`, per-product widths, thresholds, and insider regimes in config/state. **[Directly visible]** [6], [7] | Extremely fast to implement; fewer moving parts; config knobs encourage systematic tuning | It can become unmaintainable without conventions; bugs can silently affect multiple products |
| Per-product compute functions inside one class | Stanford Cardinal: single Trader with `compute_orders_*` per product, shared limits/caches, explicit predictor caches, pair trading, and exogenous triggers in helpers. **[Directly visible]** [11] | Simple mental model; easy to add a new product quickly | Harder to share a common execution/risk layer cleanly; logging tends to sprawl |
| Fast research loop: notebooks + vectorised prototypes → implement in trader | Frankfurt advocates quick vectorised notebook backtests early, then backtester integration for robustness. **[Directly visible]** [1], [32] CMU and Alpha Animals both maintain round folders / notebooks for EDA. [5], [6] | You validate ideas cheaply before writing a full simulator-integrated strategy | Notebook alpha often dies in execution; it must be stress-tested in replay for fills / limits |
| Minimal-on-submission debug tooling | CMU removed visualiser code after it triggered a memory / Lambda restart that wiped strategy state. **[Directly visible]** [5] Alpha Animals report verbose logging causing AWS errors. [6] | Prevents “it worked locally, died in prod” | Without a lightweight log protocol you go blind; the solution is log levels + bounded output, not “no logging” |

### Best architecture for a strong but time-constrained competitor

Based on the public evidence, the highest-ROI architecture is:

**A modular core with config-first parameters hybrid:**

- One `Trader.run` that calls `strategy_registry[product].act(state, ctx)` and merges orders + conversions. **[Reasonable inference]** but directly aligned with Frankfurt’s pattern. [32]
- Each product strategy is a small class/module with **three explicit responsibilities**:
  1. compute fair / signals,  
  2. generate desired target inventory or desired quotes,  
  3. call shared execution helpers (“take then make then flatten”). **[Reasonable inference]** supported by repeated “take + make + clear inventory” patterns. [1], [2], [11], [32]
- A single **central config object** (dict or dataclass) with all thresholds / widths / limits and an `active_products` toggle map (Alpha Animals shows this is extremely practical). [6], [7]
- A shared **risk / inventory layer** that enforces:
  - per-product max position,
  - “do not place invalid orders” guardrails,
  - a universal flatten / unwind method at zero edge when capped (as Linear Utility did). [2], [6]
- A shared **logging layer** that can switch to minimal mode on submission, to prevent the failures cited by CMU and Alpha Animals. [5], [6]

Architecture mistakes to avoid (directly motivated by public failures):

- **No guardrails on position-limit violations**: Alpha Animals’ basket arb broke due to a limit-related bug and they abandoned the round’s core alpha. [6], [7]
- **Embedding heavy visualiser/debug code in the submission**: CMU reports Lambda restarts wiping rolling windows. [5]
- **Assuming your backtester models conversion rounds unless you verified it**: both Frankfurt and Alpha Animals warn about conversion/backtester mismatches. [1], [6], [32]

## Best concrete ideas to prototype and the measurement stack to validate them

### Ten concrete strategy ideas “stolen” from strong public evidence

Each idea includes evidence, what to implement, and a robustness rating.

| Idea | What to implement (concretely) | Evidence | Robustness rating |
|---|---|---|---|
| Wall-mid fair estimator + generic MM engine | Detect bid/ask walls (depth threshold + persistence), compute wall-mid; implement “take mispricings vs fair → quote inside spread → flatten if near cap”. | Frankfurt writeup + code. [1], [32] | Robust recurring edge |
| 0-EV inventory clearing | When you are position-capped, allow trades at approximately zero edge to free capacity for future positive edge. | Linear Utility. [2] | Robust recurring edge |
| Fair-from-dominant-MM mid detection | Identify a persistent large market maker and use its mid as fair (less noisy than the mid). | CMU + Linear Utility. [2], [5] | Robust recurring edge |
| Chaos-product throttle + spike MR | Use a volatility trigger (rolling std) to decide when to fade; cap risk to a small fraction of the limit; add a time-in-position stop. | CMU + Alpha Animals code. [5], [6], [7] | Good but product-dependent |
| Basket spread arb with premium-bias correction | Implement `spread = basket - synthetic - premium`; estimate running premium; trade with thresholds or z-score; use stable plateaus. | Frankfurt + Linear Utility. [1], [2], [32] | Robust recurring edge |
| Basket arb under limits via premium-difference | If you cannot fully hedge two baskets, trade `(premium1 - premium2)` and allocate leftover capacity to low-risk MM. | CMU. [5] | Robust recurring edge |
| Informed-trader detector (IDs hidden) | Detect extrema prints like repeated buys at daily lows / sells at daily highs; maintain invalidation logic. | Frankfurt. [1], [32] | Robust recurring edge (if present) |
| Insider detection (IDs visible) via good-trade rate | Per trader, compute the percentage of trades that are profitable vs future mid over horizon `H` (rolling window); flag statistical outliers; then copy-trade selectively. | Alpha Animals. [6], [7] | Robust recurring edge (if present) |
| Options: rolling-mid-IV mean reversion + cross-strike sanity checks | Compute IV per strike; track rolling mean IV; trade deviations; add cross-strike constraints (voucher spread vs strike difference). | CMU + Alpha Animals. [5], [6], [7] | Good but product-dependent |
| Conversion arb break-even engine + fill-adaptive pricing | Build an accurate fee model; compute break-evens; trade when positive; adapt posted edge based on realised fill volume. | Linear Utility + Frankfurt + CMU. [1], [2], [5], [32] | Robust recurring edge |

### Five tooling components to build immediately

| Tool | Why it’s urgent | Public evidence |
|---|---|---|
| Backtest CLI wrapper + parameter sweep runner | Converts “I think this works” into “I can test 200 configs tonight.” | Linear Utility grid-search + `prosperity3bt` CLI. [2], [12] |
| Minimal visual playback (or adopt `jmerle` visualiser) | Most early alpha is discovered visually, not from summary stats. | Frankfurt + Linear Utility dashboards; Alpha Animals’ visualiser reliance. [1], [2], [6], [13] |
| Bounded logging + submission-safe mode | Prevent state wipes / restarts; keep logs workable. | CMU + Alpha Animals failure reports. [5], [6] |
| Conversion simulator (even approximate) | Conversion rounds can be dominated by mechanics; backtest mismatch is common. | Frankfurt + Alpha Animals on conversion gaps. [1], [6], [32] |
| PnL decomposition + trade annotation | Lets you answer: “Did we profit by taking, making, copy trading, or conversions?” | Strongly implied by dashboard-centric workflows. [1], [2], [13] |

### Five diagnostics/metrics to track during testing (high signal, low effort)

These are chosen to align with the exact failure modes and edge sources documented by top public teams.

1. **Inventory utilisation**: fraction of time near position limits (by product). This directly ties to the 0-EV clearing optimisation. [2]  
2. **Edge capture vs spread cost**: realised edge per fill minus estimated half-spread; CMU’s options lesson is that spread costs can dominate the whole trade. [5]  
3. **Fill-rate by quote type**: passive quotes filled vs not; in conversion / taker rounds, probabilistic taker capture is the edge. [1], [2], [32]  
4. **PnL by mode**: taking vs making vs flatten / unwind vs conversion vs copy trades (separate buckets). This mirrors the dashboard-debugging workflow teams used. [1], [2], [6], [13]  
5. **State continuity checks**: detect if rolling buffers reset mid-day (symptom of restarts / parse failures). CMU’s account makes this non-optional. [5]

### Five implementation shortcuts that preserve most of the value

1. **Use a single shared `take_then_make` helper** for every product; plug in different fairs / thresholds. This matches how multiple teams reused the same base logic across products. [1], [2], [5], [32]  
2. **Put all thresholds in one config dict** and thread it through strategies; Alpha Animals’ code shows this is how you iterate without refactoring. [6], [7]  
3. **Hardcode coefficients only when the product definition literally hardcodes them** (basket composition, strike prices), and keep a learnable intercept / premium term that updates online. [1], [6], [32]  
4. **For options, start with rolling-IV mean and cross-strike sanity checks before any smile fitting**; CMU’s experience shows a fitted baseline can break on submission day. [5], [6], [7]  
5. **For conversions, build a break-even calculator first and hidden-taker logic second**; both CMU and Frankfurt show the baseline arb matters, but the hidden-taker layer is where the extra step-function PnL comes from. [1], [2], [5], [32]

## What not to waste time on

This section is intentionally blunt and anchored to “teams tried it and it did not pay” or “it was too brittle.”

| Rabbit hole | Why it’s low value (per public evidence) | Evidence | Classification |
|---|---|---|---|
| Heavy ML on exogenous theme variables without a mechanics thesis | Linear Utility tried correlations / regressions / feature engineering on sunlight, humidity, tariffs, etc. and concluded it was likely a distraction; the real edge was market mechanics (taker + conversion). [2] | [2] | Flashy but overrated |
| Sophisticated volatility-surface fitting as a first implementation | Alpha Animals explicitly list volatility-surface fitting as too complex to implement reliably under time constraints; CMU found their quadratic IV fit failed on the submission day and needed a rolling-mean fallback. [5], [6] | [5], [6] | Situational niche edge (only after the baseline works) |
| Full delta hedging at high frequency without cost accounting | CMU quantified hedging spread costs and concluded it could be optimal *not* to hedge; Linear Utility also show hedge feasibility is constrained by limits. [2], [5] | [2], [5] | Flashy but overrated (unless costs are low) |
| Anything that requires the backtester to be perfect | Public tooling explicitly documents cases where matching differs materially; multiple teams warn about conversion / bot-nuance mismatches. [1], [6], [18], [32] | [1], [6], [18], [32] | Mostly not worth replicating as a belief |
| Cross-year oracle exploits as your main plan | Linear Utility’s cross-year predictor hack was silly-but-effective in that edition; it is inherently brittle and may be prevented or simply not repeat. [2] | [2] | Situational niche edge |

## End-state deliverables

### Top ten concrete ideas stolen from public evidence

1. Wall-mid / dominant-liquidity fair estimator + MM engine (Frankfurt Hedgehogs). [1], [32]  
2. Take-then-make-then-flatten as a reusable execution skeleton (repeated across top repos). [1], [2], [5], [32]  
3. 0-EV inventory clearing to unlock limit-capped opportunity (Linear Utility). [2]  
4. Basket premium arb with running premium correction (Frankfurt Hedgehogs). [1], [32]  
5. Basket hedge-under-limits using `(premium1 - premium2)` and leftover-capacity MM (CMU Physics). [5]  
6. Event-triggered mean reversion with risk throttle on chaos product (CMU Physics; Alpha Animals’ 3-sigma spike logic). [5], [6], [7]  
7. Insider detection if IDs are visible: rolling good-trade scoring per trader + selective copy trading (Alpha Animals). [6], [7]  
8. Insider inference if IDs are hidden: daily-extrema print detection with invalidation logic (Frankfurt Hedgehogs). [1], [32]  
9. Options baseline: rolling-mid-IV mean + cross-strike consistency arb before fancy fitting (CMU Physics; Alpha Animals). [5], [6], [7]  
10. Conversion arb engine: fee-correct break-even + fill-adaptive pricing + hidden-taker capture (Linear Utility + Frankfurt Hedgehogs). [1], [2], [32]  

### Top five tools to build immediately

1. Backtester + batch parameter sweep runner (or adopt `prosperity3bt` and wrap it). [2], [12]  
2. Visual playback (adopt `jmerle` visualiser or build a minimal stepper). [1], [6], [13]  
3. Submission-safe logging (hard size limits, log levels, fail-closed). [5], [6]  
4. Conversion simulator (even approximate) + break-even-calculator test suite. [1], [5], [6], [32]  
5. PnL decomposition dashboard: by product and by mode (take / make / flatten / conversion / copy). [1], [2], [13]  

### Best architecture for your own Prosperity codebase

- **Core**: one `Trader.run` + registry of product strategies (Frankfurt-style modularity). [32]  
- **Each product strategy** returns: (a) orders, (b) optional conversions, (c) minimal debug events; no direct printing except through a bounded logger (CMU / Alpha Animals failure lessons). [5], [6]  
- **Shared utilities**: fair estimation, order-book helpers, inventory/risk constraints, and a `take_then_make_then_flatten` execution helper. [1], [2], [11], [32]  
- **Config-first**: one dict/dataclass with all thresholds and an `active_products` toggle map (Alpha Animals-style fast iteration). [6], [7]  
- **State**: explicit rolling buffers per product + an integrity check so you notice when state resets mid-day. [5], [7]  

### What not to waste time on

- Predictive modelling on theme exogenous variables until you have ruled out pure mechanics arb (Linear Utility found the mechanics were the edge). [2]  
- Smile fitting and advanced Greeks infrastructure before you can reliably compute IV, compare it to a rolling baseline, and account for hedging costs (CMU and Alpha Animals both show the baseline-first path). [5], [6]  
- Blindly trusting local backtests for conversion rounds or bot-interaction-heavy edges; validate those mechanics explicitly (Frankfurt + Alpha Animals). [1], [6], [32]  
- Any submission that ships heavy debug components or unbounded logging (CMU memory restart; Alpha Animals AWS errors). [5], [6]  
- Cross-year oracle hacks as a default strategy direction (too brittle; may not repeat or may be policed). [2]  

### If you only had two weekends to prepare, what to build in order

**Weekend one (foundation + Round-1 dominance)**  
Goal: be immediately profitable on fixed-fair and dominant-liquidity-fair products, and not lose money on chaos.

1. Install/adopt a `prosperity3bt`-style workflow: CLI runs, merged PnL, log outputs; stub a parameter-sweep wrapper. [12]  
2. Build your config-first Trader skeleton with:
   - registry per product,
   - shared execution helper,
   - position-limit guardrails,
   - minimal bounded logging. [5], [6], [32]  
3. Implement wall-mid estimator + fixed-fair MM template + 0-EV clearing. [2], [5], [32]  
4. Implement the chaos-product module: size throttle + spike mean reversion + time-in-position stop. [5], [6], [7]  
5. Implement dashboards/diagnostics: inventory utilisation, edge capture vs spread cost, PnL decomposition. [1], [2], [5], [13]  

**Weekend two (structural alpha modules that win rounds)**  
Goal: be ready for baskets, options, and conversions with robust baselines and fallbacks.

1. Basket arb engine: spread computation, premium estimator, z-score/threshold entry, hedge allocation under limits; add premium-difference mode. [1], [2], [5], [32]  
2. Insider module: pipeline for trader scoring if IDs exist, and extrema-trader inference when they do not. [1], [6], [7], [32]  
3. Options baseline: Black–Scholes IV computation, rolling mean IV, cross-strike sanity arb; add cost accounting for hedging. [5], [6], [7], [32]  
4. Conversion engine: fee-correct break-even + conversion scheduling; add fill-adaptive edge search (volume-based). [1], [2], [5], [32]  
5. Submission automation (CLI submitter) so you can iterate more often with less friction. [15], [16]

## References

[1]: https://github.com/TimoDiehm/imc-prosperity-3
[2]: https://github.com/ericcccsliu/imc-prosperity-2
[5]: https://github.com/chrispyroberts/imc-prosperity-3
[6]: https://github.com/CarterT27/imc-prosperity-3
[7]: https://github.com/CarterT27/imc-prosperity-3/blob/main/trader.py
[10]: https://github.com/ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal
[11]: https://github.com/ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal/blob/main/trader.py
[12]: https://github.com/jmerle/imc-prosperity-3-backtester
[13]: https://github.com/jmerle/imc-prosperity-3-visualizer
[15]: https://github.com/jmerle/imc-prosperity-3-submitter
[16]: https://github.com/jmerle/imc-prosperity-2-submitter
[17]: https://github.com/jmerle/imc-prosperity-2
[18]: https://github.com/jmerle/imc-prosperity-2-backtester/releases
[32]: https://github.com/TimoDiehm/imc-prosperity-3/blob/main/FrankfurtHedgehogs_polished.py