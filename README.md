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
```

## MVP roadmap

1. Typed models for markets, quotes, signals, orders, fills, positions
2. Mock/read-only data layer with sqlite persistence
3. Paper execution engine with stored portfolio state
4. CLI commands for quote capture, strategy step, and portfolio inspection
5. Risk checks with market allowlist and paper-only enforcement
