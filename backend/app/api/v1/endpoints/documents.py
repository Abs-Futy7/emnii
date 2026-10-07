from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status

from app.api.deps import (
    CurrentOrganization,
    CurrentUser,
    DatabaseSession,
    SettingsDep,
    require_role,
)
from app.db.models import OrganizationMembership
from app.domain.enums import OrganizationRole
from app.schemas.document import DocumentDetail, DocumentListResponse, DocumentRead
from app.schemas.pagination import PaginationMeta
from app.services.documents import DocumentService
from app.services.rag.providers import get_vector_store

router = APIRouter(prefix="/clients/{client_id}/documents")

DocumentUploadAccess = Annotated[
    OrganizationMembership,
    Depends(
        require_role(
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
            OrganizationRole.AGENT,
        )
    ),
]
DocumentDeleteAccess = Annotated[
    OrganizationMembership,
    Depends(require_role(OrganizationRole.OWNER, OrganizationRole.ADMIN)),
]


def get_document_service(db: DatabaseSession, settings: SettingsDep) -> DocumentService:
    return DocumentService(db, settings, get_vector_store(settings))


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


@router.post("", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
async def upload_document(
    client_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: DocumentUploadAccess,
    service: DocumentServiceDep,
    file: Annotated[UploadFile, File(description="PDF, DOCX, TXT, or Markdown")],
) -> DocumentDetail:
    document = await service.upload(organization.id, client_id, user.id, file)
    return DocumentDetail.model_validate(document)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    client_id: UUID,
    organization: CurrentOrganization,
    service: DocumentServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> DocumentListResponse:
    result = service.list(organization.id, client_id, page=page, page_size=page_size)
    return DocumentListResponse(
        items=[DocumentRead.model_validate(document) for document in result.items],
        pagination=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
            total_pages=result.total_pages,
        ),
    )


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    client_id: UUID,
    document_id: UUID,
    organization: CurrentOrganization,
    service: DocumentServiceDep,
) -> DocumentDetail:
    return DocumentDetail.model_validate(
        service.get(organization.id, client_id, document_id)
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    client_id: UUID,
    document_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: DocumentDeleteAccess,
    service: DocumentServiceDep,
) -> Response:
    service.delete(organization.id, client_id, document_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
