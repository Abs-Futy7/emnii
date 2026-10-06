import { StatusBadge } from "@/components/dashboard/status-badge";
import type { ClientStatus } from "@/types/client";

const statusPresentation = {
  onboarding: { status: "pending", label: "Onboarding" },
  active: { status: "active", label: "Active" },
  "needs-attention": { status: "warning", label: "Needs Attention" },
  disabled: { status: "inactive", label: "Disabled" },
} as const;

export function ClientStatusBadge({ status }: { status: ClientStatus }) {
  const presentation = statusPresentation[status];

  return (
    <StatusBadge status={presentation.status} label={presentation.label} />
  );
}
