"use client";

import { useRef, useState } from "react";
import {
  AlertCircle,
  FileJson,
  FileSpreadsheet,
  UploadCloud,
} from "lucide-react";

import { StatusBadge, type Status } from "@/components/dashboard/status-badge";
import { WorkspacePageHeader } from "@/components/clients/workspace-page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { simulateDatasetUpload } from "@/lib/mock-dataset-upload";
import { formatFileSize } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type {
  DatasetFormat,
  DatasetUploadHandler,
  DatasetUploadResult,
  IngestionHistoryItem,
  IngestionStatus,
} from "@/types/data-ingestion";

const statusMap: Record<IngestionStatus, Status> = {
  Processing: "pending",
  Completed: "active",
  Failed: "critical",
  "Needs Review": "warning",
};

const extensionFormats: Record<string, DatasetFormat> = {
  csv: "CSV",
  json: "JSON",
  xlsx: "XLSX",
};

type DataIngestionWorkspaceProps = {
  initialHistory: IngestionHistoryItem[];
  uploadHandler?: DatasetUploadHandler;
};

export function DataIngestionWorkspace({
  initialHistory,
  uploadHandler = simulateDatasetUpload,
}: DataIngestionWorkspaceProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [currentUpload, setCurrentUpload] = useState<DatasetUploadResult | null>(null);
  const [history, setHistory] = useState(initialHistory);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
    const format = extensionFormats[extension];

    if (!format) {
      setError("That file type is not supported. Choose a CSV, JSON, or XLSX file.");
      return;
    }

    setError(null);
    setCurrentUpload({
      id: `pending-${Date.now()}`,
      fileName: file.name,
      fileSize: file.size,
      format,
      rows: 0,
      columns: 0,
      status: "Processing",
    });

    try {
      const result = await uploadHandler(file);
      setCurrentUpload(result);
      setHistory((items) => [
        {
          id: result.id,
          fileName: result.fileName,
          format: result.format,
          records: result.rows,
          uploadedBy: "Operations Admin",
          uploadedAt: "Just now",
          status: result.status,
        },
        ...items,
      ]);
    } catch (uploadError) {
      setCurrentUpload((upload) =>
        upload ? { ...upload, status: "Failed" } : null,
      );
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "The file could not be processed.",
      );
    } finally {
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="space-y-6">
      <WorkspacePageHeader
        title="Data Ingestion"
        description="Upload customer datasets for profiling, schema mapping, and validation. Files are processed locally in this prototype."
      />

      <Card>
        <CardHeader className="border-b">
          <CardTitle>Upload Dataset</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
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
            onDragEnter={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={(event) => {
              event.preventDefault();
              if (event.currentTarget === event.target) setIsDragging(false);
            }}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragging(false);
              const file = event.dataTransfer.files[0];
              if (file) void handleFile(file);
            }}
            className={cn(
              "flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed px-6 py-10 text-center transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
              isDragging
                ? "border-primary bg-primary/5"
                : "border-border bg-muted/20 hover:border-primary/50 hover:bg-muted/40",
            )}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".csv,.json,.xlsx,text/csv,application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              className="sr-only"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void handleFile(file);
              }}
              aria-label="Choose dataset file"
            />
            <span className="mb-4 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <UploadCloud className="size-5" aria-hidden="true" />
            </span>
            <p className="font-medium">Drop a dataset here, or click to browse</p>
            <p className="mt-1.5 text-sm text-muted-foreground">
              CSV, JSON, or XLSX · Local simulation only
            </p>
            <div className="mt-4 flex gap-2" aria-hidden="true">
              <Badge variant="secondary">CSV</Badge>
              <Badge variant="secondary">JSON</Badge>
              <Badge variant="secondary">XLSX</Badge>
            </div>
          </div>

          {error ? (
            <div role="alert" className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
              <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
              {error}
            </div>
          ) : null}

          {currentUpload ? (
            <div className="rounded-xl border bg-card p-4" aria-live="polite">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  {currentUpload.format === "JSON" ? (
                    <FileJson className="size-5" aria-hidden="true" />
                  ) : (
                    <FileSpreadsheet className="size-5" aria-hidden="true" />
                  )}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{currentUpload.fileName}</p>
                  <p className="text-xs text-muted-foreground">Selected dataset</p>
                </div>
                <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-5">
                  <div><dt className="text-xs text-muted-foreground">File size</dt><dd className="mt-0.5 text-sm font-medium tabular-nums">{formatFileSize(currentUpload.fileSize)}</dd></div>
                  <div><dt className="text-xs text-muted-foreground">Format</dt><dd className="mt-0.5 text-sm font-medium">{currentUpload.format}</dd></div>
                  <div><dt className="text-xs text-muted-foreground">Rows</dt><dd className="mt-0.5 text-sm font-medium tabular-nums">{currentUpload.status === "Processing" ? "Detecting…" : currentUpload.rows.toLocaleString("en-US")}</dd></div>
                  <div><dt className="text-xs text-muted-foreground">Columns</dt><dd className="mt-0.5 text-sm font-medium tabular-nums">{currentUpload.status === "Processing" ? "—" : currentUpload.columns}</dd></div>
                  <div><dt className="text-xs text-muted-foreground">Status</dt><dd className="mt-1"><StatusBadge status={statusMap[currentUpload.status]} label={currentUpload.status} /></dd></div>
                </dl>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="border-b"><CardTitle>Ingestion History</CardTitle></CardHeader>
        <CardContent className="px-0">
          <Table className="min-w-[820px]">
            <TableHeader><TableRow className="hover:bg-transparent"><TableHead className="pl-4">File</TableHead><TableHead>Type</TableHead><TableHead className="text-right">Records</TableHead><TableHead>Uploaded By</TableHead><TableHead>Uploaded At</TableHead><TableHead className="pr-4">Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {history.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="max-w-64 truncate pl-4 font-medium">{item.fileName}</TableCell>
                  <TableCell><Badge variant="outline">{item.format}</Badge></TableCell>
                  <TableCell className="text-right tabular-nums">{item.records ? item.records.toLocaleString("en-US") : "—"}</TableCell>
                  <TableCell>{item.uploadedBy}</TableCell>
                  <TableCell className="text-muted-foreground">{item.uploadedAt}</TableCell>
                  <TableCell className="pr-4"><StatusBadge status={statusMap[item.status]} label={item.status} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
