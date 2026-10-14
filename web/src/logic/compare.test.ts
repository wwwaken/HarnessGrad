import { describe, expect, it } from "vitest";
import { classifyMove, classifyScore, compareRuns, diffStatRows } from "./compare";
import { bundle, point as rawPoint } from "./test-support";
import type { RoundDiff } from "@/types";

// Existing task-movement fixtures explicitly model one matching runtime class.
const point = (overrides: Parameters<typeof rawPoint>[0]) =>
  rawPoint({ scorer_isolation_class: "snapshot-service", ...overrides });

/**
 * The task-flip diff — the core of the Compare screen.
 *
 * The case with the most weight is `maskedByScore`: the platform's own `runs/ds-dgm` keeps
 * `score = 0.1` at rounds 0, 1 and 2 while the passing task changes. If the diff only reported
 * the score delta it would say "no change" about a run that lost one capability and gained
 * another.
 */

const DS_DGM_R0 = point({
  round: 0,
  score: 0.1,
  test_rate: 0.48,
  per_task: { cobol: 1, fixgit: 0, gcode: 0 },
  per_task_test_rate: { cobol: 1, fixgit: 0.5, gcode: 0.4 },
  n_scored: 3,
});

const DS_DGM_R2 = point({
  round: 2,
  score: 0.1,
  test_rate: 0.55,
  per_task: { cobol: 0, fixgit: 1, gcode: 0 },
  per_task_test_rate: { cobol: 0.6, fixgit: 0.8, gcode: 0.4 },
  n_scored: 3,
});

describe("classifyScore / classifyMove", () => {
  it("treats 1 as a pass, 0 as a fail, and anything between as partial", () => {
    expect(classifyScore(1)).toBe("pass");
    expect(classifyScore(1.0)).toBe("pass");
    expect(classifyScore(0)).toBe("fail");
    expect(classifyScore(0.5)).toBe("partial");
    expect(classifyScore(null)).toBe("unmeasured");
    expect(classifyScore(undefined)).toBe("unmeasured");
    expect(classifyScore(Number.NaN)).toBe("unmeasured");
  });

  it("names the two directions that matter", () => {
    expect(classifyMove("fail", "pass")).toBe("gained");
    expect(classifyMove("pass", "fail")).toBe("lost");
    expect(classifyMove("pass", "pass")).toBe("still-pass");
    expect(classifyMove("fail", "fail")).toBe("still-fail");
    expect(classifyMove("pass", "unmeasured")).toBe("unmeasured");
  });
});

describe("compareRuns", () => {
  it("refuses comparison across scorer isolation classes and names the reason", () => {
    const left = bundle("offline", [point({ round: 0, score: 1,
      scorer_isolation_class: "pristine-offline", per_task: { a: 1 } })]);
    const right = bundle("snapshot", [point({ round: 0, score: 0,
      scorer_isolation_class: "snapshot-service", per_task: { a: 0 } })]);
    const result = compareRuns(left, right);
    expect(result.valid).toBe(false);
    expect(result.invalidReason).toBe("scorer isolation class mismatch: pristine-offline, snapshot-service");
    expect(result.summary.scoreDelta).toBeNull();
    expect(result.summary.testRateDelta).toBeNull();
    expect(result.tasks[0].move).toBe("unmeasured");
    expect(result.summary.headline).toContain("Comparison invalid");
  });

  it("refuses unknown legacy classes and internally mixed points", () => {
    const legacy = bundle("legacy", [point({ round: 0, scorer_isolation_class: undefined })]);
    expect(compareRuns(legacy, legacy).invalidReason).toContain("unknown");
    const mixed = bundle("mixed", [point({ round: 0, scorer_isolation_class: "pristine-offline",
      per_task_scorer_isolation: { a: "snapshot-service" } })]);
    expect(compareRuns(mixed, mixed).valid).toBe(false);
  });
  const left = bundle("ds-dgm", [
    point({ ...DS_DGM_R0, run_id: "ds-dgm" }),
    point({ ...DS_DGM_R2, run_id: "ds-dgm" }),
  ]);
  const right = bundle("ds-rrsi", [point({ ...DS_DGM_R2, run_id: "ds-rrsi", score: 0.1 })]);

  it("classifies each task into gained, lost and still-fail", () => {
    const comparison = compareRuns(left, right, { leftRound: 0, rightRound: 2 });
    const byTask = Object.fromEntries(comparison.tasks.map((t) => [t.taskId, t.move]));
    expect(byTask.cobol).toBe("lost");
    expect(byTask.fixgit).toBe("gained");
    expect(byTask.gcode).toBe("still-fail");
  });

  it("flags the flat-score / moved-task-set case in the summary and the headline", () => {
    const comparison = compareRuns(left, right, { leftRound: 0, rightRound: 2 });
    expect(comparison.summary.scoreDelta).toBe(0);
    expect(comparison.summary.gained).toBe(1);
    expect(comparison.summary.lost).toBe(1);
    expect(comparison.summary.maskedByScore).toBe(true);
    expect(comparison.summary.headline).toContain("hides the change");
  });

  it("does not flag masking when the score itself moved", () => {
    const worse = bundle("ds-rrsi", [point({ ...DS_DGM_R2, run_id: "ds-rrsi", score: 0.0, per_task: { cobol: 0, fixgit: 0, gcode: 0 } })]);
    const comparison = compareRuns(left, worse, { leftRound: 0, rightRound: 2 });
    expect(comparison.summary.scoreDelta).toBeCloseTo(-0.1);
    expect(comparison.summary.maskedByScore).toBe(false);
  });

  it("computes the per-task test_rate delta and leaves it null when a side has no tally", () => {
    const noTally = bundle("other", [
      point({ round: 0, score: 0.1, per_task: { cobol: 1, fixgit: 0, gcode: 0 }, per_task_test_rate: { cobol: 0.9 } }),
    ]);
    const comparison = compareRuns(left, noTally, { leftRound: 0, rightRound: 0 });
    const cobol = comparison.tasks.find((t) => t.taskId === "cobol");
    const fixgit = comparison.tasks.find((t) => t.taskId === "fixgit");
    expect(cobol?.testRateDelta).toBeCloseTo(-0.1);
    expect(fixgit?.testRateDelta).toBeNull();
  });

  it("keeps a task present on only one side as unmeasured, with its membership named", () => {
    const narrow = bundle("narrow", [
      point({ round: 0, score: 0.1, per_task: { cobol: 1 }, per_task_test_rate: { cobol: 1 } }),
    ]);
    const comparison = compareRuns(left, narrow, { leftRound: 0, rightRound: 0 });
    const fixgit = comparison.tasks.find((t) => t.taskId === "fixgit");
    expect(fixgit?.membership).toBe("left-only");
    expect(fixgit?.move).toBe("unmeasured");
    expect(fixgit?.rightScore).toBeNull();
  });

  it("defaults each side to its own last measured round", () => {
    const comparison = compareRuns(left, right);
    expect(comparison.leftRound).toBe(2);
    expect(comparison.rightRound).toBe(2);
  });

  it("reports an empty task list as unmeasured rather than as ten failures", () => {
    const empty = bundle("empty", [point({ round: 0, score: 0, per_task: {} })]);
    const comparison = compareRuns(empty, empty);
    expect(comparison.tasks).toEqual([]);
    expect(comparison.summary.gained).toBe(0);
    expect(comparison.summary.lost).toBe(0);
  });
});

describe("record field diff", () => {
  it("marks differing fields and renders a one-sided absence as null", () => {
    const left = bundle("a", [
      point({ round: 0, score: 0.1, identity: { harness_sha: "sha-1", agent_model: "m1" } }),
    ]);
    const right = bundle(
      "b",
      [point({ round: 0, score: 0.2, identity: { harness_sha: "sha-2", agent_model: "m2" } })],
      { meta: { ...bundle("b", []).meta, platform: {} } },
    );
    const comparison = compareRuns(left, right, { leftRound: 0, rightRound: 0 });
    const harness = comparison.fields.find((f) => f.path === "identity.harness_sha");
    const platform = comparison.fields.find((f) => f.path === "run_meta.platform.content_sha");
    expect(harness?.same).toBe(false);
    expect(harness?.left).toBe("sha-1");
    expect(harness?.right).toBe("sha-2");
    expect(platform?.right).toBeNull();
    expect(platform?.same).toBe(false);
  });

  it("calls identical fields equal", () => {
    const left = bundle("a", [point({ round: 0 })]);
    const right = bundle("a", [point({ round: 0 })]);
    const comparison = compareRuns(left, right, { leftRound: 0, rightRound: 0 });
    expect(comparison.fields.find((f) => f.path === "identity.harness_sha")?.same).toBe(true);
  });
});

describe("diffStatRows", () => {
  const diff: RoundDiff = {
    round: 1,
    from: "aaa",
    to: "bbb",
    files: [{ path: "agent.py", added: 161, removed: 34 }],
    added: 161,
    removed: 34,
    patch: "diff --git a/agent.py b/agent.py",
  };

  it("summarises a round's stat", () => {
    const result = diffStatRows(bundle("a", [], { diffs: { "1": diff } }), 1);
    expect(result.rows).toHaveLength(1);
    expect(result.added).toBe(161);
    expect(result.removed).toBe(34);
  });

  it("returns an empty stat for a round with no saved diff", () => {
    const result = diffStatRows(bundle("a", []), 1);
    expect(result.rows).toEqual([]);
    expect(result.from).toBeNull();
  });
});
