export type DatasetFormat = "CSV" | "JSON" | "XLSX";

export type IngestionStatus =
  | "Processing"
  | "Completed"
  | "Failed"
  | "Needs Review";

export type Dataset = {
  id: string;
  fileName: string;
  fileSize: number;
  format: DatasetFormat;
  rows: number;
  columns: number;
  status: IngestionStatus;
};

export type DatasetUploadResult = Dataset;

export type IngestionHistoryItem = {
  id: string;
  fileName: string;
  format: DatasetFormat;
  records: number;
  uploadedBy: string;
  uploadedAt: string;
  status: IngestionStatus;
};

export type DatasetUploadHandler = (file: File) => Promise<DatasetUploadResult>;
