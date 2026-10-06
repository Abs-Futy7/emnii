import {
  ArrowDownRight,
  ArrowUpRight,
  Minus,
  type LucideIcon,
} from "lucide-react";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type StatTrend = {
  value: string;
  direction: "up" | "down" | "neutral";
  tone?: "positive" | "negative" | "neutral";
  label?: string;
};

type StatCardProps = React.ComponentProps<typeof Card> & {
  title: string;
  value: React.ReactNode;
  description?: string;
  icon?: LucideIcon;
  trend?: StatTrend;
};

const trendStyles = {
  positive: "text-emerald-600 dark:text-emerald-400",
  negative: "text-red-600 dark:text-red-400",
  neutral: "text-muted-foreground",
};

const trendIcons = {
  up: ArrowUpRight,
  down: ArrowDownRight,
  neutral: Minus,
};

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  className,
  ...props
}: StatCardProps) {
  const TrendIcon = trend ? trendIcons[trend.direction] : null;

  return (
    <Card className={cn("shadow-xs", className)} {...props}>
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        {Icon ? (
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Icon className="size-4" aria-hidden="true" />
          </div>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-2xl font-semibold tracking-tight tabular-nums">{value}</p>
        {description ? (
          <p className="text-xs text-muted-foreground">{description}</p>
        ) : null}
        {trend && TrendIcon ? (
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1 border-t pt-2 text-xs">
            <span
              className={cn(
                "inline-flex items-center gap-0.5 font-medium tabular-nums",
                trendStyles[
                  trend.tone ??
                    (trend.direction === "up"
                      ? "positive"
                      : trend.direction === "down"
                        ? "negative"
                        : "neutral")
                ],
              )}
            >
              <TrendIcon className="size-3.5" aria-hidden="true" />
              {trend.value}
              <span className="sr-only"> trend {trend.direction}</span>
            </span>
            {trend.label ? (
              <span className="text-muted-foreground">{trend.label}</span>
            ) : null}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
