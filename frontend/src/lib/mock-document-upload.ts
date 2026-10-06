import type {
  DocumentType,
  DocumentUploadHandler,
} from "@/types/knowledge-document";

const typeByExtension: Record<string, { type: DocumentType; mimeType: string }> = {
  pdf: { type: "PDF", mimeType: "application/pdf" },
  docx: {
    type: "DOCX",
    mimeType:
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  },
  txt: { type: "TXT", mimeType: "text/plain" },
  md: { type: "Markdown", mimeType: "text/markdown" },
  markdown: { type: "Markdown", mimeType: "text/markdown" },
};

export const simulateDocumentUpload: DocumentUploadHandler = async (
  file,
  context,
) => {
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const detected = typeByExtension[extension];

  if (!detected) {
    throw new Error("Choose a PDF, DOCX, TXT, or Markdown document.");
  }

  await new Promise((resolve) => setTimeout(resolve, 700));

  return {
    id: `local-document-${Date.now()}`,
    name: file.name,
    type: detected.type,
    size: file.size,
    chunks: 0,
    indexStatus: "Uploaded",
    uploadedAt: "Just now",
    uploadedBy: "Operations Admin",
    tenant: context.company,
    lastIndexedAt: "Not indexed yet",
    metadata: {
      category: "Uncategorized",
      language: "English",
      source: "Manual upload",
      mimeType: detected.mimeType,
    },
  };
};
