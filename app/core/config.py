from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "FireSight Sports API"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg2://firesight:firesight@localhost:5432/firesight"
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
