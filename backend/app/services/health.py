from app.core.config import Settings
from app.schemas.health import HealthResponse


def build_health_response(settings: Settings) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="resolveops-api",
        version=settings.app_version,
    )
