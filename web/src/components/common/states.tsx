import type { ReactNode } from "react";
import { AlertTriangle, Inbox, RefreshCw, ServerCrash } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { ApiError } from "@/lib/api";

/**
 * Empty, error and loading states.
 *
 * These are not decoration. A comparison UI's most common failure is showing a number that
 * looks like a measurement when it is not, so the empty state names *why* there is nothing
 * to show and the error state names the layer that failed — "the fixtures carry two runs"
 * is a different fact from "the request failed".
 */

export function EmptyState({
  title,
  description,
  action,
  icon,
  className,
}: {
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  icon?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border px-6 py-10 text-center",
        className,
      )}
    >
      <div className="text-muted-foreground/70">{icon ?? <Inbox className="h-5 w-5" />}</div>
      <div className="text-sm font-medium">{title}</div>
      {description ? (
        <p className="max-w-md text-xs leading-relaxed text-muted-foreground">{description}</p>
      ) : null}
      {action ? <div className="pt-1">{action}</div> : null}
    </div>
  );
}

export function ErrorState({
  error,
  onRetry,
  className,
}: {
  error: unknown;
  onRetry?: () => void;
  className?: string;
}) {
  const api = error as Partial<ApiError> | undefined;
  const kind = api?.kind ?? "network";
  const title =
    kind === "not-found"
      ? "Not in the data this build carries"
      : kind === "parse"
        ? "The record could not be parsed"
        : "Could not load the data";
  return (
    <div
      className={cn(
        "flex flex-col items-start gap-2 rounded-lg border border-fail/35 bg-fail/5 px-4 py-3",
        className,
      )}
    >
      <div className="flex items-center gap-2 text-sm font-medium text-fail">
        {kind === "not-found" ? (
          <AlertTriangle className="h-4 w-4" />
        ) : (
          <ServerCrash className="h-4 w-4" />
        )}
        {title}
      </div>
      <p className="text-xs text-muted-foreground">
        {error instanceof Error ? error.message : String(error)}
      </p>
      {api?.hint ? (
        <p className="max-w-2xl text-2xs leading-relaxed text-muted-foreground">{api.hint}</p>
      ) : null}
      {onRetry ? (
        <Button variant="outline" size="xs" onClick={onRetry}>
          <RefreshCw className="h-3 w-3" />
          Retry
        </Button>
      ) : null}
    </div>
  );
}

/** A skeleton that keeps the real layout's height, so the page does not jump on load. */
export function TableSkeleton({ rows = 8, columns = 6 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-1.5">
      <div className="flex gap-2">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-6 flex-1" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex gap-2">
          {Array.from({ length: columns }).map((_, c) => (
            <Skeleton key={c} className="h-7 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("space-y-2", className)}>
      <Skeleton className="h-4 w-48" />
      <Skeleton className="h-[240px] w-full" />
      <div className="flex gap-3">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-3 w-24" />
      </div>
    </div>
  );
}

export function DetailSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      <Skeleton className="h-5 w-64" />
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14" />
        ))}
      </div>
      <Skeleton className="h-[220px] w-full" />
      <TableSkeleton rows={rows} columns={5} />
    </div>
  );
}
