from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin, utc_now
from app.domain.enums import MappingStatus

if TYPE_CHECKING:
    from app.db.models.dataset import Dataset


class CanonicalField(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "canonical_fields"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )


class SchemaMapping(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "schema_mappings"
    __table_args__ = (
        UniqueConstraint(
            "dataset_id",
            "source_column",
            name="uq_schema_mappings_dataset_source_column",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="schema_mapping_confidence_range",
        ),
        Index("ix_schema_mappings_dataset_status", "dataset_id", "status"),
    )

    dataset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_column: Mapped[str] = mapped_column(String(255), nullable=False)
    target_field: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("canonical_fields.name", ondelete="RESTRICT"),
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[MappingStatus] = mapped_column(
        Enum(
            MappingStatus,
            name="mapping_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=MappingStatus.SUGGESTED,
        server_default=text("'suggested'"),
    )
    manually_overridden: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )

    dataset: Mapped[Dataset] = relationship(back_populates="schema_mappings")
    canonical_field: Mapped[CanonicalField | None] = relationship()
