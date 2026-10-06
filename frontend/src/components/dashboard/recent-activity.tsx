import {
  AlertTriangle,
  CheckCircle2,
  DatabaseZap,
  FileCheck2,
  UploadCloud,
  type LucideIcon,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { ActivityKind, RecentActivity as RecentActivityItem } from "@/types/dashboard";

const activityPresentation: Record<
  ActivityKind,
  { icon: LucideIcon; className: string }
> = {
  upload: { icon: UploadCloud, className: "bg-blue-500/10 text-blue-600 dark:text-blue-400" },
  approval: { icon: CheckCircle2, className: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" },
  indexing: { icon: DatabaseZap, className: "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400" },
  failure: { icon: AlertTriangle, className: "bg-red-500/10 text-red-600 dark:text-red-400" },
  response: { icon: FileCheck2, className: "bg-violet-500/10 text-violet-600 dark:text-violet-400" },
};

export function RecentActivity({ activity }: { activity: RecentActivityItem[] }) {
  return (
    <Card>
      <CardHeader className="border-b">
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="px-0">
        <ol className="divide-y">
          {activity.map((item) => {
            const presentation = activityPresentation[item.kind];
            const Icon = presentation.icon;

            return (
              <li key={item.id} className="flex gap-3 px-4 py-3.5">
                <span className={cn("mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg", presentation.className)}>
                  <Icon className="size-4" aria-hidden="true" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-sm font-medium">{item.title}</p>
                    <time className="shrink-0 text-[11px] text-muted-foreground">{item.occurredAt}</time>
                  </div>
                  <p className="mt-0.5 text-xs leading-5 text-muted-foreground">{item.description}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}
