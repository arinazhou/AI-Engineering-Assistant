"""Environment and path configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
INDEXES_DIR = DATA_DIR / "indexes"
DEFAULT_SAMPLE_REPO = ROOT_DIR / "sample_repo"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    retrieval_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 150


def get_settings() -> Settings:
    return Settings()


def ensure_data_dirs() -> None:
    INDEXES_DIR.mkdir(parents=True, exist_ok=True)


def index_dir_for(repo_path: Path, name: str | None = None) -> Path:
    """Return the on-disk index directory for a given repo path."""
    ensure_data_dirs()
    label = name or repo_path.resolve().name
    return INDEXES_DIR / label
