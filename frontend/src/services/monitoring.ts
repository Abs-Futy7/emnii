import { monitoringSnapshot } from "@/data/mock-monitoring";
import { apiClient, assertEndpoint } from "@/lib/api";
import { endpoints } from "@/lib/endpoints";
import type { ApiResponse, ServiceOptions } from "@/types/api";
import type { MonitoringSnapshot } from "@/types/monitoring";

export async function getMonitoringSnapshot(options: ServiceOptions = {}): Promise<MonitoringSnapshot> {
  if (options.source !== "api") return monitoringSnapshot;
  const response = await apiClient.get<ApiResponse<MonitoringSnapshot>>(assertEndpoint(endpoints.monitoring.snapshot, "Get monitoring snapshot"));
  return response.data.data;
}
