from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from kelshi_trade.models import LiveNBAMarket, PregameOddsSnapshot, ResearchMarket


@dataclass(slots=True)
class CandidateReview:
    market_id: str
    matchup: str
    start_time_utc: str
    market_type: str
    score: float
    rationale: str
    description: str = ""
    priority: str = "medium"
    model_probability_pct: float | None = None
    market_implied_probability_pct: float | None = None
    confidence_note: str = "needs_data"


TEAM_CODE_MAP = {
    "ATL": "Atlanta Hawks",
    "BKN": "Brooklyn Nets",
    "BOS": "Boston Celtics",
    "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards",
}


def decode_matchup_from_event(event_code: str) -> str:
    match = re.search(r"-(?:\d{2}[A-Z]{3}\d{2})([A-Z]{3})([A-Z]{3})$", event_code)
    if not match:
        return event_code
    away, home = match.group(1), match.group(2)
    away_name = TEAM_CODE_MAP.get(away, away)
    home_name = TEAM_CODE_MAP.get(home, home)
    return f"{away_name} @ {home_name}"


def decode_game_key(event_code: str) -> str:
    match = re.search(r"-(?:\d{2}[A-Z]{3}\d{2})([A-Z]{3})([A-Z]{3})$", event_code)
    if not match:
        return event_code
    return f"{match.group(1)}@{match.group(2)}"


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
                f"- Description: {candidate.description or candidate.market_id}",
                f"- Start: {candidate.start_time_utc}",
                f"- Review score: {candidate.score}",
                f"- Priority: {candidate.priority}",
                f"- Model probability: {candidate.model_probability_pct if candidate.model_probability_pct is not None else 'needs_data'}",
                f"- Market implied probability: {candidate.market_implied_probability_pct if candidate.market_implied_probability_pct is not None else 'n/a'}",
                f"- Confidence note: {candidate.confidence_note}",
                f"- Rationale: {candidate.rationale}",
                "",
            ]
        )
    return "\n".join(lines)


def load_live_nba_markets(raw_json_path: str) -> list[LiveNBAMarket]:
    payload = json.loads(Path(raw_json_path).read_text(encoding="utf-8"))
    dedup: dict[str, LiveNBAMarket] = {}

    for item in payload.get("markets", []):
        custom = item.get("custom_strike") or {}
        associated_events = str(custom.get("Associated Events", ""))
        associated_markets = str(custom.get("Associated Markets", ""))
        event_parts = [part.strip() for part in associated_events.split(",") if part.strip()]
        market_parts = [part.strip() for part in associated_markets.split(",") if part.strip()]

        for event_code, market_code in zip(event_parts, market_parts):
            if not event_code.startswith(("KXNBAGAME", "KXNBASPREAD", "KXNBATOTAL", "KXNBAPTS", "KXNBAREB", "KXNBAAST", "KXNBA3PT")):
                continue

            market_type = "unknown"
            if event_code.startswith("KXNBAGAME"):
                market_type = "game"
            elif event_code.startswith("KXNBASPREAD"):
                market_type = "spread"
            elif event_code.startswith("KXNBATOTAL"):
                market_type = "total"
            elif event_code.startswith("KXNBAPTS"):
                market_type = "player_points_prop"
            elif event_code.startswith("KXNBAREB"):
                market_type = "player_rebounds_prop"
            elif event_code.startswith("KXNBAAST"):
                market_type = "player_assists_prop"
            elif event_code.startswith("KXNBA3PT"):
                market_type = "player_threes_prop"

            title = market_code
            matchup = decode_matchup_from_event(event_code)
            dedup[market_code] = LiveNBAMarket(
                market_id=market_code,
                event_ticker=event_code,
                title=title,
                matchup=matchup,
                start_time_utc=str(item.get("expected_expiration_time", "")),
                market_type=market_type,
                yes_bid=float(item.get("yes_bid_dollars") or 0),
                yes_ask=float(item.get("yes_ask_dollars") or 0),
                no_bid=float(item.get("no_bid_dollars") or 0),
                no_ask=float(item.get("no_ask_dollars") or 0),
                liquidity=float(item.get("liquidity_dollars") or 0),
                volume=float(item.get("volume_fp") or 0),
                status=str(item.get("status", "")),
                is_bundle=False,
                raw={"source_wrapper": item.get("ticker", "")},
            )
    return list(dedup.values())


def filter_live_nba_markets(markets: list[LiveNBAMarket]) -> tuple[list[LiveNBAMarket], list[str]]:
    allowed: list[LiveNBAMarket] = []
    blocked: list[str] = []
    for market in markets:
        if market.status != "active":
            blocked.append(f"{market.market_id}: inactive status")
            continue
        if market.market_type not in {
            "game",
            "spread",
            "total",
            "player_points_prop",
            "player_rebounds_prop",
            "player_assists_prop",
            "player_threes_prop",
        }:
            blocked.append(f"{market.market_id}: blocked unsupported NBA market type {market.market_type}")
            continue
        if not market.start_time_utc:
            blocked.append(f"{market.market_id}: missing event time")
            continue
        allowed.append(market)
    return allowed, blocked


def decode_market_description(market: LiveNBAMarket) -> str:
    tail = market.market_id.split('-')[-1]
    if market.market_type == "game":
        team_code = tail
        team_name = TEAM_CODE_MAP.get(team_code, team_code)
        return f"Game winner: {team_name}"
    if market.market_type == "spread":
        match = re.match(r"([A-Z]{3})(\d+)$", tail)
        if match:
            team_name = TEAM_CODE_MAP.get(match.group(1), match.group(1))
            line = match.group(2)
            return f"Spread: {team_name} by over {line}.5 points"
    if market.market_type == "total":
        if tail.isdigit():
            return f"Total points line: {tail}.5"
    if market.market_type == "player_points_prop":
        return f"Player points prop: {tail}"
    if market.market_type == "player_rebounds_prop":
        return f"Player rebounds prop: {tail}"
    if market.market_type == "player_assists_prop":
        return f"Player assists prop: {tail}"
    if market.market_type == "player_threes_prop":
        return f"Player threes prop: {tail}"
    return market.market_id


def implied_probability_pct(market: LiveNBAMarket) -> float | None:
    if market.market_type != "game":
        return None
    if market.yes_ask and market.yes_ask > 0:
        return round(market.yes_ask * 100, 2)
    if market.yes_bid and market.yes_bid > 0:
        return round(market.yes_bid * 100, 2)
    return None


def parse_iso_utc(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


def select_markets_near_tipoff(
    markets: list[LiveNBAMarket],
    *,
    now: datetime | None = None,
    target_minutes_before_tip: int = 30,
    window_minutes: int = 15,
) -> list[LiveNBAMarket]:
    anchor = now or datetime.now(timezone.utc)
    lower = target_minutes_before_tip - window_minutes
    upper = target_minutes_before_tip + window_minutes
    selected: list[LiveNBAMarket] = []
    for market in markets:
        if market.market_type != "game":
            continue
        try:
            start = parse_iso_utc(market.start_time_utc)
        except ValueError:
            continue
        minutes_before_start = (start - anchor).total_seconds() / 60
        if lower <= minutes_before_start <= upper:
            selected.append(market)
    return sorted(selected, key=lambda market: market.start_time_utc)


def build_pregame_odds_snapshot(market: LiveNBAMarket, *, capture_time: datetime | None = None) -> PregameOddsSnapshot:
    capture = capture_time or datetime.now(timezone.utc)
    start = parse_iso_utc(market.start_time_utc)
    minutes_before_start = int(round((start - capture).total_seconds() / 60))
    return PregameOddsSnapshot(
        capture_timestamp_utc=capture.isoformat().replace("+00:00", "Z"),
        minutes_before_start=minutes_before_start,
        market_id=market.market_id,
        event_ticker=market.event_ticker,
        matchup=market.matchup,
        market_type=market.market_type,
        start_time_utc=market.start_time_utc,
        implied_probability_pct=implied_probability_pct(market),
        yes_bid=market.yes_bid,
        yes_ask=market.yes_ask,
        no_bid=market.no_bid,
        no_ask=market.no_ask,
        liquidity=market.liquidity,
        volume=market.volume,
    )


def score_live_market_for_review(market: LiveNBAMarket) -> CandidateReview:
    spread_penalty = abs((market.yes_ask + market.no_bid) - 1.0) * 100 if market.yes_ask and market.no_bid else 10.0
    quote_bonus = 8.0 if (market.yes_ask > 0 or market.yes_bid > 0 or market.no_bid < 1.0 or market.no_ask < 1.0) else 0.0
    type_bonus = {
        "game": 18.0,
        "spread": 16.0,
        "total": 16.0,
        "player_points_prop": 12.0,
        "player_rebounds_prop": 10.0,
        "player_assists_prop": 10.0,
        "player_threes_prop": 10.0,
    }.get(market.market_type, 0.0)
    score = round(type_bonus + quote_bonus + min(market.liquidity, 20.0) + min(market.volume, 20.0) - spread_penalty, 2)
    priority = "high" if score >= 40 else "medium" if score >= 28 else "low"
    rationale = "Single-NBA market prioritized for paper review based on cleaner structure and visible quote quality."
    return CandidateReview(
        market_id=market.market_id,
        matchup=market.matchup,
        start_time_utc=market.start_time_utc,
        market_type=market.market_type,
        score=score,
        rationale=rationale,
        description=decode_market_description(market),
        priority=priority,
        model_probability_pct=None,
        market_implied_probability_pct=implied_probability_pct(market),
        confidence_note="needs_data",
    )


def dedupe_live_candidates(candidates: list[CandidateReview]) -> list[CandidateReview]:
    seen_keys: set[tuple[str, str]] = set()
    deduped: list[CandidateReview] = []
    for candidate in sorted(candidates, key=lambda c: c.score, reverse=True):
        family = candidate.market_id.split('-')[0]
        key = (family, candidate.matchup)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(candidate)
    return deduped


def split_candidates_by_type(candidates: list[CandidateReview]) -> dict[str, list[CandidateReview]]:
    buckets: dict[str, list[CandidateReview]] = {}
    for candidate in candidates:
        buckets.setdefault(candidate.market_type, []).append(candidate)
    return buckets


def best_candidate_per_game(candidates: list[CandidateReview]) -> list[CandidateReview]:
    best: dict[str, CandidateReview] = {}
    for candidate in sorted(candidates, key=lambda c: c.score, reverse=True):
        key = candidate.matchup
        best.setdefault(key, candidate)
    return list(best.values())


def filter_candidates_by_start_window(candidates: list[CandidateReview], hours_ahead: int | None = None) -> list[CandidateReview]:
    if hours_ahead is None:
        return candidates
    now = datetime.now(timezone.utc)
    filtered: list[CandidateReview] = []
    for candidate in candidates:
        try:
            start = datetime.fromisoformat(candidate.start_time_utc.replace('Z', '+00:00'))
        except ValueError:
            continue
        delta_hours = (start - now).total_seconds() / 3600
        if 0 <= delta_hours <= hours_ahead:
            filtered.append(candidate)
    return filtered


def best_by_game_and_type(candidates: list[CandidateReview]) -> dict[str, dict[str, CandidateReview]]:
    summary: dict[str, dict[str, CandidateReview]] = {}
    for candidate in sorted(candidates, key=lambda c: c.score, reverse=True):
        game_bucket = summary.setdefault(candidate.matchup, {})
        family = candidate.market_type
        game_bucket.setdefault(family, candidate)
    return summary
