from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.enums import DatasetFileType, DatasetStatus
from app.schemas.base import ORMModel
from app.schemas.pagination import PaginationMeta


class DatasetColumnRead(ORMModel):
    id: UUID
    source_name: str
    detected_type: str
    sample_values: list[Any]
    null_count: int
    unique_count: int
    created_at: datetime


class DatasetRead(ORMModel):
    id: UUID
    organization_id: UUID
    client_id: UUID
    original_filename: str
    file_type: DatasetFileType
    file_size: int
    row_count: int
    column_count: int
    status: DatasetStatus
    uploaded_by: UUID | None
    created_at: datetime
    updated_at: datetime


class DatasetDetail(DatasetRead):
    columns: list[DatasetColumnRead]


class DatasetListResponse(ORMModel):
    items: list[DatasetRead]
    pagination: PaginationMeta
