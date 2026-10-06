import { Inbox, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

type EmptyStateProps = React.ComponentProps<"section"> & {
  title: string;
  description?: string;
  icon?: LucideIcon;
  action?: React.ReactNode;
};

export function EmptyState({
  title,
  description,
  icon: Icon = Inbox,
  action,
  className,
  ...props
}: EmptyStateProps) {
  return (
    <section
      className={cn(
        "flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed bg-card px-6 py-12 text-center",
        className,
      )}
      {...props}
    >
      <div className="mb-4 flex size-10 items-center justify-center rounded-lg border bg-muted/60 text-muted-foreground">
        <Icon className="size-5" aria-hidden="true" />
      </div>
      <h2 className="text-base font-semibold tracking-tight">{title}</h2>
      {description ? (
        <p className="mt-1.5 max-w-md text-sm leading-6 text-muted-foreground">
          {description}
        </p>
      ) : null}
      {action ? <div className="mt-5">{action}</div> : null}
    </section>
  );
}
