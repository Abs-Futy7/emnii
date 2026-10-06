import { IntegrationsGrid } from "@/components/integrations/integrations-grid";
import { PageHeader } from "@/components/layout/page-header";
import { integrations } from "@/data/mock-integrations";

export default function IntegrationsPage() {
  return (
    <>
      <PageHeader
        title="Integrations"
        description="Connect client systems, support tools, and custom APIs to the ResolveOps platform."
      />
      <IntegrationsGrid initialIntegrations={integrations} />
    </>
  );
}
