from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.domain.enums import ClientStatus
from app.schemas.base import ORMModel
from app.schemas.organization import SLUG_PATTERN


class ClientBase(ORMModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=SLUG_PATTERN)
    industry: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=2048)
    primary_contact_name: str | None = Field(default=None, max_length=255)
    primary_contact_email: str | None = Field(default=None, max_length=320)
    description: str | None = None


class ClientCreate(ClientBase):
    status: ClientStatus = ClientStatus.ONBOARDING


class ClientRead(ClientBase):
    id: UUID
    organization_id: UUID
    status: ClientStatus
    created_at: datetime
    updated_at: datetime
