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
