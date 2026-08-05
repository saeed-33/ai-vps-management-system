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


class ServerDetail(ServerSummary):
    metadata: dict[str, str]
    assigned_monitoring_profiles: list[str]
