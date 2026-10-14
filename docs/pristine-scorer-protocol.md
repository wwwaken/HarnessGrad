# Pristine scorer input, completion and native evidence contract

`pristine-offline` command scorers must obey this protocol in addition to the
independently pinned bundle, task export and quota contracts. A bundle's exit
status alone cannot establish that its predicate completed. Existing exit-only
bundles therefore fail closed as unmeasured until their sealed scorer implements
the completion protocol; there is no numeric-zero compatibility fallback.

## Input identity and permissions

The platform creates the bounded data projection under an exclusive private parent.
Every projected directory has mode `0750`, every data file `0640`, and their group
is the platform process's effective primary GID. This applies explicitly to every
nested directory and survives restrictive umasks. File bytes, file allowlist,
inode/byte limits, regular-file/link checks and receipt seals retain their existing
meaning. Data files gain no execute bits and no group write or other access.

The created container explicitly runs as numeric UID `65534` and that projection
GID. The platform refuses if its own effective UID equals the reserved scorer UID.
The scorer therefore does not run as the platform host user. Admission checks the
actual `Config.User`, refuses supplemental groups, and checks read/search access to
both mounted trees plus execute access to the sealed runtime. The platform does
not chmod or chown the pinned scorer closure to make an inaccessible bundle work;
its provider must prepare readable dependencies and an executable runtime.

The only bind mounts remain the two original projections, both read-only. Rootfs
read-only, `--cap-drop ALL`, no-new-privileges, no network, fixed environment,
CPU/memory/PID configuration and bounded tmpfs scratch/output remain required.
Both original projection integrity checks still run after Docker inspection and
before start. No added mount, capability or UID matching the host writer is used.

The DAC check assumes the daemon's normal host-ID mapping. It does not establish
readability under every rootless/user-namespace/LSM configuration. A runtime denial
still has to produce a valid completion marker to be measured; otherwise it is
unmeasured. This change does not attest race-proof source quiescence or close any
shared dataset blocker.

## Completion protocol

After successfully initializing, reading all required inputs and finishing its
measurement predicate, the sealed scorer must emit **exactly one** complete stdout
line (line boundaries follow Python `str.splitlines()`; a terminating newline is optional):

- `completed_check=pass` and exit status `0` for a completed passing check.
- `completed_check=fail` and exit status `1` for a completed failing check.

The `completed_check=` stdout prefix is reserved for this protocol. The trusted
scorer must not echo untrusted input as protocol lines, emit a marker before the
predicate completes, or emit a marker from an exception handler. Other diagnostic
stdout lines and stderr are permitted. A failed initialization must emit no marker.

Missing, malformed or duplicate markers, marker/exit disagreement, an exit other
than `0`/`1`, disagreement between Docker attach returncode and stopped exit status,
OOM, runtime errors, timeout and missing stopped inspection are unmeasured with
`score=null`, `passed=false`, and an explicit `unmeasured` reason. Timeout retains
`outcome=timeout`; other unavailable outcomes use `outcome=unmeasured`. A completed
failing check remains `outcome=measured, score=0.0`. Missing-marker reasons retain
the stopped exit and a bounded stderr suffix naming initialization failures.
Isolation mismatch annotation preserves the original failure reason.

## Native evidence and cleanup

`scorer_isolation_evidence.start_result` retains Docker attach argv/returncode and
stdout/stderr. `stopped_result` retains inspection argv/returncode and stdout/stderr,
and the raw stopped `state` before classifying it, including abnormal exits. Failed
inspection retains the command result without inventing a State. `cleanup` retains
the container name, removal returncode/stdout/stderr and the `removed` Boolean; a
removal exception retains its type/message. Cleanup failure overrides any score to
unmeasured. `removed=true` means the removal command returned zero; it does not by
itself prove exhaustive namespace absence. External absence probes remain separate.
