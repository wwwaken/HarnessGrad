# Task 242 — ordinary GPU entrypoints and sandbox behavior

**No universal strict filesystem-quota or backend-observer prerequisite is added
to ordinary runs.** This task changes documentation, CLI help and tests only.
Existing declared-policy refusals and production diagnostic requirements remain.

Reviewed base: `0930d99cc882c5a049c98f9123e9427470e7e818`; isolated worktree
`/tmp/hg-codex-242`, 2026-10-14. The initial tree was clean.
This is source review and authored, mocked regression evidence. No model, H0,
endpoint request, GPU probe, container, host-quota inspection or benchmark ran.
The test model identity and sandbox responses are authored facts, not observations.

## Entrypoint inventory

| Entrypoint | Observed current behavior | Scope of the evidence |
| --- | --- | --- |
| `tools/serve_local_model.sh` | Configures the existing vLLM environment and local service; does not call quota or runner/scorer admission contracts. | Source inspection and shell syntax only; service readiness was not measured. |
| `tools/keep_local_models.sh` | Supervises GPU0/8001 and GPU1/8002 using that service launcher. | Source inspection and shell syntax only; supervisor was not started. |
| `tools/harnessgrad.sh` | Starts the model service/UI, reports status and stops them. It does not add a quota/backend-observer gate. | Source inspection and shell syntax only; no subcommand was run. |
| `tools/serve_ui.py:start_job` | Passes `--sampling all`; forwards `--no-sandbox` only on an explicit request. It adds no `--policy-evidence`, quota or strict backend-observer requirement. | Mocked `Popen` captures argv and launch metadata; it executes no process. |
| `driver.py:main`, general sampling | Ordinary files-task preflight can reach metadata without staged evidence or a budget profile. The trusted budget dispatcher is opt-in, except for the existing approved `task25-` ID contract. Existing model/configuration, workspace, harness/runtime and sandbox checks still apply. | Authored model identity; stubbed sandbox check; stop before workspace staging or evaluation. This is compatibility evidence, not a measured GPU run. |
| `driver.py:main`, staged sampling | Default `diagnostic` and explicit `pilot_10pct` require policy evidence. Staged selection, trials/jobs/rounds, endpoint binding and separate expansion review retain their existing rules. | Existing pure/mocked policy and receipt tests; no actual endpoint is contacted. |
| `eval.runner.run_one` / `_evaluate` | Legacy files tasks without policy declarations retain their existing route. Policy-bearing tasks retain the refusal-only hook before launch/cache reuse. | Existing authored legacy/refusal tests; no backend enforcement is observed. |

The help description now states the ordinary-run scope, staged evidence requirement
and non-production test boundary. README demo commands explicitly choose `all`:
they previously relied on a default that now selects the incompatible staged policy.
That correction describes the local demo; it does not authorize general sampling
for a production H0 or replace the staged policy.

## Existing refusal boundaries

When sandboxing is requested, a failed driver `sandbox.self_check` returns 2 before
active run metadata, workspace staging or evaluation. There is no automatic retry
without the sandbox. A later `SandboxUnavailable` in the native runner remains an
explicit fatal refusal. The new tests use an authored failed self-check and forbid
external execution; they do not probe the host's isolation.

`--no-sandbox` remains an explicit debugging choice. The driver warns and records
`requested=false`, `active=false`; sandboxed and unsandboxed numbers remain
non-comparable. For `exec` tasks, this option retains the container boundary.
It does not override the runner's declared-policy refusal.

The existing runner hook, introduced in `5044731`, refuses declarations of
`cpus`, `memory_mb`, `agent_timeout_s`, `verify_timeout_s`, `network`, `resources`,
`filesystems`, `resource_policy`, `network_policy`, or `artifact_policy`;
`kind=exec` and `state=container`; and verifier `timeout_s` or `artifact_policy`.
Even empty/null declarations trigger the hook. Its bounded receipt says
`backend_observation_unavailable`, `observation=unknown`, `measured=false` and
`production_authorized=false`, with no fabricated score. Tests retain both
sandbox settings and cached-success refusal. See the historical
[shared wiring audit](../reports/SHARED_ADMISSION_WIRING.md).

Thus, “no universal prerequisite” does not mean that every dataset currently runs.
The task neither removes that existing hook nor introduces a strict backend mode,
required quota flag, allocator, observer, new environment variable or runtime call.

## Production and evidence limits

The standalone runner/scorer/artifact contracts and proposed quota sidecar do not
establish a connected, authenticated production observer. Driver staged receipts
still supply unknown cleanup/snapshot and no lifecycle completion; provisional
results cannot become a staged measured curve. Mocked successes prove neither
effective quotas nor sandbox enforcement. Missing observations remain unknown,
not claims that the host lacks support.

The [quota specification](filesystem-quota-backends.md),
[diagnostic policy](../reports/DIAGNOSTIC_POLICY.md) and pinned
[task-234 readiness review](task-234-diagnostic-readiness.md) keep their own
scope and requirements. This task supplies no production admission, dataset-gate
closure, diagnostic receipt, benchmark score or expansion authorization.

## Validation

The new test module blocks subprocess execution and sockets, model probes,
evaluation/loop execution, container preflight, budget dispatch and workspace
staging. The UI test replaces `Popen` with a capture-only stub. The final focused
command binds both pytest basetemp and standard-library `TMPDIR` beneath
`/tmp/hg-codex-242/.scratch`.

Initial invocation: **1 passed, 5 setup errors** because `.scratch` did not exist;
no runtime control failed. After creating that directory, the new suite passed
**6 tests**. Both outputs are preserved in
`reports/gpu-entrypoint-codex242-initial-test-result.txt` and
`reports/gpu-entrypoint-codex242-corrected-test-result.txt`.

An earlier focused run also passed 156 tests, but bound only pytest's scratch
path. Existing receipt tests use standard-library temporary runner directories,
so the suite was repeated with explicit `TMPDIR`. The earlier output is preserved
in `reports/gpu-entrypoint-codex242-focused-initial-test-result.txt`; it is not evidence
that all scratch writes stayed inside this worktree.

Final focused verification uses:

```bash
mkdir -p /tmp/hg-codex-242/.scratch/task242-stdlib-temp
env TMPDIR=/tmp/hg-codex-242/.scratch/task242-stdlib-temp \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  tests/quality/test_gpu_entrypoint_contract_codex242.py \
  tests/quality/test_shared_admission_wiring_codex163.py \
  tests/quality/test_staged_receipt_audit_codex193.py \
  tests/quality/test_diagnostic_policy.py \
  --basetemp=/tmp/hg-codex-242/.scratch/task242-focused-final
```

Focused result: **156 passed**, no failures or skips. The
[focused output](../reports/gpu-entrypoint-codex242-test-result.txt) is the test result,
not production runtime evidence. `bash -n` passed for the three shell entrypoints;
`git diff --check` passed. The
[static checks](../reports/gpu-entrypoint-codex242-static-validation.txt) also confirm
that the driver AST is unchanged after removing argparse description/help text.
Scratch cleanup is test-file housekeeping, not a backend cleanup receipt.
The [HTML overview](task-242-gpu-entrypoint-overview.html) summarizes these boundaries.
