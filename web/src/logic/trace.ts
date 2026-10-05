import type { HarnessIdentity, JsonObject, JsonValue, TraceEvent } from "@/types";

/**
 * A task's trace, turned from JSONL into a timeline.
 *
 * The file is a sequence of heterogeneous events distinguished by their keys, not by a
 * `type` field: a model reply, a command and its output, an output-clip, a finish or repeat
 * nudge, a submit attempt, and — at the end — the wall clock and token usage. Rendering it as
 * raw JSONL is what the *old* UI did; `docs/refactor_references.md` §6.3 asks instead for "a
 * task's raw run next to its score", because the common failure is a score that is
 * arithmetically right and semantically wrong.
 *
 * One modelling decision matters: **order is preserved inside a step.** A model can emit
 * several tool calls in one step, so the trace reads `model → command → command → model →
 * …` all at the same `step` number. Grouping commands away from replies would destroy the
 * only narrative the file has, so a step holds an ordered item list rather than separate
 * buckets.
 *
 * Unknown event kinds are kept as `unknown` items instead of being dropped: a trace that
 * silently loses events is worse than one that shows an unfamiliar one.
 */

export type TimelineItem =
  | { kind: "model"; reply: string; modelMs: number | null }
  | { kind: "command"; command: string; exit: number | null; commandMs: number | null; output: string | null }
  | { kind: "clipped"; shown: JsonValue; original: JsonValue }
  | { kind: "nudge"; nudge: "finish" | "repeat"; value: JsonValue }
  | { kind: "submit"; event: "submitted" | "missing" | "rejected"; value: JsonValue }
  | { kind: "duplicate"; keys: JsonValue }
  | { kind: "unknown"; event: TraceEvent };

export interface TimelineStep {
  step: number;
  items: TimelineItem[];
  /** Total model latency for the step, summed over its replies. */
  modelMs: number;
  /** Total command latency for the step. */
  commandMs: number;
  /** Every command exit code in the step, in order. */
  exitCodes: number[];
  /** The step ended with a rejected submit or a missing artifact. */
  flagged: boolean;
}

export interface TraceTimeline {
  /** `harness_identity` — which harness and config produced this trace. */
  identity: HarnessIdentity | null;
  harnessConfig: JsonObject | null;
  preamble: TimelineItem[];
  steps: TimelineStep[];
  wallClockS: number | null;
  usage: JsonValue;
  /** Events that could not be placed (no `step` and not a known trailer). */
  unpaced: TraceEvent[];
  eventCount: number;
}

export function buildTimeline(events: TraceEvent[]): TraceTimeline {
  const steps: TimelineStep[] = [];
  const preamble: TimelineItem[] = [];
  const unpaced: TraceEvent[] = [];
  let identity: HarnessIdentity | null = null;
  let wallClockS: number | null = null;
  let usage: JsonValue = null;
  let current: TimelineStep | null = null;

  const push = (step: number | null, item: TimelineItem) => {
    if (step === null) {
      preamble.push(item);
      return;
    }
    if (!current || current.step !== step) {
      current = { step, items: [], modelMs: 0, commandMs: 0, exitCodes: [], flagged: false };
      steps.push(current);
    }
    current.items.push(item);
    if (item.kind === "model" && item.modelMs) current.modelMs += item.modelMs;
    if (item.kind === "command") {
      if (item.commandMs) current.commandMs += item.commandMs;
      if (typeof item.exit === "number") current.exitCodes.push(item.exit);
    }
    if (item.kind === "submit" && item.event !== "submitted") current.flagged = true;
  };

  for (const event of events) {
    const step =
      "step" in event && typeof (event as { step?: unknown }).step === "number"
        ? (event as { step: number }).step
        : null;
    if ("harness_identity" in event) {
      identity = (event as { harness_identity: HarnessIdentity }).harness_identity;
      continue;
    }
    if ("wall_clock_s" in event) {
      wallClockS = (event as { wall_clock_s: number }).wall_clock_s;
      continue;
    }
    if ("usage" in event && !("step" in event)) {
      usage = (event as { usage: JsonValue }).usage;
      continue;
    }
    if ("reply" in event) {
      const e = event as { reply: string; model_ms?: number };
      push(step, { kind: "model", reply: e.reply, modelMs: e.model_ms ?? null });
      continue;
    }
    if ("command" in event) {
      const e = event as { command: string; exit?: number; command_ms?: number; output?: string };
      push(step, {
        kind: "command",
        command: e.command,
        exit: typeof e.exit === "number" ? e.exit : null,
        commandMs: e.command_ms ?? null,
        output: e.output ?? null,
      });
      continue;
    }
    if ("output_clipped" in event) {
      const e = event as { output_clipped: JsonValue; shown: JsonValue };
      push(step, { kind: "clipped", original: e.output_clipped, shown: e.shown });
      continue;
    }
    if ("finish_nudge" in event) {
      push(step, { kind: "nudge", nudge: "finish", value: (event as { finish_nudge: JsonValue }).finish_nudge });
      continue;
    }
    if ("repeat_nudge" in event) {
      push(step, { kind: "nudge", nudge: "repeat", value: (event as { repeat_nudge: JsonValue }).repeat_nudge });
      continue;
    }
    if ("submitted" in event) {
      push(step, { kind: "submit", event: "submitted", value: (event as { submitted: JsonValue }).submitted });
      continue;
    }
    if ("missing" in event) {
      push(step, { kind: "submit", event: "missing", value: (event as { missing: JsonValue }).missing });
      continue;
    }
    if ("submit_rejected" in event) {
      push(step, { kind: "submit", event: "rejected", value: (event as { submit_rejected: JsonValue }).submit_rejected });
      continue;
    }
    if ("duplicate_keys" in event) {
      push(step, { kind: "duplicate", keys: (event as { duplicate_keys: JsonValue }).duplicate_keys });
      continue;
    }
    // An event this viewer does not know: kept where it belongs rather than dropped. A trace
    // that silently loses events is worse than one that shows an unfamiliar one.
    if (step === null) {
      unpaced.push(event);
    } else {
      push(step, { kind: "unknown", event });
    }
  }

  // `harness_identity` events can also appear with a step; only the config form matters.
  return {
    identity,
    harnessConfig: (identity?.config as JsonObject | undefined) ?? null,
    preamble,
    steps,
    wallClockS,
    usage,
    unpaced,
    eventCount: events.length,
  };
}

/** A one-line summary of the trace, for the task header. */
export function traceSummary(timeline: TraceTimeline): {
  steps: number;
  commands: number;
  failedCommands: number;
  nudges: number;
  modelMs: number;
  commandMs: number;
} {
  let commands = 0;
  let failedCommands = 0;
  let nudges = 0;
  let modelMs = 0;
  let commandMs = 0;
  for (const step of timeline.steps) {
    modelMs += step.modelMs;
    commandMs += step.commandMs;
    for (const item of step.items) {
      if (item.kind === "command") {
        commands += 1;
        if (item.exit !== null && item.exit !== 0) failedCommands += 1;
      }
      if (item.kind === "nudge") nudges += 1;
    }
  }
  return { steps: timeline.steps.length, commands, failedCommands, nudges, modelMs, commandMs };
}
