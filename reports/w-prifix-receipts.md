# Pristine production defect repairs and sealed control rerun - w-prifix

**Final code produces a genuine measured failure: score `0.0`, measured=1,
invalid=0, unmeasured=0.** The unchanged answer is `41\n`, the sealed expected
answer is `42\n`, and the real scorer now emits `completed_check=fail`. D1/D2/D3
are repaired. Both shared blockers remain open; this locally authored runtime
control grants no dataset/H0/official-scorer authorization.

All artifact paths below are relative to `reports/w-prifix-evidence/` unless a
repository or absolute path is written. Original w-pristine evidence and every
new attempt remain preserved. `copy-provenance.json` verifies 89 byte-identical
copies (713864 bytes) from the two external run roots and their follow-up probes.

## Defects, fixes and retained guarantees

The starting evidence is `reports/w-pristine-receipts.md`, section “Real failure,
audited counts and production defects”, and
`tests/fixtures/hg_wpristine/evidence/{docker-02,measurement-audit,verdict}.json`.
It records a permission error before the predicate, an invalid native `0.0`, and
no stopped State in native evidence. Its audited partition remains unchanged:
invalid=1, measured=0, unmeasured=0, publishable score=null.

- **D1:** `eval/admission/artifact_admission.py:292-315` explicitly assigns the
  platform effective primary group and modes 0750/0640 to export directories/data
  files, including every nested directory despite umask. The platform keeps file
  ownership; there are no data execute bits, group writes or other permissions.
  `eval/verification/pristine.py:72-76` explicitly selects numeric scorer UID
  65534 and the export group (observed `65534:1026`, host writer UID 1026).
  The reserved UID cannot equal the platform UID. Shared runtime validation at
  `eval/admission/artifact_admission.py:417-453` checks actual `Config.User`, rejects
  added groups, and checks DAC read/search permissions on both projections and
  execute permission on the pinned runtime. POSIX owner/group/other precedence is
  honored. The closure is checked, never permission-rewritten to force admission.
  Group read/search is narrower than world-readable exports; the exclusive private
  parent retains host custody, and the scorer's two bind roots are read-only.
- **D2:** `eval/verification/pristine.py:99-129` requires exactly one reserved stdout
  line, `completed_check=pass` with exit 0 or `completed_check=fail` with exit 1,
  consistent with both Docker attach returncode and stopped ExitCode. Exit status
  alone cannot distinguish initialization failure from a completed failing check.
  Missing/malformed/duplicate markers, mismatches, abnormal runtime/OOM and
  inspection failures yield score=null and an explicit unmeasured reason; timeout
  has outcome=timeout. Marker failures retain exit and a bounded stderr suffix.
  Completed failing checks retain measured `0.0`. Cleanup failure still overrides
  measurement. `eval/verification/isolation.py:41-48` preserves the underlying
  failure reason when appending an isolation mismatch. This follows the existing
  HotpotQA timeout and SpreadsheetBench incomplete-comparator distinction.
- **D3:** `eval/verification/pristine.py:101-108,130-141` retains native
  `start_result`, `stopped_result` (including raw State before classification), and
  cleanup argv/returncode/stdout/stderr or exception detail. These facts survive
  JSON serialization in the verdict; external observers are corroboration.

The bundle protocol and compatibility consequence are documented in
`docs/pristine-scorer-protocol.md`: older exit-only bundles become unmeasured until
updated and re-sealed. Line boundaries follow `str.splitlines()` and EOF can
terminate the line. A trusted bundle must emit the marker only after its predicate
completes and must not echo actor input as protocol lines.

The original regular-file/data-only checks, selected allowlist, byte/inode bounds,
exact two mounts, both projection integrity rechecks, read-only rootfs and binds,
capability drop, no-new-privileges, exact environment ordering, offline network and
bounded tmpfs remain required. No host-user execution or added mount/capability is
used. Normal host-ID mapping is the DAC assumption; arbitrary rootless/remapping/
LSM configurations are not attested. Such failures remain unmeasured without a
valid marker. Source quiescence/race-proof custody and dataset-wide closure remain
separate unmet obligations.

## Exact final rerun and unchanged identity

Executed in `/tmp/hg-prifix` using the existing, unmodified driver:

```sh
python3 tests/fixtures/hg_wpristine/run_control.py --work-root /tmp/hg-wprifix-runtime --run-id w-prifix-final-20261014T231720Z-483ac92d
```

Original artifacts:
`/tmp/hg-wprifix-runtime/w-prifix-final-20261014T231720Z-483ac92d/evidence/`.
Copied artifacts: `final-control/`. `final-control/launch.json` records exact argv,
cwd, source hashes and actual execution timestamp
`2026-10-14T23:14:48.753635+00:00`; the run ID is an opaque label, not its timestamp.
Base git HEAD is `3616713733b3e9bcb9a284f6af9d13e081841214`; the launch's source
hashes identify the edited production code, and `final-audit.json` verifies these
bytes against the final worktree. No model, GPU or paid endpoint is involved:
endpoint/model=null, trials=1, jobs=1, verifier timeout=60s.

`audit_packet.py` reverified all **55** existing fixture manifest entries. No file
under `tests/fixtures/hg_wpristine/` changed. Existing SHA256SUMS file digest:
`ef236df615c01463ffb3635b678ededc26211088d0a0ddf2778359ba19e8b2a0`.

| Identity | Unchanged raw value |
| --- | --- |
| Task / metric | `w-pristine-addition-control` / `exact-answer-command-exit0` |
| Bundle SHA-256 | `168d15a4945ea4ef093da3040fb7bd441ad1ec77ef4143379fbd1a6d318c4fbd` |
| Contract SHA-256 | `28d615baa4b11c72c67f097e25025817f19a18e8abb3c22a6207e7172cda82e6` |
| Task source SHA-256 | `8e13963d42f2b87eb36756e9124922e24bc91ea9ef20af81ff15e9334dfd3f0b` |
| Image ID | `sha256:3d32c18960e2cd4340c95b9cb3042581be0e2392959e6428fc06a37de334981d` |
| Exported answer SHA-256 (`41\n`, 3 bytes) | `040316eca5e77dbb2212c1efe8b81cb23bc67ce0ac8cb5c9d902d98bd45ddfa1` |

Pins are in the unchanged fixture `trusted-pins.json`; actual export identity is
in `final-control/verdict.json`. This synthetic source has no dataset split or
model hash (not applicable); base HEAD plus recorded source-file SHA-256s establish
the harness identity. No official or cross-dataset comparability is claimed.

## Raw result, coverage, resources and cleanup

`final-control/docker-02.json`: attach returncode=1, stderr="", stdout includes
`expected=42`, `actual=41`, and exactly one `completed_check=fail` line.
`final-control/inspect-03.json`: Status=exited, Running=false, ExitCode=1,
OOMKilled=false, Error="", StartedAt=`2026-10-14T23:14:49.101024947Z`,
FinishedAt=`2026-10-14T23:14:49.285266195Z`.

`final-control/verdict.json`: passed=false, score=0.0, outcome=measured,
class=pristine-offline, detail=`sealed scorer completed_check=fail, exit 1`.
Its own evidence contains that stopped State and the attach/removal results.
`final-control/control-receipt.json` and independent `final-audit.json` agree:
eligible=1, selected=1, expected trials=1, measured=1, invalid=0, unmeasured=0.

`final-control/projection-rechecks.json` retains both successful post-inspection
rechecks: scorer files=3/bytes=2194251, export bytes=3/inodes=2 with limits 16/2.
Export inventory is solely non-executable answer.txt, mode0640, UID1026, nlink1,
with the unchanged hash above. Runtime admission then succeeds before start.
`final-control/inspect-01.json` observes user `65534:1026`, network none, rootfs RO,
CapDrop=[ALL], two RO/rprivate binds and the exact PATH/HOME/TMPDIR environment.

| Final created Docker resource observation | Raw value |
| --- | --- |
| NanoCpus | 1000000000 |
| Memory / MemorySwap | 536870912 / 1073741824 |
| PidsLimit / CgroupnsMode | 128 / private |
| `/tmp` options | `rw,nosuid,nodev,noexec,size=1048576,nr_inodes=64,mode=1777` |
| `/control-output` options | `rw,nosuid,nodev,noexec,size=65536,nr_inodes=16,mode=1777` |

Unlike the original failed control, the scorer reached its kernel observation
loop (`final-control/docker-02.json`): cpu.max=`100000 100000`,
memory.max=`536870912`, pids.max=`128`, sampled memory.current=`2195456`,
pids.current=`1`. Mountinfo reports `/tmp` size1024k/nr_inodes64 and
`/control-output` size64k/nr_inodes16, both nosuid/nodev/noexec, and both projections
ro. These are actual samples, not peak utilization or an infallible enforcement
claim. Logging remains bounded by the inspected existing log configuration.
`host-observations.json` retains actual `id` and `docker info` output.

Native cleanup: container `hg-pristine-7a190109f07e43859e3ac605e25a95e4`,
removed=true, returncode=0, stderr="", stdout=that name plus newline
(`final-control/verdict.json`, independently `docker-04.json`).
`post-removal-inspect.json`: returncode=1, stdout=`[]\n`, stderr names “no such
object”. `post-return-projection.json`: `/tmp/hg-pristine-xnaccu3w/input`,
exists=false. All stopped probes also record removal=0 and absent-object inspect=1.
No snapshot was used; formal lifecycle=null. External actor/preparation trees,
probe exports and receipts are retained. This is bounded object/projection cleanup,
not exhaustive namespace absence.

## Refusals, including every environment confounder

The existing driver created three real stopped-instance probes and passed their
unaltered inspections to the production checker. None started or scored.

| Final probe evidence | Observation and honest attribution |
| --- | --- |
| `final-control/refusal-image-{inspect,result,commands}.json` | Unexpected actual image `sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce`; refused at image boundary, checked before environment. |
| `final-control/refusal-network-{inspect,result,commands}.json` | Bridge network, exact required environment order, correct pinned image/user/command. Refused; network attribution is isolated in this final run. |
| `final-control/refusal-mount-{inspect,result,commands}.json` | Third RO bind at /unexpected AND reordered HOME/TMPDIR/PATH. Refused, but this particular final-driver refusal is environment-confounded. |

The first successful code version is separately preserved in `control/`, run
`w-prifix-control-20261014T230846Z-29e481b7`; it also measured 0.0 (1/0/0), but its
bridge probe had reordered TMPDIR/PATH/HOME. Its mount probe reached the explicit
mount refusal. `network-followup/attempt-01/` preserves a subsequent actual bridge
probe with exact environment; it refused without starting. Nothing was normalized.

After moving the access check into the shared validator, the final fresh run above
verified the exact final production bytes. Its independent final network follow-up
is retained in `final-network-followup/attempt-01/` and also isolates bridge with
exact environment. `final-audit.json` confirms every earlier boundary condition is
true, making `host["NetworkMode"] != "none"` the first mismatching condition.

For final-code extra-mount attribution, `final-mount-followup/attempt-01/` and
`attempt-02/` preserve two further reordered-environment refusals. `attempt-03/`
has exact PATH/HOME/TMPDIR, network none, and the third RO bind; the actual checker
refuses with `artifact-only read-only mounts required`. All three attempts were
removed; none was started or scored. Exact follow-up commands were:

```sh
python3 reports/w-prifix-evidence/probe_network.py /tmp/hg-wprifix-runtime/w-prifix-control-20261014T230846Z-29e481b7
python3 reports/w-prifix-evidence/probe_network.py /tmp/hg-wprifix-runtime/w-prifix-final-20261014T231720Z-483ac92d
python3 reports/w-prifix-evidence/probe_network.py /tmp/hg-wprifix-runtime/w-prifix-final-20261014T231720Z-483ac92d mount
```

Each follow-up retains its actually executed script, create/inspect/remove/absence
commands and real raw outputs. `all-attempts-summary.json` counts **two separate
one-task/one-trial controls**, both measured zeros (total measured2/invalid0/
unmeasured0), and **11 stopped refusal probes: 11 refused, 11 removed, 0 started,
0 scored**. The final run's published partition remains 1/0/0; the preparatory
success is not hidden or pooled into a benchmark result.

## Focused regression and validation receipts

`tests/quality/test_prifix_regressions.py` has D1=6, D2=15, D3=3 cases.
**Before: 24 failed; after: 24 passed.** The exact final test/helper bytes ran in
registered isolated baseline `/tmp/hg-prifix-review` against unchanged HEAD
production bytes; `baseline-context.json` records hashes and checks this identity.
`focused-before-exact-final.txt` and `focused-after-final.txt` retain full outputs.
The first 17-case baseline and intermediate failures are preserved separately.

`reports/w-prifix-validation.txt` records checker output, focused output and the
broader **194 passed** result (252 existing openpyxl deprecation warnings), covering
both admission entry points, dispatcher/persistence, HotpotQA timeouts and
SpreadsheetBench classification. The intermediate facade failures were stale
synthetic observation/permission fixtures; those now explicitly provide the new
scorer identity and executable inert runtime, without modifying the sealed fixture.

Independent audit command:

```sh
python3 reports/w-prifix-evidence/audit_packet.py reports/w-prifix-evidence/final-control reports/w-prifix-evidence/final-network-followup reports/w-prifix-evidence/final-audit.json
```

The output file was created exclusively; rerunning needs a new output filename.
Registry checker remains valid with 28 datasets, 2 shared blockers, 11 historical
records, production_authorized=false. The registry is unchanged, including every
existing evidence locator and both blocker statuses. Journal is append-only.
No historical run/archive was overwritten or resumed; no `runs/` path was used.
Only the isolated `wg-prifix` worktree is committed; parent merge remains separate.
