from kelshi_trade.models import ResearchMarket
from kelshi_trade.research.nba_markets import filter_nba_markets, score_market_for_review


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
