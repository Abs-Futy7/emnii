from pydantic import EmailStr, Field, SecretStr, field_validator

from app.schemas.base import ORMModel
from app.schemas.organization import OrganizationMembershipRead, OrganizationRead
from app.schemas.user import UserRead


class RegisterRequest(ORMModel):
    email: EmailStr
    password: SecretStr = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    organization_name: str = Field(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("full_name", "organization_name")
    @classmethod
    def strip_nonempty_names(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be blank")
        return normalized


class LoginRequest(ORMModel):
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class TokenResponse(ORMModel):
    access_token: str
    token_type: str = "bearer"


class RegistrationResponse(ORMModel):
    user: UserRead
    organization: OrganizationRead
    membership: OrganizationMembershipRead


class CurrentUserResponse(RegistrationResponse):
    pass
