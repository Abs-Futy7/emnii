from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.domain.enums import ClientStatus
from app.schemas.base import ORMModel
from app.schemas.organization import SLUG_PATTERN
from app.schemas.pagination import PaginationMeta


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


class ClientUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=SLUG_PATTERN,
    )
    industry: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=2048)
    primary_contact_name: str | None = Field(default=None, max_length=255)
    primary_contact_email: str | None = Field(default=None, max_length=320)
    description: str | None = None
    status: ClientStatus | None = None

    @field_validator("name", "slug", "status")
    @classmethod
    def required_fields_cannot_be_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("cannot be null when provided")
        return value


class ClientListResponse(ORMModel):
    items: list[ClientRead]
    pagination: PaginationMeta
