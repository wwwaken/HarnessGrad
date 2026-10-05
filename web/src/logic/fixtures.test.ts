import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { buildCurveView, detectFlatScoreTaskChurn } from "./curve";
import { badgeFor } from "./certify";
import { compareRuns } from "./compare";
import { buildTimeline } from "./trace";
import type { RunBundle, RunSummary, TaskPage } from "@/types";

/**
 * The fixture contract, end to end.
 *
 * The unit tests above build their own records; this suite reads the **actual fixture files**
 * that the app fetches and runs the real logic over them. It is the test that fails when the
 * fixture generator drifts from `harnessgrad/store/schema.py`, which is the one failure mode
 * the fixture layer cannot catch on its own.
 *
 * Read from `process.cwd()` rather than `import.meta.url`: Vitest rewrites a literal
 * `new URL(..., import.meta.url)` as a build-time asset, which is exactly what the app wants
 * at runtime and exactly what a test must not depend on.
 */

const DATA = path.resolve(process.cwd(), "src/fixtures/data");

function load<T>(name: string): T {
  return JSON.parse(readFileSync(path.join(DATA, name), "utf8")) as T;
}

describe("runs-index.json", () => {
  const rows = load<RunSummary[]>("runs-index.json");

  it("carries all three badge outcomes the Experiments screen renders", () => {
    const levels = rows.map((row) => badgeFor(row.certify).level);
    expect(levels).toContain("certified");
    expect(levels).toContain("valid");
    expect(levels).toContain("invalid");
    expect(levels).toContain("no-points");
  });

  it("marks ds-dgm valid but not certified, matching certify() on the real directory", () => {
    const row = rows.find((r) => r.run_id === "ds-dgm");
    expect(row).toBeDefined();
    const badge = badgeFor(row!.certify);
    expect(badge.level).toBe("valid");
    expect(badge.certificationNote).toContain("content_sha");
    expect(row!.certify.final_score).toBeCloseTo(0.1);
  });

  it("keeps a run with no curve as not-measured rather than as a score of zero", () => {
    const row = rows.find((r) => r.run_id === "codex-task-dgm");
    expect(row?.certify.points).toBe(0);
    expect(badgeFor(row!.certify).level).toBe("no-points");
  });

  it("exposes the claimed-number run as invalid", () => {
    const row = rows.find((r) => r.run_id === "smoke-a");
    expect(badgeFor(row!.certify).level).toBe("invalid");
  });
});

describe("run-ds-dgm.json", () => {
  const bundle = load<RunBundle>("run-ds-dgm.json");

  it("has the three measured states and a saved diff for the rounds after 0", () => {
    expect(bundle.points.map((p) => p.round)).toEqual([0, 1, 2]);
    expect(Object.keys(bundle.diffs).sort()).toEqual(["1", "2"]);
  });

  it("shows the platform's own flat-score / moved-task-set case", () => {
    const view = buildCurveView(bundle.points);
    expect(view.points.map((p) => p.score)).toEqual([0.1, 0.1, 0.1]);
    expect(new Set(view.points.map((p) => p.passedCount)).size).toBe(1);
    expect(detectFlatScoreTaskChurn(bundle.points)).toBe(true);
    expect(view.scoreFlatButTasksMoved).toBe(true);
    // the passing task changes identity while the count stays at one
    const passing = bundle.points.map((p) =>
      Object.entries(p.per_task).filter(([, v]) => v === 1).map(([k]) => k).sort().join(","),
    );
    expect(passing[0]).not.toBe(passing[1]);
  });

  it("carries a measurable test_rate on every round, derived from the verdicts", () => {
    const view = buildCurveView(bundle.points);
    expect(view.testRateCoverage.present).toBe(bundle.points.length);
    expect(view.testRateCoverage.caveat).toBeNull();
    for (const p of view.points) {
      expect(typeof p.testRate).toBe("number");
    }
  });

  it("keeps the harness identity the points were recorded with", () => {
    expect(bundle.points[0].identity.harness_sha).toBe("9746711132c33f6020340d55082111431f9a04ef");
    expect(bundle.meta.harness).toBe("loop");
    expect(bundle.meta.dataset).toBe("terminal_bench");
  });
});

describe("comparing the two real fixture runs", () => {
  const left = load<RunBundle>("run-ds-dgm.json");
  const right = load<RunBundle>("run-ds-rrsi.json");

  it("finds the task that ds-rrsi lost without the score hiding it", () => {
    const comparison = compareRuns(left, right, { leftRound: 0, rightRound: 2 });
    expect(comparison.tasks.length).toBe(10);
    expect(comparison.summary.lostTasks).toContain("cobol-modernization");
    expect(comparison.summary.gained).toBe(0);
    expect(comparison.summary.scoreDelta).toBeCloseTo(-0.1);
  });

  it("reports the masked case when both runs are read at their own base and final state", () => {
    const comparison = compareRuns(left, left, { leftRound: 0, rightRound: 1 });
    expect(comparison.summary.scoreDelta).toBe(0);
    expect(comparison.summary.gainedTasks).toContain("fix-git");
    expect(comparison.summary.lostTasks).toContain("cobol-modernization");
    expect(comparison.summary.maskedByScore).toBe(true);
  });

  it("reads a per-task test_rate delta from the derived per-task tallies", () => {
    const comparison = compareRuns(left, right, { leftRound: 2, rightRound: 2 });
    const gcode = comparison.tasks.find((t) => t.taskId === "gcode-to-text");
    expect(gcode?.testRateDelta).not.toBeNull();
  });

  it("diffs the two records field by field and finds the harness sha", () => {
    const comparison = compareRuns(left, right, { leftRound: 2, rightRound: 2 });
    const sha = comparison.fields.find((f) => f.path === "identity.harness_sha");
    expect(sha?.same).toBe(false);
    expect(sha?.left).not.toBe(sha?.right);
  });
});

describe("task page fixtures", () => {
  const page = load<TaskPage>("task-ds-dgm-r0-cobol-modernization.json");

  it("carries the verdict on disk, with its tally recovered from the detail string", () => {
    expect(page.verdict?.task_id).toBe("cobol-modernization");
    expect(page.verdict?.passed).toBe(true);
    expect(page.verdict?.tests).toEqual({ passed: 3, failed: 0 });
  });

  it("parses the trace into a timeline with the harness identity at the top", () => {
    const timeline = buildTimeline(page.trace);
    expect(page.trace.length).toBeGreaterThan(50);
    expect(timeline.identity?.harness).toBe("loop");
    expect(timeline.steps.length).toBeGreaterThan(3);
    expect(timeline.wallClockS).not.toBeNull();
    expect(timeline.unpaced).toEqual([]);
  });
});
