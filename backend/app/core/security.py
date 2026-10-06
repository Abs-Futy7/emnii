from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError
from pydantic import BaseModel, ValidationError

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, ConfigurationError

password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash("resolveops-dummy-password")


class TokenPayload(BaseModel):
    sub: UUID
    organization_id: UUID
    type: str
    iat: datetime
    exp: datetime


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(password, hashed_password)
    except PwdlibError:
        return False


def verify_password_and_update(
    password: str,
    hashed_password: str,
) -> tuple[bool, str | None]:
    try:
        return password_hash.verify_and_update(password, hashed_password)
    except PwdlibError:
        return False, None


def perform_dummy_password_check(password: str) -> None:
    password_hash.verify(password, DUMMY_PASSWORD_HASH)


def create_access_token(
    *,
    user_id: UUID,
    organization_id: UUID,
    settings: Settings,
) -> str:
    secret = _require_jwt_secret(settings)
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    claims = {
        "sub": str(user_id),
        "organization_id": str(organization_id),
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(claims, secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> TokenPayload:
    secret = _require_jwt_secret(settings)
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "organization_id", "type", "iat", "exp"]},
        )
        payload = TokenPayload.model_validate(claims)
    except (jwt.InvalidTokenError, ValidationError) as exc:
        raise AuthenticationError("Invalid or expired access token") from exc

    if payload.type != "access":
        raise AuthenticationError("Invalid or expired access token")
    return payload


def _require_jwt_secret(settings: Settings) -> str:
    if len(settings.jwt_secret) < 32:
        raise ConfigurationError("JWT_SECRET must contain at least 32 characters")
    return settings.jwt_secret
