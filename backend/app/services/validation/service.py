from datetime import UTC, datetime
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import ConflictError, InvalidUploadError, NotFoundError
from app.db.models import Dataset, ValidationIssue, ValidationRun
from app.domain.canonical_schema import CANONICAL_FIELD_BY_NAME
from app.domain.enums import (
    DatasetStatus,
    MappingStatus,
    ValidationSeverity,
    ValidationStatus,
)
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.datasets import DatasetRepository
from app.repositories.schema_mappings import SchemaMappingRepository
from app.repositories.validations import ValidationRepository
from app.services.dataset_frames import DatasetFrameLoader
from app.services.ingestion.parsers.base import DatasetParseError
from app.services.validation.rules import (
    DateParseRule,
    DuplicateRule,
    EmailFormatRule,
    PhoneFormatRule,
    RequiredFieldRule,
    TypeRule,
    UniqueFieldRule,
    UnknownColumnRule,
    ValidationContext,
    ValidationResult,
    ValidationRule,
)

COMPLETENESS_WEIGHT = 0.30
VALIDITY_WEIGHT = 0.30
UNIQUENESS_WEIGHT = 0.25
CONSISTENCY_WEIGHT = 0.15


class ValidationService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.datasets = DatasetRepository(session)
        self.mappings = SchemaMappingRepository(session)
        self.validations = ValidationRepository(session)
        self.audit_logs = AuditLogRepository(session)
        self.frame_loader = DatasetFrameLoader(settings)

    def validate(
        self,
        organization_id: UUID,
        client_id: UUID,
        dataset_id: UUID,
        actor_id: UUID,
    ) -> ValidationRun:
        dataset = self.datasets.get(organization_id, client_id, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found")

        run = ValidationRun(
            organization_id=organization_id,
            client_id=client_id,
            dataset_id=dataset_id,
            status=ValidationStatus.PROCESSING,
        )
        self.validations.add(run)
        self.session.commit()

        try:
            dataframe = self.frame_loader.load(dataset).reset_index(drop=True)
            results, dimensions = self._run_rules(dataframe, dataset)
            total_records = len(dataframe.index)
            error_rows = set().union(
                *(
                    result.affected_rows
                    for result in results
                    if result.severity == ValidationSeverity.ERROR
                )
            )
            run.total_records = total_records
            run.valid_records = max(total_records - len(error_rows), 0)
            run.warning_count = sum(
                result.affected_count
                for result in results
                if result.severity == ValidationSeverity.WARNING
            )
            run.error_count = sum(
                result.affected_count
                for result in results
                if result.severity == ValidationSeverity.ERROR
            )
            run.completeness_score = dimensions["completeness"]
            run.validity_score = dimensions["validity"]
            run.uniqueness_score = dimensions["uniqueness"]
            run.consistency_score = dimensions["consistency"]
            run.quality_score = round(
                (dimensions["completeness"] * COMPLETENESS_WEIGHT)
                + (dimensions["validity"] * VALIDITY_WEIGHT)
                + (dimensions["uniqueness"] * UNIQUENESS_WEIGHT)
                + (dimensions["consistency"] * CONSISTENCY_WEIGHT),
                2,
            )
            run.status = ValidationStatus.COMPLETED
            run.completed_at = datetime.now(UTC)
            run.issues = [
                ValidationIssue(
                    rule=result.rule,
                    severity=result.severity,
                    field=result.field,
                    message=result.message,
                    affected_count=result.affected_count,
                    affected_percentage=round(
                        (result.affected_count / total_records * 100)
                        if total_records
                        else 0,
                        2,
                    ),
                    example_rows=list(result.examples),
                )
                for result in results
            ]
            dataset.status = DatasetStatus.VALIDATED
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=actor_id,
                client_id=client_id,
                action="dataset.validated",
                resource_type="validation_run",
                resource_id=run.id,
                metadata={
                    "dataset_id": str(dataset_id),
                    "quality_score": run.quality_score,
                    "issue_count": len(results),
                },
            )
            self.session.commit()
        except DatasetParseError as exc:
            run.status = ValidationStatus.FAILED
            run.completed_at = datetime.now(UTC)
            self.session.commit()
            raise InvalidUploadError("Stored dataset could not be parsed") from exc

        return self.validations.latest(organization_id, client_id, dataset_id) or run

    def latest(
        self, organization_id: UUID, client_id: UUID, dataset_id: UUID
    ) -> ValidationRun:
        if self.datasets.get(organization_id, client_id, dataset_id) is None:
            raise NotFoundError("Dataset not found")
        run = self.validations.latest(organization_id, client_id, dataset_id)
        if run is None:
            raise NotFoundError("No validation run found")
        return run

    def _run_rules(
        self, dataframe: pd.DataFrame, dataset: Dataset
    ) -> tuple[list[ValidationResult], dict[str, float]]:
        mappings = self.mappings.list_for_dataset(dataset.id)
        if not mappings:
            raise ConflictError("Run schema detection before validating this dataset")
        active = [
            mapping
            for mapping in mappings
            if mapping.target_field is not None
            and mapping.status not in {MappingStatus.REJECTED, MappingStatus.IGNORED}
        ]
        active.sort(
            key=lambda mapping: (
                mapping.status == MappingStatus.APPROVED,
                mapping.manually_overridden,
                mapping.confidence,
            )
        )
        field_sources = {
            mapping.target_field: mapping.source_column for mapping in active
        }
        handled_sources = {
            mapping.source_column
            for mapping in mappings
            if mapping.status == MappingStatus.IGNORED
            or mapping.target_field is not None
        }
        context = ValidationContext(
            field_sources=field_sources,
            unknown_columns=tuple(
                str(column)
                for column in dataframe.columns
                if str(column) not in handled_sources
            ),
        )

        completeness_rules: list[ValidationRule] = [RequiredFieldRule("customer_id")]
        validity_rules: list[ValidationRule] = []
        if "email" in field_sources:
            validity_rules.append(EmailFormatRule())
        if "phone" in field_sources:
            validity_rules.append(PhoneFormatRule())
        if "created_at" in field_sources:
            validity_rules.append(DateParseRule("created_at"))
        validity_rules.extend(
            TypeRule(field, CANONICAL_FIELD_BY_NAME[field].data_type)
            for field in field_sources
            if field in CANONICAL_FIELD_BY_NAME
            and CANONICAL_FIELD_BY_NAME[field].data_type
            not in {"string", "email", "phone", "datetime"}
        )
        uniqueness_rules: list[ValidationRule] = [DuplicateRule()]
        if "customer_id" in field_sources:
            uniqueness_rules.append(UniqueFieldRule("customer_id"))
        consistency_rules: list[ValidationRule] = [UnknownColumnRule()]

        categorized_rules = {
            "completeness": completeness_rules,
            "validity": validity_rules,
            "uniqueness": uniqueness_rules,
            "consistency": consistency_rules,
        }
        categorized_results: dict[str, list[ValidationResult]] = {}
        all_results: list[ValidationResult] = []
        for dimension, rules in categorized_rules.items():
            dimension_results = [
                result for rule in rules for result in rule.validate(dataframe, context)
            ]
            categorized_results[dimension] = dimension_results
            all_results.extend(dimension_results)

        total = len(dataframe.index)
        dimensions = {
            "completeness": self._row_score(
                total, len(completeness_rules), categorized_results["completeness"]
            ),
            "validity": self._row_score(
                total, len(validity_rules), categorized_results["validity"]
            ),
            "uniqueness": self._row_score(
                total, len(uniqueness_rules), categorized_results["uniqueness"]
            ),
            "consistency": round(
                100
                * (
                    1
                    - (
                        len(context.unknown_columns) / len(dataframe.columns)
                        if len(dataframe.columns)
                        else 0
                    )
                ),
                2,
            ),
        }
        return all_results, dimensions

    @staticmethod
    def _row_score(
        total_rows: int,
        rule_count: int,
        results: list[ValidationResult],
    ) -> float:
        denominator = total_rows * rule_count
        if denominator == 0:
            return 100.0
        failures = min(sum(result.affected_count for result in results), denominator)
        return round(100 * (1 - failures / denominator), 2)
