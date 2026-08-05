from datetime import UTC, datetime

from ai_vps_agent.periodic_monitoring.collectors import BaselineCollector
from ai_vps_agent.periodic_monitoring.models import AgentServer, AgentServerSubAgentReport


class ServerSubAgent:
    def __init__(self, server: AgentServer, collector: BaselineCollector) -> None:
        self._server = server
        self._collector = collector

    def collect_report(self, *, started_at: datetime) -> AgentServerSubAgentReport:
        profile_ids = self._server.monitoring_profiles
        try:
            collection = self._collector.collect(self._server, profile_ids)
        except Exception as exc:
            completed_at = datetime.now(UTC)
            return AgentServerSubAgentReport(
                sub_agent_id=f"server-sub-agent-{self._server.id}",
                server_id=self._server.id,
                server_name=self._server.name,
                status="failed",
                started_at=started_at,
                completed_at=completed_at,
                monitoring_profiles=profile_ids,
                metrics=[],
                raw_snapshot={
                    "collector": self._collector.__class__.__name__,
                    "server_id": self._server.id,
                    "profile_ids": profile_ids,
                    "error_type": exc.__class__.__name__,
                    "error": str(exc),
                },
                collection_summary=f"Baseline metric collection failed: {exc.__class__.__name__}: {exc}",
            )

        completed_at = datetime.now(UTC)
        return AgentServerSubAgentReport(
            sub_agent_id=f"server-sub-agent-{self._server.id}",
            server_id=self._server.id,
            server_name=self._server.name,
            status="completed",
            started_at=started_at,
            completed_at=completed_at,
            monitoring_profiles=profile_ids,
            metrics=collection.metrics,
            raw_snapshot=collection.raw_snapshot,
            collection_summary="Baseline metrics collected successfully by periodic monitoring agent.",
        )
