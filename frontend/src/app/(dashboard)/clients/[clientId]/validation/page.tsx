import { DataQualityReport } from "@/components/clients/data-quality-report";
import { dataQualityReport } from "@/data/mock-data-quality";

export default function ValidationPage() {
  return <DataQualityReport report={dataQualityReport} />;
}
