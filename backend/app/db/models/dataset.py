from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin, utc_now
from app.domain.enums import DatasetFileType, DatasetStatus

if TYPE_CHECKING:
    from app.db.models.client import Client
    from app.db.models.organization import Organization
    from app.db.models.pii import PIIScan
    from app.db.models.schema_mapping import SchemaMapping
    from app.db.models.user import User
    from app.db.models.validation import ValidationRun


class Dataset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "datasets"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "client_id"],
            ["clients.organization_id", "clients.id"],
            name="fk_datasets_organization_client",
            ondelete="CASCADE",
        ),
        UniqueConstraint("stored_filename", name="uq_datasets_stored_filename"),
        UniqueConstraint(
            "organization_id",
            "client_id",
            "id",
            name="uq_datasets_organization_client_id",
        ),
        Index(
            "ix_datasets_organization_client_created_at",
            "organization_id",
            "client_id",
            "created_at",
        ),
        Index("ix_datasets_organization_status", "organization_id", "status"),
        CheckConstraint("file_size >= 0", name="dataset_file_size_nonnegative"),
        CheckConstraint("row_count >= 0", name="dataset_row_count_nonnegative"),
        CheckConstraint("column_count >= 0", name="dataset_column_count_nonnegative"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[DatasetFileType] = mapped_column(
        Enum(
            DatasetFileType,
            name="dataset_file_type",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    row_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(
            DatasetStatus,
            name="dataset_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=DatasetStatus.UPLOADED,
        server_default=text("'uploaded'"),
    )
    uploaded_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    organization: Mapped[Organization] = relationship(
        back_populates="datasets",
        viewonly=True,
    )
    client: Mapped[Client] = relationship(back_populates="datasets")
    uploader: Mapped[User | None] = relationship(back_populates="uploaded_datasets")
    columns: Mapped[list[DatasetColumn]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DatasetColumn.id",
    )
    schema_mappings: Mapped[list[SchemaMapping]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    validation_runs: Mapped[list[ValidationRun]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    pii_scans: Mapped[list[PIIScan]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DatasetColumn(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "dataset_columns"
    __table_args__ = (
        Index("ix_dataset_columns_dataset_id", "dataset_id"),
        CheckConstraint(
            "null_count >= 0",
            name="dataset_column_null_count_nonnegative",
        ),
        CheckConstraint(
            "unique_count >= 0",
            name="dataset_column_unique_count_nonnegative",
        ),
    )

    dataset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    detected_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sample_values: Mapped[list[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
        server_default="[]",
    )
    null_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unique_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )
    dataset: Mapped[Dataset] = relationship(back_populates="columns")
