from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db_session
from app.core.config import Settings, get_settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.models import Organization, OrganizationMembership, User
from app.domain.enums import OrganizationRole
from app.main import app


@pytest.fixture(scope="session")
def asgi_app() -> FastAPI:
    return app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@dataclass(frozen=True)
class Identity:
    user: User
    organization: Organization
    membership: OrganizationMembership
    token: str


@dataclass(frozen=True)
class ApiTestContext:
    client: AsyncClient
    session_factory: sessionmaker[Session]
    settings: Settings

    def create_identity(
        self,
        *,
        email: str,
        organization_name: str,
        organization_slug: str,
        role: OrganizationRole = OrganizationRole.OWNER,
    ) -> Identity:
        with self.session_factory() as session:
            user = User(
                email=email,
                hashed_password=hash_password("test-password-long-enough"),
                full_name=email.split("@", 1)[0].title(),
            )
            organization = Organization(
                name=organization_name,
                slug=organization_slug,
            )
            membership = OrganizationMembership(
                user=user,
                organization=organization,
                role=role,
            )
            session.add_all([user, organization, membership])
            session.commit()
            token = create_access_token(
                user_id=user.id,
                organization_id=organization.id,
                settings=self.settings,
            )
            return Identity(user, organization, membership, token)


@pytest.fixture
async def api_context(tmp_path: Path) -> AsyncGenerator[ApiTestContext]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    settings = Settings(
        _env_file=None,
        jwt_secret="test-secret-at-least-32-characters-long",
        upload_dir=tmp_path / "uploads",
        document_upload_dir=tmp_path / "documents",
        chroma_persist_dir=tmp_path / "chroma",
        max_upload_size_mb=1,
        max_document_upload_size_mb=1,
        dataset_max_rows=1_000,
        dataset_sample_size=3,
        document_chunk_size=100,
        document_chunk_overlap=15,
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
        yield ApiTestContext(client, testing_session, settings)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
