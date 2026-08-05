import { getApiBaseUrl } from "@/lib/api-client";

export type SpecialistAgentSummary = {
  id: string;
  name: string;
  domain: string;
  version: number;
  status: string;
  execution_mode: string;
  trigger_profiles: string[];
  allowed_tools_count: number;
  source: string;
};

export type SpecialistAgentsListResponse = {
  agents: SpecialistAgentSummary[];
};

export type SpecialistAgentsSummaryResponse = {
  total: number;
  active: number;
  draft: number;
  by_domain: Record<string, number>;
  by_execution_mode: Record<string, number>;
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

export function getSpecialistAgents(token: string) {
  return getAuthorizedJson<SpecialistAgentsListResponse>("/api/v1/specialist-agents", token);
}

export function getSpecialistAgentsSummary(token: string) {
  return getAuthorizedJson<SpecialistAgentsSummaryResponse>("/api/v1/specialist-agents/summary", token);
}
