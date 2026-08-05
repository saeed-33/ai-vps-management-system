import asyncio
from contextlib import suppress
from datetime import UTC, datetime, timedelta

from ai_vps_agent.periodic_monitoring import AgentPeriodicMonitoringCycleReport, AgentServer
from ai_vps_agent.periodic_monitoring.collectors import HybridBaselineCollector
from ai_vps_agent.periodic_monitoring.orchestrator import PeriodicMonitoringAgent
from ai_vps_agent.server_access.models import SshServerAccess

from control_plane_api.core.config import Settings, get_settings
from control_plane_api.modules.servers.service import get_active_agent_servers, get_server_ssh_access_config
from control_plane_api.modules.periodic_monitoring.analysis import analyze_server_report
from control_plane_api.modules.periodic_monitoring.analysis_reports import build_analysis_reports
from control_plane_api.modules.periodic_monitoring.llm_analysis import analyze_report_with_llm
from control_plane_api.modules.periodic_monitoring.persistence import (
    load_periodic_monitoring_cycles,
    persist_periodic_monitoring_cycle,
)
from control_plane_api.schemas.periodic_monitoring import (
    PeriodicMonitoringAnalysisReportsListResponse,
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


async def run_periodic_monitoring_cycle(
    *,
    trigger: str = "manual",
    settings: Settings | None = None,
) -> PeriodicMonitoringCycleReport:
    global SCHEDULER_LAST_ERROR

    settings = settings or get_settings()
    cycle = _to_api_cycle(MONITORING_AGENT.run_cycle(servers=await _get_agent_servers(settings), trigger=trigger))
    cycle = await _with_analysis(cycle, settings)
    RECENT_CYCLES.insert(0, cycle)
    del RECENT_CYCLES[10:]
    try:
        await persist_periodic_monitoring_cycle(cycle, settings)
    except Exception as exc:  # pragma: no cover - database availability depends on local environment.
        SCHEDULER_LAST_ERROR = f"database persistence skipped: {exc.__class__.__name__}: {exc}"
    return cycle


async def start_periodic_monitoring_scheduler(
    interval_seconds: int,
    *,
    settings: Settings | None = None,
) -> PeriodicMonitoringSchedulerStatus:
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
    first_cycle = await run_periodic_monitoring_cycle(trigger="scheduler", settings=settings)
    SCHEDULER_LAST_RUN_AT = first_cycle.completed_at
    SCHEDULER_RUNS_COUNT = 1
    SCHEDULER_NEXT_RUN_AT = datetime.now(UTC) + timedelta(seconds=interval_seconds)
    SCHEDULER_TASK = asyncio.create_task(_scheduler_loop(interval_seconds, settings=settings))
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


async def _scheduler_loop(interval_seconds: int, *, settings: Settings | None = None) -> None:
    global SCHEDULER_LAST_ERROR
    global SCHEDULER_LAST_RUN_AT
    global SCHEDULER_NEXT_RUN_AT
    global SCHEDULER_RUNS_COUNT

    while True:
        SCHEDULER_NEXT_RUN_AT = datetime.now(UTC) + timedelta(seconds=interval_seconds)
        await asyncio.sleep(interval_seconds)
        try:
            cycle = await run_periodic_monitoring_cycle(trigger="scheduler", settings=settings)
            SCHEDULER_LAST_RUN_AT = cycle.completed_at
            SCHEDULER_RUNS_COUNT += 1
            SCHEDULER_LAST_ERROR = None
        except Exception as exc:  # pragma: no cover - defensive scheduler boundary
            SCHEDULER_LAST_ERROR = str(exc)


async def list_periodic_monitoring_cycles(settings: Settings | None = None) -> PeriodicMonitoringCyclesListResponse:
    settings = settings or get_settings()
    try:
        persisted_cycles = await load_periodic_monitoring_cycles(settings)
    except Exception:  # pragma: no cover - database availability depends on local environment.
        persisted_cycles = None
    if persisted_cycles is not None:
        return PeriodicMonitoringCyclesListResponse(cycles=persisted_cycles)
    return PeriodicMonitoringCyclesListResponse(cycles=RECENT_CYCLES)


async def get_latest_periodic_monitoring_cycle(settings: Settings | None = None) -> PeriodicMonitoringCycleReport | None:
    settings = settings or get_settings()
    try:
        persisted_cycles = await load_periodic_monitoring_cycles(settings, limit=1)
    except Exception:  # pragma: no cover - database availability depends on local environment.
        persisted_cycles = None
    if persisted_cycles:
        return persisted_cycles[0]
    return RECENT_CYCLES[0] if RECENT_CYCLES else None


async def list_periodic_monitoring_reports(settings: Settings | None = None) -> PeriodicMonitoringReportsListResponse:
    cycles = (await list_periodic_monitoring_cycles(settings)).cycles
    reports = [report for cycle in RECENT_CYCLES for report in cycle.reports]
    if cycles:
        reports = [report for cycle in cycles for report in cycle.reports]
    return PeriodicMonitoringReportsListResponse(reports=reports)


async def list_periodic_monitoring_analysis_reports(
    settings: Settings | None = None,
) -> PeriodicMonitoringAnalysisReportsListResponse:
    cycles = (await list_periodic_monitoring_cycles(settings)).cycles
    return PeriodicMonitoringAnalysisReportsListResponse(analysis_reports=build_analysis_reports(cycles))


async def _get_agent_servers(settings: Settings) -> list[AgentServer]:
    servers = await get_active_agent_servers(settings)
    return [
        AgentServer(
            id=server.id,
            name=server.name,
            hostname=server.hostname,
            status=server.status,
            monitoring_profiles=server.assigned_monitoring_profiles or DEFAULT_PROFILE_IDS,
            ssh=await _server_ssh_access(server.id, settings),
        )
        for server in servers
    ]


def _to_api_cycle(agent_cycle: AgentPeriodicMonitoringCycleReport) -> PeriodicMonitoringCycleReport:
    return PeriodicMonitoringCycleReport.model_validate(agent_cycle.model_dump())


async def _with_analysis(cycle: PeriodicMonitoringCycleReport, settings: Settings) -> PeriodicMonitoringCycleReport:
    reports = []
    for report in cycle.reports:
        rule_signals = analyze_server_report(report)
        llm_analysis = await analyze_report_with_llm(
            report=report,
            rule_signals=rule_signals,
            settings=settings,
        )
        reports.append(report.model_copy(update={"analysis": llm_analysis}))
    return cycle.model_copy(
        update={
            "reports": reports
        }
    )


async def _server_ssh_access(server_id: str, settings: Settings) -> SshServerAccess | None:
    configured_access = await get_server_ssh_access_config(settings, server_id)
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
