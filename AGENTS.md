# HarnessGrad Agent Operating Rules

## Execution priorities

1. Close automatically solvable blockers and internalize reusable platform capabilities before launching large pilots.
2. Use isolated Codex worktrees only. Parent reviews every diff, runs focused tests, rejects stale reports and unrelated changes, then merges safe commits and updates the journal.
3. Keep up to 10 independent Codex tasks active when work can be parallelized. Every task must have a unique output filename; never trust inherited `reports/report.md` without checking the diff and commit.
4. Avoid idle rounds: combine waits with concrete receipt inspection, diff review, test execution, journal work or launch preparation. Do not spend a round only polling unchanged status.

## Test execution

Pytest `--basetemp` must be **OUTSIDE the platform tree**, for example
`--basetemp=/tmp/harnessgrad-pytest-quality`. Driver-based tests use `tmp_path`
as a harness work root, which the runner correctly refuses inside the platform.
Omitting the option preserves pytest's normal default.

## GPU execution

- GPU0: endpoint `http://127.0.0.1:8001/v1`.
- GPU1: endpoint `http://127.0.0.1:8002/v1`.
- Keep both GPUs productively occupied with necessary no-model controls, diagnostics or valid pilots; never create duplicate, fake or scientifically unjustified work for utilization.
- Bind each run to one endpoint and one fresh run ID. Keep total H0 concurrency `<=3`, `jobs=1`.

## Staged pilot policy

- First run a one-task/one-trial diagnostic after all dataset gates pass.
- For temporary reruns of blocked/incomplete datasets, select `min(30, ceil(10% * eligible))` tasks before execution, with `trials=1`, `jobs=1`.
- Expand only after a separate review of a valid measured diagnostic receipt. Do not silently revert to the historical `min(50, ceil(10% * eligible)) x 3` protocol.
- Invalid, unmeasured, timeout, scorer, provider, cleanup or snapshot failures are not ordinary zero scores.
- Preserve old and incomplete receipts; never resume or overwrite an old run ID.

## Dataset taxonomy

Task capability is a cross-table: `demand x surface`. Harness coverage is a separate axis: `exercises`. Do not collapse these into one flat dataset category.

## Prohibited shortcuts

No method tuning, paid endpoints, heldout leakage, SOTUQA, API-Bank, NESTFUL, Tau2-bench, Matrix, score fabrication or fake benchmark utilization.

## Evidence requirements

Every diagnostic or pilot records metric identity, eligible/selected/task/trial coverage, invalid and unmeasured counts, source/split/manifest/model/harness hashes, endpoint binding, resource/budget limits, cleanup receipt and comparability notes.

## Blocker closure priorities

Prioritize selected-only/privacy and provenance, scorer dependency/network and offline closure, trusted verifier/runtime, artifact-only state export, filesystem quota enforcement, official scorer execution, snapshot lifecycle and cleanup. A passing synthetic control is not a production H0 authorization.
