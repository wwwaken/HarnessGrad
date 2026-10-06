import { describe, expect, it } from "vitest";
import {
  badgeFor,
  levelCounts,
  matchesSearch,
  matchesValidity,
  quotableSummary,
} from "./certify";
import { certify } from "./test-support";
import type { RunSummary } from "@/types";

/**
 * The validation badge logic.
 *
 * `certify()`'s own docstring is the specification: `valid` = every point is readable and
 * measured by the platform; `certified` = additionally the record names its platform. A run
 * that predates the platform-hash field is `valid` and **not** `certified`, and that is the
 * honest reading rather than a defect. Two UI-level levels are layered on top — `tampered`
 * (which `certify()` keeps out of `problems`, so it would otherwise read as merely old) and
 * `no-points` (there is no number to be wrong about).
 */
describe("badgeFor", () => {
  it("marks a certified run as quotable with the strongest tone", () => {
    const badge = badgeFor(certify({ certified: true, platform_content_sha: "abc" }));
    expect(badge.level).toBe("certified");
    expect(badge.tone).toBe("pass");
    expect(badge.explanationKey).toBe("record.certify.certifiedWhy");
  });

  it("keeps valid-but-uncertified distinct, with the reason attached", () => {
    const badge = badgeFor(
      certify({
        valid: true,
        certified: false,
        notes: [
          "not certified: the record does not name the platform that produced it (`run_meta.platform.content_sha`)",
        ],
      }),
    );
    expect(badge.level).toBe("valid");
    expect(badge.tone).toBe("info");
    expect(badge.certificationNote).toContain("content_sha");
  });

  it("marks a run whose point is unreadable as invalid, carrying every problem", () => {
    const badge = badgeFor(
      certify({
        valid: false,
        problems: [
          "point 1: `measured_by_platform` is not true -- this number is a claim by the method, not a measurement by the platform",
        ],
      }),
    );
    expect(badge.level).toBe("invalid");
    expect(badge.tone).toBe("fail");
    expect(badge.problems).toHaveLength(1);
  });

  it("prefers tampered over valid, because certify() keeps it out of problems", () => {
    const badge = badgeFor(
      certify({
        valid: true,
        certified: false,
        tampered: ["eval/runner.py: hash changed"],
      }),
    );
    expect(badge.level).toBe("tampered");
    expect(badge.tone).toBe("fail");
  });

  it("renders a run with no points as not-measured, not as invalid", () => {
    const badge = badgeFor(certify({ points: 0, rounds: [], valid: false, final_score: null }));
    expect(badge.level).toBe("no-points");
    expect(badge.tone).toBe("muted");
    expect(badge.explanationKey).toBe("record.certify.notMeasuredWhy");
  });

  it("returns an unknown badge when no validation result exists", () => {
    expect(badgeFor(null).level).toBe("no-points");
    expect(badgeFor(undefined).labelKey).toBe("record.certify.unknown");
  });
});

function summary(runId: string, overrides: Partial<RunSummary> = {}): RunSummary {
  return {
    certify: certify(),
    run_id: runId,
    agent_model: "qwen3.5-9b-local",
    agent_backend: "openai",
    harness: "loop",
    dataset: "terminal_bench",
    improver: "deepseek",
    mode: "unified",
    side: "train",
    score_kind: "training",
    last_score: 0.1,
    last_test_rate: null,
    wall_clock_s: 100,
    timestamp_utc: "2026-10-05T12:00:00Z",
    meta_error: null,
    ...overrides,
  };
}

describe("filters and counts", () => {
  const rows = [
    summary("certified-1", { certify: certify({ certified: true }) }),
    summary("valid-1"),
    summary("invalid-1", {
      certify: certify({ valid: false, problems: ["point 0: no `score`"] }),
    }),
    summary("tampered-1", { certify: certify({ tampered: ["x: changed"] }) }),
    summary("empty-1", {
      certify: certify({ points: 0, rounds: [], valid: false, final_score: null }),
    }),
  ];

  it("counts each level", () => {
    const counts = levelCounts(rows.map((r) => badgeFor(r.certify)));
    expect(counts.certified).toBe(1);
    expect(counts.valid).toBe(1);
    expect(counts.invalid).toBe(1);
    expect(counts.tampered).toBe(1);
    expect(counts["no-points"]).toBe(1);
  });

  it("treats `quotable` as valid-or-certified — the question the screen exists for", () => {
    const quotable = rows.filter((r) => matchesValidity(badgeFor(r.certify), "quotable"));
    expect(quotable.map((r) => r.run_id).sort()).toEqual(["certified-1", "valid-1"]);
  });

  it("groups tampered with invalid under the invalid filter", () => {
    const invalid = rows.filter((r) => matchesValidity(badgeFor(r.certify), "invalid"));
    expect(invalid.map((r) => r.run_id).sort()).toEqual(["invalid-1", "tampered-1"]);
  });

  it("summarises quotable and certified separately", () => {
    const result = quotableSummary(rows);
    expect(result).toEqual({
      total: 5,
      certified: 1,
      valid: 1,
      quotable: 2,
      invalid: 2,
      noPoints: 1,
    });
  });

  it("searches across id, model, harness, dataset and improver", () => {
    expect(matchesSearch(rows[1], "valid-1")).toBe(true);
    expect(matchesSearch(rows[1], "qwen3")).toBe(true);
    expect(matchesSearch(rows[1], "terminal")).toBe(true);
    expect(matchesSearch(rows[1], "deepseek")).toBe(true);
    expect(matchesSearch(rows[1], "nothing-matches")).toBe(false);
    expect(matchesSearch(rows[1], "   ")).toBe(true);
  });
});
