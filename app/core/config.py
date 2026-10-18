"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Holds all runtime settings for the app."""

    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Fitness Studio Booking API"
    app_version: str = "1.0.0"

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./fitness.db")

    # JWT settings
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # Class times are stored in IST as per assignment requirement
    studio_timezone: str = "Asia/Kolkata"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
