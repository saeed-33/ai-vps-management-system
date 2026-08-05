from typing import Protocol

from ai_vps_agent.periodic_monitoring.models import AgentMonitoringMetricSample, AgentServer


class BaselineCollector(Protocol):
    def collect(self, server: AgentServer, profile_ids: list[str]) -> list[AgentMonitoringMetricSample]:
        """Collect read-only baseline metrics for a server."""


class FixtureBaselineCollector:
    def collect(self, server: AgentServer, profile_ids: list[str]) -> list[AgentMonitoringMetricSample]:
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
        return metrics
