from control_plane_api.schemas.periodic_monitoring import (
    MonitoringAnalysisFinding,
    MonitoringMetricSample,
    MonitoringReportAnalysis,
    ServerSubAgentReport,
)


def analyze_server_report(report: ServerSubAgentReport) -> MonitoringReportAnalysis:
    findings: list[MonitoringAnalysisFinding] = []

    if report.status != "completed":
        findings.append(
            MonitoringAnalysisFinding(
                code="collection_failed",
                severity="warning",
                title="Metric collection failed",
                detail=report.collection_summary,
            )
        )

    metrics = {metric.metric: metric for metric in report.metrics}
    _check_upper(findings, metrics.get("cpu_usage_percent"), warning=80, critical=95, title="High CPU usage")
    _check_upper(findings, metrics.get("memory_usage_percent"), warning=80, critical=92, title="High memory usage")
    _check_upper(findings, metrics.get("root_disk_usage_percent"), warning=80, critical=90, title="High root disk usage")
    _check_upper(findings, metrics.get("load_1m_per_core"), warning=1.0, critical=2.0, title="High normalized load")
    _check_upper(findings, metrics.get("failed_systemd_units"), warning=1, critical=5, title="Failed systemd units")

    severity = _max_severity(findings)
    if not findings:
        return MonitoringReportAnalysis(
            status="no_issue",
            severity="info",
            summary="No periodic monitoring issue was detected in the collected baseline metrics.",
            findings=[],
        )

    return MonitoringReportAnalysis(
        status="suspected_issue" if severity == "warning" else "confirmed_issue",
        severity=severity,
        summary=_summary_for(findings, severity),
        findings=findings,
    )


def _check_upper(
    findings: list[MonitoringAnalysisFinding],
    metric: MonitoringMetricSample | None,
    *,
    warning: float,
    critical: float,
    title: str,
) -> None:
    if metric is None or not isinstance(metric.value, (int, float)):
        return
    if metric.value >= critical:
        findings.append(
            MonitoringAnalysisFinding(
                code=f"{metric.metric}_critical",
                severity="critical",
                title=title,
                detail=f"{metric.metric} is {metric.value} {metric.unit}, at or above critical threshold {critical}.",
                metric=metric.metric,
                value=metric.value,
                threshold=critical,
            )
        )
    elif metric.value >= warning:
        findings.append(
            MonitoringAnalysisFinding(
                code=f"{metric.metric}_warning",
                severity="warning",
                title=title,
                detail=f"{metric.metric} is {metric.value} {metric.unit}, at or above warning threshold {warning}.",
                metric=metric.metric,
                value=metric.value,
                threshold=warning,
            )
        )


def _max_severity(findings: list[MonitoringAnalysisFinding]) -> str:
    if any(finding.severity == "critical" for finding in findings):
        return "critical"
    if any(finding.severity == "warning" for finding in findings):
        return "warning"
    return "info"


def _summary_for(findings: list[MonitoringAnalysisFinding], severity: str) -> str:
    if severity == "critical":
        return f"Critical periodic monitoring findings detected: {len(findings)} finding(s)."
    return f"Periodic monitoring warnings detected: {len(findings)} finding(s)."
