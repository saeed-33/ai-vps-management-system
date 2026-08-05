import { getApiBaseUrl } from "@/lib/api-client";

export type UserSummary = {
  id: string;
  email: string;
  display_name: string;
  status: string;
  roles: string[];
  source: string;
};

export type UsersListResponse = {
  users: UserSummary[];
};

export type RoleSummary = {
  code: string;
  name: string;
  permission_count: number;
};

export type RolesListResponse = {
  roles: RoleSummary[];
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

export function getUsers(token: string) {
  return getAuthorizedJson<UsersListResponse>("/api/v1/users", token);
}

export function getRoles(token: string) {
  return getAuthorizedJson<RolesListResponse>("/api/v1/users/roles", token);
}
