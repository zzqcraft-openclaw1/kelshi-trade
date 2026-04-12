from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from kelshi_trade.models import ResearchMarket


@dataclass(slots=True)
class CandidateReview:
    market_id: str
    matchup: str
    start_time_utc: str
    market_type: str
    score: float
    rationale: str


class MockNBAMarketSource:
    def __init__(self, slate_csv: str) -> None:
        self.slate_csv = slate_csv

    def load_markets(self) -> list[ResearchMarket]:
        rows: list[ResearchMarket] = []
        with Path(self.slate_csv).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                matchup = f"{row['away_team']} @ {row['home_team']}"
                base_id = row["reference_game_id"]
                rows.extend(
                    [
                        ResearchMarket(
                            market_id=f"{base_id}-spread",
                            reference_game_id=base_id,
                            title=f"{matchup} spread review candidate",
                            league=row["league"],
                            category="sports",
                            subcategory="nba",
                            matchup=matchup,
                            start_time_utc=row["start_time_utc"],
                            market_type="spread",
                            liquidity_score=0.72,
                            spread_bps=80,
                            validated=False,
                        ),
                        ResearchMarket(
                            market_id=f"{base_id}-total",
                            reference_game_id=base_id,
                            title=f"{matchup} total review candidate",
                            league=row["league"],
                            category="sports",
                            subcategory="nba",
                            matchup=matchup,
                            start_time_utc=row["start_time_utc"],
                            market_type="total",
                            liquidity_score=0.68,
                            spread_bps=95,
                            validated=False,
                        ),
                    ]
                )
        return rows


def filter_nba_markets(markets: list[ResearchMarket]) -> tuple[list[ResearchMarket], list[str]]:
    allowed: list[ResearchMarket] = []
    blocked: list[str] = []
    for market in markets:
        if market.category != "sports":
            blocked.append(f"{market.market_id}: blocked non-sports category")
            continue
        if market.subcategory != "nba":
            blocked.append(f"{market.market_id}: blocked non-NBA subcategory")
            continue
        if market.market_type not in {"spread", "total", "moneyline"}:
            blocked.append(f"{market.market_id}: blocked unsupported market type")
            continue
        allowed.append(market)
    return allowed, blocked


def score_market_for_review(market: ResearchMarket) -> CandidateReview:
    score = round((market.liquidity_score * 100) - (market.spread_bps / 10), 2)
    rationale = (
        "Research-only candidate ranked by liquidity quality and tighter spread; "
        "not a trade recommendation."
    )
    return CandidateReview(
        market_id=market.market_id,
        matchup=market.matchup,
        start_time_utc=market.start_time_utc,
        market_type=market.market_type,
        score=score,
        rationale=rationale,
    )


def render_top_candidates_markdown(candidates: list[CandidateReview]) -> str:
    lines = ["# Top NBA Paper-Review Candidates", "", "Research-only review list. Not a live trading recommendation.", ""]
    for idx, candidate in enumerate(candidates, start=1):
        lines.extend(
            [
                f"## {idx}. {candidate.matchup}",
                f"- Market: `{candidate.market_id}`",
                f"- Type: {candidate.market_type}",
                f"- Start: {candidate.start_time_utc}",
                f"- Review score: {candidate.score}",
                f"- Rationale: {candidate.rationale}",
                "",
            ]
        )
    return "\n".join(lines)
