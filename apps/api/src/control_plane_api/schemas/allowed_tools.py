from pydantic import BaseModel


class ToolGuardrail(BaseModel):
    rule: str
    reason: str


class AllowedToolSummary(BaseModel):
    id: str
    code: str
    name: str
    category: str
    version: int
    status: str
    execution_scope: str
    read_only: bool
    used_by: list[str]
    source: str


class AllowedToolDetail(AllowedToolSummary):
    description: str
    command_shape: str
    guardrails: list[ToolGuardrail]
    output_contract: list[str]


class AllowedToolsListResponse(BaseModel):
    tools: list[AllowedToolSummary]


class AllowedToolsSummaryResponse(BaseModel):
    total: int
    active: int
    draft: int
    read_only: int
    by_category: dict[str, int]
    by_scope: dict[str, int]
