from kelshi_trade.config import Settings


def test_settings_resolve_db_path() -> None:
    settings = Settings(db_path="var/test.db")
    assert settings.resolved_db_path().endswith("var/test.db")
