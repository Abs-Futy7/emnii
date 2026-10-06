import type {
  DatasetFormat,
  DatasetUploadHandler,
} from "@/types/data-ingestion";

const formatByExtension: Record<string, DatasetFormat> = {
  csv: "CSV",
  json: "JSON",
  xlsx: "XLSX",
};

export const simulateDatasetUpload: DatasetUploadHandler = async (file) => {
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const format = formatByExtension[extension];

  if (!format) {
    throw new Error("Choose a CSV, JSON, or XLSX file.");
  }

  await new Promise((resolve) => setTimeout(resolve, 900));

  return {
    id: `local-${Date.now()}`,
    fileName: file.name,
    fileSize: file.size,
    format,
    rows: Math.max(1, Math.round(file.size / (format === "JSON" ? 140 : 96))),
    columns: format === "XLSX" ? 18 : format === "JSON" ? 14 : 12,
    status: "Needs Review",
  };
};
