from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    CurrentOrganization,
    CurrentUser,
    DatabaseSession,
    SettingsDep,
    require_role,
)
from app.db.models import OrganizationMembership
from app.domain.enums import OrganizationRole
from app.schemas.pii import PIIScanRead
from app.services.pii import PIIService

router = APIRouter(prefix="/clients/{client_id}/datasets/{dataset_id}/pii")

PIIWriteAccess = Annotated[
    OrganizationMembership,
    Depends(
        require_role(
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
            OrganizationRole.AGENT,
        )
    ),
]


def get_pii_service(db: DatabaseSession, settings: SettingsDep) -> PIIService:
    return PIIService(db, settings)


PIIServiceDep = Annotated[PIIService, Depends(get_pii_service)]


@router.post("/scan", response_model=PIIScanRead, status_code=status.HTTP_201_CREATED)
def scan_dataset_for_pii(
    client_id: UUID,
    dataset_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: PIIWriteAccess,
    service: PIIServiceDep,
) -> PIIScanRead:
    return PIIScanRead.model_validate(
        service.scan(organization.id, client_id, dataset_id, user.id)
    )


@router.get("", response_model=PIIScanRead)
def get_latest_pii_scan(
    client_id: UUID,
    dataset_id: UUID,
    organization: CurrentOrganization,
    service: PIIServiceDep,
) -> PIIScanRead:
    return PIIScanRead.model_validate(
        service.latest(organization.id, client_id, dataset_id)
    )
