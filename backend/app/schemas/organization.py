from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.domain.enums import OrganizationRole
from app.schemas.base import ORMModel

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class OrganizationBase(ORMModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=SLUG_PATTERN)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class OrganizationMembershipCreate(ORMModel):
    user_id: UUID
    role: OrganizationRole


class OrganizationMembershipRead(OrganizationMembershipCreate):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
