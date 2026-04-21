from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class FeatureRow:
    market_id: str
    matchup: str
    market_type: str
    snapshot_time: datetime = field(default_factory=utc_now)
    source: str = "paper_only"
    model_version: str = "baseline-v0"
    market_implied_probability_pct: float | None = None
    liquidity: float | None = None
    volume: float | None = None
    spread_bps: float | None = None
    yes_bid_pct: float | None = None
    yes_ask_pct: float | None = None
    no_bid_pct: float | None = None
    no_ask_pct: float | None = None
    recent_price_move_pct: float | None = None
    rest_edge_note: str | None = None
    injury_note: str | None = None
    missing_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ForecastOutput:
    market_id: str
    matchup: str
    market_type: str
    forecast_time: datetime = field(default_factory=utc_now)
    model_name: str = "baseline-paper-forecaster"
    model_version: str = "baseline-v0"
    predicted_probability_pct: float | None = None
    baseline_probability_pct: float | None = None
    market_implied_probability_pct: float | None = None
    estimated_edge_pct: float | None = None
    confidence: str = "needs_data"
    rationale: str = "paper-only baseline forecast scaffold"
