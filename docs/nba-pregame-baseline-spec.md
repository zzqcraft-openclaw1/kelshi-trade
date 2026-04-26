# NBA Pregame Baseline Capture v1

## Goal

Capture a paper-only snapshot of Kalshi NBA game-winner odds roughly 30 minutes before tip so post-game review can compare:

- what the market implied before the game
- what our later tool/report said
- how far the market moved or where our view differed

## Scope

Focused v1 only:

- NBA game-winner markets only
- one-shot capture command, no scheduler baked into code
- store enough quote/context fields for later comparison
- save artifacts into the existing run structure
- emit a markdown note snippet that can be linked or pasted into daily notes

## Inputs

- existing raw Kalshi snapshot file, or
- fresh read-only Kalshi fetch using current credentials

## Selection rule

From extracted live NBA markets:

1. keep only active allowed NBA markets
2. keep only `market_type == game`
3. keep only markets whose start time is within the configured window around target tipoff lead time
   - default target: 30 minutes before tip
   - default window: +/- 15 minutes

## Stored fields

Per captured market:

- capture timestamp UTC
- minutes before start
- matchup
- market id
- event ticker
- market type
- start time UTC
- implied probability pct
- yes bid / yes ask
- no bid / no ask
- liquidity
- volume

## Artifacts

Within the run directory:

- `nba_pregame_game_odds.json` — machine-readable baseline snapshot
- `nba_pregame_game_odds.csv` — quick spreadsheet/review export
- `nba_pregame_game_odds_note.md` — daily-note/post-game-review friendly markdown
- `pregame_capture_manifest.json` — run metadata

## CLI

```bash
kelshi-trade capture-nba-pregame-baseline
```

Useful flags:

```bash
kelshi-trade capture-nba-pregame-baseline --target-minutes-before-tip 30 --window-minutes 15
```

## Non-goals

- no auto scheduler in repo code
- no live trading action
- no non-NBA or non-game market support in v1
- no attempt to infer closing line or intra-game movement yet

## Follow-up ideas

- stitch latest pregame baseline into the daily review workflow automatically
- add post-game join/reporting that compares baseline vs forecast output vs result
- support multiple snapshots per game if we later want T-60 / T-30 / T-5 tracking
