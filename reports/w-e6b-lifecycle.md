# Remaining live lifecycle observations - w-e6b

**E6 remains PARTIAL. No shared or dataset blocker closes.** Eleven serial authored
controls add live observations for mounted reward/evidence errors, snapshot
post-create early exits, unsandboxed command exits and service health failure.
Both the read-only mounted verifier and the writable actor-shaped helper remove
their sleeping children and containers on timeout. No production source changes.

Read `AGENTS.md`, `reports/w-reassess2-shared-closures.md`,
`reports/w-e6-lifecycle.md` and `reports/w-e6fix-receipts.md`, then checked their
claims against this registered `/tmp/hg-e6b` worktree on `wg-e6b`.
`reports/w-e6b-evidence/source-current.txt` preserves current **file:line text**,
source byte counts and command-derived SHA-256s without importing task pools.
The live packet's `preflight.jsonl` preserves HEAD, branch/worktree registration,
Python/Docker versions, source hashes and the actual cached image inspection.
Historical HEADs and old line numbers are not substituted for current source.

## Inventory reconciliation: precise dispatch and exit branches

Paths in this table are current. The old inventory's native-command lines moved
when the pinned native-runtime entry wrapper was added; for example old
`verifier.py:648` now reaches `:690-693`, not a container cleanup branch.
“Remaining” means live coverage still absent from the reviewed packets; it does
not mean locally impossible. Earlier bounded successes retain their original scope.

| Inventory branch; exact current source | Coverage at entry and exact remaining/new scope |
| --- | --- |
| Pristine dispatch `eval/verification/verifier.py:512`, `:518`; attempted-create/start/removal `eval/verification/pristine.py:130`, `:143`, `:172`, `:175` | Prior w-prifix/w-bind live normal controls remain credited. W-e6fix's create/start timeout controls are fake-Docker tests. Those live transport-timeout/cleanup-failure exits remain unobserved here; no current dataset opts in. |
| In-process answer `eval/verification/verifier.py:589`, `:593`; controller dispatch/termination `eval/run/runner.py:454`, `:497`, `:521` | Answer comparison launches no subprocess. W-chess3's bounded exchange remains credited; controller interruption/error/finally breadth is not supplied by this packet. |
| Mounted command `eval/verification/verifier.py:531`, `:533`, `:653`, `:659`; helper teardown `eval/containers/container.py:578`, `:615`, `:618`, `:620` | W-e6fix already covers normal/timeout with an idle recording service. New **mounted-timeout** adds an observed checker child; **mounted-missing-reward**, **mounted-malformed-reward**, **mounted-missing-evidence** add actual error exits through `verifier.py:727`, `:748`, `:760`. Complete AppWorld replay and forced caller-death/daemon-transport failure remain uncovered. |
| Mounted actor caller `eval/run/runner.py:463`; harness/state mounts `eval/containers/container.py:522`, `:524` | New **mounted-writable-helper-timeout** calls the same repaired helper with a RW task, RO authored harness and RW `.state`, then observes checker/child/container absence. This is the helper's actor mount shape, not execution of the whole actor driver or a model-bearing harness. |
| Actor snapshot dispatch/outer lifecycle `eval/run/runner.py:235`; `eval/containers/container_state.py:92`, `:110`, `:179`, `:181`, `:190`, `:191`, `:213`, `:235`, `:246`, `:250` | W-e6 observes GAIA/Tau helper snapshot normal/timeout, not the full outer driver. Other TB task/image/bootstrap paths, full actor timeout/commit-error/cancellation and outer-driver removal remain unobserved here. This packet creates no actor or committed image. |
| Snapshot verifier `eval/verification/verifier.py:241`, `:264`, `:302`, `:306`, `:315`, `:317`, `:322`, `:331`, `:412`, `:414`, `:415` | W-e6 normal/checker-timeout remains credited. W-e6fix's missing-argv/staging tests gain live observations here: **snapshot-missing-argv** starts trusted idle PID 1 then removes it; **snapshot-staging-error** creates a stopped container, fails on a genuinely absent input at `:427`, removes it without starting any process. Both release idle bind sources. Allocation-before-create-acknowledgement remains unobserved. |
| Snapshot output/network variants `eval/verification/verifier.py:313`, `:340`, `:347`, `:375`, `:385` | Missing/malformed reward, missing report and declared bridge/error variants remain without new live observations. Mounted output controls execute a different parsing block and do not cover these snapshot exits. |
| Native sandbox `eval/verification/verifier.py:669`, `:685`; `eval/containers/sandbox.py:395`, `:420` | W-e6 normal/timeout namespace teardown remains credited. No new sandbox import/engine-error/OOM/caller-death observations here. |
| Unsandboxed native `eval/verification/verifier.py:690`, `:691`, `:695`, `:698` | Previously unexercised: new **unsandboxed-normal** waits/reaps its child; **unsandboxed-single-timeout** kills/waits the checker (deliberately no child); **unsandboxed-missing-command** returns the actual ENOENT. Timeout with surviving descendants remains untested; no process-tree cleanup guarantee follows. No sandbox route was replaced or admission changed. |
| Input/class/command pre-launch exits `eval/verification/verifier.py:521`, `:525`, `:546`, `:601`, `:602`, `:606` | Snapshot absent-input is newly observed separately at `:427`; mounted input-staging error, scorer-input receipt mismatch, incompatible class and absent `argv` key at these exact branches gain no live execution. Existing refusal/unit evidence is retained without relabeling it. |
| Service startup/health/stop `eval/service/services.py:361`, `:414`, `:419`, `:424`, `:426`, `:430`, `:450`, `:457`, `:458`, `:206`, `:226`, `:232` | New **service-health-failure** observes nonzero health probes, native exception teardown and exact container/network absence. Start-command failure, allocation-before-start-acknowledgement, health transport timeout, stop/log transport failure, OOM and interruption remain unobserved. |
| Discovery and uncertain allocation/removal `eval/containers/container.py:407`, `:409`, `:412`, `:968`, `:981`, `:984`, `:989`, `:992`; network creation `eval/service/services.py:245`; crash reaper `:271`, `:308`, `:318` | W-e6fix identifies unnamed interpreter discovery, uncertain create/commit/network acknowledgements and best-effort removal. No new live uncertainty injection, daemon fault or crash-reaper execution here. Read-only exact-object postmortem checks are not reaper execution. |
| Pinned host runtime, now before the old inventory's dispatch: `eval/verification/verifier.py:465`, `:487`, `:489`, `:634`; `eval/verification/native_runtime.py:66`, `:103`, `:142` | New unsandboxed controls have **no native_runtime binding**; they do not exercise this route. BIRD/Jericho/ALF pins added since w-e6 do not turn generic Python controls into native-closure lifecycle coverage. |

## Dataset/runtime obligations still without these live observations

This enumerates the inventory's runtime branches, rather than assigning lifecycle
coverage to every adapter that eventually reaches the same command launcher.
No dataset scorer, released benchmark predicate, engine, selected task pool or
gold input was executed by w-e6b. Earlier w-jvm component observations retain
their collector limits/assisted-reaping boundaries.

| Dataset | Exact current adapter and consuming runtime; outstanding observations |
| --- | --- |
| ALFWorld | `data/datasets/alfworld.py:329`, `:365`; `data/datasets/alfworld/verify/check.py:169`: replay/engine-error/timeout and actual pinned-runtime custody/cleanup beyond the historical noop. |
| ScienceWorld | `data/datasets/scienceworld.py:300`; `data/datasets/scienceworld/verify/check.py:168`, `:183`, `:190`, `:204`: JVM load/step-error/timeout/close in the production verifier; generic child cleanup does not observe JVM cleanup. |
| Jericho | `data/datasets/jericho.py:245`, `:278`; `data/datasets/jericho/verify/check.py:122`, `:134`: libfrotz load/replay/error/timeout and production pinned-runtime cleanup. It is not a Java child. |
| SpreadsheetBench | `data/datasets/spreadsheetbench.py:224`; `data/datasets/spreadsheetbench/verify/check.py:246`, `:247`, `:374`: LibreOffice subprocess timeout/profile cleanup without external subreaper assistance. |
| DS-1000 | `data/datasets/ds1000.py:194`; `data/datasets/ds1000/verify/check.py:55`, `:76`: temporary wrapper/upstream worker and library/test-string/timeout/error cleanup under the production launcher; w-scratch's repair remains separate. |
| LiveCodeBench | `data/datasets/livecodebench.py:264`; `data/datasets/livecodebench/verify/check.py:96`, `:180`, `:182`, `:184`, `:185`, `:188`: per-test/global worker timeout, kill/join and executor-error cleanup under production limits. |
| BIRD mini-dev | `data/datasets/bird_minidev.py:253`, `:269`; `data/datasets/bird_minidev/verify/check.py:63`, `:68`, `:117`, `:134`, `:135`: in-process SQLite query timeout/error, alarm restoration and connection close in the production pinned route. There is no invented SQL subprocess. |
| GAIA | `data/datasets/gaia.py:99`, `:196`: full web-gateway/actor/scorer/error lifecycle beyond the w-e6 authored snapshot controls. |
| Tau | `data/datasets/tau_bench.py:182`, `:328`: complete dataset actor/network/scorer/error lifecycle beyond the w-e6 authored snapshot controls. |
| Terminal-Bench | `data/datasets/terminal_bench.py:194`, `:231`: task/image/bootstrap/error breadth beyond the separately recorded w-net/TB controls. No benchmark or bootstrap is rerun here. |
| AppWorld | `data/datasets/appworld.py:267`, `:294`, `:303`; `data/datasets/appworld/verify/check.py:32`, `:35`, `:44`, `:45`, `:56`: real recording replay/evaluator/error cleanup beyond service startup and authored recording-bind predicates. |

All twelve QA-command hooks still owe scorer/import-specific lifecycle evidence:
`data/scaffolds/qa/base.py:339`, `:345`, `:357`, `:392` feed
`data/scaffolds/qa/verify/check.py:171`, `:235`, `:256`. Exact adapter hooks are:

- BFCL: `data/datasets/bfcl_v3.py:582`.
- Chess: `data/datasets/chessbench_puzzles.py:370`, `:437`.
- FEVER: `data/datasets/fever.py:53`; GSM8K: `data/datasets/gsm8k.py:238`.
- HotpotQA: `data/datasets/hotpotqa.py:65`; MuSiQue: `data/datasets/musique.py:226`, `:271`.
- PhysicsQuestions: `data/datasets/physicsquestions.py:191`; Reasoning Gym: `data/datasets/reasoning_gym.py:153`.
- SportsUnderstanding: `data/datasets/sportsunderstanding.py:166`; StrategyQA: `data/datasets/strategyqa.py:176`.
- TriviaQA: `data/datasets/triviaqa.py:339`; 2WikiMultiHopQA: `data/datasets/twowikimultihopqa.py:654`.

## Executed controls and raw packet

Sole complete packet used for the new Docker coverage:
`reports/w-e6b-evidence/w-e6b-61fad626fa3647ee9425609ad8d229fb/`.
Its `summary.json` indexes every case, exact object and PID/start-time absence
check. Each `<case>.jsonl` records actual argv, timeouts, outputs/return codes or
exceptions, daemon inspection projections, top/proc/cgroup samples and verdict.
`executed-collect.py`/`executed-probe.py` bind the executed observer and probe.
`reports/w-e6b-evidence/audit.txt` independently checks their hashes, live limits,
mount permissions, teardown ordering/absence and unchanged registry boundary.

| Control name / raw JSONL in that packet | What starts, what is reaped, observed native result |
| --- | --- |
| `mounted-timeout` | Actual pinned-image Python checker PID 1 and a sleeping Python child, RO task/recording and RW verdict binds. Three-second timeout remains explicitly unmeasured. Production named `rm --force` removes the container; both sampled host identities and exact container are absent immediately after `_verify`, before service stop/rescue. |
| `mounted-missing-reward` | Checker starts child, terminates it and waits, then raises the authored error before writing reward. Raw stdout records child exit -15 and namespace `/proc` absence; traceback/exit 1 survives. Container is absent after `_verify`. Native raw score=0 remains visible but is **not a measured benchmark zero**. |
| `mounted-malformed-reward` | Child terminate/wait completes; checker writes `not-a-number`, exits 0. Parser refuses the reward; container and sampled checker identity are absent. Native raw score=0 is not counted as a measurement. |
| `mounted-missing-evidence` | Child terminate/wait completes, reward=1 but declared evidence is absent. Native verdict retains passed=true/score=1 **and unmeasured**; no valid score is inferred. Container/checker/observed child are absent. |
| `mounted-writable-helper-timeout` | Same helper with RW `/app`, RO authored harness and RW `.state`, no recording mount. Checker and sleeping child are sampled live; helper raises the original three-second TimeoutExpired after named removal. Container and both identities are absent on return. |
| `snapshot-missing-argv` | Real create, consumed-image check and trusted BusyBox idle start; no checker argv. Native missing-argv verdict returns after `finally` removes idle container and closes its startup bind. |
| `snapshot-staging-error` | Real create and consumed-image check; `_input_source` raises ValueError for the exact absent input in the raw exception. No `docker start`, no checker, no PID. `finally` removes the stopped container and startup bind. |
| `unsandboxed-normal` | Actual `_verify` → direct subprocess; checker launches, terminates and waits its child. Reward=1. Both independently sampled host PID/start-time identities are absent after return. |
| `unsandboxed-single-timeout` | Actual direct checker, **no child**, two-second timeout, explicitly unmeasured. Its independently sampled identity is absent after return. Descendant timeout cleanup is not tested. |
| `unsandboxed-missing-command` | Actual absent executable raises FileNotFoundError; native missing-command verdict. No checker starts; an empty observed PID set is not a process-tree absence proof. |
| `service-health-failure` | Authored idle Python service with RW recording starts and is sampled; health commands actually exit 7. One-second declared health budget expires; ServiceUnavailable reaches native `services.start` exception cleanup. Container/PID and owned network are absent before collector rescue. No verifier starts on this failed prerequisite. |

The service used for mounted verification is authored idle Python, **not AppWorld
API startup or replay**. It has a 90-second self deadline; checker/child sleeps
are bounded at 20 seconds. Command deadlines are three seconds for mounted
timeouts and twelve for the other mounted checks; native normal/missing-command
use ten seconds, native timeout two. Thread observation bounds are 35 seconds.
Production Docker create/start/copy/remove transport deadlines remain their
original values and are recorded separately. The shell invocation has a
150-second outer guard. No CPU/memory/PID limit exhaustion is attempted.

The snapshot controls consume the actual inspected content ID of that cached
runtime, pass it as independent `expected_snapshot`, and run the production
consumed-container image check. They deliberately exercise post-create exits
without claiming a new dataset image, actor snapshot, commit or outer-driver run.
No cached image is removed or pulled.

## Limits, absence and regression discrimination

All observed containers configure NanoCpus=2000000000, Memory=4294967296,
MemorySwap=8589934592 and PidsLimit=1024. For **each running container**, host
proc/cgroup samples corroborate `cpu.max=200000 100000`,
`memory.max=4294967296`, `pids.max=1024`; the stopped staging-error container
has configuration only. Mounted verifier/helper rootfs is RO with the existing
512m `/tmp` tmpfs. Services and snapshot rootfs retain their existing writable
configuration; no filesystem quota is introduced or inferred. Empty Ulimits and
absent StorageOpt remain explicit in daemon projections.

The native checker has inherited unlimited CPU/address-space, Max processes
1028970 and open files 1048576. Its session memory.max/pids.max are `max`;
ancestor user-slice pids.max is 679120 and user.slice cpu.max is `max 100000`.
Missing controller files are preserved as errors. These are shared inherited
limits, **not private native caps**. The collector sets no rlimit, affinity,
namespace or subreaper and performs no process rescue.

Final complete-packet observations establish **nine exact containers and fourteen
captured PID/start-time identities absent, six temporary host bind sources absent,
zero collector rescues**. Native service stop returns `[]`; its owned network is
absent before rescue. The failed-health service's network is likewise absent at
its own native failure boundary. Object removal releases the observed container
recording mounts/endpoints. Host recording directories/service.log, authored
work roots and snapshot verdict staging are retained intentionally as evidence.
Not every short-lived child is independently sampled; authored child wait
observations and host samples are distinguished. These are bounded observations,
not daemon-wide or exhaustive host absence claims.

The regression assertion is concrete: an observed live mounted timeout container
must be absent **as soon as the helper/verifier returns**, before service teardown
or collector rescue. Both mounted timeout shapes pass it here. `audit_packet.py`
also evaluates that same object-absence predicate against the untouched actual
pre-fix packet
`reports/w-e6fix-evidence/w-e6fix-before-9d6a0ecfe85a41a69a6edf96146436dc/summary.json`:
it returns **false**, because its timeout `after_return` retains the verifier.
Thus this control would fail before the w-e6fix omission repair; a successful
normal exit alone would not distinguish it. No old run is resumed and no
production implementation is replaced to manufacture a baseline.

## Failed observers and exact prerequisite boundaries

All attempts are retained; no failed receipt is overwritten or counted twice.

- `w-e6b-4f0710aa5cce4a17aabf64f6ef2ce685/` executes the controls, but the Docker
  template fails at absent optional `HostConfig.Tmpfs`/`StorageOpt` fields. Its
  empty container-observation maps supply **no Docker absence evidence**.
- `w-e6b-d780eb5e4ec44a5ab1227e14a86032f8/` observes the mounted timeout live and
  its named removal, but the observer rejects this Docker version's lowercase
  `error: no such object` as a collector error and aborts. It has no native
  summary; raw streams and executed source are retained, not repaired in place.
- A fresh third invocation fixes observation only: optional map fields use
  `index`, absence must contain the actual object-not-found error, and unrelated
  inspection failures raise. The platform code, probe, admissions and limits
  are unchanged. `postmortem.txt` read-only inspections verify every derived
  container/network name from **all attempts**, plus captured identities, absent.

The only local full-dataset replay prerequisite rechecked is the historical
**actual AppWorld startup** recording, not a made-up recording in our idle service.
`reports/w-e6b-evidence/postmortem.txt` retains real failing `stat` outputs for:

```text
/tmp/w-e6-20261015T032920Z-72d6bfb0-wia1848y/recordings/cf6abd2_2/appworld/experiments/outputs/harness/tasks/cf6abd2_2/logs/api_calls.jsonl
/tmp/w-e6-20261015T033109Z-e7153160-klc89fp0/recordings/cf6abd2_2/appworld/experiments/outputs/harness/tasks/cf6abd2_2/logs/api_calls.jsonl
```

The unchanged checker refuses an absent log at
`data/datasets/appworld/verify/check.py:32-33`, before importing AppWorld at
`:44`. No API log is invented, copied or resumed; no replay/metric coverage is
claimed. This does not say a new authorized actor could never produce a log.

Other unexercised runtime/QA/TB/OOM/cancellation/transport/crash branches above
were **not attempted in this bounded packet**, so there is no observed failed
prerequisite to invent for them. Cached-runtime inspection and snapshot idle
startup succeeded for the final authored controls. The snapshot-staging-error
and unsandboxed-missing-command ENOENTs are intentional authored error inputs,
not claims that a dataset installation is missing.

## Validation and registry scope

Actual invocations and results are preserved in `reports/w-e6b-validation.txt`.
Registry/source-only, journal and focused cleanup/adjacent checks report
**72 passed, 3 xfailed**; the independent packet audit passes. The hash manifest
`reports/w-e6b-evidence/SHA256SUMS` covers this report, registry/journal edits,
fixture scripts and all raw packet text, excluding the validation log and itself
to avoid a self-reference. Its verification output is in the validation log.
The raw live console/stderr files are `reports/w-e6b-evidence/live*.txt`;
the reproducible observer/probe, source inventory, read-only postmortem and
independent packet audit are under `tests/fixtures/hg_we6b/`.

Only `artifact-only-state-export.observed` and its evidence list are appended at
the exact authored branch/helper scope above. Shared statuses/full next_actions,
all dataset blockers/history, production authorization and all gates remain
unchanged. E4/E5/E6 remain PARTIAL. No `runs/`, frozen receipt, model server,
model endpoint, GPU, paid endpoint or benchmark pilot is touched. No binary,
download, response body or bulk trace/dump is added. The commit is made only in
this registered worktree for parent review, without merging to main.
