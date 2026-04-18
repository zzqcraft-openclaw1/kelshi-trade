# NBA Pregame Win Probability

Scaffold for training a team-level pregame NBA win probability model.

## Scope

- Predict home-team win probability before tip-off
- Use team-level aggregate features only
- Start with historical regular season games
- No live/in-game features yet

## Planned feature families

- Season-to-date team stats
- Rolling form over last N games
- Home/away splits
- Rest days
- Back-to-back flag
- Head-to-head summary
- Opponent-relative feature deltas

## Project layout

- `src/nba_win_prob/config.py` — paths and defaults
- `src/nba_win_prob/data/fetch.py` — raw game fetchers
- `src/nba_win_prob/data/build_dataset.py` — feature construction
- `src/nba_win_prob/models/baseline.py` — baseline sklearn model
- `src/nba_win_prob/train.py` — train/eval entrypoint
- `data/raw/` — fetched source data
- `data/processed/` — model-ready datasets
- `artifacts/` — trained models and reports

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.nba_win_prob.data.fetch --season 2023-24
python -m src.nba_win_prob.data.build_dataset --season 2023-24
python -m src.nba_win_prob.train --season 2023-24
```

## Notes

This scaffold starts with a calibrated logistic-regression baseline because:

- it is fast to train
- it gives interpretable coefficients
- probability quality is often decent with good features
- it is a strong baseline before trying tree models or neural nets

Next upgrades after the baseline works:

1. add multiple seasons
2. add richer schedule context
3. compare XGBoost/LightGBM
4. add probability calibration plots
5. package inference for future schedules
