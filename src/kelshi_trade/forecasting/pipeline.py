from __future__ import annotations

from kelshi_trade.forecasting.features import build_feature_row
from kelshi_trade.forecasting.models.baseline import BaselinePaperForecaster
from kelshi_trade.forecasting.schemas import ForecastOutput
from kelshi_trade.models import LiveNBAMarket


GAME_MARKET_TYPE = "game"


def select_game_markets(markets: list[LiveNBAMarket]) -> list[LiveNBAMarket]:
    return [market for market in markets if market.market_type == GAME_MARKET_TYPE]


def run_forecast_pipeline(markets: list[LiveNBAMarket]) -> list[ForecastOutput]:
    feature_rows = [build_feature_row(m) for m in markets]
    model = BaselinePaperForecaster()
    model.fit(feature_rows)
    return [model.predict(row) for row in feature_rows]
