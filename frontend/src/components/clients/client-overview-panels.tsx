import { Bot, FileText, PlugZap, UploadCloud } from "lucide-react";

import { StatusBadge, type Status } from "@/components/dashboard/status-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { AiActivity, IngestionJob, WorkspaceDocument, WorkspaceIntegration } from "@/types/client-workspace";

import { formatCompactNumber } from "@/lib/formatters";

const operationStatus: Record<string, Status> = {
  completed: "active",
  indexed: "active",
  connected: "active",
  processing: "pending",
  syncing: "pending",
  failed: "critical",
  error: "critical",
};

function toLabel(value: string) {
  return value[0].toUpperCase() + value.slice(1);
}

function PanelTitle({ icon: Icon, children }: { icon: typeof UploadCloud; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2">
      <Icon className="size-4 text-primary" aria-hidden="true" />
      <CardTitle>{children}</CardTitle>
    </div>
  );
}

export function IngestionJobsPanel({ jobs }: { jobs: IngestionJob[] }) {
  return (
    <Card>
      <CardHeader className="border-b"><PanelTitle icon={UploadCloud}>Recent Ingestion Jobs</PanelTitle></CardHeader>
      <CardContent className="px-0">
        <Table>
          <TableHeader><TableRow className="hover:bg-transparent"><TableHead className="pl-4">Source</TableHead><TableHead>Status</TableHead><TableHead className="pr-4 text-right">Records</TableHead></TableRow></TableHeader>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.id}>
                <TableCell className="pl-4"><p className="font-medium">{job.source}</p><p className="max-w-52 truncate text-xs text-muted-foreground">{job.fileName} · {job.startedAt}</p></TableCell>
                <TableCell><StatusBadge status={operationStatus[job.status]} label={toLabel(job.status)} /></TableCell>
                <TableCell className="pr-4 text-right tabular-nums">{formatCompactNumber(job.records)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

export function RecentDocumentsPanel({ documents }: { documents: WorkspaceDocument[] }) {
  return (
    <Card>
      <CardHeader className="border-b"><PanelTitle icon={FileText}>Recent Documents</PanelTitle></CardHeader>
      <CardContent className="divide-y px-0">
        {documents.map((document) => (
          <div key={document.id} className="flex items-center gap-3 px-4 py-3.5">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-xs font-semibold text-muted-foreground">{document.type}</span>
            <div className="min-w-0 flex-1"><p className="truncate text-sm font-medium">{document.name}</p><p className="text-xs text-muted-foreground">{document.chunks} chunks · {document.updatedAt}</p></div>
            <StatusBadge status={operationStatus[document.status]} label={toLabel(document.status)} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export function IntegrationStatusPanel({ integrations }: { integrations: WorkspaceIntegration[] }) {
  return (
    <Card>
      <CardHeader className="border-b"><PanelTitle icon={PlugZap}>Integration Status</PanelTitle></CardHeader>
      <CardContent className="divide-y px-0">
        {integrations.map((integration) => (
          <div key={integration.id} className="flex items-center gap-3 px-4 py-3.5">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary"><PlugZap className="size-4" aria-hidden="true" /></span>
            <div className="min-w-0 flex-1"><p className="text-sm font-medium">{integration.name}</p><p className="text-xs text-muted-foreground">Last sync: {integration.lastSync}</p></div>
            <StatusBadge status={operationStatus[integration.status]} label={toLabel(integration.status)} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export function LatestAiActivityPanel({ activity }: { activity: AiActivity[] }) {
  return (
    <Card>
      <CardHeader className="border-b"><PanelTitle icon={Bot}>Latest AI Activity</PanelTitle></CardHeader>
      <CardContent className="divide-y px-0">
        {activity.map((item) => (
          <div key={item.id} className="flex gap-3 px-4 py-3.5">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-violet-500/10 text-violet-600 dark:text-violet-400"><Bot className="size-4" aria-hidden="true" /></span>
            <div className="min-w-0 flex-1"><p className="text-sm leading-5 font-medium">{item.summary}</p><div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground"><span>{item.channel}</span><span aria-hidden="true">•</span><span>{item.occurredAt}</span></div></div>
            <Badge variant="secondary" className="h-fit tabular-nums">{item.confidence}%</Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
