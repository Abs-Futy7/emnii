import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

type LoadingStateProps = React.ComponentProps<"div"> & {
  rows?: number;
  label?: string;
};

export function LoadingState({
  rows = 3,
  label = "Loading content",
  className,
  ...props
}: LoadingStateProps) {
  return (
    <div
      className={cn("space-y-4 rounded-xl border bg-card p-5", className)}
      aria-busy="true"
      aria-live="polite"
      {...props}
    >
      <span className="sr-only">{label}</span>
      <div className="space-y-2">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-4 w-64 max-w-full" />
      </div>
      <div className="space-y-3 pt-2">
        {Array.from({ length: rows }, (_, index) => (
          <Skeleton key={index} className="h-12 w-full" />
        ))}
      </div>
    </div>
  );
}
