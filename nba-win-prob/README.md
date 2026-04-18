# NBA Win Probability

Pregame NBA game win probability modeling using team-level aggregate features.

## Objective

Predict `P(home_team_wins)` before tip-off using only information available before the game starts.

## Scope for v1

- Pregame predictions only
- Team-level aggregates only
- Leakage-safe feature generation
- Logistic regression baseline first
- Time-based evaluation

## Planned pipeline

1. Ingest historical NBA schedules and team game stats
2. Build rolling/team-to-date aggregates using only prior games
3. Produce one training row per game
4. Train a baseline probabilistic classifier
5. Evaluate calibration and probabilistic accuracy

## Repository layout

```text
nba-win-prob/
  README.md
  configs/
  data/
    raw/
    processed/
  src/
    ingest/
    features/
    models/
    evaluation/
  scripts/
  tests/
```

## Important constraint

Avoid data leakage. No feature for a game may use that game's outcome or stats.
