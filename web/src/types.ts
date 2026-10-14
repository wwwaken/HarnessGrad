/**
 * The record schema, mirrored from `harnessgrad/store/schema.py`.
 *
 * `schema.py` is the authority. This file is a hand-written TypeScript projection of it,
 * written against the real data in `runs/` (read-only) and the shape `certify()` returns.
 * Two rules from the Python module are carried over literally, because a UI that loses
 * them launders refusals into zeros:
 *
 *   1. **absent, null and zero are three different facts.** A required field may be
 *      explicitly `null` ("the platform looked and found nothing"); a field in
 *      `ADDED_LATER` may be *absent* ("this point predates the field"). Neither is `0`.
 *   2. **`measured_by_platform: false` means the number is a claim, not a measurement.**
 *
 * ## What is inferred, and why
 *
 * The read API does not exist yet (stage 5's next task). Therefore:
 *
 * * Every field in `CURVE_POINT` / `ADDED_LATER` / `RUN_META` is taken directly from
 *   `schema.py` and is **certain**.
 * * Fields observed in `runs/<id>/curve.jsonl` but *not* declared in `schema.py`
 *   (`score_ci95`, `n_passed`, `method_hypothesis`, `editable_surface_touched`, …) are
 *   typed as **optional** and marked `observed`. `schema.py` deliberately declares only
 *   the fields a reader cannot do without; the rest are reports, and a report is allowed
 *   to be absent.
 * * The *endpoint envelopes* (`RunSummary`, `RunBundle`, `TaskPage`) are **inferred**:
 *   they are the minimum a read API must return for the five screens to work. They are
 *   documented in `web/README.md` under "API contract".
 */

// ---------------------------------------------------------------------------
// JSON primitives
// ---------------------------------------------------------------------------

export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type JsonObject = { [key: string]: JsonValue };

// ---------------------------------------------------------------------------
// Presence
// ---------------------------------------------------------------------------

/**
 * The three-state read of a field. `schema.py` makes this distinction load-bearing, so
 * the UI never collapses it: `absent` renders as "—" with an explanation, `null` as
 * "null (looked, found nothing)", `present` as the value.
 */
export type Presence = "present" | "null" | "absent";

// ---------------------------------------------------------------------------
// Curve point
// ---------------------------------------------------------------------------

/** `identity` — what ran. Required; the point cannot be compared without it. */
export interface Identity {
  harness_name?: string;
  harness_version?: string;
  /** Required by `check_point`: a point with no `harness_sha` is a problem. */
  harness_sha: string;
  improve_entrypoint?: string | null;
  accept_entrypoint?: string | null;
  run_mode?: string;
  framework_version?: string;
  agent_model?: string;
  agent_backend?: string;
  agent_model_source?: string;
  method_model?: string;
  method?: string;
  improver?: Improver;
  skill_sha?: string;
  harness_identity?: HarnessIdentity;
  harness_config?: JsonObject;
  /** `observed`, not declared in schema.py: the two-model conflict record. */
  [key: string]: JsonValue | Improver | HarnessIdentity | JsonObject | undefined;
}

export interface Improver {
  name?: string;
  kind?: string;
  base_url?: string;
  version?: string;
  sha256?: string;
  model?: string;
  requested?: string;
  /** `true` when the run's declaration and the platform's environment disagreed. */
  modified?: boolean;
  path?: string;
  [key: string]: JsonValue | undefined;
}

export interface HarnessIdentity {
  harness?: string;
  config?: JsonObject;
  agent_model?: string;
  agent_backend?: string;
  [key: string]: JsonValue | JsonObject | undefined;
}

/** `env` — the environment the measurement was taken in. Two envs, two quantities. */
export interface EnvRecord {
  kind?: string;
  /** The pinned digest. A run that cannot resolve one refuses to start. */
  image_digest?: string | null;
  network?: string | null;
  placement?: string | null;
  services?: JsonValue[];
  model?: string | null;
  seed?: JsonValue;
  model_gateway?: JsonObject | null;
  harness_runtime?: JsonValue[];
  variants?: JsonValue[];
  [key: string]: JsonValue | JsonObject | undefined | null;
}

export interface Sampling {
  policy?: string;
  task_ids?: string[];
  selection_basis_round?: number;
  selected_within?: string;
  [key: string]: JsonValue | undefined;
}

/** `cost` — three budgets that are never summed (see `records.py:_cost_of`). */
export interface CostRecord {
  evaluation_trials?: number | null;
  generation_tokens?: number | null;
  method_generation_tokens?: number | null;
  method_generation_input?: number | null;
  method_generation_output?: number | null;
  method_model_calls?: number | null;
  method_model?: string | null;
  harness_tokens?: number | null;
  harness_tokens_reported_by_tasks?: number | null;
  harness_model_calls?: number | null;
  env_generation_tokens?: number | null;
  env_services_reported?: number | null;
  wall_clock_s?: number | null;
  [key: string]: JsonValue | undefined;
}

export interface Cumulative {
  evaluation_trials?: number | null;
  generation_tokens?: number | null;
  env_generation_tokens?: number | null;
  wall_clock_s?: number | null;
  [key: string]: JsonValue | undefined;
}

/**
 * One measured state of a run.
 *
 * Required fields are exactly `schema.py:CURVE_POINT` (minus the ones the UI re-reads
 * through `RunMeta`). Optional fields include every `ADDED_LATER` entry — each optional
 * field's comment says when it was added, because its absence is a *note*, not a defect.
 */
export interface CurvePoint {
  scorer_isolation_class?: string;
  per_task_scorer_isolation?: Record<string, string>;
  // ---- required by schema.py ----
  run_id: string;
  round: number;
  identity: Identity;
  score: number | null;
  /** `training` or `exam`. A training score must never be quoted as a result. */
  score_kind: string;
  /** Which half of the split this point measured. */
  side: string;
  per_task: Record<string, number | null>;
  /** `score` is the mean over these. */
  n_scored: number;
  env: EnvRecord;
  sampling: Sampling;
  cost: CostRecord;
  timestamp_utc: string;
  /** `false`/absent means the number is a claim by the method, not a measurement. */
  measured_by_platform: boolean;

  // ---- optional in schema.py: present only when it applies ----
  method_reported?: JsonObject;
  edit_kind?: string | null;
  /** Per task, why the *harness* failed. Distinct from `invalid`. */
  harness_failed?: Record<string, string> | null;
  /** Per task, why the task could not be measured. Distinct from `harness_failed`. */
  invalid?: Record<string, string> | null;

  // ---- ADDED_LATER: absence is a note, never a problem ----
  /** 2026-10-05 (stage 0): the check's own test tally, as a number. */
  test_rate?: number | null;
  /** 2026-10-05 (stage 0): how many tasks reported a tally. */
  test_rate_n_tasks?: number | null;
  /** 2026-10-05 (stage 0). */
  per_task_test_rate?: Record<string, number | null>;
  /** 2026-10-05 (stage 0). */
  tests_passed?: number | null;
  /** 2026-10-05 (stage 0). */
  tests_total?: number | null;
  /** 2026-10-05: every changed file is outside the entrypoint's import closure. */
  no_loadable_change?: boolean | null;
  /** 2026-10-05: the harness never started on any task. */
  startup_failure?: string | null;
  /** 2026-10-04 (`--trials > 1`). */
  per_task_trials?: Record<string, number[]> | null;
  /** 2026-10-04 (`--trials > 1`). */
  score_std?: number | null;
  /** 2026-10-04 (`--trials > 1`). */
  n_trials?: number | null;
  /** 2026-10-05: which state the method decided to keep. */
  kept_round?: number | null;
  /** 2026-10-05: which step of its submission this point is. */
  step_index?: number | null;
  /** 2026-10-05: how many states one call bought. */
  steps_in_submission?: number | null;

  // ---- observed in runs/ but not declared in schema.py: typed, optional ----
  /** `observed`: the Wilson/normal interval the platform wrote beside `score`. */
  score_ci95?: [number, number] | null;
  /** `observed`. */
  n_passed?: number | null;
  /** `observed`. */
  n_invalid?: number | null;
  /** `observed`. */
  n_harness_failed?: number | null;
  /** `observed`: the label the run wrote for this state. */
  label?: string | null;
  /** `observed`: the method's own sentence about what it changed. */
  method_hypothesis?: string | null;
  /** `observed`: read from `git diff`, never from the method's word. */
  edits_applied?: string[] | null;
  /** `observed`. */
  editable_surface_touched?: string[] | null;
  /** `observed`: what the method *claimed* to edit. */
  files_claimed?: string[] | null;
  /** `observed`. */
  candidate_problems?: string[] | null;
  /** `observed`: per-step geometric mean, when the method made several edits. */
  score_geomean?: number | null;
  /** `observed`. */
  kept_score?: number | null;
  /** `observed`: the capability-floor check against the baseline round. */
  capability_floor?: JsonObject | null;
  /** `observed`: static analysis of the candidate's code. */
  candidate_code?: JsonObject | null;
  /** `observed`: the platform's tamper record; presence is a problem in `certify()`. */
  tampered?: Record<string, string[]> | null;
  /** `observed`. */
  verifier_kinds?: string[] | null;
  /** `observed`. */
  train_score?: number | null;
  /** `observed`. */
  train_per_task?: Record<string, number | null> | null;
  /** `observed`. */
  split?: { train?: string[]; eval?: string[] } | null;
  /** `observed`. */
  selection_effect?: JsonObject | null;
  /** `observed`. */
  cumulative?: Cumulative | null;
}

// ---------------------------------------------------------------------------
// run_meta.json
// ---------------------------------------------------------------------------

export interface PlatformRef {
  /** The content hash of the code that decided what these numbers mean. */
  content_sha?: string | null;
  git_sha?: string | null;
  dirty?: boolean | null;
  [key: string]: JsonValue | undefined;
}

export interface SandboxRecord {
  requested?: boolean;
  active?: boolean;
  plan_version?: number;
  detail?: string;
  [key: string]: JsonValue | undefined;
}

/** `run_meta.json`. */
export interface RunMeta {
  // ---- required by schema.py:RUN_META ----
  run_id: string;
  /** Added 2026-10-05 (stage 1). Certified runs carry it; older runs do not. */
  platform?: PlatformRef;
  agent_model: string;
  agent_backend: string;
  harness: string;
  dataset: string;
  rounds_measured?: number;
  workspace: string;

  // ---- RUN_META_ADDED_LATER ----
  /** Added 2026-10-05 (stage 1): the improver the run *resolved*. */
  improver?: Improver | string | null;

  // ---- observed in runs/: reports, therefore optional ----
  mode?: string;
  sampling_policy?: string;
  env?: EnvRecord;
  sandbox?: SandboxRecord;
  split?: { train?: string[]; eval?: string[] } | null;
  split_declared?: boolean;
  framework_version?: string;
  method_entrypoint?: string | null;
  trials?: number | null;
  jobs?: number | null;
  trajectory_shape?: string | null;
  curve_drawn?: string | null;
  nominated?: number | null;
  selection_pool_size?: number | null;
  failed_steps?: JsonValue[];
  steps_truncated?: number | null;
  steps_measured?: number | null;
  final_score?: number | null;
  wall_clock_s?: number | null;
  work_root?: string;
  platform_root?: string;
  [key: string]: JsonValue | undefined | null | PlatformRef | Improver | EnvRecord | SandboxRecord;
}

// ---------------------------------------------------------------------------
// certify() — the answer to "can I quote this run?"
// ---------------------------------------------------------------------------

/**
 * The exact dict `harnessgrad/store/schema.py:certify()` returns, which is also the
 * per-run object `tools/validate_run.py --json` emits.
 *
 * The distinction the Experiments screen exists to surface:
 *
 * * `valid` — every point can be read, and every one was measured by the platform.
 * * `certified` — *additionally*, the record names the platform that produced it and the
 *   run did not touch the platform while it ran. A run that predates those fields is
 *   `valid` and **not** `certified`, which is the honest reading.
 */
export interface CertifyResult {
  run_id: string;
  points: number;
  rounds: number[];
  valid: boolean;
  certified: boolean;
  /** A problem means the point cannot be read as a measurement. */
  problems: string[];
  /** A note means the point is missing something a later platform recorded. */
  notes: string[];
  tampered: string[];
  platform_content_sha: string | null;
  final_score: number | null;
}

// ---------------------------------------------------------------------------
// Verdicts and traces
// ---------------------------------------------------------------------------

/** The per-test tally `eval/runner.py:_test_report_failures` parses out of a CTRF report. */
export interface TestTally {
  passed: number;
  failed: number;
  skipped?: number;
  pending?: number;
  other?: number;
}

/** `verdicts/round-<n>/<task_id>.json`. */
export interface Verdict {
  scorer_isolation_class?: string;
  task_id: string;
  round: number;
  score: number | null;
  /** The verifier's kind, e.g. `command`. */
  kind: string;
  passed: boolean;
  /** The one-line summary the check produced. The difference between `reward 0` and a reason. */
  detail: string;
  /** Present for some runs; the harness's own exit code and stderr. */
  harness?: { exit_code?: number | null; stderr?: string | null } | null;
  /**
   * The check's own test tally, when its report was machine-readable. Absent means the
   * check reported no tally — which is *not* zero tests passed (`eval/runner.py:838`).
   */
  tests?: TestTally | null;
  [key: string]: JsonValue | TestTally | undefined | null;
}

/**
 * One line of a `<round>_traces/<task_id>.jsonl` file.
 *
 * The file is a sequence of heterogeneous events, distinguished by their keys rather than
 * by a `type` field. The union below models every kind observed in
 * `runs/ds-dgm/round0_traces/*.jsonl`; `UnknownTraceEvent` keeps a future event from
 * breaking the timeline.
 */
export interface TraceIdentityEvent {
  harness_identity: HarnessIdentity;
}
export interface TraceModelEvent {
  step: number;
  reply: string;
  model_ms?: number;
}
export interface TraceCommandEvent {
  step: number;
  command: string;
  exit: number;
  command_ms?: number;
  output?: string;
}
export interface TraceClipEvent {
  step: number;
  output_clipped: JsonValue;
  shown: JsonValue;
}
export interface TraceNudgeEvent {
  step: number;
  finish_nudge?: JsonValue;
  repeat_nudge?: JsonValue;
}
export interface TraceSubmitEvent {
  step: number;
  missing?: JsonValue;
  submitted?: JsonValue;
  submit_rejected?: JsonValue;
}
export interface TraceWallClockEvent {
  wall_clock_s: number;
}
export interface TraceUsageEvent {
  usage: JsonValue;
}
export interface TraceDuplicateEvent {
  step: number;
  duplicate_keys: JsonValue;
}
export interface UnknownTraceEvent {
  [key: string]: JsonValue;
}

export type TraceEvent =
  | TraceIdentityEvent
  | TraceModelEvent
  | TraceCommandEvent
  | TraceClipEvent
  | TraceNudgeEvent
  | TraceSubmitEvent
  | TraceWallClockEvent
  | TraceUsageEvent
  | TraceDuplicateEvent
  | UnknownTraceEvent;

// ---------------------------------------------------------------------------
// Round diffs — `runs/<id>/diffs/round-<n>.json` + `.patch`
// ---------------------------------------------------------------------------

export interface RoundDiffFile {
  path: string;
  added: number;
  removed: number;
}

/**
 * The stat half of a round's saved diff (`records.py:_save_round_diff`).
 *
 * `from`, `to`, `added` and `removed` are nullable because the read API still serves the
 * *patch* when the sibling `round-<n>.json` stat is half-written or unreadable: in that
 * case it reports `stat: null` and a `stat_error`. Fabricating `0` here would let a patch
 * with no numstat render as "no textual change", which is the opposite claim.
 */
export interface RoundDiffStat {
  round: number;
  /** The harness sha before the round. */
  from: string | null;
  /** The harness sha after the round. */
  to: string | null;
  files: RoundDiffFile[];
  added: number | null;
  removed: number | null;
}

/** The stat plus the unified patch, which is what Monaco renders. */
export interface RoundDiff extends RoundDiffStat {
  patch: string;
  /** Set when the API could not read the stat file but still served the patch. */
  stat_error?: string | null;
}

/**
 * `GET /api/runs/:id/rounds/:n/diff` — the endpoint the run/compare/task screens read the
 * patch from.
 *
 * The bundle's `diffs` map carries the **stat only**; this endpoint carries the patch. That
 * split is what keeps a run bundle small enough to load eagerly. A round with no saved
 * patch is `404`, which the client turns into an explicit absence, not an empty patch.
 */
export interface RoundDiffResponse {
  run_id: string;
  round: number;
  /** `null` when the stat file is unreadable while the patch still exists. */
  stat: RoundDiffStat | null;
  /** Why `stat` is `null`; `null` when the stat was read. */
  stat_error: string | null;
  patch: string;
}

// ---------------------------------------------------------------------------
// Inferred endpoint envelopes (the read API does not exist yet)
// ---------------------------------------------------------------------------

/**
 * `GET /api/runs` — one row per run directory.
 *
 * **Inferred envelope.** It is `certify(run_dir)` for the whole tree plus the handful of
 * `run_meta` fields the Experiments table sorts and filters on. `certify()` does not read
 * `agent_model`, `harness`, `dataset` or a timestamp; the API must join them in.
 */
export interface RunSummary {
  certify: CertifyResult;
  run_id: string;
  /** `run_meta.agent_model`; `null` when `run_meta.json` is missing or unreadable. */
  agent_model: string | null;
  agent_backend: string | null;
  harness: string | null;
  dataset: string | null;
  /** `run_meta.improver`, resolved by the platform — not guessed from the method's name. */
  improver: string | null;
  mode: string | null;
  side: string | null;
  score_kind: string | null;
  /** The last point's `score` (also `certify().final_score`). */
  last_score: number | null;
  /**
   * The last point's `test_rate`.
   *
   * **The key is omitted, not nulled, when the last point carried no `test_rate`.** A point
   * recorded before stage 0 has no such field at all, and a point whose checks report no
   * per-test tally carries `null`; the API keeps those two apart the same way the record
   * does, so this is optional rather than nullable. `presence.testRate` renders all three
   * cases (absent, null, a real zero) differently.
   */
  last_test_rate?: number | null;
  /** `run_meta.wall_clock_s`. */
  wall_clock_s: number | null;
  /**
   * The run's timestamp. `certify()` does not return one; the read API uses the last
   * point's `timestamp_utc` when the curve has one, otherwise the run directory's mtime.
   * `timestamp_source` names which, so a reader is never told an mtime is a measurement.
   */
  timestamp_utc: string | null;
  /** `"curve"` or `"run_meta_mtime"`; absent in the fixture subset. */
  timestamp_source?: string | null;
  /**
   * Why the run is unreadable, when there is no `run_meta.json` at all. A run directory
   * with no curve is `valid: false, points: 0`; it is not an error to fetch.
   */
  meta_error: string | null;
}

/**
 * `GET /api/runs/:id` — everything the Run detail screen renders.
 *
 * **Inferred envelope.** The API should return the whole point list (a run has tens of
 * points, not millions), the verdict index for every round, and the round diff stats.
 * Traces are *not* included here: they are fetched per task by the Task detail screen.
 */
export interface RunBundle {
  run_id: string;
  /**
   * **`Partial`, because a run directory need not have a readable `run_meta.json`.** The API
   * answers `{}` for one that does not (and sets `load_problems`), rather than 404: a
   * directory that was interrupted before its first write is still a row an operator wants
   * to see. `RunHeader` guards on `meta.dataset` and says so.
   */
  meta: Partial<RunMeta>;
  points: CurvePoint[];
  /** `round number -> task_id -> verdict`. Loaded from `verdicts/round-<n>/`. */
  verdicts: Record<string, Record<string, Verdict>>;
  /**
   * `round number -> diff stat`. **Statistic only** — the read API moved the patch to
   * `GET /api/runs/:id/rounds/:n/diff` so a bundle stays small. The fixture files still
   * carry `patch` on each entry, which is why the fixture-backed `getRoundDiff` can answer
   * without a second request. `RoundDiffStat`, not `RoundDiff`: reading a patch out of the
   * bundle is exactly the client/API mismatch this type now forbids.
   */
  diffs: Record<string, RoundDiffStat>;
  /** Problems reading the run directory; empty for a healthy run. */
  load_problems: string[];
}

/**
 * `GET /api/runs/:id/rounds/:round/tasks/:task` — the Task detail screen.
 *
 * **Inferred envelope.** `verdict` is the file on disk; `trace` is the parsed JSONL, one
 * object per line, in file order. `patch` is present only for a round that has one.
 */
export interface TaskPage {
  run_id: string;
  round: number;
  task_id: string;
  verdict: Verdict | null;
  /** The verdict file's absence is a fact: the task was not scored in this round. */
  verdict_problems: string[];
  trace: TraceEvent[];
  trace_problems: string[];
  /** The round diff that produced this round, for context. */
  diff: RoundDiff | null;
}

/**
 * `GET /api/launch/options` — the values the Launch form may offer.
 *
 * **Inferred envelope.** The layout is the point: `env_derived` is the list of fields
 * whose *default* comes from the environment (`.env` / `HG_*`), and which the form must
 * mark as such rather than presenting as a free choice.
 */
export interface LaunchOptions {
  harnesses: string[];
  datasets: string[];
  samplings: string[];
  improvers: string[];
  modes: string[];
  sides: string[];
  /** `improvers/improvers.json` names, or `null` when the file is unreadable. */
  improver_names: string[];
  /** Values the driver would take from the environment when the flag is omitted. */
  env_derived: EnvDerivedField[];
  /** The driver's own flags, for the argv preview. */
  flag_help: Record<string, string>;
}

export interface EnvDerivedField {
  /** The flag it backs, e.g. `--agent-model (no flag; harness-declared)`. */
  flag: string;
  env_var: string;
  /** The current value for a non-secret variable, or `null` when unset or secret. */
  value: string | null;
  /** Whether the variable is set at all. A secret's value is never returned. */
  set: boolean;
  /** `true` for a variable whose value must never leave the process (a key, token or password). */
  secret: boolean;
  /** One line on what it changes. */
  note: string;
}
