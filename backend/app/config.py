from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://hiresense:hiresense@localhost:5432/hiresense"

    frontend_origin: str = "http://localhost:3000"

    jwt_secret_key: str
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 7

    aws_region: str = "us-east-1"
    aws_endpoint_url: str | None = None  # set to LocalStack URL for local dev
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket_name: str = "hiresense-resumes-dev"
    sqs_queue_url: str = "http://localhost:4566/000000000000/hiresense-evaluation-jobs-dev"

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    return Settings()
