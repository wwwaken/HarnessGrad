# Ordinary local entrypoint audit — Task 235

Review basis: `0930d99cc882c5a049c98f9123e9427470e7e818`, isolated worktree
`/tmp/hg-codex-235`. Documentation and CLI guidance only; no production authorization.

## Findings and changes

- README installation/run guidance and `driver.py --help` omitted the explicit
  ordinary-user boundary. They now state that native/files demos and help require
  no sudo, dedicated quota volume, root Docker access or strict runtime mode.
  Sandboxed runs still require working bubblewrap/user namespaces. Installing
  system dependencies and host provisioning remain administrator work; Docker-backed
  tasks and image/overlay builds retain their own prerequisites and admission gates.
- README demo commands and the installer's successful-check next-step text inherited
  the staged `diagnostic` default. Those commands would require policy evidence and
  a live endpoint instead of selecting the advertised local demo. The examples now
  explicitly select `--dataset demo --sampling all` with `HG_AGENT_BACKEND=mock`.
  The installer no longer asks for model credentials to try this demo.
- README and help state that local/demo success grants no production/H0 authorization.
  Staged evidence requirements and declared-policy refusals remain in place. Missing
  enforcement evidence stays blocked and invalid/unmeasured, never an ordinary zero.
  Sampling and sandbox choices do not satisfy those evidence gates.

The source review also covered ordinary harness-authoring/onboarding docs, web
entrypoint docs, configuration declarations, image/overlay tool help, and quota,
runner-admission and runtime contract docs. These did not establish a universal
privilege, dedicated-volume or strict-mode prerequisite. The quota checklists already
describe pending operator/backend work rather than completed ordinary-user setup.
No new runtime flag, fallback, evidence override or policy-declaration change was added.

## Verification

The final focused suite passed **255 tests in 0.57s**, without failures or skips:

```bash
env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  TMPDIR=/tmp/hg-codex-235/.scratch/local-entrypoint-codex235 \
  python3 -m pytest -q -p no:cacheprovider \
  --basetemp /tmp/harnessgrad-pytest-codex235-local-entrypoint-codex235-pytest-final \
  tests/quality/test_local_entrypoint_docs_codex235.py \
  tests/quality/test_shared_admission_wiring_codex163.py \
  tests/quality/test_runner_admission.py \
  tests/quality/test_install_sh.py::test_the_script_is_valid_bash \
  tests/quality/test_install_sh.py::test_help_does_not_run_anything \
  tests/quality/test_install_sh.py::test_an_unknown_option_is_rejected
```

The [new tests](../tests/quality/test_local_entrypoint_docs_codex235.py) render real
driver help under execution/read/write guards, parse the README commands without
proceeding past argparse, and render only the installer's report section using
authored success facts. Existing synthetic regressions verify policy refusal before
dispatch/cache/scoring, ordinary files compatibility and false authorization flags.
The initial 251-test pass predates the installer text correction; both
[initial](../reports/local-entrypoint-codex235-test-result.txt) and
[final](../reports/local-entrypoint-codex235-final-test-result.txt) outputs are retained.

An AST comparison against the review basis confirms that `driver.py` is unchanged
after excluding argparse description/help strings. `eval/`, `harnessgrad/`, `ckpt/`,
`data/` and `tools/` have no diff. Installer changes affect printed guidance only.
Whitespace and local documentation-link checks passed.

No H0, model, endpoint, payload, scorer, Docker, installer readiness check, host
administration or real runtime was executed. The demo commands were parsed only;
no end-to-end demo or live host readiness is claimed. Task-owned pytest scratch
files were removed after retaining test output. This is local file cleanup, not a
runtime cleanup receipt. Parent review/integration remains separate.
