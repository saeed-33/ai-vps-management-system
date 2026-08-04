from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI VPS Management Control Plane"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = ""
    redis_url: str = ""
    cors_origins: list[str] = Field(default_factory=lambda: ["http://127.0.0.1:3000"])
    auth_secret_key: str = ""
    access_token_expire_minutes: int = 60
    bootstrap_admin_email: str = ""
    bootstrap_admin_password_hash: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
