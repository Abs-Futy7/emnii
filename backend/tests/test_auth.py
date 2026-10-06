from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db_session
from app.core.config import Settings, get_settings
from app.db.models import Organization, OrganizationMembership, User
from app.main import app

REGISTER_PAYLOAD = {
    "email": "alice@example.com",
    "password": "correct-horse-battery-staple",
    "full_name": "Alice Morgan",
    "organization_name": "SupportOps Ltd",
}


@dataclass(frozen=True)
class AuthTestContext:
    client: AsyncClient
    session_factory: sessionmaker[Session]
    settings: Settings


@pytest.fixture
async def auth_context() -> AsyncGenerator[AuthTestContext]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    auth_tables = [
        User.__table__,
        Organization.__table__,
        OrganizationMembership.__table__,
    ]
    User.metadata.create_all(engine, tables=auth_tables)
    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    settings = Settings(
        _env_file=None,
        jwt_secret="test-secret-at-least-32-characters-long",
        jwt_access_token_expire_minutes=30,
    )

    def override_db_session() -> Generator[Session]:
        with testing_session() as session:
            yield session

    def override_settings() -> Settings:
        return settings

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield AuthTestContext(client, testing_session, settings)

    app.dependency_overrides.clear()
    engine.dispose()


async def register(context: AuthTestContext) -> None:
    response = await context.client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201, response.text


async def login(context: AuthTestContext) -> str:
    response = await context.client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.mark.anyio
async def test_register_creates_owner_and_hashes_password(
    auth_context: AuthTestContext,
) -> None:
    response = await auth_context.client.post(
        "/api/v1/auth/register",
        json=REGISTER_PAYLOAD,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["organization"]["slug"] == "supportops-ltd"
    assert body["membership"]["role"] == "owner"
    assert "password" not in str(body).lower()

    with auth_context.session_factory() as session:
        user = session.scalar(select(User).where(User.email == "alice@example.com"))
        assert user is not None
        assert user.hashed_password != REGISTER_PAYLOAD["password"]
        assert user.hashed_password.startswith("$argon2")


@pytest.mark.anyio
async def test_duplicate_email_returns_conflict(
    auth_context: AuthTestContext,
) -> None:
    await register(auth_context)

    response = await auth_context.client.post(
        "/api/v1/auth/register",
        json=REGISTER_PAYLOAD,
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "resource_conflict"


@pytest.mark.anyio
async def test_login_success(auth_context: AuthTestContext) -> None:
    await register(auth_context)

    response = await auth_context.client.post(
        "/api/v1/auth/login",
        json={
            "email": "alice@example.com",
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    token = response.json()["access_token"]
    claims = jwt.decode(
        token,
        auth_context.settings.jwt_secret,
        algorithms=[auth_context.settings.jwt_algorithm],
    )
    assert set(claims) == {"sub", "organization_id", "type", "iat", "exp"}


@pytest.mark.anyio
async def test_wrong_password_uses_generic_login_error(
    auth_context: AuthTestContext,
) -> None:
    await register(auth_context)

    wrong_password = await auth_context.client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "wrong-password"},
    )
    unknown_email = await auth_context.client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@example.com", "password": "wrong-password"},
    )

    assert wrong_password.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["error"]["message"] == "Invalid email or password"


@pytest.mark.anyio
async def test_me_authenticated(auth_context: AuthTestContext) -> None:
    await register(auth_context)
    token = await login(auth_context)

    response = await auth_context.client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "alice@example.com"
    assert response.json()["organization"]["slug"] == "supportops-ltd"
    assert response.json()["membership"]["role"] == "owner"


@pytest.mark.anyio
async def test_me_unauthenticated(auth_context: AuthTestContext) -> None:
    response = await auth_context.client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.anyio
async def test_me_rejects_expired_token(auth_context: AuthTestContext) -> None:
    now = datetime.now(UTC)
    expired_token = jwt.encode(
        {
            "sub": "7be6ca00-0553-45a5-a87a-96b320f47b4f",
            "organization_id": "45460344-16ac-4e9f-b08b-56cbe59c6303",
            "type": "access",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        },
        auth_context.settings.jwt_secret,
        algorithm=auth_context.settings.jwt_algorithm,
    )

    response = await auth_context.client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid or expired access token"
