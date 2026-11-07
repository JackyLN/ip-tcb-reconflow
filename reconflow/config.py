"""Runtime configuration. Secrets never have shared defaults."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///reconflow.db"
    session_secret: str = Field(min_length=32)
    demo_mode: bool = False
    cookie_secure: bool = True
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_input_usd_per_million: str = "0"
    llm_output_usd_per_million: str = "0"


@lru_cache
def settings() -> Settings:
    return Settings()
