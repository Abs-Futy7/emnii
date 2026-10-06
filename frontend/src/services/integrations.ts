import { integrations } from "@/data/mock-integrations";
import { apiClient, assertEndpoint } from "@/lib/api";
import { endpoints } from "@/lib/endpoints";
import type { ApiListResponse, ServiceOptions } from "@/types/api";
import type { Integration } from "@/types/integration";

export async function listIntegrations(options: ServiceOptions = {}): Promise<Integration[]> {
  if (options.source !== "api") return integrations;
  const response = await apiClient.get<ApiListResponse<Integration>>(assertEndpoint(endpoints.integrations.list, "List integrations"));
  return response.data.data;
}
