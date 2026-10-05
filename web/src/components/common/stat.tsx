import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export type StatTone = "neutral" | "pass" | "fail" | "warn" | "info";

const TONE_TEXT: Record<StatTone, string> = {
  neutral: "text-foreground",
  pass: "text-pass",
  fail: "text-fail",
  warn: "text-warn",
  info: "text-info",
};

/**
 * A single headline number with its explanation attached.
 *
 * Every tile carries its own caveat, because on this platform a number without one is the
 * failure mode: a `score` of 0.0 that is really "the harness never started", or a
 * `test_rate` that is absent because the point predates the field.
 */
export function Stat({
  label,
  value,
  hint,
  tone = "neutral",
  className,
}: {
  label: ReactNode;
  value: ReactNode;
  hint?: ReactNode;
  tone?: StatTone;
  className?: string;
}) {
  return (
    <div className={cn("rounded-lg border border-border bg-card px-3 py-2.5", className)}>
      <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div className={cn("mt-1 text-xl font-semibold tabular leading-none", TONE_TEXT[tone])}>
        {value}
      </div>
      {hint ? <div className="mt-1.5 text-2xs leading-snug text-muted-foreground">{hint}</div> : null}
    </div>
  );
}

/**
 * A compact signed-delta pill, used in the compare tables.
 *
 * Zero is rendered as `±0.000` in muted ink rather than as a green or red: "nothing moved"
 * is not an improvement, and colouring it would say it was.
 */
export function DeltaPill({
  value,
  digits = 3,
  className,
}: {
  value: number | null;
  digits?: number;
  className?: string;
}) {
  if (value === null) {
    return <span className={cn("text-muted-foreground", className)}>—</span>;
  }
  if (value === 0) {
    return <span className={cn("tabular text-muted-foreground", className)}>±0.000</span>;
  }
  return (
    <span
      className={cn(
        "tabular font-medium",
        value > 0 ? "text-pass" : "text-fail",
        className,
      )}
    >
      {value > 0 ? "+" : "−"}
      {Math.abs(value).toFixed(digits)}
    </span>
  );
}
