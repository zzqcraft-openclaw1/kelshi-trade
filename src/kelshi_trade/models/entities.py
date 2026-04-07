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
