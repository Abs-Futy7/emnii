from datetime import datetime
from uuid import UUID

from app.domain.enums import PIIScanStatus, PIIType
from app.schemas.base import ORMModel


class PIIFindingRead(ORMModel):
    id: UUID
    column_name: str
    pii_type: PIIType
    count: int
    confidence: float
    method: str
    sample_redacted_values: list[str]


class PIIScanRead(ORMModel):
    id: UUID
    organization_id: UUID
    client_id: UUID
    dataset_id: UUID
    status: PIIScanStatus
    findings_count: int
    created_at: datetime
    completed_at: datetime | None
    findings: list[PIIFindingRead]
