from kelshi_trade.forecasting.features import build_feature_row
from kelshi_trade.forecasting.pipeline import run_forecast_pipeline
from kelshi_trade.models import LiveNBAMarket


def make_market(*, market_type: str = "game", yes_bid: float | None = 0.45, yes_ask: float | None = 0.48, no_bid: float | None = 0.51, no_ask: float | None = 0.55, liquidity: float = 10.0, volume: float = 12.0) -> LiveNBAMarket:
    return LiveNBAMarket(
        market_id="KXNBAGAME-TEST-LAL",
        event_ticker="KXNBAGAME-26APR12UTALAL",
        title="demo",
        matchup="Utah Jazz @ Los Angeles Lakers",
        start_time_utc="2026-04-13T04:00:00Z",
        market_type=market_type,
        yes_bid=yes_bid,
        yes_ask=yes_ask,
        no_bid=no_bid,
        no_ask=no_ask,
        liquidity=liquidity,
        volume=volume,
        status="active",
        is_bundle=False,
        raw={},
    )


def test_build_feature_row_sets_implied_probability_for_game_market() -> None:
    row = build_feature_row(make_market())
    assert row.market_implied_probability_pct == 48.0
    assert row.yes_bid_pct == 45.0
    assert row.yes_ask_pct == 48.0


def test_build_feature_row_withholds_implied_probability_for_non_game_market() -> None:
    row = build_feature_row(make_market(market_type="spread"))
    assert row.market_implied_probability_pct is None
    assert "market_implied_probability_pct" in row.missing_fields


def test_run_forecast_pipeline_returns_adjusted_game_output() -> None:
    outputs = run_forecast_pipeline([make_market()])
    assert len(outputs) == 1
    assert outputs[0].market_id == "KXNBAGAME-TEST-LAL"
    assert outputs[0].market_type == "game"
    assert outputs[0].baseline_probability_pct == 48.0
    assert outputs[0].predicted_probability_pct == 47.48
    assert outputs[0].estimated_edge_pct == -0.52
    assert "quote-mid adjustment -0.52 pts" in outputs[0].rationale


def test_run_forecast_pipeline_withholds_non_game_markets() -> None:
    outputs = run_forecast_pipeline([make_market(market_type="total")])
    assert len(outputs) == 1
    assert outputs[0].predicted_probability_pct is None
    assert outputs[0].confidence == "needs_data"
    assert "withholds non-game NBA markets" in outputs[0].rationale


def test_run_forecast_pipeline_fails_soft_when_quote_inputs_are_incomplete() -> None:
    outputs = run_forecast_pipeline([make_market(yes_bid=None, yes_ask=0.48, no_bid=0.51, no_ask=0.55)])
    assert len(outputs) == 1
    assert outputs[0].predicted_probability_pct == 48.0
    assert outputs[0].estimated_edge_pct == 0.0
    assert outputs[0].confidence == "low"
    assert "no complete game quote inputs for heuristic adjustment" in outputs[0].rationale
