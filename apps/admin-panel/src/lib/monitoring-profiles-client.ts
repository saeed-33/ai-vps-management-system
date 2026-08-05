import { getApiBaseUrl } from "@/lib/api-client";

export type MonitoringProfileSummary = {
  id: string;
  name: string;
  domain: string;
  version: number;
  status: string;
  assigned_servers: number;
  thresholds_count: number;
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

async function getAuthorizedJson<T>(path: string, token: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      accept: "application/json",
      authorization: `Bearer ${token}`,
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
