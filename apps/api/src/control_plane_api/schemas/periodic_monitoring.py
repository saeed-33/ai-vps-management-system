from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MonitoringMetricSample(BaseModel):
    metric: str
    domain: str
    value: float | str | bool
    unit: str
    source_tool: str


class MonitoringAnalysisFinding(BaseModel):
    code: str
    severity: str
    title: str
    detail: str
    metric: str | None = None
    value: float | str | bool | None = None
    threshold: float | str | bool | None = None
    profile_id: str | None = None
    interpretation_note: str | None = None
    suggested_specialist_agents: list[str] = Field(default_factory=list)


class MonitoringReportAnalysis(BaseModel):
    status: str = "not_analyzed"
    severity: str = "info"
    summary: str = "Report has not been analyzed yet."
    findings: list[MonitoringAnalysisFinding] = Field(default_factory=list)
    profiles_evaluated: list[str] = Field(default_factory=list)
    suggested_specialist_agents: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


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
    analysis: MonitoringReportAnalysis = Field(default_factory=MonitoringReportAnalysis)


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


class PeriodicMonitoringAnalysisReport(BaseModel):
    analysis_report_id: str
    source_cycle_id: str
    source_report_id: str
    server_id: str
    server_name: str
    generated_at: datetime
    title: str
    analysis: MonitoringReportAnalysis
    metrics_count: int
    monitoring_profiles: list[str]


class PeriodicMonitoringAnalysisReportsListResponse(BaseModel):
    analysis_reports: list[PeriodicMonitoringAnalysisReport]


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
