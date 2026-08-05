from datetime import UTC, datetime
from uuid import uuid4

from ai_vps_agent.periodic_monitoring.collectors import BaselineCollector, FixtureBaselineCollector
from ai_vps_agent.periodic_monitoring.models import AgentPeriodicMonitoringCycleReport, AgentServer
from ai_vps_agent.periodic_monitoring.server_sub_agent import ServerSubAgent


class PeriodicMonitoringAgent:
    def __init__(self, collector: BaselineCollector | None = None) -> None:
        self._collector = collector or FixtureBaselineCollector()

    def run_cycle(self, *, servers: list[AgentServer], trigger: str) -> AgentPeriodicMonitoringCycleReport:
        started_at = datetime.now(UTC)
        active_servers = [server for server in servers if server.status == "active"]
        reports = [
            ServerSubAgent(server=server, collector=self._collector).collect_report(started_at=started_at)
            for server in active_servers
        ]
        completed_at = datetime.now(UTC)
        return AgentPeriodicMonitoringCycleReport(
            cycle_id=f"cycle-{uuid4()}",
            trigger=trigger,
            status="completed",
            started_at=started_at,
            completed_at=completed_at,
            servers_planned=len(active_servers),
            servers_checked=len(reports),
            reports_count=len(reports),
            reports=reports,
            scope_note="Periodic monitoring agent report collection only. No issue analysis, specialist agents, solutions, or execution.",
        )
