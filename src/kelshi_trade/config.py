from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "kelshi-trade"
    environment: str = "dev"
    paper_only: bool = True
    db_path: str = "var/kelshi_trade.db"
    kalshi_api_key_id: str = ""
    kalshi_private_key_path: str = ""
    kalshi_base_url: str = "https://api.elections.kalshi.com/trade-api/v2"

    model_config = SettingsConfigDict(env_prefix="KELSHI_", env_file=".env", extra="ignore")

    def resolved_db_path(self) -> str:
        return str(Path(self.db_path))


settings = Settings()
