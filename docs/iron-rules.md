# Iron Rules

These rules govern the `kelshi-trade` research and paper-trading system.

They are intended to be hard constraints, not soft suggestions.

> Main trading rule: 少做、做窄、做有验证优势的；没 edge 就空仓；先想怎么死，再想赚多少。

## 1. Paper Only

The system must remain paper-trading only.

Rules:
- no live order submission paths
- no real-money execution mode
- no production trading credentials used for execution
- if execution mode is not explicitly `paper`, the system should fail closed
- read-only authenticated market-data retrieval is allowed for research and paper-review workflows only
- no order, execution, or account-changing endpoints may be used
- no credential material may be printed, exported, or committed

## 2. Sports-Only Whitelist

The tradable whitelist currently contains one category only:
- `sports`

Rules:
- any non-sports market is automatically rejected
- rejection should happen at ingestion, signal, and simulation layers
- no manual exception unless whitelist policy is intentionally changed in config/docs/code

## 3. No Trade Without a Recorded Thesis

Every simulated trade decision should have a logged rationale.

Minimum log fields:
- market id
- category
- signal direction
- estimated edge
- confidence
- timestamp
- concise reason for taking or skipping the trade

## 4. Risk Caps Are Mandatory

Every simulated order must pass hard limits before execution.

Required limits include:
- max position size per market
- max concurrent exposure
- max daily loss threshold
- max concentration in correlated events
- no order that breaks whitelist constraints

## 5. No Martingale / No Doubling Down by Emotion

The system must not increase size simply because prior paper trades lost.

Rules:
- no revenge trading
- no uncontrolled averaging down
- no size escalation without a predefined sizing rule backed by evidence

## 6. Skip Bad Markets

Some markets should be skipped even if they are sports markets.

Skip conditions include:
- poor liquidity
- stale quotes
- ambiguous settlement rules
- spreads too wide for the expected edge
- event too close to resolution for reliable entry/exit assumptions

## 7. No Silent Overrides

Important changes must be explicit.

Rules:
- whitelist changes must be documented
- strategy changes must be documented
- risk-limit changes must be documented
- config changes affecting decisions must be logged

## 8. Audit Everything

The system should log enough detail to reconstruct a decision later.

At minimum log:
- market ingestion decisions
- allowed vs blocked markets
- signals produced
- blocked signals
- simulated orders and fills
- position updates
- rule violations
- config changes relevant to a run

## 9. Fail Closed on Uncertainty

If key assumptions are missing, the system should do less, not more.

Examples:
- missing market category -> reject
- missing settlement interpretation -> reject
- missing risk config -> reject
- unclear signal rationale -> reject

## 10. Review Before Expansion

Before broadening beyond sports-only paper trading:
- review performance evidence
- review rule violations
- review model drift
- update docs/config/code together
- require an explicit decision before changing whitelist scope
