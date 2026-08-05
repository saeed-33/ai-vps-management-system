from datetime import UTC, datetime
from uuid import uuid4

from control_plane_api.modules.monitoring_profiles.service import get_monitoring_profile
from control_plane_api.modules.servers.service import FOUNDATION_SERVERS
from control_plane_api.schemas.periodic_monitoring import (
    MonitoringMetricSample,
    PeriodicMonitoringCycleReport,
    PeriodicMonitoringCyclesListResponse,
    PeriodicMonitoringReportsListResponse,
    ServerSubAgentReport,
)

DEFAULT_PROFILE_IDS = ["profile-linux-baseline"]
RECENT_CYCLES: list[PeriodicMonitoringCycleReport] = []


def run_periodic_monitoring_cycle() -> PeriodicMonitoringCycleReport:
    started_at = datetime.now(UTC)
    active_servers = [server for server in FOUNDATION_SERVERS if server.status == "active"]
    reports = [_run_server_sub_agent(server_id=server.id, server_name=server.name, started_at=started_at) for server in active_servers]
    completed_at = datetime.now(UTC)
    cycle = PeriodicMonitoringCycleReport(
        cycle_id=f"cycle-{uuid4()}",
        status="completed",
        started_at=started_at,
        completed_at=completed_at,
        servers_planned=len(active_servers),
        servers_checked=len(reports),
        reports_count=len(reports),
        reports=reports,
        scope_note="Periodic monitoring report collection only. No issue analysis, specialist agents, solutions, or execution.",
    )
    RECENT_CYCLES.insert(0, cycle)
    del RECENT_CYCLES[10:]
    return cycle


def list_periodic_monitoring_cycles() -> PeriodicMonitoringCyclesListResponse:
    return PeriodicMonitoringCyclesListResponse(cycles=RECENT_CYCLES)


def get_latest_periodic_monitoring_cycle() -> PeriodicMonitoringCycleReport | None:
    return RECENT_CYCLES[0] if RECENT_CYCLES else None


def list_periodic_monitoring_reports() -> PeriodicMonitoringReportsListResponse:
    reports = [report for cycle in RECENT_CYCLES for report in cycle.reports]
    return PeriodicMonitoringReportsListResponse(reports=reports)


def _run_server_sub_agent(server_id: str, server_name: str, started_at: datetime) -> ServerSubAgentReport:
    profile_ids = DEFAULT_PROFILE_IDS
    metrics = _collect_baseline_metrics(profile_ids)
    completed_at = datetime.now(UTC)
    return ServerSubAgentReport(
        sub_agent_id=f"server-sub-agent-{server_id}",
        server_id=server_id,
        server_name=server_name,
        status="completed",
        started_at=started_at,
        completed_at=completed_at,
        monitoring_profiles=profile_ids,
        metrics=metrics,
        raw_snapshot={
            "collector": "foundation-fixture",
            "server_id": server_id,
            "profile_ids": profile_ids,
            "samples": {sample.metric: sample.value for sample in metrics},
        },
        collection_summary="Baseline metrics collected successfully from foundation fixture.",
    )


def _collect_baseline_metrics(profile_ids: list[str]) -> list[MonitoringMetricSample]:
    metrics: list[MonitoringMetricSample] = []
    for profile_id in profile_ids:
        profile = get_monitoring_profile(profile_id)
        if profile is None:
            continue
        metrics.extend(
            [
                MonitoringMetricSample(
                    metric="cpu_usage_percent",
                    domain=profile.domain,
                    value=12.5,
                    unit="percent",
                    source_tool="uptime",
                ),
                MonitoringMetricSample(
                    metric="memory_usage_percent",
                    domain=profile.domain,
                    value=43.2,
                    unit="percent",
                    source_tool="free",
                ),
                MonitoringMetricSample(
                    metric="load_1m_per_core",
                    domain=profile.domain,
                    value=0.18,
                    unit="ratio",
                    source_tool="uptime",
                ),
                MonitoringMetricSample(
                    metric="root_disk_usage_percent",
                    domain=profile.domain,
                    value=38.7,
                    unit="percent",
                    source_tool="df",
                ),
                MonitoringMetricSample(
                    metric="failed_systemd_units",
                    domain=profile.domain,
                    value=0,
                    unit="count",
                    source_tool="systemctl_status",
                ),
            ]
        )
    return metrics
