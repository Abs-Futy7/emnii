import { Activity } from "lucide-react";

import { StatusBadge, type Status } from "@/components/dashboard/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ServiceHealth } from "@/types/dashboard";

const statusMap: Record<ServiceHealth["status"], Status> = {
  operational: "active",
  degraded: "warning",
  outage: "critical",
};

export function SystemHealthPanel({ services }: { services: ServiceHealth[] }) {
  return (
    <Card>
      <CardHeader className="border-b">
        <div className="flex items-center gap-2">
          <Activity className="size-4 text-primary" aria-hidden="true" />
          <CardTitle>System Health</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="divide-y px-0">
        {services.map((service) => (
          <div key={service.name} className="flex items-center gap-3 px-4 py-3.5">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{service.name}</p>
              <p className="truncate text-xs text-muted-foreground">{service.detail}</p>
            </div>
            <div className="hidden text-right sm:block">
              <p className="text-xs font-medium tabular-nums">{service.uptime}</p>
              <p className="text-[11px] text-muted-foreground">30-day uptime</p>
            </div>
            <StatusBadge
              status={statusMap[service.status]}
              label={service.status === "operational" ? "Operational" : service.status === "degraded" ? "Degraded" : "Outage"}
            />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
