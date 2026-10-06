import { knowledgeDocuments } from "@/data/mock-documents";
import { apiClient, assertEndpoint } from "@/lib/api";
import { endpoints } from "@/lib/endpoints";
import { simulateDocumentUpload } from "@/lib/mock-document-upload";
import type { ApiListResponse, ApiResponse, ServiceOptions } from "@/types/api";
import type { Document, DocumentUploadContext } from "@/types/knowledge-document";

export async function listDocuments(clientId: string, options: ServiceOptions = {}): Promise<Document[]> {
  if (options.source !== "api") return knowledgeDocuments;
  const response = await apiClient.get<ApiListResponse<Document>>(assertEndpoint(endpoints.documents.list?.(clientId) ?? null, "List documents"));
  return response.data.data;
}
export async function uploadDocument(clientId: string, file: File, context: DocumentUploadContext, options: ServiceOptions = {}): Promise<Document> {
  if (options.source !== "api") return simulateDocumentUpload(file, context);
  const body = new FormData(); body.append("file", file);
  const response = await apiClient.post<ApiResponse<Document>>(assertEndpoint(endpoints.documents.upload?.(clientId) ?? null, "Upload document"), body, { headers: { "Content-Type": "multipart/form-data" } });
  return response.data.data;
}
