from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.schemas.health import HealthResponse
from app.services.health import build_health_response

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(settings: SettingsDep) -> HealthResponse:
    return build_health_response(settings)
