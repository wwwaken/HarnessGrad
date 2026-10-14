# S6: six-file serial quality-test triage

Worktree: `/tmp/hg-s6`, starting commit `065d29c`. Only the six requested test
files were executed, one pytest process at a time. No full-suite or concurrent
test run was attempted.

## Per-file outcome

Every basetemp below is under `/mnt/20t/xubuqiang/.hg-pytest/`.

| Test file in `tests/quality/` | Verdict | Final isolated result | Basetemp suffix |
| --- | --- | --- | --- |
| `test_verifier.py` | No failure reproduced | 22 passed, 2.88 s | `s6-verifier` |
| `test_unified_budget.py` | No failure reproduced | 3 passed, 15.17 s | `s6-unified-budget` |
| `test_stop_semantics.py` | No failure reproduced | 4 passed, 13.18 s | `s6-stop-semantics` |
| `test_dgm_rule.py` | No failure reproduced | 5 passed, 17.32 s | `s6-dgm-rule` |
| `test_code_metrics.py` | No failure reproduced | 11 passed, 9.71 s | `s6-code-metrics` |
| `test_cli_harness.py` | real: fixture paths; fixed-temp-path contention risk also removed | Before: 2 failed, 4 passed; after: 6 passed, 3.01 s | `s6-cli-harness` |

Total final result: **51 passed**. Serial success does not identify the shared
resource responsible for the first five files' previously reported concurrent
failures. Those historical failures remain unclassified; no contention cause is
claimed without a receipt identifying it.

## One-line verdict for each reproduced failure

- **real** — `test_the_curve_point_prefers_the_declaration_and_records_the_conflict`: the fake CLI was placed at `/tmp/harnessgrad_cli`, hidden by the sandbox, while the example manifest declared a different machine-specific runtime path; the positive token-cost assertion failed with `harness_tokens == 0`.
- **real** — `test_a_cli_outside_usr_is_unreachable_until_the_manifest_declares_it`: declaring a runtime under `/tmp` cannot survive the sandbox's subsequent `/tmp` hide; the declared-path result remained `UNREACHABLE`.

The old fixtures also used fixed paths: `/tmp/harnessgrad_work/pytest-cli`
and `/tmp/harnessgrad_cli` in this worktree. Cleanup recursively deleted the
shared work path. This is a **contention risk (fixed temp path)** between test
processes, identified from the fixture implementation. The race itself was not
reproduced; no concurrent test run was performed.

## Focused fix

`test_cli_harness.py` now allocates a per-test work directory and a sibling fake
CLI directory under pytest's unique external temporary directory. Pytest owns
their lifecycle, so fixture teardown no longer deletes a shared path.

The curve test copies the reference CLI harness into its temporary directory and
sets that copy's `runtime_paths` to the fixture's actual CLI location. The reference
harness and production sandbox code are unchanged. A setup failure explains the
required external basetemp if the CLI fixture would otherwise land under `/tmp`.

All existing correctness assertions remain intact, including the undeclared CLI
being unreachable, the declared CLI becoming reachable, positive token cost,
model identity/conflict reporting, and task-local HOME behavior. No timing
thresholds were changed; no missing dependency was observed.

The successful CLI curve receipt contains two points; H0 records the harness
model `fake-model-1`, source `harness`, and `harness_tokens: 4564`.

## Scope-safe execution

The production integrity snapshot recursively reads `data/`. A temporary Python
audit hook refused opens, directory traversal, and imports of the excluded
adapter. Initial verifier/budget attempts stopped at that guard; those were
scope-setup failures, not product regressions.

To run the complete requested files, a temporary source view copied only permitted
`data/` entries, pruning the excluded file and directory before copying or descent
and excluding bytecode caches. Bubblewrap mounted that view read-only at
`/tmp/hg-s6/data` for pytest and its children. The audit guard stayed enabled.
Integrity snapshots still ran normally over the available source, without code
patches, missing-file suppression, test skips, or changed assertions. The excluded
paths were not read, imported, modified, or executed. This is validation of the
permitted source view, not validation of the excluded adapter.

The command shape for each final run was:

```bash
bwrap --bind / / --dev /dev --proc /proc \
  --ro-bind /tmp/hg-s6/.s6-data-view /tmp/hg-s6/data -- \
  env PYTHONPATH=/tmp/hg-s6/.s6-scope-guard:/tmp/hg-s6 \
  python -m pytest -q tests/quality/test_<name>.py \
  --basetemp=/mnt/20t/xubuqiang/.hg-pytest/s6-<suffix>
```

For both CLI runs the wrapper additionally used
`--tmpfs /tmp --bind /tmp/hg-s6 /tmp/hg-s6` before the data-view mount. This kept
the old fixture's fixed `/tmp` paths in a disposable mount namespace during the
baseline run, rather than touching other worktrees' host paths. The same wrapper
was retained for the successful post-fix run.

The temporary data view and audit hook were removed after validation. Ignored
`.s6-*.log` files in the worktree contain the captured pytest output, including
the CLI baseline and successful serial runs. `git diff --check` passed.
