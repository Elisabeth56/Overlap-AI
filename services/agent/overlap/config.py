"""Environment-backed settings. Read once at import time."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    fixture_project_id: str = "11111111-1111-1111-1111-111111111111"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
