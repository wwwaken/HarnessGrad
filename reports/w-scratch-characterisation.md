# DS-1000 wrapper scratch characterisation - w-scratch

**Defect confirmed and fixed:** the DS-1000 verify wrapper allocated a directory
with `mkdtemp` and never removed it. This is a wrapper lifetime defect, not an
observed escape from the collector's cleanup scope. No equivalent allocation was
found in the LiveCodeBench or BIRD wrappers; fresh authored controls agree.

## Evidence and reproduction

Read `reports/w-jvm-runtime-observations.md` and its evidence packet first.
`sha256sum -c reports/w-jvm-evidence/SHA256SUMS` verified all 338 entries; raw output
is `reports/w-scratch-evidence/original-manifest-check.txt`. The original observed
directory was `/tmp/ds1000-check-rugl1mm4`, retained under
`reports/w-jvm-evidence/followup/ds1000/after-scratch/` before collector removal.
Original scratch inventory and cleanup are respectively
`reports/w-jvm-evidence/followup/ds1000/scratch-observations.json` and `cleanup.json`.

Executed these fresh, serial, authored controls with the existing collector:

```sh
python3 tests/fixtures/hg_wjvm/collect.py --output reports/w-scratch-evidence/before --runtimes ds1000 livecodebench bird_minidev
python3 tests/fixtures/hg_wjvm/collect.py --output reports/w-scratch-evidence/after --runtimes ds1000
```

The first invocation precedes the fix, ID `w-jvm-20261015T003129Z-2f78e965`;
the second follows it, ID `w-jvm-20261015T003308Z-f03ddab1`. Each case has a
50-second outer bound, a fresh network namespace without external routes,
30-second CPU / 8-GiB address-space rlimits and two-CPU affinity. These are local
control limits, not production enforcement evidence. Full argv, environment,
limits, sources/digests, inputs, native verdicts, process observations and cleanup
are under `reports/w-scratch-evidence/{before,after}/`; collection stdout is in
`before-collection.txt` and `after-collection.txt` alongside those directories.
No benchmark rows, model, GPU, endpoint or benchmark driver were used.

Before the fix, the check PID **621082** created
`/tmp/ds1000-check-g_vvdeqq`; runner PID **621086** executed from it.
`reports/w-scratch-evidence/ds1000-scratch-syscalls.txt` extracts the actual
mkdir/exec/removal calls from the retained compressed traces. The creator is
the **verify wrapper itself**, not upstream `execution.py` or its candidate child:
pre-fix `data/datasets/ds1000/verify/check.py:34` allocates it, lines 35–44 write
its files, and lines 53–54 launch the runner. The exact pre-fix file is saved at
`reports/w-scratch-evidence/before/ds1000/inputs/verify/check.py` with identical
line numbering. `reports/w-scratch-evidence/source-review.txt` retains these
lines and the cleanup-contract excerpts.

| Leftover file | Bytes | Contents |
| --- | ---: | --- |
| `execution.py` | 5791 | Copied official execution implementation. |
| `program.json` | 187 | JSON string containing the authored test context, candidate `result = 1 + 2` with a short sleep, and `test_execution(code)`. |
| `run_ds1000.py` | 161 | Imports `check_correctness`, reads that JSON, invokes it with timeout 120, prints its result. |

The complete bytes and SHA-256 values are in
`reports/w-scratch-evidence/before/ds1000/after-scratch/ds1000-check-g_vvdeqq/`
and `reports/w-scratch-evidence/before/ds1000/scratch-observations.json`.
The audit verifies all three files are byte-identical to the original w-jvm
leftovers. Upstream candidate `/tmp/tmp_q6iiv97` and manager
`/tmp/pymp-f3owxg8w` were removed, while the wrapper directory survived check
exit. No collector child reaping or forced process cleanup was needed.

## Ownership, lifetime and decision

The collector binds its owned host directory
`/tmp/w-jvm-20261015T003129Z-2f78e965/ds1000/scratch` over the check's `/tmp`.
Thus the observed wrapper directory is **outside the task work directory but
inside the collector's owned scratch root**. Its `after_check` inventory records
the leak; its later `cleanup.json` records successful collector removal. The
original w-jvm packet uses the same arrangement. Calling this an escape beyond
the collector's cleanup scope would contradict those receipts.

Production also deliberately permits temporary storage: host sandbox checks
get private `/tmp` (`eval/verification/verifier.py:600`,
`eval/containers/sandbox.py:266`); container checks use `/tmp` tmpfs and `--rm`
(`eval/containers/container.py:540`, `:549`). Pristine verification owns its
host projection via `TemporaryDirectory` and forcibly removes its container in
`finally` (`eval/verification/pristine.py:51`, `:130`). Admission cleanup checks
supplied owned identities/absence facts rather than performing deletion
(`eval/admission/runner_admission.py:248`); the control backend validates ownership
before removal and retains cleanup errors (`eval/admission/pilot_admission.py:484`).
`docs/runner-admission-contract.md:123` explicitly retains uncertainty for missing
observations while refusing known leftovers. The fix changes none of that policy.

The **location** is appropriate, but leaving copied executor and candidate/test
payload indefinitely has no declared retention purpose. Direct host checks lack
the private-tmpfs fallback (`eval/verification/verifier.py:616`), so removing the
task directory alone cannot remove this allocation. A separate bounded host
reproduction demonstrates this with an explicitly isolated `TMPDIR` outside the
task directory:

```sh
python3 reports/w-scratch-evidence/host-reproduction.py --check reports/w-scratch-evidence/before/ds1000/inputs/verify/check.py --output reports/w-scratch-evidence/host-before
python3 reports/w-scratch-evidence/host-reproduction.py --check data/datasets/ds1000/verify/check.py --output reports/w-scratch-evidence/host-after
```

`reports/w-scratch-evidence/host-before/observation.json` records
`/tmp/w-scratch-host-4q2jsoyw/ambient-tmp/ds1000-check-pigii4f4` surviving both
check exit and removal of `/tmp/w-scratch-host-4q2jsoyw/task`. Its bytes were
archived before the reproducer removed its whole fresh root. The fixed host
control (`reports/w-scratch-evidence/host-after/observation.json`) has empty scratch
after both operations, with identical native evidence and stdout. These commands
use only the authored arithmetic inputs and actual upstream executor, with an
8-second outer subprocess bound. Every output directory is exclusive; the listed
commands must use new output paths for another execution.

## Fix and other runtimes

`data/datasets/ds1000/verify/check.py:35` now owns the allocation with
`TemporaryDirectory`, encompassing file preparation and `subprocess.run`.
Its context exits before result parsing/output, removing wrapper files on normal
return and Python exceptions. Candidate construction, conditional `test_string`,
upstream execution bytes, environment, timeouts and reward/evidence logic are
unchanged. In the fresh fixed trace, PID **623156** successfully removes
`/tmp/ds1000-check-k37wwntg`; only collector-created `control` and `home` remain.

| Runtime | Same unpaired wrapper scratch pattern? | Basis |
| --- | --- | --- |
| DS-1000 | Yes before fix; removed after fix. | Fresh before/after inventories and syscall traces. Upstream already uses `TemporaryDirectory` for candidate scratch (`before/ds1000/inputs/execution.py:102` in the new packet). |
| LiveCodeBench | No in the reviewed wrapper or exercised path. | `data/datasets/livecodebench/verify/check.py:62` imports materialized files from the task directory; `:168` launches a process/queue without allocating a wrapper temp tree, and `:171`/`:174` join it. Fresh `before/livecodebench/scratch-observations.json` contains only collector `control`/`home`. |
| BIRD Mini-Dev | No in the reviewed wrapper or exercised path. | `data/datasets/bird_minidev/verify/check.py:105` opens SQLite in the check process; `:126` closes it in `finally`. It allocates no wrapper temp tree or SQL subprocess. Fresh `before/bird_minidev/scratch-observations.json` contains only collector `control`/`home`; `after-work/` retains only authored inputs and the copied check. |

This agrees with w-jvm's other runtime observations: Jericho's native temporary
directory was removed; ScienceWorld removed its temporary directory/per-process
JVM marker but left an empty JVM marker directory; SpreadsheetBench removed its
profile/conversion tree while home caches persisted until collector cleanup, and
its failed attempt left an IPC socket. Those documented library/cache/process
limits are different from this unpaired DS-1000 wrapper allocation.

## Validation and limits

`tests/quality/test_ds1000_scratch_cleanup_w_scratch.py` tests cleanup and retention
of unrelated scratch across success, candidate failure, simulated timeout exception,
simulated spawn error and missing executor during setup. The test uses an authored
dependency stub to isolate wrapper lifecycle; actual upstream execution is covered
by the separate control packet. All five tests fail on the old allocation and
pass on the fix (`regression-before.txt`, `regression-after.txt` in the new packet).
Focused tests plus source-only blocker tests pass **59/59**; the blocker checker
remains valid with `production_authorized=false`. Raw output and commands are in
`reports/w-scratch-validation.txt`. `reports/w-scratch-evidence/audit.py` validates
the packet without re-executing a scorer; `audit.json` retains its output, and
`reports/w-scratch-evidence/SHA256SUMS` seals the packet.
Copied upstream files and raw `/proc` output retain their original whitespace;
the full staged whitespace check reports those evidence bytes, while the scoped
code/test/documentation check passes. Both results are retained in validation.

This fixes only wrapper-owned files during Python unwinding. SIGKILL, whole-check
termination, upstream descendant timeout/reaping, broader scientific-library tasks,
SQLite mutation/spill paths, LCB error/timeout paths and production resource or
cleanup enforcement are not established here. Private namespace/container cleanup
remains the fallback for abrupt termination. Both shared blockers, all dataset
blockers and registry bytes remain unchanged: `scorer-offline-closure` remains
open/code-solvable; S1/S3/S4/S6 and S5 remain **PARTIAL**. No H0 authorization,
`runs/` access, frozen receipt modification or existing-ID reuse follows.
