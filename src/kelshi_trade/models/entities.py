from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Side = Literal["BUY", "SELL"]
SignalAction = Literal["BUY", "SELL", "HOLD"]
OrderStatus = Literal["NEW", "FILLED", "REJECTED"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Market:
    market_id: str
    title: str
    status: str = "open"


@dataclass(slots=True)
class Quote:
    market_id: str
    bid: float
    ask: float
    last: float
    ts: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Signal:
    market_id: str
    action: SignalAction
    reason: str
    ts: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Order:
    order_id: str
    market_id: str
    side: Side
    size: int
    price: float
    status: OrderStatus = "NEW"
    ts: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Fill:
    fill_id: str
    order_id: str
    market_id: str
    side: Side
    size: int
    price: float
    ts: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Position:
    market_id: str
    size: int = 0
    avg_price: float = 0.0


@dataclass(slots=True)
class ResearchMarket:
    market_id: str
    reference_game_id: str
    title: str
    league: str
    category: str
    subcategory: str
    matchup: str
    start_time_utc: str
    market_type: str
    liquidity_score: float
    spread_bps: int
    validated: bool = False


@dataclass(slots=True)
class LiveNBAMarket:
    market_id: str
    event_ticker: str
    title: str
    matchup: str
    start_time_utc: str
    market_type: str
    yes_bid: float
    yes_ask: float
    no_bid: float
    no_ask: float
    liquidity: float
    volume: float
    status: str
    is_bundle: bool
    raw: dict


@dataclass(slots=True)
class PregameOddsSnapshot:
    capture_timestamp_utc: str
    minutes_before_start: int
    market_id: str
    event_ticker: str
    matchup: str
    market_type: str
    start_time_utc: str
    implied_probability_pct: float | None
    yes_bid: float | None
    yes_ask: float | None
    no_bid: float | None
    no_ask: float | None
    liquidity: float
    volume: float
