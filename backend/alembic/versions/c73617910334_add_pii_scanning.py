"""Add PII scanning.

Revision ID: c73617910334
Revises: 2fe7910ef308
Create Date: 2026-10-07 22:39:13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c73617910334"
down_revision: str | Sequence[str] | None = "2fe7910ef308"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

pii_scan_status = postgresql.ENUM(
    "processing", "completed", "failed",
    name="pii_scan_status", create_type=False,
)
pii_type = postgresql.ENUM(
    "EMAIL", "PHONE", "IP_ADDRESS", "CREDIT_CARD", "PERSON_NAME", "ADDRESS",
    name="pii_type", create_type=False,
)


def upgrade() -> None:
    """Create tenant-scoped scans and redacted findings."""
    bind = op.get_bind()
    pii_scan_status.create(bind, checkfirst=True)
    pii_type.create(bind, checkfirst=True)

    op.create_table(
        "pii_scans",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status", pii_scan_status, server_default=sa.text("'processing'"),
            nullable=False,
        ),
        sa.Column("findings_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "findings_count >= 0",
            name=op.f("ck_pii_scans_pii_scan_findings_count_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["client_id"], ["clients.id"],
            name=op.f("fk_pii_scans_client_id_clients"), ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "client_id", "dataset_id"],
            ["datasets.organization_id", "datasets.client_id", "datasets.id"],
            name="fk_pii_scans_tenant_dataset", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"],
            name=op.f("fk_pii_scans_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pii_scans")),
    )
    op.create_index(
        "ix_pii_scans_tenant_dataset_created", "pii_scans",
        ["organization_id", "client_id", "dataset_id", "created_at"],
    )

    op.create_table(
        "pii_findings",
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=False),
        sa.Column("pii_type", pii_type, nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("method", sa.String(length=100), nullable=False),
        sa.Column(
            "sample_redacted_values", postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"), nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name=op.f("ck_pii_findings_pii_finding_confidence_range"),
        ),
        sa.CheckConstraint(
            "count >= 0",
            name=op.f("ck_pii_findings_pii_finding_count_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["scan_id"], ["pii_scans.id"],
            name=op.f("fk_pii_findings_scan_id_pii_scans"), ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pii_findings")),
    )
    op.create_index(
        "ix_pii_findings_scan_type", "pii_findings", ["scan_id", "pii_type"]
    )


def downgrade() -> None:
    """Remove PII scans, findings, and native enum types."""
    op.drop_index("ix_pii_findings_scan_type", table_name="pii_findings")
    op.drop_table("pii_findings")
    op.drop_index(
        "ix_pii_scans_tenant_dataset_created", table_name="pii_scans"
    )
    op.drop_table("pii_scans")

    bind = op.get_bind()
    pii_type.drop(bind, checkfirst=True)
    pii_scan_status.drop(bind, checkfirst=True)
