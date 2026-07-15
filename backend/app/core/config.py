"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://sonu2704:0GVZoxEOYwrkUA2ukevvaD7te28ltIyT@dpg-d975drsvikkc73dlo59g-a.singapore-postgres.render.com/finsight_db_z9pe"

    # Auth
    SECRET_KEY: str = "V6JGoPztxvenCKnzE4gMNkxgFSi3aaZpwbbqsNiEeo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None
    AI_MODEL: str = "gemini-3.5-flash"

    # App
    ENVIRONMENT: str = "production"
    CORS_ORIGINS: str = "https://finsight-ai-kappa-six.vercel.app"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
