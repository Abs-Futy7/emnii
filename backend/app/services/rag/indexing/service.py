from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ExternalServiceError, NotFoundError
from app.db.models import Document
from app.domain.enums import DocumentIndexingStatus, DocumentStatus
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.documents import DocumentRepository
from app.services.rag.embeddings import EmbeddingProvider
from app.services.rag.vector_store import VectorRecord, VectorStore


class DocumentIndexingService:
    def __init__(
        self,
        session: Session,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.documents = DocumentRepository(session)
        self.audit_logs = AuditLogRepository(session)

    def index(
        self,
        organization_id: UUID,
        client_id: UUID,
        document_id: UUID,
        actor_id: UUID,
    ) -> Document:
        document = self.documents.get(organization_id, client_id, document_id)
        if document is None:
            raise NotFoundError("Document not found")
        if document.status != DocumentStatus.PROCESSED:
            raise ConflictError("Only successfully processed documents can be indexed")
        if not document.chunks:
            raise ConflictError("Document contains no chunks to index")

        document.indexing_status = DocumentIndexingStatus.INDEXING
        self.session.commit()
        replacement_started = False
        try:
            embeddings = self.embedding_provider.embed_texts(
                [chunk.content for chunk in document.chunks]
            )
            if len(embeddings) != len(document.chunks):
                raise ValueError("Embedding provider returned an unexpected batch size")
            records = [
                VectorRecord(
                    id=str(chunk.id),
                    embedding=embeddings[index],
                    document=chunk.content,
                    metadata={
                        "organization_id": str(organization_id),
                        "client_id": str(client_id),
                        "document_id": str(document.id),
                        "chunk_id": str(chunk.id),
                        "chunk_index": chunk.chunk_index,
                        "source_filename": document.original_filename,
                        **(
                            {"page_number": chunk.page_number}
                            if chunk.page_number is not None
                            else {}
                        ),
                    },
                )
                for index, chunk in enumerate(document.chunks)
            ]
            self.vector_store.delete_document(organization_id, client_id, document_id)
            replacement_started = True
            self.vector_store.add(records)
        except Exception as exc:
            if replacement_started:
                try:
                    self.vector_store.delete_document(
                        organization_id, client_id, document_id
                    )
                except Exception:
                    pass
            document.indexing_status = DocumentIndexingStatus.FAILED
            document.indexed_at = None
            document.embedding_model = self.embedding_provider.model_name
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=actor_id,
                client_id=client_id,
                action="document.indexing_failed",
                resource_type="document",
                resource_id=document_id,
                metadata={"error_type": type(exc).__name__},
            )
            self.session.commit()
            raise ExternalServiceError("Document indexing failed") from exc

        document.indexing_status = DocumentIndexingStatus.INDEXED
        document.indexed_at = datetime.now(UTC)
        document.embedding_model = self.embedding_provider.model_name
        self.audit_logs.add(
            organization_id=organization_id,
            user_id=actor_id,
            client_id=client_id,
            action="document.indexed",
            resource_type="document",
            resource_id=document_id,
            metadata={
                "embedding_model": self.embedding_provider.model_name,
                "chunk_count": len(document.chunks),
            },
        )
        self.session.commit()
        self.session.expire_all()
        return self.documents.get(organization_id, client_id, document_id) or document
