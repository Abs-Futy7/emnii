from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import (
    CurrentOrganization,
    CurrentUser,
    DatabaseSession,
    require_role,
)
from app.db.models import OrganizationMembership
from app.domain.enums import ClientStatus, OrganizationRole
from app.schemas.client import (
    ClientCreate,
    ClientListResponse,
    ClientRead,
    ClientUpdate,
)
from app.schemas.pagination import PaginationMeta
from app.services.clients import ClientService

router = APIRouter(prefix="/clients")

ClientWriteAccess = Annotated[
    OrganizationMembership,
    Depends(require_role(OrganizationRole.OWNER, OrganizationRole.ADMIN)),
]


def get_client_service(db: DatabaseSession) -> ClientService:
    return ClientService(db)


ClientServiceDep = Annotated[ClientService, Depends(get_client_service)]


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: ClientWriteAccess,
    service: ClientServiceDep,
) -> ClientRead:
    return ClientRead.model_validate(service.create(organization.id, user.id, payload))


@router.get("", response_model=ClientListResponse)
def list_clients(
    organization: CurrentOrganization,
    service: ClientServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=255)] = None,
    client_status: Annotated[ClientStatus | None, Query(alias="status")] = None,
    industry: Annotated[str | None, Query(max_length=150)] = None,
) -> ClientListResponse:
    result = service.list(
        organization.id,
        page=page,
        page_size=page_size,
        search=search,
        status=client_status,
        industry=industry,
    )
    return ClientListResponse(
        items=[ClientRead.model_validate(client) for client in result.items],
        pagination=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
            total_pages=result.total_pages,
        ),
    )


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: UUID,
    organization: CurrentOrganization,
    service: ClientServiceDep,
) -> ClientRead:
    return ClientRead.model_validate(service.get(organization.id, client_id))


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: UUID,
    payload: ClientUpdate,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: ClientWriteAccess,
    service: ClientServiceDep,
) -> ClientRead:
    return ClientRead.model_validate(
        service.update(organization.id, user.id, client_id, payload)
    )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_client(
    client_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: ClientWriteAccess,
    service: ClientServiceDep,
) -> Response:
    service.disable(organization.id, user.id, client_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
