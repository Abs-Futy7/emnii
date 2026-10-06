import { clients, getClientById } from "@/data/mock-clients";
import { apiClient, assertEndpoint } from "@/lib/api";
import { endpoints } from "@/lib/endpoints";
import type { ApiListResponse, ApiResponse, ServiceOptions } from "@/types/api";
import type { Client } from "@/types/client";

export async function listClients(options: ServiceOptions = {}): Promise<Client[]> {
  if (options.source !== "api") return clients;
  const response = await apiClient.get<ApiListResponse<Client>>(assertEndpoint(endpoints.clients.list, "List clients"));
  return response.data.data;
}
export async function getClient(clientId: string, options: ServiceOptions = {}): Promise<Client | undefined> {
  if (options.source !== "api") return getClientById(clientId);
  const route = endpoints.clients.detail;
  const response = await apiClient.get<ApiResponse<Client>>(assertEndpoint(route?.(clientId) ?? null, "Get client"));
  return response.data.data;
}
