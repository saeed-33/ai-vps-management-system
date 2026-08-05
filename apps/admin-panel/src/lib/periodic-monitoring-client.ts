import { getApiBaseUrl } from "@/lib/api-client";

export type MonitoringMetricSample = {
  metric: string;
  domain: string;
  value: number | string | boolean;
  unit: string;
  source_tool: string;
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
  collection_summary: string;
};

export type PeriodicMonitoringCycleReport = {
  cycle_id: string;
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
