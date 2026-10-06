import type {
  DashboardMetric,
  RecentActivity,
  ServiceHealth,
} from "@/types/dashboard";

export const dashboardMetrics: DashboardMetric[] = [
  {
    id: "active-clients",
    title: "Active Clients",
    value: "48",
    description: "Production workspaces",
    icon: "clients",
    trend: { value: "8.2%", direction: "up", tone: "positive", label: "vs. last month" },
  },
  {
    id: "open-tickets",
    title: "Open Tickets",
    value: "126",
    description: "Across all queues",
    icon: "tickets",
    trend: { value: "12.4%", direction: "down", tone: "positive", label: "vs. last week" },
  },
  {
    id: "ai-resolutions",
    title: "AI-Assisted Resolutions",
    value: "1,842",
    description: "72% of resolved tickets",
    icon: "ai",
    trend: { value: "18.6%", direction: "up", tone: "positive", label: "vs. last month" },
  },
  {
    id: "resolution-time",
    title: "Average Resolution Time",
    value: "3h 24m",
    description: "Median across channels",
    icon: "resolution-time",
    trend: { value: "9.1%", direction: "down", tone: "positive", label: "faster this month" },
  },
  {
    id: "data-quality",
    title: "Data Quality Score",
    value: "92.4",
    description: "Weighted workspace average",
    icon: "data-quality",
    trend: { value: "2.3 pts", direction: "up", tone: "positive", label: "since last review" },
  },
  {
    id: "system-health",
    title: "System Health",
    value: "99.98%",
    description: "30-day platform uptime",
    icon: "health",
    trend: { value: "Stable", direction: "neutral", tone: "neutral", label: "all core services online" },
  },
];

export const systemHealth: ServiceHealth[] = [
  { name: "API Gateway", status: "operational", detail: "84 ms response time", uptime: "99.99%" },
  { name: "PostgreSQL", status: "operational", detail: "18 ms query latency", uptime: "99.99%" },
  { name: "Vector Database", status: "operational", detail: "42 ms search latency", uptime: "99.97%" },
  { name: "Local LLM", status: "operational", detail: "1.2 s generation latency", uptime: "99.95%" },
  { name: "Document Processor", status: "degraded", detail: "Queue depth: 24 documents", uptime: "99.82%" },
];

export const recentActivity: RecentActivity[] = [
  { id: "act-1", kind: "upload", title: "Client dataset uploaded", description: "ShopNest uploaded 184,200 customer records.", occurredAt: "8 minutes ago" },
  { id: "act-2", kind: "approval", title: "Schema mapping approved", description: "TechMart's customer and order schema is ready for processing.", occurredAt: "27 minutes ago" },
  { id: "act-3", kind: "indexing", title: "Document indexing completed", description: "NovaRetail indexed 86 knowledge base documents.", occurredAt: "1 hour ago" },
  { id: "act-4", kind: "failure", title: "Integration failed", description: "Acme Commerce's Freshdesk sync requires attention.", occurredAt: "2 hours ago" },
  { id: "act-5", kind: "response", title: "Support response approved", description: "A billing escalation response was approved for ShopNest.", occurredAt: "3 hours ago" },
];
