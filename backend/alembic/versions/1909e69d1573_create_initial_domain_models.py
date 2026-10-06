"""Create initial domain models.

Revision ID: 1909e69d1573
Revises:
Create Date: 2026-10-06 23:41:34
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "1909e69d1573"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

organization_role = postgresql.ENUM(
    "owner", "admin", "agent", "viewer", name="organization_role", create_type=False
)
client_status = postgresql.ENUM(
    "onboarding",
    "active",
    "needs_attention",
    "disabled",
    name="client_status",
    create_type=False,
)


def timestamp_columns() -> list[sa.Column]:
    return [
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
    ]


def upgrade() -> None:
    """Create the initial multi-tenant relational schema."""
    bind = op.get_bind()
    organization_role.create(bind, checkfirst=True)
    client_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "length(trim(email)) > 0",
            name=op.f("ck_users_user_email_not_blank"),
        ),
        sa.CheckConstraint(
            "length(trim(full_name)) > 0",
            name=op.f("ck_users_user_full_name_not_blank"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )

    op.create_table(
        "organizations",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=op.f("ck_organizations_organization_name_not_blank"),
        ),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_organizations_organization_slug_format"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organizations")),
        sa.UniqueConstraint("slug", name=op.f("uq_organizations_slug")),
    )

    op.create_table(
        "organization_memberships",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", organization_role, nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_organization_memberships_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_organization_memberships_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization_memberships")),
        sa.UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_organization_memberships_user_organization",
        ),
    )
    op.create_index(
        op.f("ix_organization_memberships_organization_id"),
        "organization_memberships",
        ["organization_id"],
    )
    op.create_index(
        "ix_organization_memberships_organization_role",
        "organization_memberships",
        ["organization_id", "role"],
    )
    op.create_index(
        op.f("ix_organization_memberships_user_id"),
        "organization_memberships",
        ["user_id"],
    )

    op.create_table(
        "clients",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("industry", sa.String(length=150), nullable=True),
        sa.Column("website", sa.String(length=2048), nullable=True),
        sa.Column("primary_contact_name", sa.String(length=255), nullable=True),
        sa.Column("primary_contact_email", sa.String(length=320), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            client_status,
            server_default=sa.text("'onboarding'"),
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=op.f("ck_clients_client_name_not_blank"),
        ),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_clients_client_slug_format"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_clients_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clients")),
        sa.UniqueConstraint(
            "organization_id", "slug", name="uq_clients_organization_slug"
        ),
    )
    op.create_index(
        op.f("ix_clients_organization_id"), "clients", ["organization_id"]
    )
    op.create_index(
        "ix_clients_organization_status",
        "clients",
        ["organization_id", "status"],
    )

    op.create_table(
        "audit_logs",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(action)) > 0",
            name=op.f("ck_audit_logs_audit_log_action_not_blank"),
        ),
        sa.CheckConstraint(
            "length(trim(resource_type)) > 0",
            name=op.f("ck_audit_logs_audit_log_resource_type_not_blank"),
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            name=op.f("fk_audit_logs_client_id_clients"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_audit_logs_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_audit_logs_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(
        "ix_audit_logs_client_created_at",
        "audit_logs",
        ["client_id", "created_at"],
    )
    op.create_index(
        "ix_audit_logs_organization_created_at",
        "audit_logs",
        ["organization_id", "created_at"],
    )
    op.create_index(
        "ix_audit_logs_resource",
        "audit_logs",
        ["resource_type", "resource_id"],
    )
    op.create_index(
        "ix_audit_logs_user_created_at",
        "audit_logs",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    """Remove the initial multi-tenant relational schema."""
    op.drop_index("ix_audit_logs_user_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_resource", table_name="audit_logs")
    op.drop_index("ix_audit_logs_organization_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_client_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_clients_organization_status", table_name="clients")
    op.drop_index(op.f("ix_clients_organization_id"), table_name="clients")
    op.drop_table("clients")

    op.drop_index(
        op.f("ix_organization_memberships_user_id"),
        table_name="organization_memberships",
    )
    op.drop_index(
        "ix_organization_memberships_organization_role",
        table_name="organization_memberships",
    )
    op.drop_index(
        op.f("ix_organization_memberships_organization_id"),
        table_name="organization_memberships",
    )
    op.drop_table("organization_memberships")

    op.drop_table("organizations")
    op.drop_table("users")

    bind = op.get_bind()
    client_status.drop(bind, checkfirst=True)
    organization_role.drop(bind, checkfirst=True)
