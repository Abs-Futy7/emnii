import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { TicketPriority, TicketStatus } from "@/types/support-ticket";

const priorityStyles: Record<TicketPriority, string> = {
  Low: "border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300",
  Medium: "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-300",
  High: "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300",
  Urgent: "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300",
};
const statusStyles: Record<TicketStatus, string> = {
  Open: "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-300",
  "In Progress": "border-violet-200 bg-violet-50 text-violet-700 dark:border-violet-900 dark:bg-violet-950 dark:text-violet-300",
  Waiting: "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300",
  Resolved: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300",
};
export function TicketPriorityBadge({ priority }: { priority: TicketPriority }) { return <Badge variant="outline" className={cn(priorityStyles[priority])}>{priority}</Badge>; }
export function TicketStatusBadge({ status }: { status: TicketStatus }) { return <Badge variant="outline" className={cn(statusStyles[status])}>{status}</Badge>; }
