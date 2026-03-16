---
name: prosperity-manual-round-solver
description: Solve or template Prosperity manual challenges with fast, structured working. Use when a manual round is live, when the user wants reusable solution templates for likely manual problem types, or when a prior manual challenge should be analyzed for speed and repeatability.
---

# Prosperity Manual Round Solver

Use this skill when the manual challenge matters. Do not let it consume time meant for the algorithmic round unless the EV is clear.

## Core Workflow

1. Capture the exact prompt.
- Save the full text, constraints, and any tables or images.
- Record the time budget and submission deadline.

2. Classify the problem type.
- Typical buckets:
  - probability
  - optimization
  - graph or path
  - game or equilibrium
  - combinatorics

3. Solve with visible working.
- Prefer the shortest correct path.
- Use quick scripts when arithmetic is error-prone.
- Keep the final answer and the reusable pattern separate.

4. Preserve the pattern.
- Update `/Users/sb/tcosw/docs/manual-round-log.md` with the problem type, method, and reusable idea.
- Save any helper script or artifact under `artifacts/` if it may be useful again.

## Output Standard

Return:

- the classified problem type
- the working approach
- the final answer
- the reusable pattern or shortcut

## References

- For the working template, read:
  - `/Users/sb/tcosw/.agents/skills/prosperity-manual-round-solver/references/workflow.md`
