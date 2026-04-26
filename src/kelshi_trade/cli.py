import typer

from kelshi_trade.client.kalshi import KalshiReadOnlyClient
from kelshi_trade.config import get_settings
from kelshi_trade.forecasting.pipeline import run_forecast_pipeline, select_game_markets
from kelshi_trade.data.mock import MockMarketDataSource
from kelshi_trade.paper_trader.engine import PaperEngine, build_store, run_paper_demo
from kelshi_trade.research import export_review_report
from kelshi_trade.research.nba_markets import (
    MockNBAMarketSource,
    best_by_game_and_type,
    best_candidate_per_game,
    dedupe_live_candidates,
    filter_candidates_by_start_window,
    filter_live_nba_markets,
    filter_nba_markets,
    load_live_nba_markets,
    render_top_candidates_markdown,
    score_live_market_for_review,
    score_market_for_review,
    split_candidates_by_type,
)
from kelshi_trade.research.reporting import export_best_per_game_report, export_split_review_reports, export_summary_by_game
from kelshi_trade.risk.rules import RiskLimits
from kelshi_trade.workflow import doctor_ok, run_doctor, run_nba_paper_review
from kelshi_trade.workflow import run_nba_pregame_baseline_capture

app = typer.Typer(help="kelshi-trade CLI")


@app.command()
def status() -> None:
    """Show basic project status."""
    settings = get_settings()
    typer.echo(
        f"kelshi-trade scaffold is ready | env={settings.environment} db={settings.resolved_db_path()} paper_only={settings.paper_only}"
    )


@app.command()
def doctor() -> None:
    """Run paper-only workflow preflight checks."""
    settings = get_settings()
    checks = run_doctor(settings)
    for check in checks:
        status = "OK" if check.ok else "FAIL"
        typer.echo(f"[{status}] {check.name}: {check.detail}")
    if doctor_ok(checks):
        typer.echo("doctor passed: paper-only NBA review workflow looks ready")
        return
    raise typer.Exit(code=1)


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
    settings = get_settings()
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
    out: str | None = None,
) -> None:
    """Generate a research-only top-candidate review list for NBA markets."""
    source = MockNBAMarketSource(slate_csv)
    markets = source.load_markets()
    allowed, blocked = filter_nba_markets(markets)
    scored = sorted((score_market_for_review(m) for m in allowed), key=lambda c: c.score, reverse=True)
    top_candidates = scored[:top]
    typer.echo(render_top_candidates_markdown(top_candidates))
    if out:
        md_path, csv_path = export_review_report(top_candidates, out)
        typer.echo(f"\nExported report: {md_path}")
        typer.echo(f"Exported csv: {csv_path}")
    if blocked:
        typer.echo("\nBlocked markets:")
        for item in blocked:
            typer.echo(f"- {item}")


@app.command("sync-kalshi-markets")
def sync_kalshi_markets(
    limit: int = 100,
    out: str = "var/kalshi_raw_markets.json",
    pages: int = 1,
) -> None:
    """Fetch Kalshi markets in read-only mode and dump the raw response for research use."""
    settings = get_settings()
    if not settings.paper_only:
        raise typer.BadParameter("paper_only must remain enabled for read-only research sync")
    if not settings.kalshi_api_key_id or not settings.kalshi_private_key_path:
        raise typer.BadParameter("KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY_PATH must be configured")

    client = KalshiReadOnlyClient(
        base_url=settings.kalshi_base_url,
        api_key_id=settings.kalshi_api_key_id,
        private_key_path=settings.kalshi_private_key_path,
    )
    payload = client.list_markets_paginated(limit=limit, max_pages=pages) if pages > 1 else client.list_markets(limit=limit)
    client.dump_raw_snapshot(payload, out)
    typer.echo(f"saved raw Kalshi market snapshot to {out}")
    if pages > 1:
        typer.echo(f"pages fetched: {payload.get('pages_fetched')}")
        typer.echo(f"markets fetched: {len(payload.get('markets', []))}")


@app.command("report-kalshi-nba-review")
def report_kalshi_nba_review(
    raw_json: str = "var/kalshi_raw_markets.json",
    top: int = 10,
    out: str | None = "reports/live_nba_review",
    hours_ahead: int | None = None,
) -> None:
    """Build a cleaner NBA-only paper-review report from a saved Kalshi raw snapshot."""
    markets = load_live_nba_markets(raw_json)
    allowed, blocked = filter_live_nba_markets(markets)
    scored = sorted((score_live_market_for_review(m) for m in allowed), key=lambda c: c.score, reverse=True)
    deduped = dedupe_live_candidates(scored)
    windowed = filter_candidates_by_start_window(deduped, hours_ahead)
    working = windowed if hours_ahead is not None else deduped
    top_candidates = working[:top]
    typer.echo(render_top_candidates_markdown(top_candidates))
    typer.echo(f"\nDetected NBA-linked markets: {len(markets)}")
    typer.echo(f"Clean single-NBA review candidates: {len(allowed)}")
    typer.echo(f"Deduped review candidates: {len(deduped)}")
    if hours_ahead is not None:
        typer.echo(f"Within next {hours_ahead}h: {len(working)}")
    typer.echo(f"Blocked/filtered markets: {len(blocked)}")
    if out:
        md_path, csv_path = export_review_report(top_candidates, out)
        typer.echo(f"Exported report: {md_path}")
        typer.echo(f"Exported csv: {csv_path}")
        split_paths = export_split_review_reports(split_candidates_by_type(working), out)
        for path in split_paths:
            typer.echo(f"Exported split report: {path}")
        best_game_path = export_best_per_game_report(best_candidate_per_game(working), out)
        typer.echo(f"Exported best-per-game report: {best_game_path}")
        summary_path = export_summary_by_game(best_by_game_and_type(working), out)
        typer.echo(f"Exported summary-by-game report: {summary_path}")


@app.command("report-kalshi-nba-forecast")
def report_kalshi_nba_forecast(
    raw_json: str = "var/kalshi_raw_markets.json",
    matchup: str | None = None,
    top: int = 10,
) -> None:
    """Run the paper-only forecast scaffold over extracted NBA markets."""
    markets = load_live_nba_markets(raw_json)
    allowed, _ = filter_live_nba_markets(markets)
    allowed = select_game_markets(allowed)
    if matchup:
        allowed = [m for m in allowed if m.matchup == matchup]
    forecasts = run_forecast_pipeline(allowed)
    shown = 0
    for forecast in forecasts:
        typer.echo(
            f"{forecast.matchup} | {forecast.market_id} | {forecast.market_type} | "
            f"predicted={forecast.predicted_probability_pct if forecast.predicted_probability_pct is not None else 'needs_data'} | "
            f"implied={forecast.market_implied_probability_pct if forecast.market_implied_probability_pct is not None else 'n/a'} | "
            f"edge={forecast.estimated_edge_pct if forecast.estimated_edge_pct is not None else 'n/a'} | "
            f"surfaced_edge={forecast.surfaced_edge_pct if forecast.surfaced_edge_pct is not None else 'n/a'} | "
            f"recommendation={forecast.recommendation} | confidence={forecast.confidence} | rationale={forecast.rationale}"
        )
        shown += 1
        if shown >= top:
            break


@app.command("run-nba-paper-review")
def run_nba_review_command(
    top: int = 10,
    hours_ahead: int | None = None,
    include_forecast: bool = True,
    refresh_snapshot: bool = False,
    limit: int = 100,
    pages: int = 1,
) -> None:
    """Run the one-shot daily NBA paper-review workflow."""
    settings = get_settings()
    try:
        artifacts = run_nba_paper_review(
            settings,
            top=top,
            hours_ahead=hours_ahead,
            include_forecast=include_forecast,
            refresh_snapshot=refresh_snapshot,
            limit=limit,
            pages=pages,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"run_id={artifacts.run_id}")
    typer.echo(f"reports_dir={artifacts.reports_dir}")
    typer.echo(f"state_dir={artifacts.state_dir}")
    typer.echo(f"raw_snapshot={artifacts.raw_snapshot_path}")
    typer.echo(f"manifest={artifacts.manifest_path}")
    for name, count in artifacts.summary_counts.items():
        typer.echo(f"{name}={count}")
    if artifacts.forecast_path:
        typer.echo(f"forecast={artifacts.forecast_path}")
    typer.echo("paper-only research run complete")


@app.command("capture-nba-pregame-baseline")
def capture_nba_pregame_baseline(
    refresh_snapshot: bool = False,
    limit: int = 100,
    pages: int = 1,
    target_minutes_before_tip: int = 30,
    window_minutes: int = 15,
) -> None:
    """Capture NBA game-winner odds near tipoff for paper-only post-game review."""
    settings = get_settings()
    try:
        artifacts = run_nba_pregame_baseline_capture(
            settings,
            refresh_snapshot=refresh_snapshot,
            limit=limit,
            pages=pages,
            target_minutes_before_tip=target_minutes_before_tip,
            window_minutes=window_minutes,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"run_id={artifacts.run_id}")
    typer.echo(f"reports_dir={artifacts.reports_dir}")
    typer.echo(f"state_dir={artifacts.state_dir}")
    typer.echo(f"raw_snapshot={artifacts.raw_snapshot_path}")
    typer.echo(f"manifest={artifacts.manifest_path}")
    typer.echo(f"pregame_json={artifacts.json_path}")
    typer.echo(f"pregame_csv={artifacts.csv_path}")
    typer.echo(f"pregame_note={artifacts.note_path}")
    typer.echo(f"captured_count={artifacts.captured_count}")
    typer.echo("paper-only pregame baseline capture complete")


if __name__ == "__main__":
    app()
