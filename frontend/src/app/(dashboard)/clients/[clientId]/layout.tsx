import { notFound } from "next/navigation";

import { ClientWorkspaceHeader } from "@/components/clients/client-workspace-header";
import { ClientWorkspaceNav } from "@/components/clients/client-workspace-nav";
import { clients, getClientById } from "@/data/mock-clients";

export function generateStaticParams() {
  return clients.map((client) => ({ clientId: client.id }));
}

export default async function ClientWorkspaceLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ clientId: string }>;
}) {
  const { clientId } = await params;
  const client = getClientById(clientId);

  if (!client) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <ClientWorkspaceHeader client={client} />
      <ClientWorkspaceNav clientId={client.id} />
      {children}
    </div>
  );
}
