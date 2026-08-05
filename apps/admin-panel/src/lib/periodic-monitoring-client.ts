import { getApiBaseUrl } from "@/lib/api-client";

export type MonitoringMetricSample = {
  metric: string;
  domain: string;
  value: number | string | boolean;
  unit: string;
  source_tool: string;
};

export type MonitoringAnalysisFinding = {
  code: string;
  severity: string;
  title: string;
  detail: string;
  metric: string | null;
  value: number | string | boolean | null;
  threshold: number | string | boolean | null;
  profile_id: string | null;
  interpretation_note: string | null;
  suggested_specialist_agents: string[];
};

export type MonitoringReportAnalysis = {
  status: string;
  severity: string;
  summary: string;
  findings: MonitoringAnalysisFinding[];
  profiles_evaluated: string[];
  suggested_specialist_agents: string[];
  next_actions: string[];
  llm_enrichment: MonitoringLlmEnrichment | null;
};

export type MonitoringLlmEnrichment = {
  status: string;
  provider: string;
  model: string | null;
  summary: string | null;
  root_cause_hypotheses: string[];
  recommended_questions: string[];
  limitations: string[];
  error: string | null;
};

export type ServerSubAgentReport = {
  sub_agent_id: string;
  server_id: string;
  server_name: string;
  status: string;
  started_at: string;
  completed_at: string;
  monitoring_profiles: string[];
  metrics: MonitoringMetricSample[];
  raw_snapshot: Record<string, unknown>;
  collection_summary: string;
  analysis: MonitoringReportAnalysis;
};

export type PeriodicMonitoringCycleReport = {
  cycle_id: string;
  trigger: string;
  status: string;
  started_at: string;
  completed_at: string;
  servers_planned: number;
  servers_checked: number;
  reports_count: number;
  reports: ServerSubAgentReport[];
  scope_note: string;
};

export type PeriodicMonitoringCyclesListResponse = {
  cycles: PeriodicMonitoringCycleReport[];
};

export type PeriodicMonitoringAnalysisReport = {
  analysis_report_id: string;
  source_cycle_id: string;
  source_report_id: string;
  server_id: string;
  server_name: string;
  generated_at: string;
  title: string;
  analysis: MonitoringReportAnalysis;
  metrics_count: number;
  monitoring_profiles: string[];
};

export type PeriodicMonitoringAnalysisReportsListResponse = {
  analysis_reports: PeriodicMonitoringAnalysisReport[];
};

export type PeriodicMonitoringSchedulerStatus = {
  enabled: boolean;
  interval_seconds: number | null;
  started_at: string | null;
  last_run_at: string | null;
  next_run_at: string | null;
  runs_count: number;
  last_error: string | null;
};

async function requestJson<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      accept: "application/json",
      authorization: `Bearer ${token}`,
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function startPeriodicMonitoringCycle(token: string) {
  return requestJson<PeriodicMonitoringCycleReport>("/api/v1/periodic-monitoring/cycles", token, {
    method: "POST",
  });
}

export function getPeriodicMonitoringCycles(token: string) {
  return requestJson<PeriodicMonitoringCyclesListResponse>("/api/v1/periodic-monitoring/cycles", token);
}

export function getPeriodicMonitoringAnalysisReports(token: string) {
  return requestJson<PeriodicMonitoringAnalysisReportsListResponse>("/api/v1/periodic-monitoring/analysis-reports", token);
}

export function getPeriodicMonitoringSchedulerStatus(token: string) {
  return requestJson<PeriodicMonitoringSchedulerStatus>("/api/v1/periodic-monitoring/scheduler/status", token);
}

export function startPeriodicMonitoringScheduler(token: string, intervalSeconds: number) {
  return requestJson<PeriodicMonitoringSchedulerStatus>("/api/v1/periodic-monitoring/scheduler/start", token, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({ interval_seconds: intervalSeconds }),
  });
}

export function stopPeriodicMonitoringScheduler(token: string) {
  return requestJson<PeriodicMonitoringSchedulerStatus>("/api/v1/periodic-monitoring/scheduler/stop", token, {
    method: "POST",
  });
}
