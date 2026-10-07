"""Add document ingestion and indexing.

Revision ID: 6ee8501e739c
Revises: c73617910334
Create Date: 2026-10-07 22:52:22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "6ee8501e739c"
down_revision: str | Sequence[str] | None = "c73617910334"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

document_file_type = postgresql.ENUM(
    "pdf", "docx", "txt", "markdown",
    name="document_file_type", create_type=False,
)
document_status = postgresql.ENUM(
    "uploaded", "processing", "processed", "failed",
    name="document_status", create_type=False,
)
document_indexing_status = postgresql.ENUM(
    "not_indexed", "indexing", "indexed", "failed",
    name="document_indexing_status", create_type=False,
)


def upgrade() -> None:
    """Create tenant-scoped documents and chunks."""
    bind = op.get_bind()
    document_file_type.create(bind, checkfirst=True)
    document_status.create(bind, checkfirst=True)
    document_indexing_status.create(bind, checkfirst=True)

    op.create_table(
        "documents",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", document_file_type, nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column(
            "status", document_status, server_default=sa.text("'uploaded'"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("extracted_text_length", sa.BigInteger(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column(
            "indexing_status", document_indexing_status,
            server_default=sa.text("'not_indexed'"), nullable=False,
        ),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("embedding_model", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.CheckConstraint(
            "extracted_text_length >= 0",
            name=op.f("ck_documents_document_extracted_text_length_nonnegative"),
        ),
        sa.CheckConstraint(
            "file_size >= 0",
            name=op.f("ck_documents_document_file_size_nonnegative"),
        ),
        sa.CheckConstraint(
            "page_count IS NULL OR page_count >= 0",
            name=op.f("ck_documents_document_page_count_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "client_id"],
            ["clients.organization_id", "clients.id"],
            name="fk_documents_organization_client", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"],
            name=op.f("fk_documents_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"], ["users.id"],
            name=op.f("fk_documents_uploaded_by_users"), ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
        sa.UniqueConstraint(
            "organization_id", "client_id", "id",
            name="uq_documents_organization_client_id",
        ),
        sa.UniqueConstraint(
            "stored_filename", name="uq_documents_stored_filename"
        ),
    )
    op.create_index(
        "ix_documents_tenant_created", "documents",
        ["organization_id", "client_id", "created_at"],
    )
    op.create_index(
        "ix_documents_tenant_status", "documents",
        ["organization_id", "client_id", "status"],
    )

    op.create_table(
        "document_chunks",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column(
            "metadata", postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"), nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "chunk_index >= 0",
            name=op.f("ck_document_chunks_document_chunk_index_nonnegative"),
        ),
        sa.CheckConstraint(
            "length(trim(content)) > 0",
            name=op.f("ck_document_chunks_document_chunk_content_not_blank"),
        ),
        sa.CheckConstraint(
            "page_number IS NULL OR page_number >= 1",
            name=op.f("ck_document_chunks_document_chunk_page_number_positive"),
        ),
        sa.CheckConstraint(
            "token_count IS NULL OR token_count >= 0",
            name=op.f("ck_document_chunks_document_chunk_token_count_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["client_id"], ["clients.id"],
            name=op.f("fk_document_chunks_client_id_clients"), ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "client_id", "document_id"],
            ["documents.organization_id", "documents.client_id", "documents.id"],
            name="fk_document_chunks_tenant_document", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"],
            name=op.f("fk_document_chunks_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_chunks")),
        sa.UniqueConstraint(
            "document_id", "chunk_index",
            name="uq_document_chunks_document_index",
        ),
    )
    op.create_index(
        "ix_document_chunks_tenant_document", "document_chunks",
        ["organization_id", "client_id", "document_id"],
    )


def downgrade() -> None:
    """Remove document ingestion and indexing tables."""
    op.drop_index(
        "ix_document_chunks_tenant_document", table_name="document_chunks"
    )
    op.drop_table("document_chunks")
    op.drop_index("ix_documents_tenant_status", table_name="documents")
    op.drop_index("ix_documents_tenant_created", table_name="documents")
    op.drop_table("documents")

    bind = op.get_bind()
    document_indexing_status.drop(bind, checkfirst=True)
    document_status.drop(bind, checkfirst=True)
    document_file_type.drop(bind, checkfirst=True)
