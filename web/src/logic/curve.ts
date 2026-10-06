import type { TranslationKey } from "@/i18n/en";
import type { CurvePoint } from "@/types";
import { presenceOf } from "./presence";

/**
 * The curve, as the Run detail screen draws it.
 *
 * Two series, because one cannot resolve the effect (see `docs/refactor_plan.md` stage 0):
 * measured on this platform, `large-scale-text-editing` passed 4 of 5 check tests for a
 * binary `score` of 0.0, and an edit took it to 3 of 5 — also 0.0. The score said nothing
 * happened; the artifact got worse. `test_rate` is the finer signal, and it only exists on
 * points recorded after 2026-10-05.
 *
 * The builder therefore keeps three states for `test_rate`:
 *
 * * `undefined` — the field is **absent**; the point predates stage 0. Render a gap, and
 *   say why. Never plot it as 0.
 * * `null` — the field is present and null: the checks in this round reported no per-test
 *   tally (`test_rate_of` returns `None`, not zero).
 * * a number.
 */
export interface CurvePointView {
  round: number;
  label: string | null;
  score: number | null;
  scoreLow: number | null;
  scoreHigh: number | null;
  testRate: number | null | undefined;
  testRateNTasks: number | null;
  testsPassed: number | null;
  testsTotal: number | null;
  passedCount: number | null;
  scoredCount: number;
  scoreKind: string;
  side: string;
  harnessSha: string | null;
  timestampUtc: string | null;
  /** The method's own word for the state it kept. `undefined` = field absent. */
  keptRound: number | null | undefined;
  isKept: boolean;
  /** Why the point cannot be read as a measurement. Empty = readable. */
  problems: string[];
}

/** How much of a series is actually measurable. A legend without this is a claim. */
export interface SeriesCoverageCaveat {
  key: TranslationKey;
  params: Record<string, string | number>;
  /** A record-shaped tail appended after an em dash, when the reason has a specific one. */
  extra: TranslationKey | null;
}

export interface SeriesCoverage {
  /** Rounds with a numeric value. */
  present: number;
  total: number;
  /** `null` when every round carries a number. */
  /**
   * Why the series is not complete — a key plus parameters, not a sentence. The date in
   * `coverageRecordedLate` is a fact about the platform's history and is deliberately left in
   * the string; the sentence around it is the app's own voice.
   */
  caveat: SeriesCoverageCaveat | null;
}

export interface CurveView {
  points: CurvePointView[];
  scoreCoverage: SeriesCoverage;
  testRateCoverage: SeriesCoverage;
  /** last − first, over the rounds that have a number. `null` when < 2 such rounds. */
  scoreLift: number | null;
  testRateLift: number | null;
  /** The round the method kept, if any point records `kept_round`. */
  keptRound: number | null;
  /** True when the score never moves but at least one `per_task` entry does. */
  scoreFlatButTasksMoved: boolean;
}

export function buildCurveView(points: CurvePoint[]): CurveView {
  const views = [...points]
    .sort((a, b) => a.round - b.round)
    .map(toPointView);

  const scores = views.map((v) => v.score).filter(isNumber);
  const rates = views.map((v) => v.testRate).filter(isNumber);

  return {
    points: views,
    scoreCoverage: coverage(scores.length, views.length, "score"),
    testRateCoverage: coverage(
      rates.length,
      views.length,
      "test_rate",
      views.some((v) => v.testRate === undefined)
        ? "run.chart.coverageRecordedLate"
        : "run.chart.coverageNoTally",
    ),
    scoreLift: lift(scores),
    testRateLift: lift(rates),
    keptRound: views.find((v) => v.isKept)?.round ?? null,
    scoreFlatButTasksMoved: detectFlatScoreTaskChurn(points),
  };
}

export function toPointView(point: CurvePoint): CurvePointView {
  const ci = Array.isArray(point.score_ci95) ? point.score_ci95 : null;
  const passed =
    isNumber(point.n_passed) ? point.n_passed : countPassed(point.per_task);
  const kept = presenceOf(point as unknown as Record<string, unknown>, "kept_round");
  return {
    round: point.round,
    label: point.label ?? null,
    score: isNumber(point.score) ? point.score : null,
    scoreLow: ci && isNumber(ci[0]) ? ci[0] : null,
    scoreHigh: ci && isNumber(ci[1]) ? ci[1] : null,
    testRate: point.test_rate === undefined ? undefined : isNumber(point.test_rate) ? point.test_rate : null,
    testRateNTasks: isNumber(point.test_rate_n_tasks) ? point.test_rate_n_tasks : null,
    testsPassed: isNumber(point.tests_passed) ? point.tests_passed : null,
    testsTotal: isNumber(point.tests_total) ? point.tests_total : null,
    passedCount: passed,
    scoredCount: point.n_scored,
    scoreKind: point.score_kind,
    side: point.side,
    harnessSha: point.identity?.harness_sha ?? null,
    timestampUtc: point.timestamp_utc ?? null,
    keptRound: kept === "present" ? (point.kept_round as number) : kept === "null" ? null : undefined,
    isKept: kept === "present" && point.kept_round === point.round,
    problems: pointProblems(point),
  };
}

/**
 * The per-point problems `schema.py:check_point` would report.
 *
 * Duplicated here on purpose: the Experiments screen must be able to explain *why* a run
 * is invalid by pointing at the point, without a second round trip. `logic/certify.ts`
 * holds the run-level reading.
 */
export function pointProblems(point: CurvePoint): string[] {
  const problems: string[] = [];
  if (point.measured_by_platform !== true) {
    problems.push(
      "`measured_by_platform` is not true — this number is a claim by the method, not a " +
        "measurement by the platform",
    );
  }
  if (!point.identity || !point.identity.harness_sha) {
    problems.push("`identity` names no `harness_sha` — which harness this score belongs to is not recorded");
  }
  if (point.startup_failure) {
    problems.push(`startup_failure — ${String(point.startup_failure).slice(0, 160)}`);
  }
  for (const [key, value] of Object.entries(point.tampered ?? {})) {
    if (Array.isArray(value) && value.length) {
      problems.push(`tampered: ${key}: ${value.join(", ")}`);
    }
  }
  return problems;
}

/** `score >= 1` is the platform's convention for a task that passed. */
export function countPassed(perTask: Record<string, number | null> | undefined): number | null {
  if (!perTask) return null;
  const values = Object.values(perTask).filter(isNumber);
  if (!values.length) return null;
  return values.filter((v) => v >= 1).length;
}

function coverage(
  present: number,
  total: number,
  series: string,
  extra?: TranslationKey,
): SeriesCoverage {
  if (present === total) return { present, total, caveat: null };
  return {
    present,
    total,
    caveat: {
      key: present === 0 ? "run.chart.coverageNone" : "run.chart.coverageSome",
      params: { series, present, total },
      extra: extra ?? null,
    },
  };
}

function lift(values: number[]): number | null {
  if (values.length < 2) return null;
  return values[values.length - 1] - values[0];
}

function isNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

/**
 * Does the *set* of passing tasks change while `score` does not?
 *
 * This is the run-level version of the Compare screen's headline. The platform's own
 * history is full of it (`runs/ds-dgm`: `score = 0.1` at rounds 0, 1 and 2, while the one
 * passing task goes `cobol-modernization` → `fix-git` → `fix-git`).
 */
export function detectFlatScoreTaskChurn(points: CurvePoint[]): boolean {
  const ordered = [...points].sort((a, b) => a.round - b.round);
  if (ordered.length < 2) return false;
  const scores = ordered.map((p) => p.score).filter(isNumber);
  if (scores.length < 2 || new Set(scores).size !== 1) return false;
  const sets = ordered.map((p) =>
    Object.entries(p.per_task ?? {})
      .filter(([, v]) => isNumber(v) && v >= 1)
      .map(([k]) => k)
      .sort()
      .join("|"),
  );
  return new Set(sets).size > 1;
}
