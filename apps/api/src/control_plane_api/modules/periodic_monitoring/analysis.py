from control_plane_api.schemas.periodic_monitoring import MonitoringReportAnalysis, ServerSubAgentReport


def analyze_server_report(report: ServerSubAgentReport) -> MonitoringReportAnalysis:
    collection_state = "completed" if report.status == "completed" else "collection_failed"

    return MonitoringReportAnalysis(
        status="not_analyzed",
        severity="info",
        summary=(
            "No rule-based diagnostic analysis was produced. "
            f"Collection state: {collection_state}. Final diagnosis is delegated to the configured LLM."
        ),
        findings=[],
        profiles_evaluated=report.monitoring_profiles,
        suggested_specialist_agents=[],
        next_actions=[],
    )
