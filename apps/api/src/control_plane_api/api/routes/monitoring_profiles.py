from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_current_principal
from control_plane_api.modules.monitoring_profiles.service import (
    get_monitoring_profile,
    list_monitoring_profiles,
    summarize_monitoring_profiles,
)
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.monitoring_profiles import (
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


@router.get("", response_model=MonitoringProfilesListResponse)
async def monitoring_profiles(
    principal: Principal = Depends(get_current_principal),
) -> MonitoringProfilesListResponse:
    require_monitoring_read(principal)
    return list_monitoring_profiles()


@router.get("/summary", response_model=MonitoringProfilesSummaryResponse)
async def monitoring_profiles_summary(
    principal: Principal = Depends(get_current_principal),
) -> MonitoringProfilesSummaryResponse:
    require_monitoring_read(principal)
    return summarize_monitoring_profiles()


@router.get("/{profile_id}", response_model=MonitoringProfileDetail)
async def monitoring_profile_detail(
    profile_id: str,
    principal: Principal = Depends(get_current_principal),
) -> MonitoringProfileDetail:
    require_monitoring_read(principal)
    profile = get_monitoring_profile(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring profile not found",
        )
    return profile
