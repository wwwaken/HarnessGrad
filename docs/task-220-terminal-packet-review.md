# Task 220 — Terminal task-211 packet review

**Disposition: two documentation corrections; Terminal remains BLOCKED.**
Reviewed base: `82459cfa6d16c323ca40f21db2daf597921aedb3`.
Workspace: `/tmp/hg-codex-220`; date: 2026-10-14.

## Corrections

- The [packet's scorer observation checklist](task-211-terminal-operator-backend-packet.md)
  said “created/stopped.” The actual [artifact runtime check](../eval/admission/artifact_admission.py)
  requires both `State.Status="created"` and `State.Running=false`. An exited
  container with `Running=false` is refused. The packet now states the exact
  fields, and three facade regressions cover an exited container and either
  missing state field. Observed mismatch is blocked; incomplete evidence is
  unknown. Runtime implementation is unchanged.
- The packet's result table said “fixed reason” for all statuses. The
  [quota schema](filesystem-quota-evidence.schema.json), `$defs.result`, requires
  `reason=null` for verified records and a fixed schema reason code for blocked
  or unknown records. The table now matches that conditional rule.

## Observer completeness and closure

All seven required observer fields appear in the packet: `observer_id`,
`implementation_sha256`, `boot_id`, `observed_at`, `sequence`,
`privilege_boundary_sha256` and `raw_observation_sha256`. No observer-envelope
field is missing. Kind-specific facts remain governed by the linked closed schema
and the [backend semantic requirements](filesystem-quota-backends.md); this
review adds no schema keys or observer implementation.

No mistaken runtime closure was found:

- The [Codex 168 audit](../reports/filesystem-quota-codex168-report.md) explicitly says
  host kernel/mount/quota state was not inspected. Its source inventory also
  records `host_kernel_mount_and_quota_state="not_inspected"` and live enforcement
  as unverified. The packet correctly keeps current host capability unknown.
- The [scorer facade](../eval/admission/scorer_admission.py) checks pinned declared bytes,
  selected exports and supplied runtime facts. It does not prove official-source
  completeness, authenticate an observer or execute the official scorer. The
  packet preserves those open obligations.
- [Runner admission](../eval/admission/runner_admission.py) still requires a read-only root,
  network none, exact paired limits and distinct scope IDs. Writable-root quota
  evidence or a local endpoint does not change those refusals. Its five-kind
  cleanup receipt does not replace the sidecar's eight-kind cleanup requirements.
- `benchmark_blockers` in [pilot admission](../eval/admission/pilot_admission.py) retains
  three unconditional gates per task plus quota and official-execution blockers.
  The [driver](../driver.py) still writes unknown cleanup/snapshot without a
  lifecycle receipt. Task-211 does not authorize a diagnostic or expansion.

## Command safety

The task-211 packet contains no executable host administration or workload command
sequence. Its filesystem features, options and acceptance equations are requirements,
not an approved provisioning procedure.

The linked [historical storage note](moving-docker-data-root.md) does contain risky
administrative operations. It stops Docker without establishing containerd
quiescence before copying the containerd store, replaces the daemon configuration,
and claims rollback remains valid after switching roots without reconciling later
writes. It also includes old-root removal. These are unsafe instructions to reuse
as a current operator handoff or quota fix. The packet already explicitly declines
to adopt that procedure; no replacement host commands are supplied here. The
historical note is preserved as evidence, and storage relocation closes no quota
gate. No referenced command was executed.

## Validation and limits

Focused synthetic suites: **294 passed in 0.44s**, including the three new
scorer-state cases. The suites guard subprocess/socket execution and use inert
local files and fabricated runtime facts.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/quality/test_runner_admission.py tests/quality/test_terminal_artifact_admission.py tests/quality/test_scorer_admission_codex173.py --basetemp=/tmp/harnessgrad-pytest-codex220-task220-test-tmp -p no:cacheprovider
```

The first attempt had 211 passes and 83 fixture setup errors because the chosen
base-temp parent did not exist. Creating that directory inside the worktree fixed
the invocation; the unchanged suite then passed. This was a local test setup error,
not enforcement evidence or a benchmark failure/zero score.

Additional local checks validated the Draft 2020-12 schema, all six
status/reason combinations, required-field refusal for each of the seven observer
fields, and their presence in the packet. All 19 source pins in task-211's review
record match the reviewed files. `git diff --check` passed.

The optional local HTML review rendered with three panels and zero prose warnings.
The bundled `answer-me-with-html` renderer used a worktree-local `AM_HOME`, disabled
update checks and `--no-open`; parsing found no remote active assets. Generated
HTML, its draft and captured passing test output stay under ignored `docs/_build/`
to keep the commit limited to the packet, regression tests and this review.

All writes stayed inside this worktree. No host changes, mounts, Docker commands,
model/H0 calls or task payload execution/reads occurred. No measurement, live
quota observation, scorer invocation or cleanup receipt was produced. Synthetic
passes do not close backend, observer, production wiring or lifecycle blockers.
Parent integration and its shared journal remain separate.
