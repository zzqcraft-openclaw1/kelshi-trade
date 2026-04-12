from pathlib import Path

from kelshi_trade.research.nba_markets import CandidateReview
from kelshi_trade.research.reporting import export_review_report


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
