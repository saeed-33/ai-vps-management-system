"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Activity, Play, RefreshCw, Server, Square } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { getStoredAccessToken } from "@/lib/auth-client";
import {
  getPeriodicMonitoringCycles,
  getPeriodicMonitoringSchedulerStatus,
  startPeriodicMonitoringCycle,
  startPeriodicMonitoringScheduler,
  stopPeriodicMonitoringScheduler,
  type PeriodicMonitoringCycleReport,
  type ServerSubAgentReport,
} from "@/lib/periodic-monitoring-client";

export function PeriodicMonitoringView() {
  const token = typeof window === "undefined" ? null : getStoredAccessToken();
  const [intervalSeconds, setIntervalSeconds] = useState(300);

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

  const startMutation = useMutation({
    mutationFn: () => startPeriodicMonitoringCycle(token ?? ""),
    onSuccess: () => {
      void cyclesQuery.refetch();
      void schedulerQuery.refetch();
    },
  });

  const startSchedulerMutation = useMutation({
    mutationFn: () => startPeriodicMonitoringScheduler(token ?? "", intervalSeconds),
    onSuccess: () => {
      void schedulerQuery.refetch();
      void cyclesQuery.refetch();
    },
  });

  const stopSchedulerMutation = useMutation({
    mutationFn: () => stopPeriodicMonitoringScheduler(token ?? ""),
    onSuccess: () => {
      void schedulerQuery.refetch();
    },
  });

  if (!token) {
    return (
      <div className="page-stack">
        <section className="card wide-card">
          <h2 className="section-title">Periodic Monitoring</h2>
          <p className="metric-note">Sign in to run and inspect periodic monitoring reports.</p>
          <Link className="button primary" href="/login">
            Sign in
          </Link>
        </section>
      </div>
    );
  }

  const cycles = cyclesQuery.data?.cycles ?? [];
  const latestCycle = cycles[0];
  const allReports = cycles.flatMap((cycle) => cycle.reports);
  const failedReports = allReports.filter((report) => report.status !== "completed").length;

  return (
    <div className="page-stack">
      <section className="grid" aria-label="Periodic monitoring summary">
        <article className="card metric-card">
          <p className="card-title">Cycles</p>
          <p className="metric-value">{cycles.length}</p>
          <p className="metric-note">Loaded from PostgreSQL when available, otherwise API memory.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">Latest Servers</p>
          <p className="metric-value">{latestCycle?.servers_checked ?? "-"}</p>
          <p className="metric-note">Servers checked in the latest cycle.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">Reports</p>
          <p className="metric-value">{latestCycle?.reports_count ?? "-"}</p>
          <p className="metric-note">Reports generated in the latest cycle.</p>
        </article>
        <article className="card metric-card">
          <p className="card-title">Failures</p>
          <p className="metric-value">{failedReports}</p>
          <p className="metric-note">Failed server reports across the loaded cycles.</p>
        </article>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">Run Monitoring</h2>
            <p className="metric-note">Runs one server sub-agent per active server and stores a periodic report.</p>
          </div>
          <div className="toolbar">
            <button
              className="button"
              type="button"
              onClick={() => {
                void cyclesQuery.refetch();
                void schedulerQuery.refetch();
              }}
            >
              <RefreshCw aria-hidden="true" />
              Refresh
            </button>
            <button
              className="button primary"
              type="button"
              disabled={startMutation.isPending}
              onClick={() => startMutation.mutate()}
            >
              <Play aria-hidden="true" />
              {startMutation.isPending ? "Running" : "Run cycle"}
            </button>
          </div>
        </div>

        {startMutation.isError || cyclesQuery.isError ? (
          <p className="notice danger">Could not run or load monitoring cycles. Check your token and permissions.</p>
        ) : null}

        {latestCycle ? <CycleSummary cycle={latestCycle} /> : <p className="notice">No monitoring cycles yet.</p>}
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">Scheduler</h2>
            <p className="metric-note">Runs inside the current API process. Restarting the API stops the scheduler.</p>
          </div>
          <span className={`badge ${schedulerQuery.data?.enabled ? "success" : "neutral"}`}>
            {schedulerQuery.data?.enabled ? "running" : "stopped"}
          </span>
        </div>

        <div className="form-stack">
          <label className="field">
            <span>Interval seconds</span>
            <input
              dir="ltr"
              min={1}
              max={86400}
              type="number"
              value={intervalSeconds}
              onChange={(event) => setIntervalSeconds(Number(event.target.value))}
            />
          </label>
          <div className="toolbar">
            <button
              className="button primary"
              type="button"
              disabled={startSchedulerMutation.isPending || schedulerQuery.data?.enabled}
              onClick={() => startSchedulerMutation.mutate()}
            >
              <Play aria-hidden="true" />
              Start scheduler
            </button>
            <button
              className="button"
              type="button"
              disabled={stopSchedulerMutation.isPending || !schedulerQuery.data?.enabled}
              onClick={() => stopSchedulerMutation.mutate()}
            >
              <Square aria-hidden="true" />
              Stop
            </button>
          </div>
        </div>

        {schedulerQuery.data?.last_error ? (
          <p className="notice danger" dir="ltr">
            {schedulerQuery.data.last_error}
          </p>
        ) : null}

        <ul className="status-list">
          <li className="status-row">
            <div>
              <strong>runs_count</strong>
              <span>
                interval: {schedulerQuery.data?.interval_seconds ?? "-"} / last:{" "}
                {formatDate(schedulerQuery.data?.last_run_at)}
              </span>
              <span>next: {formatDate(schedulerQuery.data?.next_run_at)}</span>
            </div>
            <span className="badge neutral">{schedulerQuery.data?.runs_count ?? 0}</span>
          </li>
        </ul>
      </section>

      <section className="card wide-card">
        <div className="toolbar">
          <div>
            <h2 className="section-title">Monitoring Reports</h2>
            <p className="metric-note">Every loaded cycle, server report, metric, and collection error.</p>
          </div>
          <Activity aria-hidden="true" />
        </div>

        {cycles.length === 0 ? (
          <p className="notice">Run a cycle to create the first periodic monitoring report.</p>
        ) : (
          <div className="form-stack">
            {cycles.map((cycle) => (
              <CycleDetails cycle={cycle} key={cycle.cycle_id} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function CycleSummary({ cycle }: { cycle: PeriodicMonitoringCycleReport }) {
  return (
    <ul className="status-list">
      <li className="status-row">
        <div>
          <strong>{cycle.cycle_id}</strong>
          <span>
            {cycle.trigger} / {cycle.servers_checked} checked / {cycle.reports_count} reports
          </span>
          <span>{formatDate(cycle.completed_at)}</span>
        </div>
        <span className={`badge ${cycle.status === "completed" ? "success" : "neutral"}`}>{cycle.status}</span>
      </li>
    </ul>
  );
}

function CycleDetails({ cycle }: { cycle: PeriodicMonitoringCycleReport }) {
  return (
    <details className="status-row" open>
      <summary>
        <strong>{cycle.cycle_id}</strong>{" "}
        <span>
          {cycle.trigger} / {cycle.status} / {formatDate(cycle.completed_at)}
        </span>
      </summary>
      <p className="metric-note">{cycle.scope_note}</p>
      <div className="form-stack">
        {cycle.reports.map((report) => (
          <ReportDetails key={`${cycle.cycle_id}-${report.sub_agent_id}`} report={report} />
        ))}
      </div>
    </details>
  );
}

function ReportDetails({ report }: { report: ServerSubAgentReport }) {
  const errorType = typeof report.raw_snapshot.error_type === "string" ? report.raw_snapshot.error_type : null;
  const error = typeof report.raw_snapshot.error === "string" ? report.raw_snapshot.error : null;

  return (
    <details className="status-row" open>
      <summary>
        <Server aria-hidden="true" /> <strong>{report.server_name}</strong>{" "}
        <span>
          {report.status} / {report.metrics.length} metrics / {formatDate(report.completed_at)}
        </span>
      </summary>
      <p className="metric-note">{report.collection_summary}</p>
      <p className="metric-note" dir="ltr">
        server_id: {report.server_id} / sub_agent: {report.sub_agent_id}
      </p>
      {report.monitoring_profiles.length > 0 ? (
        <p className="metric-note" dir="ltr">
          profiles: {report.monitoring_profiles.join(", ")}
        </p>
      ) : null}
      {errorType || error ? (
        <p className="notice danger" dir="ltr">
          {errorType}: {error}
        </p>
      ) : null}
      {report.metrics.length === 0 ? (
        <p className="notice">No metrics were collected for this server report.</p>
      ) : (
        <ul className="status-list">
          {report.metrics.map((metric, index) => (
            <li className="status-row" key={`${report.sub_agent_id}-${metric.metric}-${metric.source_tool}-${index}`}>
              <div>
                <strong>{metric.metric}</strong>
                <span>
                  {metric.domain} / {metric.source_tool}
                </span>
              </div>
              <span className="badge neutral">
                {String(metric.value)} {metric.unit}
              </span>
            </li>
          ))}
        </ul>
      )}
    </details>
  );
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString();
}
