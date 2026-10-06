import { Plus } from "lucide-react";
import Link from "next/link";

import { ClientsTable } from "@/components/clients/clients-table";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { clientIndustries, clients } from "@/data/mock-clients";

export default function ClientsPage() {
  return (
    <>
      <PageHeader
        title="Clients"
        description="Manage customer organizations and their AI support workspaces."
        actions={
          <Button render={<Link href="/clients/new" />}>
            <Plus data-icon="inline-start" aria-hidden="true" />
            Create Client
          </Button>
        }
      />
      <ClientsTable clients={clients} industries={clientIndustries} />
    </>
  );
}
