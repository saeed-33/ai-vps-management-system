import asyncio
from contextlib import suppress
from datetime import UTC, datetime, timedelta

from ai_vps_agent.periodic_monitoring import AgentPeriodicMonitoringCycleReport, AgentServer
from ai_vps_agent.periodic_monitoring.orchestrator import PeriodicMonitoringAgent

from control_plane_api.modules.servers.service import FOUNDATION_SERVERS
from control_plane_api.schemas.periodic_monitoring import (
    PeriodicMonitoringCycleReport,
    PeriodicMonitoringCyclesListResponse,
    PeriodicMonitoringReportsListResponse,
    PeriodicMonitoringSchedulerStatus,
)

DEFAULT_PROFILE_IDS = ["profile-linux-baseline"]
RECENT_CYCLES: list[PeriodicMonitoringCycleReport] = []
MONITORING_AGENT = PeriodicMonitoringAgent()
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
    return [
        AgentServer(
            id=server.id,
            name=server.name,
            hostname=server.hostname,
            status=server.status,
            monitoring_profiles=server.assigned_monitoring_profiles or DEFAULT_PROFILE_IDS,
        )
        for server in FOUNDATION_SERVERS
    ]


def _to_api_cycle(agent_cycle: AgentPeriodicMonitoringCycleReport) -> PeriodicMonitoringCycleReport:
    return PeriodicMonitoringCycleReport.model_validate(agent_cycle.model_dump())
