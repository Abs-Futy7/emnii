"use client";

import { useState } from "react";
import {
  Braces,
  CircleGauge,
  ContactRound,
  DatabaseZap,
  GitFork,
  Info,
  LoaderCircle,
  MessageSquare,
  PlugZap,
  RefreshCw,
  Ticket,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react";

import { StatusBadge, type Status } from "@/components/dashboard/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type {
  Integration,
  IntegrationHealth,
  IntegrationStatus,
} from "@/types/integration";

const iconMap: Record<Integration["icon"], LucideIcon> = {
  github: GitFork,
  slack: MessageSquare,
  crm: ContactRound,
  ticketing: Ticket,
  api: Braces,
  mockcorp: DatabaseZap,
};

const statusMap: Record<IntegrationStatus, Status> = {
  Connected: "active",
  Disconnected: "inactive",
  Degraded: "warning",
};

const healthMap: Record<IntegrationHealth, Status> = {
  Healthy: "active",
  Warning: "warning",
  Offline: "inactive",
};

export function IntegrationsGrid({ initialIntegrations }: { initialIntegrations: Integration[] }) {
  const [items, setItems] = useState(initialIntegrations);
  const [selected, setSelected] = useState<Integration | null>(null);
  const [connectingId, setConnectingId] = useState<string | null>(null);

  async function connect(integration: Integration) {
    setConnectingId(integration.id);
    await new Promise((resolve) => setTimeout(resolve, 700));
    setItems((current) =>
      current.map((item) =>
        item.id === integration.id
          ? { ...item, status: "Connected", health: "Healthy", lastSync: "Just now" }
          : item,
      ),
    );
    setConnectingId(null);
  }

  return (
    <>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {items.map((integration) => {
          const Icon = iconMap[integration.icon];
          const isConnecting = connectingId === integration.id;

          return (
            <Card key={integration.id} className="transition-shadow hover:shadow-sm">
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/15"><Icon className="size-5" aria-hidden="true" /></span>
                  <StatusBadge status={statusMap[integration.status]} label={integration.status} />
                </div>
                <div className="mt-3"><CardTitle>{integration.name}</CardTitle><p className="mt-1 text-xs text-muted-foreground">{integration.category}</p></div>
              </CardHeader>
              <CardContent className="flex-1">
                <p className="min-h-10 text-sm leading-5 text-muted-foreground">{integration.description}</p>
                <dl className="mt-5 grid grid-cols-2 gap-3 rounded-lg bg-muted/30 p-3">
                  <div><dt className="text-[11px] text-muted-foreground">Last sync</dt><dd className="mt-0.5 text-xs font-medium">{integration.lastSync}</dd></div>
                  <div><dt className="text-[11px] text-muted-foreground">Records synced</dt><dd className="mt-0.5 text-xs font-medium tabular-nums">{integration.recordsSynced.toLocaleString("en-US")}</dd></div>
                  <div className="col-span-2 flex items-center justify-between"><dt className="text-[11px] text-muted-foreground">Health</dt><dd><StatusBadge status={healthMap[integration.health]} label={integration.health} /></dd></div>
                </dl>
              </CardContent>
              <CardFooter className="gap-2">
                <Button
                  type="button"
                  className="flex-1"
                  variant={integration.status === "Disconnected" ? "default" : "outline"}
                  disabled={isConnecting}
                  onClick={() =>
                    integration.status === "Disconnected"
                      ? void connect(integration)
                      : setSelected(integration)
                  }
                >
                  {isConnecting ? <LoaderCircle data-icon="inline-start" className="animate-spin" aria-hidden="true" /> : <PlugZap data-icon="inline-start" aria-hidden="true" />}
                  {isConnecting ? "Connecting…" : integration.status === "Disconnected" ? "Connect" : "Configure"}
                </Button>
                <Button type="button" variant="ghost" size="icon" aria-label={`View ${integration.name} connector details`} title="Connector details" onClick={() => setSelected(integration)}>
                  <Info aria-hidden="true" />
                </Button>
              </CardFooter>
            </Card>
          );
        })}
      </div>

      <Dialog open={Boolean(selected)} onOpenChange={(open) => { if (!open) setSelected(null); }}>
        {selected ? (
          <DialogContent className="sm:max-w-xl">
            <DialogHeader>
              <div className="flex items-start gap-3 pr-8">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">{(() => { const Icon = iconMap[selected.icon]; return <Icon className="size-5" aria-hidden="true" />; })()}</span>
                <div><DialogTitle>{selected.name}</DialogTitle><DialogDescription className="mt-1">Connector configuration and operational health.</DialogDescription></div>
              </div>
            </DialogHeader>

            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge status={statusMap[selected.status]} label={selected.status} />
              <StatusBadge status={healthMap[selected.health]} label={selected.health} />
            </div>

            <dl className="grid gap-4 rounded-lg border bg-muted/20 p-4 sm:grid-cols-2">
              <div className="sm:col-span-2"><dt className="text-xs text-muted-foreground">Endpoint</dt><dd className="mt-1 break-all font-mono text-xs font-medium">{selected.details.endpoint}</dd></div>
              <div><dt className="text-xs text-muted-foreground">Authentication type</dt><dd className="mt-1 font-medium">{selected.details.authenticationType}</dd></div>
              <div><dt className="text-xs text-muted-foreground">Last sync</dt><dd className="mt-1 font-medium">{selected.lastSync}</dd></div>
              <div><dt className="text-xs text-muted-foreground">API latency</dt><dd className="mt-1 font-medium tabular-nums">{selected.details.apiLatency}</dd></div>
              <div><dt className="text-xs text-muted-foreground">Failed requests</dt><dd className="mt-1 font-medium tabular-nums">{selected.details.failedRequests}</dd></div>
            </dl>

            <div className={selected.details.schemaDriftDetected ? "rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200" : "rounded-lg border bg-muted/20 p-3 text-sm text-muted-foreground"}>
              <div className="flex items-start gap-2">
                {selected.details.schemaDriftDetected ? <TriangleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" /> : <CircleGauge className="mt-0.5 size-4 shrink-0" aria-hidden="true" />}
                <div><p className="font-medium">Schema drift {selected.details.schemaDriftDetected ? "detected" : "not detected"}</p><p className="mt-1 text-xs leading-5">{selected.details.schemaDriftDetected ? "The customer payload includes new fields that require mapping review." : "The current connector schema matches its approved mapping."}</p></div>
              </div>
            </div>

            {selected.id === "mockcorp-crm" ? (
              <div className="rounded-lg border border-primary/20 bg-primary/[0.03] p-3 text-sm">
                <p className="font-medium text-primary">MockCorp CRM diagnostic</p>
                <p className="mt-1 text-xs leading-5 text-muted-foreground">Elevated latency, {selected.details.failedRequests} failed requests, and schema drift are contributing to degraded connector health.</p>
              </div>
            ) : null}

            <DialogFooter showCloseButton>
              <Button type="button" variant="outline" disabled={selected.status === "Disconnected"}><RefreshCw data-icon="inline-start" aria-hidden="true" />Sync now</Button>
            </DialogFooter>
          </DialogContent>
        ) : null}
      </Dialog>
    </>
  );
}
