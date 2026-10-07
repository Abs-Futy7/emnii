from datetime import datetime
from uuid import uuid4

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.models import (
    AuditLog,
    Client,
    OrganizationMembership,
    PIIFinding,
    User,
    ValidationIssue,
)
from app.domain.enums import ClientStatus, OrganizationRole
from app.schemas.audit_log import AuditLogRead


def constraint_column_sets(model: type[object]) -> set[frozenset[str]]:
    return {
        frozenset(column.name for column in constraint.columns)
        for constraint in model.__table__.constraints  # type: ignore[attr-defined]
        if isinstance(constraint, UniqueConstraint)
    }


def test_membership_is_unique_per_user_and_organization() -> None:
    assert frozenset({"user_id", "organization_id"}) in constraint_column_sets(
        OrganizationMembership
    )


def test_client_slug_is_unique_inside_organization() -> None:
    assert frozenset({"organization_id", "slug"}) in constraint_column_sets(Client)


def test_user_email_has_database_unique_constraint() -> None:
    assert frozenset({"email"}) in constraint_column_sets(User)


def test_postgresql_types_and_timezone_aware_timestamps() -> None:
    assert isinstance(User.__table__.c.id.type, UUID)
    metadata_type = AuditLog.__table__.c.metadata.type.dialect_impl(
        postgresql.dialect()
    )
    assert isinstance(metadata_type, JSONB)
    examples_type = ValidationIssue.__table__.c.example_rows.type.dialect_impl(
        postgresql.dialect()
    )
    assert isinstance(examples_type, JSONB)
    pii_samples_type = PIIFinding.__table__.c.sample_redacted_values.type.dialect_impl(
        postgresql.dialect()
    )
    assert isinstance(pii_samples_type, JSONB)
    assert User.__table__.c.created_at.type.timezone is True
    assert AuditLog.__table__.c.created_at.type.timezone is True


def test_domain_enum_values_are_stable() -> None:
    assert {role.value for role in OrganizationRole} == {
        "owner",
        "admin",
        "agent",
        "viewer",
    }
    assert {status.value for status in ClientStatus} == {
        "onboarding",
        "active",
        "needs_attention",
        "disabled",
    }


def test_audit_log_schema_maps_reserved_orm_metadata_attribute() -> None:
    now = datetime.now().astimezone()
    audit_log = AuditLog(
        id=uuid4(),
        organization_id=uuid4(),
        action="client.created",
        resource_type="client",
        metadata_={"source": "test"},
        created_at=now,
    )

    response = AuditLogRead.model_validate(audit_log)

    assert response.metadata == {"source": "test"}
