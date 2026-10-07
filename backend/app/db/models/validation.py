from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
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
from app.domain.enums import ValidationSeverity, ValidationStatus

if TYPE_CHECKING:
    from app.db.models.client import Client
    from app.db.models.dataset import Dataset
    from app.db.models.organization import Organization


class ValidationRun(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "validation_runs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "client_id", "dataset_id"],
            ["datasets.organization_id", "datasets.client_id", "datasets.id"],
            name="fk_validation_runs_tenant_dataset",
            ondelete="CASCADE",
        ),
        Index(
            "ix_validation_runs_tenant_dataset_started",
            "organization_id",
            "client_id",
            "dataset_id",
            "started_at",
        ),
        CheckConstraint(
            "quality_score >= 0 AND quality_score <= 100",
            name="validation_quality_score_range",
        ),
        CheckConstraint(
            "completeness_score >= 0 AND completeness_score <= 100",
            name="validation_completeness_score_range",
        ),
        CheckConstraint(
            "validity_score >= 0 AND validity_score <= 100",
            name="validation_validity_score_range",
        ),
        CheckConstraint(
            "uniqueness_score >= 0 AND uniqueness_score <= 100",
            name="validation_uniqueness_score_range",
        ),
        CheckConstraint(
            "consistency_score >= 0 AND consistency_score <= 100",
            name="validation_consistency_score_range",
        ),
        CheckConstraint(
            "total_records >= 0", name="validation_total_records_nonnegative"
        ),
        CheckConstraint(
            "valid_records >= 0", name="validation_valid_records_nonnegative"
        ),
        CheckConstraint(
            "warning_count >= 0", name="validation_warning_count_nonnegative"
        ),
        CheckConstraint("error_count >= 0", name="validation_error_count_nonnegative"),
        CheckConstraint(
            "valid_records <= total_records",
            name="validation_valid_records_within_total",
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
    status: Mapped[ValidationStatus] = mapped_column(
        Enum(
            ValidationStatus,
            name="validation_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=ValidationStatus.PROCESSING,
        server_default=text("'processing'"),
    )
    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    completeness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    validity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    uniqueness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    consistency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    organization: Mapped[Organization] = relationship(viewonly=True)
    client: Mapped[Client] = relationship(viewonly=True)
    dataset: Mapped[Dataset] = relationship(back_populates="validation_runs")
    issues: Mapped[list[ValidationIssue]] = relationship(
        back_populates="validation_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ValidationIssue(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "validation_issues"
    __table_args__ = (
        Index("ix_validation_issues_run_severity", "validation_run_id", "severity"),
        CheckConstraint(
            "affected_count >= 0",
            name="validation_issue_affected_count_nonnegative",
        ),
        CheckConstraint(
            "affected_percentage >= 0 AND affected_percentage <= 100",
            name="validation_issue_affected_percentage_range",
        ),
    )

    validation_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("validation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[ValidationSeverity] = mapped_column(
        Enum(
            ValidationSeverity,
            name="validation_severity",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    field: Mapped[str | None] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    affected_count: Mapped[int] = mapped_column(Integer, nullable=False)
    affected_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    example_rows: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
        server_default="[]",
    )

    validation_run: Mapped[ValidationRun] = relationship(back_populates="issues")
