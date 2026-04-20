# PLAN.md

## NBA Pregame Win Probability Roadmap

### Goal

Build a training and evaluation scaffold for predicting **pregame NBA home-team win probability** using **team-level aggregate features**.

### Current decisions

- Problem type: binary probabilistic classification
- Target: whether the home team wins
- Input level: team-level aggregates only
- Timing: pregame only, no in-game/live features
- Initial baseline: calibrated logistic regression
- Evaluation: time-ordered train/validation/test split

### What is already complete

- historical team-game fetch from `stats.nba.com`
- pregame dataset construction using prior-game history only
- rolling aggregate feature generation
- baseline training pipeline
- evaluation metrics and artifact saving
- first end-to-end baseline run for `2023-24`

### Training / evaluation scaffold scope

1. **Data ingestion**
   - fetch historical NBA team-game rows
   - store raw snapshots locally

2. **Dataset building**
   - transform raw team-game rows into pregame supervised examples
   - enforce no future leakage
   - derive one row per game from both teams' prior histories

3. **Feature engineering**
   - rolling team aggregates over prior games
   - rest-day features
   - back-to-back indicators
   - home/away context
   - opponent-relative delta features

4. **Training**
   - start with a calibrated logistic-regression baseline
   - keep training flow reproducible and easy to extend

5. **Evaluation**
   - use time-based splits
   - report accuracy, ROC AUC, log loss, and Brier score
   - save model and metrics artifacts

### Immediate next steps

1. add **multi-season training data**
2. add stronger team-level pregame features:
   - rolling win rate
   - home/away splits
   - net-rating-style proxies
   - opponent-strength-adjusted features
3. compare against stronger models:
   - XGBoost
   - LightGBM
4. add probability calibration diagnostics
5. build inference for future scheduled games

### Explicit non-goals for now

- player-level features
- injury/news features
- betting market integration
- live or in-game win probability
- deep learning unless simpler baselines plateau

### Success criteria for this phase

- reproducible fetch → build → train → evaluate pipeline
- probability outputs, not just class labels
- clear offline metrics and saved artifacts
- extensible structure for richer feature sets and models later
