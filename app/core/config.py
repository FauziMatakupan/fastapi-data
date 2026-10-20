"""Core settings for fastapi-data-lite (12-factor: env vars / .env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Application ---
    app_name: str = "FastAPI-Data-Lite"
    environment: str = "development"  # development | staging | production
    api_v1_prefix: str = "/api/v1"

    # --- Data layer ---
    data_dir: str = "./data"
    max_upload_mb: int = 100


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor - routes should import `settings` directly."""
    return Settings()


settings = get_settings()