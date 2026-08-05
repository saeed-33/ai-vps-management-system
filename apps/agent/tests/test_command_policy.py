import pytest

from ai_vps_agent.server_access.command_policy import AllowedCommand, CommandPolicy, CommandPolicyError


def test_command_policy_allows_registered_read_only_tool() -> None:
    policy = CommandPolicy([AllowedCommand(tool_code="uptime", command="uptime")])

    assert policy.command_for("uptime") == "uptime"


def test_command_policy_rejects_unknown_tool() -> None:
    policy = CommandPolicy([AllowedCommand(tool_code="uptime", command="uptime")])

    with pytest.raises(CommandPolicyError):
        policy.command_for("rm")


def test_command_policy_rejects_mutating_command_even_if_registered() -> None:
    policy = CommandPolicy([AllowedCommand(tool_code="restart_nginx", command="systemctl restart nginx")])

    with pytest.raises(CommandPolicyError):
        policy.command_for("restart_nginx")
