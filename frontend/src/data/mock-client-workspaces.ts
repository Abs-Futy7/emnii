import { clients } from "@/data/mock-clients";
import type { ClientWorkspaceData, OnboardingStep } from "@/types/client-workspace";

const completedOnboarding: OnboardingStep[] = [
  { id: "created", title: "Client created", status: "completed", detail: "Workspace provisioned" },
  { id: "uploaded", title: "Data uploaded", status: "completed", detail: "Primary dataset received" },
  { id: "mapped", title: "Schema mapped", status: "completed", detail: "Fields mapped to canonical schema" },
  { id: "validated", title: "Validation complete", status: "completed", detail: "All blocking checks passed" },
  { id: "pii", title: "PII scan complete", status: "completed", detail: "Sensitive fields classified" },
  { id: "documents", title: "Documents indexed", status: "completed", detail: "Knowledge sources searchable" },
  { id: "ready", title: "AI workspace ready", status: "completed", detail: "Assistant enabled for production" },
];

const onboardingInProgress: OnboardingStep[] = completedOnboarding.map((step, index) => ({
  ...step,
  status: index < 2 ? "completed" : index === 2 ? "warning" : "pending",
  detail:
    index === 2
      ? "Three fields require review"
      : index > 2
        ? "Waiting for previous step"
        : step.detail,
}));

function createWorkspaceData(
  clientId: string,
  company: string,
  onboarding: OnboardingStep[],
): ClientWorkspaceData {
  return {
    clientId,
    onboarding,
    ingestionJobs: [
      { id: `${clientId}-job-1`, source: "Customer export", fileName: "customers_2026_10.csv", status: "completed", records: 184_200, startedAt: "Today, 09:42" },
      { id: `${clientId}-job-2`, source: "Support platform", fileName: "tickets_incremental.jsonl", status: "processing", records: 28_460, startedAt: "Today, 10:18" },
      { id: `${clientId}-job-3`, source: "Order warehouse", fileName: "orders_2026_09.parquet", status: "completed", records: 412_890, startedAt: "Yesterday, 16:05" },
    ],
    documents: [
      { id: `${clientId}-doc-1`, name: `${company} Support Playbook`, type: "PDF", status: "indexed", chunks: 184, updatedAt: "24 minutes ago" },
      { id: `${clientId}-doc-2`, name: "Returns and Refunds Policy", type: "DOCX", status: "indexed", chunks: 62, updatedAt: "2 hours ago" },
      { id: `${clientId}-doc-3`, name: "Product Catalog FAQ", type: "HTML", status: "processing", chunks: 128, updatedAt: "3 hours ago" },
    ],
    integrations: [
      { id: `${clientId}-int-1`, name: "Zendesk", status: "connected", lastSync: "8 minutes ago" },
      { id: `${clientId}-int-2`, name: "Slack", status: "connected", lastSync: "14 minutes ago" },
      { id: `${clientId}-int-3`, name: "Data Warehouse", status: "syncing", lastSync: "Sync in progress" },
    ],
    aiActivity: [
      { id: `${clientId}-ai-1`, summary: "Drafted a response for a delayed delivery escalation", channel: "Email", confidence: 94, occurredAt: "11 minutes ago" },
      { id: `${clientId}-ai-2`, summary: "Suggested three related knowledge articles", channel: "Chat", confidence: 91, occurredAt: "36 minutes ago" },
      { id: `${clientId}-ai-3`, summary: "Classified a billing request and routed it to Tier 2", channel: "Web", confidence: 97, occurredAt: "1 hour ago" },
    ],
  };
}

export const clientWorkspaces: Record<string, ClientWorkspaceData> = Object.fromEntries(
  clients.map((client) => [
    client.id,
    createWorkspaceData(
      client.id,
      client.company,
      client.status === "onboarding" || client.status === "needs-attention"
        ? onboardingInProgress
        : completedOnboarding,
    ),
  ]),
);

export function getClientWorkspace(clientId: string) {
  return clientWorkspaces[clientId];
}
