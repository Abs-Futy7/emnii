from uuid import UUID, uuid4

import chromadb
import pytest

from app.core.exceptions import ExternalServiceError
from app.db.models import Client, Document, DocumentChunk
from app.domain.enums import (
    ClientStatus,
    DocumentFileType,
    DocumentIndexingStatus,
    DocumentStatus,
)
from app.services.rag.embeddings import EmbeddingProvider
from app.services.rag.indexing import DocumentIndexingService
from app.services.rag.vector_store import (
    ChromaVectorStore,
    VectorQueryResult,
    VectorRecord,
    VectorStore,
)
from tests.conftest import ApiTestContext

pytestmark = pytest.mark.anyio


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    @property
    def model_name(self) -> str:
        return "test-embedding-model"

    def embed_text(self, text: str) -> list[float]:
        return [float(len(text)), 1.0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[float(index + 1), 1.0] for index, _ in enumerate(texts)]


class FakeVectorStore(VectorStore):
    def __init__(self, fail_add: bool = False) -> None:
        self.records: dict[str, VectorRecord] = {}
        self.delete_calls: list[tuple[UUID, UUID, UUID]] = []
        self.fail_add = fail_add

    def add(self, records: list[VectorRecord]) -> None:
        if self.fail_add:
            raise RuntimeError("vector write failed")
        self.records.update({record.id: record for record in records})

    def query(
        self,
        embedding: list[float],
        *,
        organization_id: UUID,
        client_id: UUID,
        limit: int = 10,
    ) -> list[VectorQueryResult]:
        del embedding
        return [
            VectorQueryResult(record.id, record.document, record.metadata, 0.0)
            for record in self.records.values()
            if record.metadata["organization_id"] == str(organization_id)
            and record.metadata["client_id"] == str(client_id)
        ][:limit]

    def delete_document(
        self, organization_id: UUID, client_id: UUID, document_id: UUID
    ) -> None:
        self.delete_calls.append((organization_id, client_id, document_id))
        self.records = {
            record_id: record
            for record_id, record in self.records.items()
            if not (
                record.metadata["organization_id"] == str(organization_id)
                and record.metadata["client_id"] == str(client_id)
                and record.metadata["document_id"] == str(document_id)
            )
        }

    def health_check(self) -> dict[str, str | int | bool]:
        return {"healthy": True, "records": len(self.records)}


def create_processed_document(
    context: ApiTestContext,
) -> tuple[UUID, UUID, UUID, UUID]:
    identity = context.create_identity(
        email=f"index-{uuid4()}@example.com",
        organization_name="Index Org",
        organization_slug=f"index-{uuid4().hex}",
    )
    with context.session_factory() as session:
        client = Client(
            organization_id=identity.organization.id,
            name="Index Client",
            slug=f"index-client-{uuid4().hex}",
            status=ClientStatus.ACTIVE,
        )
        session.add(client)
        session.flush()
        document = Document(
            organization_id=identity.organization.id,
            client_id=client.id,
            uploaded_by=identity.user.id,
            original_filename="knowledge.txt",
            stored_filename=f"{uuid4().hex}.txt",
            file_type=DocumentFileType.TXT,
            mime_type="text/plain",
            file_size=100,
            status=DocumentStatus.PROCESSED,
            extracted_text_length=42,
            chunks=[
                DocumentChunk(
                    organization_id=identity.organization.id,
                    client_id=client.id,
                    chunk_index=0,
                    content="Refunds are available within thirty days.",
                    metadata_={},
                ),
                DocumentChunk(
                    organization_id=identity.organization.id,
                    client_id=client.id,
                    chunk_index=1,
                    content="Shipping replacements require an order identifier.",
                    metadata_={},
                ),
            ],
        )
        session.add(document)
        session.commit()
        return identity.organization.id, client.id, document.id, identity.user.id


async def test_indexing_batches_embeddings_and_reindex_does_not_duplicate(
    api_context: ApiTestContext,
) -> None:
    organization_id, client_id, document_id, actor_id = create_processed_document(
        api_context
    )
    embeddings = FakeEmbeddingProvider()
    vectors = FakeVectorStore()

    with api_context.session_factory() as session:
        service = DocumentIndexingService(session, embeddings, vectors)
        indexed = service.index(organization_id, client_id, document_id, actor_id)
        assert indexed.indexing_status == DocumentIndexingStatus.INDEXED
        assert indexed.embedding_model == "test-embedding-model"
        assert indexed.indexed_at is not None
        assert len(embeddings.calls) == 1
        assert len(embeddings.calls[0]) == 2
        assert len(vectors.records) == 2
        assert all(
            record.metadata["organization_id"] == str(organization_id)
            and record.metadata["client_id"] == str(client_id)
            and record.metadata["document_id"] == str(document_id)
            for record in vectors.records.values()
        )

        service.index(organization_id, client_id, document_id, actor_id)
        assert len(embeddings.calls) == 2
        assert len(vectors.records) == 2
        assert len(vectors.delete_calls) == 2


async def test_partial_vector_failure_is_cleaned_and_recorded(
    api_context: ApiTestContext,
) -> None:
    organization_id, client_id, document_id, actor_id = create_processed_document(
        api_context
    )
    vectors = FakeVectorStore(fail_add=True)
    with api_context.session_factory() as session:
        service = DocumentIndexingService(session, FakeEmbeddingProvider(), vectors)
        with pytest.raises(ExternalServiceError):
            service.index(organization_id, client_id, document_id, actor_id)
        document = session.get(Document, document_id)
        assert document is not None
        assert document.indexing_status == DocumentIndexingStatus.FAILED
        assert len(vectors.delete_calls) == 2
        assert vectors.records == {}


async def test_chroma_query_filters_tenants_before_retrieval() -> None:
    organization_a, organization_b = uuid4(), uuid4()
    client_a, client_b = uuid4(), uuid4()
    document_a, document_b = uuid4(), uuid4()
    store = ChromaVectorStore(
        collection_name="tenant-filter-test",
        client=chromadb.EphemeralClient(),
    )
    store.add(
        [
            VectorRecord(
                id="tenant-a-chunk",
                embedding=[1.0, 0.0],
                document="Tenant A private refund policy",
                metadata={
                    "organization_id": str(organization_a),
                    "client_id": str(client_a),
                    "document_id": str(document_a),
                    "chunk_id": "tenant-a-chunk",
                    "chunk_index": 0,
                    "source_filename": "a.txt",
                },
            ),
            VectorRecord(
                id="tenant-b-chunk",
                embedding=[1.0, 0.0],
                document="Tenant B private refund policy",
                metadata={
                    "organization_id": str(organization_b),
                    "client_id": str(client_b),
                    "document_id": str(document_b),
                    "chunk_id": "tenant-b-chunk",
                    "chunk_index": 0,
                    "source_filename": "b.txt",
                },
            ),
        ]
    )

    results = store.query(
        [1.0, 0.0],
        organization_id=organization_a,
        client_id=client_a,
        limit=10,
    )

    assert [result.id for result in results] == ["tenant-a-chunk"]
    assert all(
        result.metadata["organization_id"] == str(organization_a)
        and result.metadata["client_id"] == str(client_a)
        for result in results
    )
