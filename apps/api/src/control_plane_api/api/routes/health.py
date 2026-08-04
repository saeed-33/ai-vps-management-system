from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from control_plane_api.api.dependencies import get_app_settings
from control_plane_api.core.config import Settings
from control_plane_api.core.database import check_database
from control_plane_api.schemas.health import LivenessResponse, ReadinessResponse

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/live", response_model=LivenessResponse)
async def live(settings: Settings = Depends(get_app_settings)) -> LivenessResponse:
    return LivenessResponse(
        service=settings.app_name,
        environment=settings.app_env,
        status="ok",
    )


@health_router.get("/ready", response_model=ReadinessResponse)
async def ready(settings: Settings = Depends(get_app_settings)) -> JSONResponse:
    database = await check_database(settings)
    response = ReadinessResponse(
        service=settings.app_name,
        environment=settings.app_env,
        ready=database.ok,
        components=[database],
    )
    status_code = status.HTTP_200_OK if response.ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=response.model_dump())
