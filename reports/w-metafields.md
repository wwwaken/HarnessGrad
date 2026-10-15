# w-metafields: failures not reproduced; zero-state regression strengthened

## Observed result and limits

**FOUND:** Both requested files passed before any edit in this worktree: `5 passed in 18.11s` and `3 passed in 22.39s`. After the test-only changes they report `5 passed in 18.51s` and `3 passed in 23.20s`. Sources: `reports/w-metafields-evidence/before-dgm-pytest.txt:2`, `before-budget-pytest.txt:2`, `after-dgm-pytest.txt:2`, and `after-budget-pytest.txt:2` (all under the same evidence directory). Exact commands and output are in `reports/w-metafields-validation.txt`.

**UNKNOWN:** The prompt's historical `1 failed, 4 passed` and `1 failed, 2 passed` executions were not retrieved. Their revision, environment, full output, return code and receipts are unobserved. They cannot honestly be presented as this worker's before results. The observed baseline metadata identifies revision `be29c8514d8f9373a2ebe30ba42c62df1f73f59c` and a clean platform (`reports/w-metafields-evidence/before-dgm-batch-run_meta.json:133`).

**ABSENT in the enumerated executed scope:** No pytest failures in the four individual-file executions listed above; no non-zero exits or timeouts in the three direct invocations recorded in `direct-batch-receipt.json:35`, `direct-single-receipt.json:35`, and `direct-kept-receipt.json:35`. This does not establish absence across other revisions, environments or suites.

## Failure 1: mechanism and actual metadata

Classification for the observed run: **(c) omission not reproduced**. It is neither observed `steps_done=None` nor an observed missed final write. The original failure remains UNKNOWN.

The actual code says `steps_done, step_attempts = 0, 0` (`harnessgrad/loops/mode_a.py:287`), breaks after three unsuccessful attempts (`harnessgrad/loops/mode_a.py:302`), and finally calls `_write_run_meta(` with `steps_measured=steps_done,` (`harnessgrad/loops/mode_a.py:665`, `:689`). Its counter advances through `steps_done += 1` (`harnessgrad/loops/mode_a.py:627`). There is no assignment of `None` to that counter in the inspected file; inspection command: `rg -n 'steps_done|steps_measured' harnessgrad/loops/mode_a.py` (output retained in the validation file).

The writer documents, verbatim: "A field passed as `None` is left unchanged rather than written: `None` is how a" and implements `existing.update({k: v for k, v in fields.items() if v is not None})` (`harnessgrad/records.py:437`, `:452`). Integer zero survives that filter. `_write_run_meta` and its merge semantics were not modified (review the explicit production-file diff command in the validation file).

Observed **before** JSON keys, verbatim names sorted by `json.dumps(sorted(meta))` (`reports/w-metafields-evidence/before-dgm-batch-run_meta.json:1`):

```json
["acceptance_rule", "agent_backend", "config", "curve_drawn", "dataset", "env", "failed_steps", "final_score", "framework_version", "harness", "jobs", "method_entrypoint", "mode", "nominated", "oracle_source", "platform", "platform_root", "rounds_measured", "run_id", "sampling_policy", "sandbox", "split", "split_declared", "split_sha", "split_source", "steps_measured", "steps_truncated", "trajectory_shape", "trials", "wall_clock_s", "work_root", "workspace"]
```

Observed **after** JSON keys, same extraction (`reports/w-metafields-evidence/after-dgm-batch-run_meta.json:1`):

```json
["acceptance_rule", "agent_backend", "config", "curve_drawn", "dataset", "env", "failed_steps", "final_score", "framework_version", "harness", "jobs", "method_entrypoint", "mode", "nominated", "oracle_source", "platform", "platform_root", "rounds_measured", "run_id", "sampling_policy", "sandbox", "split", "split_declared", "split_sha", "split_source", "steps_measured", "steps_truncated", "trajectory_shape", "trials", "wall_clock_s", "work_root", "workspace"]
```

Both complete JSON files are retained. Both contain `"steps_measured": 0`, `"steps_truncated": 0`, and `"rounds_measured": 1` (`before-dgm-batch-run_meta.json:164`, `after-dgm-batch-run_meta.json:164`, in the evidence directory). The one round is H0, not a child: the baseline events record three connection errors, exhaustion of the attempt budget, and a results curve containing only round zero (`reports/w-metafields-evidence/before-dgm-batch-events.jsonl:52`, `:56`, `:60`, `:62`, `:64`). Thus "zero" here means zero candidate steps; the baseline itself was measured.

The added assertions require successful driver completion, an explicit zero count, and a curve containing only H0 (`tests/quality/test_dgm_rule.py:196`, `:209`). Existing assertions remain. A production record fix is not claimed: the record already represents zero correctly in this checkout.

## Failure 2: full direct captures and classification

The reproduction helper imports the exact `_BATCH_METHOD` / `_KEEPING_METHOD` source from the test, invokes the same driver options and inherited environment expression `{**os.environ, 'HG_AGENT_BACKEND': 'mock'}`, and retains full stdout and stderr (`reports/w-metafields-evidence/reproduce.py:24`). Only the run IDs, temporary roots, and generated method paths differ, to keep every direct run fresh. The parent invocation was:

```sh
TMPDIR=/tmp/metafields-tmp python3 reports/w-metafields-evidence/reproduce.py /mnt/20t/xubuqiang/hg-work/metafields > /mnt/20t/xubuqiang/hg-work/metafields/direct-reproduction.txt 2>&1
```

Exact argv arrays, cwd, timeout and explicit environment overrides are retained per invocation:

- `reports/w-metafields-evidence/direct-batch-receipt.json:2`: rounds 5, exit 0, no timeout; full output in `direct-batch-stdout.txt:1` and `direct-batch-stderr.txt:1`.
- `reports/w-metafields-evidence/direct-single-receipt.json:2`: rounds 3, exit 0, no timeout; full output in `direct-single-stdout.txt:1` and `direct-single-stderr.txt:1`.
- `reports/w-metafields-evidence/direct-kept-receipt.json:2`: rounds 4, exit 0, no timeout; full output in `direct-kept-stdout.txt:1` and `direct-kept-stderr.txt:1`.

All abbreviated filenames in this list are under `reports/w-metafields-evidence/`. Corresponding complete run_meta files are also retained. Environment overrides and TMPDIR are exact; the entire inherited process environment was not serialized because it may contain credentials. Effective driver configuration, including credential presence rather than secret values, is in each retained run_meta (`direct-batch-run_meta.json:16`, and corresponding single/kept files).

**Classification:** Current reproduction is successful, so neither a driver defect nor a timeout defect is demonstrated. The historical cause is UNKNOWN; there is no full *failing* output to supply from these successful executions. No output was invented or truncated.

One distinction is established: this test uses `subprocess.run(..., timeout=900)` without catching `TimeoutExpired` before its return-code assertion (`tests/quality/test_unified_budget.py:78`). A timeout of that subprocess call raises rather than returning a non-zero CompletedProcess; the independent minimal probe prints `TimeoutExpired raised; no CompletedProcess returned` (`reports/w-metafields-evidence/timeout-contract.txt:1`; exact command in validation). Therefore, if the historical failure really reached `assert proc.returncode == 0`, it was not that call's own timeout exception. A genuine non-zero child exit or an external signal would still need the original return code and output to distinguish.

The budget helper now prints the return code, argv, full stdout and full stderr instead of the last 800 characters of each stream (`tests/quality/test_unified_budget.py:80`). This preserves all existing assertions and should make a recurrence reviewable.

## Scope and review target

No production-file change or registry proposal is warranted by the observed results. The four conditional `_write_run_meta` regression files were not run because the writer was not changed; they remain unverified. No benchmark pilot, external dataset/scorer run, GPU operation, live model request, registry/journal/AGENTS edit, merge or push was performed. The demo/mock driver invocations are the synthetic invocations required by the assigned tests (`tests/quality/test_dgm_rule.py:180`, `:191`; `tests/quality/test_unified_budget.py:70`, `:79`; direct receipts above).

The required blocker checker reports exactly `{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}` (`reports/w-metafields-evidence/dataset-blockers-check.txt:1`). Test-only edits do not change its registry input.

**Most important uncertainty:** Recover the original failing process's full output, status, environment and revision. Without those, assigning (a)/(b) to historical DGM or claiming a production fix for the budget failure would be unsupported.
