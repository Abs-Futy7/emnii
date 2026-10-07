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
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin, utc_now
from app.domain.enums import (
    DocumentFileType,
    DocumentIndexingStatus,
    DocumentStatus,
)

if TYPE_CHECKING:
    from app.db.models.client import Client
    from app.db.models.user import User


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "client_id"],
            ["clients.organization_id", "clients.id"],
            name="fk_documents_organization_client",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "organization_id",
            "client_id",
            "id",
            name="uq_documents_organization_client_id",
        ),
        UniqueConstraint("stored_filename", name="uq_documents_stored_filename"),
        Index(
            "ix_documents_tenant_created",
            "organization_id",
            "client_id",
            "created_at",
        ),
        Index(
            "ix_documents_tenant_status",
            "organization_id",
            "client_id",
            "status",
        ),
        CheckConstraint("file_size >= 0", name="document_file_size_nonnegative"),
        CheckConstraint(
            "extracted_text_length >= 0",
            name="document_extracted_text_length_nonnegative",
        ),
        CheckConstraint(
            "page_count IS NULL OR page_count >= 0",
            name="document_page_count_nonnegative",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    uploaded_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[DocumentFileType] = mapped_column(
        Enum(
            DocumentFileType,
            name="document_file_type",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=DocumentStatus.UPLOADED,
        server_default=text("'uploaded'"),
    )
    title: Mapped[str | None] = mapped_column(String(500))
    extracted_text_length: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    page_count: Mapped[int | None] = mapped_column(Integer)
    indexing_status: Mapped[DocumentIndexingStatus] = mapped_column(
        Enum(
            DocumentIndexingStatus,
            name="document_indexing_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=DocumentIndexingStatus.NOT_INDEXED,
        server_default=text("'not_indexed'"),
    )
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    embedding_model: Mapped[str | None] = mapped_column(String(255))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    client: Mapped[Client] = relationship(back_populates="documents")
    uploader: Mapped[User | None] = relationship(back_populates="uploaded_documents")
    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DocumentChunk.chunk_index",
    )


class DocumentChunk(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "client_id", "document_id"],
            ["documents.organization_id", "documents.client_id", "documents.id"],
            name="fk_document_chunks_tenant_document",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "document_id", "chunk_index", name="uq_document_chunks_document_index"
        ),
        Index(
            "ix_document_chunks_tenant_document",
            "organization_id",
            "client_id",
            "document_id",
        ),
        CheckConstraint("chunk_index >= 0", name="document_chunk_index_nonnegative"),
        CheckConstraint(
            "length(trim(content)) > 0", name="document_chunk_content_not_blank"
        ),
        CheckConstraint(
            "token_count IS NULL OR token_count >= 0",
            name="document_chunk_token_count_nonnegative",
        ),
        CheckConstraint(
            "page_number IS NULL OR page_number >= 1",
            name="document_chunk_page_number_positive",
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
    document_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer)
    page_number: Mapped[int | None] = mapped_column(Integer)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
        server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    document: Mapped[Document] = relationship(back_populates="chunks")
