import type { CurvePoint, RunBundle, Verdict } from "@/types";
import type { TranslationKey } from "@/i18n/en";
import { toPointView, type CurvePointView } from "./curve";

/**
 * Comparing two runs is the most important thing this UI does, and the failure mode it
 * exists to prevent is specific: **the total score can stay flat while the set of passing
 * tasks changes.**
 *
 * `runs/ds-dgm` is the platform's own example. Its `score` is `0.1` at rounds 0, 1 and 2,
 * but the task that passes goes `cobol-modernization` → `fix-git` → `fix-git`. Read as a
 * single number, the run did nothing; read per task, one capability was lost and another
 * gained. `summarise` therefore reports `maskedByScore` beside the deltas, and the Compare
 * screen puts it above the chart.
 *
 * `per_task` values are the platform's task scores: `1.0` is a pass, `0.0` a fail, and a
 * value strictly between them is a partial (only reachable with `--trials > 1`). A task
 * missing from one side, or carrying a non-finite score, is `unmeasured` — never `0`.
 */

export type ScoreClass = "pass" | "fail" | "partial" | "unmeasured";

export type TaskMove =
  | "gained" // fail -> pass
  | "lost" // pass -> fail
  | "still-pass"
  | "still-fail"
  | "partial-moved"
  | "unchanged"
  | "unmeasured";

export interface TaskComparison {
  taskId: string;
  membership: "both" | "left-only" | "right-only";
  leftScore: number | null;
  rightScore: number | null;
  leftClass: ScoreClass;
  rightClass: ScoreClass;
  leftTestRate: number | null | undefined;
  rightTestRate: number | null | undefined;
  /** right − left, or `null` when either side has no tally. */
  testRateDelta: number | null;
  move: TaskMove;
  leftDetail: string | null;
  rightDetail: string | null;
}

export interface FieldDiff {
  /**
   * A translation key, not a label. Kept as a key so this module stays language-free and so
   * `FieldDiffTable` cannot forget to translate — the prop's type is the reminder.
   */
  labelKey: TranslationKey;
  path: string;
  left: string | null;
  right: string | null;
  same: boolean;
}

export interface ComparisonSummary {
  gained: number;
  lost: number;
  stillPass: number;
  stillFail: number;
  partialMoved: number;
  unmeasured: number;
  gainedTasks: string[];
  lostTasks: string[];
  scoreDelta: number | null;
  testRateDelta: number | null;
  /** score did not move, but the passing set did. The one-glance verdict. */
  maskedByScore: boolean;
  /** A sentence a reader can quote without opening anything. */
  headline: string;
}

export interface RunComparison {
  leftRunId: string;
  rightRunId: string;
  leftRound: number | null;
  rightRound: number | null;
  left: CurvePointView | null;
  right: CurvePointView | null;
  tasks: TaskComparison[];
  summary: ComparisonSummary;
  fields: FieldDiff[];
}

export interface CompareOptions {
  /** Default: each run's last measured round. */
  leftRound?: number;
  rightRound?: number;
  leftLabel?: string;
  rightLabel?: string;
}

export function selectPoint(bundle: RunBundle, round?: number): CurvePoint | null {
  const points = [...bundle.points].sort((a, b) => a.round - b.round);
  if (!points.length) return null;
  if (round === undefined) return points[points.length - 1];
  return points.find((p) => p.round === round) ?? null;
}

export function compareRuns(
  leftBundle: RunBundle,
  rightBundle: RunBundle,
  options: CompareOptions = {},
): RunComparison {
  const leftRaw = selectPoint(leftBundle, options.leftRound);
  const rightRaw = selectPoint(rightBundle, options.rightRound);
  const left = leftRaw ? toPointView(leftRaw) : null;
  const right = rightRaw ? toPointView(rightRaw) : null;

  const tasks = compareTasks(leftBundle, rightBundle, leftRaw, rightRaw);
  return {
    leftRunId: leftBundle.run_id,
    rightRunId: rightBundle.run_id,
    leftRound: leftRaw?.round ?? null,
    rightRound: rightRaw?.round ?? null,
    left,
    right,
    tasks,
    summary: summarise(tasks, left, right),
    fields: diffFields(leftBundle, rightBundle, leftRaw, rightRaw),
  };
}

export function classifyScore(score: number | null | undefined): ScoreClass {
  if (typeof score !== "number" || !Number.isFinite(score)) return "unmeasured";
  if (score >= 1) return "pass";
  if (score <= 0) return "fail";
  return "partial";
}

export function classifyMove(left: ScoreClass, right: ScoreClass): TaskMove {
  if (left === "unmeasured" || right === "unmeasured") return "unmeasured";
  if (left === "fail" && right === "pass") return "gained";
  if (left === "pass" && right === "fail") return "lost";
  if (left === "pass" && right === "pass") return "still-pass";
  if (left === "fail" && right === "fail") return "still-fail";
  if (left === "partial" || right === "partial") {
    return left === right ? "unchanged" : "partial-moved";
  }
  return "unchanged";
}

function compareTasks(
  leftBundle: RunBundle,
  rightBundle: RunBundle,
  leftPoint: CurvePoint | null,
  rightPoint: CurvePoint | null,
): TaskComparison[] {
  const leftTasks = leftPoint?.per_task ?? {};
  const rightTasks = rightPoint?.per_task ?? {};
  const leftRates = leftPoint?.per_task_test_rate ?? {};
  const rightRates = rightPoint?.per_task_test_rate ?? {};
  const ids = new Set<string>([
    ...Object.keys(leftTasks),
    ...Object.keys(rightTasks),
    ...Object.keys(leftRates),
    ...Object.keys(rightRates),
  ]);
  const leftVerdicts = leftPoint ? verdictsFor(leftBundle, leftPoint.round) : {};
  const rightVerdicts = rightPoint ? verdictsFor(rightBundle, rightPoint.round) : {};

  return [...ids].sort().map((taskId) => {
    const leftScore = finiteOrNull(leftTasks[taskId]);
    const rightScore = finiteOrNull(rightTasks[taskId]);
    const leftClass = classifyScore(leftScore);
    const rightClass = classifyScore(rightScore);
    const leftRate = finiteOrUndefined(leftRates[taskId]);
    const rightRate = finiteOrUndefined(rightRates[taskId]);
    const membership: TaskComparison["membership"] =
      taskId in leftTasks && taskId in rightTasks
        ? "both"
        : taskId in leftTasks
          ? "left-only"
          : "right-only";
    return {
      taskId,
      membership,
      leftScore,
      rightScore,
      leftClass,
      rightClass,
      leftTestRate: leftRate,
      rightTestRate: rightRate,
      testRateDelta:
        typeof leftRate === "number" && typeof rightRate === "number"
          ? rightRate - leftRate
          : null,
      move: membership === "both" ? classifyMove(leftClass, rightClass) : "unmeasured",
      leftDetail: leftVerdicts[taskId]?.detail ?? null,
      rightDetail: rightVerdicts[taskId]?.detail ?? null,
    };
  });
}

export function verdictsFor(
  bundle: RunBundle,
  round: number,
): Record<string, Verdict> {
  return bundle.verdicts[String(round)] ?? {};
}

export function summarise(
  tasks: TaskComparison[],
  left: CurvePointView | null,
  right: CurvePointView | null,
): ComparisonSummary {
  const gainedTasks = tasks.filter((t) => t.move === "gained").map((t) => t.taskId);
  const lostTasks = tasks.filter((t) => t.move === "lost").map((t) => t.taskId);
  const scoreDelta =
    typeof left?.score === "number" && typeof right?.score === "number"
      ? right.score - left.score
      : null;
  const testRateDelta =
    typeof left?.testRate === "number" && typeof right?.testRate === "number"
      ? right.testRate - left.testRate
      : null;
  const movedCount = gainedTasks.length + lostTasks.length;
  // "The score did not move" means exactly that: a delta of 0, not an unmeasurable one.
  const maskedByScore = scoreDelta === 0 && movedCount > 0;

  const summary: ComparisonSummary = {
    gained: gainedTasks.length,
    lost: lostTasks.length,
    stillPass: tasks.filter((t) => t.move === "still-pass").length,
    stillFail: tasks.filter((t) => t.move === "still-fail").length,
    partialMoved: tasks.filter((t) => t.move === "partial-moved").length,
    unmeasured: tasks.filter((t) => t.move === "unmeasured").length,
    gainedTasks,
    lostTasks,
    scoreDelta,
    testRateDelta,
    maskedByScore,
    headline: "",
  };
  summary.headline = headline(summary);
  return summary;
}

function headline(summary: ComparisonSummary): string {
  const delta = summary.scoreDelta;
  const deltaText =
    delta === null
      ? "score not comparable"
      : delta === 0
        ? "score unchanged"
        : `score ${delta > 0 ? "+" : ""}${delta.toFixed(3)}`;
  if (summary.maskedByScore) {
    return (
      `${deltaText}, but ${summary.gained + summary.lost} task(s) moved: ` +
      `${summary.gained} gained, ${summary.lost} lost. The score hides the change.`
    );
  }
  if (summary.gained === 0 && summary.lost === 0) {
    return `${deltaText}; the passing set did not move.`;
  }
  return `${deltaText}; ${summary.gained} task(s) gained, ${summary.lost} lost.`;
}

/**
 * The identity block, compared field by field.
 *
 * `docs/refactor_references.md` §6.3 asks for "not two metrics side by side — two records,
 * field by field, with the fields that differ and the fields that are absent on one side".
 * Absence is rendered as `null` here and the screen labels it, rather than being skipped:
 * a field that is absent on one side is itself a difference.
 */
export function diffFields(
  leftBundle: RunBundle,
  rightBundle: RunBundle,
  leftPoint: CurvePoint | null,
  rightPoint: CurvePoint | null,
): FieldDiff[] {
  // The label is a **translation key**, not a string: this module is pure and has no
  // language, so it names the field and the component that renders it decides how to say it.
  // A bare English string here would be the one place a reader saw an untranslated label.
  const rows: Array<[TranslationKey, string, string | null, string | null]> = [
    ["record.run", "run_id", leftBundle.run_id, rightBundle.run_id],
    ["record.round", "round", num(leftPoint?.round), num(rightPoint?.round)],
    ["record.score", "score", num(leftPoint?.score), num(rightPoint?.score)],
    [
      "record.testRate",
      "test_rate",
      numOrAbsent(leftPoint, "test_rate"),
      numOrAbsent(rightPoint, "test_rate"),
    ],
    ["record.scoreKind", "score_kind", str(leftPoint?.score_kind), str(rightPoint?.score_kind)],
    ["record.side", "side", str(leftPoint?.side), str(rightPoint?.side)],
    [
      "record.harnessSha",
      "identity.harness_sha",
      str(leftPoint?.identity?.harness_sha),
      str(rightPoint?.identity?.harness_sha),
    ],
    [
      "record.harnessVersion",
      "identity.harness_version",
      str(leftPoint?.identity?.harness_version),
      str(rightPoint?.identity?.harness_version),
    ],
    [
      "record.agentModel",
      "identity.agent_model",
      str(leftPoint?.identity?.agent_model),
      str(rightPoint?.identity?.agent_model),
    ],
    [
      "record.agentBackend",
      "identity.agent_backend",
      str(leftPoint?.identity?.agent_backend),
      str(rightPoint?.identity?.agent_backend),
    ],
    ["record.improver", "identity.improver", improver(leftPoint), improver(rightPoint)],
    ["record.method", "identity.method", str(leftPoint?.identity?.method), str(rightPoint?.identity?.method)],
    ["record.editKind", "edit_kind", str(leftPoint?.edit_kind), str(rightPoint?.edit_kind)],
    ["record.environment", "env.image_digest", str(leftPoint?.env?.image_digest), str(rightPoint?.env?.image_digest)],
    ["record.placement", "env.placement", str(leftPoint?.env?.placement), str(rightPoint?.env?.placement)],
    ["record.sampling", "sampling.policy", str(leftPoint?.sampling?.policy), str(rightPoint?.sampling?.policy)],
    ["record.tasksScored", "n_scored", num(leftPoint?.n_scored), num(rightPoint?.n_scored)],
    ["record.timestamp", "timestamp_utc", str(leftPoint?.timestamp_utc), str(rightPoint?.timestamp_utc)],
    ["record.platformSha", "run_meta.platform.content_sha", platformSha(leftBundle), platformSha(rightBundle)],
  ];
  return rows.map(([labelKey, path, l, r]) => ({
    labelKey,
    path,
    left: l,
    right: r,
    same: l === r,
  }));
}

/**
 * A run's round diff, as a stat row. The patch is rendered by Monaco on the screen; this
 * keeps the summary free of the file's tens of kilobytes.
 */
export interface DiffStatRow {
  path: string;
  added: number;
  removed: number;
}

export function diffStatRows(
  bundle: RunBundle,
  round: number | null,
): {
  rows: DiffStatRow[];
  added: number | null;
  removed: number | null;
  from: string | null;
  to: string | null;
} {
  if (round === null) return { rows: [], added: null, removed: null, from: null, to: null };
  const diff = bundle.diffs[String(round)];
  if (!diff) return { rows: [], added: null, removed: null, from: null, to: null };
  return {
    rows: diff.files ?? [],
    added: diff.added,
    removed: diff.removed,
    from: diff.from,
    to: diff.to,
  };
}

function finiteOrNull(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function finiteOrUndefined(value: unknown): number | null | undefined {
  if (value === undefined) return undefined;
  return finiteOrNull(value);
}

function num(value: unknown): string | null {
  return typeof value === "number" && Number.isFinite(value) ? String(value) : null;
}

function str(value: unknown): string | null {
  return typeof value === "string" && value.length ? value : null;
}

function numOrAbsent(point: CurvePoint | null, key: string): string | null {
  if (!point || !(key in point)) return null;
  const value = (point as unknown as Record<string, unknown>)[key];
  return value === null ? "null" : num(value);
}

function improver(point: CurvePoint | null): string | null {
  const value = point?.identity?.improver;
  if (!value || typeof value !== "object") return null;
  return value.model ? `${value.name ?? "?"} (${value.model})` : (value.name ?? null);
}

function platformSha(bundle: RunBundle): string | null {
  return bundle.meta?.platform?.content_sha ?? null;
}
