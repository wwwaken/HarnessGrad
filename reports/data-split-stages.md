# Data namespace split verification

Worktree: `/tmp/hg-ds`, starting at `fdef36a`. All implementation and review
happened here; no integration merge or frozen-receipt execution was performed.
Stage B (`ad25c7d`, `5cb804e`) was already present and is not repeated.

## Stage A

Moved `data/qa/`, `registry.py`, `command_control.py`, and
`command_oracle_harness/` into `data/scaffolds/`. Added documented temporary
module aliases at the old Python paths, including submodules and direct script
entry points. Standalone QA CLI/prediction assets use temporary links, since
existing callers copy their bytes. Adjusted root/discovery paths for the extra
level. No adapter changed. Import-direction exceptions follow the moved files;
the same test file now guards scaffold declarations and private asset directories.
`pinchbench` is explicitly unclassified rather than assumed to be an adapter.

Command (guard included in `test_import_direction.py`):

```sh
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/ds/a tests/quality/test_import_direction.py tests/quality/test_dataset_lint.py tests/quality/test_dataset_blockers.py tests/quality/test_new_dataset.py
```

Exact final output:

```text
........................................................................ [ 78%]
....................                                                     [100%]
92 passed in 42.22s
```

Additional compatibility inspection: old and canonical registry/base modules
have the same identity; publication still returns 28 names; the relocated
command oracle harness exists. `git diff --check` passes.

The first attempt exposed a wrapper root-depth error (fixed) and a missing
pytest basetemp parent (created). A successful intermediate run reported
`92 passed in 51.73s`; the final run above includes the optimized guard.

## Stage C

Rewired all live adapter/platform/tool/test imports and current documentation to
`data.scaffolds.*`, including generator templates and QA verifier materialization.
Deleted every Stage A shim/link and old scaffold path. Added an import guard that
rejects cross-adapter and non-scaffold shared data imports, including relative
imports under the forthcoming `data.datasets.*` namespace. Recorded eval edges
and architecture/import-direction docs follow the canonical files.

Stage B had introduced `data/aggregation.py`, imported by MuSiQue and 2Wiki.
To satisfy the requested scaffold-only shared boundary, that helper also moved
to `data/scaffolds/aggregation.py` in C. Its policy JSON remains at the original
path and its content/aggregation rules are unchanged. This is an import/path
change, not a repeat of Stage B's semantic changes.

Command:

```sh
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/ds/c tests/quality/test_import_direction.py tests/quality/test_dataset_lint.py tests/quality/test_dataset_blockers.py tests/quality/test_new_dataset.py tests/quality/test_adapters.py tests/quality/test_dataset_classes.py
```

Exact output:

```text
........................................................................ [ 53%]
........................sssssssss..............................          [100%]
126 passed, 9 skipped in 187.35s (0:03:07)
```

`git diff --check` passes. Remaining old scaffold import spellings in live
Python source are deliberate negative examples in the import-direction guard.

The supported `legacy/adapters/harnessgrad_domain` bridge also had two registry
imports; those were rewired before closing C. Focused follow-up:

```sh
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/ds/c-legacy tests/quality/test_adapters.py
```

```text
...sssssssss                                                             [100%]
3 passed, 9 skipped in 0.74s
```

## Stage D

Pre-D review used the registered `/tmp/hg-ds` worktree only. Stage C's final
commit is `2e50b5217dae8cbd6d53b84366e46250e792e600`; the integration ref and common
base were `fdef36a7dfe2d219136fbfc76024477c82f77fd5`. Registered worktree heads were
inspected via `git worktree list`; no other worktree, frozen copy, or receipt was
used as a run or merge source. No integration merge was performed.

Moved all 28 adapter modules into `data/datasets/`, plus these 14 reviewed
same-stem asset directories: agentdojo, alfworld, api_bank, appworld,
bird_minidev, ds1000, gaia, jericho, livecodebench, nestful, reasoning_gym,
scienceworld, spreadsheetbench, tau_bench. Added the ordinary datasets package
initializer. There are **zero adapter compatibility shims**. Top-level fixtures
`demo.py`, `probe_set.py`, `broken_service.py`, and `verify_*.py` remain unchanged
in location; the registry resolves those six fixture names explicitly.

Moved `tau_bench_difficulty.json` and `terminal_bench_difficulty.json` beside their
adapters, following the explicit per-dataset sidecar contract in
`tools/task_difficulty.py`. Both are byte-identical; its output path now follows
the new location. Shared schema and aggregation declarations stay at top level.

Updated discovery, registry loaders, taxonomy/lint/blocker tools, schema metadata,
new-dataset generation/templates, UI discovery, dynamic module strings, asset
root calculations, source-attestation paths, tests and current layout docs.
The new guard pins the unchanged **ordered** 28-name publication tuple and checks
canonical imported module identities. Private asset imports cannot cross adapter
boundaries. QA verification copies both package initializers and the canonical
adapter/scaffold hierarchy into the workdir. Stage B's explicit noop and
aggregation contracts are unchanged; no module-name rule was widened.

Asset review used `docs/tau-bench-vendoring.md`: all 210 present files match its
inventory (4 handwritten assets, 33 pinned vendored files, 173 generated files,
0 unclear). The vendored/generated dependency moves together with provenance
and relative paths intact. All **206 vendored/generated files are byte-identical**;
only the handwritten Dockerfile provenance label and verifier documentation
received path spelling updates. No upstream code was reclassified as first-party.

`data/pinchbench/inventory.json` stays untouched at its original path. Its intended
future ownership is still undetermined; it has no published adapter and is an
explicit unclassified exception in the directory guard. Nothing uncertain was
silently moved. Historical `docs/evidence/`, reports, and test fixtures retain
their baseline bytes; historical audits retain baseline paths with a current-layout
note. Old/incomplete run receipts were neither edited nor executed.

Additional review: after normalizing namespace/path spellings and removing
module/function docstrings, 27 adapter executable ASTs match the pre-D sources.
SpreadsheetBench differs only in the parent path needed to locate shared QA
assets. All tracked Python sources parse. The web's AST `load()` discovery has
the same ordered 33-name adapter/fixture result as before D. `git diff --check`
passes. The initial focused run found eight old generated-control paths; after
repair the exact final verification follows.

Blocker command:

```sh
python3 tools/check_dataset_blockers.py
```

Exact output:

```text
{"valid": true, "datasets": 28, "shared_blockers": 8, "historical_records": 11, "production_authorized": false}
```

Focused command:

```sh
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/ds/d tests/quality/test_import_direction.py tests/quality/test_dataset_lint.py tests/quality/test_dataset_blockers.py tests/quality/test_new_dataset.py tests/quality/test_adapters.py tests/quality/test_dataset_classes.py tests/quality/test_dataset_controls.py tests/quality/test_test_scope.py tests/quality/test_qa_control_expectations.py tests/quality/test_aggregation_policies.py
```

Exact output:

```text
........................................................................ [ 32%]
.........................sssssssss...................................... [ 64%]
.s...................................................................... [ 96%]
........                                                                 [100%]
214 passed, 10 skipped in 306.75s (0:05:06)
```

Registry command:

```sh
python3 tools/run_tests.py --registry-only
```

This selects only five cross-dataset files, never the whole suite. Exact output:

```text
scope: registry-wide only; 5/154 files
basetemp: /mnt/20t/xubuqiang/.hg-pytest/harnessgrad-pytest-3vphxry0
parallel lane: 5 files at 32 jobs
exclusive lane: 0 files at 1 job
  ok   test_dataset_blockers.py                                       3.7s  52 passed in 3.45s
  ok   test_dataset_lint.py                                          38.2s  4 passed in 36.29s
  ok   test_dataset_controls.py                                     129.6s  25 passed, 1 skipped in 127.58s (0:02:07)
  ok   test_qa_dataset_contract.py                                  145.6s  133 passed, 12 skipped in 143.75s (0:02:23)
  ok   test_dataset_classes.py                                      156.4s  30 passed in 154.64s (0:02:34)

5 files in 156.4s wall clock (serial measured total 455s)
all files passed
```

No model endpoint or benchmark pilot was launched. All three stage gates pass.
The skipped tests are reported as skips, not counted as passes. Parent review
and integration merging remain outside this worktree-only task.
