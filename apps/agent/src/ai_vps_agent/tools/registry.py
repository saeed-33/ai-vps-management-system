from ai_vps_agent.server_access.command_policy import AllowedCommand, CommandPolicy

BASELINE_TOOL_CODES = [
    "uptime",
    "free_m",
    "df_portable",
    "systemctl_failed",
]


def baseline_command_policy() -> CommandPolicy:
    return CommandPolicy(
        [
            AllowedCommand(tool_code="uptime", command="uptime"),
            AllowedCommand(tool_code="free_m", command="free -m"),
            AllowedCommand(tool_code="df_portable", command="df -P -T"),
            AllowedCommand(tool_code="systemctl_failed", command="systemctl --failed --no-pager"),
        ]
    )
