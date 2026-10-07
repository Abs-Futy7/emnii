from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/resolveops"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ResolveOps"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = DEFAULT_DATABASE_URL
    frontend_url: str = "http://localhost:3000"

    jwt_secret: str = ""
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = 30

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""
    chroma_host: str = ""
    chroma_port: int | None = None
    chroma_ssl: bool = False
    chroma_persist_dir: Path = Path("./storage/chroma")
    chroma_collection: str = "resolveops_document_chunks"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    retrieval_default_top_k: int = 5
    retrieval_max_top_k: int = 20

    upload_dir: Path = Path("./storage/uploads")
    max_upload_size_mb: int = 25
    dataset_max_rows: int = 250_000
    dataset_sample_size: int = 5

    document_upload_dir: Path = Path("./storage/documents")
    max_document_upload_size_mb: int = 25
    document_chunk_size: int = 1_000
    document_chunk_overlap: int = 150

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_value(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev"}:
                return True
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def use_local_database_when_empty(cls, value: object) -> object:
        return value or DEFAULT_DATABASE_URL

    @field_validator("chroma_port", mode="before")
    @classmethod
    def empty_port_is_none(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator(
        "max_document_upload_size_mb",
        "document_chunk_size",
        "embedding_batch_size",
        "retrieval_default_top_k",
        "retrieval_max_top_k",
    )
    @classmethod
    def positive_document_settings(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be positive")
        return value

    @model_validator(mode="after")
    def validate_document_chunk_overlap(self) -> Self:
        if not 0 <= self.document_chunk_overlap < self.document_chunk_size:
            raise ValueError(
                "DOCUMENT_CHUNK_OVERLAP must be nonnegative and smaller than "
                "DOCUMENT_CHUNK_SIZE"
            )
        if self.retrieval_default_top_k > self.retrieval_max_top_k:
            raise ValueError(
                "RETRIEVAL_DEFAULT_TOP_K cannot exceed RETRIEVAL_MAX_TOP_K"
            )
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_url]

    @property
    def docs_enabled(self) -> bool:
        return self.app_env != "production" or self.debug

    @property
    def log_level(self) -> str:
        return "DEBUG" if self.debug else "INFO"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def max_document_upload_size_bytes(self) -> int:
        return self.max_document_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
