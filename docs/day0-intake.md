# Day 0 Intake

Captured on `2026-03-16` from the Day 0 uplink, the algorithmic challenge page, and the official tutorial files placed in `data/TUTORIAL_ROUND_1/`.

## Official references

- Prosperity 4 wiki: `https://imc-prosperity.notion.site/prosperity-4-wiki`
- Upload page constraint: Python files only, maximum size `100 KB`
- Upload cadence: unlimited uploads, latest upload replaces the previous one
- Tutorial note: tutorial round does not produce final results

## Uplink notes

- Current phase is transit and practice, not the live trading round.
- Tutorial practice products are `TOMATOES` and `EMERALDS`.
- The wiki and downloadable data capsule are the primary sources during this phase.
- A dedicated adviser must be chosen before landing; if not, the system auto-assigns one.

## Data intake

- Local files:
  - `data/TUTORIAL_ROUND_1/prices_round_0_day_-2.csv`
  - `data/TUTORIAL_ROUND_1/prices_round_0_day_-1.csv`
  - `data/TUTORIAL_ROUND_1/trades_round_0_day_-2.csv`
  - `data/TUTORIAL_ROUND_1/trades_round_0_day_-1.csv`
- Schema matches the prior Prosperity price and trade CSV layout already supported by `prosperity3bt`.
- Product set is exactly `EMERALDS` and `TOMATOES`.
- Official tutorial limits from the wiki page:
  - `EMERALDS: 80`
  - `TOMATOES: 80`
- Current local note: `prosperity3bt` does not ship those product names in its internal limit table, so local tutorial replays use `scripts/run_backtest_with_limit_overrides.py` to patch the official limits without modifying the dependency.

## Product triage

- `EMERALDS`
  - Archetype: fixed-fair market making
  - Evidence: both tutorial days center almost exactly on `10,000`
  - First-pass baseline: fixed fair `10,000` with inventory clearing and limit `80`
- `TOMATOES`
  - Archetype: book-driven fair / short-horizon mean reversion
  - Evidence: tutorial-day means differ materially (`~5008` on day `-2`, `~4978` on day `-1`), so a single fixed fair across both days is weak
  - First-pass baseline: dominant-liquidity estimator rather than hardcoded fair, with limit `80`

## Immediate Day 0 action

1. Use `rounds/tutorial_round_1/trader.py` as the current upload candidate.
2. Run `./scripts/run_official_tutorial_backtest.sh`.
3. Open the resulting log in the visualizer with `./scripts/open_visualizer.py artifacts/official_tutorial/replays/round0.log --no-open`.
4. Keep `EMERALDS` and `TOMATOES` inside the recurring market-making archetypes from the research; the profitable Day 0 work is in sizing, taking, and fair estimation, not in adding a new strategy family.
5. Upload only the standalone single-file trader, not repo-local wrappers.

## Current tutorial upload candidate

- `EMERALDS`
  - Keep the fixed-fair baseline at `10,000`.
  - Use aggressive take / clear / make logic around the fixed fair.
- `TOMATOES`
  - Use EMA-based fair estimation with one-step mean reversion, inventory skew, and an adverse-volume filter on taker trades.
  - Keep tomato buy-taking more permissive than tomato sell-taking; the hidden live tutorial review showed tomato sell-takes were the weaker side.
  - Persist the tomato EMA state through `traderData` rather than relying on in-memory state.
- Why this is the upload candidate:
  - It is upload-safe as a true single-file submission that only depends on `datamodel` and the Python standard library.
  - It improved total official tutorial replay PnL from `+8,022` to `+31,558.0`.
  - The gain remained strong across both official tutorial days even after the live-driven tomato sell-taker tightening.
  - Replay inspection showed the stronger candidate still stayed well inside the official `80` position limit on both products.
  - Live tutorial submission `576` confirmed the hidden evaluator differs from the public sample path, so the current file includes one small hidden-evidence patch rather than a larger public-only re-tune.

## Reference files

- Current upload file: `rounds/tutorial_round_1/trader.py`
- Original teammate candidate preserved for reference: `rounds/tutorial_round_1/algo_original.py`
