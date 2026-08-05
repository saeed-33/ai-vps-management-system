from pydantic import BaseModel, Field


class SshServerAccess(BaseModel):
    host: str
    port: int = Field(default=22, ge=1, le=65535)
    username: str
    private_key_path: str | None = None
    password: str | None = None
    connect_timeout_seconds: float = Field(default=10, gt=0, le=120)
    command_timeout_seconds: float = Field(default=10, gt=0, le=120)
    max_output_bytes: int = Field(default=20000, ge=1024, le=2_000_000)


class CommandResult(BaseModel):
    tool_code: str
    command: str
    exit_status: int
    stdout: str
    stderr: str
