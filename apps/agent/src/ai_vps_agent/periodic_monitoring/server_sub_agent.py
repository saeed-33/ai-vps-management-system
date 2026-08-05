from datetime import UTC, datetime

from ai_vps_agent.periodic_monitoring.collectors import BaselineCollector
from ai_vps_agent.periodic_monitoring.models import AgentServer, AgentServerSubAgentReport


class ServerSubAgent:
    def __init__(self, server: AgentServer, collector: BaselineCollector) -> None:
        self._server = server
        self._collector = collector

    def collect_report(self, *, started_at: datetime) -> AgentServerSubAgentReport:
        profile_ids = self._server.monitoring_profiles
        metrics = self._collector.collect(self._server, profile_ids)
        completed_at = datetime.now(UTC)
        return AgentServerSubAgentReport(
            sub_agent_id=f"server-sub-agent-{self._server.id}",
            server_id=self._server.id,
            server_name=self._server.name,
            status="completed",
            started_at=started_at,
            completed_at=completed_at,
            monitoring_profiles=profile_ids,
            metrics=metrics,
            raw_snapshot={
                "collector": self._collector.__class__.__name__,
                "server_id": self._server.id,
                "profile_ids": profile_ids,
                "samples": {sample.metric: sample.value for sample in metrics},
            },
            collection_summary="Baseline metrics collected successfully by periodic monitoring agent.",
        )
