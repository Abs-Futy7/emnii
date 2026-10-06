from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import AliasChoices, Field

from app.schemas.base import ORMModel


class AuditLogCreate(ORMModel):
    organization_id: UUID
    user_id: UUID | None = None
    client_id: UUID | None = None
    action: str = Field(min_length=1, max_length=100)
    resource_type: str = Field(min_length=1, max_length=100)
    resource_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogRead(AuditLogCreate):
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("metadata_", "metadata"),
    )
    id: UUID
    created_at: datetime
