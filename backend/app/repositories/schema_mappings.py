from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CanonicalField, SchemaMapping
from app.domain.canonical_schema import CANONICAL_FIELDS


class SchemaMappingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ensure_canonical_fields(self) -> dict[str, CanonicalField]:
        existing = {
            field.name: field
            for field in self.session.scalars(select(CanonicalField)).all()
        }
        for definition in CANONICAL_FIELDS:
            if definition.name not in existing:
                field = CanonicalField(
                    name=definition.name,
                    data_type=definition.data_type,
                    description=definition.description or None,
                )
                self.session.add(field)
                existing[definition.name] = field
        self.session.flush()
        return existing

    def list_for_dataset(self, dataset_id: UUID) -> list[SchemaMapping]:
        statement = (
            select(SchemaMapping)
            .where(SchemaMapping.dataset_id == dataset_id)
            .order_by(SchemaMapping.source_column)
        )
        return list(self.session.scalars(statement))

    def by_source(self, dataset_id: UUID) -> dict[str, SchemaMapping]:
        return {
            mapping.source_column: mapping
            for mapping in self.list_for_dataset(dataset_id)
        }

    def add_all(self, mappings: Iterable[SchemaMapping]) -> None:
        self.session.add_all(mappings)
