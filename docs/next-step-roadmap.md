# Next-Step Roadmap for `kelshi-trade`

This roadmap focuses on restoring `kelshi-trade` into a disciplined, repeatable **paper-only NBA research and paper-trading workflow**.

It is intentionally staged so the project becomes usable first, then more sophisticated later.

---

## Phase 0 — Finish the Current NBA Game-Win Baseline

### Goal
Complete the current forecasting work so the repo has a clean, reviewable, game-only baseline for NBA winner markets.

### Features
- make the forecast CLI truly `game`-only
- ensure non-game NBA markets do not appear in the game forecast output
- add end-to-end tests for CLI + pipeline behavior
- get reviewer approval on scope, tests, and edge cases
- ensure work lands in the correct/original repo path

### Definition of Done
- the game forecast command emits only game-winner markets
- non-game markets are withheld safely and are not mixed into game forecast output
- tests pass
- reviewer signs off

---

## Phase 1 — Daily Research Workflow

### Goal
Make the repo usable as a daily tool instead of just a collection of components.

### Features
- add a `doctor` / preflight check command
- add a one-shot `run-nba-paper-review` command
- create timestamped run folders
- write a run manifest JSON per run
- standardize artifact layout under `reports/` and `var/`

### Suggested Command Flow
1. run environment and setup checks
2. fetch read-only Kalshi market snapshot
3. extract NBA-linked markets
4. filter to eligible review candidates
5. generate review reports
6. optionally run game-winner forecasts
7. save outputs under a timestamped run id

### Definition of Done
- one command can produce a reproducible daily paper-review run
- failures are surfaced early and clearly
- artifacts are easy to locate and compare across runs

---

## Phase 2 — Forecast Persistence and Audit Trail

### Goal
Preserve enough structured output to compare runs and reconstruct decisions later.

### Features
- persist forecast outputs in sqlite
- persist run metadata and config snapshots
- add a decision log table
- add a rule-violation log table
- link output artifacts to run ids

### Definition of Done
- every forecast run is reproducible and auditable
- changes in config or logic can be traced to outputs

---

## Phase 3 — NBA Game-Win Model v2

### Goal
Move beyond quote-only heuristics into a more meaningful basketball-aware baseline.

### Features
- team-strength baseline
- home-court adjustment
- recent-form features
- rest / back-to-back features
- injury-status placeholders or feed integration
- confidence scoring based on data completeness

### Guardrail
Keep the model simple, explicit, and auditable. Avoid pretending to have precision that the data does not support.

### Definition of Done
- the model uses real basketball context, not just market structure
- missing-data cases fail soft and remain visible

---

## Phase 4 — Evaluation Discipline

### Goal
Measure whether the model is getting better instead of relying on intuition.

### Features
- settled outcome capture
- historical evaluation dataset
- Brier score reporting
- log loss reporting
- calibration summaries
- baseline vs new-model comparison

### Definition of Done
- every meaningful model change can be measured against a baseline
- evaluation outputs are reproducible and reviewable

---

## Phase 5 — Paper Decision Engine Integration

### Goal
Connect forecasts to disciplined paper decisions.

### Features
- translate forecast edge into candidate paper decisions
- require written thesis logging per simulated trade
- enforce exposure and risk caps by game/day
- skip low-liquidity, stale, or wide-spread markets
- persist simulated orders, fills, and position updates

### Definition of Done
- forecasts can drive a complete paper-decision workflow
- every simulated action is logged with rationale and guardrail checks

---

## Phase 6 — Reporting and Analyst UX

### Goal
Make outputs easier to review without digging through raw code or databases.

### Features
- best-per-game forecast cards
- top-edge summary report
- low-confidence / missing-data report
- post-game review report
- skipped-vs-taken paper trade summary

### Definition of Done
- daily review is readable and fast
- weak-data cases are obvious rather than hidden

---

## Recommended Priority Order

1. finish current game-only baseline cleanup
2. build the daily workflow command
3. add persistence and audit trail
4. add real basketball features
5. add evaluation tooling
6. integrate with the paper engine
7. improve analyst-facing reporting UX

---

## Immediate Next-Step Feature Bundle

### Bundle A — Finish Current Model Work
- filter forecast CLI to game markets only
- add CLI and pipeline tests
- send back for reviewer approval
- land work in the correct/original repo path

### Bundle B — Make It Operational
- implement `kelshi-trade doctor`
- implement `kelshi-trade run-nba-paper-review`
- add timestamped outputs and run manifests

### Why This Order
This sequence gives the project two things quickly:
- a correct, bounded NBA game-winner baseline
- a usable daily workflow to build on

---

## Guiding Principle

The goal is not to look sophisticated.
The goal is to become **correct, repeatable, auditable, and useful** inside a paper-only system.
