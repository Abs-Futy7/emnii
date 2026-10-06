"use client";

import { useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  Eye,
  FileText,
  Search,
  UploadCloud,
} from "lucide-react";

import { WorkspacePageHeader } from "@/components/clients/workspace-page-header";
import { StatusBadge, type Status } from "@/components/dashboard/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { simulateDocumentUpload } from "@/lib/mock-document-upload";
import { formatFileSize } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type {
  DocumentUploadHandler,
  IndexStatus,
  KnowledgeDocument,
} from "@/types/knowledge-document";

const statusMap: Record<IndexStatus, Status> = {
  Uploaded: "pending",
  Processing: "pending",
  Indexed: "active",
  Failed: "critical",
};

function DocumentDetails({ document }: { document: KnowledgeDocument }) {
  return (
    <DialogContent className="sm:max-w-lg">
      <DialogHeader>
        <div className="flex items-start gap-3 pr-8">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <FileText className="size-5" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <DialogTitle className="truncate">{document.name}</DialogTitle>
            <DialogDescription className="mt-1">
              Knowledge document metadata and indexing details.
            </DialogDescription>
          </div>
        </div>
      </DialogHeader>
      <dl className="grid gap-4 rounded-lg border bg-muted/20 p-4 sm:grid-cols-2">
        <div><dt className="text-xs text-muted-foreground">Document type</dt><dd className="mt-1 font-medium">{document.type}</dd></div>
        <div><dt className="text-xs text-muted-foreground">File size</dt><dd className="mt-1 font-medium tabular-nums">{formatFileSize(document.size)}</dd></div>
        <div><dt className="text-xs text-muted-foreground">Indexing status</dt><dd className="mt-1"><StatusBadge status={statusMap[document.indexStatus]} label={document.indexStatus} /></dd></div>
        <div><dt className="text-xs text-muted-foreground">Chunk count</dt><dd className="mt-1 font-medium tabular-nums">{document.chunks || "Not chunked"}</dd></div>
        <div><dt className="text-xs text-muted-foreground">Tenant / client</dt><dd className="mt-1 font-medium">{document.tenant}</dd></div>
        <div><dt className="text-xs text-muted-foreground">Last indexed</dt><dd className="mt-1 font-medium">{document.lastIndexedAt}</dd></div>
      </dl>
      <div>
        <h3 className="text-sm font-medium">Metadata</h3>
        <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
          <div><dt className="text-xs text-muted-foreground">Category</dt><dd className="mt-0.5">{document.metadata.category}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Language</dt><dd className="mt-0.5">{document.metadata.language}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Source</dt><dd className="mt-0.5">{document.metadata.source}</dd></div>
          <div><dt className="text-xs text-muted-foreground">Uploaded by</dt><dd className="mt-0.5">{document.uploadedBy}</dd></div>
        </dl>
      </div>
      <DialogFooter showCloseButton />
    </DialogContent>
  );
}

export function DocumentsWorkspace({
  clientId,
  company,
  initialDocuments,
  uploadHandler = simulateDocumentUpload,
}: {
  clientId: string;
  company: string;
  initialDocuments: KnowledgeDocument[];
  uploadHandler?: DocumentUploadHandler;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [documents, setDocuments] = useState(() =>
    initialDocuments.map((document) => ({ ...document, tenant: company })),
  );
  const [query, setQuery] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filteredDocuments = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return normalized
      ? documents.filter(
          (document) =>
            document.name.toLowerCase().includes(normalized) ||
            document.type.toLowerCase().includes(normalized),
        )
      : documents;
  }, [documents, query]);

  async function handleFile(file: File) {
    setError(null);
    setIsUploading(true);
    try {
      const document = await uploadHandler(file, { clientId, company });
      setDocuments((items) => [document, ...items]);
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "The document could not be uploaded.",
      );
    } finally {
      setIsUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="space-y-6">
      <WorkspacePageHeader
        title="Documents"
        description="Manage the trusted content indexed for this client's knowledge and retrieval workflows."
      />

      <Card>
        <CardHeader className="border-b"><CardTitle>Upload Document</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div
            role="button"
            tabIndex={0}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                inputRef.current?.click();
              }
            }}
            onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={(event) => {
              event.preventDefault();
              if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setIsDragging(false);
            }}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragging(false);
              const file = event.dataTransfer.files[0];
              if (file) void handleFile(file);
            }}
            className={cn(
              "flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed p-6 text-center outline-none transition-colors focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
              isDragging ? "border-primary bg-primary/5" : "bg-muted/20 hover:border-primary/50 hover:bg-muted/40",
            )}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md,.markdown,application/pdf,text/plain,text/markdown,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="sr-only"
              aria-label="Choose knowledge document"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void handleFile(file);
              }}
            />
            <span className="mb-3 flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <UploadCloud className="size-5" aria-hidden="true" />
            </span>
            <p className="font-medium">{isUploading ? "Adding document…" : "Drop a document here, or click to browse"}</p>
            <p className="mt-1 text-sm text-muted-foreground">PDF, DOCX, TXT, or Markdown · Stored locally for this prototype</p>
          </div>
          {error ? <div role="alert" className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"><AlertCircle className="size-4" aria-hidden="true" />{error}</div> : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="border-b">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>Knowledge Documents</CardTitle>
            <div className="relative w-full sm:w-72">
              <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
              <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search documents…" aria-label="Search documents" className="pl-8" />
            </div>
          </div>
          <p className="text-xs text-muted-foreground" aria-live="polite">{filteredDocuments.length} document{filteredDocuments.length === 1 ? "" : "s"}</p>
        </CardHeader>
        <CardContent className="px-0">
          {filteredDocuments.length ? (
            <Table className="min-w-[900px]">
              <TableHeader><TableRow className="hover:bg-transparent"><TableHead className="pl-4">Name</TableHead><TableHead>Type</TableHead><TableHead className="text-right">Size</TableHead><TableHead className="text-right">Chunks</TableHead><TableHead>Index Status</TableHead><TableHead>Uploaded At</TableHead><TableHead className="pr-4 text-right">Actions</TableHead></TableRow></TableHeader>
              <TableBody>
                {filteredDocuments.map((document) => (
                  <TableRow key={document.id}>
                    <TableCell className="pl-4"><div className="flex items-center gap-2.5"><span className="flex size-8 items-center justify-center rounded-lg bg-muted text-muted-foreground"><FileText className="size-4" aria-hidden="true" /></span><span className="max-w-64 truncate font-medium">{document.name}</span></div></TableCell>
                    <TableCell><Badge variant="outline">{document.type}</Badge></TableCell>
                    <TableCell className="text-right tabular-nums">{formatFileSize(document.size)}</TableCell>
                    <TableCell className="text-right tabular-nums">{document.chunks || "—"}</TableCell>
                    <TableCell><StatusBadge status={statusMap[document.indexStatus]} label={document.indexStatus} /></TableCell>
                    <TableCell className="text-muted-foreground">{document.uploadedAt}</TableCell>
                    <TableCell className="pr-4 text-right">
                      <Dialog>
                        <DialogTrigger render={<Button variant="ghost" size="sm" />}>
                          <Eye data-icon="inline-start" aria-hidden="true" />
                          Details
                        </DialogTrigger>
                        <DocumentDetails document={document} />
                      </Dialog>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="p-10 text-center"><FileText className="mx-auto size-7 text-muted-foreground" aria-hidden="true" /><p className="mt-3 font-medium">No documents found</p><p className="mt-1 text-sm text-muted-foreground">Try a different search term.</p></div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
