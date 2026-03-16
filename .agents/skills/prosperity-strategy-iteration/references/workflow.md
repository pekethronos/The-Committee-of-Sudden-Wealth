# Strategy Iteration Reference

## Default checklist

1. define the target and false-positive cases
2. confirm the exact replay window and artifacts
3. patch the smallest viable rule or module
4. replay baseline and current on the same window
5. replay at least one challenge window when possible
6. record trade-level changes and confidence level

## Confidence rules

- fewer than 10 trades: label the result `provisional`
- one clean case with no analogs: usually not enough
- improvements that only move one trade and degrade the challenge window are not real wins

## Preferred change order

- shared risk and execution helpers
- fair-value estimation improvements
- entry gating
- sizing
- exits

Avoid changing entry, sizing, and exit logic at once unless the old structure is clearly broken.
