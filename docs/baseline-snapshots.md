# Baseline Snapshots

Use this file for wider-window replay summaries so cumulative drift is visible.

## Snapshot template

### YYYY-MM-DD

- Commit / branch:
- Dataset:
- Window:
- Trade count:
- Realized PnL:
- Win rate:
- Max drawdown:
- Notes:

## Snapshots

### 2026-03-16

- Commit / branch: `uncommitted scaffold on main`
- Dataset: `prosperity3bt` bundled resources
- Window: `round 0 day -1`
- Trade count: tutorial artifact generated; use `scripts/diff_backtest_trades.py --show-unchanged` for exact count
- Realized PnL: `+3,203`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: first end-to-end local replay for the repo using the shared runtime scaffold in `rounds/tutorial/trader.py`

### 2026-03-16

- Commit / branch: `post-probe pre-commit state on main`
- Dataset: `prosperity3bt` bundled resources
- Window: `round 2 days -1/0/1`
- Trade count: `21,458` submission trades
- Realized PnL: `+57,018.5`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: round-2 baseline uses only the positive fixed-fair and dominant-liquidity core; generic basket variants were left out of the default trader after challenge-window sweeps stayed negative on the bundled public data

### 2026-03-16

- Commit / branch: `post-Day-0 intake pre-commit state on main`
- Dataset: official tutorial bundle in `data/TUTORIAL_ROUND_1/`
- Window: `round 0 days -2/-1`
- Trade count: `1,945` submission trades
- Realized PnL: `+8,022`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: first official Prosperity 4 tutorial baseline; local replay uses product-limit overrides because the public backtester does not yet know the `EMERALDS` and `TOMATOES` names

### 2026-03-16

- Commit / branch: `post-Day-0 tutorial sweep pre-commit state on main`
- Dataset: official tutorial bundle in `data/TUTORIAL_ROUND_1/`
- Window: `round 0 days -2/-1`
- Trade count: `1,218` submission trades
- Realized PnL: `+17,408.5`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: current tutorial upload candidate keeps `EMERALDS` fixed fair and refines `TOMATOES` within the same dominant-liquidity archetype; best candidate on the official bundle used wider quotes, stricter tomato taking, and effectively no tomato clearing because observed inventory stayed far below the official limit

### 2026-03-16

- Commit / branch: `post-teammate-integration pre-commit state on main`
- Dataset: official tutorial bundle in `data/TUTORIAL_ROUND_1/`
- Window: `round 0 days -2/-1`
- Trade count: `1,995` submission trades
- Realized PnL: `+31,797.0`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: current tutorial upload candidate is now a standalone single-file submission in `rounds/tutorial_round_1/trader.py`; it integrates the teammate market-making logic and persists tomato EMA state through `traderData`

### 2026-03-17

- Commit / branch: `post-live-review pre-commit state on main`
- Dataset: hidden live tutorial submission `576`
- Window: hidden evaluator day from downloaded submission logs
- Trade count: `172` submission trades
- Realized PnL: `+2,434.578125`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: hidden evaluator path differs from the public `prices_round_0_day_-1.csv` on `371` of `4,000` compared product-timestamp rows; live estimated product PnL was approximately `EMERALDS +1,050` and `TOMATOES +1,384`

### 2026-03-17

- Commit / branch: `post-live-review pre-commit state on main`
- Dataset: hidden live tutorial submission `1462`
- Window: hidden evaluator day from downloaded submission logs
- Trade count: `166` submission trades
- Realized PnL: `+2,436.296875`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: repeated hidden run matched the same hidden-public mismatch profile as `576`; repeated review rejected further tomato buy-side and asymmetric-reversion changes, so the current standalone trader remains the best upload candidate
