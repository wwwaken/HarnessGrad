# ScienceWorld platform-write prevention review — Codex 186

Base: `d21d79d`, containing `34a472a7c9e5c4e94452df1b018d0b202f60a84f`.
Isolated worktree: `/tmp/hg-codex-186`; all authored files and test scratch stay here.

Code-solvable prevention review is closed for the existing default native sandbox
route. The machine registry retains `prevent-platform-writes` with status
`runtime`: effective backend enforcement remains unverified. No production or
H0 readiness follows from this review.

`34a472a` changes attribution wording and adds synthetic mismatch tests. It
does not implement write prevention. The current source already supplies that
plan in `eval/sandbox.py::command`: protected platform paths are hidden before
the entrypoint, and required source trees are bound read-only. Native harness
launch in `eval/runner.py::run_one` and sandboxed method entrypoints in
`harnessgrad/methods.py::_call_entrypoint` use this path. The method plan supplies
an explicit candidate `repo` rather than defaulting to the platform, with
read-only visibility for its own program. Requested sandbox failures refuse
execution; explicit unsandboxed paths retain detection only. Source comments
that describe hashing as detection do not negate this separate sandbox path.

The new regression inspects generated plans for inert harness, verifier and
method layouts, covering platform hiding, read-only source restoration,
verification artifacts frozen except for the verdict directory, and refusal
before process execution when the sandbox is unavailable. Adapter imports,
sockets and subprocesses are denied in the new suite; its sandbox binary and
runtime paths are synthetic. It executes no namespace or entrypoint. The
existing Codex 181 suite separately verifies fatal added/removed/modified
mismatches with unknown writer/tracking attribution and legitimate candidate
changes outside protected paths. Its only child processes are temporary Git
fixture indexing commands.

The registry regression preserves the runtime classification, evidence links,
shared runtime gate and `production_authorized=false`, and compares ScienceWorld
history exactly with the independently pinned baseline. All shared blockers,
other dataset rows and every historical registry record remain unchanged.
The entire original ScienceWorld V4 journal section remains unchanged, including
the old unverified candidate citation. Neither that external candidate nor
external run receipts were opened or applied. The historical
`scienceworld-h0-10pct-v4` stays `incomplete`, `effect=null`; 354/354 and diagnostic
mean `0.1380508475` remain historical journal claims, not newly measured results.
Writer attribution remains unknown.

Remaining work is independent trusted observation of effective runtime mounts
and immutable platform provenance, plus all shared admission requirements.
This review does not establish backend enforcement, JVM/scorer behavior,
cleanup or snapshot completion. Future authorized diagnostics require all
dataset gates, a fresh run ID and the staged AGENTS.md protocol.

Validation:

```sh
mkdir -p .scratch/scienceworld-platform-writes-codex186
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/tmp/hg-codex-186/.scratch/scienceworld-platform-writes-codex186 \
python3 -m pytest -q -p no:cacheprovider \
  --basetemp=/tmp/hg-codex-186/.scratch/scienceworld-platform-writes-codex186/pytest \
  tests/quality/test_scienceworld_platform_writes_codex186.py \
  tests/quality/test_scienceworld_integrity_codex181.py \
  tests/quality/test_dataset_blockers.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py
git diff --check
```

Results: **64 passed in 3.36s**, no failures/skips; registry valid with **28
datasets, 8 shared blockers, 11 historical records**,
`production_authorized=false`; whitespace check passed. Reviewed the complete
diff, including the new test and report. Compared every historical record,
non-ScienceWorld row, shared blocker, history fixture bytes and original V4
journal section against `d21d79d`; all are unchanged. Owned test scratch was
removed after validation. Only the two registry/journal documents, the registry
test, the new synthetic regression and this unique report are committed.
No real-data/runtime/model/H0 execution, production-source edits or main-branch
changes were performed.
