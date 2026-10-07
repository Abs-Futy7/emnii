from datetime import datetime
from uuid import UUID

from pydantic import Field, model_validator

from app.domain.enums import MappingStatus
from app.schemas.base import ORMModel


class SchemaMappingRead(ORMModel):
    id: UUID
    source_column: str
    suggested_field: str | None = Field(validation_alias="target_field")
    confidence: float
    method: str
    status: MappingStatus
    manually_overridden: bool
    created_at: datetime


class SchemaMappingOverride(ORMModel):
    source_column: str = Field(min_length=1, max_length=255)
    target_field: str | None = Field(default=None, max_length=100)
    status: MappingStatus

    @model_validator(mode="after")
    def validate_override(self) -> "SchemaMappingOverride":
        if self.status == MappingStatus.APPROVED and self.target_field is None:
            raise ValueError("approved mappings require a target_field")
        if self.status == MappingStatus.IGNORED and self.target_field is not None:
            raise ValueError("ignored mappings cannot have a target_field")
        return self


class SchemaMappingUpdate(ORMModel):
    mappings: list[SchemaMappingOverride] = Field(min_length=1)
