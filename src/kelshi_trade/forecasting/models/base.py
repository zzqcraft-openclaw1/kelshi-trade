from __future__ import annotations

from typing import Protocol

from kelshi_trade.forecasting.schemas import FeatureRow, ForecastOutput


class Forecaster(Protocol):
    def fit(self, rows: list[FeatureRow]) -> None: ...
    def predict(self, row: FeatureRow) -> ForecastOutput: ...
    def describe(self) -> str: ...
