import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { explainPresence, presenceOf } from "@/logic/presence";
import { EM_DASH } from "@/lib/format";

/**
 * Renders a field in one of the three states `schema.py` distinguishes.
 *
 * This is a component rather than a formatter because the distinction is visual as well as
 * textual: an **absent** field is an em dash (the recording code path never set it — often
 * because the point predates the field), a **null** field says `null` (the platform looked
 * and found nothing), and a zero says `0`. Collapsing any two of them is the defect the
 * schema module's docstring is about.
 */
export function Value({
  value,
  absent = false,
  fieldName,
  className,
  nullClassName,
  absentClassName,
}: {
  value: string | number | null | undefined;
  /** Force the absent state for a value read out of a detached object. */
  absent?: boolean;
  /** The schema field name, used to look up the `ADDED_LATER` date. */
  fieldName?: string;
  className?: string;
  nullClassName?: string;
  absentClassName?: string;
}) {
  const presence = absent ? "absent" : value === undefined ? "absent" : value === null ? "null" : "present";
  const explanation = fieldName ? explainPresence(presence, fieldName) : null;
  if (presence === "present") return <span className={cn("tabular", className)}>{value}</span>;
  if (presence === "null") {
    return (
      <span
        className={cn("text-muted-foreground/80 italic", nullClassName)}
        title={explanation ?? "null — the platform looked and found nothing"}
      >
        null
      </span>
    );
  }
  return (
    <span
      className={cn("text-muted-foreground/60", absentClassName)}
      title={explanation ?? "absent — the recording code path did not set it"}
    >
      {EM_DASH}
    </span>
  );
}

/** The same three states, read straight off an object and a key. */
export function FieldValue({
  object,
  field,
  value,
  className,
}: {
  object: Record<string, unknown> | null | undefined;
  field: string;
  /** Override the value; when omitted, `object[field]` is read. */
  value?: string | number | null;
  className?: string;
}) {
  const presence = presenceOf(object, field);
  if (value !== undefined) {
    return <Value value={value} fieldName={field} className={className} />;
  }
  const raw = object ? (object[field] as string | number | null | undefined) : undefined;
  return <Value value={raw} absent={presence === "absent"} fieldName={field} className={className} />;
}

/** A labelled field cell for the identity panels. */
export function Field({
  label,
  children,
  hint,
  className,
}: {
  label: ReactNode;
  children: ReactNode;
  hint?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("min-w-0 space-y-0.5", className)}>
      <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div className="truncate text-xs">{children}</div>
      {hint ? <div className="text-2xs text-muted-foreground">{hint}</div> : null}
    </div>
  );
}
