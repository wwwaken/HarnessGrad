import type { TranslationKey } from "@/i18n/en";
import type { EnvDerivedField, LaunchOptions } from "@/types";

/**
 * What the Launch screen produces: the argv `driver.py` would be given, and the JSON a
 * future `POST /api/runs` would take.
 *
 * Nothing here submits anything — there is no write API yet, and this session must not
 * create one. The point of building the argv is that it is *checkable*: a researcher can
 * see exactly which flags their form became, and the fields the driver would take from
 * the environment are marked as such rather than presented as choices.
 *
 * The flags mirror `python3 driver.py --help` (read 2026-10-06). Two details that help
 * text does not make obvious are honoured:
 *
 * * `--mode` is **deprecated and ignored** — there is one engine. The builder never emits
 *   it, and says so when the form has one selected.
 * * `--trials 1` and `--jobs 1` are the defaults, so they are omitted rather than spelled
 *   out; the argv a person reads should be the argv they would have typed.
 */

export interface LaunchConfig {
  runId: string;
  harness: string;
  dataset: string;
  sampling: string;
  rounds: number;
  trials: number;
  jobs: number;
  improver: string;
  improverModel: string;
  methodEntrypoint: string;
  /** Comma- or whitespace-separated task ids; empty means "the whole side". */
  tasks: string;
  side: "train" | "eval";
  fromRun: string;
  fromRound: string;
  seed: string;
  noSandbox: boolean;
  workRoot: string;
  /** Kept for the form's completeness only: the driver ignores it. */
  mode: "A" | "B";
}

export const DEFAULT_LAUNCH_CONFIG: LaunchConfig = {
  runId: "",
  harness: "",
  dataset: "",
  sampling: "all",
  rounds: 2,
  trials: 1,
  jobs: 1,
  improver: "",
  improverModel: "",
  methodEntrypoint: "",
  tasks: "",
  side: "train",
  fromRun: "",
  fromRound: "",
  seed: "",
  noSandbox: false,
  workRoot: "",
  mode: "A",
};

/** The JSON body `POST /api/runs` should take. Inferred; see `web/README.md`. */
export interface LaunchRequest {
  run_id: string;
  harness: string;
  dataset: string;
  sampling: string;
  rounds: number;
  trials: number;
  jobs: number;
  improver: string | null;
  improver_model: string | null;
  method_entrypoint: string | null;
  tasks: string[];
  side: "train" | "eval";
  from_run: string | null;
  from_round: number | null;
  seed: string | null;
  sandbox: boolean;
  work_root: string | null;
}

export interface LaunchPlan {
  argv: string[];
  /** The argv as a copy-pasteable line, with shell quoting. */
  command: string;
  request: LaunchRequest;
  /**
   * Hard errors: the driver would refuse this. Keys plus parameters, for the same reason as
   * `warnings` — this module knows *what* is wrong, the screen knows how to say it.
   */
  errors: Array<{ key: TranslationKey; params?: Record<string, string | number> }>;
  /** Things a reader should know before running it. */
  /**
   * Warnings as **keys plus parameters**, not sentences. This module builds the argv and
   * knows what is wrong with it; how to say that is the screen's business, and a string here
   * would be the one part of the Launch screen a Chinese reader could not read.
   */
  warnings: Array<{ key: TranslationKey; params?: Record<string, string | number> }>;
  /** Fields whose value would come from the environment, kept visible beside the form. */
  envHints: EnvDerivedField[];
}

export function splitTasks(tasks: string): string[] {
  return tasks
    .split(/[,\s]+/)
    .map((t) => t.trim())
    .filter(Boolean);
}

export function shellQuote(token: string): string {
  if (/^[A-Za-z0-9_@%+=:,./-]+$/.test(token)) return token;
  return `'${token.replace(/'/g, `'\\''`)}'`;
}

export function commandString(argv: string[]): string {
  return ["python3", "driver.py", ...argv].map(shellQuote).join(" ");
}

export type LaunchError = { key: TranslationKey; params?: Record<string, string | number> };

export function validateLaunch(config: LaunchConfig, options?: LaunchOptions): LaunchError[] {
  const errors: LaunchError[] = [];
  if (!config.runId.trim()) {
    errors.push({ key: "launch.errRunIdRequired" });
  } else if (!/^[A-Za-z0-9._-]+$/.test(config.runId.trim())) {
    errors.push({ key: "launch.errRunIdChars" });
  }
  if (!config.harness.trim()) errors.push({ key: "launch.errHarnessRequired" });
  if (!config.dataset.trim()) errors.push({ key: "launch.errDatasetRequired" });
  if (options && config.harness && !options.harnesses.includes(config.harness)) {
    errors.push({ key: "launch.errHarnessUnknown", params: { name: config.harness } });
  }
  if (options && config.dataset && !options.datasets.includes(config.dataset)) {
    errors.push({ key: "launch.errDatasetUnknown", params: { name: config.dataset } });
  }
  if (!Number.isInteger(config.rounds) || config.rounds < 1) {
    errors.push({ key: "launch.errRoundsPositive" });
  }
  if (!Number.isInteger(config.trials) || config.trials < 1) {
    errors.push({ key: "launch.errTrialsPositive" });
  }
  if (!Number.isInteger(config.jobs) || config.jobs < 1) {
    errors.push({ key: "launch.errJobsPositive" });
  }
  if (config.side === "eval" && !config.fromRun.trim()) {
    errors.push({ key: "launch.errEvalNeedsFromRun" });
  }
  if (config.side === "train" && config.fromRun.trim()) {
    errors.push({ key: "launch.errFromRunOnlyEval" });
  }
  if (config.side === "eval" && config.fromRound && !/^\d+$/.test(config.fromRound.trim())) {
    errors.push({ key: "launch.errFromRoundInteger" });
  }
  return errors;
}

export function buildLaunchPlan(config: LaunchConfig, options?: LaunchOptions): LaunchPlan {
  const argv: string[] = [];
  const tasks = splitTasks(config.tasks);
  const warnings: Array<{ key: TranslationKey; params?: Record<string, string | number> }> = [];

  if (config.runId.trim()) argv.push("--run-id", config.runId.trim());
  if (config.harness.trim()) argv.push("--harness", config.harness.trim());
  if (config.dataset.trim()) argv.push("--dataset", config.dataset.trim());
  argv.push("--sampling", config.sampling);
  argv.push("--rounds", String(config.rounds));
  if (config.trials !== 1) argv.push("--trials", String(config.trials));
  if (config.jobs !== 1) argv.push("--jobs", String(config.jobs));
  argv.push("--side", config.side);
  if (config.side === "eval" && config.fromRun.trim()) {
    argv.push("--from-run", config.fromRun.trim());
    if (config.fromRound.trim()) argv.push("--from-round", config.fromRound.trim());
  }
  if (config.improver.trim()) argv.push("--improver", config.improver.trim());
  if (config.improverModel.trim()) argv.push("--improver-model", config.improverModel.trim());
  if (config.methodEntrypoint.trim()) {
    argv.push("--method-entrypoint", config.methodEntrypoint.trim());
  }
  if (tasks.length) argv.push("--tasks", tasks.join(","));
  if (config.seed.trim()) argv.push("--seed", config.seed.trim());
  if (config.noSandbox) argv.push("--no-sandbox");
  if (config.workRoot.trim()) argv.push("--work-root", config.workRoot.trim());

  if (config.trials > 1) {
    warnings.push({ key: "launch.warnTrials", params: { n: config.trials } });
  }
  if (config.jobs > 1) {
    warnings.push({ key: "launch.warnJobs", params: { n: config.jobs } });
  }
  if (config.side === "train") {
    warnings.push({ key: "launch.warnTrainSide" });
  }
  if (config.noSandbox) {
    warnings.push({ key: "launch.warnNoSandbox" });
  }
  if (!config.noSandbox) {
    warnings.push({ key: "launch.warnSandboxRequired" });
  }
  if (config.mode !== "A") {
    warnings.push({ key: "launch.warnModeDeprecated", params: { mode: config.mode } });
  }
  if (!config.improver.trim()) {
    warnings.push({ key: "launch.warnNoImprover" });
  }

  const request: LaunchRequest = {
    run_id: config.runId.trim(),
    harness: config.harness.trim(),
    dataset: config.dataset.trim(),
    sampling: config.sampling,
    rounds: config.rounds,
    trials: config.trials,
    jobs: config.jobs,
    improver: config.improver.trim() || null,
    improver_model: config.improverModel.trim() || null,
    method_entrypoint: config.methodEntrypoint.trim() || null,
    tasks,
    side: config.side,
    from_run: config.side === "eval" ? config.fromRun.trim() || null : null,
    from_round:
      config.side === "eval" && config.fromRound.trim() ? Number(config.fromRound.trim()) : null,
    seed: config.seed.trim() || null,
    sandbox: !config.noSandbox,
    work_root: config.workRoot.trim() || null,
  };

  return {
    argv,
    command: commandString(argv),
    request,
    errors: validateLaunch(config, options),
    warnings,
    envHints: options?.env_derived ?? [],
  };
}
