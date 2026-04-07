from dataclasses import dataclass
from typing import Protocol


@dataclass
class MarketSnapshot:
    market_id: str
    bid: float
    ask: float
    last: float


class MarketClient(Protocol):
    def get_market(self, market_id: str) -> MarketSnapshot: ...
