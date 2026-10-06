import { SchemaMappingWorkspace } from "@/components/clients/schema-mapping-workspace";
import { canonicalFields, schemaMappings } from "@/data/mock-schema-mapping";

export default async function SchemaPage({
  params,
}: {
  params: Promise<{ clientId: string }>;
}) {
  const { clientId } = await params;

  return (
    <SchemaMappingWorkspace
      clientId={clientId}
      initialMappings={schemaMappings}
      fields={canonicalFields}
    />
  );
}
