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
from app.db.models import OrganizationMembership
from app.domain.enums import OrganizationRole
from app.schemas.document import DocumentDetail
from app.schemas.retrieval import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResult,
)
from app.services.rag.indexing import DocumentIndexingService
from app.services.rag.providers import get_embedding_provider, get_vector_store
from app.services.rag.retrieval import SemanticRetrievalService

router = APIRouter()

IndexAccess = Annotated[
    OrganizationMembership,
    Depends(
        require_role(
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
            OrganizationRole.AGENT,
        )
    ),
]


def get_indexing_service(
    db: DatabaseSession, settings: SettingsDep
) -> DocumentIndexingService:
    return DocumentIndexingService(
        db,
        get_embedding_provider(settings),
        get_vector_store(settings),
    )


IndexingServiceDep = Annotated[DocumentIndexingService, Depends(get_indexing_service)]


def get_retrieval_service(
    db: DatabaseSession, settings: SettingsDep
) -> SemanticRetrievalService:
    return SemanticRetrievalService(
        db,
        get_embedding_provider(settings),
        get_vector_store(settings),
        settings,
    )


RetrievalServiceDep = Annotated[
    SemanticRetrievalService,
    Depends(get_retrieval_service),
]


@router.post(
    "/clients/{client_id}/documents/{document_id}/index",
    response_model=DocumentDetail,
)
def index_document(
    client_id: UUID,
    document_id: UUID,
    organization: CurrentOrganization,
    user: CurrentUser,
    _: IndexAccess,
    service: IndexingServiceDep,
) -> DocumentDetail:
    document = service.index(organization.id, client_id, document_id, user.id)
    return DocumentDetail.model_validate(document)


@router.post(
    "/clients/{client_id}/search",
    response_model=SemanticSearchResponse,
)
def semantic_search(
    client_id: UUID,
    payload: SemanticSearchRequest,
    organization: CurrentOrganization,
    service: RetrievalServiceDep,
) -> SemanticSearchResponse:
    result = service.search(
        organization.id,
        client_id,
        payload.query,
        top_k=payload.top_k,
        score_threshold=payload.score_threshold,
    )
    return SemanticSearchResponse(
        query=result.query,
        results=[SemanticSearchResult(**vars(item)) for item in result.results],
    )


@router.get("/rag/health")
def rag_health(
    _: CurrentOrganization,
    settings: SettingsDep,
) -> dict[str, object]:
    return {
        "embedding_model": settings.embedding_model,
        "vector_store": get_vector_store(settings).health_check(),
    }
