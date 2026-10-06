import { AlertTriangle } from "lucide-react";

import { cn } from "@/lib/utils";

export function ErrorState({
  title = "Something went wrong",
  description,
  action,
  className,
}: {
  title?: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      role="alert"
      className={cn(
        "flex min-h-64 flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50/50 px-6 py-12 text-center dark:border-red-900 dark:bg-red-950/20",
        className,
      )}
    >
      <span className="mb-4 flex size-10 items-center justify-center rounded-lg bg-red-500/10 text-red-600 dark:text-red-400">
        <AlertTriangle className="size-5" aria-hidden="true" />
      </span>
      <h2 className="font-semibold">{title}</h2>
      <p className="mt-1.5 max-w-md text-sm leading-6 text-muted-foreground">
        {description}
      </p>
      {action ? <div className="mt-5">{action}</div> : null}
    </section>
  );
}
