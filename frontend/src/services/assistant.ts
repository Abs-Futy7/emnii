import { supportAssistantCase } from "@/data/mock-support-assistant";
import { apiClient, assertEndpoint } from "@/lib/api";
import { endpoints } from "@/lib/endpoints";
import type { ApiResponse, ServiceOptions } from "@/types/api";
import type { SupportAssistantCase } from "@/types/support-assistant";

export async function getAssistantCase(clientId: string, options: ServiceOptions = {}): Promise<SupportAssistantCase> {
  if (options.source !== "api") return supportAssistantCase;
  const response = await apiClient.get<ApiResponse<SupportAssistantCase>>(assertEndpoint(endpoints.assistant.case?.(clientId) ?? null, "Get assistant case"));
  return response.data.data;
}
