import re
import unicodedata
from dataclasses import dataclass
from uuid import UUID

import pandas as pd
from rapidfuzz.fuzz import ratio
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidUploadError, NotFoundError
from app.db.models import SchemaMapping
from app.domain.canonical_schema import CANONICAL_FIELDS
from app.domain.enums import MappingStatus
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.datasets import DatasetRepository
from app.repositories.schema_mappings import SchemaMappingRepository
from app.schemas.schema_mapping import SchemaMappingUpdate

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN = re.compile(r"^\+?[\d\s().-]{7,25}$")
AUTO_MAP_THRESHOLD = 0.72


def normalize_source_name(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    )
    with_word_boundaries = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", ascii_value)
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", with_word_boundaries).strip("_")
    return re.sub(r"_+", "_", normalized).lower()


@dataclass(frozen=True)
class MappingSuggestion:
    target_field: str | None
    confidence: float
    method: str


class DeterministicMappingEngine:
    def suggest(
        self, source_name: str, sample_values: list[object]
    ) -> MappingSuggestion:
        normalized = normalize_source_name(source_name)
        if not normalized:
            return MappingSuggestion(None, 0.0, "unresolved")

        for field in CANONICAL_FIELDS:
            if normalized == field.name:
                return MappingSuggestion(field.name, 1.0, "exact")
            if normalized in field.aliases:
                return MappingSuggestion(field.name, 0.94, "alias")

        best_field: str | None = None
        best_score = 0.0
        best_method = "unresolved"
        for field in CANONICAL_FIELDS:
            canonical_similarity = ratio(normalized, field.name) / 100
            alias_similarity = max(
                (ratio(normalized, alias) / 100 for alias in field.aliases),
                default=0.0,
            )
            if alias_similarity > canonical_similarity:
                lexical_score = alias_similarity * 0.90
                method = "alias+fuzzy"
            else:
                lexical_score = canonical_similarity * 0.88
                method = "fuzzy"

            value_score = self._value_evidence(field.data_type, sample_values)
            if value_score is None:
                score = lexical_score
            else:
                score = (0.65 * lexical_score) + (0.35 * value_score)
                method = f"{method}+values"

            if score > best_score:
                best_field = field.name
                best_score = score
                best_method = method

        rounded_score = round(min(best_score, 1.0), 4)
        if rounded_score < AUTO_MAP_THRESHOLD:
            return MappingSuggestion(None, rounded_score, "unresolved")
        return MappingSuggestion(best_field, rounded_score, best_method)

    @staticmethod
    def _value_evidence(data_type: str, values: list[object]) -> float | None:
        observed = [str(value).strip() for value in values if str(value).strip()]
        if not observed or data_type not in {"email", "phone", "datetime"}:
            return None
        if data_type == "email":
            valid = sum(bool(EMAIL_PATTERN.fullmatch(value)) for value in observed)
        elif data_type == "phone":
            valid = sum(
                bool(PHONE_PATTERN.fullmatch(value))
                and 7 <= len(re.sub(r"\D", "", value)) <= 15
                for value in observed
            )
        else:
            valid = sum(
                not pd.isna(pd.to_datetime(value, errors="coerce"))
                for value in observed
            )
        return valid / len(observed)


class SchemaMappingService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.datasets = DatasetRepository(session)
        self.mappings = SchemaMappingRepository(session)
        self.audit_logs = AuditLogRepository(session)
        self.engine = DeterministicMappingEngine()

    def detect(
        self, organization_id: UUID, client_id: UUID, dataset_id: UUID, actor_id: UUID
    ) -> list[SchemaMapping]:
        dataset = self.datasets.get(organization_id, client_id, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found")
        self.mappings.ensure_canonical_fields()
        existing = self.mappings.by_source(dataset.id)
        created: list[SchemaMapping] = []
        for column in dataset.columns:
            current = existing.get(column.source_name)
            if current is not None and current.manually_overridden:
                continue
            suggestion = self.engine.suggest(column.source_name, column.sample_values)
            if current is None:
                current = SchemaMapping(
                    dataset_id=dataset.id, source_column=column.source_name
                )
                created.append(current)
            current.target_field = suggestion.target_field
            current.confidence = suggestion.confidence
            current.method = suggestion.method
            current.status = MappingStatus.SUGGESTED
            current.manually_overridden = False
        self.mappings.add_all(created)
        self.audit_logs.add(
            organization_id=organization_id,
            user_id=actor_id,
            client_id=client_id,
            action="schema.detected",
            resource_type="dataset",
            resource_id=dataset_id,
            metadata={"column_count": len(dataset.columns)},
        )
        self.session.commit()
        return self.mappings.list_for_dataset(dataset.id)

    def get(
        self, organization_id: UUID, client_id: UUID, dataset_id: UUID
    ) -> list[SchemaMapping]:
        if self.datasets.get(organization_id, client_id, dataset_id) is None:
            raise NotFoundError("Dataset not found")
        return self.mappings.list_for_dataset(dataset_id)

    def update(
        self,
        organization_id: UUID,
        client_id: UUID,
        dataset_id: UUID,
        actor_id: UUID,
        payload: SchemaMappingUpdate,
    ) -> list[SchemaMapping]:
        dataset = self.datasets.get(organization_id, client_id, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found")
        canonical = self.mappings.ensure_canonical_fields()
        existing = self.mappings.by_source(dataset_id)
        dataset_columns = {column.source_name for column in dataset.columns}
        requested_sources = [item.source_column for item in payload.mappings]
        if len(requested_sources) != len(set(requested_sources)):
            raise InvalidUploadError("Each source column may only be updated once")

        for override in payload.mappings:
            if override.source_column not in dataset_columns:
                raise InvalidUploadError(
                    f"Unknown source column: {override.source_column}"
                )
            if (
                override.target_field is not None
                and override.target_field not in canonical
            ):
                raise InvalidUploadError(
                    f"Unknown canonical field: {override.target_field}"
                )
            mapping = existing.get(override.source_column)
            if mapping is None:
                mapping = SchemaMapping(
                    dataset_id=dataset_id,
                    source_column=override.source_column,
                    confidence=1.0,
                    method="manual",
                )
                self.session.add(mapping)
            mapping.target_field = override.target_field
            mapping.confidence = 1.0
            mapping.method = "manual"
            mapping.status = override.status
            mapping.manually_overridden = True

        self.audit_logs.add(
            organization_id=organization_id,
            user_id=actor_id,
            client_id=client_id,
            action="schema.updated",
            resource_type="dataset",
            resource_id=dataset_id,
            metadata={"updated_columns": sorted(requested_sources)},
        )
        self.session.commit()
        return self.mappings.list_for_dataset(dataset_id)
