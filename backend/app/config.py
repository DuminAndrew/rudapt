from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
    REDIS_URL: str = ""

    JWT_SECRET: str = "dev-insecure-change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_TTL_MIN: int = 60
    REFRESH_TOKEN_TTL_DAYS: int = 30

    CORS_ORIGINS: str = "http://localhost:3000"

    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL_ANTHROPIC: str = "claude-opus-4-7"
    LLM_MODEL_OPENAI: str = "gpt-4o"

    PRODUCTHUNT_TOKEN: str | None = None
    CRUNCHBASE_API_KEY: str | None = None

    PDF_SERVICE_URL: str = "http://pdf:9000"
    PDF_SERVICE_TOKEN: str = ""

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
