import type { CertifyResult, CurvePoint, RunBundle, Verdict } from "@/types";

/**
 * Typed builders for the unit tests. Not imported by any component, so nothing here reaches
 * the bundle; it exists so a test can state only the fields it is about and still construct a
 * schema-complete record.
 */

export function point(overrides: Partial<CurvePoint> & { round: number }): CurvePoint {
  const base: CurvePoint = {
    run_id: "run-a",
    round: overrides.round,
    identity: { harness_sha: "sha-base", agent_model: "agent-x", agent_backend: "openai" },
    score: 0.5,
    score_kind: "exam",
    side: "eval",
    per_task: {},
    n_scored: 0,
    env: { kind: "exec", image_digest: "sha256:abc", placement: "inside" },
    sampling: { policy: "all", task_ids: [] },
    cost: {},
    timestamp_utc: "2026-10-05T12:00:00Z",
    measured_by_platform: true,
  };
  return { ...base, ...overrides };
}

export function bundle(
  runId: string,
  points: CurvePoint[],
  overrides: Partial<RunBundle> = {},
): RunBundle {
  return {
    run_id: runId,
    meta: {
      run_id: runId,
      agent_model: "agent-x",
      agent_backend: "openai",
      harness: "loop",
      dataset: "demo",
      workspace: "/tmp/ws",
      platform: { content_sha: "platform-sha", git_sha: "git-sha", dirty: false },
    },
    points,
    verdicts: {},
    diffs: {},
    load_problems: [],
    ...overrides,
  };
}

export function certify(overrides: Partial<CertifyResult> = {}): CertifyResult {
  return {
    run_id: "run-a",
    points: 3,
    rounds: [0, 1, 2],
    valid: true,
    certified: false,
    problems: [],
    notes: [],
    tampered: [],
    platform_content_sha: null,
    final_score: 0.1,
    ...overrides,
  };
}

export function verdict(overrides: Partial<Verdict> & { task_id: string }): Verdict {
  return {
    round: 0,
    score: 0,
    kind: "command",
    passed: false,
    detail: "reward 0 from /logs/verifier/reward.txt (exit 0)",
    ...overrides,
  };
}
