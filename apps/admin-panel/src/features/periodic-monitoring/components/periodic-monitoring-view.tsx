"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, CheckCircle2, Clock3, Database, Play, RefreshCw, Square } from "lucide-react";
import { useMemo, useState } from "react";
import { Tabs } from "@/components/ui/tabs";
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
  const [selectedAnalysisReportId, setSelectedAnalysisReportId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("run");

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
  const selectedAnalysisReport =
    analysisReports.find((report) => report.analysis_report_id === selectedAnalysisReportId) ?? analysisReports[0] ?? null;
  const failedReports = allReports.filter((report) => report.status !== "completed").length;
  const totalMetrics = allReports.reduce((sum, report) => sum + report.metrics.length, 0);

  return (
    <div className="page-stack">
      <section className="grid" aria-label="Periodic monitoring summary">
        <MetricCard title="الدورات" value={cycles.length} note="آخر الدورات المحملة." />
        <MetricCard title="السيرفرات" value={selectedCycle?.servers_checked ?? "-"} note="في الدورة المحددة." />
        <MetricCard title="المقاييس" value={totalMetrics} note="إجمالي المقاييس المعروضة." />
        <MetricCard title="الفشل" value={failedReports} note="تقارير سيرفر لم تكتمل." danger={failedReports > 0} />
      </section>

      <Tabs
        activeTab={activeTab}
        onChange={setActiveTab}
        tabs={[
          {
            id: "run",
            label: "تشغيل دورة",
            content: (
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
            ),
          },
          {
            id: "scheduler",
            label: "الجدولة",
            content: (
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
            ),
          },
          {
            id: "server-reports",
            label: "تقارير السيرفرات",
            content: (
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
            ),
          },
          {
            id: "analysis-reports",
            label: "تقارير التحليل",
            content: (
              <AnalysisReportsWorkspace
                reports={analysisReports}
                selectedReport={selectedAnalysisReport}
                onSelect={setSelectedAnalysisReportId}
              />
            ),
          },
        ]}
      />
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
  const commandResults = getCommandResults(report.raw_snapshot);

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
      {commandResults.length > 0 ? <CommandEvidenceList commandResults={commandResults} /> : null}
    </article>
  );
}

type CommandEvidence = {
  tool_code: string;
  command: string;
  exit_status: number;
  stdout: string;
  stderr: string;
};

function CommandEvidenceList({ commandResults }: { commandResults: CommandEvidence[] }) {
  return (
    <details className="command-evidence">
      <summary>Raw monitoring evidence ({commandResults.length})</summary>
      <div className="command-evidence-list">
        {commandResults.map((result) => (
          <article className="command-evidence-item" key={`${result.tool_code}-${result.command}`}>
            <div>
              <strong>{result.tool_code}</strong>
              <span dir="ltr">exit {result.exit_status}</span>
            </div>
            <code dir="ltr">{result.command}</code>
            {result.stdout ? <pre dir="ltr">{trimEvidence(result.stdout)}</pre> : null}
            {result.stderr ? <pre className="stderr" dir="ltr">{trimEvidence(result.stderr)}</pre> : null}
          </article>
        ))}
      </div>
    </details>
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

function getCommandResults(rawSnapshot: Record<string, unknown>): CommandEvidence[] {
  const value = rawSnapshot.command_results;
  if (!Array.isArray(value)) return [];
  return value.flatMap((item) => {
    if (!item || typeof item !== "object") return [];
    const record = item as Record<string, unknown>;
    return [
      {
        tool_code: String(record.tool_code ?? "unknown"),
        command: String(record.command ?? ""),
        exit_status: Number(record.exit_status ?? 0),
        stdout: String(record.stdout ?? ""),
        stderr: String(record.stderr ?? ""),
      },
    ];
  });
}

function trimEvidence(value: string) {
  return value.length > 1600 ? `${value.slice(0, 1600)}\n... truncated in UI` : value;
}

function AnalysisReportsWorkspace({
  reports,
  selectedReport,
  onSelect,
}: {
  reports: PeriodicMonitoringAnalysisReport[];
  selectedReport: PeriodicMonitoringAnalysisReport | null;
  onSelect: (reportId: string) => void;
}) {
  if (reports.length === 0) {
    return (
      <section className="card wide-card">
        <h2 className="section-title">تقارير التحليل</h2>
        <p className="notice">لا توجد تقارير تحليل بعد. شغل دورة مراقبة أولا.</p>
      </section>
    );
  }

  return (
    <section className="analysis-workspace">
      <aside className="card analysis-list-panel">
        <div className="toolbar">
          <div>
            <h2 className="section-title">تقارير التحليل</h2>
            <p className="metric-note">اختر تقريرا لعرض التحليل الكامل.</p>
          </div>
          <span className="badge neutral">{reports.length}</span>
        </div>
        <ul className="analysis-report-list">
          {reports.map((report) => (
            <li key={report.analysis_report_id}>
              <button
                className={`analysis-report-button ${selectedReport?.analysis_report_id === report.analysis_report_id ? "selected" : ""}`}
                onClick={() => onSelect(report.analysis_report_id)}
                type="button"
              >
                <span className={`severity-marker ${analysisBadge(report.analysis.severity)}`} aria-hidden="true" />
                <strong>{report.server_name}</strong>
                <span>{formatDate(report.generated_at)}</span>
                <small>
                  {report.analysis.status} / {report.metrics_count} metrics
                </small>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <section className="card analysis-detail-panel">
        {selectedReport ? <AnalysisReportDetail report={selectedReport} /> : <p className="notice">اختر تقرير تحليل من القائمة.</p>}
      </section>
    </section>
  );
}

function AnalysisReportDetail({ report }: { report: PeriodicMonitoringAnalysisReport }) {
  return (
    <article className="analysis-detail">
      <header className="analysis-detail-header">
        <div>
          <p className="card-title">تقرير تحليل دوري</p>
          <h2>{report.server_name}</h2>
          <p dir="ltr">{report.server_id}</p>
        </div>
        <span className={`badge ${analysisBadge(report.analysis.severity)}`}>{report.analysis.severity}</span>
      </header>

      <section className="analysis-kpi-row" aria-label="Analysis metadata">
        <div>
          <span>الحالة</span>
          <strong>{report.analysis.status}</strong>
        </div>
        <div>
          <span>المقاييس</span>
          <strong>{report.metrics_count}</strong>
        </div>
        <div>
          <span>وقت التحليل</span>
          <strong>{formatDate(report.generated_at)}</strong>
        </div>
      </section>

      <section className="analysis-block primary">
        <h3>الخلاصة</h3>
        <p>{report.analysis.summary}</p>
      </section>

      <section className="analysis-block">
        <h3>ملفات المراقبة</h3>
        <div className="analysis-tags">
          {report.monitoring_profiles.length > 0 ? (
            report.monitoring_profiles.map((profile) => (
              <span className="badge neutral" key={profile}>
                {profile}
              </span>
            ))
          ) : (
            <span className="badge neutral">لا يوجد</span>
          )}
        </div>
      </section>

      {report.analysis.llm_enrichment ? (
        <section className="analysis-block">
          <div className="toolbar">
            <h3>تحليل LLM</h3>
            <span className={`badge ${report.analysis.llm_enrichment.status === "completed" ? "success" : "neutral"}`}>
              {report.analysis.llm_enrichment.provider} / {report.analysis.llm_enrichment.status}
            </span>
          </div>
          {report.analysis.llm_enrichment.summary ? <p>{report.analysis.llm_enrichment.summary}</p> : null}
          {report.analysis.llm_enrichment.root_cause_hypotheses.length > 0 ? (
            <AnalysisBullets title="احتمالات السبب" items={report.analysis.llm_enrichment.root_cause_hypotheses} />
          ) : null}
          {report.analysis.llm_enrichment.recommended_questions.length > 0 ? (
            <AnalysisBullets title="أسئلة مقترحة" items={report.analysis.llm_enrichment.recommended_questions} />
          ) : null}
          {report.analysis.llm_enrichment.limitations.length > 0 ? (
            <AnalysisBullets title="حدود التحليل" items={report.analysis.llm_enrichment.limitations} />
          ) : null}
          {report.analysis.llm_enrichment.error ? (
            <p className="notice danger" dir="ltr">
              {report.analysis.llm_enrichment.error}
            </p>
          ) : null}
        </section>
      ) : null}

      <section className="analysis-block">
        <h3>النتائج</h3>
        {report.analysis.findings.length > 0 ? (
          <ul className="finding-list detailed">
            {report.analysis.findings.map((finding) => (
              <li key={finding.code}>
                <span className={`badge ${analysisBadge(finding.severity)}`}>{finding.severity}</span>
                <div>
                  <strong>{finding.title}</strong>
                  <p>{finding.detail}</p>
                  {finding.interpretation_note ? <small>{finding.interpretation_note}</small> : null}
                  {finding.profile_id ? <small dir="ltr">{finding.profile_id}</small> : null}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="metric-note">لا توجد نتائج تحذيرية أو حرجة في هذا التقرير.</p>
        )}
      </section>

      {report.analysis.next_actions.length > 0 ? (
        <section className="analysis-block">
          <AnalysisBullets title="الخطوات التالية" items={report.analysis.next_actions} />
        </section>
      ) : null}
    </article>
  );
}

function AnalysisBullets({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="analysis-subsection">
      <h4>{title}</h4>
      <ul className="next-action-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
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
