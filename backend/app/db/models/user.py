from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.audit_log import AuditLog
    from app.db.models.dataset import Dataset
    from app.db.models.document import Document
    from app.db.models.organization_membership import OrganizationMembership


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "length(trim(email)) > 0",
            name="user_email_not_blank",
        ),
        CheckConstraint(
            "length(trim(full_name)) > 0",
            name="user_full_name_not_blank",
        ),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    memberships: Mapped[list[OrganizationMembership]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="user",
        passive_deletes=True,
    )
    uploaded_datasets: Mapped[list[Dataset]] = relationship(
        back_populates="uploader",
        passive_deletes=True,
    )
    uploaded_documents: Mapped[list[Document]] = relationship(
        back_populates="uploader",
        passive_deletes=True,
    )
