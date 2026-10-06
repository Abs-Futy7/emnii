import { notFound } from "next/navigation";

import { DocumentsWorkspace } from "@/components/clients/documents-workspace";
import { knowledgeDocuments } from "@/data/mock-documents";
import { getClientById } from "@/data/mock-clients";

export default async function DocumentsPage({
  params,
}: {
  params: Promise<{ clientId: string }>;
}) {
  const { clientId } = await params;
  const client = getClientById(clientId);

  if (!client) {
    notFound();
  }

  return (
    <DocumentsWorkspace
      clientId={clientId}
      company={client.company}
      initialDocuments={knowledgeDocuments}
    />
  );
}
