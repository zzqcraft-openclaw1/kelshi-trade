# NBA Win Probability Scaffolding Plan

## Objective

Build safe, reproducible training/evaluation scaffolding for pregame NBA win probability prediction using team-level aggregate features.

## Scope

- Pregame predictions only
- Team-level aggregates only
- One row per game
- Target: `home_win`
- Output: calibrated win probability

## Guiding constraints

- No data leakage
- Time-ordered feature generation only
- Time-based train/test splitting only
- Start with a simple probabilistic baseline before more complex models

## Milestones

### 1. Canonical data contract
Define the exact schemas for:
- `schedule`
- `team_games`

Deliverables:
- `src/ingest/contracts.py`

Acceptance criteria:
- required fields are explicit
- dtypes are documented
- row-granularity is unambiguous

### 2. Normalization layer
Convert raw historical NBA inputs into canonical tables.

Deliverables:
- `src/ingest/normalize.py`

Responsibilities:
- parse dates
- standardize team names
- derive wins/losses and team-level game stats
- derive possessions and four-factor stats when possible

Acceptance criteria:
- outputs match the canonical contract
- malformed input fails loudly
- duplicate/ambiguous rows are handled safely

### 3. Leakage-safe feature builder
Produce pregame features using prior information only.

Deliverables:
- refine `src/features/build_training_table.py`

Responsibilities:
- rolling form features
- season-to-date stats
- rest / back-to-back
- home/away join logic
- differential features

Acceptance criteria:
- current-game stats are excluded from that game's features
- first-game defaults are explicit
- output schema matches model expectations

### 4. Baseline training scaffold
Train a first probabilistic baseline.

Deliverables:
- refine `src/models/train_baseline.py`

Responsibilities:
- train logistic regression
- produce probabilities
- support config-driven feature selection

Acceptance criteria:
- training runs from canonical training table
- no ad hoc column editing required

### 5. Evaluation scaffold
Evaluate as a probability model, not just a classifier.

Deliverables:
- refine `src/evaluation/metrics.py`
- add `src/evaluation/report.py`

Metrics:
- log loss
- Brier score
- ROC-AUC
- accuracy
- calibration diagnostics

Acceptance criteria:
- evaluation is time-based
- report is readable and reproducible

### 6. End-to-end runnable pipeline
Wire the scaffold into a reproducible command path.

Deliverables:
- `scripts/build_training_table.py`
- improved `scripts/run_baseline.py`

Acceptance criteria:
- raw data -> normalized tables -> training table -> model -> evaluation
- outputs are saved predictably

### 7. Guardrails and tests
Protect against silent regressions.

Deliverables:
- additional tests under `tests/`

Priority tests:
- leakage checks
- schema checks
- chronology checks
- train/test split checks
- missing-value fallback behavior

## Recommended immediate next steps

1. implement `src/ingest/contracts.py`
2. implement `src/ingest/normalize.py`
3. add `scripts/build_training_table.py`

## Success definition

A good v1 scaffold is:
- reproducible
- leakage-safe
- time-split correctly
- probability-focused
- easy to extend

A bad v1 scaffold is:
- data-leaky
- hard to rerun
- overly complex too early
- optimized for appearance instead of reliability
