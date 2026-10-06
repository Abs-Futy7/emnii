import Link from "next/link";
import { Building2 } from "lucide-react";

import { EmptyState } from "@/components/layout/empty-state";
import { Button } from "@/components/ui/button";

export default function ClientNotFound() {
  return (
    <EmptyState
      icon={Building2}
      title="Client not found"
      description="This workspace does not exist or is no longer available."
      action={
        <Button render={<Link href="/clients" />}>
          Return to clients
        </Button>
      }
      className="min-h-[60vh]"
    />
  );
}
