export type MonitoringMetric = { label: string; value: string; change: string; trend: "up" | "down" | "neutral"; description: string };
export type ApiRequestPoint = { time: string; requests: number };
export type LatencyPoint = { time: string; p50: number; p95: number };
export type ToolCallPoint = { time: string; successful: number; failed: number };
export type AIUsagePoint = { time: string; requests: number; tokens: number };
export type MonitoringServiceHealth = {
  id: string; name: string; status: "Healthy" | "Degraded" | "Down";
  uptime: string; latency: string; errorRate: string; lastCheck: string;
};
export type MonitoringSnapshot = {
  metrics: MonitoringMetric[]; apiRequests: ApiRequestPoint[]; latency: LatencyPoint[];
  toolCalls: ToolCallPoint[]; aiUsage: AIUsagePoint[]; services: MonitoringServiceHealth[];
};
