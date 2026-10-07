from pathlib import Path
from typing import Any
from uuid import UUID

from app.services.rag.vector_store.base import (
    VectorQueryResult,
    VectorRecord,
    VectorStore,
)


class ChromaVectorStore(VectorStore):
    def __init__(
        self,
        *,
        collection_name: str,
        host: str = "",
        port: int | None = None,
        ssl: bool = False,
        persist_directory: Path | None = None,
        client: Any | None = None,
    ) -> None:
        self.collection_name = collection_name
        self.host = host
        self.port = port or 8000
        self.ssl = ssl
        self.persist_directory = persist_directory or Path("./storage/chroma")
        self._client = client
        self._collection: Any | None = None

    def add(self, records: list[VectorRecord]) -> None:
        if not records:
            return
        collection = self._get_collection()
        max_batch = max(int(self._get_client().get_max_batch_size()), 1)
        for start in range(0, len(records), max_batch):
            batch = records[start : start + max_batch]
            collection.upsert(
                ids=[record.id for record in batch],
                embeddings=[record.embedding for record in batch],
                documents=[record.document for record in batch],
                metadatas=[record.metadata for record in batch],
            )

    def query(
        self,
        embedding: list[float],
        *,
        organization_id: UUID,
        client_id: UUID,
        limit: int = 10,
    ) -> list[VectorQueryResult]:
        tenant_filter = {
            "$and": [
                {"organization_id": {"$eq": str(organization_id)}},
                {"client_id": {"$eq": str(client_id)}},
            ]
        }
        result = self._get_collection().query(
            query_embeddings=[embedding],
            n_results=limit,
            where=tenant_filter,
            include=["documents", "metadatas", "distances"],
        )
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        return [
            VectorQueryResult(
                id=record_id,
                document=documents[index] or "",
                metadata=metadatas[index] or {},
                distance=distances[index] if index < len(distances) else None,
            )
            for index, record_id in enumerate(ids)
        ]

    def delete_document(
        self, organization_id: UUID, client_id: UUID, document_id: UUID
    ) -> None:
        self._get_collection().delete(
            where={
                "$and": [
                    {"organization_id": {"$eq": str(organization_id)}},
                    {"client_id": {"$eq": str(client_id)}},
                    {"document_id": {"$eq": str(document_id)}},
                ]
            }
        )

    def health_check(self) -> dict[str, str | int | bool]:
        try:
            heartbeat = self._get_client().heartbeat()
            count = self._get_collection().count()
        except Exception as exc:
            return {"healthy": False, "error": type(exc).__name__}
        return {"healthy": True, "heartbeat": int(heartbeat), "records": int(count)}

    def _get_client(self) -> Any:
        if self._client is None:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            chroma_settings = ChromaSettings(anonymized_telemetry=False)
            if self.host:
                self._client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    ssl=self.ssl,
                    settings=chroma_settings,
                )
            else:
                self.persist_directory.mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(
                    path=str(self.persist_directory.resolve()),
                    settings=chroma_settings,
                )
        return self._client

    def _get_collection(self) -> Any:
        if self._collection is None:
            self._collection = self._get_client().get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=None,
            )
        return self._collection
