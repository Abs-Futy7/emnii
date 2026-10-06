import { PlugZap } from "lucide-react";

import { WorkspaceSectionPlaceholder } from "@/components/clients/workspace-section-placeholder";

export default function ClientIntegrationsPage() {
  return (
    <WorkspaceSectionPlaceholder
      icon={PlugZap}
      title="Client integrations"
      description="Support platforms, communication channels, and data connectors will be managed here."
    />
  );
}
