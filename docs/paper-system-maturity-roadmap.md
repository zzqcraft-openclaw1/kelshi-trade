# Paper System Maturity Roadmap

This roadmap is for improving the `kelshi-trade` system as a **paper-only / research-only** platform.

It is not a rollout plan for live trading.

## Goal

Build a paper-review and forecasting system that is:
- measurable
- reproducible
- auditable
- disciplined
- useful for research iteration

## Stage 1 — Data Reliability

### Objectives
- capture consistent raw market snapshots
- store normalized NBA market records
- maintain clean historical game/outcome data
- preserve enough metadata to reproduce past research runs

### Deliverables
- historical market snapshot schema
- historical game outcome schema
- ingestion validation checks
- raw + normalized storage paths
- dataset versioning rules

### Exit Criteria
- historical snapshots are queryable
- outcomes can be matched back to prior forecasts
- missing/invalid data rates are visible

## Stage 2 — Forecasting Baselines

### Objectives
- move from heuristic review scoring toward paper forecasting
- establish simple baseline models before adding complexity
- compare forecasts to market-implied probabilities

### Deliverables
- feature dataset builder
- baseline forecasting models
- probability output schema
- forecast storage and report generation
- deterministic train/eval runner

### Exit Criteria
- forecasts can be reproduced from saved data
- baseline model outputs are stable across reruns
- paper reports show implied probability vs forecast probability cleanly

## Stage 3 — Evaluation Discipline

### Objectives
- measure forecast quality rather than trusting intuition
- evaluate model quality on held-out historical data
- track whether changes improve or degrade performance

### Deliverables
- train/validation/test split rules
- Brier score reporting
- log loss reporting
- hit-rate summaries
- calibration summaries
- experiment tracking by model version/config

### Exit Criteria
- every meaningful model change has evaluation results
- model performance is compared against a baseline
- calibration errors are visible and reviewable

## Stage 4 — Research Workflow Quality

### Objectives
- improve the day-to-day analyst workflow
- make candidate review faster and less error-prone
- keep explanations tied to data

### Deliverables
- cleaner matchup/game clustering
- best-per-game review reports
- split reports by market family
- confidence/priority labeling
- forecast cards with missing-data flags
- post-event review templates

### Exit Criteria
- research outputs are readable without raw code inspection
- analysts can understand why a market surfaced
- unresolved data gaps are explicit, not hidden

## Stage 5 — Risk & Governance for Paper Mode

### Objectives
- ensure the system stays disciplined while improving
- avoid accidental drift beyond the defined scope
- maintain strong auditability

### Deliverables
- explicit paper-only guardrails in code and docs
- no execution endpoints in research workflows
- rule-violation logging
- config snapshot logging
- documented change-control process

### Exit Criteria
- every research run is auditable
- changes to logic/config can be traced
- paper-only restrictions remain enforced

## Stage 6 — Operational Stability

### Objectives
- make the system dependable enough for repeated daily use
- reduce friction in rerunning ingestion, reports, and evaluations

### Deliverables
- consistent local environment setup
- CLI workflows for ingest/report/eval
- test coverage for core paths
- artifact cleanup rules
- reproducible directory conventions for inputs and outputs

### Exit Criteria
- routine runs succeed without manual repair
- outputs are generated consistently
- failures are easier to diagnose than before

## Stage 7 — Continuous Learning Loop

### Objectives
- turn forecasts and post-game results into better future research
- build feedback loops without overfitting to anecdotes

### Deliverables
- post-settlement result capture
- forecast-vs-outcome comparisons
- recurring review summaries
- model drift checks
- backlog of research questions based on observed weaknesses

### Exit Criteria
- lessons from prior runs are recorded
- repeated mistakes become visible
- model changes are grounded in evidence, not impulse

## Recommended Immediate Priorities

1. historical data schemas and storage
2. train/eval scaffold with baseline metrics
3. cleaner implied-probability handling
4. richer forecast reporting
5. stronger automated tests around forecasting and reporting

## Guiding Principle

The goal is not to appear sophisticated.
The goal is to become **more correct, more measurable, and more disciplined** inside a paper-only system.
