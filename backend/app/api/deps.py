from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.db.models import Organization, OrganizationMembership, User
from app.db.session import SessionLocal
from app.domain.enums import OrganizationRole
from app.repositories.organizations import (
    MembershipRepository,
    OrganizationRepository,
)
from app.repositories.users import UserRepository
from app.services.auth import AuthService


def get_db_session() -> Generator[Session]:
    with SessionLocal() as session:
        yield session


SettingsDep = Annotated[Settings, Depends(get_settings)]
DatabaseSession = Annotated[Session, Depends(get_db_session)]

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Security(bearer_scheme),
]


@dataclass(frozen=True)
class AuthContext:
    user: User
    membership: OrganizationMembership
    organization: Organization


def get_auth_service(db: DatabaseSession, settings: SettingsDep) -> AuthService:
    return AuthService(db, settings)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_auth_context(
    credentials: BearerCredentials,
    db: DatabaseSession,
    settings: SettingsDep,
) -> AuthContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError()

    payload = decode_access_token(credentials.credentials, settings)
    user = UserRepository(db).get_by_id(payload.sub)
    if user is None or not user.is_active:
        raise AuthenticationError()

    membership = MembershipRepository(db).get_for_user_and_organization(
        user.id,
        payload.organization_id,
    )
    if membership is None:
        raise AuthenticationError()

    organization = OrganizationRepository(db).get_by_id(payload.organization_id)
    if organization is None:
        raise AuthenticationError()

    return AuthContext(user, membership, organization)


AuthContextDep = Annotated[AuthContext, Depends(get_auth_context)]


def get_current_user(context: AuthContextDep) -> User:
    return context.user


def get_current_membership(context: AuthContextDep) -> OrganizationMembership:
    return context.membership


def get_current_organization(context: AuthContextDep) -> Organization:
    return context.organization


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentMembership = Annotated[
    OrganizationMembership,
    Depends(get_current_membership),
]
CurrentOrganization = Annotated[Organization, Depends(get_current_organization)]


def require_role(
    *allowed_roles: OrganizationRole,
) -> Callable[[CurrentMembership], OrganizationMembership]:
    allowed = frozenset(allowed_roles)

    def role_dependency(membership: CurrentMembership) -> OrganizationMembership:
        if membership.role not in allowed:
            raise AuthorizationError()
        return membership

    return role_dependency
