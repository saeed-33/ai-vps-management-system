from control_plane_api.modules.monitoring_profiles.service import get_monitoring_profile
from control_plane_api.schemas.monitoring_profiles import MonitoringProfileDetail, MonitoringThreshold
from control_plane_api.schemas.periodic_monitoring import (
    MonitoringAnalysisFinding,
    MonitoringMetricSample,
    MonitoringReportAnalysis,
    ServerSubAgentReport,
)


def analyze_server_report(report: ServerSubAgentReport) -> MonitoringReportAnalysis:
    findings: list[MonitoringAnalysisFinding] = []
    profiles = _profiles_for(report)

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
    for profile in profiles:
        _evaluate_profile(findings, profile, metrics)

    if not profiles:
        _evaluate_default_baseline(findings, metrics)

    severity = _max_severity(findings)
    suggested_agents = sorted(
        {
            agent
            for finding in findings
            if finding.severity in {"warning", "critical"}
            for agent in finding.suggested_specialist_agents
        }
    )

    if not findings:
        return MonitoringReportAnalysis(
            status="no_issue",
            severity="info",
            summary="No periodic monitoring issue was detected from the evaluated monitoring profile rules.",
            findings=[],
            profiles_evaluated=[profile.id for profile in profiles],
            suggested_specialist_agents=[],
            next_actions=["Continue periodic monitoring and compare with future trend data."],
        )

    return MonitoringReportAnalysis(
        status=_status_for(severity),
        severity=severity,
        summary=_summary_for(findings, severity),
        findings=findings,
        profiles_evaluated=[profile.id for profile in profiles],
        suggested_specialist_agents=suggested_agents,
        next_actions=_next_actions(severity, suggested_agents),
    )


def _profiles_for(report: ServerSubAgentReport) -> list[MonitoringProfileDetail]:
    profiles = []
    for profile_id in report.monitoring_profiles:
        profile = get_monitoring_profile(profile_id)
        if profile is not None:
            profiles.append(profile)
    return profiles


def _evaluate_profile(
    findings: list[MonitoringAnalysisFinding],
    profile: MonitoringProfileDetail,
    metrics: dict[str, MonitoringMetricSample],
) -> None:
    missing_metrics = []
    for threshold in profile.thresholds:
        metric = metrics.get(threshold.metric)
        if metric is None:
            missing_metrics.append(threshold.metric)
            continue
        _evaluate_threshold(findings, profile, threshold, metric)

    if missing_metrics:
        findings.append(
            MonitoringAnalysisFinding(
                code=f"{profile.id}_coverage_gap",
                severity="info",
                title="Monitoring profile coverage gap",
                detail=(
                    f"Profile {profile.id} expects metrics that were not collected in this report: "
                    f"{', '.join(sorted(missing_metrics))}."
                ),
                profile_id=profile.id,
                interpretation_note="A missing metric is not an issue by itself, but it limits analysis confidence.",
                suggested_specialist_agents=[],
            )
        )


def _evaluate_threshold(
    findings: list[MonitoringAnalysisFinding],
    profile: MonitoringProfileDetail,
    threshold: MonitoringThreshold,
    metric: MonitoringMetricSample,
) -> None:
    if not isinstance(metric.value, (int, float)):
        return

    direction = _threshold_direction(threshold.metric)
    if threshold.critical is not None and _crosses(metric.value, threshold.critical, direction):
        _append_threshold_finding(findings, profile, threshold, metric, "critical", threshold.critical)
    elif threshold.warning is not None and _crosses(metric.value, threshold.warning, direction):
        _append_threshold_finding(findings, profile, threshold, metric, "warning", threshold.warning)


def _append_threshold_finding(
    findings: list[MonitoringAnalysisFinding],
    profile: MonitoringProfileDetail,
    threshold: MonitoringThreshold,
    metric: MonitoringMetricSample,
    severity: str,
    limit: float,
) -> None:
    findings.append(
        MonitoringAnalysisFinding(
            code=f"{profile.id}_{metric.metric}_{severity}",
            severity=severity,
            title=f"{metric.metric.replace('_', ' ')} crossed {severity} threshold",
            detail=f"{metric.metric} is {metric.value} {metric.unit}; {severity} threshold is {limit} {threshold.unit}.",
            metric=metric.metric,
            value=metric.value,
            threshold=limit,
            profile_id=profile.id,
            interpretation_note=threshold.interpretation_note,
            suggested_specialist_agents=profile.specialist_agents if severity in {"warning", "critical"} else [],
        )
    )


def _evaluate_default_baseline(findings: list[MonitoringAnalysisFinding], metrics: dict[str, MonitoringMetricSample]) -> None:
    defaults = {
        "cpu_usage_percent": (80, 95, "High CPU usage"),
        "memory_usage_percent": (80, 92, "High memory usage"),
        "root_disk_usage_percent": (80, 90, "High root disk usage"),
        "load_1m_per_core": (1.0, 2.0, "High normalized load"),
        "failed_systemd_units": (1, 5, "Failed systemd units"),
    }
    for metric_key, (warning, critical, title) in defaults.items():
        metric = metrics.get(metric_key)
        if metric is None or not isinstance(metric.value, (int, float)):
            continue
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


def _threshold_direction(metric: str) -> str:
    lower_is_worse_metrics = {"nginx_active_state", "listen_port_80_443_count"}
    return "lower" if metric in lower_is_worse_metrics else "upper"


def _crosses(value: float, threshold: float, direction: str) -> bool:
    if direction == "lower":
        return value <= threshold
    return value >= threshold


def _max_severity(findings: list[MonitoringAnalysisFinding]) -> str:
    if any(finding.severity == "critical" for finding in findings):
        return "critical"
    if any(finding.severity == "warning" for finding in findings):
        return "warning"
    if any(finding.severity == "info" for finding in findings):
        return "info"
    return "info"


def _status_for(severity: str) -> str:
    if severity == "critical":
        return "confirmed_issue"
    if severity == "warning":
        return "suspected_issue"
    return "no_issue"


def _summary_for(findings: list[MonitoringAnalysisFinding], severity: str) -> str:
    actionable = [finding for finding in findings if finding.severity in {"warning", "critical"}]
    if severity == "critical":
        return f"Critical periodic monitoring findings detected: {len(actionable)} actionable finding(s)."
    if severity == "warning":
        return f"Periodic monitoring warnings detected: {len(actionable)} actionable finding(s)."
    return "No actionable issue was detected, but the report has analysis notes that affect confidence."


def _next_actions(severity: str, suggested_agents: list[str]) -> list[str]:
    if severity == "critical":
        actions = ["Review the critical evidence before any remediation step."]
    elif severity == "warning":
        actions = ["Review the warning evidence and compare with the next periodic cycle."]
    else:
        actions = ["Continue periodic monitoring and improve metric coverage where needed."]
    if suggested_agents:
        actions.append(f"Suggested specialist agents for later phases: {', '.join(suggested_agents)}.")
    return actions
