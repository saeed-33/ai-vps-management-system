import re

from ai_vps_agent.periodic_monitoring.models import AgentMonitoringMetricSample
from ai_vps_agent.server_access.models import CommandResult


def parse_baseline_results(results: list[CommandResult]) -> list[AgentMonitoringMetricSample]:
    metrics: list[AgentMonitoringMetricSample] = []
    for result in results:
        if result.tool_code == "uptime":
            metrics.extend(parse_uptime(result.stdout))
        elif result.tool_code == "free_m":
            metrics.extend(parse_free_m(result.stdout))
        elif result.tool_code == "df_portable":
            metrics.extend(parse_df_portable(result.stdout))
        elif result.tool_code == "systemctl_failed":
            metrics.extend(parse_systemctl_failed(result.stdout))
    return metrics


def parse_uptime(stdout: str) -> list[AgentMonitoringMetricSample]:
    match = re.search(r"load average[s]?:\s*([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)", stdout)
    if match is None:
        return []
    return [
        AgentMonitoringMetricSample(
            metric="load_1m",
            domain="system",
            value=float(match.group(1)),
            unit="load",
            source_tool="uptime",
        ),
        AgentMonitoringMetricSample(
            metric="load_5m",
            domain="system",
            value=float(match.group(2)),
            unit="load",
            source_tool="uptime",
        ),
        AgentMonitoringMetricSample(
            metric="load_15m",
            domain="system",
            value=float(match.group(3)),
            unit="load",
            source_tool="uptime",
        ),
    ]


def parse_free_m(stdout: str) -> list[AgentMonitoringMetricSample]:
    for line in stdout.splitlines():
        parts = line.split()
        if parts and parts[0].rstrip(":").lower() == "mem" and len(parts) >= 3:
            total = float(parts[1])
            used = float(parts[2])
            usage = round((used / total) * 100, 2) if total else 0.0
            return [
                AgentMonitoringMetricSample(
                    metric="memory_usage_percent",
                    domain="system",
                    value=usage,
                    unit="percent",
                    source_tool="free_m",
                )
            ]
    return []


def parse_df_portable(stdout: str) -> list[AgentMonitoringMetricSample]:
    root_usage = None
    for line in stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 7 and parts[-1] == "/":
            usage_text = parts[-2].rstrip("%")
            root_usage = float(usage_text)
            break
    if root_usage is None:
        return []
    return [
        AgentMonitoringMetricSample(
            metric="root_disk_usage_percent",
            domain="storage",
            value=root_usage,
            unit="percent",
            source_tool="df_portable",
        )
    ]


def parse_systemctl_failed(stdout: str) -> list[AgentMonitoringMetricSample]:
    if "0 loaded units listed" in stdout or "0 failed units listed" in stdout:
        failed_count = 0
    else:
        failed_count = sum(1 for line in stdout.splitlines() if " failed " in f" {line} ")
    return [
        AgentMonitoringMetricSample(
            metric="failed_systemd_units",
            domain="services",
            value=failed_count,
            unit="count",
            source_tool="systemctl_failed",
        )
    ]
