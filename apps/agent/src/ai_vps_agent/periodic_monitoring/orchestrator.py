from datetime import UTC, datetime
from typing import TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from ai_vps_agent.periodic_monitoring.collectors import BaselineCollector, FixtureBaselineCollector
from ai_vps_agent.periodic_monitoring.models import AgentPeriodicMonitoringCycleReport, AgentServer, AgentServerSubAgentReport
from ai_vps_agent.periodic_monitoring.server_sub_agent import ServerSubAgent


class PeriodicMonitoringGraphState(TypedDict):
    trigger: str
    servers: list[AgentServer]
    active_servers: list[AgentServer]
    started_at: datetime
    reports: list[AgentServerSubAgentReport]


class PeriodicMonitoringAgent:
    def __init__(self, collector: BaselineCollector | None = None) -> None:
        self._collector = collector or FixtureBaselineCollector()
        self._graph = self._build_graph()

    def run_cycle(self, *, servers: list[AgentServer], trigger: str) -> AgentPeriodicMonitoringCycleReport:
        started_at = datetime.now(UTC)
        state = self._graph.invoke(
            {
                "trigger": trigger,
                "servers": servers,
                "active_servers": [],
                "started_at": started_at,
                "reports": [],
            }
        )
        active_servers = state["active_servers"]
        reports = state["reports"]
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
            scope_note="Periodic monitoring collection completed. Control plane analysis is applied after collection. No specialist agents, solutions, or execution.",
        )

    def _build_graph(self):
        graph = StateGraph(PeriodicMonitoringGraphState)
        graph.add_node("select_active_servers", self._select_active_servers)
        graph.add_node("collect_server_reports", self._collect_server_reports)
        graph.add_edge(START, "select_active_servers")
        graph.add_edge("select_active_servers", "collect_server_reports")
        graph.add_edge("collect_server_reports", END)
        return graph.compile()

    def _select_active_servers(self, state: PeriodicMonitoringGraphState) -> dict[str, list[AgentServer]]:
        return {"active_servers": [server for server in state["servers"] if server.status == "active"]}

    def _collect_server_reports(
        self,
        state: PeriodicMonitoringGraphState,
    ) -> dict[str, list[AgentServerSubAgentReport]]:
        return {
            "reports": [
                ServerSubAgent(server=server, collector=self._collector).collect_report(started_at=state["started_at"])
                for server in state["active_servers"]
            ]
        }
