import { getApiBaseUrl } from "@/lib/api-client";

export type ServerSummary = {
  id: string;
  name: string;
  hostname: string;
  ip_address: string | null;
  os_family: string | null;
  environment: string;
  status: string;
  monitoring_status: string;
  source: string;
};

export type ServersListResponse = {
  servers: ServerSummary[];
};

export type ServersSummaryResponse = {
  total: number;
  active: number;
  disabled: number;
  maintenance: number;
  by_environment: Record<string, number>;
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

export function getServers(token: string) {
  return getAuthorizedJson<ServersListResponse>("/api/v1/servers", token);
}

export function getServersSummary(token: string) {
  return getAuthorizedJson<ServersSummaryResponse>("/api/v1/servers/summary", token);
}
