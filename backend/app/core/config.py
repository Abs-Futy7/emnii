from functools import lru_cache
from typing import Literal

from pydantic import field_validator
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

    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_url]

    @property
    def docs_enabled(self) -> bool:
        return self.app_env != "production" or self.debug

    @property
    def log_level(self) -> str:
        return "DEBUG" if self.debug else "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
