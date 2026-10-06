import { getTicketById, supportTickets } from "@/data/mock-tickets";
import { apiClient, assertEndpoint } from "@/lib/api";
import { endpoints } from "@/lib/endpoints";
import type { ApiListResponse, ApiResponse, ServiceOptions } from "@/types/api";
import type { SupportTicket } from "@/types/support-ticket";

export async function listTickets(options: ServiceOptions = {}): Promise<SupportTicket[]> {
  if (options.source !== "api") return supportTickets;
  const response = await apiClient.get<ApiListResponse<SupportTicket>>(assertEndpoint(endpoints.tickets.list, "List tickets"));
  return response.data.data;
}
export async function getTicket(ticketId: string, options: ServiceOptions = {}): Promise<SupportTicket | undefined> {
  if (options.source !== "api") return getTicketById(ticketId);
  const response = await apiClient.get<ApiResponse<SupportTicket>>(assertEndpoint(endpoints.tickets.detail?.(ticketId) ?? null, "Get ticket"));
  return response.data.data;
}
