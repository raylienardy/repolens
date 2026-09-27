from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "RepoLens API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    SECRET_KEY: str = "secret_key"
    DATABASE_URL: str = "postgresql+asyncpg://repolens:repolens@localhost:5433/repolens"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    GITHUB_TOKEN: str | None = None
    AI_PROVIDER: str = "mock"
    AI_MODEL: str | None = None
    AI_API_KEY: str | None = None
    AI_BASE_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
