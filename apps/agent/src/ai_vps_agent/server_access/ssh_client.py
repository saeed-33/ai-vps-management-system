import asyncio

import asyncssh

from ai_vps_agent.server_access.command_policy import CommandPolicy
from ai_vps_agent.server_access.models import CommandResult, SshServerAccess


class SshCommandClient:
    def __init__(self, access: SshServerAccess, policy: CommandPolicy) -> None:
        self._access = access
        self._policy = policy

    async def run_tool(self, tool_code: str) -> CommandResult:
        command = self._policy.command_for(tool_code)
        connect_kwargs: dict[str, object] = {
            "host": self._access.host,
            "port": self._access.port,
            "username": self._access.username,
            "known_hosts": None,
            "connect_timeout": self._access.connect_timeout_seconds,
        }
        if self._access.private_key_path:
            connect_kwargs["client_keys"] = [self._access.private_key_path]
        if self._access.password:
            connect_kwargs["password"] = self._access.password

        async with asyncssh.connect(**connect_kwargs) as connection:
            result = await asyncio.wait_for(
                connection.run(command, check=False),
                timeout=self._access.command_timeout_seconds,
            )

        stdout = _truncate_output(str(result.stdout), self._access.max_output_bytes)
        stderr = _truncate_output(str(result.stderr), self._access.max_output_bytes)
        return CommandResult(
            tool_code=tool_code,
            command=command,
            exit_status=int(result.exit_status),
            stdout=stdout,
            stderr=stderr,
        )


def _truncate_output(output: str, max_bytes: int) -> str:
    encoded = output.encode("utf-8")
    if len(encoded) <= max_bytes:
        return output
    return encoded[:max_bytes].decode("utf-8", errors="ignore")
