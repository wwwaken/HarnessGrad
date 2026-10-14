# Real production pristine diagnostic attempt - w-pristine

**The production pristine path executed, but the answer check did not.** A real
stopped Docker instance passed admission and both projection rechecks, started,
then exited on `Permission denied` reading the exported answer. The native verdict
returned `score=0.0`; this is an **invalid/unmeasured scorer failure**, not a genuine
zero. No production fix, gate relaxation, UID override or second production attempt
was made. Unexpected image/network/mount controls genuinely refused before start.

Artifact paths below are relative to `tests/fixtures/hg_wpristine/`; paths starting
with `eval/`, `docs/` or `reports/` are repository-relative. Every raw captured original remains under
`/tmp/hg-wpristine-runtime/w-pristine-control-20261014T225600Z-7cbd8f16/evidence/`
as well. The audited receipt and later summaries are additional files in the fixture,
not replacements for original receipts. `SHA256SUMS` pins the complete fixture.

## Exact execution and authored contract

Executed from `/tmp/hg-pristine`:

```sh
python3 tests/fixtures/hg_wpristine/build_control.py
python3 tests/fixtures/hg_wpristine/run_control.py --work-root /tmp/hg-wpristine-runtime --run-id w-pristine-control-20261014T225600Z-7cbd8f16
python3 tests/fixtures/hg_wpristine/audit_control.py --evidence tests/fixtures/hg_wpristine/evidence
```

`build-evidence/commands.json` records every actual build/inspection command and
stdout/stderr, including `docker build --pull=false --network=none --iidfile ...`
and `docker image save --output ...`. `evidence/launch.json` records the exact
interpreter/argv/cwd, timestamp, source hashes, work root and initial inventories.
Its UTC timestamp is the execution timestamp; the external run ID is an opaque label.
Harness base commit is `cc4dc28ea66c585a9c4afd8204f93d21df814368`.

This calls the **real production dispatcher** at `eval/verification/verifier.py:468-475`
and the unmodified pristine backend. No dataset is added. It is a scorer-runtime
diagnostic, not a full runner/policy-admitted staged pilot; no actor harness, model,
GPU, paid endpoint or model endpoint is used (`evidence/launch.json`: endpoint/model=null,
trials=1, jobs=1). Production authorization stays false.

| Identity | Exact value / artifact |
| --- | --- |
| Bundle SHA-256 | `168d15a4945ea4ef093da3040fb7bd441ad1ec77ef4143379fbd1a6d318c4fbd` — `bundle.json`, independent `trusted-pins.json` |
| Contract SHA-256 | `28d615baa4b11c72c67f097e25025817f19a18e8abb3c22a6207e7172cda82e6` — `task-contract.json`, independent `trusted-pins.json` |
| Source SHA-256 | `8e13963d42f2b87eb36756e9124922e24bc91ea9ef20af81ff15e9334dfd3f0b` — exact `task-source.json` bytes |
| Runtime image ID | `sha256:3d32c18960e2cd4340c95b9cb3042581be0e2392959e6428fc06a37de334981d` — `build-evidence/image-id.txt`, `build-evidence/image-inspect.json`, actual `evidence/inspect-01.json` |
| Runtime/export ID | `hg-pristine-476fa4a67f8f422e9f18e2d0027b32ba` — `evidence/verdict.json` export and cleanup |
| Task / metric | `w-pristine-addition-control` / `exact-answer-command-exit0` — `task-source.json`, `evidence/measurement-audit.json` |
| Sealed scorer command | `["/control-scorer/sh", "/control-scorer/check.sh"]` — `bundle.json`, `evidence/verifier-spec.json` |

The local image is `FROM scratch` with one diagnostic marker and no volumes.
`build-evidence/image-inspect.json` records a builder/default PATH environment;
the actual scorer's exact three-variable environment overrides it. The complete
save is `build-evidence/image.tar`; `build-evidence/image-save-members.json`
recomputes every member digest, including the 855-byte image-config blob whose
SHA-256 is the runtime image ID. No registry/official provenance is claimed.
`closure/sh` is the actually installed static BusyBox, SHA-256
`b3c1009e1b5c927e537487c80639cdf404f69e3eb49371d9be5d841672be3ff9`;
actual `file`, `readelf -l` and package output are in `build-evidence/commands.json`, with copyright
saved separately. The scorer graph has three reachable pinned files, 2194251 bytes;
it does not claim a complete closure for any existing dataset.

The task is locally authored addition, 19+23. `closure/expected.txt` is `42\n`,
SHA-256 `084c799cd551dd1d8d5c5f9a5d593b2e931f5e36122ee5c793c1d08a19839cc0`,
and is a sealed dependency outside actor state. The controlled submission is `41\n`;
its actual export SHA-256 is
`040316eca5e77dbb2212c1efe8b81cb23bc67ce0ac8cb5c9d902d98bd45ddfa1`.
The authoritative control-only contract permits only non-executable `answer.txt`,
max_bytes=16, max_inodes=2. This provisions export/private-input instances for this
synthetic task alone; it does not satisfy dataset-wide E1/E2 or official equivalence.

`evidence/launch.json` inventories actor files `answer.txt` and `unselected.txt`,
both mode `0o444`, UID 1026; no private expected file enters actor state. No actor is
launched. Same-UID platform preparation and read-only source files do not establish
race-proof quiescence or exclusion of an external same-UID writer. The driver copies
the fixture into external `platform/scorer/{bundle.json,closure}` and
`platform/contracts/task.json`; pins remain outside the actor. No `runs/` is touched.

## Actual inspection, rechecks and verdict

`evidence/docker-calls.json` is an ordered capture of **actual** `container.docker`
returns using `sys.setprofile`, not replacement functions or a Docker double:
create → inspect → start --attach → inspect → rm --force. Exact argv/stdout/stderr
are additionally in `evidence/docker-00.json` through `evidence/docker-04.json`.

`evidence/inspect-01.json` is the raw stopped-instance inspection:
`State.Status="created"`, `Running=false`, pinned Image as above,
`NetworkMode="none"`, `ReadonlyRootfs=true`, `CapDrop=["ALL"]`,
`Env=["PATH=/control-scorer","HOME=/tmp","TMPDIR=/tmp"]`.
The two actual binds both have `Type="bind"`, `RW=false`, `Propagation="rprivate"`:

| Destination | Actual source |
| --- | --- |
| `/control-input` | `/tmp/hg-pristine-sfa9udgm/input` |
| `/control-scorer` | `/tmp/hg-wpristine-runtime/w-pristine-control-20261014T225600Z-7cbd8f16/platform/scorer/closure` |

`evidence/projection-rechecks.json` captures the original production calls and
their returns. After the inspection at monotonic_ns=6541252297577976 (see raw
`evidence/docker-01.json` for the authoritative timestamp), `verify_scorer_files` returns
`files=3, bytes=2194251` at 6541252310673567; `verify_state_export` returns normally
at 6541252319024541. The artifact inventory contains only `answer.txt`, bytes=3,
mode=`0o600`, UID=1026, nlink=1, matching the receipt hash. The final runtime check
returns `scope="inspected_runtime_contract"` at 6541252325913206, before the start
return at 6541252615057135. Both original projections were rechecked; a null return
from `verify_state_export` is its normal success return, corroborated by the later
successful runtime receipt and actual start. These observations do not attest
that bytes cannot change after the recheck.

`evidence/verdict.json` records executed and declared class `pristine-offline`, with
all four native evidence keys: bundle/export/runtime/cleanup. Export has bytes=3,
inodes=2, limits={max_bytes:16,max_inodes:2}, selected task, contract/source hashes
and the exact generated runtime/export ID. Raw `passed=false`, `score=0.0`,
`detail="sealed scorer exit 1"` is preserved **without treating it as measurement**.

## Resource observations and lifecycle limits

These are raw fields inspected from the actual created instance, **not copied
launch declarations**: `evidence/inspect-01.json`, summarized with scope and source
in `evidence/resource-observations.json`.

| Observed Docker field | Raw value |
| --- | --- |
| `HostConfig.NanoCpus` | `1000000000` |
| `HostConfig.Memory` | `536870912` |
| `HostConfig.MemorySwap` | `1073741824` |
| `HostConfig.PidsLimit` | `128` |
| `HostConfig.Tmpfs["/tmp"]` | `rw,nosuid,nodev,noexec,size=1048576,nr_inodes=64,mode=1777` |
| `HostConfig.Tmpfs["/control-output"]` | `rw,nosuid,nodev,noexec,size=65536,nr_inodes=16,mode=1777` |

This establishes applied Docker configuration, not kernel readback, peak usage or
infallible enforcement. Effective cgroup CPU/memory/PID values and kernel tmpfs
bounds are **unknown**: the script failed before its cgroup/mountinfo observation
loop. No values are substituted from the declarations. `evidence/host-observations.json`
retains actual `id` and `docker info` commands: UID/GID=1026, cgroup driver=systemd,
version=2, AppArmor/seccomp and cgroup-namespace support reported by Docker.
The actual `HostConfig.CgroupnsMode="private"` is in `evidence/inspect-01.json`.
Formal lifecycle remains `null`; no formal lifecycle backend receipt was emitted.

## Real failure, audited counts and production defects

`evidence/docker-02.json` records `docker start --attach` returncode=1, stdout="",
and exact stderr:

```text
/control-scorer/check.sh: line 5: can't open /control-input/answer.txt: Permission denied
```

No `completed_check=fail` or `completed_check=pass` marker was emitted. The scorer
did read its private expected dependency first, but failed before comparing answers.
`evidence/inspect-03.json`: `Status="exited"`, `Running=false`, `ExitCode=1`,
`OOMKilled=false`, `Error=""`, StartedAt=`2026-10-14T22:51:55.278462757Z`,
FinishedAt=`2026-10-14T22:51:55.431904266Z`. Normal process exit is not evidence
that the scoring predicate completed.

1. **Unreadable platform export:** `eval/admission/artifact_admission.py:280,289,292`
   creates the projection directories mode 0700 and files 0600, owned by the calling
   user. Observed exported file ownership/mode is UID 1026/0600. The created image
   has `Config.User=""` (default container root), and
   `eval/verification/pristine.py:67-82` drops all capabilities without aligning
   the container user to export ownership. `evidence/inspect-01.json` corroborates those
   actual settings. On this host it prevents reading the projection. Retained
   negative-probe export directories also actually stat as UID 1026/mode 0700
   (`evidence/host-observations.json`). No chmod/chown/user/capability workaround was used.
2. **Invalid scorer exit becomes numeric zero:**
   `eval/verification/pristine.py:100-108` checks Docker state/OOM/error and maps
   every normal nonzero exit to score 0. This shell initialization failure passes
   that condition. For the generic exit-status protocol, scorer initialization
   and a completed failing check are indistinguishable; this authored control's
   completion marker exposes the difference. No production code was changed.
3. **Stopped result not retained natively:** pristine.py:97-103 reads stopped
   State but does not put it into `scorer_isolation_evidence`; :115-118 retains
   only cleanup name/removal Boolean. Raw inspection/removal evidence exists here
   because the external observer saved the real outputs, not because the native
   verdict contains a stopped-result field.

`evidence/measurement-audit.json`, derived by the recorded audit command from
unchanged raw artifacts, is the measurement decision:

| Control coverage / measurement | Value |
| --- | --- |
| eligible / selected tasks / expected trials | `1 / 1 / 1` |
| completed answer checks / genuine measured zeros | `0 / 0` |
| measured / unmeasured / invalid trials | `0 / 0 / 1` (disjoint counts; invalid means no valid measurement) |
| publishable score | `null` |
| raw native verdict score | `0.0` (invalid for this metric) |
| formal lifecycle / production_authorized | `null / false` |

These disjoint counts follow `eval/policy/diagnostic_policy.py:108-114`: scorer
failures must be invalid or unmeasured; a measured zero requires a successful
measurement contract. The initial `evidence/audited-control-receipt.json` treated invalid
as a subset of unmeasured (0/1/1); it is preserved as a superseded provisional
classification. The final `evidence/measurement-audit.json` partitions the single trial.

The executed driver's first count inference used the numeric verdict and therefore
wrote `measured_trials=1, unmeasured_trials=0, invalid_trials=0` to the original
`evidence/control-receipt.json`. That artifact and `evidence/driver-executed.py` remain unchanged and
are explicitly superseded by the audit, never republished as valid measurement.
The current fixture driver requires the completion marker for future counts; it
was not rerun. No staged pilot receipt or curve score was published.

## Refusals and cleanup, with raw outputs

Three separate **real stopped-instance admission** probes (not task trials) create
actual containers differing from the valid launch in image, network, or extra bind.
Each uses a fresh export with its own run ID and the original production
`require_artifact_runtime` at `artifact_admission.py:378-436`. No inspected JSON is
mutated. These checks do not rerun the production dispatcher or start the scorer.

| Probe / artifacts under `evidence/` | Actual unexpected observation | Actual refusal |
| --- | --- | --- |
| `refusal-image-{inspect,result,commands,export}.json` | `Image="sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce"` from `evidence/alternate-image-inspect.json`, different from the pin | `AdmissionError: trusted artifact runtime boundary mismatch` |
| `refusal-network-{inspect,result,commands,export}.json` | `NetworkMode="bridge"` | `AdmissionError: trusted artifact runtime boundary mismatch` |
| `refusal-mount-{inspect,result,commands,export}.json` | third read-only bind at `/unexpected` | `AdmissionError: artifact-only read-only mounts required` |

`evidence/refusal-counts.json` and `evidence/refusals-summary.json`: controls=3, refused=3, started=0,
scored=0, removed=3. Every result has score=null, removed=true, and post-removal
inspect returncode=1. Each commands file contains the real create, inspect, remove
and absent-object inspection outputs. Refusal source is :399-412 (image/network)
and :426-436 (binds). The compliant main instance was **not refused** at admission;
its scorer later failed on file access.

Network-specific causality is **not isolated**: the real bridge instance also has
`Config.Env=["HOME=/tmp","TMPDIR=/tmp","PATH=/control-scorer"]`, whereas the
exact required order is PATH/HOME/TMPDIR. The strict list equality at :402 rejects
before the network clause at :404. These same three assignments have identical
meaning but Docker returned a different order. No observation was normalized or
rerun to conceal it. The image mismatch is checked first at :399; the extra-bind
probe has the required environment order and reaches the mount refusal. Focused
synthetic tests cover the network check, but this live probe alone does not.

Main stopped result **exists** at `evidence/inspect-03.json`. Removal receipt
**exists** at `evidence/docker-04.json`: returncode=0, stderr="", stdout is the
runtime name plus newline; native `evidence/verdict.json` cleanup has `removed=true`.
`evidence/post-removal-inspect.json`: returncode=1, stdout=`[]\n`, stderr=`error: no such
object: hg-pristine-476fa4a67f8f422e9f18e2d0027b32ba\n`.
`evidence/post-return-projection.json`: `/tmp/hg-pristine-sfa9udgm/input`, exists=false.
This is bounded object/projection cleanup evidence, not exhaustive namespace
absence. External work roots, negative-probe exports, image archive and historical
receipts are preserved; no snapshot was created. Snapshot lifecycle is not inferred.

## Shared blocker decision and validation

**Neither shared blocker closes.** Their observed text now records one failed
production pristine-offline control, explicit control-only export/private-input
contracts, actual inspection/rechecks/refusals/configuration/cleanup, and the
invalid-zero defect. S2/S5 and E1/E2/E6 gain evidence at that exact scope; they do
not become fully satisfied. S1/S3/S4/S6 and E3-E6 remain partial across the surveyed
datasets. Original next_actions/statuses, every dataset blocker/reference and all
historical records are retained.

`reports/w-pristine-validation.txt` records the registry checker and focused
existing test output, plus independent fixture-hash/admission/audit checks.
Source-only tests do not repair or validate the failed live measurement.
