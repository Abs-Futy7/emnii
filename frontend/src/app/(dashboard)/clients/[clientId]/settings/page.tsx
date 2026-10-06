import { Settings } from "lucide-react";

import { WorkspaceSectionPlaceholder } from "@/components/clients/workspace-section-placeholder";

export default function ClientSettingsPage() {
  return (
    <WorkspaceSectionPlaceholder
      icon={Settings}
      title="Workspace settings"
      description="Regional defaults, access policies, and workspace preferences will be managed here."
    />
  );
}
