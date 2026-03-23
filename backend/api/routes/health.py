from fastapi import APIRouter

from backend.api.models import HealthResponse
from backend.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.app_version)
