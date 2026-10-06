"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  EyeOff,
  GitMerge,
  LoaderCircle,
  Play,
  Save,
} from "lucide-react";

import { WorkspacePageHeader } from "@/components/clients/workspace-page-header";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
  CanonicalField,
  MappingStatus,
  SchemaMappingRow,
} from "@/types/schema-mapping";

function ConfidenceIndicator({ value }: { value: number }) {
  const tone = value >= 90 ? "bg-emerald-500" : value >= 70 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="flex min-w-32 items-center gap-2">
      <div
        className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted"
        role="progressbar"
        aria-label={`Mapping confidence: ${value}%`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={value}
      >
        <div className={cn("h-full rounded-full", tone)} style={{ width: `${value}%` }} />
      </div>
      <span className={cn("w-9 text-right text-sm font-medium tabular-nums", value < 70 && "text-red-600 dark:text-red-400")}>{value}%</span>
    </div>
  );
}

function MappingStatusBadge({ status }: { status: MappingStatus }) {
  if (status === "approved") return <StatusBadge status="active" label="Approved" />;
  if (status === "ignored") return <StatusBadge status="inactive" label="Ignored" />;
  if (status === "review") return <StatusBadge status="warning" label="Needs Review" />;
  return <StatusBadge status="pending" label="Suggested" />;
}

export function SchemaMappingWorkspace({
  clientId,
  initialMappings,
  fields,
}: {
  clientId: string;
  initialMappings: SchemaMappingRow[];
  fields: CanonicalField[];
}) {
  const router = useRouter();
  const [mappings, setMappings] = useState(initialMappings);
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved">("idle");
  const lowConfidenceCount = mappings.filter(
    (mapping) => mapping.confidence < 70 && mapping.status !== "ignored",
  ).length;

  function updateMapping(id: string, changes: Partial<SchemaMappingRow>) {
    setSaveState("idle");
    setMappings((rows) =>
      rows.map((row) => (row.id === id ? { ...row, ...changes } : row)),
    );
  }

  function approveHighConfidence() {
    setMappings((rows) =>
      rows.map((row) =>
        row.confidence >= 90 && row.status !== "ignored"
          ? { ...row, status: "approved" }
          : row,
      ),
    );
    setSaveState("idle");
  }

  async function saveMapping() {
    setSaveState("saving");
    await new Promise((resolve) => setTimeout(resolve, 600));
    setSaveState("saved");
  }

  return (
    <div className="space-y-6">
      <WorkspacePageHeader
        title="Schema Mapping"
        description="Review AI-suggested mappings from source columns to the ResolveOps canonical customer schema."
        actions={
          <>
            <Button variant="outline" type="button" onClick={approveHighConfidence}>
              <Check data-icon="inline-start" aria-hidden="true" />
              Approve high confidence
            </Button>
            <Button type="button" onClick={() => void saveMapping()} disabled={saveState === "saving"}>
              {saveState === "saving" ? (
                <LoaderCircle data-icon="inline-start" className="animate-spin" aria-hidden="true" />
              ) : (
                <Save data-icon="inline-start" aria-hidden="true" />
              )}
              {saveState === "saving" ? "Saving…" : "Save Mapping"}
            </Button>
            <Button type="button" variant="secondary" onClick={() => router.push(`/clients/${clientId}/validation`)}>
              <Play data-icon="inline-start" aria-hidden="true" />
              Run Validation
            </Button>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <Card size="sm"><CardContent><p className="text-xs text-muted-foreground">Source columns</p><p className="mt-1 text-2xl font-semibold tabular-nums">{mappings.length}</p></CardContent></Card>
        <Card size="sm"><CardContent><p className="text-xs text-muted-foreground">Approved mappings</p><p className="mt-1 text-2xl font-semibold tabular-nums">{mappings.filter((item) => item.status === "approved").length}</p></CardContent></Card>
        <Card size="sm" className={cn(lowConfidenceCount && "ring-amber-500/40")}><CardContent><p className="text-xs text-muted-foreground">Low confidence</p><p className="mt-1 text-2xl font-semibold tabular-nums">{lowConfidenceCount}</p></CardContent></Card>
      </div>

      {lowConfidenceCount ? (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
          <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
          <div><p className="font-medium">{lowConfidenceCount} mapping needs review</p><p className="mt-0.5 text-amber-700 dark:text-amber-300">Confirm the canonical field or ignore the source column before validation.</p></div>
        </div>
      ) : null}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <div className="flex items-center gap-2"><GitMerge className="size-4 text-primary" aria-hidden="true" /><CardTitle>Column Mapping</CardTitle></div>
          <p className="text-xs text-muted-foreground" aria-live="polite">
            {saveState === "saved" ? <span className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400"><CheckCircle2 className="size-3.5" aria-hidden="true" />Mapping saved locally</span> : "AI suggestions based on sample values"}
          </p>
        </CardHeader>
        <CardContent className="px-0">
          <Table className="min-w-[1080px]">
            <TableHeader><TableRow className="hover:bg-transparent"><TableHead className="pl-4">Source Column</TableHead><TableHead>Sample Value</TableHead><TableHead>Detected Type</TableHead><TableHead>Suggested Canonical Field</TableHead><TableHead>Confidence</TableHead><TableHead className="pr-4">Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {mappings.map((mapping) => (
                <TableRow key={mapping.id} className={cn(mapping.confidence < 70 && mapping.status !== "ignored" && "bg-amber-50/50 dark:bg-amber-950/10")}>
                  <TableCell className="pl-4"><code className="rounded bg-muted px-1.5 py-0.5 text-xs font-medium">{mapping.sourceColumn}</code></TableCell>
                  <TableCell className="max-w-52 truncate text-muted-foreground">{mapping.sampleValue}</TableCell>
                  <TableCell><Badge variant="outline">{mapping.detectedType}</Badge></TableCell>
                  <TableCell>
                    <Select
                      value={mapping.canonicalField}
                      onValueChange={(value) =>
                        updateMapping(mapping.id, {
                          canonicalField: value ?? "unmapped",
                          status: value === "ignored" ? "ignored" : mapping.confidence < 70 ? "review" : "suggested",
                        })
                      }
                    >
                      <SelectTrigger className="w-52" aria-label={`Canonical field for ${mapping.sourceColumn}`}><SelectValue /></SelectTrigger>
                      <SelectContent align="start">
                        <SelectItem value="unmapped">Unmapped</SelectItem>
                        {fields.map((field) => <SelectItem key={field.id} value={field.id}>{field.name}</SelectItem>)}
                        <SelectItem value="ignored">Ignore column</SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell><ConfidenceIndicator value={mapping.confidence} /></TableCell>
                  <TableCell className="pr-4">
                    <div className="flex items-center gap-1.5">
                      <MappingStatusBadge status={mapping.status} />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-xs"
                        title="Approve mapping"
                        aria-label={`Approve ${mapping.sourceColumn} mapping`}
                        disabled={mapping.canonicalField === "unmapped" || mapping.status === "ignored"}
                        onClick={() => updateMapping(mapping.id, { status: "approved" })}
                      >
                        <Check aria-hidden="true" />
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-xs"
                        title="Ignore source column"
                        aria-label={`Ignore ${mapping.sourceColumn}`}
                        onClick={() => updateMapping(mapping.id, { canonicalField: "ignored", status: "ignored" })}
                      >
                        <EyeOff aria-hidden="true" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="border-b"><CardTitle>Canonical Schema Fields</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {fields.map((field) => (
              <div key={field.id} className="rounded-lg border bg-muted/20 p-3">
                <div className="flex items-center justify-between gap-2"><code className="text-sm font-semibold">{field.name}</code>{field.required ? <Badge variant="secondary">Required</Badge> : <Badge variant="outline">Optional</Badge>}</div>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">{field.description}</p>
                <p className="mt-2 font-mono text-[11px] text-primary">{field.dataType}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
