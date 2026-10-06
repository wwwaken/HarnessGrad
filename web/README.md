# HarnessGrad web

The frontend for HarnessGrad, stage 5 of the refactor in `docs/refactor_plan.md`: a SPA over the
read API in `web/server/readapi.py`. It **replaced** the 2,467 lines of hand-written vanilla
JS/CSS that lived in `tools/ui/` — those three files, the `tools/screenshot_ui.py` that
photographed them, and their 400 lines of DOM tests were deleted on 2026-10-06, so this is now
the only frontend. It is built around one subject — **comparison and debugging**, not
launching.

The read API exists; the **write** API does not, and the Launch screen says so on the page
rather than pretending. Everything the SPA reads is real recorded runs under `runs/`.

A researcher's questions are *"did this edit help?"*, *"which tasks moved?"*, and *"why is this
number what it is?"*. The layout answers those first: the Compare screen is a top-level
destination, the certification badge qualifies every number before it is read, and a run whose
total score never moved while its passing set did is called out in words rather than left for
the reader to notice.

## Run it

```bash
cd web
pnpm install
pnpm dev            # http://localhost:5273
pnpm build          # tsc --noEmit && vite build
pnpm test           # vitest run
pnpm type-check     # tsc --noEmit
```

`pnpm dev` serves on **5273**, not Vite's default 5173: on this machine another project's Vite
dev server already holds 5173, and `server.strictPort` turns that collision into a startup
error rather than a silent move to a port this README does not name.

The app chooses its backend at runtime. `pnpm dev` proxies `/api` to the read API on
`http://127.0.0.1:8791`: start `python3 web/server/serve.py --port 8791 --runs-root runs`
first for live data, or start nothing and the app falls back to the fixtures. The banner in
the shell always says which source is in use. See [Live vs fixture](#live-vs-fixture).

## Stack

| piece | choice | why |
| --- | --- | --- |
| build | Vite 5 + React 18 + TypeScript 5.9 (strict) | the common core across Dify, Open WebUI and MLflow (`docs/refactor_references.md` §6.2) |
| styling | Tailwind 3 + shadcn/ui (Radix primitives) | tokens in CSS variables, so the light/dark theme is one class on `<html>`, not two component trees |
| server state | TanStack Query 5 | the common core in both React projects studied; retries are off, because a hidden retry turns "the fixture is missing" into a spinner |
| dense tables | TanStack Table 8 | the row model for sorting and filtering; MLflow's precedent |
| charts | **Recharts 2** | see below |
| code/diff view | Monaco (npm package, not CDN) | read-only unified diffs; bundled so an old experiment is readable with no network |
| unit tests | vitest 2 | 107 tests: the pure logic, the fixtures, the API client's mode/endpoint contract, and a server-render smoke test of all five screens |

### Why Recharts, not ECharts

Both have precedent — Dify ships ECharts, MLflow ships Recharts. We picked Recharts for this
UI's actual chart, which is small:

* **The data is small.** A run is tens of rounds with two series and a 95% interval band.
  ECharts' advantages (canvas rendering, WebGL, exotic series types, datasets in the tens of
  thousands of points) are all out of scope here.
* **It composes as React.** Series are components, and their colours come from the same CSS
  variables the rest of the design system uses (`hsl(var(--chart-score))`). The light/dark
  switch therefore needs no chart-theme object and no re-render with different options —
  ECharts requires a registered theme or an option rebuild.
* **The output is inspectable.** Recharts renders SVG in the DOM, so the legend, axis labels
  and tooltip text are real text. ECharts renders to canvas.
* **Cost.** ECharts adds roughly a megabyte and, to tree-shake, requires importing from
  `echarts/core` and registering each chart, renderer and component individually. For two line
  series that is ceremony with no payoff.

**The tradeoff, stated.** If the platform later needs to plot hundreds of runs on one axis, or
a brush-and-zoom data explorer over individual trials, ECharts is the better tool. The
boundary is one file — `src/components/run/curve-chart.tsx` — and its props are already the
series the chart draws.

## Layout

```
web/
  package.json / tsconfig.json / vite.config.ts / tailwind.config.ts    build + tokens
  postcss.config.js / index.html / components.json                      shadcn CLI conventions
  scripts/build_fixtures.py                                             generates the fixtures from ../runs (read-only)
  src/
    types.ts                the record schema, mirrored from harnessgrad/store/schema.py
    lib/
      api.ts                the read-API client: live `/api/...` or fixtures, chosen by a runtime probe
      monaco.ts             Monaco wired to the npm package, 2 languages, no CDN
      theme.ts              light/dark/system, one class on <html>
      format.ts             number/date formatting; a missing number is never "0"
      utils.ts              shadcn's cn()
    logic/                  7 modules + 6 test suites: the pure logic the screens read
      presence.ts           absent vs null vs present — schema.py's three-state rule
      curve.ts              the score/test_rate series builder and flat-score churn detection
      compare.ts            the task-flip diff, the field-by-field record diff, the summary
      certify.ts            the validity/certification badge and the Experiments filters
      launch.ts             the argv/JSON builder and the driver's refusals
      trace.ts              JSONL trace → ordered timeline
      test-support.ts       typed builders for tests
    hooks/
      queries.ts            TanStack Query hooks and query keys (incl. the round-diff query)
      use-backend.ts        the live/fixture banner state, read through useSyncExternalStore
    fixtures/
      urls.ts               where each fixture lives, as a runtime URL
      data/*.json           the fixture records (6 files, 440 KB)
      README.md             provenance: what is verbatim, what is derived, why
    components/
      ui/ (13)              shadcn/ui primitives (button, table, select, tabs, …); only the ones used
      common/ (7)           section, stat, presence-value, states (empty/error/skeleton), code-view
      layout/ (2)           app shell (rail, nav, backend banner) and the theme toggle
      experiments/ (3)      the runs table, its toolbar, the validity summary
      run/ (6)              curve chart, point strip, per-task table, identity panel, round diff, header
      compare/ (5)          run picker, flip summary, task delta table, field diff, candidate diffs
      task/ (2)             verdict panel and the trace timeline
    pages/ (5)              experiments, run-detail, compare, task-detail, launch
    screens.test.tsx        server-renders all five routes over the fixture data
```

~10,000 lines of TS/TSX/CSS/Python across 80 source files, of which ~1,500 lines are the
nine test files. The `ui/` primitives are shadcn-generated (`components.json` is checked in, so
`pnpm dlx shadcn@latest add <name>` regenerates one); the three the app did not use were deleted
rather than shipped as scaffolding.

## The five screens

### 1. Experiments — `src/pages/experiments.tsx`

Every run, as a dense sortable/filterable table. It answers *"which of our runs can I actually
quote?"* — which is why the certification badge is the second column and the score is not the
first.

**Reads:** `certify()` in full (`run_id`, `points`, `rounds`, `valid`, `certified`, `problems`,
`notes`, `tampered`, `platform_content_sha`, `final_score`) joined with `run_meta.run_id`,
`.agent_model`, `.agent_backend`, `.harness`, `.dataset`, `.improver`, `.mode`,
`.wall_clock_s`, `.platform.content_sha`, and each run's last curve point for `score`,
`test_rate` and `timestamp_utc`.

### 2. Run detail — `src/pages/run-detail.tsx`

The curve (**score and `test_rate` as two series on two axes**), the per-task table for the
selected round, the candidate diff for that round, and the run's identity/config/cost.

**Reads:** `run_meta` — `run_id`, `harness`, `dataset`, `agent_model`, `agent_backend`, `mode`,
`trials`, `workspace`, `sandbox.{active,plan_version,detail}`, `platform.{content_sha,git_sha,dirty}`,
`method_entrypoint`, `jobs`, `wall_clock_s`. Curve points — `round`, `score`, `score_ci95`,
`test_rate`, `test_rate_n_tasks`, `tests_passed`, `tests_total`, `per_task`,
`per_task_test_rate`, `n_scored`, `n_passed`, `n_invalid`, `n_harness_failed`, `score_kind`,
`side`, `timestamp_utc`, `kept_round`, `kept_score`, `startup_failure`, `tampered`, `invalid`,
`harness_failed`, `edit_kind`, `label`, `measured_by_platform`, `identity.{harness_name,
harness_version,harness_sha,run_mode,framework_version,agent_model,agent_backend,
agent_model_source,method,improver,skill_sha,harness_config}`, `env.{kind,image_digest,
placement,network,seed,harness_runtime}`, `sampling.{policy,selected_within,task_ids,
selection_basis_round}`, `cost.{harness_tokens,harness_model_calls,method_generation_tokens,
env_generation_tokens,evaluation_trials,wall_clock_s}`. Round verdicts and round diffs.

### 3. Compare — `src/pages/compare.tsx`

The most important screen. Two runs, two rounds (each side defaults to its own last measured
round), and in order: the headline deltas and passing-set movement; a movement chip per task;
small-multiple curves; the per-task delta table with `test_rate` change and each side's verdict
summary; the two records diffed field by field; and both candidate patches (side by side, or
as a patch-versus-patch diff).

The selection lives in the URL (`?left=ds-dgm&right=ds-rrsi&leftRound=0&rightRound=2`), so a
comparison can be linked into a report.

**Reads:** both runs' selected points (`per_task`, `per_task_test_rate`, `score`, `test_rate`,
`n_scored`) and their identity blocks; both rounds' verdicts for the `detail` column; both
rounds' `diffs/round-<n>.patch`; `run_meta.platform.content_sha` for the field diff.

### 4. Task detail — `src/pages/task-detail.tsx`

One task's verdict and its trace, side by side. The trace is a **timeline of steps**, not
JSONL: model replies, commands with their exit codes and outputs, output clips, finish/repeat
nudges, submit attempts and duplicate keys, in the order the harness produced them. A "raw
events" tab keeps the JSONL reachable so the rendering can be checked against the record.

**Reads:** `verdicts/round-<n>/<task>.json` — `task_id`, `round`, `score`, `kind`, `passed`,
`detail`, `tests.{passed,failed,skipped}`, `harness.{exit_code,stderr}`. `round<n>_traces/
<task>.jsonl` — `harness_identity`, and the event kinds `step`+`reply`+`model_ms`,
`step`+`command`+`exit`+`command_ms`+`output`, `output_clipped`+`shown`, `finish_nudge`,
`repeat_nudge`, `submitted`/`missing`/`submit_rejected`, `duplicate_keys`, `wall_clock_s`,
`usage`. Plus the point's `per_task[task]`, `per_task_test_rate[task]` and
`identity.harness_sha`, and the round's patch.

### 5. Launch — `src/pages/launch.tsx`

A form that configures a run and produces **the argv and the JSON a future API would take**. It
does not submit anywhere. It reproduces the driver's real refusals (an unsafe `--run-id`, an
eval side without `--from-run`) and warns about the things that change what a number means
(`--trials`, `--jobs`, the training side, `--no-sandbox`).

Fields whose value reaches a run through `.env`/`HG_*` are in their own panel, marked `env`,
with the environment variable named and only whether it is set (never a secret's value).
`--mode` is never emitted: `driver.py --help` says it is "DEPRECATED and ignored: there is one
engine", and emitting it would imply a choice that does not exist.

**Reads:** `base_harness/*/harness.json` (harness names), `data/*.py` (dataset names),
`improvers/improvers.json` (improver names and the default), `driver.py --help` (flag text),
`.env` (variable names and whether they are set). It reads no part of the record schema; it
produces the fields that later appear in `run_meta` and the curve points.

## Live vs fixture

Every screen fetches through `src/lib/api.ts` and nothing else. Which backend it reads is
decided **at runtime**, because the point of the fixture fallback is that a demo with no
server still works:

| `VITE_API` | `/api/health` | what you get |
| --- | --- | --- |
| unset / `auto` | answers | **live** — every run under `runs/`, banner says `Live API · N run row(s)` |
| unset / `auto` | unreachable | **fixtures** — the curated subset, banner names the failure |
| `fixture` | not probed | **fixtures**, always |
| `live` | not used to fall back | **live**, and requests fail visibly when the API is down |

`resolveBackend()` runs the `/api/health` probe once on startup (memoized, `use-backend.ts`
re-renders the banner when it resolves); every data function awaits it, so the first request
already goes to the right place. `VITE_API` is a build-time *preference*, not a bake-in: a
`pnpm build` from either setting still works with the server absent.

`pnpm dev` proxies `/api` to `http://127.0.0.1:8791` (`vite.config.ts`), and the built SPA is
served by `serve.py` from the same origin as `/api`, so no CORS and no base URL are needed in
either mode. `VITE_API_BASE` can point at another host if one is ever wanted.

**How to tell which mode is active.** The shell's header shows a coloured badge and one
sentence (`Live API` / `Fixtures` / `Live API (unreachable)` / `Checking…`), and the rail's
footnote repeats it. There is no configuration in which a fixture number is shown without the
banner saying so.

### Live mode is not the fixture contract

A live run directory can be **mid-write**, so the API and the client keep three distinctions:

* a run with no `curve.jsonl` (`runs/full-a`, `runs/full-b`) is a legitimate row with
  `points: 0` and a `no curve.jsonl` problem — rendered as `not measured`, never hidden;
* `test_rate` absent from a point (every run before 2026-10-05) reads as *not recorded*
  through `logic/presence.ts`, never as `0.000`; the Experiments cell and the curve both
  leave it a gap;
* an unreadable file becomes a `*_problems` string on the response, which the run detail
  renders as a "Problems reading this run" section; a `404` (run not found, no saved patch)
  and a `400` (refused path) surface through `ErrorState`, not a blank page.

Fixtures are **fetched rather than imported** on purpose: the async, fallible shape is the
shape the real client has, so loading skeletons and error states are exercised. They are a
small, real subset of `runs/`, generated by `scripts/build_fixtures.py` and documented in
`src/fixtures/README.md`. Certify results come from the platform's own
`tools/validate_run.py --json`, so they cannot drift from the authority. The fixture bundles
still ship the round patch inline *beside* the stat; the live API keeps them apart, which is
why `getRoundDiff` branches on the mode.

**Nothing in `web/` writes anywhere.** The read API is read-only and the SPA only reads.

### The read API contract

`web/server/` implements the six endpoints below (`GET /api/health` is the probe; the other
five are the data); see `web/server/README.md`. The record types (`CurvePoint`, `RunMeta`,
`Verdict`, `RoundDiff`) mirror `harnessgrad/store/schema.py` and the files it certifies; the
endpoint envelopes (`RunSummary`, `RunBundle`, `TaskPage`, `LaunchOptions`) are the client's
contract with the server.

| # | endpoint | returns | notes |
| --- | --- | --- | --- |
| 1 | `GET /api/runs` | `RunSummary[]` | `certify(run_dir)` for every run, joined with `run_meta.agent_model`, `.agent_backend`, `.harness`, `.dataset`, `.improver`, `.mode`, `.wall_clock_s` and the last point's `score`, `test_rate`, `side`, `score_kind`, `timestamp_utc`. `certify()` returns none of the join fields, and it returns no timestamp at all, so the API supplies one (the last point's `timestamp_utc`, or `run_meta`'s mtime) and names the source in `timestamp_source`. A directory with no `run_meta.json` must still return a row (`meta_error` set), because "unreadable" is a state the screen renders. |
| 2 | `GET /api/runs/:id` | `RunBundle` | `meta`, the full `points` list, `verdicts` as `round -> task -> Verdict`, and `diffs` as `round -> stat` — **statistic only**. Traces are **not** here. A run with no `curve.jsonl` returns `points: []` and a `load_problems` entry, not a 404. |
| 3 | `GET /api/runs/:id/rounds/:n/diff` | `{stat, patch}` | the saved `diffs/round-<n>.json` and `round-<n>.patch`. The bundle carries the stat and this endpoint the patch, so a bundle stays small; `src/types.ts:RunBundle.diffs` is `RoundDiffStat` and cannot be read for a patch. A round with no saved patch returns 404, which `getRoundDiff` resolves to `null` and the UI renders as an explicit absence (round 0 has no diff by construction). A malformed stat still serves the patch, with `stat: null` and a `stat_error`. |
| 4 | `GET /api/runs/:id/rounds/:n/tasks/:task` | `TaskPage` | the verdict file, the parsed `round<n>_traces/<task>.jsonl` (one object per line, file order), the round diff, and separate `verdict_problems` / `trace_problems`. A task that was not scored in the round returns `verdict: null` — absence, not a zero. |
| 5 | `GET /api/launch/options` | `LaunchOptions` | harnesses (directories with a `harness.json`), datasets, sampling policies, improver names and default, and `env_derived`: for each `HG_*`/`.env` variable, the flag it backs, whether it is set, and its value **only** for non-secret variables. |
| 6 | `GET /api/health` | `{ok, runs}` | the startup probe. `resolveBackend()` reads it to choose live vs fixture; it is not one of the six the screens render from. |

### Write API the Launch screen implies (not built)

`POST /api/runs` should accept the `LaunchRequest` body the form renders — `run_id`, `harness`,
`dataset`, `sampling`, `rounds`, `trials`, `jobs`, `improver`, `improver_model`,
`method_entrypoint`, `tasks[]`, `side`, `from_run`, `from_round`, `seed`, `sandbox`,
`work_root` — refuse exactly what `driver.py` refuses, and answer `202` with a run id plus a
stream of the run's events. `agent_model`, `agent_backend` and the timeouts have **no CLI flag
today**: they are read from `.env`, which is why the form shows them as environment-derived
rather than as choices. A write API that wanted them per-request would have to add flags to the
driver first.

## What this build does not do

* **No live progress.** Launching, cancellation, and a progress stream are out of scope: there
  is no write API and no event stream.
* **No artifact browsing.** `run_meta.workspace` is displayed, but the checkpointed git history
  and `tools/export_harnesses.py` are not reachable from the UI.
* **No cross-run aggregation.** Summing cost across runs, or plotting many curves on one axis,
  is deliberately absent: `docs/refactor_references.md` §7 makes each curve point's environment
  a per-point fact, so two curves with different `env.image_digest` values must not share an
  axis without saying so. The Compare screen uses small multiples for this reason.
* **No trace search.** Tracing is per task; there is no full-text search across traces.
* **No pagination or virtualisation.** Fine for the ~90 runs on disk and for a run's tens of
  points. A read API returning thousands of runs would need both, and the runs table already
  goes through TanStack Table's row model, which is where they would attach.
* **No auth.** A local research instrument, not a multi-tenant service.

## Verification

```bash
cd web
pnpm install     # exit 0
pnpm type-check  # no output: no TypeScript errors
pnpm test        # 9 files, 107 tests passed
pnpm build       # tsc --noEmit && vite build, exit 0
pnpm dev         # VITE v5.4.21 ready on http://localhost:5273/
```

Live mode, end to end — the two processes are started together and both stopped again:

```bash
# from the repository root
python3 web/server/serve.py --port 8791 --runs-root runs &
cd web && pnpm dev &
curl -s http://127.0.0.1:5273/api/health             # {"ok": true, "runs": 96}
curl -s http://127.0.0.1:5273/api/runs | python3 -c \
  'import json,sys; print([r["run_id"] for r in json.load(sys.stdin) if r["run_id"] in ("full-a","full-b")])'
# ['full-a', 'full-b']
kill %1 %2
```

The banner reads `Live API · 96 run row(s)` while both are up, and `Fixtures` once the API is
gone. `pnpm dev` is started and stopped on demand; nothing in this directory leaves a
listening socket behind.
