from pydantic import BaseModel


class SpecialistAgentToolPolicy(BaseModel):
    tool_code: str
    purpose: str
    required: bool


class SpecialistAgentTrigger(BaseModel):
    profile_id: str
    domain: str
    trigger_condition: str


class SpecialistAgentSummary(BaseModel):
    id: str
    name: str
    domain: str
    version: int
    status: str
    execution_mode: str
    trigger_profiles: list[str]
    allowed_tools_count: int
    source: str


class SpecialistAgentDetail(SpecialistAgentSummary):
    description: str
    triggers: list[SpecialistAgentTrigger]
    allowed_tools: list[SpecialistAgentToolPolicy]
    analysis_contract: list[str]
    output_contract: list[str]


class SpecialistAgentsListResponse(BaseModel):
    agents: list[SpecialistAgentSummary]


class SpecialistAgentsSummaryResponse(BaseModel):
    total: int
    active: int
    draft: int
    by_domain: dict[str, int]
    by_execution_mode: dict[str, int]
