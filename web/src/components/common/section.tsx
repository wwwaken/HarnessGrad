import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/** A page or section title with its one-line purpose. */
export function PageHeader({
  title,
  description,
  actions,
  meta,
  className,
}: {
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  meta?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap items-start justify-between gap-3", className)}>
      <div className="min-w-0 space-y-1">
        <h1 className="truncate text-lg font-semibold tracking-tight">{title}</h1>
        {description ? (
          <p className="max-w-3xl text-xs leading-relaxed text-muted-foreground">{description}</p>
        ) : null}
        {meta ? <div className="flex flex-wrap items-center gap-2 pt-0.5">{meta}</div> : null}
      </div>
      {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
    </div>
  );
}

/** A card-shaped region with a header row, used to keep every panel's rhythm identical. */
export function Section({
  title,
  description,
  actions,
  children,
  className,
  contentClassName,
}: {
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
}) {
  return (
    <section className={cn("overflow-hidden rounded-lg border border-border bg-card", className)}>
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-border px-3 py-2">
        <div className="min-w-0">
          <h2 className="text-xs font-semibold tracking-tight">{title}</h2>
          {description ? (
            <p className="mt-0.5 max-w-3xl text-2xs leading-relaxed text-muted-foreground">
              {description}
            </p>
          ) : null}
        </div>
        {actions ? <div className="flex shrink-0 items-center gap-1.5">{actions}</div> : null}
      </header>
      <div className={cn("p-3", contentClassName)}>{children}</div>
    </section>
  );
}
