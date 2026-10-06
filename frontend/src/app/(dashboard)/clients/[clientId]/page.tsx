import { notFound } from "next/navigation";
import { Database, FileText, PlugZap, Rows3 } from "lucide-react";

import {
  IngestionJobsPanel,
  IntegrationStatusPanel,
  LatestAiActivityPanel,
  RecentDocumentsPanel,
} from "@/components/clients/client-overview-panels";
import { OnboardingProgress } from "@/components/clients/onboarding-progress";
import { StatCard } from "@/components/dashboard/stat-card";
import { getClientWorkspace } from "@/data/mock-client-workspaces";
import { getClientById } from "@/data/mock-clients";
import { formatCompactNumber } from "@/lib/formatters";

export default async function ClientOverviewPage({
  params,
}: {
  params: Promise<{ clientId: string }>;
}) {
  const { clientId } = await params;
  const client = getClientById(clientId);
  const workspace = getClientWorkspace(clientId);

  if (!client || !workspace) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <section aria-labelledby="client-summary-heading">
        <h2 id="client-summary-heading" className="sr-only">Client summary</h2>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            title="Total Records"
            value={formatCompactNumber(client.records)}
            description="Across connected data sources"
            icon={Rows3}
          />
          <StatCard
            title="Documents Indexed"
            value={client.documents.toLocaleString("en-US")}
            description="Searchable knowledge documents"
            icon={FileText}
          />
          <StatCard
            title="Active Integrations"
            value={client.integrations.length}
            description="Connected production systems"
            icon={PlugZap}
          />
          <StatCard
            title="Data Quality Score"
            value={`${client.dataQualityScore}/100`}
            description="Latest validation assessment"
            icon={Database}
          />
        </div>
      </section>

      <OnboardingProgress steps={workspace.onboarding} />

      <div className="grid items-start gap-4 xl:grid-cols-2">
        <IngestionJobsPanel jobs={workspace.ingestionJobs} />
        <RecentDocumentsPanel documents={workspace.documents} />
        <IntegrationStatusPanel integrations={workspace.integrations} />
        <LatestAiActivityPanel activity={workspace.aiActivity} />
      </div>
    </div>
  );
}
