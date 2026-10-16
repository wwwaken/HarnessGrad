# Fixtures

Stand-ins for the read API in `web/server/`, used when it is not running: the SPA probes
`GET /api/health` at startup and only falls back to these files when nothing answers (see
[Live vs fixture](../README.md#live-vs-fixture) in the web README). They are
**generated**, not hand-written, and the generator is checked in so they can be audited:

```bash
cd web && python3 scripts/build_fixtures.py     # reads ../runs/ read-only
```

`build_fixtures.py` reads the real run tree and writes six files into `data/`. Nothing outside
`web/` is touched.

| file | source | size |
| --- | --- | --- |
| `runs-index.json` | 14 curated runs from `runs/`, validated by the platform's own `tools/validate_run.py --json` | 39 KB |
| `run-ds-dgm.json` | `runs/ds-dgm` — every point, every verdict, both saved round patches inline (the live API serves a patch from `GET /api/runs/:id/rounds/:n/diff`, not from the bundle) | 121 KB |
| `run-ds-rrsi.json` | `runs/ds-rrsi` — the compare partner | 164 KB |
| `task-ds-dgm-r0-cobol-modernization.json` | verdict + full trace for one task | 85 KB |
| `task-ds-dgm-r0-fix-git.json` | verdict + full trace for one task | 25 KB |
| `launch-options.json` | the harnesses, datasets and improver names actually on this machine, plus which fields come from `.env` | 7 KB |

The whole directory is ~444 KB. The real `runs/` tree is tens of megabytes and is not
committed here.

## What is verbatim, and what is derived

**Verbatim.** `certify()` output (via the platform's CLI, so it cannot drift), every curve
point, every verdict, every `detail` string on the two featured task pages, both traces, and
both `.patch` files. Trimming, where it happens, is stated in the file:

* per-point `env.variants` and `env.harness_runtime[].packages` are dropped (they are
  hundreds of kilobytes of image and wheel manifests no screen reads); the pinned
  `image_digest`, `placement`, `network` and the runtime `source`/`python` survive;
* each point's `split` (89 task ids, identical on every point) is dropped — `run_meta`
  carries it once;
* `candidate_code` is dropped (a static-analysis report with no screen yet);
* in the two bundles, verdict `detail` is cut at 1200 characters with a marker that says how
  much was dropped. The two featured task pages keep `detail` whole;
* trace `reply` and `output` strings are cut at 6000 characters with a marker. The base
  harness's own `output_limit` is 4000 and its context budget is 60000, so a 6000-character
  cut never hides something the model could have seen.

**Derived, and this matters.** No run on disk carries `test_rate`, `per_task_test_rate`,
`tests_passed`, `tests_total` or `verdict.tests`: those fields were added on 2026-10-05
(stage 0) and every recorded run predates them. Without them, the second curve series would
be empty on every screen — precisely where stage 0's whole argument lives (a binary score
cannot resolve the effect).

So the generator recovers them from the data that *is* on disk:

* `verdict.tests` is parsed out of the verdict's own `detail` string, which is where
  `eval/run/runner.py:_test_report_failures` got it in the first place
  (`check_report … (3 passed)` → `{passed: 3, failed: 0}`);
* `point.test_rate`, `point.per_task_test_rate`, `point.tests_passed` and
  `point.tests_total` are computed from those tallies with the same formula as
  `eval/run/runner.py:test_rate_of` — `passed / (passed + failed)`, skipping tasks whose check
  reported no tally, treating `None` as "not zero".

`src/logic/fixtures.test.ts` runs the real logic over these files, so a drift between the
generator and the schema fails the test suite rather than a screen.

## Which runs are in the index, and why those

The index is curated for **coverage of the badge states**, not for score:

| run | state it demonstrates |
| --- | --- |
| `ds-dgm`, `ds-rrsi`, `codex-local-dgm`, `v10-dgm`, `handfix-1` | `valid`, not `certified` — the common case for a run recorded before stage 1 |
| `smoke-a-noimprover`, `smoke-b-noimprover` | `certified` — the record names its platform content hash |
| `smoke-testrate` | `valid`; the run stage 0 was verified against |
| `smoke-a`, `smoke-b` | `invalid` — `measured_by_platform` is not true, so the numbers are claims |
| `codex-task-dgm`, `v8-rrsi` | `invalid` in a different way: no `curve.jsonl` at all |
| `noise-1`, `B2-noop` | small runs, for the round/point columns |

`ds-dgm` and `ds-rrsi` are the compare pair because they are the platform's own headline
case: both keep `score = 0.1` across rounds while the set of passing tasks changes under them.
