from control_plane_api.schemas.periodic_monitoring import (
    PeriodicMonitoringAnalysisReport,
    PeriodicMonitoringCycleReport,
    ServerSubAgentReport,
)


def build_analysis_reports(cycles: list[PeriodicMonitoringCycleReport]) -> list[PeriodicMonitoringAnalysisReport]:
    return [_to_analysis_report(cycle, report) for cycle in cycles for report in cycle.reports]


def _to_analysis_report(
    cycle: PeriodicMonitoringCycleReport,
    report: ServerSubAgentReport,
) -> PeriodicMonitoringAnalysisReport:
    return PeriodicMonitoringAnalysisReport(
        analysis_report_id=f"analysis-{cycle.cycle_id}-{report.server_id}",
        source_cycle_id=cycle.cycle_id,
        source_report_id=f"{cycle.cycle_id}:{report.server_id}",
        server_id=report.server_id,
        server_name=report.server_name,
        generated_at=report.completed_at,
        title=f"Periodic analysis for {report.server_name}",
        analysis=report.analysis,
        metrics_count=len(report.metrics),
        monitoring_profiles=report.monitoring_profiles,
    )
