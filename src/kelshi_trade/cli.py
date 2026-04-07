import typer

from kelshi_trade.config import settings
from kelshi_trade.data.mock import MockMarketDataSource
from kelshi_trade.paper_trader.engine import PaperEngine, build_store, run_paper_demo
from kelshi_trade.risk.rules import RiskLimits

app = typer.Typer(help="kelshi-trade CLI")


@app.command()
def status() -> None:
    """Show basic project status."""
    typer.echo(
        f"kelshi-trade scaffold is ready | env={settings.environment} db={settings.resolved_db_path()} paper_only={settings.paper_only}"
    )


@app.command("capture-quotes")
def capture_quotes(market_id: str = "demo") -> None:
    """Capture a quote from the mock data source into sqlite."""
    source = MockMarketDataSource()
    store = build_store()
    quote = source.get_quote(market_id)
    store.save_quote(quote)
    typer.echo(f"captured quote for {market_id}: last={quote.last}")


@app.command("run-strategy")
def run_strategy(market_id: str = "demo") -> None:
    """Run one paper-engine step using mock data."""
    source = MockMarketDataSource()
    store = build_store()
    engine = PaperEngine(store=store, limits=RiskLimits(paper_only=settings.paper_only))
    quote = source.get_quote(market_id)
    typer.echo(engine.step(quote))


@app.command("show-portfolio")
def show_portfolio(market_id: str = "demo") -> None:
    """Show stored paper position for a market."""
    store = build_store()
    position = store.get_position(market_id)
    typer.echo(
        f"market={position.market_id} size={position.size} avg_price={position.avg_price}"
    )


@app.command()
def paper_demo() -> None:
    """Run a tiny paper-trading demo."""
    result = run_paper_demo()
    typer.echo(result)


if __name__ == "__main__":
    app()
