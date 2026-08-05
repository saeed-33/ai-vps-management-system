from pydantic import BaseModel


class ServerSummary(BaseModel):
    id: str
    name: str
    hostname: str
    ip_address: str | None
    os_family: str | None
    environment: str
    status: str
    monitoring_status: str
    source: str


class ServersListResponse(BaseModel):
    servers: list[ServerSummary]


class ServersSummaryResponse(BaseModel):
    total: int
    active: int
    disabled: int
    maintenance: int
    by_environment: dict[str, int]


class ServerSshAccessPublic(BaseModel):
    enabled: bool
    host: str | None = None
    port: int = 22
    username: str | None = None
    auth_method: str = "none"
    has_password: bool = False
    private_key_path: str | None = None


class ServerSshAccessUpdate(BaseModel):
    enabled: bool
    host: str | None = None
    port: int = 22
    username: str | None = None
    private_key_path: str | None = None
    password: str | None = None


class ServerDetail(ServerSummary):
    metadata: dict[str, str]
    assigned_monitoring_profiles: list[str]
    ssh_access: ServerSshAccessPublic
