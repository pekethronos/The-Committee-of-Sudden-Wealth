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
