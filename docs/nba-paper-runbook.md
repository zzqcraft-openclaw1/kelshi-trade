# NBA Paper Runbook

## Goal

Run a one-day, paper-only NBA market workflow for tomorrow's slate.

This is an MVP operating runbook for research and simulation only.

## Preconditions

Before starting the run:
- sports-only whitelist is active
- paper-only mode is active
- no live execution paths are enabled
- logging and sqlite paths are writable
- the working assumptions for the run are documented

## Allowed Scope

For this runbook, focus only on:
- NBA games scheduled for tomorrow
- sports-category markets only
- paper-trading and research actions only

Any market that is not clearly an NBA sports market should be skipped.

## Pre-Run Workflow

1. list tomorrow's NBA games
2. map each game to approved market ids
3. reject any market with ambiguous wording or unclear settlement
4. capture baseline quotes for each candidate market
5. fill out the paper-run template for each game
6. treat `reference_game_id` values as schedule-reference placeholders until a real market is validated
7. log any key assumptions such as injuries, rest, or lineup uncertainty

## Market Filters

A market is eligible only if all of the following are true:
- it is in the sports whitelist
- it clearly maps to an NBA game on tomorrow's slate
- settlement terms are understandable
- quotes are fresh enough for a decision
- liquidity/spread quality is acceptable for simulation

A market should be skipped if any of these checks fail.

## Prediction Step

For each eligible game/market:
- estimate fair probability or directional view
- compare to market-implied probability
- estimate edge
- subtract assumed slippage/fees
- assign confidence level
- record the rationale in writing

If the rationale is weak or the edge is unclear, skip the trade.

## Trade Filter

Only simulate an entry when:
- whitelist check passed
- market quality checks passed
- thesis is recorded
- expected net edge clears the threshold
- risk checks pass
- stake size is within the paper-trading risk rules

If there is no validated edge, stay flat.

## Logging Requirements

For every candidate market, record:
- matchup
- reference game id
- validated market id once known
- candidate market type
- quote snapshot
- model view
- implied probability
- estimated edge
- confidence
- simulated action or skip
- written rationale

## Monitoring and Closeout

During the run:
- snapshot updated quotes at defined intervals if needed
- do not silently override earlier assumptions
- record any thesis changes explicitly
- close or settle paper positions according to the simulation rules

After games finish:
- mark outcome
- compute simulated PnL
- note whether the thesis was right for the right reason
- document lessons for the next slate

## End-of-Run Review

At minimum summarize:
- number of games reviewed
- number of markets skipped
- number of simulated trades taken
- realized paper PnL
- biggest mistake
- biggest correct skip
- any rule violations
- any model changes proposed for future research
