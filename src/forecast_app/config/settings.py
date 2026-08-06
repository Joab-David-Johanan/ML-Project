"""Application runtime settings (env-driven)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    data_dir: str = "data"
    artifacts_dir: str = "artifacts"


settings = AppSettings()

