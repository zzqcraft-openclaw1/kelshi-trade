import typer

from kelshi_trade.config import settings
from kelshi_trade.data.mock import MockMarketDataSource
from kelshi_trade.paper_trader.engine import PaperEngine, build_store, run_paper_demo
from kelshi_trade.research.nba_markets import (
    MockNBAMarketSource,
    filter_nba_markets,
    render_top_candidates_markdown,
    score_market_for_review,
)
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


@app.command("sync-nba-markets")
def sync_nba_markets(
    slate_csv: str = "data/nba_tomorrow_template.csv",
) -> None:
    """Load research-only NBA market candidates from the seeded slate file."""
    source = MockNBAMarketSource(slate_csv)
    markets = source.load_markets()
    allowed, blocked = filter_nba_markets(markets)
    store = build_store()
    store.save_research_markets(allowed)
    typer.echo(f"synced {len(allowed)} research-only NBA market candidates")
    if blocked:
        typer.echo(f"blocked {len(blocked)} candidates during sync")


@app.command("report-top-nba")
def report_top_nba(
    slate_csv: str = "data/nba_tomorrow_template.csv",
    top: int = 3,
) -> None:
    """Generate a research-only top-candidate review list for NBA markets."""
    source = MockNBAMarketSource(slate_csv)
    markets = source.load_markets()
    allowed, blocked = filter_nba_markets(markets)
    scored = sorted((score_market_for_review(m) for m in allowed), key=lambda c: c.score, reverse=True)
    typer.echo(render_top_candidates_markdown(scored[:top]))
    if blocked:
        typer.echo("\nBlocked markets:")
        for item in blocked:
            typer.echo(f"- {item}")


if __name__ == "__main__":
    app()
