from pydantic import BaseModel, Field


class MonitoringTool(BaseModel):
    code: str
    purpose: str
    read_only: bool


class MonitoringInstruction(BaseModel):
    id: str
    title: str
    tool_code: str
    command: str
    purpose: str
    parser: str | None = None
    expected_evidence: list[str] = Field(default_factory=list)
    read_only: bool = True


class MonitoringProfileSummary(BaseModel):
    id: str
    name: str
    domain: str
    version: int
    status: str
    assigned_servers: int
    instructions_count: int
    specialist_agents: list[str]
    source: str


class MonitoringProfileDetail(MonitoringProfileSummary):
    description: str
    tools: list[MonitoringTool]
    monitoring_instructions: list[MonitoringInstruction]
    analysis_instructions: list[str]


class MonitoringProfileCreate(BaseModel):
    id: str
    name: str
    domain: str
    status: str = "draft"
    description: str
    monitoring_instructions: list[MonitoringInstruction]
    analysis_instructions: list[str] = Field(default_factory=list)
    specialist_agents: list[str] = Field(default_factory=list)


class MonitoringProfilesListResponse(BaseModel):
    profiles: list[MonitoringProfileSummary]


class MonitoringProfilesSummaryResponse(BaseModel):
    total: int
    active: int
    draft: int
    by_domain: dict[str, int]
