from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.domain.enums import (
    DocumentFileType,
    DocumentIndexingStatus,
    DocumentStatus,
)
from app.schemas.base import ORMModel
from app.schemas.pagination import PaginationMeta


class DocumentChunkRead(ORMModel):
    id: UUID
    chunk_index: int
    content: str
    token_count: int | None
    page_number: int | None
    metadata: dict[str, Any] = Field(validation_alias="metadata_")
    created_at: datetime


class DocumentRead(ORMModel):
    id: UUID
    organization_id: UUID
    client_id: UUID
    uploaded_by: UUID | None
    original_filename: str
    file_type: DocumentFileType
    mime_type: str
    file_size: int
    status: DocumentStatus
    title: str | None
    extracted_text_length: int
    page_count: int | None
    indexing_status: DocumentIndexingStatus
    indexed_at: datetime | None
    embedding_model: str | None
    created_at: datetime
    updated_at: datetime


class DocumentDetail(DocumentRead):
    chunks: list[DocumentChunkRead]


class DocumentListResponse(ORMModel):
    items: list[DocumentRead]
    pagination: PaginationMeta
