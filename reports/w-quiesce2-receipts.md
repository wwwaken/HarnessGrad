# Selected-source interval observations - w-quiesce2

The demonstrated write/restore is now detected and invalidates the score.
E4 remains PARTIAL: endpoint file probes do not establish source quiescence or
native outer-run/trial binding. E1/E2/E3/E6 remain PARTIAL; E5 still needs
dataset-specific transformation/private-input/metric equivalence. Neither the
shared blocker nor any dataset blocker closes. No production authorization.

Registered worktree `/tmp/hg-quiesce2`, branch `wg-quiesce2`, baseline
`a6b97392ce6ecf01124a7fcaff88362a321d4964`. The prior report and its cited
`export_state` disclaimer were read first. Historical runs/receipts/archives,
sealed fixtures, scorer logic and `runs/` are unchanged.

## E4: selected-file changes observed, quiescence unproven

`eval/admission/artifact_admission.py:271` adds a bounded allowlist-only probe:
SHA-256, size, device/inode, nanosecond mtime/ctime, link count, mode, UID/GID.
It uses the existing no-link regular-file traversal and per-file/aggregate byte
bounds, with the existing before/after-read metadata check. It never inventories
unselected actor files. Read-induced atime changes are excluded.

`eval/verification/pristine.py:72` captures the first probe before export and
compares its selected bytes with the genuine export receipt before container
creation. Line 159 probes again after attempted container cleanup, including on
admission/scoring/timeout failure. A difference or unavailable final probe
invalidates an otherwise measured result (`passed=false`, `score=null`,
`outcome=unmeasured`); earlier timeout/cleanup failures keep their original reason.
Both projection rechecks, exact mount/runtime admission, bounds and scorer
completion/exit protocol remain enforced.

Native verdict `scorer_isolation_evidence.source_observation` records both probe
intervals and file records, `export_content_matches_before`, and one of
`no_change_observed`, `difference_observed`, `probe_unavailable`.
`scope=selected_source_file_endpoint_probes` and `quiescence_established=false`
are explicit. No-change can accompany a refused/failed execution: it never
promotes that execution to measured. This is observation across the elapsed
export/scoring/cleanup interval, not continuous interval custody.

## Reproduction and raw artifacts

All paths below are relative to `reports/w-quiesce2-evidence/`. Commands ran
from the worktree root, using the Python executable recorded in each launch:

```sh
python3 reports/w-quiesce2-evidence/collect.py --work-root /tmp/hg-wquiesce2-runtime --run-id w-quiesce2-before-20261015T-observe-a1 --phase before
python3 reports/w-quiesce2-evidence/collect.py --work-root /tmp/hg-wquiesce2-runtime --run-id w-quiesce2-after-20261015T-observe-b1 --phase after
python3 reports/w-quiesce2-evidence/audit.py reports/w-quiesce2-evidence reports/w-quiesce2-evidence/audit.json
```

These are fresh, exclusive run labels, not timestamps. Actual launch UTC times
are `2026-10-15T00:32:04.394793+00:00` (before) and
`2026-10-15T00:33:29.885991+00:00` (after), from `{before,after}/launch.json`.
Those files pin executed production/collector sources, unchanged task/metric,
fixture manifest checks, bundle/contract/image identities, limits and envelope.
`before-source/` and `after-source/` retain exact executed source bytes, verified
against every launch hash. Before production bytes come from the baseline git
objects; the new collector's unchanged bytes come from disk. These are evidence
copies, never executed as a substitute production path.

The collector reuses the prior worker's exact `production` observer from
`reports/w-quiesce-evidence/collect.py`: no gate, observation or returned result
is replaced. It changes caller-owned `answer.txt` from `41\n` to `42\n` only
after both projection checks and runtime admission, holds it through attached
scoring, then restores `41\n`. Owner-reversible 0444/0555 permissions remain.

| Real Docker case | Baseline native verdict | Updated native verdict |
| --- | --- | --- |
| Source write/restore | measured score 0.0, no source probe | unmeasured, score null, difference_observed |
| Unchanged `42\n` | measured score 1.0 | measured score 1.0, no_change_observed |

Raw mutation packets: `{before,after}/source-aba-attempt-01/` contain
`binding.json`, `events.json`, `docker-calls.json`, `verdict.json`, original/restored
source binaries, actual exported binary and cleanup/absence observations.
`audit.json` reconciles the genuine scorer predicate in both mutation cases:
actual41/expected42, completed_check=fail, exit1. The updated platform refuses to
publish that predicate's numeric score because the source changed.

Updated mutation timeline (`after/source-aba-attempt-01/events.json` and native
`verdict.json`, all actual monotonic_ns):

| Event | monotonic_ns |
| --- | ---: |
| First source probe finished | 6547348173597486 |
| Export returned | 6547348176306973 |
| Source changed to 42 | 6547348379632239 |
| Before attached scoring | 6547348380636980 |
| Attached scoring returned | 6547348684917067 |
| Source restored to 41 | 6547348686167888 |
| Final source probe started | 6547348823950026 |

Native source mtime_ns and ctime_ns both changed from `1792024411046287681` to
`1792024411570274039`; the digest remained
`040316eca5e77dbb2212c1efe8b81cb23bc67ce0ac8cb5c9d902d98bd45ddfa1` at both
probes. Thus this is real metadata detection despite equal endpoint contents.
The passing updated control is `after/unchanged-attempt-02/`, with equal native
file records and actual42/expected42, completed_check=pass, exit0.

`after/unchanged-attempt-01/` preserves a genuine environment-order admission
refusal before start: actual `[HOME=/tmp,TMPDIR=/tmp,PATH=/control-scorer]`
differs from required `[PATH=/control-scorer,HOME=/tmp,TMPDIR=/tmp]`. It is
unmeasured, not a zero, and was followed by a fresh UUID. Nothing was normalized.
Baseline: two created/removed/started, two native measurements (one unsafe
mutation acceptance), zero refusals. Updated: three created/removed, two started,
one measurement, two unmeasured (mutation plus admission refusal). No model,
GPU, endpoint, benchmark or dataset trial was used; these counts are local controls.
Classifying the baseline's accepted mutation as invalid source-integrity evidence
gives valid=1 / invalid=1 / unmeasured=0 before, and valid=1 / invalid=0 /
unmeasured=2 after. The raw native baseline score is preserved, not credited.

`copy-provenance.json` records 58 byte-identical copied raw files / 349353 bytes.
External originals and source/preparation trees remain under the two fresh
`/tmp/hg-wquiesce2-runtime/` run directories. Packet manifests seal 23 before and
33 after files. `audit.py` verifies those seals, source pins, event ordering,
predicate results, source/export bytes, native bindings and cleanup. `audit.json`
and `audit-output.txt` contain the derived results; outer `SHA256SUMS` seals the
committed evidence including source archives and retained failed test output.

## Residual threat model

Detected on a trusted ordinary host/filesystem: persistent selected-file content,
size or identity/metadata differences; ordinary same-inode write/restore even
when mtime is reset with `utime` (ctime remains changed); observed replacement
inodes; export bytes differing from the first probe. Missing, linked, oversized
or unreadable final selected state produces probe_unavailable and no score.
Focused tests exercise these paths, pre-export mismatch, timeout and cleanup.

Undetected: unselected-file changes, directory/ancestor namespace history and
any mutation that leaves every sampled file field/digest equal. A focused
counterexample actually swaps the source directory for a prepared changed tree
during scoring and restores the original directory before the final probe. The
original selected inodes never change, so status is no_change_observed even
though the source pathname contained different bytes. The test deliberately
retains this limitation; this is a same-UID attack without privileged timestamp
restoration. Multi-file probes are sequential, not an atomic snapshot.

A compromised observer/platform, privileged or filesystem-level metadata
restoration/rollback, unusual timestamp semantics/resolution, races that show
the original files only at probes, or mutation after the final probe are also
outside the guarantee. Ordinary `utime` alone cannot reset kernel ctime on this
host; that does not turn these probes into writer exclusion. A trusted lifecycle
or immutable snapshot/custody backend is still needed for actual E4 quiescence.
The existing `export_state` caller-quiescence obligation remains at
`eval/admission/artifact_admission.py:312`.

## Trial binding remains incomplete

`eval/verification/pristine.py:67` now explicitly records `execution_binding`.
It binds contract task/source/contract pins and exported bytes to the generated
runtime/export UUID; a supplied selected task is checked before probing/export.
Real observer calls still prove wrong requested export-run IDs are refused;
focused tests retain wrong-task refusal before any export/create/start.

The updated mutation runtime/export ID is
`hg-pristine-b54a2ea99d614522a6f13cf53b0aaee4`; the passing updated control ID is
`hg-pristine-a5cbaeef81d84d07a4c39a980e2b8bb1` (their native verdicts and Docker
calls). Each observer binding names its distinct outer run/task/trial=1, but
native `_verify`/`pristine.verify` still receive no outer-run/trial inputs.
Native fields honestly say `outer_run_id=null`, `trial_id=null`,
`outer_run_trial_binding=not_provided`; `selected_task_checked` distinguishes
calls without a task input. Remaining: receive and enforce execution-bound
outer-run/trial identities end to end, beyond a generated runtime UUID or
observer envelope. No trial-binding claim was added to the v1 export receipt.

## Validation and shared blocker decision

`tests-before.txt`: the same ABA assertion fails twice (with/without mtime
restoration), while two unchanged existing measurement cases pass: **2 failed,
2 passed**. `tests-after.txt`: **4 passed**, same selection after implementation.
`tests-focused.txt` retains the initial broader result (177 passed, one failed):
the historical receipt auditor compared its pinned historical code to newly
edited production files. The test now supplies git-authenticated historical
bytes to that unchanged auditor; every original SHA-256 check still runs.
No historical receipt, manifest or audit script was edited.

Final commands and exact checker/focused-test output are in
`reports/w-quiesce2-validation.txt`. Registry changes only sharpen this shared
blocker's observed scope and add this locator. E1/E2/E3/E4/E5/E6 remain PARTIAL;
all blocker statuses, next actions, dataset records, gates and historical evidence
are preserved. E4 still needs trusted continuous custody and native outer-run/trial
binding; E5 still needs dataset-specific equivalence. No blocker closes.
