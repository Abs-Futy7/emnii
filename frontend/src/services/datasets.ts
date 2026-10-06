import { ingestionHistory } from "@/data/mock-data-ingestion";
import { apiClient, assertEndpoint } from "@/lib/api";
import { endpoints } from "@/lib/endpoints";
import { simulateDatasetUpload } from "@/lib/mock-dataset-upload";
import type { ApiListResponse, ApiResponse, ServiceOptions } from "@/types/api";
import type { Dataset, IngestionHistoryItem } from "@/types/data-ingestion";

export async function listDatasets(clientId: string, options: ServiceOptions = {}): Promise<IngestionHistoryItem[]> {
  if (options.source !== "api") return ingestionHistory;
  const response = await apiClient.get<ApiListResponse<IngestionHistoryItem>>(assertEndpoint(endpoints.datasets.list?.(clientId) ?? null, "List datasets"));
  return response.data.data;
}
export async function uploadDataset(clientId: string, file: File, options: ServiceOptions = {}): Promise<Dataset> {
  if (options.source !== "api") return simulateDatasetUpload(file);
  const body = new FormData(); body.append("file", file);
  const response = await apiClient.post<ApiResponse<Dataset>>(assertEndpoint(endpoints.datasets.upload?.(clientId) ?? null, "Upload dataset"), body, { headers: { "Content-Type": "multipart/form-data" } });
  return response.data.data;
}
