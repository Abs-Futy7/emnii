from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import ClientStatus

if TYPE_CHECKING:
    from app.db.models.audit_log import AuditLog
    from app.db.models.organization import Organization


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_clients_organization_slug",
        ),
        Index("ix_clients_organization_status", "organization_id", "status"),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="client_name_not_blank",
        ),
        CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name="client_slug_format",
        ).ddl_if(dialect="postgresql"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(150))
    website: Mapped[str | None] = mapped_column(String(2048))
    primary_contact_name: Mapped[str | None] = mapped_column(String(255))
    primary_contact_email: Mapped[str | None] = mapped_column(String(320))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ClientStatus] = mapped_column(
        Enum(
            ClientStatus,
            name="client_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=ClientStatus.ONBOARDING,
        server_default=text("'onboarding'"),
    )

    organization: Mapped[Organization] = relationship(back_populates="clients")
    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="client",
        passive_deletes=True,
    )
