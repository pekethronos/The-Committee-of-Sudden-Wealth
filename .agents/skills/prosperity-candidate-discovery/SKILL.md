---
name: prosperity-candidate-discovery
description: Proactively scan Prosperity datasets, replay outputs, and prior-round artifacts for plausible missed trades, suspicious triggered trades, and repeated candidate patterns worth deeper review. Use when the user wants Codex to find candidate opportunities or failure cases before changing strategy code.
---

# Prosperity Candidate Discovery

Find candidate opportunities from data and replay outputs without assuming they are real edges and without changing strategy code by default.

## Core Workflow

1. Define the scope.
- Identify the round, products, data source, and replay outputs to scan.
- Read the current operating context before interpreting cases:
  - `/Users/sb/tcosw/README.md`
  - `/Users/sb/tcosw/CODEX.md`
  - `/Users/sb/tcosw/docs/day0-intake.md` when official Day 0 or tutorial materials exist
  - `/Users/sb/tcosw/docs/trade-candidate-log.md`
- Prefer official round data, replay outputs, and structured logs over screenshots or memory.

2. Pull the retained evidence.
- Start from public round files in `data/` and replay artifacts in `artifacts/`.
- If official Prosperity 4 data is available, treat it as highest priority.
- If the official tutorial bundle is active, start from:
  - `data/TUTORIAL_ROUND_1/`
  - `artifacts/official_tutorial/replays/round0.log`
  - `scripts/decompose_backtest_trades.py`
  - `scripts/open_visualizer.py`
- If only prior-round public data exists, be explicit that the output is practice evidence, not Prosperity 4 confirmation.

3. Generate candidate windows objectively.
- Search for:
  - strong missed opportunities
  - suspicious triggered trades
  - repeated false-positive patterns
  - repeated near-miss windows that suggest one missing gating rule
- Rank cases using measurable evidence:
  - edge versus fees and spread
  - adverse excursion
  - follow-through
  - proximity to actual fills
  - repeat count across windows

4. Review with no-lookahead discipline.
- Use future path only for post-trade evaluation.
- Do not justify live entry logic from hindsight path alone.
- Compare each candidate against nearby non-candidates and nearby bad trades.
- Prefer `uncertain` over forcing a pattern claim from one attractive chart.

5. Classify and record.
- Label every reviewed case as:
  - `valid target`
  - `invalid / visually misleading`
  - `uncertain`
- Update `/Users/sb/tcosw/docs/trade-candidate-log.md` when the case should survive beyond the current turn.
- Store durable evidence bundles under `/Users/sb/tcosw/docs/candidate-artifacts/` when the case may matter after raw data rolls away.

6. Stop or hand off.
- If the evidence is weak, stop after analysis.
- If the evidence supports a real implementation pass, switch to `$prosperity-strategy-iteration`.
- If the evidence is for a tutorial upload candidate, end with one explicit recommendation:
  - keep current baseline
  - patch one rule now
  - reject the idea for the current upload

## Output Standard

Return:

- exact windows reviewed
- the evidence summary for each candidate
- measured favorable and adverse path
- the classification for each candidate
- whether the set justifies strategy iteration now
- the exact upload recommendation for the current baseline if a tutorial or live upload is in play

## References

- For the reusable checklist and output schema, read:
  - `/Users/sb/tcosw/.agents/skills/prosperity-candidate-discovery/references/workflow.md`
