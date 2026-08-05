"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, CheckCircle2, Clock3, Database, Play, RefreshCw, Square } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { getStoredAccessToken } from "@/lib/auth-client";
import {
  getPeriodicMonitoringAnalysisReports,
  getPeriodicMonitoringCycles,
  getPeriodicMonitoringSchedulerStatus,
  startPeriodicMonitoringCycle,
  startPeriodicMonitoringScheduler,
  stopPeriodicMonitoringScheduler,
  type MonitoringMetricSample,
  type PeriodicMonitoringAnalysisReport,
  type PeriodicMonitoringCycleReport,
  type ServerSubAgentReport,
} from "@/lib/periodic-monitoring-client";

export function PeriodicMonitoringView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();
  const [intervalSeconds, setIntervalSeconds] = useState(300);
  const [selectedCycleId, setSelectedCycleId] = useState<string | null>(null);

  const cyclesQuery = useQuery({
    queryKey: ["periodic-monitoring", "cycles"],
    queryFn: () => getPeriodicMonitoringCycles(token ?? ""),
    enabled: Boolean(token),
  });

  const schedulerQuery = useQuery({
    queryKey: ["periodic-monitoring", "scheduler"],
    queryFn: () => getPeriodicMonitoringSchedulerStatus(token ?? ""),
    enabled: Boolean(token),
  });

  const analysisReportsQuery = useQuery({
    queryKey: ["periodic-monitoring", "analysis-reports"],
    queryFn: () => getPeriodicMonitoringAnalysisReports(token ?? ""),
    enabled: Boolean(token),
  });

  const startMutation = useMutation({
    mutationFn: () => startPeriodicMonitoringCycle(token ?? ""),
    onSuccess: (cycle) => {
      setSelectedCycleId(cycle.cycle_id);
      void cyclesQuery.refetch();
      void analysisReportsQuery.refetch();
      void schedulerQuery.refetch();
    },
  });

  const startSchedulerMutation = useMutation({
    mutationFn: () => startPeriodicMonitoringScheduler(token ?? "", intervalSeconds),
    onSuccess: () => {
      void schedulerQuery.refetch();
      void cyclesQuery.refetch();
      void analysisReportsQuery.refetch();
    },
  });

  const stopSchedulerMutation = useMutation({
    mutationFn: () => stopPeriodicMonitoringScheduler(token ?? ""),
    onSuccess: () => {
      void schedulerQuery.refetch();
    },
  });

  const cycles = useMemo(() => cyclesQuery.data?.cycles ?? [], [cyclesQuery.data?.cycles]);
  const selectedCycle = cycles.find((cycle) => cycle.cycle_id === selectedCycleId) ?? cycles[0] ?? null;
  const allReports = cycles.flatMap((cycle) => cycle.reports);
  const analysisReports = analysisReportsQuery.data?.analysis_reports ?? [];
  const failedReports = allReports.filter((report) => report.status !== "completed").length;
  const totalMetrics = allReports.reduce((sum, report) => sum + report.metrics.length, 0);

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">المراقبة الدورية</h2>
          <p className="metric-note">يجب تسجيل الدخول لتشغيل المراقبة وفحص التقارير.</p>
          <Link className="button primary" href="/login">
            تسجيل الدخول
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="grid" aria-label="Periodic monitoring summary">
        <MetricCard title="الدورات" value={cycles.length} note="آخر الدورات المحملة." />
        <MetricCard title="السيرفرات" value={selectedCycle?.servers_checked ?? "-"} note="في الدورة المحددة." />
        <MetricCard title="المقاييس" value={totalMetrics} note="إجمالي المقاييس المعروضة." />
        <MetricCard title="الفشل" value={failedReports} note="تقارير سيرفر لم تكتمل." danger={failedReports > 0} />
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">تشغيل المراقبة</h2>
            <p className="metric-note">تشغيل دورة ينشئ تقريرا وتحليلا أوليا لكل سيرفر نشط.</p>
          </div>
          <div className="row-actions">
            <button
              className="button"
              type="button"
              onClick={() => {
                void cyclesQuery.refetch();
                void analysisReportsQuery.refetch();
                void schedulerQuery.refetch();
              }}
            >
              <RefreshCw aria-hidden="true" />
              تحديث
            </button>
            <button className="button primary" type="button" disabled={startMutation.isPending} onClick={() => startMutation.mutate()}>
              <Play aria-hidden="true" />
              {startMutation.isPending ? "جاري التشغيل" : "تشغيل دورة"}
            </button>
          </div>
        </div>
        {startMutation.isError || cyclesQuery.isError ? (
          <p className="notice danger">{errorText(startMutation.error ?? cyclesQuery.error)}</p>
        ) : null}
        {selectedCycle ? <CycleHeader cycle={selectedCycle} /> : <p className="notice">لا توجد تقارير بعد. شغل دورة مراقبة أولى.</p>}
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">جدولة المراقبة</h2>
            <p className="metric-note">الجدولة تعمل طالما خدمة المراقبة قيد التشغيل.</p>
          </div>
          <span className={`badge ${schedulerQuery.data?.enabled ? "success" : "neutral"}`}>
            <Clock3 aria-hidden="true" />
            {schedulerQuery.data?.enabled ? "running" : "stopped"}
          </span>
        </div>
        <div className="form-stack form-wide">
          <div className="form-grid">
            <label className="field">
              <span>الفاصل الزمني بالثواني</span>
              <input
                dir="ltr"
                min={1}
                max={86400}
                type="number"
                value={intervalSeconds}
                onChange={(event) => setIntervalSeconds(Number(event.target.value))}
              />
            </label>
            <div className="scheduler-stats">
              <span>runs: {schedulerQuery.data?.runs_count ?? 0}</span>
              <span>last: {formatDate(schedulerQuery.data?.last_run_at)}</span>
              <span>next: {formatDate(schedulerQuery.data?.next_run_at)}</span>
            </div>
          </div>
          <div className="row-actions">
            <button
              className="button primary"
              type="button"
              disabled={startSchedulerMutation.isPending || schedulerQuery.data?.enabled}
              onClick={() => startSchedulerMutation.mutate()}
            >
              <Play aria-hidden="true" />
              تشغيل الجدولة
            </button>
            <button
              className="button"
              type="button"
              disabled={stopSchedulerMutation.isPending || !schedulerQuery.data?.enabled}
              onClick={() => stopSchedulerMutation.mutate()}
            >
              <Square aria-hidden="true" />
              إيقاف
            </button>
          </div>
        </div>
        {schedulerQuery.data?.last_error ? (
          <p className="notice danger" dir="ltr">
            {schedulerQuery.data.last_error}
          </p>
        ) : null}
      </section>

      <section className="report-workspace">
        <aside className="card report-sidebar">
          <div className="toolbar">
            <h2 className="section-title">الدورات</h2>
            <Database aria-hidden="true" />
          </div>
          {cycles.length === 0 ? (
            <p className="notice">لا توجد دورات محفوظة.</p>
          ) : (
            <ul className="cycle-list">
              {cycles.map((cycle) => (
                <li key={cycle.cycle_id}>
                  <button
                    className={`cycle-button ${selectedCycle?.cycle_id === cycle.cycle_id ? "selected" : ""}`}
                    type="button"
                    onClick={() => setSelectedCycleId(cycle.cycle_id)}
                  >
                    <strong>{shortCycleId(cycle.cycle_id)}</strong>
                    <span>{formatDate(cycle.completed_at)}</span>
                    <span>
                      {cycle.reports_count} reports / {cycle.trigger}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <section className="card report-detail">
          <div className="toolbar">
            <div>
              <h2 className="section-title">تقارير السيرفرات</h2>
              <p className="metric-note">اختر دورة من اليمين لعرض تفاصيل السيرفرات والمقاييس.</p>
            </div>
            <Activity aria-hidden="true" />
          </div>
          {selectedCycle ? (
            <div className="report-grid">
              {selectedCycle.reports.map((report) => (
                <ServerReportCard key={`${selectedCycle.cycle_id}-${report.sub_agent_id}`} report={report} />
              ))}
            </div>
          ) : (
            <p className="notice">لا توجد دورة محددة.</p>
          )}
        </section>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">تقارير التحليل</h2>
            <p className="metric-note">تقارير مستقلة ناتجة عن تحليل تقارير المراقبة الدورية.</p>
          </div>
          <span className="badge neutral">{analysisReports.length} reports</span>
        </div>
        {analysisReports.length === 0 ? (
          <p className="notice">لا توجد تقارير تحليل بعد. شغل دورة مراقبة أولا.</p>
        ) : (
          <div className="analysis-report-grid">
            {analysisReports.map((report) => (
              <AnalysisReportCard key={report.analysis_report_id} report={report} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function MetricCard({ title, value, note, danger = false }: { title: string; value: string | number; note: string; danger?: boolean }) {
  return (
    <article className="card metric-card">
      <p className="card-title">{title}</p>
      <p className={`metric-value ${danger ? "danger-text" : ""}`}>{value}</p>
      <p className="metric-note">{note}</p>
    </article>
  );
}

function CycleHeader({ cycle }: { cycle: PeriodicMonitoringCycleReport }) {
  const failed = cycle.reports.filter((report) => report.status !== "completed").length;
  return (
    <ul className="status-list">
      <li className="status-row">
        <div>
          <strong>{shortCycleId(cycle.cycle_id)}</strong>
          <span>
            {cycle.trigger} / {cycle.servers_checked} checked / {cycle.reports_count} reports / {cycle.status}
          </span>
          <span>{formatDate(cycle.completed_at)}</span>
        </div>
        <div className="row-actions">
          <span className={`badge ${failed > 0 ? "danger" : "success"}`}>
            {failed > 0 ? <AlertTriangle aria-hidden="true" /> : <CheckCircle2 aria-hidden="true" />}
            {failed > 0 ? `${failed} failed` : "clean"}
          </span>
        </div>
      </li>
    </ul>
  );
}

function ServerReportCard({ report }: { report: ServerSubAgentReport }) {
  const errorType = typeof report.raw_snapshot.error_type === "string" ? report.raw_snapshot.error_type : null;
  const error = typeof report.raw_snapshot.error === "string" ? report.raw_snapshot.error : null;
  const failed = report.status !== "completed";

  return (
    <article className={`server-report-card ${failed ? "failed" : ""}`}>
      <div className="server-report-header">
        <div>
          <h3>{report.server_name}</h3>
          <p dir="ltr">{report.server_id}</p>
        </div>
        <span className={`badge ${failed ? "danger" : "success"}`}>
          {failed ? <AlertTriangle aria-hidden="true" /> : <CheckCircle2 aria-hidden="true" />}
          {report.status}
        </span>
      </div>

      <div className="server-report-meta">
        <span>{formatDate(report.completed_at)}</span>
        <span>{report.metrics.length} metrics</span>
        <span>{report.monitoring_profiles.join(", ") || "no profiles"}</span>
      </div>

      <p className="metric-note">{report.collection_summary}</p>
      <div className="analysis-summary">
        <span className={`badge ${analysisBadge(report.analysis.severity)}`}>{report.analysis.severity}</span>
        <div>
          <strong>{report.analysis.status}</strong>
          <p>{report.analysis.summary}</p>
          <small>{report.analysis.profiles_evaluated.join(", ") || "no profile rules evaluated"}</small>
        </div>
      </div>
      {report.analysis.suggested_specialist_agents.length > 0 ? (
        <div className="analysis-tags">
          {report.analysis.suggested_specialist_agents.map((agent) => (
            <span className="badge warning" key={agent}>
              {agent}
            </span>
          ))}
        </div>
      ) : null}
      {errorType || error ? (
        <p className="notice danger" dir="ltr">
          {errorType}: {error}
        </p>
      ) : null}
      {report.analysis.findings.length > 0 ? (
        <ul className="finding-list">
          {report.analysis.findings.map((finding) => (
            <li key={finding.code}>
              <span className={`badge ${analysisBadge(finding.severity)}`}>{finding.severity}</span>
              <div>
                <strong>{finding.title}</strong>
                <p>{finding.detail}</p>
                {finding.interpretation_note ? <small>{finding.interpretation_note}</small> : null}
              </div>
            </li>
          ))}
        </ul>
      ) : null}
      {report.analysis.next_actions.length > 0 ? (
        <ul className="next-action-list">
          {report.analysis.next_actions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      ) : null}

      {report.metrics.length === 0 ? (
        <p className="notice">لم يتم جمع مقاييس لهذا السيرفر.</p>
      ) : (
        <div className="metric-sample-grid">
          {report.metrics.map((metric, index) => (
            <MetricSampleCard key={`${report.sub_agent_id}-${metric.metric}-${metric.source_tool}-${index}`} metric={metric} />
          ))}
        </div>
      )}
    </article>
  );
}

function MetricSampleCard({ metric }: { metric: MonitoringMetricSample }) {
  return (
    <div className="metric-sample-card">
      <span>{metricLabel(metric.metric)}</span>
      <strong dir="ltr">
        {String(metric.value)} {metric.unit}
      </strong>
      <small>
        {metric.domain} / {metric.source_tool}
      </small>
    </div>
  );
}

function AnalysisReportCard({ report }: { report: PeriodicMonitoringAnalysisReport }) {
  return (
    <article className="analysis-report-card">
      <div className="toolbar">
        <div>
          <strong>{report.title}</strong>
          <p className="metric-note">{formatDate(report.generated_at)}</p>
        </div>
        <span className={`badge ${analysisBadge(report.analysis.severity)}`}>{report.analysis.severity}</span>
      </div>
      <p>{report.analysis.summary}</p>
      <div className="server-report-meta">
        <span>{report.metrics_count} metrics</span>
        <span>{report.monitoring_profiles.join(", ") || "no profiles"}</span>
        <span>{report.analysis.status}</span>
      </div>
      {report.analysis.next_actions.length > 0 ? (
        <ul className="next-action-list">
          {report.analysis.next_actions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

function metricLabel(metric: string) {
  const labels: Record<string, string> = {
    cpu_usage_percent: "CPU",
    memory_usage_percent: "Memory",
    load_1m_per_core: "Load",
    root_disk_usage_percent: "Disk",
    failed_systemd_units: "Failed units",
  };
  return labels[metric] ?? metric.replaceAll("_", " ");
}

function analysisBadge(severity: string) {
  if (severity === "critical") {
    return "danger";
  }
  if (severity === "warning") {
    return "warning";
  }
  return "success";
}

function shortCycleId(cycleId: string) {
  return cycleId.length > 18 ? `${cycleId.slice(0, 18)}...` : cycleId;
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString();
}

function errorText(error: unknown) {
  return error instanceof Error ? error.message : "حدث خطأ غير متوقع.";
}
