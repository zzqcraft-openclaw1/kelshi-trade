import sqlite3
from pathlib import Path

from kelshi_trade.models import Position, Quote, ResearchMarket


class SQLiteStore:
    def __init__(self, db_path: str = "kelshi_trade.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS quotes (
                    market_id TEXT NOT NULL,
                    bid REAL NOT NULL,
                    ask REAL NOT NULL,
                    last REAL NOT NULL,
                    ts TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    market_id TEXT PRIMARY KEY,
                    size INTEGER NOT NULL,
                    avg_price REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS research_markets (
                    market_id TEXT PRIMARY KEY,
                    reference_game_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    league TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    matchup TEXT NOT NULL,
                    start_time_utc TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    liquidity_score REAL NOT NULL,
                    spread_bps INTEGER NOT NULL,
                    validated INTEGER NOT NULL
                )
                """
            )

    def save_quote(self, quote: Quote) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO quotes (market_id, bid, ask, last, ts) VALUES (?, ?, ?, ?, ?)",
                (quote.market_id, quote.bid, quote.ask, quote.last, quote.ts.isoformat()),
            )

    def latest_quote(self, market_id: str) -> Quote | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT market_id, bid, ask, last FROM quotes WHERE market_id = ? ORDER BY ts DESC LIMIT 1",
                (market_id,),
            ).fetchone()
        if row is None:
            return None
        return Quote(market_id=row[0], bid=row[1], ask=row[2], last=row[3])

    def save_position(self, position: Position) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO positions (market_id, size, avg_price)
                VALUES (?, ?, ?)
                ON CONFLICT(market_id) DO UPDATE SET
                    size = excluded.size,
                    avg_price = excluded.avg_price
                """,
                (position.market_id, position.size, position.avg_price),
            )

    def get_position(self, market_id: str) -> Position:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT market_id, size, avg_price FROM positions WHERE market_id = ?",
                (market_id,),
            ).fetchone()
        if row is None:
            return Position(market_id=market_id)
        return Position(market_id=row[0], size=row[1], avg_price=row[2])

    def save_research_markets(self, markets: list[ResearchMarket]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO research_markets (
                    market_id, reference_game_id, title, league, category, subcategory,
                    matchup, start_time_utc, market_type, liquidity_score, spread_bps, validated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(market_id) DO UPDATE SET
                    reference_game_id = excluded.reference_game_id,
                    title = excluded.title,
                    league = excluded.league,
                    category = excluded.category,
                    subcategory = excluded.subcategory,
                    matchup = excluded.matchup,
                    start_time_utc = excluded.start_time_utc,
                    market_type = excluded.market_type,
                    liquidity_score = excluded.liquidity_score,
                    spread_bps = excluded.spread_bps,
                    validated = excluded.validated
                """,
                [
                    (
                        market.market_id,
                        market.reference_game_id,
                        market.title,
                        market.league,
                        market.category,
                        market.subcategory,
                        market.matchup,
                        market.start_time_utc,
                        market.market_type,
                        market.liquidity_score,
                        market.spread_bps,
                        int(market.validated),
                    )
                    for market in markets
                ],
            )
