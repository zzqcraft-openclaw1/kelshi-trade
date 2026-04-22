from kelshi_trade.config import Settings


def test_settings_resolve_db_path() -> None:
    settings = Settings(db_path="var/test.db")
    assert str(settings.resolved_db_path()).endswith("var/test.db")


def test_settings_resolve_extra_paths() -> None:
    settings = Settings(reports_path="reports", var_path="var", raw_snapshot_path="var/kalshi_raw_markets.json")
    assert str(settings.resolved_reports_path()).endswith("reports")
    assert str(settings.resolved_var_path()).endswith("var")
    assert str(settings.resolved_snapshot_path()).endswith("var/kalshi_raw_markets.json")
