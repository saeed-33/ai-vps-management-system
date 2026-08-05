from typing import Protocol
from concurrent.futures import ThreadPoolExecutor

from ai_vps_agent.periodic_monitoring.models import AgentMonitoringCollection, AgentMonitoringMetricSample, AgentServer
from ai_vps_agent.server_access.models import CommandResult
from ai_vps_agent.server_access.ssh_client import SshCommandClient
from ai_vps_agent.tools.parsers import parse_baseline_results
from ai_vps_agent.tools.registry import BASELINE_TOOL_CODES, baseline_command_policy


class BaselineCollector(Protocol):
    def collect(self, server: AgentServer, profile_ids: list[str]) -> AgentMonitoringCollection:
        """Collect read-only baseline evidence for a server."""


class FixtureBaselineCollector:
    def collect(self, server: AgentServer, profile_ids: list[str]) -> AgentMonitoringCollection:
        metrics: list[AgentMonitoringMetricSample] = []
        for profile_id in profile_ids:
            domain = "system" if profile_id == "profile-linux-baseline" else "unknown"
            metrics.extend(
                [
                    AgentMonitoringMetricSample(
                        metric="cpu_usage_percent",
                        domain=domain,
                        value=12.5,
                        unit="percent",
                        source_tool="uptime",
                    ),
                    AgentMonitoringMetricSample(
                        metric="memory_usage_percent",
                        domain=domain,
                        value=43.2,
                        unit="percent",
                        source_tool="free",
                    ),
                    AgentMonitoringMetricSample(
                        metric="load_1m_per_core",
                        domain=domain,
                        value=0.18,
                        unit="ratio",
                        source_tool="uptime",
                    ),
                    AgentMonitoringMetricSample(
                        metric="root_disk_usage_percent",
                        domain=domain,
                        value=38.7,
                        unit="percent",
                        source_tool="df",
                    ),
                    AgentMonitoringMetricSample(
                        metric="failed_systemd_units",
                        domain=domain,
                        value=0,
                        unit="count",
                        source_tool="systemctl_status",
                    ),
                ]
            )
        return AgentMonitoringCollection(
            metrics=metrics,
            raw_snapshot={
                "collector": self.__class__.__name__,
                "server_id": server.id,
                "server_name": server.name,
                "profile_ids": profile_ids,
                "samples": {sample.metric: sample.value for sample in metrics},
                "command_results": [],
            },
        )


class SshBaselineCollector:
    def collect(self, server: AgentServer, profile_ids: list[str]) -> AgentMonitoringCollection:
        if server.ssh is None:
            raise ValueError("SSH access is required for SshBaselineCollector")
        return _run_async_collect(server)


async def _collect_over_ssh(server: AgentServer) -> AgentMonitoringCollection:
    if server.ssh is None:
        raise ValueError("SSH access is required for SshBaselineCollector")
    client = SshCommandClient(server.ssh, baseline_command_policy())
    results: list[CommandResult] = []
    for tool_code in BASELINE_TOOL_CODES:
        results.append(await client.run_tool(tool_code))
    metrics = parse_baseline_results(results)
    return AgentMonitoringCollection(
        metrics=metrics,
        raw_snapshot={
            "collector": SshBaselineCollector.__name__,
            "server_id": server.id,
            "server_name": server.name,
            "profile_ids": server.monitoring_profiles,
            "samples": {sample.metric: sample.value for sample in metrics},
            "command_results": [result.model_dump() for result in results],
        },
    )


def _run_async_collect(server: AgentServer) -> AgentMonitoringCollection:
    import asyncio

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_collect_over_ssh(server))

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(lambda: asyncio.run(_collect_over_ssh(server))).result()


class HybridBaselineCollector:
    def __init__(self) -> None:
        self._fixture = FixtureBaselineCollector()
        self._ssh = SshBaselineCollector()

    def collect(self, server: AgentServer, profile_ids: list[str]) -> AgentMonitoringCollection:
        if server.ssh is None:
            return self._fixture.collect(server, profile_ids)
        return self._ssh.collect(server, profile_ids)
