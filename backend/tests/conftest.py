import pytest
from fastapi import FastAPI

from app.main import app


@pytest.fixture(scope="session")
def asgi_app() -> FastAPI:
    return app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
