# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None

    # JWT / security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    watchfiles_ignore: str = "output/postgres_data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
