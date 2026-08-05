import { getApiBaseUrl } from "@/lib/api-client";

export type AllowedToolSummary = {
  id: string;
  code: string;
  name: string;
  category: string;
  version: number;
  status: string;
  execution_scope: string;
  read_only: boolean;
  used_by: string[];
  source: string;
};

export type AllowedToolsListResponse = {
  tools: AllowedToolSummary[];
};

export type AllowedToolsSummaryResponse = {
  total: number;
  active: number;
  draft: number;
  read_only: number;
  by_category: Record<string, number>;
  by_scope: Record<string, number>;
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

export function getAllowedTools(token: string) {
  return getAuthorizedJson<AllowedToolsListResponse>("/api/v1/allowed-tools", token);
}

export function getAllowedToolsSummary(token: string) {
  return getAuthorizedJson<AllowedToolsSummaryResponse>("/api/v1/allowed-tools/summary", token);
}
