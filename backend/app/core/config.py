"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://finsight_db_z9pe_user:DSgXQpk2rR784EzTEEanhcfDZfkjn0Ea@dpg-d975drsvikkc73dlo59g-a/finsight_db_z9pe"

    # Auth
    SECRET_KEY: str = "234cd2ab81b5fc92b5197931907cc848ba6f682e5fd25541db3048e29e189464"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI
    OPENAI_API_KEY: "AQ.Ab8RN6Ioj4Z-sXbwobEB9erKsuEBAKkerPyYhnRU9Y5WGcPCgg"

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
