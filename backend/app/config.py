
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./finance.db"
    llm_api_key: str = ""
    llm_base_url: str = "https://integrate.api.nvidia.com/v1"
    llm_model: str = "openai/gpt-oss-20b"
    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    api_key: str = ""
    chat_rate_limit_per_minute: int = 10
    chat_max_length: int = 2000


@lru_cache
def get_settings() -> Settings:
    return Settings()
