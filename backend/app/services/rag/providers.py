from functools import lru_cache
from pathlib import Path

from app.core.config import Settings
from app.services.rag.embeddings import (
    EmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)
from app.services.rag.vector_store import ChromaVectorStore, VectorStore


@lru_cache
def _embedding_provider(model_name: str, batch_size: int) -> EmbeddingProvider:
    return SentenceTransformerEmbeddingProvider(model_name, batch_size)


@lru_cache
def _vector_store(
    collection: str,
    host: str,
    port: int | None,
    ssl: bool,
    persist_directory: str,
) -> VectorStore:
    return ChromaVectorStore(
        collection_name=collection,
        host=host,
        port=port,
        ssl=ssl,
        persist_directory=Path(persist_directory),
    )


def get_embedding_provider(settings: Settings) -> EmbeddingProvider:
    return _embedding_provider(settings.embedding_model, settings.embedding_batch_size)


def get_vector_store(settings: Settings) -> VectorStore:
    return _vector_store(
        settings.chroma_collection,
        settings.chroma_host,
        settings.chroma_port,
        settings.chroma_ssl,
        str(settings.chroma_persist_dir.expanduser().resolve()),
    )
