"""Add schema mapping and data quality models.

Revision ID: 2fe7910ef308
Revises: 831c7a023687
Create Date: 2026-10-07 22:29:02
"""

from collections.abc import Sequence
from uuid import NAMESPACE_URL, uuid5

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2fe7910ef308"
down_revision: str | Sequence[str] | None = "831c7a023687"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

mapping_status = postgresql.ENUM(
    "suggested", "approved", "rejected", "ignored",
    name="mapping_status", create_type=False,
)
validation_status = postgresql.ENUM(
    "processing", "completed", "failed",
    name="validation_status", create_type=False,
)
validation_severity = postgresql.ENUM(
    "info", "warning", "error",
    name="validation_severity", create_type=False,
)

CANONICAL_FIELD_TYPES = {
    "customer_id": "string",
    "customer_name": "string",
    "first_name": "string",
    "last_name": "string",
    "email": "email",
    "phone": "phone",
    "address": "string",
    "city": "string",
    "country": "string",
    "created_at": "datetime",
    "order_id": "string",
    "ticket_id": "string",
    "ticket_status": "string",
}


def upgrade() -> None:
    """Create canonical mappings and persisted validation reports."""
    bind = op.get_bind()
    mapping_status.create(bind, checkfirst=True)
    validation_status.create(bind, checkfirst=True)
    validation_severity.create(bind, checkfirst=True)

    op.create_unique_constraint(
        "uq_datasets_organization_client_id",
        "datasets",
        ["organization_id", "client_id", "id"],
    )
    op.create_table(
        "canonical_fields",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("data_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_canonical_fields")),
        sa.UniqueConstraint("name", name=op.f("uq_canonical_fields_name")),
    )
    canonical_fields = sa.table(
        "canonical_fields",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("data_type", sa.String()),
    )
    op.bulk_insert(
        canonical_fields,
        [
            {
                "id": uuid5(NAMESPACE_URL, f"resolveops:{name}"),
                "name": name,
                "data_type": data_type,
            }
            for name, data_type in CANONICAL_FIELD_TYPES.items()
        ],
    )

    op.create_table(
        "schema_mappings",
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_column", sa.String(length=255), nullable=False),
        sa.Column("target_field", sa.String(length=100), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column(
            "status", mapping_status, server_default=sa.text("'suggested'"),
            nullable=False,
        ),
        sa.Column(
            "manually_overridden", sa.Boolean(),
            server_default=sa.text("false"), nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name=op.f("ck_schema_mappings_schema_mapping_confidence_range"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"], ["datasets.id"],
            name=op.f("fk_schema_mappings_dataset_id_datasets"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_field"], ["canonical_fields.name"],
            name=op.f("fk_schema_mappings_target_field_canonical_fields"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_schema_mappings")),
        sa.UniqueConstraint(
            "dataset_id", "source_column",
            name="uq_schema_mappings_dataset_source_column",
        ),
    )
    op.create_index(
        "ix_schema_mappings_dataset_status", "schema_mappings",
        ["dataset_id", "status"],
    )

    op.create_table(
        "validation_runs",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status", validation_status, server_default=sa.text("'processing'"),
            nullable=False,
        ),
        sa.Column("total_records", sa.Integer(), nullable=False),
        sa.Column("valid_records", sa.Integer(), nullable=False),
        sa.Column("warning_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=False),
        sa.Column("completeness_score", sa.Float(), nullable=False),
        sa.Column("validity_score", sa.Float(), nullable=False),
        sa.Column("uniqueness_score", sa.Float(), nullable=False),
        sa.Column("consistency_score", sa.Float(), nullable=False),
        sa.Column(
            "started_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "completeness_score >= 0 AND completeness_score <= 100",
            name=op.f("ck_validation_runs_validation_completeness_score_range"),
        ),
        sa.CheckConstraint(
            "consistency_score >= 0 AND consistency_score <= 100",
            name=op.f("ck_validation_runs_validation_consistency_score_range"),
        ),
        sa.CheckConstraint(
            "error_count >= 0",
            name=op.f("ck_validation_runs_validation_error_count_nonnegative"),
        ),
        sa.CheckConstraint(
            "quality_score >= 0 AND quality_score <= 100",
            name=op.f("ck_validation_runs_validation_quality_score_range"),
        ),
        sa.CheckConstraint(
            "total_records >= 0",
            name=op.f("ck_validation_runs_validation_total_records_nonnegative"),
        ),
        sa.CheckConstraint(
            "uniqueness_score >= 0 AND uniqueness_score <= 100",
            name=op.f("ck_validation_runs_validation_uniqueness_score_range"),
        ),
        sa.CheckConstraint(
            "valid_records >= 0",
            name=op.f("ck_validation_runs_validation_valid_records_nonnegative"),
        ),
        sa.CheckConstraint(
            "valid_records <= total_records",
            name=op.f("ck_validation_runs_validation_valid_records_within_total"),
        ),
        sa.CheckConstraint(
            "validity_score >= 0 AND validity_score <= 100",
            name=op.f("ck_validation_runs_validation_validity_score_range"),
        ),
        sa.CheckConstraint(
            "warning_count >= 0",
            name=op.f("ck_validation_runs_validation_warning_count_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["client_id"], ["clients.id"],
            name=op.f("fk_validation_runs_client_id_clients"), ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "client_id", "dataset_id"],
            ["datasets.organization_id", "datasets.client_id", "datasets.id"],
            name="fk_validation_runs_tenant_dataset", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"],
            name=op.f("fk_validation_runs_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_validation_runs")),
    )
    op.create_index(
        "ix_validation_runs_tenant_dataset_started", "validation_runs",
        ["organization_id", "client_id", "dataset_id", "started_at"],
    )

    op.create_table(
        "validation_issues",
        sa.Column("validation_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule", sa.String(length=100), nullable=False),
        sa.Column("severity", validation_severity, nullable=False),
        sa.Column("field", sa.String(length=255), nullable=True),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("affected_count", sa.Integer(), nullable=False),
        sa.Column("affected_percentage", sa.Float(), nullable=False),
        sa.Column(
            "example_rows", postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"), nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "affected_count >= 0",
            name=op.f("ck_validation_issues_validation_issue_affected_count_nonnegative"),
        ),
        sa.CheckConstraint(
            "affected_percentage >= 0 AND affected_percentage <= 100",
            name=op.f("ck_validation_issues_validation_issue_affected_percentage_range"),
        ),
        sa.ForeignKeyConstraint(
            ["validation_run_id"], ["validation_runs.id"],
            name=op.f("fk_validation_issues_validation_run_id_validation_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_validation_issues")),
    )
    op.create_index(
        "ix_validation_issues_run_severity", "validation_issues",
        ["validation_run_id", "severity"],
    )


def downgrade() -> None:
    """Remove schema mapping and data quality models."""
    op.drop_index("ix_validation_issues_run_severity", table_name="validation_issues")
    op.drop_table("validation_issues")
    op.drop_index(
        "ix_validation_runs_tenant_dataset_started", table_name="validation_runs"
    )
    op.drop_table("validation_runs")
    op.drop_index("ix_schema_mappings_dataset_status", table_name="schema_mappings")
    op.drop_table("schema_mappings")
    op.drop_table("canonical_fields")
    op.drop_constraint(
        "uq_datasets_organization_client_id", "datasets", type_="unique"
    )

    bind = op.get_bind()
    validation_severity.drop(bind, checkfirst=True)
    validation_status.drop(bind, checkfirst=True)
    mapping_status.drop(bind, checkfirst=True)
