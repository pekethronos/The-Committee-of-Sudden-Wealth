# Round Open Checklist

Use this when the official Prosperity 4 wiki or a new round drops.

## Official materials diff

- capture the exact release date and source URL
- save or link the official rules, tutorial page, and algorithm docs
- diff the new `TradingState` or equivalent schema against prior assumptions
- confirm position limits, order lifetime, conversions, and persistence semantics
- confirm runtime, allowed libraries, log limits, and submission constraints
- confirm whether trader IDs, conversions, manual tasks, or new observation fields exist

## Data intake

- save the official files under `data/`
- record round name, products, and any new fields
- note whether sample data appears to overlap with live or tutorial periods
- verify the local replay path can parse the files unchanged

## Strategy triage

- map each product into an archetype before inventing bespoke logic
- start with fixed-fair, dominant-liquidity, basket, conversion, options, or chaos classification
- explicitly mark exogenous variables as `proven useful`, `unclear`, or `likely bait`
- identify the simplest viable first-pass strategy for each product

## Tooling checks

- replay a baseline trader locally
- verify logs open cleanly in the visualizer
- confirm diff and artifact paths are working
- create the first baseline snapshot for the round

## Go / no-go questions

- what changed from prior Prosperity assumptions?
- what broke in the current scaffolding?
- what can ship within the next 6 hours?
- what should not be built this round?
