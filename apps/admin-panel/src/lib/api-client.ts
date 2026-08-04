export type LivenessResponse = {
  service: string;
  environment: string;
  status: string;
};

export type ModuleStatus = {
  name: string;
  status: string;
};

export type ServiceMetadata = {
  service: string;
  environment: string;
  version: string;
  api_prefix: string;
  modules: ModuleStatus[];
};

export function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getApiLiveness() {
  return getJson<LivenessResponse>("/health/live");
}

export function getApiMetadata() {
  return getJson<ServiceMetadata>("/api/v1/meta");
}
