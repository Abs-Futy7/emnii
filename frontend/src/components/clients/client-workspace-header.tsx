import Link from "next/link";
import { ArrowLeft, Building2, Database } from "lucide-react";

import { ClientStatusBadge } from "@/components/clients/client-status-badge";
import { Badge } from "@/components/ui/badge";
import type { Client } from "@/types/client";

export function ClientWorkspaceHeader({ client }: { client: Client }) {
  return (
    <header className="rounded-xl border bg-card p-5 shadow-xs sm:p-6">
      <Link
        href="/clients"
        className="mb-5 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        All clients
      </Link>
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div className="flex min-w-0 items-start gap-3.5">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/15">
            <Building2 className="size-5" aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="truncate text-2xl font-semibold tracking-tight sm:text-3xl">
                {client.company}
              </h1>
              <ClientStatusBadge status={client.status} />
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <span>{client.industry}</span>
              <span aria-hidden="true">•</span>
              <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                {client.workspaceId}
              </code>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 rounded-lg border bg-muted/30 px-3 py-2.5">
          <span className="flex size-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <Database className="size-4" aria-hidden="true" />
          </span>
          <div>
            <p className="text-xs text-muted-foreground">Data quality score</p>
            <p className="text-base font-semibold tabular-nums">
              {client.dataQualityScore}
              <span className="text-xs font-normal text-muted-foreground">/100</span>
            </p>
          </div>
          <Badge variant="secondary" className="ml-2">
            {client.dataQualityScore >= 90 ? "Excellent" : client.dataQualityScore >= 80 ? "Good" : "Review"}
          </Badge>
        </div>
      </div>
    </header>
  );
}
