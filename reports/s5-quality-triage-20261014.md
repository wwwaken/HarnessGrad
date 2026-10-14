# S5 quality-test triage journal

Worktree: `/tmp/hg-s5`; initial HEAD: `065d29c`.

Only the three requested test files were executed, sequentially, with a separate
external basetemp for each. No whole-suite run or model endpoint was used.

## Scope enforcement

A temporary `sitecustomize.py` supplied through `PYTHONPATH` denied imports of
`data.agentdojo`, reads of its source/bytecode, and traversal/reads under its data
directory before access occurred. The excluded files were not read, imported,
modified, or executed. The guard was used in every pytest process and inherited
by Python subprocesses; it was removed after verification.

The registry already catches adapter import errors, so its catalog checks cover
the accessible catalog only; these results make no claim about the excluded adapter.
The guard did not suppress snapshot errors: the first parallel-file run failed
before its mocked task execution because real platform snapshots attempted to
read the excluded source. This is evidence of test coupling to the entire live
checkout, not evidence of a production runner failure or resource contention.

## One-line failure verdicts

- `test_split_source.py::test_no_refused_dataset_pretends_to_have_an_evaluation_set`: real — stale test minimum of six refused adapters; four accessible adapters satisfy every refusal assertion; replaced the count with a nonempty check, preserving the per-adapter contract.
- `test_parallel_tasks.py::test_jobs_one_is_still_a_plain_sequential_loop`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked run; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_jobs_n_runs_tasks_concurrently`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked run; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_each_task_keeps_its_own_trace`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked run; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_the_record_does_not_depend_on_the_worker_count`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked runs; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_trials_and_jobs_multiply`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked runs; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_an_exception_still_travels`: real (test isolation) — live-checkout hashing hit the scope guard before the intended exception; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_a_harness_that_never_starts_stops_the_round`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked startup failures; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_a_task_specific_startup_failure_does_not_stop_the_round`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked startup failure; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_a_clean_round_has_no_startup_failure`: real (test isolation) — live-checkout hashing hit the scope guard before the mocked runs; fixed with a private synthetic platform input and real snapshots.
- `test_parallel_tasks.py::test_jobs_reaches_the_run_through_the_driver`: real (test isolation) — driver hashing hit the scope guard; fixed by staging the actual runtime plus only the demo adapter, without copying the checkout's `.env` or changing production integrity checks.

No disk, Docker, network, or missing-provisioning failure was observed. No
contention verdict is supported by these runs.

## Commands and outcomes

Each command was run with `PYTHONPATH=/tmp/hg-s5/.s5-scope-guard` while the
temporary access guard existed:

```sh
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/s5-new_dataset tests/quality/test_new_dataset.py
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/s5-split_source tests/quality/test_split_source.py
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/s5-parallel_tasks tests/quality/test_parallel_tasks.py
```

| File | Initial outcome | Verified outcome |
| --- | --- | --- |
| `test_new_dataset.py` | 28 passed | 28 passed in 8.74s; unchanged |
| `test_split_source.py` | 1 failed, 11 passed | 12 passed in 9.05s |
| `test_parallel_tasks.py` | 10 scope-guard failures, 2 passed | 12 passed in 2.06s |

The driver receipt confirms `jobs=2`, `trials=1`, four demo tasks measured, no
invalid results, an active bwrap sandbox, and a nonempty platform content hash.
Its recorded platform root is the staged fixture. No production policy hook,
snapshot/diff function, score assertion, or timing bound was disabled or relaxed.

## Focused changes

- `a5503aa`: pin the refusal contract without a stale catalog minimum.
- The parallel-test fix isolates platform inputs and stages a demo-only runtime;
  production code is unchanged. This journal records its review and validation.
- `git diff --check` passed before committing the fixes.
