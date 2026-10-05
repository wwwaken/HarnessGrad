import { fixtureUrls } from "@/fixtures/urls";
import type {
  LaunchOptions,
  RoundDiff,
  RoundDiffResponse,
  RunBundle,
  RunSummary,
  TaskPage,
  Verdict,
} from "@/types";

/**
 * The read API client.
 *
 * ## Two backends, one set of callers
 *
 * Every screen talks to this module and nothing else. Each function below is named after the
 * endpoint it reads; the body chooses **where the bytes come from**:
 *
 * * **live** — the read API in `web/server/` (`GET /api/...`), same-origin, so the Vite dev
 *   server needs a proxy and the built SPA served by `serve.py` needs nothing;
 * * **fixtures** — the curated JSON in `src/fixtures/data/`, fetched through `fixtureUrls`.
 *
 * Which one is in use is decided **at runtime**, not baked in, because the point of the
 * fixture fallback is that a demo with no server still works: `resolveBackend()` probes
 * `GET /api/health` once on startup and every request awaits that decision. `VITE_API` is a
 * build-time *preference* on top of the probe:
 *
 * | `VITE_API` | probe | result |
 * | --- | --- | --- |
 * | unset / `auto` | `/api/health` answers | live |
 * | unset / `auto` | unreachable | fixtures, banner says the API did not answer |
 * | `fixture` | not probed | fixtures, always |
 * | `live` | not used to fall back | live, even when the API is down (so the failure is visible) |
 *
 * `GET /api/health` is not one of the six data endpoints; it exists to answer exactly this
 * question, and `web/server/README.md` §6 documents it.
 *
 * ## The diff patch is its own request
 *
 * `GET /api/runs/:id` returns `diffs: {round: stat}` — a statistic, no patch — and the patch
 * lives at `GET /api/runs/:id/rounds/:n/diff` → `{stat, patch}` (404 when absent). So
 * `getRoundDiff` fetches that endpoint in live mode. Fixtures still ship the patch inline
 * because a fixture file is not a network round trip; the type `RunBundle.diffs` is
 * `RoundDiffStat`, not `RoundDiff`, so a future caller cannot read the patch from it by
 * accident.
 *
 * ## Errors are states, not blank screens
 *
 * An error response is a JSON body the server wrote (`{"error", "status", "message", …}`);
 * `fetchJson` turns it into an `ApiError` carrying the server's own sentence, and the
 * screens render it through `ErrorState`. A `404` is distinguished from a transport failure
 * because "this run is not on disk" and "the API is not running" are different facts.
 */

export type ApiErrorKind = "not-found" | "bad-request" | "network" | "parse" | "unavailable";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status: number | null;
  readonly hint: string | null;

  constructor(kind: ApiErrorKind, message: string, options: { status?: number; hint?: string } = {}) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = options.status ?? null;
    this.hint = options.hint ?? null;
  }
}

// ---------------------------------------------------------------------------
// Which backend is in use
// ---------------------------------------------------------------------------

export type BackendMode = "fixture" | "live";
/** What `VITE_API` asked for. `auto` is the default and probes the API. */
export type BackendPreference = "auto" | "live" | "fixture";
export type BackendStatus = "checking" | "ready" | "unreachable";

export interface BackendState {
  /** Which source requests use **now**. */
  mode: BackendMode;
  preference: BackendPreference;
  status: BackendStatus;
  /** `/api` prefix. Empty by default (same-origin); `VITE_API_BASE` overrides it. */
  baseUrl: string;
  /** Run directories the live API reported, or `null` when it has not answered. */
  runs: number | null;
  /** Short label for the banner, e.g. `Fixtures` or `Live API`. */
  label: string;
  /** One truthful sentence about where the numbers come from. */
  note: string;
}

//: `VITE_API_BASE` lets a build point at another host (e.g. `http://host:8791`). The SPA
//: under `serve.py` and the Vite dev proxy both use the default empty, same-origin prefix.
const API_BASE = ((import.meta.env.VITE_API_BASE as string | undefined) ?? "").replace(/\/+$/, "");

const HEALTH_TIMEOUT_MS = 1500;

function preferenceFromEnv(): BackendPreference {
  const raw = (import.meta.env.VITE_API as string | undefined)?.trim().toLowerCase();
  if (raw === "live" || raw === "api") return "live";
  if (raw === "fixture" || raw === "fixtures") return "fixture";
  return "auto";
}

function initialState(): BackendState {
  const preference = preferenceFromEnv();
  // Before the probe answers, assume the honest default: fixtures. A live run flips it to
  // `live` a tick later, and the banner says "checking…" meanwhile rather than claiming one.
  return {
    mode: preference === "live" ? "live" : "fixture",
    preference,
    status: "checking",
    baseUrl: API_BASE,
    runs: null,
    label: "Checking…",
    note:
      preference === "fixture"
        ? "Fixtures are forced by VITE_API=fixture."
        : `Checking for the read API at ${API_BASE || "this origin"}/api/health…`,
  };
}

let state: BackendState = initialState();
const listeners = new Set<() => void>();

function publish(next: BackendState): void {
  state = next;
  for (const listener of listeners) listener();
}

/** Subscribe to backend-mode changes (used by `useBackend`). */
export function subscribeBackend(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** The current backend state. Stable between changes, as `useSyncExternalStore` requires. */
export function getBackendState(): BackendState {
  return state;
}

/** Re-arm the probe. Call this after a failure, or in a test's `beforeEach`. */
export function resetBackend(): void {
  resolvePromise = null;
  publish(initialState());
}

async function probeHealth(): Promise<{ ok: boolean; runs: number | null; detail: string }> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);
  try {
    const response = await fetch(`${API_BASE}/api/health`, {
      headers: { accept: "application/json" },
      signal: controller.signal,
    });
    if (!response.ok) {
      return { ok: false, runs: null, detail: `HTTP ${response.status}` };
    }
    // A static host that answers every path with `index.html` would make the status look
    // like success; the body is the real test.
    const body = (await response.json()) as { ok?: unknown; runs?: unknown };
    if (body?.ok !== true) {
      return { ok: false, runs: null, detail: "the response was not `{ok: true}`" };
    }
    return { ok: true, runs: typeof body.runs === "number" ? body.runs : null, detail: "" };
  } catch (cause) {
    return {
      ok: false,
      runs: null,
      detail: cause instanceof Error ? cause.message : String(cause),
    };
  } finally {
    clearTimeout(timer);
  }
}

let resolvePromise: Promise<BackendState> | null = null;

/**
 * Decide, once, whether the read API is in use. Every data function awaits this.
 *
 * The result is memoized so N screens make one probe, not N.
 */
export function resolveBackend(): Promise<BackendState> {
  if (resolvePromise) return resolvePromise;
  resolvePromise = (async () => {
    const preference = preferenceFromEnv();
    if (preference === "fixture") {
      publish({
        mode: "fixture",
        preference,
        status: "ready",
        baseUrl: API_BASE,
        runs: null,
        label: "Fixtures (forced)",
        note:
          "VITE_API=fixture: this build reads the curated fixture subset " +
          "(runs/ds-dgm, runs/ds-rrsi) and never contacts the read API.",
      });
      return state;
    }

    const health = await probeHealth();
    const api = `${API_BASE || "this origin"}/api`;

    if (health.ok) {
      publish({
        mode: "live",
        preference,
        status: "ready",
        baseUrl: API_BASE,
        runs: health.runs,
        label: "Live API",
        note:
          `Live read API at ${api}: ${health.runs ?? "?"} run row(s) read from runs/. ` +
          "A run that is being written right now appears with points: 0, not hidden.",
      });
      return state;
    }

    if (preference === "live") {
      publish({
        mode: "live",
        preference,
        status: "unreachable",
        baseUrl: API_BASE,
        runs: null,
        label: "Live API (unreachable)",
        note:
          `VITE_API=live, but the read API at ${api} did not answer ` +
          `(${health.detail}). Requests will fail rather than silently fall back to fixtures.`,
      });
      return state;
    }

    publish({
      mode: "fixture",
      preference,
      status: "ready",
      baseUrl: API_BASE,
      runs: null,
      label: "Fixtures",
      note:
        `Fixtures only: the read API at ${api}/health did not answer (${health.detail}), so ` +
        "this build falls back to a real subset of runs/ds-dgm and runs/ds-rrsi. Start it " +
        "with `python3 web/server/serve.py --port 8791 --runs-root runs` for live data.",
    });
    return state;
  })();
  return resolvePromise;
}

// ---------------------------------------------------------------------------
// Fetching
// ---------------------------------------------------------------------------

function bodyMessage(text: string): { message: string | null; code: string | null } {
  try {
    const parsed = JSON.parse(text) as unknown;
    if (parsed && typeof parsed === "object") {
      const record = parsed as Record<string, unknown>;
      return {
        message: typeof record.message === "string" ? record.message : null,
        code: typeof record.error === "string" ? record.error : null,
      };
    }
  } catch {
    // not JSON; the HTTP status is all we have
  }
  return { message: null, code: null };
}

function kindForStatus(status: number): ApiErrorKind {
  if (status === 404) return "not-found";
  if (status === 400 || status === 422) return "bad-request";
  if (status >= 500) return "unavailable";
  return "network";
}

async function fetchJson<T>(url: string, what: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, { headers: { accept: "application/json" } });
  } catch (cause) {
    throw new ApiError("network", `could not reach ${what}`, {
      hint: cause instanceof Error ? cause.message : String(cause),
    });
  }

  const text = await response.text().catch(() => "");
  if (!response.ok) {
    const { message, code } = bodyMessage(text);
    throw new ApiError(
      kindForStatus(response.status),
      message ?? `${what} returned HTTP ${response.status}`,
      {
        status: response.status,
        hint: code ? `the API answered \`${code}\`` : url,
      },
    );
  }

  try {
    return JSON.parse(text) as T;
  } catch (cause) {
    throw new ApiError("parse", `${what} is not valid JSON`, {
      status: response.status,
      hint: cause instanceof Error ? cause.message : String(cause),
    });
  }
}

// ---------------------------------------------------------------------------
// GET /api/runs  -> fixture: data/runs-index.json
// ---------------------------------------------------------------------------

export async function listRuns(): Promise<RunSummary[]> {
  const backend = await resolveBackend();
  if (backend.mode === "live") {
    return fetchJson<RunSummary[]>(`${backend.baseUrl}/api/runs`, "the run index (live API)");
  }
  return fetchJson<RunSummary[]>(fixtureUrls.runsIndex, "the run index (fixtures)");
}

// ---------------------------------------------------------------------------
// GET /api/runs/:id -> fixture: data/run-<id>.json
// ---------------------------------------------------------------------------

export async function getRun(runId: string): Promise<RunBundle> {
  const backend = await resolveBackend();
  if (backend.mode === "live") {
    return fetchJson<RunBundle>(
      `${backend.baseUrl}/api/runs/${encodeURIComponent(runId)}`,
      `run \`${runId}\` (live API)`,
    );
  }
  const url = fixtureUrls.runBundles[runId];
  if (!url) {
    throw new ApiError("not-found", `run \`${runId}\` is not in the fixtures`, {
      status: 404,
      hint:
        `The fixture set carries two full runs (${Object.keys(fixtureUrls.runBundles).join(", ")}). ` +
        "Run the read API for any run directory under runs/.",
    });
  }
  return fetchJson<RunBundle>(url, `run \`${runId}\``);
}

/** Fixture run ids offered as quick links; the live API lists every run it serves. */
export function availableRunIds(): string[] {
  return Object.keys(fixtureUrls.runBundles);
}

// ---------------------------------------------------------------------------
// GET /api/runs/:id/rounds/:n/tasks/:task
// ---------------------------------------------------------------------------

export async function getTaskPage(
  runId: string,
  round: number,
  taskId: string,
): Promise<TaskPage> {
  const backend = await resolveBackend();
  if (backend.mode === "live") {
    return fetchJson<TaskPage>(
      `${backend.baseUrl}/api/runs/${encodeURIComponent(runId)}/rounds/${round}` +
        `/tasks/${encodeURIComponent(taskId)}`,
      `task \`${taskId}\` of round ${round} (live API)`,
    );
  }

  const key = `${runId}/${round}/${taskId}`;
  const url = fixtureUrls.taskPages[key];
  if (url) return fetchJson<TaskPage>(url, `task \`${taskId}\``);

  // No fixture file for this task: stand in for the endpoint by reading the run bundle,
  // which carries the verdicts and the diff stat. The trace is not in the bundle — the real
  // API reads it from `round<n>_traces/<task>.jsonl` — so the page says exactly that rather
  // than rendering an empty timeline as if the task had no steps.
  const bundle = await getRun(runId);
  const point = bundle.points.find((p) => p.round === round);
  const verdict: Verdict | null = bundle.verdicts[String(round)]?.[taskId] ?? null;
  // The fixture bundles carry the patch inline (see the module docstring); read it through
  // the one cast this fallback needs, and never through `RunBundle`'s stat-only type.
  const diff: RoundDiff | null =
    (bundle as RunBundle & { diffs: Record<string, RoundDiff> }).diffs[String(round)] ?? null;
  const verdictProblems: string[] = [];
  if (!verdict) {
    verdictProblems.push(
      `no verdict for \`${taskId}\` in round ${round}: the task was not scored in this round, ` +
        "or it is not part of this run's sampling",
    );
  }
  const traceProblems: string[] = [];
  if (!point) {
    verdictProblems.push(`round ${round} is not in this run's curve`);
  } else {
    traceProblems.push(
      "this task's trace is not part of the fixture subset; the read API returns " +
        `\`runs/${runId}/round${round}_traces/${taskId}.jsonl\` parsed one event per line`,
    );
  }
  return {
    run_id: runId,
    round,
    task_id: taskId,
    verdict,
    verdict_problems: verdictProblems,
    trace: [],
    trace_problems: traceProblems,
    diff,
  };
}

// ---------------------------------------------------------------------------
// GET /api/runs/:id/rounds/:n/diff
// ---------------------------------------------------------------------------

/** Resolve the endpoint's envelope into the shape Monaco renders. */
function toRoundDiff(body: RoundDiffResponse): RoundDiff {
  if (!body.stat) {
    // The stat file is unreadable but the patch exists (the API's `stat_error` case):
    // return the patch with an explicitly absent stat rather than a fabricated 0.
    return {
      round: body.round,
      from: null,
      to: null,
      files: [],
      added: null,
      removed: null,
      patch: body.patch,
      stat_error: body.stat_error,
    };
  }
  return {
    ...body.stat,
    round: body.stat.round ?? body.round,
    patch: body.patch,
    stat_error: body.stat_error,
  };
}

/**
 * The patch for one round, or `null` when the round has no saved diff.
 *
 * The bundle's stat is not used to answer this in live mode: the API deliberately leaves the
 * patch out of the bundle, and a round whose patch is absent is a `404` the screen renders as
 * an absence (round 0 is the unmodified base harness, by construction).
 */
export async function getRoundDiff(runId: string, round: number): Promise<RoundDiff | null> {
  const backend = await resolveBackend();
  if (backend.mode === "live") {
    try {
      const body = await fetchJson<RoundDiffResponse>(
        `${backend.baseUrl}/api/runs/${encodeURIComponent(runId)}/rounds/${round}/diff`,
        `the round ${round} diff of \`${runId}\` (live API)`,
      );
      return toRoundDiff(body);
    } catch (error) {
      // 404 is the endpoint's "no saved patch", not a failure: round 0 and a round that has
      // not been written yet are the same absence.
      if (error instanceof ApiError && error.kind === "not-found") return null;
      throw error;
    }
  }

  const bundle = await getRun(runId);
  // Fixtures ship the patch beside the stat; the live API does not. See module docstring.
  return (bundle as RunBundle & { diffs: Record<string, RoundDiff> }).diffs[String(round)] ?? null;
}

// ---------------------------------------------------------------------------
// GET /api/launch/options
// ---------------------------------------------------------------------------

export async function getLaunchOptions(): Promise<LaunchOptions> {
  const backend = await resolveBackend();
  if (backend.mode === "live") {
    return fetchJson<LaunchOptions>(
      `${backend.baseUrl}/api/launch/options`,
      "the launch options (live API)",
    );
  }
  return fetchJson<LaunchOptions>(fixtureUrls.launchOptions, "the launch options");
}
