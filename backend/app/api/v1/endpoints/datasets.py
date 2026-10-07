from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.deps import (
    CurrentOrganization,
    CurrentUser,
    DatabaseSession,
    SettingsDep,
    require_role,
)
from app.db.models import OrganizationMembership
from app.domain.enums import OrganizationRole
from app.schemas.dataset import DatasetDetail, DatasetListResponse, DatasetRead
from app.schemas.pagination import PaginationMeta
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/clients/{client_id}/datasets")

DatasetWriteAccess = Annotated[
    OrganizationMembership,
    Depends(
        require_role(
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
            OrganizationRole.AGENT,
        )
    ),
]


def get_ingestion_service(
    db: DatabaseSession,
    settings: SettingsDep,
) -> IngestionService:
    return IngestionService(db, settings)


IngestionServiceDep = Annotated[IngestionService, Depends(get_ingestion_service)]


@router.post("", response_model=DatasetDetail, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    client_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: DatasetWriteAccess,
    service: IngestionServiceDep,
    file: Annotated[UploadFile, File(description="CSV, JSON, or XLSX dataset")],
) -> DatasetDetail:
    dataset = await service.upload(organization.id, client_id, user.id, file)
    return DatasetDetail.model_validate(dataset)


@router.get("", response_model=DatasetListResponse)
def list_datasets(
    client_id: UUID,
    organization: CurrentOrganization,
    service: IngestionServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> DatasetListResponse:
    result = service.list(
        organization.id,
        client_id,
        page=page,
        page_size=page_size,
    )
    return DatasetListResponse(
        items=[DatasetRead.model_validate(dataset) for dataset in result.items],
        pagination=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
            total_pages=result.total_pages,
        ),
    )


@router.get("/{dataset_id}", response_model=DatasetDetail)
def get_dataset(
    client_id: UUID,
    dataset_id: UUID,
    organization: CurrentOrganization,
    service: IngestionServiceDep,
) -> DatasetDetail:
    dataset = service.get(organization.id, client_id, dataset_id)
    return DatasetDetail.model_validate(dataset)
