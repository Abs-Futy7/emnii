from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import ORMModel


class UserBase(ORMModel):
    email: str = Field(min_length=3, max_length=320)
    full_name: str = Field(min_length=1, max_length=255)


class UserRead(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
