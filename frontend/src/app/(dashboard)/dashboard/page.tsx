import {
  Bot,
  Building2,
  Clock3,
  Database,
  HeartPulse,
  TicketCheck,
  type LucideIcon,
} from "lucide-react";

import { RecentActivity } from "@/components/dashboard/recent-activity";
import { RecentClientsTable } from "@/components/dashboard/recent-clients-table";
import { StatCard } from "@/components/dashboard/stat-card";
import { SystemHealthPanel } from "@/components/dashboard/system-health-panel";
import { PageHeader } from "@/components/layout/page-header";
import { recentClients } from "@/data/mock-clients";
import {
  dashboardMetrics,
  recentActivity,
  systemHealth,
} from "@/data/mock-dashboard";
import type { MetricIcon } from "@/types/dashboard";

const metricIcons: Record<MetricIcon, LucideIcon> = {
  clients: Building2,
  tickets: TicketCheck,
  ai: Bot,
  "resolution-time": Clock3,
  "data-quality": Database,
  health: HeartPulse,
};

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Overview"
        description="A real-time view of customer support operations, AI performance, and platform health."
      />

      <section aria-labelledby="key-metrics-heading" className="section-stack">
        <h2 id="key-metrics-heading" className="sr-only">Key metrics</h2>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {dashboardMetrics.map((metric) => (
            <StatCard
              key={metric.id}
              title={metric.title}
              value={metric.value}
              description={metric.description}
              icon={metricIcons[metric.icon]}
              trend={metric.trend}
            />
          ))}
        </div>
      </section>

      <RecentClientsTable clients={recentClients} />

      <div className="grid items-start gap-4 xl:grid-cols-2">
        <SystemHealthPanel services={systemHealth} />
        <RecentActivity activity={recentActivity} />
      </div>
    </>
  );
}
