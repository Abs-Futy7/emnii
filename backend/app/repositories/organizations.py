from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Organization, OrganizationMembership


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        return self.session.get(Organization, organization_id)

    def slug_exists(self, slug: str) -> bool:
        statement = select(Organization.id).where(Organization.slug == slug).limit(1)
        return self.session.scalar(statement) is not None

    def add(self, organization: Organization) -> None:
        self.session.add(organization)


class MembershipRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_for_user_and_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> OrganizationMembership | None:
        statement = select(OrganizationMembership).where(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id,
        )
        return self.session.scalar(statement)

    def get_primary_for_user(self, user_id: UUID) -> OrganizationMembership | None:
        statement = (
            select(OrganizationMembership)
            .where(OrganizationMembership.user_id == user_id)
            .order_by(
                OrganizationMembership.created_at,
                OrganizationMembership.id,
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def add(self, membership: OrganizationMembership) -> None:
        self.session.add(membership)
