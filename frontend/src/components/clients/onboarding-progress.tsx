import { AlertTriangle, Check, Clock3 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { OnboardingStep } from "@/types/client-workspace";

export function OnboardingProgress({ steps }: { steps: OnboardingStep[] }) {
  const completed = steps.filter((step) => step.status === "completed").length;
  const percentage = Math.round((completed / steps.length) * 100);

  return (
    <Card>
      <CardHeader className="border-b">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle>Onboarding Progress</CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">
              {completed} of {steps.length} steps completed
            </p>
          </div>
          <Badge variant="secondary" className="tabular-nums">{percentage}% complete</Badge>
        </div>
        <div
          className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted"
          role="progressbar"
          aria-label="Client onboarding progress"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={percentage}
        >
          <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${percentage}%` }} />
        </div>
      </CardHeader>
      <CardContent>
        <ol className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {steps.map((step, index) => {
            const Icon =
              step.status === "completed"
                ? Check
                : step.status === "warning"
                  ? AlertTriangle
                  : Clock3;

            return (
              <li key={step.id} className="flex gap-3 rounded-lg border bg-muted/20 p-3">
                <span
                  className={cn(
                    "flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
                    step.status === "completed" && "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
                    step.status === "warning" && "bg-amber-500/10 text-amber-600 dark:text-amber-400",
                    step.status === "pending" && "bg-muted text-muted-foreground",
                  )}
                >
                  {step.status === "pending" ? index + 1 : <Icon className="size-3.5" aria-hidden="true" />}
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-medium">{step.title}</p>
                  <p className="mt-0.5 text-xs leading-5 text-muted-foreground">{step.detail}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}
