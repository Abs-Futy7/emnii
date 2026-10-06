import type { LucideIcon } from "lucide-react";

import { EmptyState } from "@/components/layout/empty-state";
import { PageHeader } from "@/components/layout/page-header";

type DashboardPlaceholderProps = {
  title: string;
  description: string;
  icon: LucideIcon;
};

export function DashboardPlaceholder({
  title,
  description,
  icon,
}: DashboardPlaceholderProps) {
  return (
    <>
      <PageHeader title={title} description={description} />
      <EmptyState
        icon={icon}
        title={`${title} workspace`}
        description="This area is ready for the next phase of product development."
      />
    </>
  );
}
