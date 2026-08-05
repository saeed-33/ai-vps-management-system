from ai_vps_agent.server_access.models import CommandResult
from ai_vps_agent.tools.parsers import parse_baseline_results


def test_parse_baseline_results() -> None:
    metrics = parse_baseline_results(
        [
            CommandResult(
                tool_code="uptime",
                command="uptime",
                exit_status=0,
                stdout="10:10:10 up 1 day, 1 user, load average: 0.12, 0.20, 0.30",
                stderr="",
            ),
            CommandResult(
                tool_code="free_m",
                command="free -m",
                exit_status=0,
                stdout="              total        used        free\nMem:           1000         250         750\n",
                stderr="",
            ),
            CommandResult(
                tool_code="df_portable",
                command="df -P -T",
                exit_status=0,
                stdout="Filesystem Type 1024-blocks Used Available Capacity Mounted on\n/dev/sda1 ext4 100 40 60 40% /\n",
                stderr="",
            ),
            CommandResult(
                tool_code="systemctl_failed",
                command="systemctl --failed --no-pager",
                exit_status=0,
                stdout="0 loaded units listed.",
                stderr="",
            ),
        ]
    )

    values = {metric.metric: metric.value for metric in metrics}
    assert values["load_1m"] == 0.12
    assert values["memory_usage_percent"] == 25.0
    assert values["root_disk_usage_percent"] == 40.0
    assert values["failed_systemd_units"] == 0
