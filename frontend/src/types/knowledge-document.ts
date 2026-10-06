export type DocumentType = "PDF" | "DOCX" | "TXT" | "Markdown";
export type IndexStatus = "Uploaded" | "Processing" | "Indexed" | "Failed";

export type Document = {
  id: string;
  name: string;
  type: DocumentType;
  size: number;
  chunks: number;
  indexStatus: IndexStatus;
  uploadedAt: string;
  uploadedBy: string;
  tenant: string;
  lastIndexedAt: string;
  metadata: {
    category: string;
    language: string;
    source: string;
    mimeType: string;
  };
};

export type KnowledgeDocument = Document;

export type DocumentUploadContext = { clientId: string; company: string };

export type DocumentUploadHandler = (
  file: File,
  context: DocumentUploadContext,
) => Promise<KnowledgeDocument>;
