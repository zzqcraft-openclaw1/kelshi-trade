# Prediction Framework

## Purpose

This document defines the research and paper-trading framework for `kelshi-trade`.

Current scope is deliberately narrow:
- paper-trading and simulation only
- whitelist-gated market selection
- **sports markets only**

The system should estimate probabilities, compare them to market-implied pricing, and generate paper-trading decisions only when a defined research edge exists.

> Main trading rule: 少做、做窄、做有验证优势的；没 edge 就空仓；先想怎么死，再想赚多少。

## Whitelist Scope

The active market whitelist currently contains one category only:
- `sports`

Any market outside the sports category is out of scope and must be skipped during:
- market ingestion
- signal generation
- order simulation
- portfolio/risk evaluation

## Research Loop

The default workflow is:
1. sync candidate sports markets
2. collect market metadata and quote snapshots
3. generate features for each market
4. produce a prediction or fair-value estimate
5. compare prediction against market-implied probability
6. apply confidence and market-quality filters
7. emit a paper-trade signal only if the edge clears the threshold
8. simulate execution and record outcomes
9. review results after settlement

## Inputs

The framework may use the following inputs for research:
- sports market metadata
- event timing and settlement rules
- quote snapshots and orderbook-derived state
- historical outcomes and prior market behavior
- external sports-related features used for prediction research

All inputs used in a run should be traceable in logs or reproducible configuration.

## Signal Standard

A valid signal should include:
- market identifier
- market category
- predicted probability or fair-value estimate
- market-implied probability
- estimated edge
- confidence score
- timestamp
- brief rationale

Signals must be rejected if:
- category is not `sports`
- required inputs are missing
- market quality checks fail
- confidence is below the configured threshold
- estimated edge does not clear the decision threshold

## Decision Logic

A paper trade may be simulated only when all of the following are true:
- the market is on the whitelist
- the market passes quality filters
- the prediction pipeline produced a valid signal
- expected edge exceeds the minimum threshold
- slippage/fees assumptions do not erase the edge
- all iron-rule risk checks pass

## Evaluation

Each strategy iteration should be measured with both prediction and trading metrics.

Prediction metrics:
- calibration quality
- Brier score
- log loss
- hit rate by market segment

Simulation metrics:
- expected edge vs realized outcome
- paper PnL
- drawdown
- blocked-trade counts
- rule-violation counts
- results by sport / market type / event window

## Daily Operating Pattern

The expected daily cycle is:
- refresh sports-market universe
- capture quotes
- run the prediction pipeline
- simulate qualifying trades
- inspect exposures and logs
- review settled events
- document lessons before changing any model or heuristic

## Change Discipline

Prediction logic should not be changed casually.

Before enabling a meaningful strategy change in paper runs:
- document the hypothesis
- record the configuration change
- provide evidence from prior analysis/backtest/replay
- keep the change auditable and reversible
