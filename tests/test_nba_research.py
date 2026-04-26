from datetime import datetime, timezone

from kelshi_trade.models import ResearchMarket
from kelshi_trade.research.nba_markets import (
    build_pregame_odds_snapshot,
    filter_nba_markets,
    score_market_for_review,
    select_markets_near_tipoff,
)
from kelshi_trade.models import LiveNBAMarket


def test_filter_nba_markets_blocks_non_sports() -> None:
    markets = [
        ResearchMarket(
            market_id="x",
            reference_game_id="1",
            title="Bad market",
            league="NBA",
            category="politics",
            subcategory="nba",
            matchup="A @ B",
            start_time_utc="2026-04-10T00:00:00Z",
            market_type="spread",
            liquidity_score=0.5,
            spread_bps=100,
            validated=False,
        )
    ]
    allowed, blocked = filter_nba_markets(markets)
    assert allowed == []
    assert blocked


def test_score_market_for_review_returns_candidate() -> None:
    market = ResearchMarket(
        market_id="m1",
        reference_game_id="1",
        title="Demo",
        league="NBA",
        category="sports",
        subcategory="nba",
        matchup="A @ B",
        start_time_utc="2026-04-10T00:00:00Z",
        market_type="spread",
        liquidity_score=0.8,
        spread_bps=60,
        validated=False,
    )
    candidate = score_market_for_review(market)
    assert candidate.market_id == "m1"
    assert candidate.score > 0


def test_select_markets_near_tipoff_keeps_only_game_markets_in_window() -> None:
    now = datetime(2026, 4, 13, 3, 30, tzinfo=timezone.utc)
    markets = [
        LiveNBAMarket(
            market_id="KXNBAGAME-26APR12UTALAL-LAL",
            event_ticker="KXNBAGAME-26APR12UTALAL",
            title="game",
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
        ),
        LiveNBAMarket(
            market_id="KXNBATOTAL-26APR12UTALAL-228",
            event_ticker="KXNBATOTAL-26APR12UTALAL",
            title="total",
            matchup="Utah Jazz @ Los Angeles Lakers",
            start_time_utc="2026-04-13T04:00:00Z",
            market_type="total",
            yes_bid=0.45,
            yes_ask=0.48,
            no_bid=0.51,
            no_ask=0.55,
            liquidity=10.0,
            volume=12.0,
            status="active",
            is_bundle=False,
            raw={},
        ),
        LiveNBAMarket(
            market_id="KXNBAGAME-26APR12PHIBOS-BOS",
            event_ticker="KXNBAGAME-26APR12PHIBOS",
            title="game-late",
            matchup="Philadelphia 76ers @ Boston Celtics",
            start_time_utc="2026-04-13T06:00:00Z",
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
        ),
    ]

    selected = select_markets_near_tipoff(markets, now=now, target_minutes_before_tip=30, window_minutes=15)

    assert [market.market_id for market in selected] == ["KXNBAGAME-26APR12UTALAL-LAL"]


def test_build_pregame_odds_snapshot_includes_required_fields() -> None:
    now = datetime(2026, 4, 13, 3, 30, tzinfo=timezone.utc)
    market = LiveNBAMarket(
        market_id="KXNBAGAME-26APR12UTALAL-LAL",
        event_ticker="KXNBAGAME-26APR12UTALAL",
        title="game",
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

    snapshot = build_pregame_odds_snapshot(market, capture_time=now)

    assert snapshot.capture_timestamp_utc == "2026-04-13T03:30:00Z"
    assert snapshot.minutes_before_start == 30
    assert snapshot.market_id == market.market_id
    assert snapshot.implied_probability_pct == 48.0
    assert snapshot.yes_bid == 0.45
    assert snapshot.no_ask == 0.55
