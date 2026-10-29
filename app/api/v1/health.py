from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services import health as health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report whether the API and its dependencies are reachable."""
    return health_service.get_health()
