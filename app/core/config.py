from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # allow unrelated env vars like host, user, password, etc.
    )

    APP_NAME: str = "Workflowz.ai"
    API_V1_PREFIX: str = "/api"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    OLLAMA_MODEL: str = "gpt-oss:20b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"


settings = Settings()
