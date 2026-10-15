# Live lifecycle and cleanup observations - w-e6

**E4/E5/E6 remain PARTIAL. No shared or dataset blocker closes.** Current
AppWorld service caps are observed live. Its mounted verifier leaks on timeout:
the service is removed, but the verifier retains the recording mount and prevents
network removal until collector rescue. GAIA/Tau image snapshot controls remove
their verifier containers on normal return and timeout. A native sandbox control
observes child waits and namespace teardown without a collector resource envelope.
These are authored lifecycle predicates, never benchmark scores or pilot admission.

Registered worktree `/tmp/hg-e6`, branch `wg-e6`, starting HEAD recorded in
`reports/w-e6-evidence/preflight/git-head.stdout.txt`. Read AGENTS.md and the four
requested reports before execution. No production source, gate, admission,
refusal, dataset record, historical receipt, frozen copy or `runs/` path changed.
Every execution used a fresh UUID-bearing ID and an external `/tmp` work root.
All evidence below is under `reports/w-e6-evidence/` unless otherwise stated.

## Source-confirmed uncovered branches

`source-audit.json` derives **23** participating datasets from actual registry
references, rather than assuming all 28 entries share this blocker. It records
complete-file hashes and exact matching lines for **43** files. Numbered full
source copies are in `source/`, preserving the reviewed line numbers. AgentDojo
and the four refused/prohibited entries have no reference to this shared blocker;
none was run. No new branch is inferred from those entries.

The reassessment already credits the historical AppWorld mounts/teardown; the
remaining AppWorld gap is current caps plus untested error/timeout behavior.
The w-jvm report explicitly says its six controls are *not production verifier*
runs. Component scorer execution elsewhere does not establish process cleanup.

| Current dispatch branch and exact source | What remained uncovered at entry; coverage added here |
| --- | --- |
| Explicit pristine: `eval/verification/verifier.py:478`, `eval/verification/pristine.py` | Already credited by w-prifix/w-bind/w-quiesce. No dataset opt-in currently exists; no redundant rerun here. E4 custody and E5 real-dataset equivalence remain separate. |
| In-process answer: `eval/verification/verifier.py:558`; Chess controller dispatch: `eval/run/runner.py:521` | Historical w-chess3 covers a bounded controller exchange. No subprocess is launched by the answer comparison. Other controller termination/error branches are not supplied by a generic command control. |
| Mounted exec/service: `eval/verification/verifier.py:497`, `:610`, `:618`; `eval/containers/container.py:577`, `:611` | AppWorld adapter `data/datasets/appworld.py:267`, `:294`, `:303`; service caps at `eval/service/services.py:399`; recording creation `:376`, RW bind `:405`, RO verifier bind `:475`; stop `:206`. Corrected service caps, normal and timeout mounted verifiers now exercised. Actual AppWorld evaluator replay is not rerun. |
| Actor snapshot: `eval/run/runner.py:235`; `eval/containers/container_state.py:190`, `:213`, `:235`; `eval/verification/verifier.py:241`, `:264`, `:412` | GAIA `data/datasets/gaia.py:99`, `:196` and Tau `data/datasets/tau_bench.py:182`, `:328` had no matching live route control. Added authored-state normal/timeout controls using their exact cached image defaults and production snapshot/verifier helpers. TB `data/datasets/terminal_bench.py:194`, `:231` has w-net coverage; its other images/bootstrap/task/error branches remain uncovered. |
| Native sandbox command: `eval/verification/verifier.py:627`, `:643`; `eval/containers/sandbox.py:395`, `:420` | Historical ALF observes a selected noop; w-jvm uses a different collector envelope. Added the actual `_verify` → sandbox branch with normal child wait and timeout. This is generic branch evidence, **zero new native dataset scorers**. |
| Unsandboxed native command: `eval/verification/verifier.py:648` | `sandbox=False` goes directly to `subprocess.run`. Not exercised or substituted for the sandbox branch; no child-tree cleanup guarantee is established by source inspection. |
| Reward/input and exception branches: `eval/verification/verifier.py:491`, `:512`, `:566`, `:651`, `:656`, `:674`; snapshot input/reward `:313`, `:341` | Normal reward and timeout exercised; no new missing-command, staging failure, malformed/missing reward/evidence, identity refusal, OOM or forced caller-death lifecycle coverage. Existing refusal/unit evidence is not relabeled live coverage. |

The native dataset-specific inputs and runtimes remain distinct. Every row is
source-confirmed; a normal generic Python child does not exercise these engines:

| Dataset/runtime branch | Current adapter and consuming runtime source; remaining lifecycle scope |
| --- | --- |
| alfworld | `data/datasets/alfworld.py:327`; `data/datasets/alfworld/verify/check.py:159`: native stripped-PDDL replay. Historical noop covers its selected normal path; timeout/engine-error/resource custody breadth remains. |
| scienceworld | `data/datasets/scienceworld.py:298`; `data/datasets/scienceworld/verify/check.py:157`, `:191`: JVM load/close. w-jvm uses collector limits and assisted reaping; unchanged platform launch and timeout/error cleanup remain. |
| jericho | `data/datasets/jericho.py:243`; `data/datasets/jericho/verify/check.py:109`: native libfrotz load, not Java. Production envelope and engine timeout/error branches remain. |
| spreadsheetbench | `data/datasets/spreadsheetbench.py:222`; `data/datasets/spreadsheetbench/verify/check.py:242`, `:243`, `:364`: LibreOffice subprocess, timeout, temporary profile. Independent cleanup without w-jvm's external subreaper remains. |
| ds1000 | `data/datasets/ds1000.py:192`; `data/datasets/ds1000/verify/check.py:35`, `:55`: temporary wrapper plus upstream manager/worker. Fixed wrapper scratch has w-scratch evidence; production envelope, library/test-string and timeout/error paths remain. |
| livecodebench | `data/datasets/livecodebench.py:262`; `data/datasets/livecodebench/verify/check.py:169`, `:173`, `:174`: worker creation and kill/join. Production worker envelope and global/per-test timeout/error branches remain. |
| bird_minidev | `data/datasets/bird_minidev.py:251`; `data/datasets/bird_minidev/verify/check.py:105`, `:122`: in-process SQLite connection/finally close; alarm restoration `:63`. Production query-timeout/error branches remain; no invented SQL child. |

All twelve QA-command datasets share `data/scaffolds/qa/base.py:339` (bound
selected input), `:345` (argv), `:357` (gold materialization), `:392` (timeout),
then `data/scaffolds/qa/verify/check.py:171` (read/hash), `:235` (adapter import),
`:256` (structured/legacy scoring selection). Their binding/control tests are
not live lifecycle observations for every scorer/import path. The actual hooks
are: bfcl_v3 `data/datasets/bfcl_v3.py:582`; chessbench_puzzles
`data/datasets/chessbench_puzzles.py:370`, `:437`; fever
`data/datasets/fever.py:53`; gsm8k `data/datasets/gsm8k.py:238`; hotpotqa
`data/datasets/hotpotqa.py:65`; musique `data/datasets/musique.py:226`, `:271`;
physicsquestions `data/datasets/physicsquestions.py:191`; reasoning_gym
`data/datasets/reasoning_gym.py:153`; sportsunderstanding
`data/datasets/sportsunderstanding.py:166`; strategyqa
`data/datasets/strategyqa.py:176`; triviaqa `data/datasets/triviaqa.py:339`;
twowikimultihopqa `data/datasets/twowikimultihopqa.py:654`. None is credited with
new dataset-specific lifecycle coverage from this packet.

## Exact execution and preserved attempts

Commands actually run, from the repository root:

```sh
python3 tests/fixtures/hg_we6/preflight.py
python3 tests/fixtures/hg_we6/collect.py
python3 tests/fixtures/hg_we6/collect.py --routes appworld
python3 tests/fixtures/hg_we6/source_audit.py
python3 tests/fixtures/hg_we6/native_collect.py
python3 tests/fixtures/hg_we6/native_collect.py
python3 tests/fixtures/hg_we6/audit_packet.py
```

The initial Docker packet is `w-e6-20261015T032920Z-72d6bfb0/`; the separate
AppWorld capture followup is `w-e6-20261015T033109Z-e7153160/`. Exact executed
collector/probe bytes are retained inside both packets. The followup adds
capture of verdict JSON before its temporary directory disappears, and audit-hook
argv observation; it changes no runtime behavior. Initial transport commands
and all subprocess results it wraps are retained under `commands/`. Followup
`subprocess-argv.jsonl` also records the mounted verifier's direct `docker run`.
`samples.jsonl`, `top.jsonl`, `proc/*.json` and daemon event command outputs
retain the independent raw observations. Root `collector.*`, `followup.*` and
`native*.*` files preserve console streams. No prior attempt is overwritten.

The native initial packet `w-e6-native-20261015T033334Z-971d5371/` failed before
child launch: both probes got `OSError: [Errno 30] Read-only file system` creating
`/tmp/hg-we6-probe-2`. The actual invocation uses the verifier's default work-root
fallback `/tmp`; captured mountinfo confirms `/tmp` RO. This is not a missing
interpreter or a benchmark failure. The unchanged platform returned raw
`score=0.0` without `unmeasured`; that is retained, **not counted as measured
failure evidence**. No classification code is changed here.

The new native packet `w-e6-native-20261015T033413Z-53081026/` changes only the
authored probe to put scratch inside the already writable `verifier/` directory.
Normal predicate returns 1; timeout returns `outcome=timeout`, explicitly
unmeasured after 4 seconds. Both native launchers exit 0 because they successfully
serialize the verdict. `normal|timeout/launch.json` records exact strace/entry
argv and outer 25-second bound; the inner normal deadline is 15 seconds. Saved
executed sources distinguish the attempts, including the probe revision.

## AppWorld service, recording mounts and timeout defect

The collector reads the actual literal DEFAULT_ENV from the adapter without
loading task pools. `services.start` launches the actual pinned AppWorld service,
scopes it to existing service task `cf6abd2_2`, waits using its declared health
check, and creates its recording directory. No actor, initialize, execute or
evaluate call is made. The only HTTP request is the platform's declared service
health check **inside that container**, never a model endpoint request.

The production `_verify` call uses AppWorld's pinned verifier image, owned
internal service network and `services.mounts_for` recording binds. Its check is
the saved authored `probe.py`, not AppWorld's benchmark scorer. It reads the
recording directory, starts one bounded Python child and reports lifecycle facts.
Normal child wait records exit 0 and `/proc/<child>` absent inside the namespace.
Service remains running through both verifier calls.

The followup's service is
`d2ceeab3af5b4c9b21051af0541aa981e12c7bee92e9e2f943100c6b55aab998`,
host PID 847174. Normal verifier
`d159f7d0076ee5a86ce2885c421da670e585b8a6bdf4a5946cb7b1b03a5d8570`
exits 0 and is destroyed automatically. Timeout verifier
`0cdd62dbb64355054903efd319672b74ff6842d11fe1f5f973b2b6b889dca986`
survives native timeout, retaining:

- `/app` RO from its exclusive authored task directory;
- `/recordings/appworld` RO from
  `/tmp/w-e6-20261015T033109Z-e7153160-klc89fp0/recordings/cf6abd2_2/appworld`;
- `/verifier` RW from its temporary output directory, whose **host path is already
  absent** after `_verify` returns. Host unlink does not release a live bind mount.

The service had the same recording source **RW**. `RunningServices.stop()` records
logs then removes the service with `docker rm --force`. Exact-ID inspection
observes service absence **before collector rescue**. Its event stream records
signal 9 / exit 137 / destroy, consistent with forced teardown and OOMKilled=false.
The recording bind remains attached to the timeout verifier. The following
network removal fails with `has active endpoints`, naming `hopeful_elbakyan`.
`summary.json.native_stop_problems` preserves the full returned error. The first
packet independently reproduces the same failure, naming `magical_germain`.

Source cause: `eval/containers/container.py:611` waits on `docker run` using
`subprocess.run(timeout=...)`, with no `finally` to remove the unnamed container.
`eval/verification/verifier.py:656` returns a timeout; `:499` removes only the host
temporary verdict directory. Service stop knows its service container, not this
verifier. `eval/run/runner.py:578` would report the resulting stop problem; its
task-tree removal cannot reap that Docker process. This packet observes the
verify/service helper boundary, not the complete driver or its later reaper.

Collector rescue is explicit: after archiving before-rescue inspections it copies
available verifier artifacts, force-removes **only the observed leaked control
container**, then removes the owned network. Final exact-ID inspections return
no such object, network inspections return not found, and captured PID identities
are absent. No successful native cleanup is claimed for that timeout. Recording
directories, `experiments/`, `service.log` and external work roots are deliberately
retained as evidence; they are not leaked services. The recording mount disappears
with its container; the host recording remains. These are bounded object/PID
observations, not exhaustive absence proofs.

## Limits actually observed

`observations.json` indexes each actual live container's configuration, mounts,
image identity, raw cgroup samples and final absence command. AppWorld service
and both verifiers show NanoCpus=2000000000, Memory=4294967296,
PidsLimit=1024; sampled `cpu.max=200000 100000`, `memory.max=4294967296`,
`pids.max=1024`. This supplies the missing post-w-caps live observation.
MemorySwap=8589934592 is Docker's actual configuration, not a separate workload
swap-enforcement test. Service rootfs remains writable, without tmpfs; verifier
rootfs is RO, with `/tmp` tmpfs `rw,exec,nosuid,size=512m,mode=1777`. StorageOpt
is absent and Ulimits is empty. No private filesystem quota or sizing sufficiency
is inferred. Samples are point observations, never peaks or limit-exhaustion tests.

GAIA/Tau seed and verifier containers use the existing translated 2 CPU / 4096m /
1024 PID envelope, likewise corroborated by cgroup files. Snapshot roots are
writable; no arbitrary RO-root or tmpfs policy is added. Normal verifier checker
returns while trusted BusyBox PID 1 remains idle; production `finally` removes
that whole container, so its container-level exit 137 is teardown, not a failed
predicate. Timeout receives the same removal. Idle bind sources are observed
absent afterward. Fresh committed image IDs and their removal commands are in
the packet; pre-existing cached images are never deleted.

The native control imposes **no collector rlimits, CPU affinity or subreaper**.
`normal/proc/857056-655819096.json` and
`timeout/proc/857272-655819434.json` under the final native packet observe the
actual check's unlimited CPU/address-space limits, Max processes=1028970 and
open files=1048576. Its shared session memory.max/pids.max are `max`; ancestor
user slice pids.max=679120 and cpu.max=`max 100000` at user.slice. Missing CPU
controller files are retained as errors. These are inherited/shared limits,
**no private native CPU/memory/PID cap**. The native verifier also inherits the
host network namespace in this route; the authored probe makes no socket calls.
No isolated-network claim follows from the word offline.

Native strace captures the check waiting successfully for namespace child 3,
bwrap reaping check 2, then the platform reaping the bwrap launcher. At timeout,
the platform kills its bwrap child with SIGKILL and waits; namespace init, check
and sleeping child receive SIGKILL. All captured PID/starttime identities are
absent after native return, without collector assistance. Probe-authored scratch
inside `verifier/` remains intentionally in copied output; it is not claimed
removed. The check's mount namespace and processes end; task/output retention
is separate from process cleanup.

## Exact boundaries and failed prerequisites

All final authored controls had their required local executables/images. Raw
image inspections in `preflight/` establish local cache presence before starts;
no image pull, package install or network acquisition was performed. Snapshot
admission remains active, with actual byte/headroom command outputs preserved.
GAIA/Tau use production snapshot_startup/create/stop/commit and
`_verify_container_state(expected_snapshot=actual_id)`; no identity gate bypass.
The controls use `/we6-state.txt` and their own check, not benchmark answers/DBs.

There is no new complete GAIA web-service/actor route: its model/web gateway is
not launched, and the control declares an owned internal network without bridge.
Tau also uses an owned offline network for observation rather than reproducing
its dataset's network-none topology. Consequently image/runtime/snapshot cleanup
is observed; full dataset-network equivalence and scorer equivalence are not.
The collector calls the same image/network cleanup helpers in its finally; it
does **not** claim to execute `_run_one_container_state`'s outer driver teardown.

Actual AppWorld benchmark replay cannot consume this startup-only recording:
`prerequisite-observations.json` preserves failing `stat` on the exact required
`experiments/outputs/harness/tasks/cf6abd2_2/logs/api_calls.jsonl` in both fresh
work roots. Only `experiments/` and retained `service.log` exist. The unchanged
check reads that log before importing AppWorld at
`data/datasets/appworld/verify/check.py:34`. No recording is invented, no old log
is resumed/copied, and no released predicate is run to pad lifecycle coverage.
This is the exact absent input for replay here, not a claim of missing images.

Native initial failure is the exact RO scratch prerequisite described above.
Remaining native engines, QA scorer imports, TB bootstraps, service health/start
failure, OOM, cancellation and driver reaper branches were **not attempted** in
this bounded packet. They are not labeled locally impossible or assigned invented
missing dependencies. Benchmark scorer runs are outside this task's authorized
scope. Existing w-jvm/w-alf/w-net/w-prifix evidence retains its original limits.

No model/endpoint/weights identity applies: model and endpoint are null; GPU and
paid endpoints are unused. There is no dataset split/selection/trial coverage or
benchmark eligible-count claim for these authored probes. Per-control native
verdicts and every failed attempt are retained separately; no aggregate benchmark
score or staged publication is created. Source hashes, actual image inspections,
argv, deadlines, scratch, mounts, resource samples and cleanup/rescue evidence
establish only this packet's identity and non-comparable scope.

## Registry and validation

Only `artifact-only-state-export.observed` and its evidence list gain the bounded
w-e6 findings. E4/E5/E6 remain PARTIAL. Both shared statuses, full next_actions,
all dataset blockers/references, review authorization and historical records
are unchanged. The known mount-verifier timeout failure is retained as an open
lifecycle finding; no production repair or closure is slipped into this packet.

`reports/w-e6-validation.txt` preserves the registry checker, source-only registry
tests, focused verifier/service-command tests, independent packet audit and
SHA256SUMS verification. `tests/fixtures/hg_we6/audit_packet.py` checks raw
configuration/cgroup agreement, before-rescue leak attribution, final absence,
native wait/timeout evidence and unchanged blocker boundaries without executing
any scorer or control again. The packet manifest covers the report and fixture
sources as well as raw evidence, excluding itself and cache files.

The registry checker is valid with 28 datasets, two shared blockers, 11 historical
records and production_authorized=false. Source-only registry tests: **56 passed**.
Focused verifier/service command/start-cleanup tests: **68 passed, 1 deselected**
(the explicitly excluded live-Docker test). These checks and the packet audit do
not authorize a diagnostic, pilot or benchmark publication.
