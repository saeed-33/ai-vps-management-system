import { getApiBaseUrl } from "@/lib/api-client";

export type MonitoringProfileSummary = {
  id: string;
  name: string;
  domain: string;
  version: number;
  status: string;
  assigned_servers: number;
  instructions_count: number;
  specialist_agents: string[];
  source: string;
};

export type MonitoringProfilesListResponse = {
  profiles: MonitoringProfileSummary[];
};

export type MonitoringProfilesSummaryResponse = {
  total: number;
  active: number;
  draft: number;
  by_domain: Record<string, number>;
};

export type MonitoringInstruction = {
  id: string;
  title: string;
  tool_code: string;
  command: string;
  purpose: string;
  parser: string | null;
  expected_evidence: string[];
  read_only: boolean;
};

export type MonitoringProfileCreate = {
  id: string;
  name: string;
  domain: string;
  status: string;
  description: string;
  monitoring_instructions: MonitoringInstruction[];
  analysis_instructions: string[];
  specialist_agents: string[];
};

async function getAuthorizedJson<T>(path: string, token: string, init?: RequestInit): Promise<T> {
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

export function getMonitoringProfiles(token: string) {
  return getAuthorizedJson<MonitoringProfilesListResponse>("/api/v1/monitoring-profiles", token);
}

export function getMonitoringProfilesSummary(token: string) {
  return getAuthorizedJson<MonitoringProfilesSummaryResponse>("/api/v1/monitoring-profiles/summary", token);
}

export function createMonitoringProfile(token: string, payload: MonitoringProfileCreate) {
  return getAuthorizedJson<MonitoringProfileSummary>("/api/v1/monitoring-profiles", token, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}
