from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MonitoringMetricSample(BaseModel):
    metric: str
    domain: str
    value: float | str | bool
    unit: str
    source_tool: str


class ServerSubAgentReport(BaseModel):
    sub_agent_id: str
    server_id: str
    server_name: str
    status: str
    started_at: datetime
    completed_at: datetime
    monitoring_profiles: list[str]
    metrics: list[MonitoringMetricSample]
    raw_snapshot: dict[str, Any]
    collection_summary: str


class PeriodicMonitoringCycleReport(BaseModel):
    cycle_id: str
    trigger: str
    status: str
    started_at: datetime
    completed_at: datetime
    servers_planned: int
    servers_checked: int
    reports_count: int
    reports: list[ServerSubAgentReport]
    scope_note: str


class PeriodicMonitoringCyclesListResponse(BaseModel):
    cycles: list[PeriodicMonitoringCycleReport]


class PeriodicMonitoringReportsListResponse(BaseModel):
    reports: list[ServerSubAgentReport]


class PeriodicMonitoringSchedulerStartRequest(BaseModel):
    interval_seconds: int = Field(default=300, ge=1, le=86400)


class PeriodicMonitoringSchedulerStatus(BaseModel):
    enabled: bool
    interval_seconds: int | None
    started_at: datetime | None
    last_run_at: datetime | None
    next_run_at: datetime | None
    runs_count: int
    last_error: str | None
