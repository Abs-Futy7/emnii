from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

type VectorMetadataValue = str | int | float | bool


@dataclass(frozen=True)
class VectorRecord:
    id: str
    embedding: list[float]
    document: str
    metadata: dict[str, VectorMetadataValue]


@dataclass(frozen=True)
class VectorQueryResult:
    id: str
    document: str
    metadata: dict[str, VectorMetadataValue]
    distance: float | None


class VectorStore(ABC):
    @abstractmethod
    def add(self, records: list[VectorRecord]) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        embedding: list[float],
        *,
        organization_id: UUID,
        client_id: UUID,
        limit: int = 10,
    ) -> list[VectorQueryResult]:
        raise NotImplementedError

    @abstractmethod
    def delete_document(
        self, organization_id: UUID, client_id: UUID, document_id: UUID
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> dict[str, str | int | bool]:
        raise NotImplementedError
