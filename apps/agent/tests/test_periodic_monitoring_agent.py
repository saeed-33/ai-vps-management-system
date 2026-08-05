from ai_vps_agent.periodic_monitoring import AgentServer
from ai_vps_agent.periodic_monitoring.collectors import HybridBaselineCollector
from ai_vps_agent.periodic_monitoring.orchestrator import PeriodicMonitoringAgent


def test_periodic_monitoring_agent_creates_report_per_active_server() -> None:
    agent = PeriodicMonitoringAgent()

    cycle = agent.run_cycle(
        trigger="manual",
        servers=[
            AgentServer(
                id="srv-1",
                name="server-one",
                hostname="server-one.local",
                status="active",
                monitoring_profiles=["profile-linux-baseline"],
            ),
            AgentServer(
                id="srv-2",
                name="server-two",
                hostname="server-two.local",
                status="disabled",
                monitoring_profiles=["profile-linux-baseline"],
            ),
        ],
    )

    assert cycle.status == "completed"
    assert cycle.trigger == "manual"
    assert cycle.servers_planned == 1
    assert cycle.servers_checked == 1
    assert cycle.reports_count == 1
    assert cycle.reports[0].sub_agent_id == "server-sub-agent-srv-1"
    assert len(cycle.reports[0].metrics) == 5
    assert "No issue analysis" in cycle.scope_note


def test_hybrid_collector_uses_fixture_without_ssh_access() -> None:
    collector = HybridBaselineCollector()
    server = AgentServer(
        id="srv-1",
        name="server-one",
        hostname="server-one.local",
        status="active",
        monitoring_profiles=["profile-linux-baseline"],
    )

    metrics = collector.collect(server, server.monitoring_profiles)

    assert len(metrics) == 5
    assert {metric.source_tool for metric in metrics} == {"uptime", "free", "df", "systemctl_status"}
