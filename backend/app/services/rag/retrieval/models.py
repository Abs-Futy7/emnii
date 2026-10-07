from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: UUID
    document_id: UUID
    source_filename: str
    content: str
    score: float
    page_number: int | None


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    results: list[RetrievedChunk]

