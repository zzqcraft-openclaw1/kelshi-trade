from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "kelshi-trade"
    environment: str = "dev"
    paper_only: bool = True
    db_path: str = "var/kelshi_trade.db"

    model_config = SettingsConfigDict(env_prefix="KELSHI_", env_file=".env", extra="ignore")

    def resolved_db_path(self) -> str:
        return str(Path(self.db_path))


settings = Settings()
