export type MetricIcon =
  | "clients"
  | "tickets"
  | "ai"
  | "resolution-time"
  | "data-quality"
  | "health";

export type DashboardMetric = {
  id: string;
  title: string;
  value: string;
  description: string;
  icon: MetricIcon;
  trend: {
    value: string;
    direction: "up" | "down" | "neutral";
    tone: "positive" | "negative" | "neutral";
    label: string;
  };
};

export type ServiceHealth = {
  name: string;
  status: "operational" | "degraded" | "outage";
  detail: string;
  uptime: string;
};

export type ActivityKind =
  | "upload"
  | "approval"
  | "indexing"
  | "failure"
  | "response";

export type RecentActivity = {
  id: string;
  kind: ActivityKind;
  title: string;
  description: string;
  occurredAt: string;
};
