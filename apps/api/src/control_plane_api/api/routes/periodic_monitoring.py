from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_current_principal
from control_plane_api.modules.periodic_monitoring.service import (
    get_latest_periodic_monitoring_cycle,
    list_periodic_monitoring_cycles,
    list_periodic_monitoring_reports,
    run_periodic_monitoring_cycle,
)
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.periodic_monitoring import (
    PeriodicMonitoringCycleReport,
    PeriodicMonitoringCyclesListResponse,
    PeriodicMonitoringReportsListResponse,
)

router = APIRouter(prefix="/periodic-monitoring", tags=["periodic-monitoring"])


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


@router.post("/cycles", response_model=PeriodicMonitoringCycleReport)
async def start_periodic_monitoring_cycle(
    principal: Principal = Depends(get_current_principal),
) -> PeriodicMonitoringCycleReport:
    require_monitoring_write(principal)
    return run_periodic_monitoring_cycle()


@router.get("/cycles", response_model=PeriodicMonitoringCyclesListResponse)
async def periodic_monitoring_cycles(
    principal: Principal = Depends(get_current_principal),
) -> PeriodicMonitoringCyclesListResponse:
    require_monitoring_read(principal)
    return list_periodic_monitoring_cycles()


@router.get("/cycles/latest", response_model=PeriodicMonitoringCycleReport)
async def latest_periodic_monitoring_cycle(
    principal: Principal = Depends(get_current_principal),
) -> PeriodicMonitoringCycleReport:
    require_monitoring_read(principal)
    cycle = get_latest_periodic_monitoring_cycle()
    if cycle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No periodic monitoring cycle has been created",
        )
    return cycle


@router.get("/reports", response_model=PeriodicMonitoringReportsListResponse)
async def periodic_monitoring_reports(
    principal: Principal = Depends(get_current_principal),
) -> PeriodicMonitoringReportsListResponse:
    require_monitoring_read(principal)
    return list_periodic_monitoring_reports()
