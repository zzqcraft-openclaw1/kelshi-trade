from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "kelshi-trade"
    environment: str = "dev"
    paper_only: bool = True
    db_path: str = "var/kelshi_trade.db"
    reports_path: str = "reports"
    var_path: str = "var"
    raw_snapshot_path: str = "var/kalshi_raw_markets.json"
    kalshi_api_key_id: str = ""
    kalshi_private_key_path: str = ""
    kalshi_base_url: str = "https://api.elections.kalshi.com/trade-api/v2"

    model_config = SettingsConfigDict(env_prefix="KELSHI_", env_file=".env", extra="ignore")

    def resolved_db_path(self) -> Path:
        return Path(self.db_path)

    def resolved_reports_path(self) -> Path:
        return Path(self.reports_path)

    def resolved_var_path(self) -> Path:
        return Path(self.var_path)

    def resolved_snapshot_path(self) -> Path:
        return Path(self.raw_snapshot_path)

    def resolved_private_key_path(self) -> Path | None:
        if not self.kalshi_private_key_path:
            return None
        return Path(self.kalshi_private_key_path).expanduser()

    def has_kalshi_credentials(self) -> bool:
        return bool(self.kalshi_api_key_id and self.kalshi_private_key_path)


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
