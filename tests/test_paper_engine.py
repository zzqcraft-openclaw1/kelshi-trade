from kelshi_trade.data.sqlite_store import SQLiteStore
from kelshi_trade.models import Quote
from kelshi_trade.paper_trader.engine import PaperEngine


def test_paper_engine_updates_position(tmp_path) -> None:
    store = SQLiteStore(str(tmp_path / "paper.db"))
    engine = PaperEngine(store=store)

    result = engine.step(Quote(market_id="demo", bid=0.42, ask=0.46, last=0.41))
    position = store.get_position("demo")

    assert "allowed=True" in result
    assert position.size == 1
