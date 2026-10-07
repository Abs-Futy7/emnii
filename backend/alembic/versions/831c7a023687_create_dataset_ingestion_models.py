"""Create dataset ingestion models.

Revision ID: 831c7a023687
Revises: 1909e69d1573
Create Date: 2026-10-07 22:13:37
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "831c7a023687"
down_revision: str | Sequence[str] | None = "1909e69d1573"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

dataset_file_type = postgresql.ENUM(
    "csv", "json", "xlsx", name="dataset_file_type", create_type=False
)
dataset_status = postgresql.ENUM(
    "uploaded",
    "processing",
    "needs_review",
    "validated",
    "failed",
    name="dataset_status",
    create_type=False,
)


def upgrade() -> None:
    """Create dataset and detected-column metadata tables."""
    bind = op.get_bind()
    dataset_file_type.create(bind, checkfirst=True)
    dataset_status.create(bind, checkfirst=True)

    op.create_unique_constraint(
        "uq_clients_organization_id_id",
        "clients",
        ["organization_id", "id"],
    )
    op.create_table(
        "datasets",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", dataset_file_type, nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("row_count", sa.BigInteger(), nullable=False),
        sa.Column("column_count", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            dataset_status,
            server_default=sa.text("'uploaded'"),
            nullable=False,
        ),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "column_count >= 0",
            name=op.f("ck_datasets_dataset_column_count_nonnegative"),
        ),
        sa.CheckConstraint(
            "file_size >= 0",
            name=op.f("ck_datasets_dataset_file_size_nonnegative"),
        ),
        sa.CheckConstraint(
            "row_count >= 0",
            name=op.f("ck_datasets_dataset_row_count_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_datasets_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "client_id"],
            ["clients.organization_id", "clients.id"],
            name="fk_datasets_organization_client",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name=op.f("fk_datasets_uploaded_by_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_datasets")),
        sa.UniqueConstraint(
            "stored_filename",
            name="uq_datasets_stored_filename",
        ),
    )
    op.create_index(
        "ix_datasets_organization_client_created_at",
        "datasets",
        ["organization_id", "client_id", "created_at"],
    )
    op.create_index(
        "ix_datasets_organization_status",
        "datasets",
        ["organization_id", "status"],
    )

    op.create_table(
        "dataset_columns",
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("detected_type", sa.String(length=50), nullable=False),
        sa.Column(
            "sample_values",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("null_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_count", sa.BigInteger(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "null_count >= 0",
            name=op.f("ck_dataset_columns_dataset_column_null_count_nonnegative"),
        ),
        sa.CheckConstraint(
            "unique_count >= 0",
            name=op.f("ck_dataset_columns_dataset_column_unique_count_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
            name=op.f("fk_dataset_columns_dataset_id_datasets"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dataset_columns")),
    )
    op.create_index(
        "ix_dataset_columns_dataset_id",
        "dataset_columns",
        ["dataset_id"],
    )


def downgrade() -> None:
    """Remove dataset ingestion tables and enum types."""
    op.drop_index("ix_dataset_columns_dataset_id", table_name="dataset_columns")
    op.drop_table("dataset_columns")
    op.drop_index("ix_datasets_organization_status", table_name="datasets")
    op.drop_index(
        "ix_datasets_organization_client_created_at",
        table_name="datasets",
    )
    op.drop_table("datasets")
    op.drop_constraint(
        "uq_clients_organization_id_id",
        "clients",
        type_="unique",
    )

    bind = op.get_bind()
    dataset_status.drop(bind, checkfirst=True)
    dataset_file_type.drop(bind, checkfirst=True)
