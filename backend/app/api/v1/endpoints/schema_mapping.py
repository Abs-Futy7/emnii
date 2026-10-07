from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import CurrentOrganization, CurrentUser, DatabaseSession, require_role
from app.db.models import OrganizationMembership
from app.domain.enums import OrganizationRole
from app.schemas.schema_mapping import SchemaMappingRead, SchemaMappingUpdate
from app.services.schema_mapping import SchemaMappingService

router = APIRouter(prefix="/clients/{client_id}/datasets/{dataset_id}/schema")

SchemaWriteAccess = Annotated[
    OrganizationMembership,
    Depends(
        require_role(
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
            OrganizationRole.AGENT,
        )
    ),
]


def get_schema_mapping_service(db: DatabaseSession) -> SchemaMappingService:
    return SchemaMappingService(db)


SchemaMappingServiceDep = Annotated[
    SchemaMappingService, Depends(get_schema_mapping_service)
]


@router.post("/detect", response_model=list[SchemaMappingRead])
def detect_schema(
    client_id: UUID,
    dataset_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: SchemaWriteAccess,
    service: SchemaMappingServiceDep,
) -> list[SchemaMappingRead]:
    mappings = service.detect(organization.id, client_id, dataset_id, user.id)
    return [SchemaMappingRead.model_validate(mapping) for mapping in mappings]


@router.get("", response_model=list[SchemaMappingRead])
def get_schema(
    client_id: UUID,
    dataset_id: UUID,
    organization: CurrentOrganization,
    service: SchemaMappingServiceDep,
) -> list[SchemaMappingRead]:
    mappings = service.get(organization.id, client_id, dataset_id)
    return [SchemaMappingRead.model_validate(mapping) for mapping in mappings]


@router.put("", response_model=list[SchemaMappingRead])
def update_schema(
    client_id: UUID,
    dataset_id: UUID,
    payload: SchemaMappingUpdate,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: SchemaWriteAccess,
    service: SchemaMappingServiceDep,
) -> list[SchemaMappingRead]:
    mappings = service.update(
        organization.id,
        client_id,
        dataset_id,
        user.id,
        payload,
    )
    return [SchemaMappingRead.model_validate(mapping) for mapping in mappings]
