import { cn } from "@/lib/utils";

type PageContainerProps = React.ComponentProps<"div">;

export function PageContainer({ className, ...props }: PageContainerProps) {
  return <div className={cn("page-container page-stack", className)} {...props} />;
}
