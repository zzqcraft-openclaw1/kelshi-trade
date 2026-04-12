from __future__ import annotations

from kelshi_trade.forecasting.models.base import Forecaster
from kelshi_trade.forecasting.schemas import FeatureRow, ForecastOutput


class BaselinePaperForecaster(Forecaster):
    def fit(self, rows: list[FeatureRow]) -> None:
        return None

    def predict(self, row: FeatureRow) -> ForecastOutput:
        implied = row.market_implied_probability_pct
        if implied is None:
            return ForecastOutput(
                market_id=row.market_id,
                matchup=row.matchup,
                market_type=row.market_type,
                predicted_probability_pct=None,
                baseline_probability_pct=None,
                market_implied_probability_pct=None,
                estimated_edge_pct=None,
                confidence="needs_data",
                rationale="no implied probability available; baseline forecast withheld",
            )

        predicted = implied
        confidence = "low" if row.spread_bps is None or row.spread_bps > 800 else "medium"
        return ForecastOutput(
            market_id=row.market_id,
            matchup=row.matchup,
            market_type=row.market_type,
            predicted_probability_pct=predicted,
            baseline_probability_pct=implied,
            market_implied_probability_pct=implied,
            estimated_edge_pct=0.0,
            confidence=confidence,
            rationale="baseline paper-only forecast anchored to current implied probability",
        )

    def describe(self) -> str:
        return "Baseline paper-only forecaster anchored to market-implied probability"
