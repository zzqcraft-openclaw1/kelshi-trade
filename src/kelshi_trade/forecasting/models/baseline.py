from __future__ import annotations

from kelshi_trade.forecasting.models.base import Forecaster
from kelshi_trade.forecasting.schemas import FeatureRow, ForecastOutput


class BaselinePaperForecaster(Forecaster):
    SUPPORTED_MARKET_TYPE = "game"
    EDGE_SURFACING_FLOOR_PCT = 1.0
    EXTREME_IMPLIED_LOW_PCT = 3.0
    EXTREME_IMPLIED_HIGH_PCT = 97.0

    def fit(self, rows: list[FeatureRow]) -> None:
        return None

    def predict(self, row: FeatureRow) -> ForecastOutput:
        if row.market_type != self.SUPPORTED_MARKET_TYPE:
            return ForecastOutput(
                market_id=row.market_id,
                matchup=row.matchup,
                market_type=row.market_type,
                predicted_probability_pct=None,
                baseline_probability_pct=row.market_implied_probability_pct,
                market_implied_probability_pct=row.market_implied_probability_pct,
                estimated_edge_pct=None,
                surfaced_edge_pct=None,
                confidence="needs_data",
                recommendation="withheld",
                rationale=(
                    "paper-only baseline withholds non-game NBA markets; "
                    "game-winner model only"
                ),
            )

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
                surfaced_edge_pct=None,
                confidence="needs_data",
                recommendation="withheld",
                rationale="no game-market implied probability available; baseline forecast withheld",
            )

        if self._is_extreme_implied_probability(implied):
            return ForecastOutput(
                market_id=row.market_id,
                matchup=row.matchup,
                market_type=row.market_type,
                predicted_probability_pct=None,
                baseline_probability_pct=implied,
                market_implied_probability_pct=implied,
                estimated_edge_pct=None,
                surfaced_edge_pct=None,
                confidence="guardrail",
                recommendation="withheld",
                rationale=(
                    "game-market implied probability hit extreme guardrail; "
                    "forecast withheld for review friendliness"
                ),
            )

        predicted = implied
        rationale_bits = ["paper-only game-winner baseline anchored to current implied probability"]

        quote_mid = self._quote_mid_probability_pct(row)
        if quote_mid is not None:
            blend_weight = self._blend_weight(row)
            adjustment = round((quote_mid - implied) * blend_weight, 2)
            predicted = self._clamp_probability_pct(implied + adjustment)
            rationale_bits.append(
                f"quote-mid adjustment {adjustment:+.2f} pts from implied {implied:.2f} toward {quote_mid:.2f}"
            )
        else:
            rationale_bits.append("no complete game quote inputs for heuristic adjustment")

        confidence = self._confidence(row, quote_mid)
        edge = round(predicted - implied, 2)
        surfaced_edge = self._surface_edge(edge)
        recommendation = self._recommendation(surfaced_edge, confidence)
        if surfaced_edge == 0.0 and edge != 0.0:
            rationale_bits.append(
                f"edge below {self.EDGE_SURFACING_FLOOR_PCT:.1f} pt surfacing floor; treat as noise for paper review"
            )

        return ForecastOutput(
            market_id=row.market_id,
            matchup=row.matchup,
            market_type=row.market_type,
            predicted_probability_pct=predicted,
            baseline_probability_pct=implied,
            market_implied_probability_pct=implied,
            estimated_edge_pct=edge,
            surfaced_edge_pct=surfaced_edge,
            confidence=confidence,
            recommendation=recommendation,
            rationale="; ".join(rationale_bits),
        )

    def describe(self) -> str:
        return (
            "Baseline paper-only forecaster for NBA game winners, anchored to implied "
            "probability with a small quote-mid heuristic adjustment"
        )

    def _quote_mid_probability_pct(self, row: FeatureRow) -> float | None:
        if row.yes_bid_pct is None or row.yes_ask_pct is None:
            return None
        return round((row.yes_bid_pct + row.yes_ask_pct) / 2, 2)

    def _blend_weight(self, row: FeatureRow) -> float:
        spread_bps = row.spread_bps if row.spread_bps is not None else 9999.0
        liquidity = row.liquidity or 0.0
        volume = row.volume or 0.0
        if spread_bps <= 300 and liquidity >= 20 and volume >= 20:
            return 0.5
        if spread_bps <= 600 and liquidity >= 10 and volume >= 10:
            return 0.35
        return 0.2

    def _confidence(self, row: FeatureRow, quote_mid: float | None) -> str:
        if quote_mid is None:
            return "low"
        spread_bps = row.spread_bps if row.spread_bps is not None else 9999.0
        liquidity = row.liquidity or 0.0
        volume = row.volume or 0.0
        if spread_bps <= 300 and liquidity >= 20 and volume >= 20:
            return "medium"
        return "low"

    def _surface_edge(self, edge: float) -> float:
        if abs(edge) < self.EDGE_SURFACING_FLOOR_PCT:
            return 0.0
        return edge

    def _recommendation(self, surfaced_edge: float, confidence: str) -> str:
        if surfaced_edge == 0.0:
            return "pass"
        if confidence == "medium":
            return "research_only"
        return "watch"

    def _is_extreme_implied_probability(self, implied: float) -> bool:
        return implied <= self.EXTREME_IMPLIED_LOW_PCT or implied >= self.EXTREME_IMPLIED_HIGH_PCT

    def _clamp_probability_pct(self, value: float) -> float:
        return round(max(1.0, min(99.0, value)), 2)
