# `web/server/` — the HarnessGrad read API

A small, **read-only**, dependency-free HTTP server (Python standard library only)
that serves the six endpoints the SPA in `web/src/` is written against, plus the
built SPA itself.

```bash
# from the repository root
python3 web/server/serve.py --port 8791 --runs-root runs
# -> HarnessGrad read API on http://127.0.0.1:8791
#    runs-root: /…/HarnessGrad/runs
#    web-dist:  /…/HarnessGrad/web/dist
```

Options: `--host` (default `127.0.0.1`), `--port` (default `8791`),
`--runs-root` (default `<repo>/runs`), `--web-dist` (default `<repo>/web/dist`).
Use `python3 web/server/serve.py --help` for the list.

## It never writes

**The API is an observer of a tree that a run may be appending to while it
serves.** Every file under `runs/` is opened for reading only; nothing is
created, moved, renamed or deleted. `web/server/` does not appear in
`eval/run/integrity.py:PLATFORM`, so building and running it cannot invalidate a run.

Two implementation rules enforce the read-only property:

* the platform's `harnessgrad/store/schema.py` is **imported**, never copied —
  `certify()` and `read_curve()` are the authority for what a run directory is;
* `sys.dont_write_bytecode = True` (plus `python3 -B` when probing the driver)
  keeps the server from leaving even a `__pycache__` entry in the platform tree.

A file that is half-written — a `curve.jsonl` line without its closing brace, a
`run_meta.json` captured mid-write, a truncated verdict — becomes a `problems`
string on the response. It is never a 500 and never a traceback.

## Files

| file | lines | what it is |
| --- | --- | --- |
| `serve.py` | 284 | the HTTP server: CLI, routing, path guards, JSON errors, SPA fallback |
| `readapi.py` | 431 | read-only access to `runs/`: summaries, bundles, diffs, task pages |
| `launch.py` | 311 | `GET /api/launch/options`, `.env` parsing, secret redaction |
| `README.md` | this file | how to run it, the endpoints, the read-only rule |

## The six endpoints

### 1. `GET /api/runs`

`RunSummary[]`, one row per subdirectory of the runs root. Every field
`certify(run_dir)` returns, joined with `run_meta.{agent_model, agent_backend,
harness, dataset, improver, mode, wall_clock_s}` and the **last** curve point's
`{score, test_rate, side, score_kind, timestamp_utc}`.

`certify()` returns no timestamp of its own, so the API supplies one and says
where it came from: `timestamp_utc` is the last point's `timestamp_utc` when the
curve has one, otherwise the run directory's mtime, and `timestamp_source` is
`"curve"` or `"run_meta_mtime"` accordingly.

**Reads:** `runs/*/curve.jsonl`, `runs/*/run_meta.json`, and the directory inode
(for the mtime fallback).

```console
$ curl -s http://127.0.0.1:8791/api/runs | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))'
96
$ curl -s http://127.0.0.1:8791/api/runs | python3 -c 'import json,sys; print(json.dumps([r for r in json.load(sys.stdin) if r["run_id"]=="full-a"][0], indent=1))'
{
 "certify": {
  "run_id": "full-a",
  "points": 0,
  "rounds": [],
  "valid": false,
  "certified": false,
  "problems": ["no curve.jsonl: nothing was measured"],
  "notes": ["run_meta: no `rounds_measured` (optional)"],
  "tampered": [],
  "platform_content_sha": "eef1914b…92cc",
  "final_score": null
 },
 "run_id": "full-a",
 "agent_model": "qwen3.5-9b-local",
 "agent_backend": "openai",
 "harness": "loop",
 "dataset": "terminal_bench",
 "improver": "codex",
 "mode": "unified",
 "side": null,
 "score_kind": null,
 "last_score": null,
 "last_test_rate": null,
 "wall_clock_s": null,
 "timestamp_utc": "2026-10-05T18:33:41Z",
 "timestamp_source": "run_meta_mtime",
 "meta_error": null
}
```

A directory with no `run_meta.json` is still a row: `meta_error` is set and the
join fields are `null` (`runs/guard-probe` behaves this way). A directory with no
`curve.jsonl` is `points: 0`, not a 404 — `runs/full-a` and `runs/full-b` were
mid-write and served fine. Files directly under `runs/` (for example
`runs/sensitivity-report.json`) are not runs and are not rows.

### 2. `GET /api/runs/<id>`

`{meta, points[], verdicts: {round: {task: Verdict}}, diffs: {round: stat},
load_problems[]}`. **Traces are not included** — they are tens of megabytes and
the Task screen fetches one task at a time. The bundle carries the diff *stat*
only; the patch has its own endpoint.

**Reads:** `run_meta.json`, `curve.jsonl`, `verdicts/round-<n>/*.json`,
`diffs/round-<n>.json`.

```console
$ curl -s http://127.0.0.1:8791/api/runs/ds-dgm | python3 -c 'import json,sys; b=json.load(sys.stdin); print(len(b["points"]), sorted(b["verdicts"]), sorted(b["diffs"]), b["load_problems"])'
3 ['0', '1', '2'] ['1', '2'] []
```

A run with no `curve.jsonl` returns `points: []` and a `load_problems` entry
(`"no curve.jsonl: nothing was measured"`), never a 404.

### 3. `GET /api/runs/<id>/rounds/<n>/diff`

`{stat, patch}`. 404 with a JSON body when no patch was saved — round 0 has no
diff by construction, and a round whose patch has not been written yet is the
same absence. A malformed `round-<n>.json` yields `stat: null` plus `stat_error`
while still serving the patch that exists.

**Reads:** `diffs/round-<n>.json`, `diffs/round-<n>.patch`.

```console
$ curl -s http://127.0.0.1:8791/api/runs/ds-dgm/rounds/1/diff \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(sorted(d), len(d["patch"]), d["stat"]["files"])'
['patch', 'round', 'run_id', 'stat', 'stat_error'] 14350 [{'path': 'agent.py', 'added': 161, 'removed': 34}]
$ curl -s -w ' HTTP %{http_code}\n' http://127.0.0.1:8791/api/runs/ds-dgm/rounds/0/diff
{"error": "diff-not-found", "status": 404, "message": "no saved patch for round 0 of run `ds-dgm`", "run_id": "ds-dgm", "round": 0} HTTP 404
```

### 4. `GET /api/runs/<id>/rounds/<n>/tasks/<task>`

`{verdict|null, trace[], diff|null, verdict_problems[], trace_problems[]}`.
`verdict: null` means **the task was not scored in this round** — an absence,
never a zero — and `verdict_problems` says why. `trace` is the parsed JSONL, one
object per line, in file order. `diff` is the full round diff (stat + patch) for
context, or `null` when the round has none.

**Reads:** `verdicts/round-<n>/<task>.json`,
`round<n>_traces/<task>.jsonl`, `diffs/round-<n>.{json,patch}`.

```console
$ curl -s http://127.0.0.1:8791/api/runs/ds-dgm/rounds/0/tasks/large-scale-text-editing \
  | python3 -c 'import json,sys; t=json.load(sys.stdin); v=t["verdict"]; print(v["task_id"], v["score"], v["passed"], len(t["trace"]))'
large-scale-text-editing 0.0 False 71
```

A task that was never scored returns HTTP 200 with `"verdict": null` and a
`verdict_problems` entry; a missing trace file is an empty `trace` plus a
`trace_problems` entry, not a 404.

### 5. `GET /api/launch/options`

`{harnesses, datasets, samplings, improvers, default_improver, env_derived}`.
Every `env_derived` entry is `{flag, env_var, value|null, set, secret, note}`.

* harnesses ← directories under `base_harness/` holding a `harness.json`;
* datasets ← `data/datasets/*.py` plus top-level fixture modules modules declaring a top-level, zero-argument `load()`
  (`data/scaffolds/registry.py` declares `load(name)` and is the loader, so it is not a
  dataset);
* improvers / `default_improver` ← `improvers/improvers.json`;
* flags and the environment-variable notes ← `python3 -B driver.py --help`;
* `set`/`value` ← the process environment first, then `.env`.

**A secret's value is never returned.** Redaction is name-based (`KEY`, `TOKEN`,
`SECRET`, `PASSWORD`, `PASSPHRASE`, `CREDENTIAL`) and value-shaped (`sk-…`,
`ghp_…`, `AKIA…`, …), and a redacted variable still reports `set: true,
secret: true` so the form can say "a credential is present" without seeing it.
The response also carries the extra keys the SPA's `LaunchOptions` type reads —
`modes`, `sides`, `improver_names`, `flag_help`.

**Reads:** `base_harness/*/harness.json`, `data/datasets/*.py` plus top-level fixture modules (parsed with `ast`, never
imported), `improvers/improvers.json`, `driver.py --help` (subprocess),
`.env` and the process environment.

```console
$ curl -s http://127.0.0.1:8791/api/launch/options | python3 -c 'import json,sys; d=json.load(sys.stdin); print(sorted(d)); print(d["harnesses"]); print(d["datasets"]); print(d["improvers"], d["default_improver"]); print([f for f in d["env_derived"] if f["secret"]])'
['datasets', 'default_improver', 'env_derived', 'flag_help', 'harnesses', 'improver_names', 'improvers', 'modes', 'samplings', 'sides']
['cli_agent', 'codex_agent', 'loop', 'loop_plain', 'loop_rrsi_parse', 'oracle']
['broken_service', 'demo', 'probe_set', 'terminal_bench', 'verify_demo', 'verify_exec', 'verify_service']
['deepseek', 'codex', 'local'] deepseek
[{'flag': '(no flag; environment only)', 'env_var': 'HG_AGENT_API_KEY', 'value': None, 'set': True, 'secret': True, 'note': 'Credential for the agent endpoint; recorded only as present or absent.'}, …]
```

`verify_demo`, `verify_exec` and `verify_service` are listed because they are
`data/datasets/*.py` plus top-level fixture modules datasets like any other; the fixtures in `web/src/fixtures/` ship a
smaller curated set, which is a fixture choice, not an API rule.

### 6. `GET /api/health`

`{"ok": true, "runs": <count>}`, where the count is the number of run
directories under the configured runs root.

```console
$ curl -s http://127.0.0.1:8791/api/health
{"ok": true, "runs": 96}
```

## Path safety and error shape

* A run id or task id is a **single path component**: letters, digits, `_`, `-`
  and `.`, not starting with a dot, never containing `..`, `/` or `\`. This is
  checked *before* any path is built.
* Any `.` or `..` path segment — plain or percent-encoded — is refused with
  `400 {"error": "invalid-path", …}` before routing, so
  `/api/runs/../driver.py` never reaches the filesystem.
* An unknown run is `404 {"error": "run-not-found", …}`; an unknown endpoint is
  `404 {"error": "not-found", …}`; a non-numeric round is
  `400 {"error": "invalid-round", …}`. Every error body is JSON.
* Responses are `Cache-Control: no-store`: the tree changes under the reader.

## The built SPA

Any path that is not `/api/...` is served from `web/dist` when that directory
exists: a real file is returned with its content type, and anything else falls
back to `web/dist/index.html` so client-side routes such as `/runs/ds-dgm`
work. When `web/dist` is absent the server answers `404 {"error":
"spa-not-built", …}` and the `/api/` endpoints keep working.

```console
$ curl -s -o /dev/null -w '%{http_code} %{content_type}\n' http://127.0.0.1:8791/runs/ds-dgm
200 text/html; charset=utf-8
```

## Verify it

```bash
python3 web/server/serve.py --port 8791 --runs-root runs &
curl -s http://127.0.0.1:8791/api/health
curl -s http://127.0.0.1:8791/api/runs | head -c 400
curl -s http://127.0.0.1:8791/api/runs/ds-dgm
curl -s http://127.0.0.1:8791/api/runs/ds-dgm/rounds/0/tasks/large-scale-text-editing
curl -s http://127.0.0.1:8791/api/launch/options
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8791/api/runs/definitely-not-a-run   # 404
curl -s --path-as-is -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8791/api/runs/../driver.py  # 400
kill %1
```
