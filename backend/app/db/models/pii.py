from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin, utc_now
from app.domain.enums import PIIScanStatus, PIIType

if TYPE_CHECKING:
    from app.db.models.client import Client
    from app.db.models.dataset import Dataset
    from app.db.models.organization import Organization


class PIIScan(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "pii_scans"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "client_id", "dataset_id"],
            ["datasets.organization_id", "datasets.client_id", "datasets.id"],
            name="fk_pii_scans_tenant_dataset",
            ondelete="CASCADE",
        ),
        Index(
            "ix_pii_scans_tenant_dataset_created",
            "organization_id",
            "client_id",
            "dataset_id",
            "created_at",
        ),
        CheckConstraint(
            "findings_count >= 0",
            name="pii_scan_findings_count_nonnegative",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    dataset_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    status: Mapped[PIIScanStatus] = mapped_column(
        Enum(
            PIIScanStatus,
            name="pii_scan_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=PIIScanStatus.PROCESSING,
        server_default=text("'processing'"),
    )
    findings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    organization: Mapped[Organization] = relationship(viewonly=True)
    client: Mapped[Client] = relationship(viewonly=True)
    dataset: Mapped[Dataset] = relationship(back_populates="pii_scans")
    findings: Mapped[list[PIIFinding]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="PIIFinding.column_name, PIIFinding.pii_type",
    )


class PIIFinding(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "pii_findings"
    __table_args__ = (
        Index("ix_pii_findings_scan_type", "scan_id", "pii_type"),
        CheckConstraint("count >= 0", name="pii_finding_count_nonnegative"),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="pii_finding_confidence_range",
        ),
    )

    scan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pii_scans.id", ondelete="CASCADE"),
        nullable=False,
    )
    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pii_type: Mapped[PIIType] = mapped_column(
        Enum(
            PIIType,
            name="pii_type",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(100), nullable=False)
    sample_redacted_values: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
        server_default="[]",
    )

    scan: Mapped[PIIScan] = relationship(back_populates="findings")
