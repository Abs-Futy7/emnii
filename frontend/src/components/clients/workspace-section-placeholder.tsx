import type { LucideIcon } from "lucide-react";

import { EmptyState } from "@/components/layout/empty-state";

export function WorkspaceSectionPlaceholder({
  icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
}) {
  return (
    <EmptyState
      icon={icon}
      title={title}
      description={description}
      className="min-h-80"
    />
  );
}
