import type { MonitoringSnapshot } from "@/types/monitoring";

export const monitoringSnapshot: MonitoringSnapshot = {
  metrics: [
    { label: "API Requests", value: "1.24M", change: "+8.2%", trend: "up", description: "Last 24 hours" },
    { label: "P95 Latency", value: "284 ms", change: "-12 ms", trend: "down", description: "Across all services" },
    { label: "Error Rate", value: "0.42%", change: "+0.06%", trend: "up", description: "HTTP 4xx and 5xx" },
    { label: "AI Requests", value: "84.2K", change: "+14.7%", trend: "up", description: "Copilot and enrichment" },
    { label: "Failed Tool Calls", value: "127", change: "-18.6%", trend: "down", description: "Last 24 hours" },
    { label: "Ingestion Failures", value: "18", change: "+3", trend: "up", description: "Requires review" },
  ],
  apiRequests: [
    { time: "00:00", requests: 42100 }, { time: "04:00", requests: 38600 }, { time: "08:00", requests: 59200 },
    { time: "12:00", requests: 68400 }, { time: "16:00", requests: 73100 }, { time: "20:00", requests: 64800 }, { time: "24:00", requests: 70200 },
  ],
  latency: [
    { time: "00:00", p50: 86, p95: 242 }, { time: "04:00", p50: 79, p95: 228 }, { time: "08:00", p50: 94, p95: 271 },
    { time: "12:00", p50: 102, p95: 296 }, { time: "16:00", p50: 97, p95: 284 }, { time: "20:00", p50: 91, p95: 263 }, { time: "24:00", p50: 93, p95: 278 },
  ],
  toolCalls: [
    { time: "Mon", successful: 14620, failed: 112 }, { time: "Tue", successful: 15940, failed: 98 }, { time: "Wed", successful: 17180, failed: 142 },
    { time: "Thu", successful: 16840, failed: 121 }, { time: "Fri", successful: 18320, failed: 127 }, { time: "Sat", successful: 12980, failed: 74 }, { time: "Sun", successful: 13740, failed: 81 },
  ],
  aiUsage: [
    { time: "Mon", requests: 68200, tokens: 12.4 }, { time: "Tue", requests: 74100, tokens: 13.7 }, { time: "Wed", requests: 79600, tokens: 14.8 },
    { time: "Thu", requests: 77300, tokens: 14.1 }, { time: "Fri", requests: 84200, tokens: 15.6 }, { time: "Sat", requests: 58900, tokens: 10.9 }, { time: "Sun", requests: 62100, tokens: 11.5 },
  ],
  services: [
    { id: "api-gateway", name: "API Gateway", status: "Healthy", uptime: "99.99%", latency: "42 ms", errorRate: "0.08%", lastCheck: "20 sec ago" },
    { id: "postgresql", name: "PostgreSQL", status: "Healthy", uptime: "99.98%", latency: "18 ms", errorRate: "0.02%", lastCheck: "18 sec ago" },
    { id: "vector-db", name: "Vector DB", status: "Healthy", uptime: "99.95%", latency: "67 ms", errorRate: "0.11%", lastCheck: "24 sec ago" },
    { id: "local-llm", name: "Local LLM", status: "Degraded", uptime: "99.72%", latency: "1.8 s", errorRate: "1.24%", lastCheck: "15 sec ago" },
    { id: "document-worker", name: "Document Worker", status: "Healthy", uptime: "99.91%", latency: "312 ms", errorRate: "0.19%", lastCheck: "31 sec ago" },
    { id: "mockcorp-crm", name: "MockCorp CRM", status: "Degraded", uptime: "98.84%", latency: "846 ms", errorRate: "2.36%", lastCheck: "12 sec ago" },
  ],
};
