import json
from pathlib import Path

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
    raw_json.write_text(json.dumps(MINIMAL_RAW_SNAPSHOT), encoding="utf-8")

    result = runner.invoke(app, ["report-kalshi-nba-forecast", "--raw-json", str(raw_json)])

    assert result.exit_code == 0
    assert "KXNBAGAME-26APR12UTALAL-LAL | game |" in result.stdout
    assert "recommendation=pass" in result.stdout
    assert "surfaced_edge=0.0" in result.stdout
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
    raw_json.write_text(json.dumps(payload), encoding="utf-8")

    result = runner.invoke(app, ["report-kalshi-nba-forecast", "--raw-json", str(raw_json)])

    assert result.exit_code == 0
    assert "KXNBAGAME-26APR12UTALAL-LAL | game | predicted=needs_data | implied=n/a | edge=n/a | surfaced_edge=n/a | recommendation=withheld | confidence=needs_data" in result.stdout
    assert "baseline forecast withheld" in result.stdout


def test_report_kalshi_nba_forecast_withholds_extreme_market_from_cli(tmp_path) -> None:
    raw_json = tmp_path / "kalshi_raw_markets.json"
    payload = {
        "markets": [
            {
                "ticker": "bundle-3",
                "status": "active",
                "expected_expiration_time": "2026-04-13T04:00:00Z",
                "yes_bid_dollars": 0.98,
                "yes_ask_dollars": 0.98,
                "no_bid_dollars": 0.01,
                "no_ask_dollars": 0.02,
                "liquidity_dollars": 50.0,
                "volume_fp": 50.0,
                "custom_strike": {
                    "Associated Events": "KXNBAGAME-26APR12UTALAL",
                    "Associated Markets": "KXNBAGAME-26APR12UTALAL-LAL",
                },
            }
        ]
    }
    raw_json.write_text(json.dumps(payload), encoding="utf-8")

    result = runner.invoke(app, ["report-kalshi-nba-forecast", "--raw-json", str(raw_json)])

    assert result.exit_code == 0
    assert "recommendation=withheld | confidence=guardrail" in result.stdout
    assert "extreme guardrail" in result.stdout


def test_doctor_command_passes_with_local_snapshot(tmp_path, monkeypatch) -> None:
    raw_json = tmp_path / "var" / "kalshi_raw_markets.json"
    raw_json.parent.mkdir(parents=True, exist_ok=True)
    raw_json.write_text(json.dumps(MINIMAL_RAW_SNAPSHOT), encoding="utf-8")
    monkeypatch.setenv("KELSHI_PAPER_ONLY", "true")
    monkeypatch.setenv("KELSHI_DB_PATH", str(tmp_path / "var" / "kelshi_trade.db"))
    monkeypatch.setenv("KELSHI_REPORTS_PATH", str(tmp_path / "reports"))
    monkeypatch.setenv("KELSHI_VAR_PATH", str(tmp_path / "var"))
    monkeypatch.setenv("KELSHI_RAW_SNAPSHOT_PATH", str(raw_json))

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "doctor passed" in result.stdout
    assert "[OK] market_snapshot_source" in result.stdout


def test_run_nba_paper_review_command_writes_run_artifacts(tmp_path, monkeypatch) -> None:
    raw_json = tmp_path / "var" / "kalshi_raw_markets.json"
    raw_json.parent.mkdir(parents=True, exist_ok=True)
    raw_json.write_text(json.dumps(MINIMAL_RAW_SNAPSHOT), encoding="utf-8")
    monkeypatch.setenv("KELSHI_PAPER_ONLY", "true")
    monkeypatch.setenv("KELSHI_DB_PATH", str(tmp_path / "var" / "kelshi_trade.db"))
    monkeypatch.setenv("KELSHI_REPORTS_PATH", str(tmp_path / "reports"))
    monkeypatch.setenv("KELSHI_VAR_PATH", str(tmp_path / "var"))
    monkeypatch.setenv("KELSHI_RAW_SNAPSHOT_PATH", str(raw_json))

    result = runner.invoke(app, ["run-nba-paper-review", "--top", "5"])

    assert result.exit_code == 0
    assert "paper-only research run complete" in result.stdout
    manifest_line = next(line for line in result.stdout.splitlines() if line.startswith("manifest="))
    manifest_path = Path(manifest_line.split("=", 1)[1])
    assert manifest_path.exists()
