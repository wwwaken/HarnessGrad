import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  ApiError,
  getBackendState,
  getRoundDiff,
  getRun,
  listRuns,
  resetBackend,
  resolveBackend,
} from "./api";

/**
 * The client/API boundary.
 *
 * These tests exist because the two things this module decides are invisible in a screen
 * render: *which backend* a request goes to, and *which endpoint* a patch comes from. Both
 * were wrong or absent before `web/server/` landed — the bundle used to carry the patch, the
 * mode did not exist — and both are silent when they regress (a fixture number looks exactly
 * like a live one; a missing patch looks like a round with no diff).
 *
 * `fetch` is stubbed rather than run against a server so the assertions can name the exact
 * URLs requested. The probe is memoized, so `resetBackend()` runs before every test.
 */

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function stubFetch(handler: (url: string) => Response | Promise<Response>) {
  const mock = vi.fn(async (input: RequestInfo | URL) => handler(String(input)));
  vi.stubGlobal("fetch", mock);
  return mock;
}

beforeEach(() => {
  resetBackend();
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  resetBackend();
});

describe("backend mode selection", () => {
  it("selects the live API when /api/health answers", async () => {
    const mock = stubFetch(() => json({ ok: true, runs: 96 }));
    const state = await resolveBackend();

    expect(state.mode).toBe("live");
    expect(state.status).toBe("ready");
    expect(state.runs).toBe(96);
    expect(state.label).toBe("Live API");
    expect(state.note).toContain("runs/");
    expect(String(mock.mock.calls[0]?.[0])).toBe("/api/health");
  });

  it("falls back to fixtures when the API is not running, and says why", async () => {
    stubFetch(() => {
      throw new Error("ECONNREFUSED 127.0.0.1:8791");
    });
    const state = await resolveBackend();

    expect(state.mode).toBe("fixture");
    expect(state.status).toBe("ready");
    expect(state.label).toBe("Fixtures");
    expect(state.note).toContain("ECONNREFUSED");
    expect(state.note).toContain("falls back");
  });

  it("treats a 200 that is not {ok:true} as unreachable", async () => {
    vi.stubEnv("VITE_API", "live");
    // A static host answering every path with index.html is the failure mode this guards.
    stubFetch(() => new Response("<html>index</html>", { status: 200 }));
    const state = await resolveBackend();

    expect(state.status).toBe("unreachable");
  });

  it("does not probe at all when VITE_API=fixture", async () => {
    vi.stubEnv("VITE_API", "fixture");
    const mock = stubFetch(() => json({ ok: true, runs: 1 }));
    const state = await resolveBackend();

    expect(state.mode).toBe("fixture");
    expect(state.preference).toBe("fixture");
    expect(state.label).toContain("forced");
    expect(mock).not.toHaveBeenCalled();
  });

  it("honours VITE_API=live and reports unreachable instead of silently falling back", async () => {
    vi.stubEnv("VITE_API", "live");
    stubFetch(() => {
      throw new Error("ECONNREFUSED");
    });
    const state = await resolveBackend();

    expect(state.mode).toBe("live");
    expect(state.status).toBe("unreachable");
    expect(state.note).toContain("VITE_API=live");
    expect(getBackendState().mode).toBe("live");
  });

  it("probes only once, however many callers ask", async () => {
    const mock = stubFetch(() => json({ ok: true, runs: 3 }));
    await Promise.all([resolveBackend(), resolveBackend(), resolveBackend()]);
    expect(mock).toHaveBeenCalledTimes(1);
  });
});

describe("getRoundDiff", () => {
  it("fetches the patch from the round diff endpoint, not out of the bundle", async () => {
    const calls: string[] = [];
    stubFetch((url) => {
      calls.push(url);
      if (url === "/api/health") return json({ ok: true, runs: 96 });
      return json({
        run_id: "ds-dgm",
        round: 1,
        stat: {
          round: 1,
          from: "9746711",
          to: "29bf3af",
          files: [{ path: "agent.py", added: 161, removed: 34 }],
          added: 161,
          removed: 34,
        },
        stat_error: null,
        patch: "diff --git a/agent.py b/agent.py\n",
      });
    });

    const diff = await getRoundDiff("ds-dgm", 1);

    expect(calls).toContain("/api/runs/ds-dgm/rounds/1/diff");
    // the bundle is the endpoint the client must NOT be reading the patch from
    expect(calls).not.toContain("/api/runs/ds-dgm");
    expect(diff).toMatchObject({ round: 1, from: "9746711", to: "29bf3af", added: 161, removed: 34 });
    expect(diff?.patch).toContain("diff --git");
  });

  it("resolves the endpoint's 404 to null: no saved patch is an absence, not a failure", async () => {
    stubFetch((url) => {
      if (url === "/api/health") return json({ ok: true, runs: 96 });
      return json(
        {
          error: "diff-not-found",
          status: 404,
          message: "no saved patch for round 0 of run `ds-dgm`",
          run_id: "ds-dgm",
          round: 0,
        },
        404,
      );
    });

    await expect(getRoundDiff("ds-dgm", 0)).resolves.toBeNull();
  });

  it("keeps the patch when the stat file is unreadable, without inventing zeros", async () => {
    stubFetch((url) => {
      if (url === "/api/health") return json({ ok: true, runs: 96 });
      return json({
        run_id: "ds-dgm",
        round: 2,
        stat: null,
        stat_error: "round-2.json is not JSON: Expecting value",
        patch: "diff --git a/x b/x\n",
      });
    });

    const diff = await getRoundDiff("ds-dgm", 2);

    expect(diff?.added).toBeNull();
    expect(diff?.removed).toBeNull();
    expect(diff?.from).toBeNull();
    expect(diff?.patch).toContain("diff --git");
    expect(diff?.stat_error).toContain("not JSON");
  });

  it("reads the fixture bundle's inline patch in fixture mode", async () => {
    stubFetch((url) => {
      if (url === "/api/health") throw new Error("ECONNREFUSED");
      return json({
        run_id: "ds-dgm",
        meta: {},
        points: [],
        verdicts: {},
        diffs: {
          "1": {
            round: 1,
            from: "a",
            to: "b",
            files: [],
            added: 3,
            removed: 4,
            patch: "diff --git a/fixture b/fixture",
          },
        },
        load_problems: [],
      });
    });

    const state = await resolveBackend();
    expect(state.mode).toBe("fixture");
    const diff = await getRoundDiff("ds-dgm", 1);
    expect(diff?.patch).toContain("fixture");
    expect(diff?.added).toBe(3);
  });
});

describe("API error bodies", () => {
  it("surfaces the server's own sentence for a missing run", async () => {
    stubFetch((url) => {
      if (url === "/api/health") return json({ ok: true, runs: 96 });
      return json(
        { error: "run-not-found", status: 404, message: "no directory runs/nope", run_id: "nope" },
        404,
      );
    });

    await expect(getRun("nope")).rejects.toMatchObject({
      kind: "not-found",
      status: 404,
      message: "no directory runs/nope",
    });
  });

  it("classifies a 400 path refusal as bad-request with the server's message", async () => {
    vi.stubEnv("VITE_API", "live");
    stubFetch((url) => {
      if (url === "/api/health") return json({ ok: true, runs: 96 });
      return json(
        { error: "invalid-path", status: 400, message: "path traversal is refused" },
        400,
      );
    });

    await expect(listRuns()).rejects.toMatchObject({
      kind: "bad-request",
      status: 400,
      message: "path traversal is refused",
    });
  });

  it("reports a non-JSON 200 as a parse error rather than a blank screen", async () => {
    vi.stubEnv("VITE_API", "live");
    stubFetch((url) =>
      url === "/api/health" ? json({ ok: true, runs: 96 }) : new Response("<html>", { status: 200 }),
    );

    const error = await listRuns().catch((cause: unknown) => cause);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe("parse");
  });

  it("reports an unreachable API as a network error naming the request", async () => {
    vi.stubEnv("VITE_API", "live");
    stubFetch(() => {
      throw new Error("ECONNREFUSED");
    });

    await expect(listRuns()).rejects.toMatchObject({ kind: "network" });
  });
});
