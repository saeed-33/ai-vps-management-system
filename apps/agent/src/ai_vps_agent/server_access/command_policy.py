from dataclasses import dataclass


class CommandPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class AllowedCommand:
    tool_code: str
    command: str
    read_only: bool = True


class CommandPolicy:
    def __init__(self, allowed_commands: list[AllowedCommand]) -> None:
        self._allowed_by_tool = {command.tool_code: command for command in allowed_commands}

    def command_for(self, tool_code: str) -> str:
        command = self._allowed_by_tool.get(tool_code)
        if command is None:
            raise CommandPolicyError(f"Tool is not allowed: {tool_code}")
        if not command.read_only:
            raise CommandPolicyError(f"Tool is not read-only: {tool_code}")
        _reject_mutating_tokens(command.command)
        return command.command


def _reject_mutating_tokens(command: str) -> None:
    mutating_tokens = [
        " rm ",
        " rmdir ",
        " mv ",
        " cp ",
        " chmod ",
        " chown ",
        " systemctl restart ",
        " systemctl stop ",
        " systemctl start ",
        " systemctl reload ",
        " reboot",
        " shutdown",
        " kill ",
    ]
    normalized = f" {command.strip()} "
    for token in mutating_tokens:
        if token in normalized:
            raise CommandPolicyError(f"Mutating token is not allowed: {token.strip()}")
