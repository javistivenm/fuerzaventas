from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bridge_host: str
    bridge_port: int = 8787
    bridge_api_key: str
    bridge_log_file: str = "logs/bridge.log"

    firebird_client_library: str
    firebird_host: str = "127.0.0.1"
    firebird_port: int = 3050
    firebird_database: str
    firebird_user: str
    firebird_password: str
    firebird_charset: str = "WIN1252"


settings = Settings()

