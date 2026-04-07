from dataclasses import dataclass, field
from typing import Literal

Side = Literal["BUY", "SELL"]


@dataclass
class RiskLimits:
    max_position_size: int = 10
    max_daily_loss: float = 100.0
    paper_only: bool = True
    market_allowlist: set[str] = field(default_factory=lambda: {"demo"})


def projected_position_size(current_size: int, order_size: int, side: Side) -> int:
    signed_size = order_size if side == "BUY" else -order_size
    return current_size + signed_size


def check_order_allowed(
    *,
    current_size: int,
    order_size: int,
    side: Side,
    limits: RiskLimits,
    market_id: str = "demo",
) -> bool:
    if limits.paper_only is not True:
        return False
    if market_id not in limits.market_allowlist:
        return False
    if order_size <= 0:
        return False
    return abs(projected_position_size(current_size, order_size, side)) <= limits.max_position_size
