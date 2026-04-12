from kelshi_trade.forecasting.features import build_feature_row
from kelshi_trade.forecasting.pipeline import run_forecast_pipeline
from kelshi_trade.models import LiveNBAMarket


def make_market() -> LiveNBAMarket:
    return LiveNBAMarket(
        market_id="KXNBAGAME-TEST-LAL",
        event_ticker="KXNBAGAME-26APR12UTALAL",
        title="demo",
        matchup="Utah Jazz @ Los Angeles Lakers",
        start_time_utc="2026-04-13T04:00:00Z",
        market_type="game",
        yes_bid=0.45,
        yes_ask=0.48,
        no_bid=0.51,
        no_ask=0.55,
        liquidity=10.0,
        volume=12.0,
        status="active",
        is_bundle=False,
        raw={},
    )


def test_build_feature_row_sets_implied_probability() -> None:
    row = build_feature_row(make_market())
    assert row.market_implied_probability_pct is not None


def test_run_forecast_pipeline_returns_output() -> None:
    outputs = run_forecast_pipeline([make_market()])
    assert len(outputs) == 1
    assert outputs[0].market_id == "KXNBAGAME-TEST-LAL"
