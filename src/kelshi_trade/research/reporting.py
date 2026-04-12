from __future__ import annotations

import csv
from pathlib import Path

from kelshi_trade.research.nba_markets import CandidateReview, render_top_candidates_markdown


def export_review_report(candidates: list[CandidateReview], output_dir: str) -> tuple[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    markdown_path = out / "nba_review_report.md"
    csv_path = out / "nba_review_report.csv"

    markdown_path.write_text(render_top_candidates_markdown(candidates), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["market_id", "matchup", "description", "start_time_utc", "market_type", "score", "priority", "rationale"],
        )
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(
                {
                    "market_id": candidate.market_id,
                    "matchup": candidate.matchup,
                    "description": candidate.description,
                    "start_time_utc": candidate.start_time_utc,
                    "market_type": candidate.market_type,
                    "score": candidate.score,
                    "priority": candidate.priority,
                    "rationale": candidate.rationale,
                }
            )

    return str(markdown_path), str(csv_path)


def export_split_review_reports(split_candidates: dict[str, list[CandidateReview]], output_dir: str) -> list[str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for market_type, candidates in split_candidates.items():
        safe_name = market_type.replace('/', '_')
        path = out / f"nba_review_{safe_name}.md"
        path.write_text(render_top_candidates_markdown(candidates), encoding="utf-8")
        written.append(str(path))
    return written


def export_best_per_game_report(candidates: list[CandidateReview], output_dir: str) -> str:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "nba_review_best_per_game.md"
    path.write_text(render_top_candidates_markdown(candidates), encoding="utf-8")
    return str(path)


def export_summary_by_game(summary: dict[str, dict[str, CandidateReview]], output_dir: str) -> str:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "nba_review_summary_by_game.md"
    lines = ["# NBA Review Summary by Game", "", "Research-only summary. Not a live trading recommendation.", ""]
    for matchup, families in summary.items():
        lines.append(f"## {matchup}")
        for family, candidate in families.items():
            lines.append(f"- {family}: {candidate.description or candidate.market_id} | score={candidate.score} | priority={candidate.priority}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
