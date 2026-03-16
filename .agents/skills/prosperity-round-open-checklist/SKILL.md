---
name: prosperity-round-open-checklist
description: Audit newly released Prosperity rules, wiki pages, and round files against prior assumptions. Use when official Prosperity materials drop, when a new round opens, or when the user wants a Day 1 triage pass before strategy work starts.
---

# Prosperity Round Open Checklist

Use this skill the moment official Prosperity materials or a new round becomes available.

## Core Workflow

1. Capture the source of truth.
- Save the exact official URLs, files, and release date.
- Read:
  - `/Users/sb/tcosw/README.md`
  - `/Users/sb/tcosw/CODEX.md`
  - `/Users/sb/tcosw/docs/round-open-checklist.md`
  - `/Users/sb/tcosw/prosperity_competition_research.md`

2. Diff assumptions against reality.
- Check for changes in:
  - data schema
  - order semantics
  - position limits
  - conversions
  - runtime limits
  - logging limits
  - allowed libraries
  - manual-round rules

3. Sort each product into an archetype.
- Start with:
  - fixed fair value
  - dominant-liquidity fair
  - basket or spread
  - conversion
  - options
  - chaotic or bait product
- Prefer the simplest viable first-pass strategy.

4. Identify broken assumptions immediately.
- List what in the current scaffold still holds.
- List what must be patched before shipping a round submission.
- List rabbit holes to avoid for this round.

5. Record the triage result.
- Update `/Users/sb/tcosw/docs/round-open-checklist.md` with the actual round findings.
- Save official files under `data/`.
- If strategy work should begin, hand off to `$prosperity-candidate-discovery` or `$prosperity-strategy-iteration`.

## Output Standard

Return:

- confirmed rule and schema changes
- product archetype classification
- broken assumptions
- immediate 6-hour build priorities
- explicit do-not-build items for that round

## References

- For the Day 1 triage checklist, read:
  - `/Users/sb/tcosw/.agents/skills/prosperity-round-open-checklist/references/workflow.md`
