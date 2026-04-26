from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from kelshi_trade.client.kalshi import KalshiReadOnlyClient
from kelshi_trade.config import Settings
from kelshi_trade.forecasting.pipeline import run_forecast_pipeline, select_game_markets
from kelshi_trade.research.nba_markets import (
    best_by_game_and_type,
    best_candidate_per_game,
    build_pregame_odds_snapshot,
    dedupe_live_candidates,
    filter_candidates_by_start_window,
    filter_live_nba_markets,
    load_live_nba_markets,
    select_markets_near_tipoff,
    score_live_market_for_review,
    split_candidates_by_type,
)
from kelshi_trade.research.reporting import (
    export_best_per_game_report,
    export_pregame_odds_snapshots,
    export_review_report,
    export_split_review_reports,
    export_summary_by_game,
)


@dataclass(slots=True)
class DoctorCheck:
    name: str
    ok: bool
    detail: str


@dataclass(slots=True)
class RunArtifacts:
    run_id: str
    reports_dir: str
    state_dir: str
    raw_snapshot_path: str
    manifest_path: str
    report_paths: list[str]
    forecast_path: str | None
    summary_counts: dict[str, int]


@dataclass(slots=True)
class PregameCaptureArtifacts:
    run_id: str
    reports_dir: str
    state_dir: str
    raw_snapshot_path: str
    manifest_path: str
    json_path: str
    csv_path: str
    note_path: str
    captured_count: int


@dataclass(slots=True)
class PreparedRun:
    run_id: str
    reports_dir: Path
    state_dir: Path
    snapshot_path: Path
    started_at_utc: str


PAPER_ONLY_FAILURE = "paper-only guardrail failed: KELSHI_PAPER_ONLY must remain true"


def utc_timestamp() -> datetime:
    return datetime.now(timezone.utc)


def format_run_id(now: datetime | None = None) -> str:
    stamp = now or utc_timestamp()
    return stamp.strftime("%Y%m%dT%H%M%SZ")


def ensure_writable_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    probe = path / ".write_test"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink()


def normalize_for_json(value):
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {key: normalize_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_for_json(item) for item in value]
    return value


def run_doctor(settings: Settings) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []

    checks.append(
        DoctorCheck(
            name="paper_only",
            ok=settings.paper_only is True,
            detail="paper-only mode enabled" if settings.paper_only else PAPER_ONLY_FAILURE,
        )
    )

    db_parent = settings.resolved_db_path().parent
    try:
        ensure_writable_dir(db_parent)
        checks.append(DoctorCheck("db_parent", True, f"writable: {db_parent}"))
    except Exception as exc:  # pragma: no cover - exercised through CLI failure path
        checks.append(DoctorCheck("db_parent", False, f"db parent not writable: {db_parent} ({exc})"))

    for name, path in (("reports_dir", settings.resolved_reports_path()), ("var_dir", settings.resolved_var_path())):
        try:
            ensure_writable_dir(path)
            checks.append(DoctorCheck(name, True, f"writable: {path}"))
        except Exception as exc:  # pragma: no cover
            checks.append(DoctorCheck(name, False, f"directory not writable: {path} ({exc})"))

    if settings.resolved_snapshot_path().exists():
        checks.append(DoctorCheck("market_snapshot_source", True, f"using existing raw snapshot: {settings.resolved_snapshot_path()}"))
    elif settings.has_kalshi_credentials():
        key_path = settings.resolved_private_key_path()
        if key_path and key_path.exists():
            checks.append(DoctorCheck("kalshi_credentials", True, f"read-only Kalshi credentials configured: {key_path}"))
        else:
            checks.append(DoctorCheck("kalshi_credentials", False, f"private key path does not exist: {key_path}"))
    else:
        checks.append(
            DoctorCheck(
                "market_snapshot_source",
                False,
                "missing raw snapshot and no read-only Kalshi credentials configured",
            )
        )

    return checks


def doctor_ok(checks: list[DoctorCheck]) -> bool:
    return all(check.ok for check in checks)


def prepare_run_directories(settings: Settings, now: datetime | None = None) -> PreparedRun:
    timestamp = now or utc_timestamp()
    run_id = format_run_id(timestamp)
    reports_dir = settings.resolved_reports_path() / "runs" / run_id / "nba_paper_review"
    state_dir = settings.resolved_var_path() / "runs" / run_id
    reports_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = state_dir / "kalshi_raw_markets.json"
    return PreparedRun(
        run_id=run_id,
        reports_dir=reports_dir,
        state_dir=state_dir,
        snapshot_path=snapshot_path,
        started_at_utc=timestamp.isoformat().replace("+00:00", "Z"),
    )


def acquire_snapshot(settings: Settings, snapshot_path: Path, *, refresh: bool = False, limit: int = 100, pages: int = 1) -> tuple[Path, str]:
    existing = settings.resolved_snapshot_path()
    if existing.exists() and not refresh:
        snapshot_path.write_text(existing.read_text(encoding="utf-8"), encoding="utf-8")
        return snapshot_path, "existing_snapshot"

    if not settings.has_kalshi_credentials():
        raise ValueError("no raw snapshot available and read-only Kalshi credentials are not configured")

    key_path = settings.resolved_private_key_path()
    if key_path is None:
        raise ValueError("read-only Kalshi credentials are configured incompletely")

    client = KalshiReadOnlyClient(
        base_url=settings.kalshi_base_url,
        api_key_id=settings.kalshi_api_key_id,
        private_key_path=str(key_path),
    )
    payload = client.list_markets_paginated(limit=limit, max_pages=pages) if pages > 1 else client.list_markets(limit=limit)
    client.dump_raw_snapshot(payload, str(snapshot_path))
    settings.resolved_snapshot_path().parent.mkdir(parents=True, exist_ok=True)
    settings.resolved_snapshot_path().write_text(snapshot_path.read_text(encoding="utf-8"), encoding="utf-8")
    return snapshot_path, "fresh_fetch"


def run_nba_paper_review(
    settings: Settings,
    *,
    top: int = 10,
    hours_ahead: int | None = None,
    include_forecast: bool = True,
    refresh_snapshot: bool = False,
    limit: int = 100,
    pages: int = 1,
    now: datetime | None = None,
) -> RunArtifacts:
    if not settings.paper_only:
        raise ValueError(PAPER_ONLY_FAILURE)

    prepared = prepare_run_directories(settings, now=now)
    snapshot_path, snapshot_source = acquire_snapshot(
        settings,
        prepared.snapshot_path,
        refresh=refresh_snapshot,
        limit=limit,
        pages=pages,
    )

    markets = load_live_nba_markets(str(snapshot_path))
    allowed, blocked = filter_live_nba_markets(markets)
    scored = sorted((score_live_market_for_review(m) for m in allowed), key=lambda c: c.score, reverse=True)
    deduped = dedupe_live_candidates(scored)
    working = filter_candidates_by_start_window(deduped, hours_ahead)
    top_candidates = working[:top]

    report_paths: list[str] = []
    md_path, csv_path = export_review_report(top_candidates, str(prepared.reports_dir))
    report_paths.extend([md_path, csv_path])
    report_paths.extend(export_split_review_reports(split_candidates_by_type(working), str(prepared.reports_dir)))
    report_paths.append(export_best_per_game_report(best_candidate_per_game(working), str(prepared.reports_dir)))
    report_paths.append(export_summary_by_game(best_by_game_and_type(working), str(prepared.reports_dir)))

    forecast_path: str | None = None
    if include_forecast:
        forecast_markets = select_game_markets(allowed)
        forecasts = run_forecast_pipeline(forecast_markets)
        forecast_path = str(prepared.reports_dir / "nba_game_forecasts.json")
        Path(forecast_path).write_text(
            json.dumps(normalize_for_json([asdict(item) for item in forecasts]), indent=2),
            encoding="utf-8",
        )
        report_paths.append(forecast_path)

    manifest = {
        "run_id": prepared.run_id,
        "command": "kelshi-trade run-nba-paper-review",
        "paper_only": settings.paper_only,
        "environment": settings.environment,
        "started_at_utc": prepared.started_at_utc,
        "snapshot": {
            "path": str(snapshot_path),
            "source": snapshot_source,
            "default_snapshot_path": str(settings.resolved_snapshot_path()),
        },
        "artifacts": {
            "reports_dir": str(prepared.reports_dir),
            "state_dir": str(prepared.state_dir),
            "report_paths": report_paths,
            "forecast_path": forecast_path,
        },
        "counts": {
            "nba_markets_detected": len(markets),
            "review_candidates_allowed": len(allowed),
            "review_candidates_blocked": len(blocked),
            "review_candidates_deduped": len(deduped),
            "review_candidates_windowed": len(working),
            "review_candidates_exported": len(top_candidates),
            "game_forecast_markets": len(select_game_markets(allowed)) if include_forecast else 0,
        },
        "filters": {
            "top": top,
            "hours_ahead": hours_ahead,
            "include_forecast": include_forecast,
            "refresh_snapshot": refresh_snapshot,
            "limit": limit,
            "pages": pages,
        },
        "research_only_notice": "Research and paper-review only. Not a live trading recommendation.",
    }
    manifest_path = prepared.state_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return RunArtifacts(
        run_id=prepared.run_id,
        reports_dir=str(prepared.reports_dir),
        state_dir=str(prepared.state_dir),
        raw_snapshot_path=str(snapshot_path),
        manifest_path=str(manifest_path),
        report_paths=report_paths,
        forecast_path=forecast_path,
        summary_counts=manifest["counts"],
    )


def run_nba_pregame_baseline_capture(
    settings: Settings,
    *,
    refresh_snapshot: bool = False,
    limit: int = 100,
    pages: int = 1,
    target_minutes_before_tip: int = 30,
    window_minutes: int = 15,
    now: datetime | None = None,
) -> PregameCaptureArtifacts:
    if not settings.paper_only:
        raise ValueError(PAPER_ONLY_FAILURE)

    capture_time = now or utc_timestamp()
    prepared = prepare_run_directories(settings, now=capture_time)
    snapshot_path, snapshot_source = acquire_snapshot(
        settings,
        prepared.snapshot_path,
        refresh=refresh_snapshot,
        limit=limit,
        pages=pages,
    )

    markets = load_live_nba_markets(str(snapshot_path))
    allowed, blocked = filter_live_nba_markets(markets)
    selected = select_markets_near_tipoff(
        allowed,
        now=capture_time,
        target_minutes_before_tip=target_minutes_before_tip,
        window_minutes=window_minutes,
    )
    snapshots = [build_pregame_odds_snapshot(market, capture_time=capture_time) for market in selected]
    json_path, csv_path, note_path = export_pregame_odds_snapshots(snapshots, str(prepared.reports_dir))

    manifest = {
        "run_id": prepared.run_id,
        "command": "kelshi-trade capture-nba-pregame-baseline",
        "paper_only": settings.paper_only,
        "environment": settings.environment,
        "started_at_utc": prepared.started_at_utc,
        "snapshot": {
            "path": str(snapshot_path),
            "source": snapshot_source,
            "default_snapshot_path": str(settings.resolved_snapshot_path()),
        },
        "artifacts": {
            "reports_dir": str(prepared.reports_dir),
            "state_dir": str(prepared.state_dir),
            "json_path": json_path,
            "csv_path": csv_path,
            "note_path": note_path,
        },
        "counts": {
            "nba_markets_detected": len(markets),
            "review_candidates_allowed": len(allowed),
            "review_candidates_blocked": len(blocked),
            "pregame_game_markets_captured": len(snapshots),
        },
        "filters": {
            "refresh_snapshot": refresh_snapshot,
            "limit": limit,
            "pages": pages,
            "target_minutes_before_tip": target_minutes_before_tip,
            "window_minutes": window_minutes,
        },
        "research_only_notice": "Research and paper-review only. Not a live trading recommendation.",
    }
    manifest_path = prepared.state_dir / "pregame_capture_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return PregameCaptureArtifacts(
        run_id=prepared.run_id,
        reports_dir=str(prepared.reports_dir),
        state_dir=str(prepared.state_dir),
        raw_snapshot_path=str(snapshot_path),
        manifest_path=str(manifest_path),
        json_path=json_path,
        csv_path=csv_path,
        note_path=note_path,
        captured_count=len(snapshots),
    )
