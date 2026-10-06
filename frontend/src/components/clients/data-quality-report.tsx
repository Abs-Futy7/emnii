import {
  AlertTriangle,
  AtSign,
  CheckCircle2,
  Gauge,
  MapPin,
  Rows3,
  ShieldCheck,
  UserRound,
  XCircle,
} from "lucide-react";

import { WorkspacePageHeader } from "@/components/clients/workspace-page-header";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusBadge, type Status } from "@/components/dashboard/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type {
  DataQualityReport as DataQualityReportData,
  ValidationSeverity,
} from "@/types/data-quality";

const severityStatus: Record<ValidationSeverity, Status> = {
  Info: "pending",
  Warning: "warning",
  Error: "critical",
};

const piiIcons = {
  Names: UserRound,
  Emails: AtSign,
  "Phone numbers": ShieldCheck,
  Addresses: MapPin,
};

function QualityBar({ value, label }: { value: number; label: string }) {
  const tone = value >= 95 ? "bg-emerald-500" : value >= 90 ? "bg-primary" : "bg-amber-500";

  return (
    <div
      className="h-2 overflow-hidden rounded-full bg-muted"
      role="progressbar"
      aria-label={`${label}: ${value}%`}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={value}
    >
      <div className={cn("h-full rounded-full", tone)} style={{ width: `${value}%` }} />
    </div>
  );
}

export function DataQualityReport({ report }: { report: DataQualityReportData }) {
  return (
    <div className="space-y-6">
      <WorkspacePageHeader
        title="Data Validation"
        description="Detailed quality results from the latest normalized customer dataset."
        actions={<Badge variant="secondary">Latest run · Oct 6, 2026 at 10:24</Badge>}
      />

      <section aria-labelledby="validation-summary-heading">
        <h3 id="validation-summary-heading" className="sr-only">Validation summary</h3>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <StatCard title="Total Records" value={report.totalRecords.toLocaleString("en-US")} description="Rows evaluated" icon={Rows3} />
          <StatCard title="Valid Records" value={report.validRecords.toLocaleString("en-US")} description="Passed blocking checks" icon={CheckCircle2} />
          <StatCard title="Warnings" value={report.warnings.toLocaleString("en-US")} description="Require review" icon={AlertTriangle} />
          <StatCard title="Errors" value={report.errors.toLocaleString("en-US")} description="Require correction" icon={XCircle} />
          <StatCard title="Data Quality Score" value={`${report.score}%`} description="Overall weighted score" icon={Gauge} />
        </div>
      </section>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>Validation Issues</CardTitle>
        </CardHeader>
        <CardContent className="px-0">
          <Table className="min-w-[820px]">
            <TableHeader><TableRow className="hover:bg-transparent"><TableHead className="pl-4">Issue</TableHead><TableHead>Severity</TableHead><TableHead className="text-right">Affected Rows</TableHead><TableHead className="text-right">Percentage</TableHead><TableHead className="pr-4 text-right">Action</TableHead></TableRow></TableHeader>
            <TableBody>
              {report.issues.map((issue) => (
                <TableRow key={issue.id}>
                  <TableCell className="pl-4"><p className="font-medium">{issue.issue}</p><p className="text-xs text-muted-foreground">{issue.description}</p></TableCell>
                  <TableCell><StatusBadge status={severityStatus[issue.severity]} label={issue.severity} /></TableCell>
                  <TableCell className="text-right tabular-nums">{issue.affectedRows.toLocaleString("en-US")}</TableCell>
                  <TableCell className="text-right tabular-nums">{issue.percentage.toFixed(2)}%</TableCell>
                  <TableCell className="pr-4 text-right"><Button variant="ghost" size="sm" type="button">{issue.action}</Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="grid items-start gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <CardHeader className="border-b"><CardTitle>Data Quality Breakdown</CardTitle></CardHeader>
          <CardContent className="space-y-5">
            {report.dimensions.map((dimension) => (
              <div key={dimension.name}>
                <div className="mb-2 flex items-end justify-between gap-4">
                  <div><p className="text-sm font-medium">{dimension.name}</p><p className="text-xs text-muted-foreground">{dimension.detail}</p></div>
                  <span className="text-sm font-semibold tabular-nums">{dimension.score}%</span>
                </div>
                <QualityBar value={dimension.score} label={dimension.name} />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="border-b">
            <div className="flex items-center justify-between gap-3"><div className="flex items-center gap-2"><ShieldCheck className="size-4 text-primary" aria-hidden="true" /><CardTitle>PII Detection</CardTitle></div><StatusBadge status="active" label={`Redaction ${report.redactionStatus}`} /></div>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
            {report.pii.map((item) => {
              const Icon = piiIcons[item.type];
              return (
                <div key={item.type} className="flex items-center gap-3 rounded-lg border bg-muted/20 p-3">
                  <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary"><Icon className="size-4" aria-hidden="true" /></span>
                  <div><p className="text-xs text-muted-foreground">{item.type} detected</p><p className="text-base font-semibold tabular-nums">{item.count.toLocaleString("en-US")}</p></div>
                </div>
              );
            })}
            <div className="sm:col-span-2 xl:col-span-1 2xl:col-span-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300">
              <p className="font-medium">Sensitive fields classified</p>
              <p className="mt-1 text-xs leading-5">Redaction rules are ready to apply before data is used by AI workflows.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
