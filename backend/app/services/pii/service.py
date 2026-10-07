from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import InvalidUploadError, NotFoundError
from app.db.models import PIIFinding, PIIScan
from app.domain.enums import MappingStatus, PIIScanStatus, PIIType
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.datasets import DatasetRepository
from app.repositories.pii import PIIRepository
from app.repositories.schema_mappings import SchemaMappingRepository
from app.services.dataset_frames import DatasetFrameLoader
from app.services.ingestion.parsers.base import DatasetParseError
from app.services.pii.scanner import PIIScanner

SCHEMA_PII_FIELDS = {
    "customer_name": PIIType.PERSON_NAME,
    "first_name": PIIType.PERSON_NAME,
    "last_name": PIIType.PERSON_NAME,
    "address": PIIType.ADDRESS,
}


class PIIService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.datasets = DatasetRepository(session)
        self.mappings = SchemaMappingRepository(session)
        self.scans = PIIRepository(session)
        self.audit_logs = AuditLogRepository(session)
        self.frame_loader = DatasetFrameLoader(settings)
        self.scanner = PIIScanner()

    def scan(
        self,
        organization_id: UUID,
        client_id: UUID,
        dataset_id: UUID,
        actor_id: UUID,
    ) -> PIIScan:
        dataset = self.datasets.get(organization_id, client_id, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found")

        scan = PIIScan(
            organization_id=organization_id,
            client_id=client_id,
            dataset_id=dataset_id,
            status=PIIScanStatus.PROCESSING,
        )
        self.scans.add(scan)
        self.session.commit()

        try:
            dataframe = self.frame_loader.load(dataset).reset_index(drop=True)
            schema_pii = self._schema_context(dataset_id)
            detected = self.scanner.scan(dataframe, schema_pii)
            scan.findings = [
                PIIFinding(
                    column_name=finding.column_name,
                    pii_type=finding.pii_type,
                    count=finding.count,
                    confidence=finding.confidence,
                    method=finding.method,
                    sample_redacted_values=list(finding.sample_redacted_values),
                )
                for finding in detected
            ]
            scan.findings_count = sum(finding.count for finding in detected)
            scan.status = PIIScanStatus.COMPLETED
            scan.completed_at = datetime.now(UTC)
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=actor_id,
                client_id=client_id,
                action="dataset.pii_scanned",
                resource_type="pii_scan",
                resource_id=scan.id,
                metadata={
                    "dataset_id": str(dataset_id),
                    "findings_count": scan.findings_count,
                    "categories": sorted(
                        {finding.pii_type.value for finding in detected}
                    ),
                },
            )
            self.session.commit()
        except DatasetParseError as exc:
            scan.status = PIIScanStatus.FAILED
            scan.completed_at = datetime.now(UTC)
            self.session.commit()
            raise InvalidUploadError("Stored dataset could not be parsed") from exc

        self.session.expire_all()
        return self.scans.latest(organization_id, client_id, dataset_id) or scan

    def latest(
        self, organization_id: UUID, client_id: UUID, dataset_id: UUID
    ) -> PIIScan:
        if self.datasets.get(organization_id, client_id, dataset_id) is None:
            raise NotFoundError("Dataset not found")
        scan = self.scans.latest(organization_id, client_id, dataset_id)
        if scan is None:
            raise NotFoundError("No PII scan found")
        return scan

    def _schema_context(self, dataset_id: UUID) -> dict[str, PIIType]:
        return {
            mapping.source_column: SCHEMA_PII_FIELDS[mapping.target_field]
            for mapping in self.mappings.list_for_dataset(dataset_id)
            if mapping.target_field in SCHEMA_PII_FIELDS
            and mapping.status not in {MappingStatus.REJECTED, MappingStatus.IGNORED}
        }
