from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4_000)
    top_k: int | None = Field(default=None, ge=1)
    score_threshold: float | None = Field(default=None, ge=0, le=1)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query must not be blank")
        return value


class SemanticSearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    source_filename: str
    content: str
    score: float = Field(ge=0, le=1)
    page_number: int | None


class SemanticSearchResponse(BaseModel):
    query: str
    score_type: Literal["normalized_cosine_similarity"] = (
        "normalized_cosine_similarity"
    )
    results: list[SemanticSearchResult]

