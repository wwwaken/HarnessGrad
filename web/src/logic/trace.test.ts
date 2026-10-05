import { describe, expect, it } from "vitest";
import { buildTimeline, traceSummary } from "./trace";
import type { TraceEvent } from "@/types";

/**
 * The trace timeline builder.
 *
 * The property that must hold is **order inside a step**: the base harness can emit several
 * tool calls in one step, so the file reads `model → command → output_clip → model → …` at the
 * same `step` number. Bucketing commands away from replies would destroy the only narrative
 * the trace has, so the builder keeps an ordered item list.
 */
const events: TraceEvent[] = [
  {
    harness_identity: {
      harness: "loop",
      config: { max_steps: 32, output_limit: 4000 },
      agent_model: "qwen3.5-9b-local",
    },
  },
  { step: 0, reply: "first reply", model_ms: 100 },
  { step: 0, command: "cat a.cbl", exit: 0, command_ms: 3, output: "IDENTIFICATION DIVISION" },
  { step: 0, reply: "second reply", model_ms: 200 },
  { step: 0, command: "cat b.dat", exit: 1, command_ms: 5, output: "not found" },
  { step: 0, output_clipped: 120000, shown: 4000 },
  { step: 1, reply: "done", model_ms: 50 },
  { step: 1, finish_nudge: "you have not submitted" },
  { step: 1, missing: ["answer.txt"] },
  { step: 2, submit_rejected: "too few steps" },
  { step: 2, duplicate_keys: ["a", "a"] },
  { wall_clock_s: 209.9 },
  { usage: { prompt_tokens: 1000, completion_tokens: 200 } },
];

describe("buildTimeline", () => {
  const timeline = buildTimeline(events);

  it("extracts the harness identity and its config", () => {
    expect(timeline.identity?.harness).toBe("loop");
    expect(timeline.harnessConfig).toEqual({ max_steps: 32, output_limit: 4000 });
  });

  it("groups events by step, preserving their order", () => {
    expect(timeline.steps.map((s) => s.step)).toEqual([0, 1, 2]);
    expect(timeline.steps[0].items.map((i) => i.kind)).toEqual([
      "model",
      "command",
      "model",
      "command",
      "clipped",
    ]);
  });

  it("sums latency and keeps every exit code per step", () => {
    expect(timeline.steps[0].modelMs).toBe(300);
    expect(timeline.steps[0].commandMs).toBe(8);
    expect(timeline.steps[0].exitCodes).toEqual([0, 1]);
  });

  it("reads the trailer events that carry no step", () => {
    expect(timeline.wallClockS).toBe(209.9);
    expect(timeline.usage).toEqual({ prompt_tokens: 1000, completion_tokens: 200 });
    expect(timeline.preamble).toEqual([]);
  });

  it("counts the raw events it was given", () => {
    expect(timeline.eventCount).toBe(events.length);
  });

  it("has no unknown or unpaced items for a fully understood trace", () => {
    const kinds = timeline.steps.flatMap((s) => s.items.map((i) => i.kind));
    expect(kinds).not.toContain("unknown");
    expect(timeline.unpaced).toEqual([]);
  });

  it("keeps an unrecognised event instead of dropping it", () => {
    const withUnknown: TraceEvent[] = [
      { step: 0, reply: "hi", model_ms: 1 },
      { step: 0, something_new: "value" } as unknown as TraceEvent,
      { no_step_field: true } as unknown as TraceEvent,
    ];
    const result = buildTimeline(withUnknown);
    const kinds = result.steps[0].items.map((i) => i.kind);
    expect(kinds).toContain("unknown");
    expect(result.unpaced).toHaveLength(1);
  });

  it("is empty, not broken, for an empty trace", () => {
    const result = buildTimeline([]);
    expect(result.steps).toEqual([]);
    expect(result.identity).toBeNull();
    expect(result.eventCount).toBe(0);
  });
});

describe("traceSummary", () => {
  it("counts commands, failures, nudges and total latency", () => {
    const summary = traceSummary(buildTimeline(events));
    expect(summary.steps).toBe(3);
    expect(summary.commands).toBe(2);
    expect(summary.failedCommands).toBe(1);
    expect(summary.nudges).toBe(1);
    expect(summary.modelMs).toBe(350);
    expect(summary.commandMs).toBe(8);
  });
});
