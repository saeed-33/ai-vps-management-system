from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_app_settings, get_current_principal
from control_plane_api.core.config import Settings
from control_plane_api.modules.periodic_monitoring.service import (
    get_periodic_monitoring_scheduler_status,
    get_latest_periodic_monitoring_cycle,
    list_periodic_monitoring_analysis_reports,
    list_periodic_monitoring_cycles,
    list_periodic_monitoring_reports,
    run_periodic_monitoring_cycle,
    start_periodic_monitoring_scheduler,
    stop_periodic_monitoring_scheduler,
)
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.periodic_monitoring import (
    PeriodicMonitoringCycleReport,
    PeriodicMonitoringCyclesListResponse,
    PeriodicMonitoringAnalysisReportsListResponse,
    PeriodicMonitoringReportsListResponse,
    PeriodicMonitoringSchedulerStartRequest,
    PeriodicMonitoringSchedulerStatus,
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
    settings: Settings = Depends(get_app_settings),
) -> PeriodicMonitoringCycleReport:
    require_monitoring_write(principal)
    return await run_periodic_monitoring_cycle(settings=settings)


@router.get("/cycles", response_model=PeriodicMonitoringCyclesListResponse)
async def periodic_monitoring_cycles(
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> PeriodicMonitoringCyclesListResponse:
    require_monitoring_read(principal)
    return await list_periodic_monitoring_cycles(settings)


@router.get("/cycles/latest", response_model=PeriodicMonitoringCycleReport)
async def latest_periodic_monitoring_cycle(
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> PeriodicMonitoringCycleReport:
    require_monitoring_read(principal)
    cycle = await get_latest_periodic_monitoring_cycle(settings)
    if cycle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No periodic monitoring cycle has been created",
        )
    return cycle


@router.get("/reports", response_model=PeriodicMonitoringReportsListResponse)
async def periodic_monitoring_reports(
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> PeriodicMonitoringReportsListResponse:
    require_monitoring_read(principal)
    return await list_periodic_monitoring_reports(settings)


@router.get("/analysis-reports", response_model=PeriodicMonitoringAnalysisReportsListResponse)
async def periodic_monitoring_analysis_reports(
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> PeriodicMonitoringAnalysisReportsListResponse:
    require_monitoring_read(principal)
    return await list_periodic_monitoring_analysis_reports(settings)


@router.post("/scheduler/start", response_model=PeriodicMonitoringSchedulerStatus)
async def start_scheduler(
    payload: PeriodicMonitoringSchedulerStartRequest,
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> PeriodicMonitoringSchedulerStatus:
    require_monitoring_write(principal)
    return await start_periodic_monitoring_scheduler(payload.interval_seconds, settings=settings)


@router.post("/scheduler/stop", response_model=PeriodicMonitoringSchedulerStatus)
async def stop_scheduler(
    principal: Principal = Depends(get_current_principal),
) -> PeriodicMonitoringSchedulerStatus:
    require_monitoring_write(principal)
    return await stop_periodic_monitoring_scheduler()


@router.get("/scheduler/status", response_model=PeriodicMonitoringSchedulerStatus)
async def scheduler_status(
    principal: Principal = Depends(get_current_principal),
) -> PeriodicMonitoringSchedulerStatus:
    require_monitoring_read(principal)
    return get_periodic_monitoring_scheduler_status()
