import { Settings } from "lucide-react";

import { DashboardPlaceholder } from "@/components/dashboard/dashboard-placeholder";

export default function SettingsPage() {
  return (
    <DashboardPlaceholder
      title="Settings"
      description="Configure workspace preferences and operational defaults."
      icon={Settings}
    />
  );
}
