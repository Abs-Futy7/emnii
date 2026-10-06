import { BookOpen } from "lucide-react";

import { DashboardPlaceholder } from "@/components/dashboard/dashboard-placeholder";

export default function KnowledgeBasePage() {
  return (
    <DashboardPlaceholder
      title="Knowledge Base"
      description="Organize the trusted content used by support teams and AI workflows."
      icon={BookOpen}
    />
  );
}
