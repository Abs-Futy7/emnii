import re
from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, AuthorizationError, ConflictError
from app.core.security import (
    create_access_token,
    hash_password,
    perform_dummy_password_check,
    verify_password_and_update,
)
from app.db.models import Organization, OrganizationMembership, User
from app.domain.enums import OrganizationRole
from app.repositories.organizations import (
    MembershipRepository,
    OrganizationRepository,
)
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


@dataclass(frozen=True)
class RegistrationResult:
    user: User
    organization: Organization
    membership: OrganizationMembership


class AuthService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)
        self.organizations = OrganizationRepository(session)
        self.memberships = MembershipRepository(session)

    def register(self, payload: RegisterRequest) -> RegistrationResult:
        email = str(payload.email)
        if self.users.get_by_email(email) is not None:
            raise ConflictError("An account with this email already exists")

        user = User(
            email=email,
            hashed_password=hash_password(payload.password.get_secret_value()),
            full_name=payload.full_name,
        )
        organization = Organization(
            name=payload.organization_name,
            slug=self._available_organization_slug(payload.organization_name),
        )
        membership = OrganizationMembership(
            user=user,
            organization=organization,
            role=OrganizationRole.OWNER,
        )

        self.users.add(user)
        self.organizations.add(organization)
        self.memberships.add(membership)

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            if self.users.get_by_email(email) is not None:
                raise ConflictError(
                    "An account with this email already exists"
                ) from exc
            raise ConflictError("Registration could not be completed") from exc

        self.session.refresh(user)
        self.session.refresh(organization)
        self.session.refresh(membership)
        return RegistrationResult(user, organization, membership)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(str(payload.email))
        password = payload.password.get_secret_value()
        if user is None:
            perform_dummy_password_check(password)
            raise AuthenticationError("Invalid email or password")

        password_valid, updated_hash = verify_password_and_update(
            password,
            user.hashed_password,
        )
        if not password_valid or not user.is_active:
            raise AuthenticationError("Invalid email or password")

        membership = self.memberships.get_primary_for_user(user.id)
        if membership is None:
            raise AuthorizationError("User is not assigned to an organization")

        if updated_hash is not None:
            user.hashed_password = updated_hash
            self.session.commit()

        token = create_access_token(
            user_id=user.id,
            organization_id=membership.organization_id,
            settings=self.settings,
        )
        return TokenResponse(access_token=token)

    def _available_organization_slug(self, organization_name: str) -> str:
        base_slug = re.sub(r"[^a-z0-9]+", "-", organization_name.lower()).strip("-")
        base_slug = base_slug[:100] or "organization"
        if not self.organizations.slug_exists(base_slug):
            return base_slug

        suffix = uuid4().hex[:8]
        trimmed_base = base_slug[: 100 - len(suffix) - 1].rstrip("-")
        return f"{trimmed_base}-{suffix}"
