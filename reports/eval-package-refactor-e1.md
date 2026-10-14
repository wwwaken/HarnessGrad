# Eval package structural refactor (e1)

Baseline: `9c928ed`. No model or H0 runs.

## Before: real AST import edges

Extracted before choosing the layout using the AST scanner in
`tests/quality/test_import_direction.py` over production source (including
function-local imports). The whole-tree scan additionally found 211 distinct
edges targeting eval across 437 Python files.

```text
eval.appworld_reporting -> __future__
eval.appworld_reporting -> hashlib
eval.appworld_reporting -> json
eval.appworld_reporting -> re
eval.artifact_admission -> __future__
eval.artifact_admission -> contextlib
eval.artifact_admission -> eval.pilot_admission
eval.artifact_admission -> hashlib
eval.artifact_admission -> json
eval.artifact_admission -> os
eval.artifact_admission -> pathlib
eval.artifact_admission -> re
eval.artifact_admission -> shutil
eval.artifact_admission -> stat
eval.candidate -> __future__
eval.candidate -> json
eval.candidate -> pathlib
eval.candidate -> sys
eval.candidate -> tools.validate_harness
eval.console -> __future__
eval.console -> eval.phases
eval.console -> eval.progress
eval.console -> json
eval.console -> pathlib
eval.console -> sys
eval.container -> __future__
eval.container -> ckpt.git_state
eval.container -> eval.progress
eval.container -> os
eval.container -> pathlib
eval.container -> shutil
eval.container -> subprocess
eval.container -> sys
eval.container -> tempfile
eval.container -> threading
eval.container -> time
eval.container_state -> __future__
eval.container_state -> ckpt.git_state
eval.container_state -> eval.container
eval.container_state -> eval.harness_runtime
eval.container_state -> eval.integrity
eval.container_state -> eval.modelgate
eval.container_state -> eval.progress
eval.container_state -> eval.services
eval.container_state -> eval.task_contract
eval.container_state -> eval.tracing
eval.container_state -> eval.verifier
eval.container_state -> json
eval.container_state -> os
eval.container_state -> pathlib
eval.container_state -> subprocess
eval.container_state -> sys
eval.container_state -> tempfile
eval.container_state -> tools.web_gateway
eval.diagnostic_policy -> __future__
eval.diagnostic_policy -> copy
eval.diagnostic_policy -> eval.lifecycle_receipt
eval.diagnostic_policy -> eval.metrics
eval.diagnostic_policy -> hashlib
eval.diagnostic_policy -> json
eval.diagnostic_policy -> math
eval.diagnostic_policy -> pathlib
eval.diagnostic_policy -> re
eval.gaia_preflight -> __future__
eval.gaia_preflight -> argparse
eval.gaia_preflight -> eval.gaia_snapshot_attestation
eval.gaia_preflight -> eval.runner
eval.gaia_preflight -> json
eval.gaia_preflight -> pathlib
eval.gaia_snapshot_attestation -> __future__
eval.gaia_snapshot_attestation -> hashlib
eval.gaia_snapshot_attestation -> json
eval.gaia_snapshot_attestation -> pathlib
eval.gaia_snapshot_attestation -> re
eval.gaia_snapshot_attestation -> subprocess
eval.harness_runtime -> __future__
eval.harness_runtime -> eval.container
eval.harness_runtime -> harnessgrad.config
eval.harness_runtime -> hashlib
eval.harness_runtime -> json
eval.harness_runtime -> os
eval.harness_runtime -> pathlib
eval.harness_runtime -> subprocess
eval.harness_runtime -> sys
eval.integrity -> __future__
eval.integrity -> hashlib
eval.integrity -> pathlib
eval.lifecycle_receipt -> __future__
eval.lifecycle_receipt -> copy
eval.lifecycle_receipt -> eval.runner_admission
eval.lifecycle_receipt -> hashlib
eval.lifecycle_receipt -> json
eval.metrics -> __future__
eval.metrics -> hashlib
eval.metrics -> math
eval.metrics -> random
eval.modelgate -> __future__
eval.modelgate -> socket
eval.modelgate -> socketserver
eval.modelgate -> sys
eval.modelgate -> threading
eval.modelgate -> urllib.parse
eval.phases -> __future__
eval.pilot_admission -> __future__
eval.pilot_admission -> contextlib
eval.pilot_admission -> fcntl
eval.pilot_admission -> hashlib
eval.pilot_admission -> json
eval.pilot_admission -> math
eval.pilot_admission -> os
eval.pilot_admission -> pathlib
eval.pilot_admission -> re
eval.pilot_admission -> subprocess
eval.pilot_admission -> time
eval.pilot_admission -> uuid
eval.progress -> __future__
eval.progress -> contextlib
eval.progress -> contextvars
eval.progress -> eval.phases
eval.progress -> os
eval.progress -> threading
eval.progress -> time
eval.runner -> __future__
eval.runner -> ckpt.git_state
eval.runner -> concurrent.futures
eval.runner -> eval.console
eval.runner -> eval.container
eval.runner -> eval.container_state
eval.runner -> eval.harness_runtime
eval.runner -> eval.integrity
eval.runner -> eval.modelgate
eval.runner -> eval.progress
eval.runner -> eval.runtime_policy
eval.runner -> eval.sandbox
eval.runner -> eval.services
eval.runner -> eval.task_contract
eval.runner -> eval.tracing
eval.runner -> eval.verifier
eval.runner -> json
eval.runner -> os
eval.runner -> pathlib
eval.runner -> shutil
eval.runner -> subprocess
eval.runner -> sys
eval.runner -> tempfile
eval.runner -> tools.improver
eval.runner -> tools.web_gateway
eval.runner_admission -> __future__
eval.runner_admission -> functools
eval.runner_admission -> hashlib
eval.runner_admission -> json
eval.runner_admission -> posixpath
eval.runner_admission -> re
eval.runtime_policy -> __future__
eval.runtime_policy -> eval.tracing
eval.runtime_policy -> math
eval.runtime_policy -> pathlib
eval.sandbox -> __future__
eval.sandbox -> ckpt.git_state
eval.sandbox -> harnessgrad.config
eval.sandbox -> json
eval.sandbox -> os
eval.sandbox -> pathlib
eval.sandbox -> shutil
eval.sandbox -> subprocess
eval.sandbox -> sys
eval.sandbox -> tempfile
eval.scorer_admission -> __future__
eval.scorer_admission -> eval.artifact_admission
eval.scorer_admission -> eval.pilot_admission
eval.scorer_admission -> eval.scorer_bundle
eval.scorer_admission -> functools
eval.scorer_admission -> pathlib
eval.scorer_backend -> __future__
eval.scorer_backend -> copy
eval.scorer_backend -> eval.lifecycle_receipt
eval.scorer_backend -> eval.runner_admission
eval.scorer_backend -> eval.scorer_admission
eval.scorer_backend -> pathlib
eval.scorer_bundle -> __future__
eval.scorer_bundle -> argparse
eval.scorer_bundle -> eval.artifact_admission
eval.scorer_bundle -> eval.pilot_admission
eval.scorer_bundle -> hashlib
eval.scorer_bundle -> json
eval.scorer_bundle -> pathlib
eval.scorer_bundle -> re
eval.separated_stdio -> __future__
eval.separated_stdio -> argparse
eval.separated_stdio -> decimal
eval.separated_stdio -> hashlib
eval.separated_stdio -> json
eval.separated_stdio -> os
eval.separated_stdio -> pathlib
eval.separated_stdio -> signal
eval.separated_stdio -> stat
eval.separated_stdio -> subprocess
eval.separated_stdio -> tempfile
eval.services -> __future__
eval.services -> eval.container
eval.services -> harnessgrad.config
eval.services -> hashlib
eval.services -> json
eval.services -> os
eval.services -> pathlib
eval.services -> re
eval.services -> subprocess
eval.services -> time
eval.stepwise_transport -> __future__
eval.stepwise_transport -> collections.abc
eval.stepwise_transport -> copy
eval.stepwise_transport -> json
eval.stepwise_transport -> typing
eval.task_contract -> __future__
eval.trace -> __future__
eval.trace -> eval.tracing
eval.tracing -> __future__
eval.tracing -> json
eval.tracing -> os
eval.tracing -> pathlib
eval.tracing -> shutil
eval.tracing -> sys
eval.unix_model_relay -> __future__
eval.unix_model_relay -> http.client
eval.unix_model_relay -> http.server
eval.unix_model_relay -> json
eval.unix_model_relay -> math
eval.unix_model_relay -> os
eval.unix_model_relay -> pathlib
eval.unix_model_relay -> socketserver
eval.unix_model_relay -> threading
eval.verifier -> __future__
eval.verifier -> eval.container
eval.verifier -> eval.integrity
eval.verifier -> eval.runtime_policy
eval.verifier -> eval.sandbox
eval.verifier -> eval.services
eval.verifier -> eval.tracing
eval.verifier -> json
eval.verifier -> os
eval.verifier -> pathlib
eval.verifier -> subprocess
eval.verifier -> tempfile
```

## Layout and compatibility

`containers/` and `service/` avoid collisions with the old `eval.container` and
`eval.services` module names, allowing identity-preserving compatibility aliases.

- `eval/run/`: `runner`, `candidate`, `metrics`, `integrity`, `task_contract`.
- `eval/containers/`: `container`, `container_state`, `sandbox`, `harness_runtime`.
- `eval/admission/`: `pilot_admission`, `artifact_admission`, `runner_admission`, `scorer_admission`, `scorer_bundle`, `scorer_backend`, `lifecycle_receipt`.
- `eval/service/`: `services`, `modelgate`, `unix_model_relay`, `separated_stdio`, `stepwise_transport`.
- `eval/observe/`: `console`, `progress`, `trace`, `tracing`, `phases`.
- `eval/policy/`: `diagnostic_policy`, `runtime_policy`, `appworld_reporting`, `gaia_preflight`, `gaia_snapshot_attestation`.
- `eval/verification/`: `verifier`.

All 32 old `eval.<module>` paths are documented compatibility aliases to their
canonical implementations; see `docs/architecture.md`. Existing module CLIs
delegate to the canonical module with `runpy` when invoked through an old path.
The pre-existing trace adapter moves intact to `eval.observe.trace`.

## Verification

- All 32 executable module ASTs match the originals after canonical import
  remapping, removing docstrings, and adjusting `Path(__file__)` repository-root
  lookups from `parents[1]` to `parents[2]`. Signatures, annotations, defaults,
  executable literals and function bodies are unchanged. All 243 outgoing
  implementation import edges, including 50 internal eval edges, match under
  the same remapping. Package initializers have no implementation imports.
- Final focused suite: **275 passed in 19.57s** across import direction, trace
  compatibility, candidate validation, configuration, boundary contracts,
  GAIA preflight/attestation, old-path compatibility and the live blocker index.
- Compatibility checks cover all 32 module identities, parent-package lookup,
  private names, patching shared function globals, repository-root resolution,
  all four old module CLIs, standalone stdio execution, and both old/new paths
  in the historical critic's source-file matchers.
- `python3 tools/run_tests.py --jobs 12`: **exit 1**, 147 files; first pass
  1285.9s. It reported 17 files still nonzero on serial retries and eight passing
  alone. Those categories need the corrections below; the final printed failure
  summaries retain first-pass counts, so use the serial recheck lines instead.
- `python3 tools/run_tests.py --registry-only`: **exit 1**, four of five files
  pass. The remaining file, `test_dataset_controls.py`, has two failures,
  23 passes and one skip. The untouched `9c928ed` worktree produces the same
  result, including its serial retry. The current registry first pass took
  136.0s, and its failed-file retry took 125.87s.

### Failure classification

The checkout already had an orphaned `--jobs 16` test runner when this task
started. It shared source files and integration resources with the requested
12-job run. Tests that mutate a protected source file can also invalidate other
concurrent tests' snapshots. Baseline checks used a separate detached worktree
at `9c928ed`, under `.scratch/eval-refactor/baseline`, with a sibling test work
root and pytest's ordinary external temporary directories.

- **One migration regression corrected:** the live
  `docs/dataset-blockers.json` evidence pointers still targeted `eval/sandbox.py`
  and `eval/runner.py`, which became shims. Repointing those two source locators
  makes all 52 blocker tests pass. The initial failed registry transcript is
  superseded by the final registry run. The full runner labels this corrected
  file “load-sensitive,” but its original cause was the stale source pointers.
- **Eight files affected by contention:** candidate application, console, DGM,
  progress, split, stop semantics, unified budget and trials/unmeasured all pass
  in an isolated check. In particular, trials/unmeasured initially failed even
  during the full runner's serial phase while the other runner was active;
  after both runners finished, its isolated retry passed **15/15 in 11.33s**.
- **One skip-only file:** `test_claims_doc.py` has one skipped test and exits 5.
  The runner counts that as a real failure, but no assertion failed. The same
  result occurs on `9c928ed`; runner behavior is outside this refactor's scope.
- **Fifteen persistent failure files:** serial results are listed below. Fourteen
  also fail on the untouched baseline. The slow AppWorld scorer file was not
  independently rerun in the baseline worktree: the requested full run already
  spent 1099.73s on its first pass and 1111.19s on its serial retry. Its two
  remaining failures are recorded as persistent integration failures, with
  baseline attribution unverified rather than claimed as proven.

| File | Current serial result | Untouched baseline result |
| --- | --- | --- |
| `test_appworld_official_scorer.py` | 2 failed, 12 passed | Not independently rerun; baseline attribution unverified |
| `test_appworld_service_diagnosis.py` | 1 failed, 5 passed | Same |
| `test_cli_harness.py` | 2 failed, 4 passed | Same |
| `test_container.py` | 6 failed, 20 passed | Same |
| `test_container_state.py` | 1 failed, 18 passed | Same |
| `test_dataset_controls.py` | 2 failed, 23 passed, 1 skipped | Same, including serial registry retry |
| `test_identity_and_verdicts.py` | 1 failed, 17 passed | Same |
| `test_isolation.py` | 5 failed, 9 passed | Same five assertions |
| `test_jericho_runtime_admission.py` | 1 failed, 12 passed | Same |
| `test_jericho_runtime_boundaries.py` | 2 failed, 15 passed | Same |
| `test_parallel_tasks.py` | 1 failed, 11 passed | Same |
| `test_sandbox.py` | 2 failed, 11 passed | Same two assertions |
| `test_services.py` | 7 failed, 30 passed | 8 failed, 29 passed; existing integration failures plus a baseline health-wait failure |
| `test_split_source.py` | 1 failed, 11 passed | Same |
| `test_web_gateway.py` | 3 failed, 40 passed | Same |

Existing failures are reported, not repaired. Container/service/isolation
failures were also identified as pre-existing in the task instructions. The
baseline independently confirms the missing fixture/configuration and stale
expectation failures above. No model or H0 pilot was launched.

### Scope and preserved artifacts

- The public package name remains `eval`. Top-level Python files contain only
  documented compatibility aliases. Implementation imports use canonical paths.
- The root `eval/diagnostic_receipt.schema.json` artifact path remains stable;
  only its descriptive Python reference changes. GAIA source-identity-v1
  required historical paths remain unchanged, so old manifests still validate.
- Historical receipts, JSON source hashes and report artifacts were preserved.
  The live blocker index changes only two source pointers; taxonomy, statuses
  and blocker declarations are unchanged.
- Measured `base_harness/` and `methods/` files retain their exact original bytes.
  The standalone separated-stdio scorer implementation is also byte-identical.
- The historical adapter's critic path references recognize both compatibility
  shims and moved run implementations; generated documentation names the new
  source locations. No unrelated algorithm or bug fixes are included.
- Reproduction transcripts and baseline comparison JSON are retained locally
  under `.scratch/eval-refactor/`, with unique filenames. The disposable baseline
  worktree is removed after review; these transcripts remain.
