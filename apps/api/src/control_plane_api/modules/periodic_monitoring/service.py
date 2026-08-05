import asyncio
from contextlib import suppress
from datetime import UTC, datetime, timedelta

from ai_vps_agent.periodic_monitoring import AgentPeriodicMonitoringCycleReport, AgentServer
from ai_vps_agent.periodic_monitoring.collectors import HybridBaselineCollector
from ai_vps_agent.periodic_monitoring.orchestrator import PeriodicMonitoringAgent
from ai_vps_agent.server_access.models import SshServerAccess

from control_plane_api.core.config import get_settings
from control_plane_api.modules.servers.service import FOUNDATION_SERVERS, get_server_ssh_access_config
from control_plane_api.schemas.periodic_monitoring import (
    PeriodicMonitoringCycleReport,
    PeriodicMonitoringCyclesListResponse,
    PeriodicMonitoringReportsListResponse,
    PeriodicMonitoringSchedulerStatus,
)

DEFAULT_PROFILE_IDS = ["profile-linux-baseline"]
RECENT_CYCLES: list[PeriodicMonitoringCycleReport] = []
MONITORING_AGENT = PeriodicMonitoringAgent(collector=HybridBaselineCollector())
SCHEDULER_TASK: asyncio.Task[None] | None = None
SCHEDULER_INTERVAL_SECONDS: int | None = None
SCHEDULER_STARTED_AT: datetime | None = None
SCHEDULER_LAST_RUN_AT: datetime | None = None
SCHEDULER_NEXT_RUN_AT: datetime | None = None
SCHEDULER_RUNS_COUNT = 0
SCHEDULER_LAST_ERROR: str | None = None


def run_periodic_monitoring_cycle(*, trigger: str = "manual") -> PeriodicMonitoringCycleReport:
    cycle = _to_api_cycle(MONITORING_AGENT.run_cycle(servers=_get_agent_servers(), trigger=trigger))
    RECENT_CYCLES.insert(0, cycle)
    del RECENT_CYCLES[10:]
    return cycle


async def start_periodic_monitoring_scheduler(interval_seconds: int) -> PeriodicMonitoringSchedulerStatus:
    global SCHEDULER_INTERVAL_SECONDS
    global SCHEDULER_LAST_ERROR
    global SCHEDULER_LAST_RUN_AT
    global SCHEDULER_NEXT_RUN_AT
    global SCHEDULER_RUNS_COUNT
    global SCHEDULER_STARTED_AT
    global SCHEDULER_TASK

    if SCHEDULER_TASK is not None and not SCHEDULER_TASK.done():
        return get_periodic_monitoring_scheduler_status()

    SCHEDULER_INTERVAL_SECONDS = interval_seconds
    SCHEDULER_STARTED_AT = datetime.now(UTC)
    SCHEDULER_LAST_ERROR = None
    SCHEDULER_RUNS_COUNT = 0
    first_cycle = run_periodic_monitoring_cycle(trigger="scheduler")
    SCHEDULER_LAST_RUN_AT = first_cycle.completed_at
    SCHEDULER_RUNS_COUNT = 1
    SCHEDULER_NEXT_RUN_AT = datetime.now(UTC) + timedelta(seconds=interval_seconds)
    SCHEDULER_TASK = asyncio.create_task(_scheduler_loop(interval_seconds))
    return get_periodic_monitoring_scheduler_status()


async def stop_periodic_monitoring_scheduler() -> PeriodicMonitoringSchedulerStatus:
    global SCHEDULER_NEXT_RUN_AT
    global SCHEDULER_TASK

    if SCHEDULER_TASK is not None and not SCHEDULER_TASK.done():
        SCHEDULER_TASK.cancel()
        with suppress(asyncio.CancelledError):
            await SCHEDULER_TASK

    SCHEDULER_TASK = None
    SCHEDULER_NEXT_RUN_AT = None
    return get_periodic_monitoring_scheduler_status()


def get_periodic_monitoring_scheduler_status() -> PeriodicMonitoringSchedulerStatus:
    enabled = SCHEDULER_TASK is not None and not SCHEDULER_TASK.done()
    return PeriodicMonitoringSchedulerStatus(
        enabled=enabled,
        interval_seconds=SCHEDULER_INTERVAL_SECONDS if enabled else None,
        started_at=SCHEDULER_STARTED_AT if enabled else None,
        last_run_at=SCHEDULER_LAST_RUN_AT,
        next_run_at=SCHEDULER_NEXT_RUN_AT if enabled else None,
        runs_count=SCHEDULER_RUNS_COUNT,
        last_error=SCHEDULER_LAST_ERROR,
    )


async def _scheduler_loop(interval_seconds: int) -> None:
    global SCHEDULER_LAST_ERROR
    global SCHEDULER_LAST_RUN_AT
    global SCHEDULER_NEXT_RUN_AT
    global SCHEDULER_RUNS_COUNT

    while True:
        SCHEDULER_NEXT_RUN_AT = datetime.now(UTC) + timedelta(seconds=interval_seconds)
        await asyncio.sleep(interval_seconds)
        try:
            cycle = run_periodic_monitoring_cycle(trigger="scheduler")
            SCHEDULER_LAST_RUN_AT = cycle.completed_at
            SCHEDULER_RUNS_COUNT += 1
            SCHEDULER_LAST_ERROR = None
        except Exception as exc:  # pragma: no cover - defensive scheduler boundary
            SCHEDULER_LAST_ERROR = str(exc)


def list_periodic_monitoring_cycles() -> PeriodicMonitoringCyclesListResponse:
    return PeriodicMonitoringCyclesListResponse(cycles=RECENT_CYCLES)


def get_latest_periodic_monitoring_cycle() -> PeriodicMonitoringCycleReport | None:
    return RECENT_CYCLES[0] if RECENT_CYCLES else None


def list_periodic_monitoring_reports() -> PeriodicMonitoringReportsListResponse:
    reports = [report for cycle in RECENT_CYCLES for report in cycle.reports]
    return PeriodicMonitoringReportsListResponse(reports=reports)


def _get_agent_servers() -> list[AgentServer]:
    settings = get_settings()
    return [
        AgentServer(
            id=server.id,
            name=server.name,
            hostname=server.hostname,
            status=server.status,
            monitoring_profiles=server.assigned_monitoring_profiles or DEFAULT_PROFILE_IDS,
            ssh=_server_ssh_access(server.id, settings),
        )
        for server in FOUNDATION_SERVERS
    ]


def _to_api_cycle(agent_cycle: AgentPeriodicMonitoringCycleReport) -> PeriodicMonitoringCycleReport:
    return PeriodicMonitoringCycleReport.model_validate(agent_cycle.model_dump())


def _server_ssh_access(server_id: str, settings: object) -> SshServerAccess | None:
    configured_access = get_server_ssh_access_config(server_id)
    if configured_access is not None and configured_access.enabled:
        if not configured_access.host or not configured_access.username:
            return None
        return SshServerAccess(
            host=configured_access.host,
            port=configured_access.port,
            username=configured_access.username,
            private_key_path=configured_access.private_key_path,
            password=configured_access.password,
        )
    return _foundation_ssh_access(server_id, settings)


def _foundation_ssh_access(server_id: str, settings: object) -> SshServerAccess | None:
    if server_id != "srv-foundation-001":
        return None
    if not getattr(settings, "foundation_server_ssh_enabled"):
        return None
    host = str(getattr(settings, "foundation_server_ssh_host"))
    username = str(getattr(settings, "foundation_server_ssh_username"))
    if not host or not username:
        return None
    return SshServerAccess(
        host=host,
        port=int(getattr(settings, "foundation_server_ssh_port")),
        username=username,
        private_key_path=getattr(settings, "foundation_server_ssh_private_key_path"),
        password=getattr(settings, "foundation_server_ssh_password"),
    )
