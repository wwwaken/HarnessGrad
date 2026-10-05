import { cn } from "@/lib/utils";

/** The loading state's only building block. Never a spinner over empty content. */
function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} {...props} />;
}

export { Skeleton };
