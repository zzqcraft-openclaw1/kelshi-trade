from dataclasses import dataclass

from kelshi_trade.config import Settings, settings
from kelshi_trade.data.sqlite_store import SQLiteStore
from kelshi_trade.models import Order, Position, Quote
from kelshi_trade.risk.rules import RiskLimits, check_order_allowed
from kelshi_trade.strategies.example import mean_reversion_signal


@dataclass
class PaperPortfolio:
    cash: float = 1000.0
    realized_pnl: float = 0.0


class PaperEngine:
    def __init__(self, store: SQLiteStore, limits: RiskLimits | None = None) -> None:
        self.store = store
        self.limits = limits or RiskLimits()
        self.portfolio = PaperPortfolio()

    def step(self, quote: Quote) -> str:
        self.store.save_quote(quote)
        signal = mean_reversion_signal(quote)
        if signal == "HOLD":
            return f"market={quote.market_id} signal=HOLD"

        side = signal
        position = self.store.get_position(quote.market_id)
        allowed = check_order_allowed(
            current_size=position.size,
            order_size=1,
            side=side,
            limits=self.limits,
            market_id=quote.market_id,
        )
        if not allowed:
            return f"market={quote.market_id} signal={signal} allowed=False"

        order = Order(order_id="paper-order-1", market_id=quote.market_id, side=side, size=1, price=quote.last)
        self.apply_fill(order)
        return f"market={quote.market_id} signal={signal} allowed=True price={quote.last}"

    def apply_fill(self, order: Order) -> None:
        position = self.store.get_position(order.market_id)
        signed_size = order.size if order.side == "BUY" else -order.size
        new_size = position.size + signed_size

        if new_size != 0 and order.side == "BUY":
            total_cost = (position.avg_price * position.size) + (order.price * order.size)
            avg_price = total_cost / max(new_size, 1)
        elif new_size == 0:
            avg_price = 0.0
        else:
            avg_price = position.avg_price

        updated = Position(market_id=order.market_id, size=new_size, avg_price=avg_price)
        self.store.save_position(updated)


def build_store(app_settings: Settings = settings) -> SQLiteStore:
    return SQLiteStore(app_settings.resolved_db_path())


def run_paper_demo() -> str:
    store = build_store()
    engine = PaperEngine(store=store, limits=RiskLimits(paper_only=settings.paper_only))
    quote = Quote(market_id="demo", bid=0.42, ask=0.46, last=0.41)
    return engine.step(quote)
