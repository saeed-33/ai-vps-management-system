import json
from typing import Protocol

import httpx
from pydantic import BaseModel, Field, ValidationError

from control_plane_api.core.config import Settings
from control_plane_api.schemas.periodic_monitoring import (
    MonitoringAnalysisFinding,
    MonitoringLlmEnrichment,
    MonitoringReportAnalysis,
    ServerSubAgentReport,
)


class LlmAnalysisAdapter(Protocol):
    async def analyze(
        self,
        *,
        report: ServerSubAgentReport,
        rule_signals: MonitoringReportAnalysis,
    ) -> MonitoringReportAnalysis:
        """Create the final report analysis. Rule signals are input only."""


class DisabledLlmAnalysisAdapter:
    async def analyze(
        self,
        *,
        report: ServerSubAgentReport,
        rule_signals: MonitoringReportAnalysis,
    ) -> MonitoringReportAnalysis:
        return _unavailable_analysis(
            provider="disabled",
            model=None,
            profiles_evaluated=rule_signals.profiles_evaluated,
            suggested_specialist_agents=rule_signals.suggested_specialist_agents,
            error=None,
        )


class OllamaLlmAnalysisAdapter:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.llm_analysis_base_url.rstrip("/")
        self._model = settings.llm_analysis_model
        self._timeout = settings.llm_analysis_timeout_seconds

    async def analyze(
        self,
        *,
        report: ServerSubAgentReport,
        rule_signals: MonitoringReportAnalysis,
    ) -> MonitoringReportAnalysis:
        payload = {
            "model": self._model,
            "prompt": _prompt(report, rule_signals),
            "stream": False,
            "format": "json",
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}/api/generate", json=payload)
            response.raise_for_status()
        body = response.json()
        generated = str(body.get("response", "{}"))
        llm_payload = _parse_llm_payload(generated)
        enrichment = MonitoringLlmEnrichment(
            status="completed",
            provider="ollama",
            model=self._model,
            summary=llm_payload.llm_summary,
            root_cause_hypotheses=llm_payload.root_cause_hypotheses,
            recommended_questions=llm_payload.recommended_questions,
            limitations=llm_payload.limitations,
        )
        return MonitoringReportAnalysis(
            status=llm_payload.status,
            severity=llm_payload.severity,
            summary=llm_payload.summary,
            findings=llm_payload.findings,
            profiles_evaluated=rule_signals.profiles_evaluated,
            suggested_specialist_agents=llm_payload.suggested_specialist_agents,
            next_actions=llm_payload.next_actions,
            llm_enrichment=enrichment,
        )


class _LlmAnalysisPayload(BaseModel):
    status: str
    severity: str
    summary: str
    findings: list[MonitoringAnalysisFinding] = Field(default_factory=list)
    suggested_specialist_agents: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    llm_summary: str | None = None
    root_cause_hypotheses: list[str] = Field(default_factory=list)
    recommended_questions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


async def analyze_report_with_llm(
    *,
    report: ServerSubAgentReport,
    rule_signals: MonitoringReportAnalysis,
    settings: Settings,
) -> MonitoringReportAnalysis:
    adapter = _adapter_for(settings)
    try:
        return await adapter.analyze(report=report, rule_signals=rule_signals)
    except Exception as exc:
        return _unavailable_analysis(
            provider=settings.llm_analysis_provider,
            model=settings.llm_analysis_model,
            profiles_evaluated=rule_signals.profiles_evaluated,
            suggested_specialist_agents=rule_signals.suggested_specialist_agents,
            error=f"{exc.__class__.__name__}: {exc}",
        )


def _adapter_for(settings: Settings) -> LlmAnalysisAdapter:
    if not settings.llm_analysis_enabled:
        return DisabledLlmAnalysisAdapter()
    if settings.llm_analysis_provider == "ollama":
        return OllamaLlmAnalysisAdapter(settings)
    return DisabledLlmAnalysisAdapter()


def _unavailable_analysis(
    *,
    provider: str,
    model: str | None,
    profiles_evaluated: list[str],
    suggested_specialist_agents: list[str],
    error: str | None,
) -> MonitoringReportAnalysis:
    status = "analysis_failed" if error else "analysis_unavailable"
    return MonitoringReportAnalysis(
        status=status,
        severity="warning",
        summary="LLM analysis was not produced. No final diagnostic conclusion is available.",
        findings=[],
        profiles_evaluated=profiles_evaluated,
        suggested_specialist_agents=suggested_specialist_agents,
        next_actions=["Enable a supported LLM provider and rerun periodic monitoring analysis."],
        llm_enrichment=MonitoringLlmEnrichment(
            status="failed" if error else "skipped",
            provider=provider,
            model=model,
            limitations=["Final report analysis is LLM-only; rule-based signals are not emitted as final analysis."],
            error=error,
        ),
    )


def _prompt(report: ServerSubAgentReport, rule_signals: MonitoringReportAnalysis) -> str:
    context = {
        "server": {
            "id": report.server_id,
            "name": report.server_name,
            "status": report.status,
            "monitoring_profiles": report.monitoring_profiles,
        },
        "metrics": [metric.model_dump() for metric in report.metrics],
        "rule_signals_not_final_analysis": rule_signals.model_dump(exclude={"llm_enrichment"}),
        "constraints": [
            "You are the only component allowed to produce the final report analysis.",
            "Rule signals are evidence only, not final conclusions.",
            "Do not propose command execution.",
            "Do not claim certainty beyond the provided metrics.",
            "Return JSON only.",
        ],
        "json_schema": {
            "status": "no_issue | suspected_issue | confirmed_issue | needs_human_review",
            "severity": "info | warning | critical",
            "summary": "final concise diagnostic conclusion",
            "findings": "array of findings with code, severity, title, detail, metric, value, threshold, profile_id, interpretation_note, suggested_specialist_agents",
            "suggested_specialist_agents": "array of agent ids",
            "next_actions": "array of safe review-only next actions",
            "llm_summary": "narrative summary for UI",
            "root_cause_hypotheses": "array",
            "recommended_questions": "array",
            "limitations": "array",
        },
    }
    return (
        "Analyze this periodic VPS monitoring report and produce the final report analysis. "
        "The final analysis must be based on the metrics, monitoring profiles, and rule signals, "
        "but you must make the final diagnostic judgment.\n\n"
        f"{json.dumps(context, ensure_ascii=False)}"
    )


def _parse_llm_payload(value: str) -> _LlmAnalysisPayload:
    try:
        return _LlmAnalysisPayload.model_validate_json(value)
    except ValidationError:
        return _LlmAnalysisPayload.model_validate(json.loads(value))
