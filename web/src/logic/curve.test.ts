import { describe, expect, it } from "vitest";
import { buildCurveView, detectFlatScoreTaskChurn, pointProblems, toPointView } from "./curve";
import { point } from "./test-support";

/**
 * The score/test_rate series builder.
 *
 * The cases that matter are the three-state ones: a `test_rate` that is **absent** must not
 * become 0, a `test_rate` that is **null** must not become 0, and a real `0` must stay 0.
 */
describe("buildCurveView", () => {
  it("builds both series and sorts rounds ascending regardless of input order", () => {
    const view = buildCurveView([
      point({ round: 2, score: 0.3, test_rate: 0.5 }),
      point({ round: 0, score: 0.1, test_rate: 0.4 }),
      point({ round: 1, score: 0.2, test_rate: 0.45 }),
    ]);
    expect(view.points.map((p) => p.round)).toEqual([0, 1, 2]);
    expect(view.points.map((p) => p.score)).toEqual([0.1, 0.2, 0.3]);
    expect(view.points.map((p) => p.testRate)).toEqual([0.4, 0.45, 0.5]);
    expect(view.scoreLift).toBeCloseTo(0.2);
    expect(view.testRateLift).toBeCloseTo(0.1);
  });

  it("keeps absent, null and zero distinct for test_rate", () => {
    const view = buildCurveView([
      point({ round: 0 }), // field absent: predates stage 0
      point({ round: 1, test_rate: null }), // present and null: no tally reported
      point({ round: 2, test_rate: 0 }), // a real zero
    ]);
    expect(view.points[0].testRate).toBeUndefined();
    expect(view.points[1].testRate).toBeNull();
    expect(view.points[2].testRate).toBe(0);
    // only one round carries a number, so there is no lift to report — not a lift of zero
    expect(view.testRateLift).toBeNull();
    expect(view.testRateCoverage.present).toBe(1);
    expect(view.testRateCoverage.caveat).toContain("2026-10-05");
  });

  it("reports full coverage with no caveat when every round carries both numbers", () => {
    const view = buildCurveView([
      point({ round: 0, score: 0.1, test_rate: 0.4 }),
      point({ round: 1, score: 0.1, test_rate: 0.5 }),
    ]);
    expect(view.scoreCoverage).toEqual({ present: 2, total: 2, caveat: null });
    expect(view.testRateCoverage).toEqual({ present: 2, total: 2, caveat: null });
  });

  it("carries the 95% interval and a derived passing count", () => {
    const view = buildCurveView([
      point({
        round: 0,
        score: 0.1,
        score_ci95: [-0.096, 0.296],
        per_task: { a: 1, b: 0, c: 0 },
        n_scored: 3,
      }),
    ]);
    const only = view.points[0];
    expect(only.scoreLow).toBeCloseTo(-0.096);
    expect(only.scoreHigh).toBeCloseTo(0.296);
    expect(only.passedCount).toBe(1);
    expect(only.scoredCount).toBe(3);
  });

  it("marks the kept round", () => {
    const view = buildCurveView([
      point({ round: 0 }),
      point({ round: 1, kept_round: 1 }),
    ]);
    expect(view.keptRound).toBe(1);
    expect(view.points[1].isKept).toBe(true);
    expect(view.points[0].isKept).toBe(false);
  });

  it("has no lift from a single round, rather than a lift of zero", () => {
    const view = buildCurveView([point({ round: 0, score: 0.4 })]);
    expect(view.scoreLift).toBeNull();
    expect(view.testRateLift).toBeNull();
  });
});

describe("detectFlatScoreTaskChurn", () => {
  // modelled on runs/ds-dgm: score 0.1 at rounds 0, 1, 2 while the passing task changes
  const dsDgm = [
    point({ round: 0, score: 0.1, per_task: { cobol: 1, fixgit: 0 } }),
    point({ round: 1, score: 0.1, per_task: { cobol: 0, fixgit: 1 } }),
    point({ round: 2, score: 0.1, per_task: { cobol: 0, fixgit: 1 } }),
  ];

  it("is true when the score is flat and the passing set changes", () => {
    expect(detectFlatScoreTaskChurn(dsDgm)).toBe(true);
  });

  it("is false when the passing set is also constant", () => {
    const stable = [
      point({ round: 0, score: 0.5, per_task: { a: 1, b: 0 } }),
      point({ round: 1, score: 0.5, per_task: { a: 1, b: 0 } }),
    ];
    expect(detectFlatScoreTaskChurn(stable)).toBe(false);
  });

  it("is false when the score itself moved, because then nothing is masked", () => {
    const moved = [
      point({ round: 0, score: 0.1, per_task: { a: 1, b: 0 } }),
      point({ round: 1, score: 0.2, per_task: { a: 1, b: 1 } }),
    ];
    expect(detectFlatScoreTaskChurn(moved)).toBe(false);
  });

  it("is false with fewer than two points", () => {
    expect(detectFlatScoreTaskChurn([point({ round: 0, score: 0.1 })])).toBe(false);
  });
});

describe("pointProblems", () => {
  it("flags a number the method claimed rather than the platform measured", () => {
    const problems = pointProblems(point({ round: 0, measured_by_platform: false }));
    expect(problems.join(" ")).toContain("claim by the method");
  });

  it("flags an identity with no harness_sha", () => {
    const problems = pointProblems(point({ round: 0, identity: { harness_sha: "" } }));
    expect(problems.join(" ")).toContain("harness_sha");
  });

  it("flags a startup failure and a tamper record", () => {
    const problems = pointProblems(
      point({
        round: 0,
        startup_failure: "the harness never started",
        tampered: { "eval/runner.py": ["hash changed"] },
      }),
    );
    expect(problems.some((p) => p.includes("startup_failure"))).toBe(true);
    expect(problems.some((p) => p.includes("tampered: eval/runner.py"))).toBe(true);
  });

  it("is empty for a healthy point", () => {
    expect(pointProblems(point({ round: 0 }))).toEqual([]);
  });
});

describe("toPointView", () => {
  it("reads a null score as null rather than as absent", () => {
    const view = toPointView(point({ round: 0, score: null }));
    expect(view.score).toBeNull();
  });
});
