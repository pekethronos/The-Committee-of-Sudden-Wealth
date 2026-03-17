---
name: prosperity-strategy-iteration
description: Refine Prosperity trader logic from concrete replay evidence. Use when the user has a strategy hypothesis, wants trader code changes, wants replay validation, needs baseline versus current comparison, or wants the iteration and candidate logs updated after a strategy pass.
---

# Prosperity Strategy Iteration

Refine the trader from concrete replay evidence, not from chart impressions alone.

## Core Workflow

1. Build the case list.
- Extract exact products, timestamps, and target or bad trades from replay outputs, logs, or candidate review.
- Treat user-suggested setups as hypotheses, not targets to defend.
- Read:
  - `/Users/sb/tcosw/README.md`
  - `/Users/sb/tcosw/CODEX.md`
  - `/Users/sb/tcosw/docs/day0-intake.md` when official Day 0 or tutorial files exist
  - `/Users/sb/tcosw/docs/trade-candidate-log.md`
  - `/Users/sb/tcosw/docs/strategy-iteration-log.md`
  - `/Users/sb/tcosw/docs/baseline-snapshots.md`

2. Validate the evidence.
- Use replay outputs, structured logs, and official round files as the source of truth.
- If a downloaded submission bundle exists, include that live evidence in the comparison before promoting a new upload file.
- Keep the analysis no-lookahead.
- Separate:
  - desired trades that were missed
  - bad trades that should be suppressed
  - uncertain windows that need more examples

3. Decide whether a change is justified.
- If the case does not support a robust rule, stop.
- If multiple refinements exist, prefer the one that:
  - captures the intended windows
  - suppresses known bad windows
  - adds the least complexity

4. Modify strategy code first.
- Change trader logic before adding more analysis glue.
- Preserve deterministic replay where possible.
- Prefer reusable modules and shared helpers over product-specific sprawl.

5. Replay before and after.
- Run the same window before and after the change.
- If data volume allows, run at least one challenge window not used to build the change.
- If the official tutorial bundle is active, replay both tutorial days before claiming a better upload candidate.
- Compare:
  - trade count
  - realized PnL
  - added, removed, and altered trades
  - inventory stress and obvious risk regressions

6. Update logs and artifacts.
- Append a concise entry to `/Users/sb/tcosw/docs/strategy-iteration-log.md`.
- Update `/Users/sb/tcosw/docs/trade-candidate-log.md` for any surviving rejected or uncertain cases.
- Save replay outputs or diffs under `/Users/sb/tcosw/artifacts/` when they matter beyond the current turn.
- If the goal is an upload candidate, state clearly which file should be uploaded and why.
- Validate the packaging too: upload candidates must remain standalone single-file submissions.

## Validation Standard

Do not stop at "the chart looks better."

Require, at minimum:

- repeatable replay before and after
- explicit trade-level differences
- challenge-window evidence when the data supports it
- a written note if the sample is too small for strong confidence
- a single explicit upload recommendation when the user is asking for a final trader

## References

- For the reusable checklist and log schema, read:
  - `/Users/sb/tcosw/.agents/skills/prosperity-strategy-iteration/references/workflow.md`
