import {
  AlertTriangle,
  CheckCircle2,
  CircleMinus,
  Clock3,
  XCircle,
  type LucideIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type Status =
  | "active"
  | "pending"
  | "warning"
  | "critical"
  | "inactive";

type StatusBadgeProps = Omit<React.ComponentProps<typeof Badge>, "children"> & {
  status: Status;
  label?: string;
};

const statusConfig: Record<
  Status,
  { label: string; icon: LucideIcon; className: string }
> = {
  active: {
    label: "Active",
    icon: CheckCircle2,
    className:
      "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300",
  },
  pending: {
    label: "Pending",
    icon: Clock3,
    className:
      "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-300",
  },
  warning: {
    label: "Needs attention",
    icon: AlertTriangle,
    className:
      "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300",
  },
  critical: {
    label: "Critical",
    icon: XCircle,
    className:
      "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300",
  },
  inactive: {
    label: "Inactive",
    icon: CircleMinus,
    className:
      "border-border bg-muted text-muted-foreground dark:bg-muted/60",
  },
};

export function StatusBadge({
  status,
  label,
  className,
  ...props
}: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge
      variant="outline"
      className={cn(config.className, className)}
      {...props}
    >
      <Icon data-icon="inline-start" aria-hidden="true" />
      {label ?? config.label}
    </Badge>
  );
}
