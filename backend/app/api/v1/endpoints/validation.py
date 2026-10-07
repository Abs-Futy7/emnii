from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import (
    CurrentOrganization,
    CurrentUser,
    DatabaseSession,
    SettingsDep,
    require_role,
)
from app.db.models import OrganizationMembership, ValidationRun
from app.domain.enums import OrganizationRole
from app.schemas.validation import (
    QualityDimensions,
    ValidationIssueRead,
    ValidationRunRead,
)
from app.services.validation import ValidationService

router = APIRouter(prefix="/clients/{client_id}/datasets/{dataset_id}")

ValidationWriteAccess = Annotated[
    OrganizationMembership,
    Depends(
        require_role(
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
            OrganizationRole.AGENT,
        )
    ),
]


def get_validation_service(
    db: DatabaseSession, settings: SettingsDep
) -> ValidationService:
    return ValidationService(db, settings)


ValidationServiceDep = Annotated[ValidationService, Depends(get_validation_service)]


def serialize_run(run: ValidationRun) -> ValidationRunRead:
    return ValidationRunRead(
        id=run.id,
        organization_id=run.organization_id,
        client_id=run.client_id,
        dataset_id=run.dataset_id,
        status=run.status,
        total_records=run.total_records,
        valid_records=run.valid_records,
        warning_count=run.warning_count,
        error_count=run.error_count,
        quality_score=run.quality_score,
        dimensions=QualityDimensions(
            completeness=run.completeness_score,
            validity=run.validity_score,
            uniqueness=run.uniqueness_score,
            consistency=run.consistency_score,
        ),
        started_at=run.started_at,
        completed_at=run.completed_at,
        issues=[ValidationIssueRead.model_validate(issue) for issue in run.issues],
    )


@router.post("/validate", response_model=ValidationRunRead)
def validate_dataset(
    client_id: UUID,
    dataset_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: ValidationWriteAccess,
    service: ValidationServiceDep,
) -> ValidationRunRead:
    run = service.validate(organization.id, client_id, dataset_id, user.id)
    return serialize_run(run)


@router.get("/validation/latest", response_model=ValidationRunRead)
def get_latest_validation(
    client_id: UUID,
    dataset_id: UUID,
    organization: CurrentOrganization,
    service: ValidationServiceDep,
) -> ValidationRunRead:
    return serialize_run(service.latest(organization.id, client_id, dataset_id))
