import json
from pathlib import Path

from kelshi_trade.config import Settings
from kelshi_trade.workflow import doctor_ok, format_run_id, run_doctor, run_nba_paper_review


RAW_SNAPSHOT = {
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


def make_settings(tmp_path: Path, *, paper_only: bool = True, snapshot_exists: bool = True) -> Settings:
    raw_snapshot = tmp_path / "var" / "kalshi_raw_markets.json"
    raw_snapshot.parent.mkdir(parents=True, exist_ok=True)
    if snapshot_exists:
        raw_snapshot.write_text(json.dumps(RAW_SNAPSHOT), encoding="utf-8")
    return Settings(
        paper_only=paper_only,
        db_path=str(tmp_path / "var" / "kelshi_trade.db"),
        reports_path=str(tmp_path / "reports"),
        var_path=str(tmp_path / "var"),
        raw_snapshot_path=str(raw_snapshot),
    )


def test_format_run_id_is_timestamp_like() -> None:
    assert format_run_id().__contains__("T")
    assert format_run_id().endswith("Z")


def test_doctor_passes_with_existing_snapshot(tmp_path) -> None:
    settings = make_settings(tmp_path)
    checks = run_doctor(settings)
    assert doctor_ok(checks) is True
    assert any(check.name == "market_snapshot_source" and check.ok for check in checks)


def test_doctor_fails_when_paper_only_disabled(tmp_path) -> None:
    settings = make_settings(tmp_path, paper_only=False)
    checks = run_doctor(settings)
    assert doctor_ok(checks) is False
    assert any(check.name == "paper_only" and not check.ok for check in checks)


def test_run_nba_paper_review_creates_manifest_and_reports(tmp_path) -> None:
    settings = make_settings(tmp_path)

    artifacts = run_nba_paper_review(settings, top=5, include_forecast=True)

    manifest = json.loads(Path(artifacts.manifest_path).read_text(encoding="utf-8"))
    assert manifest["run_id"] == artifacts.run_id
    assert manifest["paper_only"] is True
    assert manifest["counts"]["nba_markets_detected"] == 2
    assert manifest["counts"]["review_candidates_exported"] == 2
    assert Path(artifacts.raw_snapshot_path).exists()
    assert Path(artifacts.forecast_path).exists()
    assert Path(artifacts.reports_dir, "nba_review_report.md").exists()
    assert Path(artifacts.reports_dir, "nba_review_report.csv").exists()
    assert Path(artifacts.reports_dir, "nba_review_best_per_game.md").exists()
    assert Path(artifacts.reports_dir, "nba_review_summary_by_game.md").exists()


def test_run_nba_paper_review_requires_paper_only(tmp_path) -> None:
    settings = make_settings(tmp_path, paper_only=False)
    try:
        run_nba_paper_review(settings)
    except ValueError as exc:
        assert "paper-only guardrail failed" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected paper-only failure")
