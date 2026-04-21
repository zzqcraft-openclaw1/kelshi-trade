from typer.testing import CliRunner

from kelshi_trade.cli import app


runner = CliRunner()


MINIMAL_RAW_SNAPSHOT = {
    "markets": [
        {
            "ticker": "bundle-1",
            "status": "active",
            "expected_expiration_time": "2026-04-13T04:00:00Z",
            "yes_bid_dollars": 0.45,
            "yes_ask_dollars": 0.48,
            "no_bid_dollars": 0.51,
            "no_ask_dollars": 0.55,
            "liquidity_dollars": 10.0,
            "volume_fp": 12.0,
            "custom_strike": {
                "Associated Events": "KXNBAGAME-26APR12UTALAL,KXNBATOTAL-26APR12UTALAL",
                "Associated Markets": "KXNBAGAME-26APR12UTALAL-LAL,KXNBATOTAL-26APR12UTALAL-228",
            },
        }
    ]
}


def test_report_kalshi_nba_forecast_emits_only_game_markets(tmp_path) -> None:
    raw_json = tmp_path / "kalshi_raw_markets.json"
    raw_json.write_text(__import__("json").dumps(MINIMAL_RAW_SNAPSHOT), encoding="utf-8")

    result = runner.invoke(app, ["report-kalshi-nba-forecast", "--raw-json", str(raw_json)])

    assert result.exit_code == 0
    assert "KXNBAGAME-26APR12UTALAL-LAL | game |" in result.stdout
    assert "KXNBATOTAL-26APR12UTALAL-228" not in result.stdout
    assert "| total |" not in result.stdout


def test_report_kalshi_nba_forecast_handles_missing_game_implied_probability_cleanly(tmp_path) -> None:
    raw_json = tmp_path / "kalshi_raw_markets.json"
    payload = {
        "markets": [
            {
                "ticker": "bundle-2",
                "status": "active",
                "expected_expiration_time": "2026-04-13T04:00:00Z",
                "yes_bid_dollars": 0.0,
                "yes_ask_dollars": 0.0,
                "no_bid_dollars": 0.51,
                "no_ask_dollars": 0.55,
                "liquidity_dollars": 10.0,
                "volume_fp": 12.0,
                "custom_strike": {
                    "Associated Events": "KXNBAGAME-26APR12UTALAL",
                    "Associated Markets": "KXNBAGAME-26APR12UTALAL-LAL",
                },
            }
        ]
    }
    raw_json.write_text(__import__("json").dumps(payload), encoding="utf-8")

    result = runner.invoke(app, ["report-kalshi-nba-forecast", "--raw-json", str(raw_json)])

    assert result.exit_code == 0
    assert "KXNBAGAME-26APR12UTALAL-LAL | game | predicted=needs_data | implied=n/a | confidence=needs_data" in result.stdout
    assert "baseline forecast withheld" in result.stdout
