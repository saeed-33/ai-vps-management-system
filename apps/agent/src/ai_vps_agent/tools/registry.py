from ai_vps_agent.server_access.command_policy import AllowedCommand, CommandPolicy
from ai_vps_agent.periodic_monitoring.models import AgentMonitoringInstruction

DEFAULT_BASELINE_INSTRUCTIONS = [
    AgentMonitoringInstruction(
        id="linux-baseline-uptime",
        title="Collect load average and uptime",
        tool_code="uptime",
        command="uptime",
        purpose="Capture uptime and load averages.",
        parser="uptime",
        expected_evidence=["uptime", "load average"],
    ),
    AgentMonitoringInstruction(
        id="linux-baseline-memory",
        title="Collect memory usage",
        tool_code="free_m",
        command="free -m",
        purpose="Capture memory totals and usage.",
        parser="free_m",
        expected_evidence=["Mem", "Swap"],
    ),
    AgentMonitoringInstruction(
        id="linux-baseline-filesystems",
        title="Collect mounted filesystem usage",
        tool_code="df_portable",
        command="df -P -T",
        purpose="Capture portable filesystem usage.",
        parser="df_portable",
        expected_evidence=["Filesystem", "Mounted on"],
    ),
    AgentMonitoringInstruction(
        id="linux-baseline-failed-units",
        title="Collect failed systemd units",
        tool_code="systemctl_failed",
        command="systemctl --failed --no-pager",
        purpose="Capture failed system services.",
        parser="systemctl_failed",
        expected_evidence=["failed units", "0 loaded units listed"],
    ),
]


def baseline_command_policy(instructions: list[AgentMonitoringInstruction] | None = None) -> CommandPolicy:
    selected_instructions = instructions or DEFAULT_BASELINE_INSTRUCTIONS
    return CommandPolicy(
        [
            AllowedCommand(tool_code=instruction.tool_code, command=instruction.command)
            for instruction in selected_instructions
            if instruction.read_only
        ]
    )
