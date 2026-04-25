from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Internal Knowledge Copilot API"
    database_url: str = "sqlite:///./knowledge_copilot.db"
    upload_dir: str = str(Path(__file__).resolve().parents[2] / "data" / "uploads")
    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieval_top_k: int = 4
    embedding_dimensions: int = 96

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
