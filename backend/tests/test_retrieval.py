from uuid import UUID, uuid4

import chromadb
import pytest

from app.core.config import Settings
from app.core.exceptions import InvalidRequestError, NotFoundError
from app.db.models import Client
from app.domain.enums import ClientStatus
from app.services.rag.embeddings import EmbeddingProvider
from app.services.rag.retrieval import SemanticRetrievalService
from app.services.rag.vector_store import ChromaVectorStore, VectorRecord
from tests.conftest import ApiTestContext

pytestmark = pytest.mark.anyio


class TopicEmbeddingProvider(EmbeddingProvider):
    @property
    def model_name(self) -> str:
        return "topic-test-model"

    def embed_text(self, text: str) -> list[float]:
        lowered = text.lower()
        if "refund" in lowered or "delayed" in lowered:
            return [1.0, 0.0]
        return [0.0, 1.0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]


def add_record(
    store: ChromaVectorStore,
    *,
    organization_id: UUID,
    client_id: UUID,
    content: str,
    embedding: list[float],
    filename: str,
) -> tuple[UUID, UUID]:
    chunk_id, document_id = uuid4(), uuid4()
    store.add(
        [
            VectorRecord(
                id=str(chunk_id),
                embedding=embedding,
                document=content,
                metadata={
                    "organization_id": str(organization_id),
                    "client_id": str(client_id),
                    "document_id": str(document_id),
                    "chunk_id": str(chunk_id),
                    "chunk_index": 0,
                    "source_filename": filename,
                    "page_number": 4,
                },
            )
        ]
    )
    return chunk_id, document_id


async def test_refund_search_ranks_relevant_text_and_excludes_other_client(
    api_context: ApiTestContext,
) -> None:
    identity = api_context.create_identity(
        email=f"retrieval-{uuid4()}@example.com",
        organization_name="Retrieval Org",
        organization_slug=f"retrieval-{uuid4().hex}",
    )
    with api_context.session_factory() as session:
        refund_client = Client(
            organization_id=identity.organization.id,
            name="Refund Client",
            slug=f"refund-{uuid4().hex}",
            status=ClientStatus.ACTIVE,
        )
        other_client = Client(
            organization_id=identity.organization.id,
            name="Other Client",
            slug=f"other-{uuid4().hex}",
            status=ClientStatus.ACTIVE,
        )
        session.add_all([refund_client, other_client])
        session.commit()

        store = ChromaVectorStore(
            collection_name=f"retrieval-{uuid4().hex}",
            client=chromadb.EphemeralClient(),
        )
        refund_chunk, _ = add_record(
            store,
            organization_id=identity.organization.id,
            client_id=refund_client.id,
            content="Delayed orders qualify for a refund after seven days.",
            embedding=[1.0, 0.0],
            filename="refund_policy.pdf",
        )
        unrelated_chunk, _ = add_record(
            store,
            organization_id=identity.organization.id,
            client_id=refund_client.id,
            content="The office cafeteria menu changes every Tuesday.",
            embedding=[0.0, 1.0],
            filename="office_notes.txt",
        )
        other_client_chunk, _ = add_record(
            store,
            organization_id=identity.organization.id,
            client_id=other_client.id,
            content="A private refund policy belonging to another client.",
            embedding=[1.0, 0.0],
            filename="private_policy.pdf",
        )

        service = SemanticRetrievalService(
            session,
            TopicEmbeddingProvider(),
            store,
            api_context.settings,
        )
        response = service.search(
            identity.organization.id,
            refund_client.id,
            "What is the refund policy for delayed orders?",
            top_k=5,
        )

        result_ids = [result.chunk_id for result in response.results]
        assert result_ids[0] == refund_chunk
        assert unrelated_chunk in result_ids
        assert other_client_chunk not in result_ids
        assert response.results[0].score > response.results[1].score
        assert response.results[0].source_filename == "refund_policy.pdf"
        assert response.results[0].page_number == 4


async def test_retrieval_threshold_and_top_k_limit(
    api_context: ApiTestContext,
) -> None:
    identity = api_context.create_identity(
        email=f"threshold-{uuid4()}@example.com",
        organization_name="Threshold Org",
        organization_slug=f"threshold-{uuid4().hex}",
    )
    with api_context.session_factory() as session:
        client = Client(
            organization_id=identity.organization.id,
            name="Threshold Client",
            slug=f"threshold-client-{uuid4().hex}",
            status=ClientStatus.ACTIVE,
        )
        session.add(client)
        session.commit()
        store = ChromaVectorStore(
            collection_name=f"threshold-{uuid4().hex}",
            client=chromadb.EphemeralClient(),
        )
        add_record(
            store,
            organization_id=identity.organization.id,
            client_id=client.id,
            content="Refund guidance.",
            embedding=[1.0, 0.0],
            filename="refund.md",
        )
        add_record(
            store,
            organization_id=identity.organization.id,
            client_id=client.id,
            content="Unrelated guidance.",
            embedding=[0.0, 1.0],
            filename="other.md",
        )
        settings = Settings(
            _env_file=None,
            jwt_secret="test-secret-at-least-32-characters-long",
            retrieval_default_top_k=1,
            retrieval_max_top_k=2,
        )
        service = SemanticRetrievalService(
            session, TopicEmbeddingProvider(), store, settings
        )

        filtered = service.search(
            identity.organization.id,
            client.id,
            "refund",
            score_threshold=0.75,
        )
        assert len(filtered.results) == 1
        assert filtered.results[0].source_filename == "refund.md"

        with pytest.raises(InvalidRequestError, match="top_k"):
            service.search(
                identity.organization.id,
                client.id,
                "refund",
                top_k=3,
            )


async def test_retrieval_does_not_expose_client_from_another_tenant(
    api_context: ApiTestContext,
) -> None:
    identity_a = api_context.create_identity(
        email=f"tenant-a-{uuid4()}@example.com",
        organization_name="Tenant A",
        organization_slug=f"tenant-a-{uuid4().hex}",
    )
    identity_b = api_context.create_identity(
        email=f"tenant-b-{uuid4()}@example.com",
        organization_name="Tenant B",
        organization_slug=f"tenant-b-{uuid4().hex}",
    )
    with api_context.session_factory() as session:
        client_b = Client(
            organization_id=identity_b.organization.id,
            name="Tenant B Client",
            slug=f"tenant-b-client-{uuid4().hex}",
            status=ClientStatus.ACTIVE,
        )
        session.add(client_b)
        session.commit()
        service = SemanticRetrievalService(
            session,
            TopicEmbeddingProvider(),
            ChromaVectorStore(
                collection_name=f"cross-tenant-{uuid4().hex}",
                client=chromadb.EphemeralClient(),
            ),
            api_context.settings,
        )

        with pytest.raises(NotFoundError, match="Client not found"):
            service.search(
                identity_a.organization.id,
                client_b.id,
                "refund",
            )


async def test_search_endpoint_rejects_blank_query(
    api_context: ApiTestContext,
) -> None:
    identity = api_context.create_identity(
        email=f"blank-query-{uuid4()}@example.com",
        organization_name="Blank Query Org",
        organization_slug=f"blank-query-{uuid4().hex}",
    )
    response = await api_context.client.post(
        f"/api/v1/clients/{uuid4()}/search",
        headers={"Authorization": f"Bearer {identity.token}"},
        json={"query": "   ", "top_k": 5},
    )

    assert response.status_code == 422

