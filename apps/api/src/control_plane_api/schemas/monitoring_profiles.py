from pydantic import BaseModel


class MonitoringThreshold(BaseModel):
    metric: str
    warning: float | None = None
    critical: float | None = None
    unit: str
    interpretation_note: str


class MonitoringTool(BaseModel):
    code: str
    purpose: str
    read_only: bool


class MonitoringProfileSummary(BaseModel):
    id: str
    name: str
    domain: str
    version: int
    status: str
    assigned_servers: int
    thresholds_count: int
    specialist_agents: list[str]
    source: str


class MonitoringProfileDetail(MonitoringProfileSummary):
    description: str
    thresholds: list[MonitoringThreshold]
    tools: list[MonitoringTool]
    analysis_guidelines: list[str]


class MonitoringProfilesListResponse(BaseModel):
    profiles: list[MonitoringProfileSummary]


class MonitoringProfilesSummaryResponse(BaseModel):
    total: int
    active: int
    draft: int
    by_domain: dict[str, int]
