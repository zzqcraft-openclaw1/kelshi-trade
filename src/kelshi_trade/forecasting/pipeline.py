from __future__ import annotations

from kelshi_trade.forecasting.features import build_feature_row
from kelshi_trade.forecasting.models.baseline import BaselinePaperForecaster
from kelshi_trade.forecasting.schemas import ForecastOutput
from kelshi_trade.models import LiveNBAMarket


def run_forecast_pipeline(markets: list[LiveNBAMarket]) -> list[ForecastOutput]:
    feature_rows = [build_feature_row(m) for m in markets]
    model = BaselinePaperForecaster()
    model.fit(feature_rows)
    return [model.predict(row) for row in feature_rows]
