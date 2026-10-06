import { cn } from "@/lib/utils";

export function DataQualityScore({
  score,
  compact = false,
}: {
  score: number;
  compact?: boolean;
}) {
  const tone =
    score >= 90
      ? "bg-emerald-500"
      : score >= 80
        ? "bg-amber-500"
        : "bg-red-500";

  return (
    <div className={cn("flex items-center gap-2", compact ? "min-w-24" : "min-w-32")}>
      <div
        className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted"
        role="progressbar"
        aria-label={`Data quality score: ${score} out of 100`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={score}
      >
        <div className={cn("h-full rounded-full", tone)} style={{ width: `${score}%` }} />
      </div>
      <span className="w-8 text-right text-sm font-medium tabular-nums">{score}</span>
    </div>
  );
}
