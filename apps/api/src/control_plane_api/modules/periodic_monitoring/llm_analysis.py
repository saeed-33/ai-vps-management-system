import json
from typing import Protocol

import httpx
from pydantic import BaseModel, Field, ValidationError

from control_plane_api.core.config import Settings
from control_plane_api.schemas.periodic_monitoring import (
    MonitoringLlmEnrichment,
    MonitoringReportAnalysis,
    ServerSubAgentReport,
)


class LlmAnalysisAdapter(Protocol):
    async def enrich(
        self,
        *,
        report: ServerSubAgentReport,
        base_analysis: MonitoringReportAnalysis,
    ) -> MonitoringLlmEnrichment:
        """Create an optional LLM enrichment without changing rule-based findings."""


class DisabledLlmAnalysisAdapter:
    async def enrich(
        self,
        *,
        report: ServerSubAgentReport,
        base_analysis: MonitoringReportAnalysis,
    ) -> MonitoringLlmEnrichment:
        return MonitoringLlmEnrichment(
            status="skipped",
            provider="disabled",
            limitations=["LLM analysis is disabled; rule-based analysis is the source of truth."],
        )


class OllamaLlmAnalysisAdapter:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.llm_analysis_base_url.rstrip("/")
        self._model = settings.llm_analysis_model
        self._timeout = settings.llm_analysis_timeout_seconds

    async def enrich(
        self,
        *,
        report: ServerSubAgentReport,
        base_analysis: MonitoringReportAnalysis,
    ) -> MonitoringLlmEnrichment:
        payload = {
            "model": self._model,
            "prompt": _prompt(report, base_analysis),
            "stream": False,
            "format": "json",
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}/api/generate", json=payload)
            response.raise_for_status()
        body = response.json()
        generated = str(body.get("response", "{}"))
        narrative = _parse_narrative(generated)
        return MonitoringLlmEnrichment(
            status="completed",
            provider="ollama",
            model=self._model,
            summary=narrative.summary,
            root_cause_hypotheses=narrative.root_cause_hypotheses,
            recommended_questions=narrative.recommended_questions,
            limitations=narrative.limitations,
        )


class _LlmNarrative(BaseModel):
    summary: str
    root_cause_hypotheses: list[str] = Field(default_factory=list)
    recommended_questions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


async def enrich_analysis_with_llm(
    *,
    report: ServerSubAgentReport,
    base_analysis: MonitoringReportAnalysis,
    settings: Settings,
) -> MonitoringReportAnalysis:
    adapter = _adapter_for(settings)
    try:
        enrichment = await adapter.enrich(report=report, base_analysis=base_analysis)
    except Exception as exc:
        enrichment = MonitoringLlmEnrichment(
            status="failed",
            provider=settings.llm_analysis_provider,
            model=settings.llm_analysis_model,
            limitations=["Rule-based analysis was preserved because LLM enrichment failed."],
            error=f"{exc.__class__.__name__}: {exc}",
        )
    return base_analysis.model_copy(update={"llm_enrichment": enrichment})


def _adapter_for(settings: Settings) -> LlmAnalysisAdapter:
    if not settings.llm_analysis_enabled:
        return DisabledLlmAnalysisAdapter()
    if settings.llm_analysis_provider == "ollama":
        return OllamaLlmAnalysisAdapter(settings)
    return DisabledLlmAnalysisAdapter()


def _prompt(report: ServerSubAgentReport, base_analysis: MonitoringReportAnalysis) -> str:
    context = {
        "server": {
            "id": report.server_id,
            "name": report.server_name,
            "status": report.status,
            "monitoring_profiles": report.monitoring_profiles,
        },
        "metrics": [metric.model_dump() for metric in report.metrics],
        "rule_based_analysis": base_analysis.model_dump(exclude={"llm_enrichment"}),
        "constraints": [
            "Do not propose command execution.",
            "Do not claim certainty beyond the provided metrics.",
            "Treat rule-based findings as the source of truth.",
            "Return JSON only.",
        ],
    }
    return (
        "You are analyzing a periodic VPS monitoring report. "
        "Produce a concise diagnostic enrichment in JSON with keys: "
        "summary, root_cause_hypotheses, recommended_questions, limitations.\n\n"
        f"{json.dumps(context, ensure_ascii=False)}"
    )


def _parse_narrative(value: str) -> _LlmNarrative:
    try:
        return _LlmNarrative.model_validate_json(value)
    except ValidationError:
        return _LlmNarrative.model_validate(json.loads(value))
