/**
 * Number and string formatting.
 *
 * One rule runs through all of it: **a missing number is never rendered as `0`.** Score
 * formatting returns an em dash for `null`/`undefined`, and the caller passes the reason
 * through separately (`logic/presence.ts`). `formatScore(0)` is the only way to render
 * `0.000`, and it is a real zero.
 */

export const EM_DASH = "—";

export function formatScore(value: number | null | undefined, digits = 3): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return EM_DASH;
  return value.toFixed(digits);
}

/** A signed delta, for "did this improve" columns. Zero is signed too, deliberately. */
export function formatDelta(value: number | null | undefined, digits = 3): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return EM_DASH;
  const sign = value > 0 ? "+" : value < 0 ? "−" : "±";
  return `${sign}${Math.abs(value).toFixed(digits)}`;
}

export function formatPercent(value: number | null | undefined, digits = 0): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return EM_DASH;
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatInt(value: number | null | undefined): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return EM_DASH;
  return new Intl.NumberFormat("en-US").format(value);
}

/** Compact token counts: a run's harness budget is often in the millions. */
export function formatTokens(value: number | null | undefined): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return EM_DASH;
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (Math.abs(value) >= 1_000) return `${(value / 1_000).toFixed(1)}k`;
  return String(value);
}

export function formatDuration(seconds: number | null | undefined): string {
  if (typeof seconds !== "number" || !Number.isFinite(seconds)) return EM_DASH;
  if (seconds < 60) return `${seconds.toFixed(0)}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ${Math.round(seconds % 60)}s`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

/** `2026-10-05T12:14:02Z` → `2026-10-05 12:14 UTC`, or the em dash. */
export function formatTimestamp(value: string | null | undefined): string {
  if (!value) return EM_DASH;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  const iso = parsed.toISOString();
  return `${iso.slice(0, 10)} ${iso.slice(11, 16)} UTC`;
}

export function shortSha(value: string | null | undefined, length = 8): string {
  if (!value) return EM_DASH;
  return value.slice(0, length);
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/** First line of a multi-line detail string, for a table cell. */
export function firstLine(value: string | null | undefined, max = 140): string {
  if (!value) return EM_DASH;
  const line = value.split("\n", 1)[0];
  return line.length > max ? `${line.slice(0, max - 1)}…` : line;
}
