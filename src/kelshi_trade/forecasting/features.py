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
        yes_bid_pct=round(market.yes_bid * 100, 2) if market.yes_bid is not None else None,
        yes_ask_pct=round(market.yes_ask * 100, 2) if market.yes_ask is not None else None,
        no_bid_pct=round(market.no_bid * 100, 2) if market.no_bid is not None else None,
        no_ask_pct=round(market.no_ask * 100, 2) if market.no_ask is not None else None,
        missing_fields=missing,
    )
