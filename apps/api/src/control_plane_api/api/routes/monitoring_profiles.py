from fastapi import APIRouter, Depends, HTTPException, Request, status

from control_plane_api.api.dependencies import get_current_principal
from control_plane_api.modules.monitoring_profiles.service import (
    MonitoringProfilePersistenceError,
    create_monitoring_profile,
    get_monitoring_profile,
    list_monitoring_profiles,
    summarize_monitoring_profiles,
)
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.monitoring_profiles import (
    MonitoringProfileCreate,
    MonitoringProfileDetail,
    MonitoringProfilesListResponse,
    MonitoringProfilesSummaryResponse,
)

router = APIRouter(prefix="/monitoring-profiles", tags=["monitoring-profiles"])


def require_monitoring_read(principal: Principal) -> None:
    if "monitoring.read" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def require_monitoring_write(principal: Principal) -> None:
    if "monitoring.write" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


@router.get("", response_model=MonitoringProfilesListResponse)
async def monitoring_profiles(
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> MonitoringProfilesListResponse:
    require_monitoring_read(principal)
    return await list_monitoring_profiles(request.app.state.settings)


@router.post("", response_model=MonitoringProfileDetail, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: MonitoringProfileCreate,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> MonitoringProfileDetail:
    require_monitoring_write(principal)
    try:
        return await create_monitoring_profile(request.app.state.settings, payload)
    except MonitoringProfilePersistenceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/summary", response_model=MonitoringProfilesSummaryResponse)
async def monitoring_profiles_summary(
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> MonitoringProfilesSummaryResponse:
    require_monitoring_read(principal)
    return await summarize_monitoring_profiles(request.app.state.settings)


@router.get("/{profile_id}", response_model=MonitoringProfileDetail)
async def monitoring_profile_detail(
    profile_id: str,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> MonitoringProfileDetail:
    require_monitoring_read(principal)
    profile = await get_monitoring_profile(profile_id, request.app.state.settings)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring profile not found",
        )
    return profile
