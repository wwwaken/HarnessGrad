# Mounted timeout cleanup repair - w-e6fix

**S1/S3/S4/S5/S6 and E4/E5/E6 remain PARTIAL. No shared or dataset blocker closes.**

The bounded offline control reproduced the mounted verifier leak before the fix
and observed native verifier/service/network removal afterward. The production
change gives each `container.run()` invocation a fresh UUID name and removes that
exact container in `finally`. Existing pin refusal, mounts, UID, resource limits,
network selection, `--rm`, result streams and timeout classification remain intact.
This fixes the shared mounted actor/verifier helper; it does not certify complete
snapshot lifecycle cleanup or authorize H0.

## Read first and precise cause

Read `AGENTS.md`, `reports/w-e6-lifecycle.md`, the original collector/probe, and
`reports/w-e6-evidence/w-e6-20261015T033109Z-e7153160/summary.json` before new
execution. Its `commands/0028-platform-network.stderr.txt` preserves the active
endpoint error. Its `commands/0031-after-service-stop-before-rescue-inspect.stdout.txt`
preserves the surviving verifier inspection. Those historical files are untouched.

Baseline `eval/containers/container.py:611` (preserved verbatim as
`reports/w-e6fix-evidence/container-before.py`) calls
`subprocess.run(docker_run_argv, timeout=...)` with no teardown boundary or owned
container identity. Python kills/waits for the Docker CLI on timeout; the daemon's
still-running container does not exit, so Docker's `--rm` never runs. The exception
reaches `eval/verification/verifier.py:656`, returning an unmeasured timeout.
`verifier.py:499` only exits the host verdict `TemporaryDirectory`; unlinking its
host directory does not release a container bind mount.

`services.mounts_for()` supplies the RO recording bind at `services.py:475`.
`RunningServices.stop()` at `services.py:206` removes its service ID, then attempts
the network removal. The recording mount **does not prevent service-container
removal**: the verifier is an independent container. Its active network endpoint
blocks network removal. The bind and endpoint are co-retained by that container;
the mount itself is not Docker's network-removal predicate. Removing the verifier
releases both. The retained host recording directory is evidence, not a container
or network leak.

The repaired call is `eval/containers/container.py:618`; its `finally` calls
`remove_container(name)` at `:620`. That existing helper at `:981` issues bounded
`docker rm --force` with a 120-second transport timeout, tolerates already removed
containers and cannot replace the original timeout with its transport errors.
The control independently verifies absence; helper invocation alone is not proof
of removal. Existing helper transport/daemon failures remain best-effort and are
not strengthened or hidden by this report.

## Collector claim checked against source

The original collector outer `finally`,
`tests/fixtures/hg_we6/collect.py:312`, calls `container.remove_image` at `:326`
and `services.remove_network` at `:330`. These are exactly the helpers called by
the snapshot actor driver at `eval/containers/container_state.py:246` and `:250`.
The collector's snapshot-local finally also removes its seed actor and network at
`collect.py:239`. Its AppWorld finally calls `RunningServices.stop()` at `:289`,
matching `eval/run/runner.py:578`.

**The baseline mounted timeout never reaches `remove_container`.** The original
collector rescue at `collect.py:322` is a separate explicit `docker rm --force`
command, after preserving the leak. Image/network helpers cannot remove the
mounted verifier. Thus the report's narrow same-image/network-helper claim is
correct; it is not evidence that the full driver's teardown or a verifier-removal
helper executed. Numbered complete reviewed sources and actual SHA-256 hashes are
preserved in `reports/w-e6fix-evidence/source-audit.txt`.

## Bounded live before/after receipts

Executed, from the registered `/tmp/hg-e6fix` worktree on `wg-e6fix`:

```sh
timeout 80s python3 tests/fixtures/hg_we6fix/control.py before
timeout 80s python3 tests/fixtures/hg_we6fix/control.py after
```

Raw console streams are `reports/w-e6fix-evidence/live-before.txt` and
`live-after.txt`. Their fresh packets are:

- `reports/w-e6fix-evidence/w-e6fix-before-9d6a0ecfe85a41a69a6edf96146436dc/`
- `reports/w-e6fix-evidence/w-e6fix-after-6998065eb1404cdea0689472399b7532/`

Each contains executed control/source copies, source hashes, full subprocess argv,
timeouts, outputs/return codes/exceptions, image/config/mount inspections and
`summary.json` with native-before-rescue and final cleanup observations. Each run
starts one authored idle recording service with a 45-second self deadline and
performs normal and 3-second timeout checks using production service, recording
mount and verifier helpers. Normal checks have a 10-second deadline; each checker
thread has a 20-second observation bound. The service health command is Python
`pass`; no HTTP/API/model call or benchmark scorer is executed.

The runtime is the actual cached AppWorld verifier image, freshly inspected before
launch; its exact content address is in `preflight.txt` and both packet summaries.
The service behavior is authored idle Python, **not AppWorld startup/API replay**.
No task pool, gold, split, model, GPU or endpoint is used. Metric identity is the
authored lifecycle predicate: mount accessibility, unchanged timeout verdict,
container absence and owned-network removal. Dataset eligible/selected/task/trial
coverage and benchmark invalid/failure counts are N/A. There are two normal
authored predicate returns and two explicitly unmeasured authored timeout returns
across the two packets; no benchmark score or measured failure is inferred.

Before repair, verifier
`f51fefbe412bdb570c0e7a2999fa0390056ef91aaded9d80509c9bdf171afc4b`
remains running after `_verify` and native service stop. Its inspection retains
`/recordings/recording` RO, `/app` RO and `/verifier` RW. Service absence is
observed while the owned network still exists with `has active endpoints` in the
native removal error. The collector then rescues only its observed verifier ID
and retries stop; final exact container and network inspections show absence.

After repair, verifier
`ed200b7516d0632ebb1bdf49c3f8dc817c59c32e703dd2a8584cc630590cf919`
is observed live with the same mount permissions, then absent immediately after
`_verify` returns. Native `running.stop()` returns `[]`; the service and network
are absent **before rescue**. No ID-based collector rescue executes. The new
name-based production removal command is preserved in the subprocess receipts.
The normal predicate still returns reward 1, while timeout remains
`outcome=timeout`, `passed=false`, `unmeasured` and without a score.

Inspected verifier configurations retain 2 CPU, 4294967296-byte memory and 1024
PID limits, RO rootfs and its existing `/tmp` tmpfs. This is configuration
observation, not limit exhaustion, a filesystem quota or sizing sufficiency.
Recording directories and external work roots are retained intentionally. Object
absence establishes release of those containers' bind mounts/endpoints; no
exhaustive host process or daemon-wide absence claim is made.

## Other timeout and early-exit shapes

| Route | Verified cleanup reachability and remaining boundary |
| --- | --- |
| Mounted actor | `eval/run/runner.py:463` invokes the same `container.run()` helper as mounted verification at `verifier.py:618`. It shares the baseline defect and this repair, including its writable task/harness mounts. No model-bearing actor or complete driver run was launched. |
| Snapshot-service verifier (GAIA/Tau/TB container state) | `verifier.py:302` creates a separately named verifier; checker timeout at `:331`, missing argv at `:322`, and post-create staging errors reach `finally :412`, which removes it before `startup.close()`. New offline tests exercise all three exits and their teardown order; historical w-e6 GAIA/Tau live coverage retains its limits. |
| Snapshot verifier create acknowledgement | `created=True` is assigned only after create returns at `verifier.py:306`. A daemon allocation followed by client timeout at `:302` can therefore skip removal at `:413`, while idle host scratch closes. This is a source-confirmed risk, not newly measured live behavior or a fixed branch. |
| Snapshot actor | `container_state.py:181` catches actor exec timeout, then stop/commit at `:190`/`:191`; outer `finally :235` removes the snapshot, actor and network. Its create at `:92` also precedes `created=True :110`, leaving the same allocation/acknowledgement uncertainty on early create timeout. |
| Pristine | `pristine.py:130` sets `attempted=True` before create. `finally :172` attempts named removal even when create/start times out and records failures as unmeasured. New offline create/start-timeout tests verify removal and no score. The mounted omission is absent here; no live pristine equivalence is newly asserted. |
| Service startup | `services.py:414` starts the service before saving its ID at `:419`. Allocation followed by client timeout leaves it outside the dictionary passed to stop at `:429`; a recording/network leak is possible. Separate source-only risk; not silently counted as a passing control. |
| Interpreter discovery | Baseline `container.py:406` (`:407` after repair) uses an unnamed `docker run --rm` in `image_python()`, catches timeout at `:411`/`:412`, and lacks daemon-container teardown. No recording/owned service network is passed, but an image shell that never returns can leave a container. Source-only finding, outside the shared `run()` fix. |

Network creation (`container_state.py:79`, `services.py:245`) and commit
(`container_state.py:191`, baseline `container.py:959`) likewise need successful
client acknowledgements to save cleanup identities. Unknown allocation/commit
results can escape the outer identity-conditional cleanup. These are additional
source-level limitations, not observed live leaks in this packet. Existing
`remove_container`/`remove_image` ignore daemon return codes and swallow transport
errors; the live exact-object checks are why this report can claim success only
for the bounded mounted route. No cleanup/refusal/admission is weakened to test
or conceal those gaps.

## Tests, validation and registry boundary

The identical focused file `tests/quality/test_w_e6fix_cleanup.py` changes from
**7 failed, 1 passed** before production repair to **8 passed** afterward, with
complete outputs in `tests-before.txt` / `tests-after.txt`. It models daemon
allocation before client timeout/interruption/error, checks exact owned removal,
normal/nonzero stream preservation, distinct per-call identities, retained
pin refusal and verifier-to-service network teardown ordering.

The broader offline invocation records **105 passed, 3 failed, 1 deselected** in
`regressions.txt`; it includes the five new adjacent exit controls, verifier,
service command/start cleanup, snapshot identity and pristine gate tests. The
excluded test is the explicit live-Docker service test. All three failures are
pre-existing cases in `test_verifier_declared_network_w_net.py`: their unpinned
`synthetic-snapshot` is refused by the current snapshot identity gate before the
expected verifier is created. `baseline_tests.py` loads the preserved baseline
module without changing production files; `network-baseline.txt` records the
same **3 failed** cases. They are preserved as failures, not omitted or repaired
by weakening identity admission.

`reports/w-e6fix-validation.txt` records exact validation commands/results,
including the registry/source-only checks, packet audit, diff review and manifest
verification. The independent packet audit verifies actual source hashes,
before/after state and limits, no-rescue native success, test outcomes, and the
strict additive registry boundary.

Only `artifact-only-state-export.observed` and its evidence list gain this exact
mounted-helper repair and remaining-route findings. Both shared statuses and full
next_actions, every dataset blocker/reference/history, review authorization and
all admission/refusal gates are unchanged. All work and the final commit remain
in this worktree for parent review; no merge to main, `runs/` modification, frozen
receipt edit, old run-ID resumption, package acquisition, benchmark scoring run,
model/GPU/endpoint or paid endpoint call occurs.
