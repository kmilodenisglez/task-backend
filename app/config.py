# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None

    # JWT / security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    watchfiles_ignore: str = "output/postgres_data"
    testing: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # Rate limiting
    rate_limit_calls: int = 100
    rate_limit_period: int = 3600  # seconds

    # Monitoring
    enable_metrics: bool = True
    metrics_path: str = "/metrics"

    # Health checks
    health_check_interval: int = 30  # seconds

    # Modern configuration (Pydantic v2)
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


# Settings object instance
settings = Settings()  # type: ignore
