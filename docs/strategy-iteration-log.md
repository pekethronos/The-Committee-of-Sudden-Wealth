# Strategy Iteration Log

Record every meaningful strategy change here.

Use this log to preserve:

- the exact hypothesis
- the development-window evidence
- any challenge-window evidence
- what changed in code
- what trades were added, removed, or altered

If the sample is tiny, say so explicitly. Do not pretend small-N validation is stronger than it is.

## Entry template

### YYYY-MM-DD - short change label

- Status: `provisional` or `confirmed`
- Area: `market making` / `basket` / `conversion` / `options` / `risk` / `tooling`
- Hypothesis:
- Trigger for the work:
- Development window:
- Challenge window:
- Before:
- After:
- Trade-level changes:
- PnL / trade count deltas:
- Parameter sensitivity note:
- Rejected alternatives:
- Next follow-up:

## Entries

### 2026-03-16 - runtime-backed tutorial scaffold

- Status: `confirmed`
- Area: `tooling`
- Hypothesis: a config-first shared runtime with fixed-fair and dominant-liquidity modules should immediately outperform the placeholder starter trader on bundled round-0 practice data.
- Trigger for the work: repo had only research docs and a placeholder trader path with no reusable runtime.
- Development window: `prosperity3bt` bundled `round 0 day -1`
- Challenge window: not run yet
- Before: original placeholder tutorial trader produced `0` total profit on the bundled tutorial replay.
- After: runtime-backed tutorial trader produced `+3,203` total profit (`KELP +989`, `RAINFOREST_RESIN +2,214`) on the same replay.
- Trade-level changes: switched from a hardcoded placeholder to a shared runtime with fixed-fair resin handling and dominant-liquidity kelp handling; added diff and parameter-sweep tooling around the replay loop.
- PnL / trade count deltas: tutorial replay moved from `0` to `+3,203`; a deliberately bad resin config degraded the same replay to `+819`, validating that config sweeps now propagate into artifacts.
- Parameter sensitivity note: the resin fair-value perturbation was intentionally large and materially degraded results; smaller sweeps should be explored next on stable regions rather than peaks.
- Rejected alternatives: keeping a self-contained one-off trader file separate from the shared runtime.
- Next follow-up: add challenge-window practice runs on additional bundled rounds and extend the runtime with basket and conversion-aware modules when round files support them.

### 2026-03-16 - visualizer-compatible loop and mechanics probes

- Status: `confirmed`
- Area: `tooling`
- Hypothesis: the prep repo should not assume the visualizer or simulator mechanics are working just because the backtester runs; visualizer-compatible logging, explicit mechanics probes, and challenge-window basket checks are required to keep the workflow aligned with the research.
- Trigger for the work: the visualizer failed to parse the repo's initial replay logs, and the first generic round-2 basket implementation lost heavily across the bundled public days.
- Development window: `round 0 day -1`, custom controlled probe datasets, and bundled `round 2 days -1/0/1`
- Challenge window: full bundled `round 2`
- Before: tutorial logs were not visualizer-compatible; no controlled mechanics probes existed; generic round-2 basket execution with component hedging produced `-728,505` over bundled round-2 days.
- After: tutorial logs load in the Prosperity 3 visualizer; controlled probes confirm end-of-iteration cancellation, product-limit cancellation, and `--match-trades` behavior; round-2 baseline trader now stays on the positive fixed-fair plus dominant-liquidity core and produces `+57,018.5` over bundled round-2 days.
- Trade-level changes: added visualizer-format compressed logging, `traderData`-backed runtime persistence, trade decomposition tooling, controlled probe datasets and traders, an explicit visualizer server helper, and a basket engine with a minimum-history gate that remains available for experiments rather than enabled by default.
- PnL / trade count deltas: round-2 no-basket baseline finished at `+57,018.5` with `21,458` submission trades; generic basket variants finished at `-728,505`, `-267,125`, `-77,762`, `-15,654`, and `-14,634` on the same bundled data windows depending on hedging and threshold settings.
- Parameter sensitivity note: basket performance is highly sensitive and remained negative across the bundled challenge window even after stricter thresholds; keep the module experimental until visual inspection on actual round data identifies a repeatable edge.
- Rejected alternatives: assuming `prosperity3bt --vis` implied log compatibility, and defaulting the round-2 practice trader to a generic basket strategy just because basket stat-arb is a recurring archetype.
- Next follow-up: only re-enable basket logic in a default trader after candidate discovery and visual review on the relevant round data support the thresholds.

### 2026-03-16 - official Day 0 tutorial intake and baseline

- Status: `confirmed`
- Area: `tooling`
- Hypothesis: the fastest correct Day 0 move is to ingest the official tutorial files exactly as provided, patch only the tooling breakage needed to replay them locally, and ship the simplest baseline that matches the two tutorial archetypes.
- Trigger for the work: official Day 0 materials arrived with a new wiki, `EMERALDS` and `TOMATOES` tutorial files, and confirmed tutorial limits.
- Development window: official tutorial `round 0 days -2/-1` from `data/TUTORIAL_ROUND_1/`
- Challenge window: same official tutorial bundle; no additional official round data yet
- Before: repo had no runner for the official tutorial folder, no recorded Day 0 intake, and the public backtester crashed on the new product names because its built-in limit table did not include `EMERALDS` or `TOMATOES`.
- After: repo now has a Day 0 intake note, a limit-override backtest wrapper, an official tutorial replay script, and a tutorial-round baseline trader using `EMERALDS` fixed fair plus `TOMATOES` dominant-liquidity; the official tutorial baseline replay produced `+8,022` over the two provided days.
- Trade-level changes: added `scripts/run_backtest_with_limit_overrides.py`, `scripts/run_official_tutorial_backtest.sh`, and `rounds/tutorial_round_1/trader.py`; patched the baseline to use the official `80` position limits from the wiki.
- PnL / trade count deltas: official tutorial replay finished `EMERALDS +1,464`, `TOMATOES +6,558`, total `+8,022`, with `1,945` submission trades.
- Parameter sensitivity note: `EMERALDS` is stable enough to keep fixed fair at `10,000`; `TOMATOES` mean shifts across the two tutorial days, so keep it on a book-driven fair until visual review identifies something stronger.
- Rejected alternatives: hardcoding a single fair for `TOMATOES`, renaming official files to match prior Prosperity product names, or editing the installed backtester package directly.
- Next follow-up: run candidate discovery on `TOMATOES` using the official tutorial log and only then decide whether any extra tomato-specific logic is worth adding.
