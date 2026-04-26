from pathlib import Path

from kelshi_trade.models import PregameOddsSnapshot
from kelshi_trade.research.nba_markets import CandidateReview
from kelshi_trade.research.reporting import export_pregame_odds_snapshots, export_review_report


def test_export_review_report_writes_files(tmp_path) -> None:
    candidates = [
        CandidateReview(
            market_id="m1",
            matchup="A @ B",
            start_time_utc="2026-04-12T23:00:00Z",
            market_type="spread",
            score=12.3,
            rationale="demo",
        )
    ]
    md_path, csv_path = export_review_report(candidates, str(tmp_path))
    assert Path(md_path).exists()
    assert Path(csv_path).exists()


def test_export_pregame_odds_snapshots_writes_json_csv_and_note(tmp_path) -> None:
    snapshots = [
        PregameOddsSnapshot(
            capture_timestamp_utc="2026-04-13T03:30:00Z",
            minutes_before_start=30,
            market_id="KXNBAGAME-26APR12UTALAL-LAL",
            event_ticker="KXNBAGAME-26APR12UTALAL",
            matchup="Utah Jazz @ Los Angeles Lakers",
            market_type="game",
            start_time_utc="2026-04-13T04:00:00Z",
            implied_probability_pct=48.0,
            yes_bid=0.45,
            yes_ask=0.48,
            no_bid=0.51,
            no_ask=0.55,
            liquidity=10.0,
            volume=12.0,
        )
    ]

    json_path, csv_path, note_path = export_pregame_odds_snapshots(snapshots, str(tmp_path))

    assert Path(json_path).exists()
    assert Path(csv_path).exists()
    note_text = Path(note_path).read_text(encoding="utf-8")
    assert "Utah Jazz @ Los Angeles Lakers" in note_text
    assert "Implied win probability: 48.0%" in note_text
