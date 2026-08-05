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

export type ServerSshAccessPublic = {
  enabled: boolean;
  host: string | null;
  port: number;
  username: string | null;
  auth_method: string;
  has_password: boolean;
  private_key_path: string | null;
};

export type ServerSshAccessUpdate = {
  enabled: boolean;
  host: string | null;
  port: number;
  username: string | null;
  private_key_path: string | null;
  password: string | null;
};

export type ServerDetail = ServerSummary & {
  metadata: Record<string, string>;
  assigned_monitoring_profiles: string[];
  ssh_access: ServerSshAccessPublic;
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

async function sendAuthorizedJson<T>(path: string, token: string, payload: unknown): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "PUT",
    headers: {
      accept: "application/json",
      authorization: `Bearer ${token}`,
      "content-type": "application/json",
    },
    body: JSON.stringify(payload),
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

export function getServer(token: string, serverId: string) {
  return getAuthorizedJson<ServerDetail>(`/api/v1/servers/${serverId}`, token);
}

export function updateServerSshAccess(token: string, serverId: string, payload: ServerSshAccessUpdate) {
  return sendAuthorizedJson<ServerSshAccessPublic>(`/api/v1/servers/${serverId}/ssh-access`, token, payload);
}
