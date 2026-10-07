from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.enums import ValidationSeverity, ValidationStatus
from app.schemas.base import ORMModel


class ValidationIssueRead(ORMModel):
    id: UUID
    rule: str
    severity: ValidationSeverity
    field: str | None
    message: str
    affected_count: int
    affected_percentage: float
    example_rows: list[dict[str, Any]]


class QualityDimensions(ORMModel):
    completeness: float
    validity: float
    uniqueness: float
    consistency: float


class ValidationRunRead(ORMModel):
    id: UUID
    organization_id: UUID
    client_id: UUID
    dataset_id: UUID
    status: ValidationStatus
    total_records: int
    valid_records: int
    warning_count: int
    error_count: int
    quality_score: float
    dimensions: QualityDimensions
    started_at: datetime
    completed_at: datetime | None
    issues: list[ValidationIssueRead]
