import { describe, expect, it } from "vitest";
import {
  DEFAULT_LAUNCH_CONFIG,
  buildLaunchPlan,
  commandString,
  shellQuote,
  splitTasks,
  validateLaunch,
  type LaunchConfig,
} from "./launch";
import type { LaunchOptions } from "@/types";

/**
 * The argv builder.
 *
 * Two properties are worth pinning down, because both are easy to get subtly wrong: the
 * builder never emits `--mode` (the driver says it is deprecated and ignored, and emitting it
 * would imply a choice that does not exist), and it omits the flags whose value *is* the
 * default (`--trials 1`, `--jobs 1`) so the line reads like the one a person would type.
 */

const OPTIONS: LaunchOptions = {
  harnesses: ["loop", "loop_plain"],
  datasets: ["demo", "terminal_bench"],
  samplings: ["all", "random_10"],
  improvers: ["deepseek", "codex"],
  modes: ["A", "B"],
  sides: ["train", "eval"],
  improver_names: ["deepseek", "codex"],
  env_derived: [],
  flag_help: {},
};

function config(overrides: Partial<LaunchConfig> = {}): LaunchConfig {
  return {
    ...DEFAULT_LAUNCH_CONFIG,
    runId: "ds-dgm-r3",
    harness: "loop",
    dataset: "terminal_bench",
    ...overrides,
  };
}

describe("shell quoting", () => {
  it("leaves simple tokens alone and quotes the rest", () => {
    expect(shellQuote("--rounds")).toBe("--rounds");
    expect(shellQuote("a/b-c_d.e")).toBe("a/b-c_d.e");
    expect(shellQuote("python /x/run.py")).toBe("'python /x/run.py'");
  });

  it("escapes a single quote inside a quoted token", () => {
    expect(shellQuote("it's")).toBe("'it'\\''s'");
  });

  it("prefixes the interpreter and driver", () => {
    expect(commandString(["--run-id", "x"])).toBe("python3 driver.py --run-id x");
  });
});

describe("splitTasks", () => {
  it("accepts commas, spaces or both", () => {
    expect(splitTasks("a,b")).toEqual(["a", "b"]);
    expect(splitTasks("a, b   c")).toEqual(["a", "b", "c"]);
    expect(splitTasks("  ")).toEqual([]);
  });
});

describe("buildLaunchPlan", () => {
  it("emits the core flags and omits the defaults", () => {
    const plan = buildLaunchPlan(config(), OPTIONS);
    expect(plan.argv).toEqual([
      "--run-id",
      "ds-dgm-r3",
      "--harness",
      "loop",
      "--dataset",
      "terminal_bench",
      "--sampling",
      "all",
      "--rounds",
      "2",
      "--side",
      "train",
    ]);
    expect(plan.errors).toEqual([]);
  });

  it("never emits --mode, and warns when the form has one selected", () => {
    const plan = buildLaunchPlan(config({ mode: "B" }), OPTIONS);
    expect(plan.argv).not.toContain("--mode");
    expect(plan.warnings.some((w) => w.includes("deprecated and ignored"))).toBe(true);
  });

  it("spells out trials and jobs only when they differ from the default", () => {
    const plan = buildLaunchPlan(config({ trials: 3, jobs: 4 }), OPTIONS);
    expect(plan.argv).toContain("--trials");
    expect(plan.argv).toContain("3");
    expect(plan.argv).toContain("--jobs");
    expect(plan.argv).toContain("4");
    expect(plan.warnings.some((w) => w.includes("score_std"))).toBe(true);
  });

  it("warns about the training side, because those numbers must not be quoted", () => {
    const plan = buildLaunchPlan(config({ side: "train" }), OPTIONS);
    expect(plan.warnings.some((w) => w.includes("never be quoted as a result"))).toBe(true);
  });

  it("adds the eval wiring and the JSON body fields", () => {
    const plan = buildLaunchPlan(
      config({ side: "eval", fromRun: "ds-dgm", fromRound: "2" }),
      OPTIONS,
    );
    expect(plan.argv).toContain("--from-run");
    expect(plan.argv).toContain("--from-round");
    expect(plan.request.from_run).toBe("ds-dgm");
    expect(plan.request.from_round).toBe(2);
    expect(plan.request.sandbox).toBe(true);
  });

  it("does not leak the eval wiring into a train run's JSON body", () => {
    const plan = buildLaunchPlan(config({ side: "train", fromRun: "", fromRound: "" }), OPTIONS);
    expect(plan.request.from_run).toBeNull();
    expect(plan.request.from_round).toBeNull();
  });

  it("records --no-sandbox as sandbox:false and warns that numbers are not comparable", () => {
    const plan = buildLaunchPlan(config({ noSandbox: true }), OPTIONS);
    expect(plan.argv).toContain("--no-sandbox");
    expect(plan.request.sandbox).toBe(false);
    expect(plan.warnings.some((w) => w.includes("not comparable"))).toBe(true);
  });

  it("passes tasks through as a comma-joined argv list and as a JSON array", () => {
    const plan = buildLaunchPlan(config({ tasks: "a, b c" }), OPTIONS);
    expect(plan.argv[plan.argv.indexOf("--tasks") + 1]).toBe("a,b,c");
    expect(plan.request.tasks).toEqual(["a", "b", "c"]);
  });

  it("quotes a method entrypoint with spaces in the rendered command", () => {
    const plan = buildLaunchPlan(
      config({ methodEntrypoint: "python /x/methods/noop/run.py" }),
      OPTIONS,
    );
    expect(plan.command).toContain("'python /x/methods/noop/run.py'");
  });
});

describe("validateLaunch", () => {
  it("requires a run id and refuses a name that would be an unsafe path segment", () => {
    expect(validateLaunch(config({ runId: "" }), OPTIONS).join(" ")).toContain("--run-id");
    expect(validateLaunch(config({ runId: "../escape" }), OPTIONS).join(" ")).toContain(
      "letters, digits",
    );
    expect(validateLaunch(config({ runId: "ok-1.2_x" }), OPTIONS)).toEqual([]);
  });

  it("requires harness and dataset, and refuses values that are not on this machine", () => {
    expect(validateLaunch(config({ harness: "" }), OPTIONS).join(" ")).toContain("--harness");
    expect(validateLaunch(config({ dataset: "nope" }), OPTIONS).join(" ")).toContain(
      "not one of the datasets",
    );
  });

  it("requires --from-run for an eval side and refuses it for a train side", () => {
    expect(validateLaunch(config({ side: "eval" }), OPTIONS).join(" ")).toContain("--from-run");
    expect(validateLaunch(config({ side: "train", fromRun: "x" }), OPTIONS).join(" ")).toContain(
      "applies only to `--side eval`",
    );
  });

  it("refuses non-positive rounds, trials and jobs", () => {
    expect(validateLaunch(config({ rounds: 0 }), OPTIONS).join(" ")).toContain("--rounds");
    expect(validateLaunch(config({ trials: 0 }), OPTIONS).join(" ")).toContain("--trials");
    expect(validateLaunch(config({ jobs: -1 }), OPTIONS).join(" ")).toContain("--jobs");
  });

  it("refuses a non-integer from-round", () => {
    expect(
      validateLaunch(config({ side: "eval", fromRun: "x", fromRound: "last" }), OPTIONS).join(" "),
    ).toContain("--from-round");
  });
});
