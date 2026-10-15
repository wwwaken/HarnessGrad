# Pristine source quiescence and export equivalence - w-quiesce

**E4 remains PARTIAL: the current pristine path cannot establish source quiescence
through scoring or native outer-run/trial binding. E5 now has real paired
pre/post-export equivalence for the unchanged authored control, and remains
PARTIAL for applicable datasets.** Neither shared blocker nor any dataset blocker
closes. E1/E2/E3/E6 remain PARTIAL. No production code, scorer logic, sealed fixture,
gate, historical run/archive or `runs/` path was changed.

Baseline: registered `/tmp/hg-quiesce`, branch `wg-quiesce`, HEAD
`5732fdf4d0ea4fd158d630e6f8763b300d35c1d3`. Read the E1-E8 reassessment,
w-prifix working control, admission contract and original E3 ownership finding
before collecting evidence. A separate read-only audit of the source paths agreed
that reversible same-UID chmod cannot supply writer exclusion.

All relative artifact paths below start at `reports/w-quiesce-evidence/`.
`final-control/` is a byte-identical copy of
`/tmp/hg-wquiesce-runtime/w-quiesce-20261015T021500Z-27bc6e91/packet/`;
`first-attempt/` retains the earlier incomplete packet from
`/tmp/hg-wquiesce-runtime/w-quiesce-20261015T020700Z-6d814ef2/packet/`.
Both external originals and their preparation/source trees remain on disk.
`copy-provenance.json` records 93 matching copies / 519778 bytes, including the
original helper and independent audit. The complete packet's own `SHA256SUMS`
seals 71 raw files; `audit.json` independently reconciles those files and all
55 unchanged fixture manifest entries. The outer evidence `SHA256SUMS` also seals
the retained partial packet, scripts and derived receipts.
That outer manifest has 97 entries and SHA-256
`84d90b392d1fda3d9f424c8b44cfb6e2e8d6591fe188debf38836b4b0f14eed2`.

## Exact commands and identities

Executed from `/tmp/hg-quiesce` (Python resolves to
`/mnt/8t/xubuqiang/anaconda3/bin/python3`):

```sh
python3 reports/w-quiesce-evidence/collect.py --work-root /tmp/hg-wquiesce-runtime --run-id w-quiesce-20261015T020700Z-6d814ef2
python3 reports/w-quiesce-evidence/collect.py --work-root /tmp/hg-wquiesce-runtime --run-id w-quiesce-20261015T021500Z-27bc6e91
python3 reports/w-quiesce-evidence/audit.py /tmp/hg-wquiesce-runtime/w-quiesce-20261015T021500Z-27bc6e91/packet /tmp/hg-wquiesce-runtime/w-quiesce-20261015T021500Z-27bc6e91/audit.json
```

Run IDs are opaque labels. Actual launch timestamps in the two `launch.json`
files are `2026-10-15T00:16:59.267026+00:00` and
`2026-10-15T00:18:11.491805+00:00`. The first helper aborted on a genuine stopped
reference admission refusal. `first-driver-executed.py` reconstructs its exact
executed bytes and matches the pre-execution script hash
`5bbfa8534f361b2535578e9116277b576ded73e8b5315e8644fe907d0e6affd0`.
The final collector hash is
`0cd4b9ca6ad29b1c7eb20178b519cb5ea9cf110dd579839ffa932fa8a2c6a1b9`.
Each launch records all five executed production-file hashes and its helper hash.
The only helper change handles bounded fresh attempts on existing environment-order
refusals; it never normalizes observations or bypasses a gate. Every final case
succeeded/refused as intended on attempt 01; no hidden retry supplied the pair.

| Identity / raw input | SHA-256 or value |
| --- | --- |
| Task / metric | `w-pristine-addition-control` / `exact-answer-command-exit0` |
| Unchanged bundle | `168d15a4945ea4ef093da3040fb7bd441ad1ec77ef4143379fbd1a6d318c4fbd` |
| Unchanged task contract | `28d615baa4b11c72c67f097e25025817f19a18e8abb3c22a6207e7172cda82e6` |
| Task specification source | `8e13963d42f2b87eb36756e9124922e24bc91ea9ef20af81ff15e9334dfd3f0b` |
| Runtime image | `sha256:3d32c18960e2cd4340c95b9cb3042581be0e2392959e6428fc06a37de334981d` |
| Submitted `41\n`, 3 bytes | `040316eca5e77dbb2212c1efe8b81cb23bc67ce0ac8cb5c9d902d98bd45ddfa1` |
| Private expected / changed `42\n`, 3 bytes | `084c799cd551dd1d8d5c5f9a5d593b2e931f5e36122ee5c793c1d08a19839cc0` |
| Unchanged fixture `SHA256SUMS` | `ef236df615c01463ffb3635b678ededc26211088d0a0ddf2778359ba19e8b2a0` |
| `final-control/SHA256SUMS` | `2b9061ef5315bce4fc409752ac99929539f37ab65c277acd7c5781bbca49fb4d` |

These come from fixture pins, actual file hashing, native export receipts and the
independent audit. `source_sha256` authenticates the task specification; submitted
state bytes have their own `files[].sha256`. Source/split/manifest/model identity
is explicit in `launch.json`: locally authored source, split=null, model=null,
model_sha256=null, endpoint=null. This is no-model diagnostic work, jobs=1,
trial=1 per distinct case, not a benchmark or staged pilot.

## E4: source quiescence is not established

`final-control/source-aba-attempt-01/events.json` records a real source write after
both projection checks and runtime admission succeeded. The callback changes only
the caller-owned source `aba-source/answer.txt` from `41\n` to `42\n`, keeps it
changed until `docker start --attach` returns after scoring, then restores `41\n`.
It changes no scorer/projection/gate or returned observation. It is a deliberate
same-UID platform-writer counterexample, not a launched dataset actor.

| Observed event | monotonic_ns |
| --- | ---: |
| Export returns | 6546430930720481 |
| Runtime admission returns successfully | 6546431113768410 |
| Source changed to `42\n` | 6546431115520023 |
| Immediately before Docker start | 6546431116676506 |
| Attached scorer returns | 6546431427466477 |
| Source restored to `41\n` | 6546431428601789 |

Before and after attached execution, source SHA-256 is the `42\n` digest while
the projection remains the `41\n` digest. Native `verdict.json` and raw
`docker-calls.json` record `actual=41`, `expected=42`, `completed_check=fail`, exit1,
score0.0, outcome=measured, normal stopped State and successful removal.
`source-before.bin` and `source-after.bin` both hash to the `41\n` digest. Their
equal endpoint contents therefore cannot establish interval quiescence. The saved
mtime/ctime do change; this is not a claim that mutation defeats a hypothetical
later metadata check. The production path performs no such source check.

The precise limitation is `eval/admission/artifact_admission.py:195-204`:
descriptor metadata is compared only around the individual copy read.
Lines 274-277 assign quiescence to the caller and explicitly disclaim establishing
it. `eval/verification/pristine.py:68-69` exports, then lines 96-103 recheck
projections, start and inspect the scorer without retaining source custody or
excluding source writers through use. `docs/scorer-admission-contract.md:32-37`
assigns source custody to callers. The fixture's `run_control.py:73-75` makes
owner-reversible 0444/0555 paths; line 89 disclaims same-UID mutation exclusion.
`eval/run/runner.py:519-525` saying the harness exited is not a descendant/external
writer exclusion observation. This demonstrates the current path's limitation;
it is not an impossibility claim about future backends.

### Task/run/trial binding at its actual scope

Every case has a distinct observer `binding.json`: outer run ID equals the final
packet ID plus case name, task ID is explicit, trial=1, and the source path/spec
are recorded before execution. The native working control export/runtime ID is
`hg-pristine-ebc5641c20b54dac93e265d8afe336e8`; the source-change witness ID is
`hg-pristine-d6492e5de92f4500844bd10329370396`. Native receipts bind the actual
submitted-byte hash, selected task, task source, contract and runtime/export ID;
`audit.json` lists all six actual created-container bindings.

`wrong-task/verdict.json` refuses `artifact contract task differs from selected
task`, score=null, with no export/create/start (`docker-calls.json` is empty).
Each production export also refuses a call to the real `verify_state_export`
using its genuine receipt with a different requested run ID:
`state export receipt identity mismatch`, preserved in `events.json`.

**This is observer-run/trial evidence, not native execution-bound outer-run/trial
inputs.** `eval/verification/verifier.py:456-460,474` forwards task_id only;
`eval/verification/pristine.py:36,38,68-69` accepts optional task_id and generates
its own runtime UUID. The native receipt at
`eval/admission/artifact_admission.py:329-334` has no trial or outer-run field.
Remaining E4: trusted source/writer custody through export and scoring, and an
actual backend contract receiving and enforcing execution-bound run/trial inputs.

## E5: paired control pre/post-export equivalence is established

The actual pre-state is the selected-only directory
`/tmp/hg-wquiesce-runtime/w-quiesce-20261015T021500Z-27bc6e91/paired-source-01`.
It was initially materialized with real `export_state`; its genuine receipt is
`final-control/source-materialization.json`. Direct scoring of this root passes
the original bundle/contract checks and `require_artifact_runtime`, including both
projection rechecks, before starting. It uses exactly two read-only binds and the
unchanged scorer/image/private expected input. No actor-workdir or third mount
is substituted. The reference container is
`hg-wquiesce-pre-b59ae486abf64c2d9ef7bad4f1a1d4a7`.

The **same root** is then the actual source passed through production
`verifier._verify` -> `pristine.verify` -> `export_state` -> scorer execution.
The resulting input root is `/tmp/hg-pristine-4qu8yhfw/input`; native export/runtime
ID is `hg-pristine-58fc6eda55794cc79f4ba304da36db5e`.

| Paired fact | Original selected-only source | Production exported state |
| --- | --- | --- |
| File / bytes | `answer.txt`, `41\n`, 3 | `answer.txt`, `41\n`, 3 |
| SHA-256 | `040316eca5e77dbb2212c1efe8b81cb23bc67ce0ac8cb5c9d902d98bd45ddfa1` | same, independently hashed |
| UID / GID / nlink | 1026 / 1026 / 1 | 1026 / 1026 / 1 |
| File mode / inode | 0444 / 1837519 | 0640 / 1837536 |
| Predicate reads | expected42 / actual41 | expected42 / actual41 |
| Completion / native stopped exit / score | fail / 1 / 0.0 | fail / 1 / 0.0 |

Raw evidence: `pre-state-attempt-01/{before,after,admission,result,docker-calls}.json`
and `post-export-attempt-01/{binding,events,verdict,docker-calls}.json`, plus
post-export `source-before.bin` / `export-answer.bin`. The pre-state before/after
inventory exactly matches the next export's source inventory. The private
expected/scorer/shell bytes rehash against the unchanged fixture; both actual
Docker inspections mount the same closure. `audit.json` records their three
digests. No numeric local replacement scorer is used.

The bounded transformation copies selected bytes into a fresh inode/path, changes
permissions/metadata and assigns the platform group; this run observes unchanged
UID/GID, 0444 -> 0640, and a new inode. The original working-control source also
contains `unselected.txt`; actual export inventory excludes it. The sealed
`closure/check.sh:4-5,21-26` reads only the first submitted/expected lines for the
predicate. Its cgroup/mount reads produce diagnostic stdout, not score inputs;
their output differs and is deliberately excluded from score equivalence.

**Established: equivalent under this documented authored-control contract for the
observed pre-state and actual production export. Not established: equivalent in
general, continuous source custody, direct scoring of an arbitrary full actor
filesystem, or applicable dataset/private-input/official-metric equivalence.**
The paired source is already selected-only; this does not pretend a direct full
actor mount passed admission. Remaining E5 is authoritative dataset-specific
transformations/private inputs and their chosen official metric/profile equivalence.

### Out-of-contract change and predicate sensitivity

`projection-tamper/` changes the selected exported bytes `41\n` -> `42\n` without
changing their length or the genuine receipt. `export-answer.bin` and
`tampered-answer.bin` preserve both byte strings. The production gate refuses
`state projection seal mismatch` at
`eval/admission/artifact_admission.py:382-383` before start; score=null and
outcome=unmeasured. It is not a measured zero. Separately,
`changed-answer-attempt-01/` legitimately exports fresh `42\n` under a fresh ID;
the unchanged scorer reads actual42/expected42, completed_check=pass, exit0,
score1.0, outcome=measured. Thus equal paired zeros do not conceal a constant scorer.

## Counts, refusals, resources and cleanup

`audit.json` reconciles the final packet: four production measurements (working,
post-export, source-change, changed-answer), one direct reference measurement,
two deliberately unmeasured production refusals (tamper, wrong-task), zero invalid
measurements, six created/six removed containers. Each measured case has one
eligible task, one selected task, one task/trial execution. These distinct controls
are not pooled into a benchmark score or pilot publication. The unchanged working
case alone is measured=1 / invalid=0 / unmeasured=0 / score0.0.

The initial packet separately retains one measured working score0.0 and one
unstarted direct-reference refusal, two created/two removed. Its actual Env was
`[HOME=/tmp,TMPDIR=/tmp,PATH=/control-scorer]`; required order is
`[PATH=/control-scorer,HOME=/tmp,TMPDIR=/tmp]`. `all-attempts-summary.json` retains
the actual historical observation, real checker re-derivation and exception
file/line. No observation was edited. The complete attempt used fresh IDs; all
its measured instances had the exact required Env. Initial binding fields lacked
the packet envelope; only final bindings are credited as run/trial evidence.

For every created final instance raw inspections observe NanoCpus=1000000000,
Memory=536870912, MemorySwap=1073741824, PidsLimit=128, cgroup namespace=private;
bounded tmpfs `/tmp`=1048576 bytes/64 inodes and `/control-output`=65536 bytes/16
inodes, nosuid/nodev/noexec. Successful scorer stdout samples cpu.max=`100000
100000`, memory.max=`536870912`, pids.max=`128`. Full commands, varying usage and
mount observations remain in `docker-calls.json`. Timeout is 60s per Docker/scorer
operation (the production verifier uses its total deadline); no model/GPU/endpoint
or paid service is used. Export limits remain 16 bytes / 2 inodes, actual3 / 2.

Every created instance has removal returncode0 and subsequent inspect returncode1
with `[]` / “No such object”. All production transient projections have
`exists=false` after verifier return. Preparation/source/reference trees and both
raw packets are retained. This is bounded object/projection cleanup; lifecycle=null,
no snapshot used, no exhaustive absence or ownership certificate is asserted.

## Validation and remaining work

```sh
python3 tools/check_dataset_blockers.py
python3 -m pytest -q tests/quality/test_quiesce_evidence.py tests/quality/test_prifix_regressions.py tests/quality/test_terminal_artifact_admission.py tests/quality/test_scorer_isolation_option_b.py tests/quality/test_dataset_blockers.py --basetemp=/tmp/harnessgrad-pytest-w-quiesce-final
python3 reports/w-quiesce-evidence/audit.py reports/w-quiesce-evidence/final-control /tmp/hg-wquiesce-runtime/w-quiesce-20261015T021500Z-27bc6e91/audit-copy.json
```

Exact checker/test output is `reports/w-quiesce-validation.txt`: registry valid
(28 datasets / 2 shared / 11 historical, production_authorized=false), **162 tests
passed**, copied packet audit valid, all evidence seals match, and diff check clean.
The focused audit
tests re-derive the retained packet and reject changed seals, mismatched source
paths, missing/reordered interval evidence, changed exported content, duplicate
completion markers, mismatched actual input mounts and a refusal mislabeled as
measured. Ten tests audit the new evidence; the rest cover the existing pristine,
admission and registry behavior. Repeated collection
requires a new run ID; repeated audit requires a fresh output filename.

Quiescence is unestablished and demonstrably unenforced by today's pristine path.
Pre/post-export scoring equivalence is established for this authored control's
selected-only transformation. E4 still needs trusted source custody plus native
run/trial enforcement; E5 still needs applicable dataset transformation/private-input
and official-metric equivalence. Both remain PARTIAL; no blocker closes.
