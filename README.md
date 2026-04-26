# kelshi-trade

Python research and paper-trading scaffold for event-market strategy development.

## Scope

This repository is set up for:
- market data collection
- strategy research
- backtesting
- paper trading
- risk controls
- logging and analysis

It is intentionally scaffolded with paper/simulated execution paths only.

## Layout

- `src/kelshi_trade/` — application package
- `tests/` — test suite
- `config/` — local config files/examples
- `src/kelshi_trade/models/` — typed domain entities
- `src/kelshi_trade/data/` — mock data + sqlite persistence
- `src/kelshi_trade/paper_trader/` — simulated execution
- `src/kelshi_trade/risk/` — paper-only guardrails

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
kelshi-trade status
kelshi-trade capture-quotes
kelshi-trade run-strategy
kelshi-trade show-portfolio
kelshi-trade capture-nba-pregame-baseline
```

## NBA pregame baseline capture

Capture a research-only snapshot of NBA game-winner odds near T-30m before tip:

```bash
kelshi-trade capture-nba-pregame-baseline --target-minutes-before-tip 30 --window-minutes 15
```

Artifacts land in the existing run structure under `reports/runs/<run_id>/nba_paper_review/` and `var/runs/<run_id>/`.

Key outputs:

- `nba_pregame_game_odds.json`
- `nba_pregame_game_odds.csv`
- `nba_pregame_game_odds_note.md`

The markdown note file is meant to be linked or pasted into daily notes and post-game review.

## MVP roadmap

1. Typed models for markets, quotes, signals, orders, fills, positions
2. Mock/read-only data layer with sqlite persistence
3. Paper execution engine with stored portfolio state
4. CLI commands for quote capture, strategy step, and portfolio inspection
5. Risk checks with market allowlist and paper-only enforcement
