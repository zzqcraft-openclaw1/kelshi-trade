# Game Forecast Guardrails Iteration

## Goal
Make the paper-only NBA game forecast output easier to review after the fact, especially when quote-driven signals are weak or market prices look abnormal.

## Scope
- Keep the existing baseline game-winner forecast scaffold.
- Do not add broader basketball modeling inputs yet.
- Stay research-only and paper-only.

## Changes in this iteration
1. Add an edge floor so very small quote-derived edges are surfaced as non-signals.
2. Add recommendation labels to every forecast output.
3. Add an extreme implied-probability guardrail for near-0% / near-100% game markets.
4. Make rationale text more explicit for post-game review.

## Intended behavior
- **pass**: no actionable edge after the floor is applied.
- **watch**: some edge exists, but confidence is still low.
- **research_only**: stronger paper-only candidate worth follow-up, still not a trade instruction.
- **withheld**: the forecast is intentionally suppressed because inputs are missing or the market looks too extreme.

## Narrow heuristics
- Treat absolute edges below 1.0 percentage point as noise for surfacing.
- Withhold game forecasts when the implied probability is at or below 3% or at or above 97%.
- Preserve the baseline/implied number for review, even when the recommendation is `withheld`.

## Why
The post-game review showed that tiny quote deviations and extreme market prices were too easy to over-read. This iteration makes the output more interpretable without pretending the model knows more than it does.
