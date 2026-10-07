from time import perf_counter
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError, InvalidRequestError, NotFoundError
from app.core.logging import get_logger
from app.repositories.clients import ClientRepository
from app.services.rag.embeddings import EmbeddingProvider
from app.services.rag.retrieval.models import RetrievalResult, RetrievedChunk
from app.services.rag.vector_store import VectorQueryResult, VectorStore

logger = get_logger(__name__)


class SemanticRetrievalService:
    def __init__(
        self,
        session: Session,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        settings: Settings,
    ) -> None:
        self.clients = ClientRepository(session)
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.default_top_k = settings.retrieval_default_top_k
        self.max_top_k = settings.retrieval_max_top_k

    def search(
        self,
        organization_id: UUID,
        client_id: UUID,
        query: str,
        *,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> RetrievalResult:
        normalized_query = query.strip()
        if not normalized_query:
            raise InvalidRequestError("Search query must not be blank")

        limit = top_k if top_k is not None else self.default_top_k
        if limit < 1 or limit > self.max_top_k:
            raise InvalidRequestError(
                f"top_k must be between 1 and {self.max_top_k}"
            )
        if score_threshold is not None and not 0 <= score_threshold <= 1:
            raise InvalidRequestError("score_threshold must be between 0 and 1")
        if self.clients.get(organization_id, client_id) is None:
            raise NotFoundError("Client not found")

        embedding_started = perf_counter()
        try:
            query_embedding = self.embedding_provider.embed_text(normalized_query)
        except Exception as exc:
            logger.exception(
                "Query embedding failed organization_id=%s client_id=%s",
                organization_id,
                client_id,
            )
            raise ExternalServiceError("Could not create the search embedding") from exc
        embedding_ms = (perf_counter() - embedding_started) * 1000

        search_started = perf_counter()
        try:
            vector_results = self.vector_store.query(
                query_embedding,
                organization_id=organization_id,
                client_id=client_id,
                limit=limit,
            )
        except Exception as exc:
            logger.exception(
                "Vector search failed organization_id=%s client_id=%s",
                organization_id,
                client_id,
            )
            raise ExternalServiceError(
                "Semantic search is currently unavailable"
            ) from exc
        vector_search_ms = (perf_counter() - search_started) * 1000

        results = [
            chunk
            for item in vector_results
            if (chunk := self._to_retrieved_chunk(item, organization_id, client_id))
            is not None
            and (score_threshold is None or chunk.score >= score_threshold)
        ]
        logger.info(
            "Semantic retrieval completed organization_id=%s client_id=%s "
            "query_embedding_ms=%.2f vector_search_ms=%.2f result_count=%s top_k=%s",
            organization_id,
            client_id,
            embedding_ms,
            vector_search_ms,
            len(results),
            limit,
        )
        return RetrievalResult(query=normalized_query, results=results)

    @staticmethod
    def _to_retrieved_chunk(
        item: VectorQueryResult,
        organization_id: UUID,
        client_id: UUID,
    ) -> RetrievedChunk | None:
        metadata = item.metadata
        if (
            metadata.get("organization_id") != str(organization_id)
            or metadata.get("client_id") != str(client_id)
            or item.distance is None
        ):
            return None
        try:
            chunk_id = UUID(str(metadata["chunk_id"]))
            document_id = UUID(str(metadata["document_id"]))
            source_filename = str(metadata["source_filename"])
            page_value = metadata.get("page_number")
            page_number = int(page_value) if page_value is not None else None
        except (KeyError, TypeError, ValueError):
            logger.warning(
                "Ignoring vector result with invalid source metadata id=%s", item.id
            )
            return None

        # The collection uses cosine distance (1 - cosine similarity). Mapping
        # [-1, 1] cosine similarity onto [0, 1] creates a bounded ranking score;
        # it is intentionally not described as a probability.
        score = max(0.0, min(1.0, 1.0 - (float(item.distance) / 2.0)))
        return RetrievedChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            source_filename=source_filename,
            content=item.document,
            score=score,
            page_number=page_number,
        )

