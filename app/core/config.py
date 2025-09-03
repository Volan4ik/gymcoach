from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENV: str = "dev"
    DEBUG: bool = True

    BOT_TOKEN: str | None = None

    DATABASE_URL: str | None = None
    REDIS_URL: str | None = None
    S3_ENDPOINT: str | None = None
    S3_BUCKET: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None

settings = Settings()