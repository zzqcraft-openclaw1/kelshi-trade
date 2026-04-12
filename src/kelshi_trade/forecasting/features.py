from __future__ import annotations

from kelshi_trade.forecasting.schemas import FeatureRow
from kelshi_trade.models import LiveNBAMarket
from kelshi_trade.research.nba_markets import implied_probability_pct


def build_feature_row(market: LiveNBAMarket) -> FeatureRow:
    missing: list[str] = []
    implied = implied_probability_pct(market)
    if implied is None:
        missing.append("market_implied_probability_pct")

    spread_bps = None
    if market.yes_ask and market.no_bid:
        spread_bps = abs((market.yes_ask + market.no_bid) - 1.0) * 10000
    else:
        missing.append("spread_bps")

    return FeatureRow(
        market_id=market.market_id,
        matchup=market.matchup,
        market_type=market.market_type,
        market_implied_probability_pct=implied,
        liquidity=market.liquidity,
        volume=market.volume,
        spread_bps=spread_bps,
        missing_fields=missing,
    )
