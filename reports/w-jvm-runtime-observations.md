# Local JVM, LibreOffice and scoring-process observations - w-jvm

S5 has live local observations for scienceworld, jericho, spreadsheetbench, ds1000, livecodebench and bird_minidev; production envelopes and other runtime branches remain unexercised.

`scorer-offline-closure` stays **code-solvable/open**. S5 stays **PARTIAL**;
S1/S3/S4/S6 remain PARTIAL. No dataset blocker, gate, admission, scoring code or
historical receipt changes. These are bounded controls through byte-identical
materialized `verify/check.py` files, not production verifier or benchmark runs.
Jericho uses native **libfrotz**, not a JVM; BIRD uses **SQLite in the check
process**, not an additional SQL subprocess. The actual processes are observed
below rather than assuming a child exists at every cited source line.

## Execution and artifact custody

All artifact paths below are relative to `reports/w-jvm-evidence/`.
`observations.json` joins the actual raw snapshot file/line, limits, process
summary, native verdict, scratch inventory and cleanup receipt for each runtime.
`SHA256SUMS` hashes every packet file and the fixture collector/auditor sources;
verify it **from the repository root** with:

```sh
sha256sum -c reports/w-jvm-evidence/SHA256SUMS
```

The exact invocations are also retained in `invocations.json`; each runtime's
`launch.json.command_argv` preserves the full executed strace/bubblewrap command.
The first invocation used the saved `initial-collector.py` and `initial-entry.py`:

```sh
python3 tests/fixtures/hg_wjvm/collect.py
python3 tests/fixtures/hg_wjvm/collect.py
python3 tests/fixtures/hg_wjvm/collect.py --output reports/w-jvm-evidence/followup --runtimes spreadsheetbench ds1000 livecodebench bird_minidev
python3 tests/fixtures/hg_wjvm/audit_packet.py
```

The first command produced `execution.json`, with fresh ID
`w-jvm-20261015T001619Z-b770bca6`: every launch failed before Python scoring with
`bwrap: Can't mkdir /control: Read-only file system`. The root-level runtime
directories retain those failures. The collector's writable mountpoint was then
corrected to `/tmp/control`; no scoring logic changed.

The second command produced `live/execution.json`, fresh ID
`w-jvm-20261015T001656Z-63da9530`: ScienceWorld and Jericho completed, LibreOffice
aborted, and collection stopped while trying to copy the resulting UNIX socket.
`live/collection-interruption.json` and SpreadsheetBench's `recovery-*` files
preserve the exception, special-file metadata and separate cleanup. DS/LCB/BIRD
were not reached in that invocation, despite its metadata's planned runtime count.

The followup produced `followup/execution.json`, fresh ID
`w-jvm-20261015T001811Z-9dc8de89`, completing only the four named remaining
controls. It adds `MAX_CONCURRENCY=2` and `GSETTINGS_BACKEND=memory` to the local
control environment and archives special-file metadata without opening sockets.
It does not establish which change caused LibreOffice to succeed. Every attempt
and its collector version is preserved; no old ID was resumed or overwritten.

Each launch has an outer **50-second** wall bound, runs serially, and executes in
a fresh network namespace with only loopback and no IPv4 route. The entry reads
`/proc/net/*` and namespace links; it makes no network probe. Raw topology is in
each `output/network.json`; strace retains JVM loopback and local UNIX IPC.
No model, GPU, endpoint, benchmark driver or `runs/` access was used. ScienceWorld
uses one authored `look around` trace on `find-non-living-thing`, variation 0,
absent from the checked-in test fold. Jericho uses one authored `look` on the
existing acorncourt study ROM (hash split bucket 1). No reference path was
requested or replayed. Trusted installed packages can import their own metadata;
this packet does not prove selected-only/privacy closure.

DS/LCB/BIRD/Spreadsheet inputs are authored arithmetic, SQL and workbook controls.
LCB's unchanged evidence says “released tests”, but its input here is the single
authored test in `followup/livecodebench/inputs/tests.json`, not benchmark tests.
Each final control has native `measured=true`; the world controls return reward
0 and the four arithmetic controls return reward 1. These are control verdicts,
not benchmark scores, dataset diagnostics or valid pilot admission. Each
`sources.json` contains freshly read paths/byte lengths/SHA-256 values for the
check and runtime dependencies. `execution.json` files bind interpreter/package
versions and source HEAD; `observations.json.input_scope` records the split check.

## Resource limits observed in the actual scoring processes

These values are read from the externally captured `/proc/<pid>/limits`,
`/proc/<pid>/status`, `sched_getaffinity(pid)` and cgroup hierarchy files, not
inferred from requested flags. Every scoring role in the table below has:

| Observed limit | Value and scope |
| --- | --- |
| CPU | `Max cpu time` soft/hard **30/30 seconds per process**; affinity **[0, 1]**. Ancestor `user.slice/cpu.max` is `max 100000`; no cgroup CPU quota was observed. |
| Memory | `Max address space` soft/hard **8589934592/8589934592 bytes**, a per-process virtual-address limit. Applicable cgroup `memory.max` and `memory.high` are `max`; this is not a private RSS/memory-cgroup cap. |
| PIDs | `Max processes` soft/hard **1028970/1028970**, a shared UID limit. Session `pids.max=max`; ancestor `user-1026.slice/pids.max=679120`, shared across that user. There is no control-specific PID cap. |
| Other rlimits | Open files **256/256**; file size **67108864/67108864 bytes**; core **0/0 bytes**; stack soft **8388608 bytes**, hard `unlimited`; data and resident-set limits `unlimited`. All remaining raw limits are retained. |

Every runtime's `cgroups.json` records the actual membership
`0::/user.slice/user-1026.slice/session-30486.scope` and every ancestor read,
including missing-controller-file errors. CPU controller files are absent below
`user.slice`, whose `cpu.max` is recorded above. Root cgroup limit files are
absent, not numbers silently substituted as limits. Cgroup usage/current/event
values cover shared host groups and are **not attributed to the control**.
`JAVA_TOOL_OPTIONS` in launch records is declared configuration; it is not used
as evidence of actual JVM heap size. No peak-memory or limit-exhaustion claim is made.

| Runtime/role | PID(s) with matching post-entry limits | Raw snapshot locator(s) |
| --- | --- | --- |
| ScienceWorld check / JVM | 601047 / 601049 | `live/scienceworld/proc-snapshots.jsonl` lines 3 / 6 |
| Jericho native game/check | 601115 | `live/jericho/proc-snapshots.jsonl` line 3 |
| Spreadsheet check / launcher / first soffice / conversion soffice | 602985 / 603101 / 603144 / 603251 | `followup/spreadsheetbench/proc-snapshots.jsonl` lines 3 / 4 / 5 / 7 |
| DS check / runner / manager / candidate worker | 603773 / 603801 / 603803 / 603808 | `followup/ds1000/proc-snapshots.jsonl` lines 3 / 4 / 5 / 6 |
| LCB check / candidate worker | 603956 / 603958 | `followup/livecodebench/proc-snapshots.jsonl` lines 3 / 4 |
| BIRD SQLite/check | 603987 | `followup/bird_minidev/proc-snapshots.jsonl` line 3 |

The limits above were imposed by the **control entry**, then observed in the
actual scoring processes. They do not certify the production verifier's envelope.
`process-samples.jsonl` retains repeated external readings; `syscalls.txt.gz`
retains raw exec/fork/clone/wait/exit and scratch cleanup calls. The observer uses
ptrace and a parent subreaper, which can affect timing and reparenting. It does
not replace scoring methods, intercept verdicts or supply policy attestations.

## ScienceWorld JVM

`live/scienceworld/output/evidence.json` records the completed one-action replay,
score 0/100 and reward 0. Py4J execs the materialized JRE's `bin/java` as PID
601049, with the ScienceWorld/Py4J JAR classpath and `--die-on-broken-pipe`.
Python PID 601047 calls the unchanged check's `env.close()` at
`data/datasets/scienceworld/verify/check.py:191`. The trace observes gateway socket
shutdown and JVM exit 0. Py4J's waiting thread does not finish reaping before the
check exits; `process-summary.json.collector_waitpid` records the **external
subreaper** adopting and reaping PID 601049 with returncode 0. Thus absence is
observed, but it is not evidence that the check independently completed reaping.

The trace records removal of `/tmp/tmp199kew1i` and
`/tmp/hsperfdata_xubuqiang/601049`. `scratch-observations.json.after_check` retains
the empty `hsperfdata_xubuqiang` directory and collector-created `control`/`home`
directories. `cleanup.json` records the owned case/scratch roots and all captured
PID identities absent **after collector removal/reaping**. The full run root is
absent per `live/root-cleanup.json`.

Unexercised: longer task/action paths, load/step failures, timeout/kill branches,
independent production reaping and production resource enforcement.

## Jericho native game

`live/jericho/output/evidence.json` records native replay, maximum 30, score 0 and
reward 0. Python PID 601115 loads/reset/replays the actual libfrotz-backed game.
No JVM or separate game child is launched in this trace. Bubblewrap waits for the
check's expected exit 1, and the collector waits for strace. The raw trace records
`mkdir("/tmp/tmp0w9zq_98", 0700)=0` followed by its successful `rmdir`; this short
lived directory fell between filesystem polls and is supported by syscalls,
not claimed as a sampled path. Only collector-created `control`/`home` remain in
the scratch inventory. `cleanup.json` records all captured PIDs and owned paths
absent after collector cleanup.

Unexercised: other ROMs/game actions, native failure paths and production
enforcement. The check has no explicit `env.close()` after replay
(`data/datasets/jericho/verify/check.py:117` onward); process exit was observed,
not an independent close-method invocation or pre-exit native allocation release.

## SpreadsheetBench LibreOffice

`followup/spreadsheetbench/output/evidence.json` records `recalculated=true`,
`correct=true`, reward 1. The before/after workbooks are retained in
`inputs/result.xlsx` and `after-work/result.xlsx`; the latter's cached A1 is 3.
The unchanged check launches `/usr/bin/soffice` with its private
`UserInstallation=file:///tmp/sb-recalc-szuvakm_/lo-profile` and converter output
directory. The raw trace follows shell/oosplash PID 603101, first soffice PID
603144 (exit 81/restart), conversion soffice PID 603251 (exit 0), and helper
processes. The check's `subprocess.run` wait reaps launcher 603101; the trace also
records soffice waits. Six orphan helpers, including javaldx/GPG utilities, are
adopted and reaped by the **external collector**, with statuses in
`process-summary.json.collector_waitpid`. This is assisted cleanup evidence.

The trace and scratch inventory establish removal of the complete
`sb-recalc-szuvakm_` profile/conversion tree and the exact IPC socket
`/tmp/OSL_PIPE_1026_SingleOfficeIPC_555d241098f673def491b69c31d4edcf`.
Fontconfig cache files persist under the control's private `home/.cache` until
collector removal; their bytes/digests are archived in `after-scratch/`.
`cleanup.json` observes all captured PID identities and owned roots absent.

The prior actual abort remains at `live/spreadsheetbench/`: native evidence is
`measured=false`, `LibreOffice exited 134`, with raw SIGABRT events. The check
removed its `sb-recalc-o21001xz` profile, but left socket
`OSL_PIPE_1026_SingleOfficeIPC_84314275a16086bb5fc631871eea94f4` and font caches.
`recovery-scratch-inventory.json` explicitly records that socket's type and mode;
`recovery-cleanup.json` records later collector removal. The truncated native
error is preserved; an exact causal prerequisite for the abort was **not**
established, so this report does not invent one.

Unexercised: production envelope, other workbooks/formulas, timeout cleanup and
independent cleanup without the external subreaper. No missing LibreOffice/JRE/
data prerequisite prevented the final authored control.

## DS-1000 child processes

`followup/ds1000/output/evidence.json` records `passed`, reward 1. The check execs
runner PID 603801 from `/tmp/ds1000-check-rugl1mm4`; upstream `execution.py`
starts manager PID 603803 and candidate PID 603808. The candidate's externally
observed cwd is `/tmp/tmpvwe5rw7f`. The trace records successful waits for the
candidate, manager and runner; no collector reaping was needed.

Upstream removes candidate scratch `/tmp/tmpvwe5rw7f`, manager IPC directory
`/tmp/pymp-v03o1c7y` and its listener. **The wrapper leaves
`/tmp/ds1000-check-rugl1mm4` behind**, containing `execution.py`, `program.json`
and `run_ds1000.py`. Their actual byte lengths and digests are in
`scratch-observations.json.after_check`, with bytes retained in `after-scratch/`.
The defect is the unpaired `mkdtemp` at
`data/datasets/ds1000/verify/check.py:34`; after launching at line 53, the wrapper
returns without removing it. No scoring patch was made. Only subsequent
**collector** removal makes the owned scratch root absent in `cleanup.json`.

Unexercised: scientific-library/data branches, conditional `test_string`,
timeouts/kill branches, production resource enforcement and successful wrapper
scratch cleanup. The observed wrapper cleanup gap remains a finding.

## LiveCodeBench child process

`followup/livecodebench/output/evidence.json` records the authored one-test
result `[true]`, reward 1. The unchanged check forks candidate PID 603958 from
PID 603956; it imports the actual materialized pinned `testing_util.py` and
returns via its multiprocessing queue. `syscalls.txt.gz` records the worker
fork and `wait4(603958, ... WEXITSTATUS=0)=603958`. The worker's own post-fork
limits are captured separately. No extra executor-created temporary path
survives in `scratch-observations.json.after_check`; only collector-created
`control`/`home` remain. `cleanup.json` records captured PIDs and owned roots
absent, with no collector waitpid or forced process cleanup.

Unexercised: global/per-test timeout, kill/join branch, compile/runtime errors,
call-based tests and production enforcement. The upstream comment claiming a
4-GB memory limit is not treated as an observed limit: this worker actually has
the captured 8-GiB address-space limit from the control, not a 4-GB cgroup cap.

## BIRD Mini-Dev scoring process

`followup/bird_minidev/output/evidence.json` records EX reward 1, one predicted
and one gold row, against the authored SQLite database. Python PID 603987 opens
the DB, executes both bounded recursive queries, closes its connection and
exits 0. No extra SQL child is launched; the limits recorded for PID 603987 are
the limits on the actual scoring runtime. Bubblewrap waits for it normally.
No SQLite journal/WAL/SHM or new task-specific scratch appears in the final
`after-work/`/scratch inventory; the authored DB, SQL and output artifacts remain
until collector archival/removal. `cleanup.json` records captured PIDs and
owned roots absent, without forced cleanup or collector waitpid.

Unexercised: query alarm/error branches, writable SQL mutations, other DBs,
production enforcement and exhaustive native descriptor/namespace absence.

## Remaining scope and validation

All six requested local runtimes were exercised; no final-control prerequisite
is missing. S5 remains partial because these observations use a collector-owned
envelope and sometimes collector-assisted cleanup. Other actor/QA/TB runtimes,
GAIA/Tau routes and the corrected AppWorld service envelope are outside this
packet. It adds neither production admission nor portable transitive closure.
Dataset/task breadth, S1/S3/S4/S6, and every dataset blocker remain unchanged.

The independent artifact audit recomputes source hashes, matches each selected
role's actual raw limits/affinity, verifies native verdict/reward consistency,
and checks captured PID identities and all owned roots absent. It does not rerun
scoring. `reports/w-jvm-validation.txt` retains the checker and focused
source-only registry test outputs, audit and SHA-256 verification outcome.
