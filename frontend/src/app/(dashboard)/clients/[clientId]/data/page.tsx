import { DataIngestionWorkspace } from "@/components/clients/data-ingestion-workspace";
import { ingestionHistory } from "@/data/mock-data-ingestion";

export default function ClientDataPage() {
  return <DataIngestionWorkspace initialHistory={ingestionHistory} />;
}
