from kelshi_trade.data.sqlite_store import SQLiteStore
from kelshi_trade.models import Quote


def test_sqlite_store_round_trip_quote(tmp_path) -> None:
    store = SQLiteStore(str(tmp_path / "test.db"))
    quote = Quote(market_id="demo", bid=0.4, ask=0.5, last=0.45)
    store.save_quote(quote)

    loaded = store.latest_quote("demo")
    assert loaded is not None
    assert loaded.market_id == "demo"
    assert loaded.last == 0.45
