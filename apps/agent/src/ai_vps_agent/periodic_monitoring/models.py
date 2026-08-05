from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AgentServer(BaseModel):
    id: str
    name: str
    hostname: str
    status: str
    monitoring_profiles: list[str]


class AgentMonitoringMetricSample(BaseModel):
    metric: str
    domain: str
    value: float | str | bool
    unit: str
    source_tool: str


class AgentServerSubAgentReport(BaseModel):
    sub_agent_id: str
    server_id: str
    server_name: str
    status: str
    started_at: datetime
    completed_at: datetime
    monitoring_profiles: list[str]
    metrics: list[AgentMonitoringMetricSample]
    raw_snapshot: dict[str, Any]
    collection_summary: str


class AgentPeriodicMonitoringCycleReport(BaseModel):
    cycle_id: str
    trigger: str
    status: str
    started_at: datetime
    completed_at: datetime
    servers_planned: int
    servers_checked: int
    reports_count: int
    reports: list[AgentServerSubAgentReport]
    scope_note: str
