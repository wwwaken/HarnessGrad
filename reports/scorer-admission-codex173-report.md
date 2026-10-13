# Codex 173 scorer admission facade

Implemented `eval.scorer_admission` as the public offline API, with its contract in
`docs/scorer-admission-contract.md`. No production adapter was integrated.

Review found that scorer spec and local file validation were already shared.
Sealed JSON authentication/parsing was duplicated, while the artifact runtime
path repeatedly loaded the same task contract. Both declarations now use one
exact-byte JSON loader, including duplicate-key rejection for artifact contracts.
The shared runtime observation check consumes the authenticated contract and
derives tmpfs options from it. Legacy entry points and successful receipt shapes
remain available. Unavailable evidence uses an `AdmissionError` subclass.

The facade requires independent bundle and artifact contract pins and compares
source, runtime image and scorer declarations before reading local trees. Task
export and quota policies remain separate from reusable bundle identity. Runtime
admission verifies closure bytes once and rechecks the projection on every call.
Scoped receipts distinguish passed checks, blocked mismatches and unknown
evidence; all are unmeasured and carry `production_authorized=false`.

Validation completed:

```text
python -m pytest -q tests/quality/test_scorer_admission_codex173.py tests/quality/test_scorer_bundle_codex170.py tests/quality/test_terminal_artifact_admission.py --basetemp=/tmp/hg-codex-173/.pytest-tmp-codex173
123 passed in 0.47s
git diff --check: passed
```

The new controls use inert synthetic files and fabricated observations, deny
subprocesses/sockets, and cover public signatures, pin independence, mismatched
declarations, task policy separation, legacy receipt parity, closure check count,
repeat verification, incomplete/unavailable evidence and retained cleanup failure.

Production source provenance/completeness, ABI closure, trusted fresh observation,
ownership, quiescence, CPU/memory/PID/deadline enforcement, cleanup and official
scorer execution remain independent obligations. No Docker, H0, model/provider,
GPU, dataset or heldout execution/read was performed. Synthetic contract passes
do not close production blockers. Parent integration review remains separate.
