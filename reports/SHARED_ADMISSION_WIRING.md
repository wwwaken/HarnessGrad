# Shared admission wiring audit — Codex 163

Audit date: 2026-10-14. Workspace: `/tmp/hg-codex-163`, an isolated detached
worktree. Audit baseline: `10e983f`. Runner refusal change: `5044731`.
This is a source audit and synthetic regression result, not a production runtime
observation, dataset gate receipt, pilot result, or H0 authorization.

## Finding and implemented boundary

**None of the three `eval.runner_admission` contracts has a production caller.**
Before this change, runner execution and cached successes could reach a passing
verdict without a shared admission receipt. Backend launch flags may enforce some
bounds, but the scoring path does not require independently collected enforcement
observations. No real benchmark task was run to make this finding.

The new refusal-only hook in `eval/runner.py:33` runs at the beginning of
`run_one` (`:151`) and before cache lookup in `_evaluate._measure` (`:892`).
It returns `invalid.stage=admission`, reason `backend_observation_unavailable`,
and a `harnessgrad.runner-policy-refusal.v1` receipt with `observation=unknown`,
`status=blocked`, `measured=false`, and `production_authorized=false`.
It grants no admission and manufactures no binding, manifest hash, observation
hash, or score. Refusal receipts contain only fixed field names, not declarations,
task contents, private paths, or caller-supplied evidence.

The hook covers environment fields `cpus`, `memory_mb`, `agent_timeout_s`,
`verify_timeout_s`, and `network`; all `kind=exec` environments, including direct
calls omitting normalized defaults; and `state=container`. It also refuses direct
runner inputs carrying `resources`, `filesystems`, `resource_policy`,
`network_policy`, or `artifact_policy`, plus verifier `timeout_s` or
`artifact_policy`. Presence triggers refusal even for an empty/null policy.
Unsupported direct-input names are refusal guards, not a new dataset schema.
Adapter-supplied observations, admission receipts, success booleans, controls,
mock backends, and `sandbox=False` cannot override this hook.

**After the change, a task with one of these declarations cannot pass through
`run_one` or `_evaluate`, including by reusing a cached success.** It is excluded
from scores and verdicts, is not added to the cache, and its refusal is preserved
in the existing invalid/progress channel. Existing cache entries are preserved.

**Tasks without these declarations can still pass without a backend observation.**
The authored synthetic legacy-files regression demonstrates this with a mocked
launch and the real answer verifier. Direct backend/verifier entry points also
remain outside the hook. This change must not be described as complete production
admission wiring or as blanket authorization of undeclared tasks.

## Contract callers

| Contract | Production callers in audited source | Actual test callers | Enforcement gap |
| --- | --- | --- | --- |
| `admit_runtime` (`eval/runner_admission.py:118`) | None | `tests/quality/test_runner_admission.py`: parameterized valid-contract tests, runtime checks, and the `refused` helper; the new unknown-observation test | No independent cgroup/swap/deadline, network attachment, read-only-root, or complete hard byte/inode observation producer is wired to execution. |
| `admit_snapshot` (`:160`) | None | Same suite: parameterized contract tests and snapshot cases via `refused`; the new unknown-observation test | No shared quiescence/exit/OOM, byte/inode headroom, deadline, device, or separately admitted snapshot-worker observation is wired to commit. |
| `admit_cleanup` (`:207`) | None | Same suite: parameterized contract tests and cleanup cases via `refused`; the new unknown-observation test | No shared exact-owned-object/all-namespace absence observation or atomic lease release/quarantine application is wired to production teardown. |

These APIs validate supplied dictionaries and evidence-hash syntax. They do not
collect observations or authenticate their origin. Even a synthetically passing
contract explicitly records `measured=false` and `production_authorized=false`.
Documentation references are not callers. The new runner hook does not call a
contract with invented facts to obtain a nominal passing or blocked receipt.

## Production path by component

| Component | Current wiring and exact missing integration |
| --- | --- |
| Driver | `driver.py:1062` calls `evaluate`; `harnessgrad/loops/mode_a.py:450` and `loops/eval_side.py:122` use the same entry point. Dataset side tables are narrowed in `driver.py:550`, then image resolution and container self-checks occur before evaluation (`:767` onward). These checks do not invoke shared admission. The new runner hook does not prevent those earlier driver preflights. No driver/main changes were made. |
| Registry/runner | `data/registry.py:519` normalizes every exec environment with network/resource/deadline defaults; `load_envs` preserves supported declarations. Its unknown-field rule (`:300`) rejects artifact/shared-policy declarations rather than transporting them. The runner has a run ID but no shared frozen manifest or fresh per-trial/phase binding/observer interface. The hook blocks the existing normalized policy paths before setup, services, container-state dispatch, or cache reuse. |
| Container | `eval/container.py:531` builds network/read-only/tmpfs/PID/memory/CPU flags; `run` launches them without an independent effective-limit inventory. `create` (`:758`) supports writable roots. The mount path does not pass dataset CPU/memory limits into `container.run`, whose signature lacks that parameter; the container-state path passes `limits_from` to `create`. Neither path constructs shared observations, proves swap or all writable byte/inode quotas, or binds enforcement facts to trials. |
| Services | `eval/services.py:344` creates an internal network, starts sidecars, and health-checks them. Sidecar launch does not establish a shared resource or writable-surface quota envelope. Health and gateway inspection are not complete enforcement observations. `RunningServices.stop` returns removal errors; it does not prove all owned namespaces absent or apply shared lease quarantine. |
| Sandbox | `eval/sandbox.py:173` builds namespace/mount instructions, with `--unshare-net` for declared `none`; `run` (`:395`) uses a subprocess timeout. Neither produces shared cgroup/deadline/network/quota observations. `admit_native_network` in `eval/runtime_policy.py` checks configuration compatibility, not observed backend enforcement. |
| Verifier | `eval/verifier.py:430` / `:452` can return passing answer/command verdicts directly. `_verify_container_state` (`:237`) creates a fresh verifier container and reads its output, without shared runtime admission. Native command verification does not forward the environment network policy to `sandbox.run`. The runner hook protects runner-mediated declared-policy calls; direct verifier calls remain independent. |
| Snapshot/cleanup | `eval/container_state.py:184` stops and commits, then verifies and tears down in `finally`. `container.commit` (`:875`) calls the separate legacy `snapshot_admission`, which explicitly records `preflight_only=true`, `quota_enforced=false`; it is byte-only capacity preflight. Removal helpers ignore unsuccessful removal results or catch errors, without exact absence observations. Successful scoring can precede cleanup, and there is no production shared cleanup lease gate. |

`eval.artifact_admission` provides separate contract/export/runtime-inspection
helpers; production driver/runner/verifier code does not call them. Container-state
verification still consumes a whole committed image rather than an admitted,
allowlisted artifact export. `eval.pilot_admission.ControlSession` has separate
synthetic control inspection/quarantine machinery, not production shared admission
wiring. `harnessgrad.trusted_runner.TrustedRunnerFacade` likewise has no shared
admission caller. None supplies an exception to the new runner refusal.

## Required integration before allowing declared-policy tasks

1. Add an explicit, selected-task-only policy channel that survives registry
   validation/normalization, including artifact/export policy. Freeze provenance,
   phase limits and ownership in the manifest; provide fresh trial/phase bindings.
2. Implement a trusted backend observer independently of actor/adapter outputs.
   Collect effective enforced limits and the complete writable/network inventory;
   keep enforcement stable after observation. Call `admit_runtime` for each actor,
   sidecar, verifier, and snapshot worker before execution. The current contract
   supports only `network=none`; services/bridge/relays need their own reviewed
   contract, not reinterpretation as `none`.
3. Wire quiescence, byte/inode capacity and bounded-worker observations into
   `admit_snapshot`. Separately bound commit/export growth and admit an allowlisted
   artifact projection before trusted verification.
4. Persist allocation intent and exact ownership, independently verify cleanup
   absence, call `admit_cleanup`, and atomically retain/quarantine reservations on
   unknown cleanup. Final measurement acceptance must account for cleanup failure.
5. Keep cached scores subordinate to fresh backend admission; a cached verdict
   contains no observation or lifecycle evidence. Remove the refusal-only hook
   only when these trusted production integrations exist.

## Validation and scope

Focused validation command (the initial fixture-failure run omitted `--tb=short`):

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q --tb=short -p no:cacheprovider --basetemp=/tmp/harnessgrad-pytest-codex163-pytest-codex-163-admission tests/quality/test_shared_admission_wiring_codex163.py tests/quality/test_runner_admission.py
249 passed in 0.28s
```

The new suite has 49 authored synthetic cases. Real subprocess launch, sockets,
Docker, services, and container-state execution are blocked by its fixtures;
platform hashing is mocked to avoid dataset-file reads. It covers early refusal,
unknown observations for all three shared APIs, cleanup quarantine on unknown,
unsupported/empty policy declarations, supplied success evidence, cache refusal,
multiple trial/job settings, persisted invalid receipts, selected-only checking,
and preservation of the undeclared legacy files/cache paths. The legacy shared
contract suite contributes 200 synthetic tests. The first run had five fixture
failures because the mocked integrity `diff` returned a list; correcting it to the
actual dictionary shape produced the passing result above.

The full integration suite was not run. Existing tests expecting policy-bearing
runner execution (for example native offline end-to-end controls) describe the
previous permissive behavior and need to be reconciled with this deliberate
refusal boundary; a passing synthetic backend control is not production admission.
Backend enforcement, cleanup, scores, and real dataset coverage remain unmeasured.
No Docker/model/GPU/H0/heldout execution, benchmark payload reads, paid endpoints,
main-branch edits, or edits outside this worktree were performed.

Reviewed patch: 44 runner lines plus the uniquely named synthetic test and this
new report. `git diff --check 10e983f` passes. No inherited report was reused.

Source SHA-256:

```text
eval/runner.py 97089b38ffcc7b9abbe059ee8c4f19c694e9c5badb0bdb03016dcb3567fb42b2
eval/runner_admission.py f9d9dee76e1e1a94366d1f486c122a100bb42755b4ec9d4a86c48b4941c1f663
tests/quality/test_shared_admission_wiring_codex163.py 25d5640b6cce6e099cf33974c001598b5a061c51ad2964bce7b3faf0ce48bcc7
```
