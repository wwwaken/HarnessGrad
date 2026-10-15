# Terminal-Bench bounded live-local execution receipts - w-tb89b

**Real raw verifier execution widened by 3 tasks: 3/89 new, 4/89 cumulative including the prior OpenSSL task.** Measured tasks produced official CTRF and reward through the unchanged platform route; invalid attempts are reported separately. Shared and dataset blockers stay open; S4 remains PARTIAL. Raw verifier scores below are distinct from the policy publication receipt: 3 trials remain unmeasured for publication, with `score=null` and `policy_enforcement_not_observed`.

## Selection fixed before execution

Retain the previous four preselected tasks for async code, Git/file state, CSV aggregation and regex output; require a freshly inspected cached image, complete verifier source, zero GPU, no MCP/service dependency, <=1 CPU and <=2048 MiB. Four serial one-task diagnostics; no result-dependent substitutions. Not random or representative of benchmark performance.

Fresh command-derived inventory: **89 task references, 86 cached images**, missing mteb-leaderboard, pytorch-model-recovery, reshard-c4-data. The existing adapter's full reference pool is 89; this is not an 86-task execution or a claim that all cached tasks can run. Requested selected coverage is 4/89. Each individual driver sees exactly one eligible and selected task; summed native coverage below describes four separate one-task selections. No task reruns, substitutions, improver or method tuning occurred.

`inventory-images-raw.json` preserves the exact Docker command, exit status, stdout and stderr. `inventory.json` records the observed task metadata, immutable IDs and RepoDigests. `batch.json` fixes the four-task choice before the first model driver launch. Model-list verification returned HTTP 200 for `http://127.0.0.1:8002/v1/models` and advertised `qwen3.5-9b-local`; raw response is in `endpoint-models.json`, with another pre-run response per task. No second endpoint or paid service was used.

## Per-task raw official results

| Task | Docker image ID | CTRF | Verdict / raw reward | Official tests (passed / total) |
| --- | --- | --- | --- | --- |
| `cancel-async-tasks` | `sha256:84c7fae6b256dcc56a350790e2a9715eefc7dad662a9d8e8a472363aa71ef18d` | Yes | fail / `0.0` | 5 / 6 |
| `fix-git` | `sha256:61e431c00c58df652287aadce5457634d9f9330cfdd153ebdf2802df0d540119` | Yes | pass / `1.0` | 2 / 2 |
| `log-summary-date-ranges` | `sha256:cbeb6ba905c2fec294f16cd5e16e3ea7f2e04d38ac2484d51a11de262aa7dc51` | No | invalid / `null` | n/a / n/a |
| `regex-log` | `sha256:90101b2e815323a8da20528a1439bebc407eb9761c9c68a3d557730856c878e9` | Yes | fail / `0.0` | 0 / 1 |

Observed RepoDigests (distinct from Docker image IDs):

- `cancel-async-tasks`: `alexgshaw/cancel-async-tasks@sha256:84c7fae6b256dcc56a350790e2a9715eefc7dad662a9d8e8a472363aa71ef18d`
- `fix-git`: `docker.1panel.live/alexgshaw/fix-git@sha256:61e431c00c58df652287aadce5457634d9f9330cfdd153ebdf2802df0d540119`, `alexgshaw/fix-git@sha256:61e431c00c58df652287aadce5457634d9f9330cfdd153ebdf2802df0d540119`
- `log-summary-date-ranges`: `docker.1panel.live/alexgshaw/log-summary-date-ranges@sha256:cbeb6ba905c2fec294f16cd5e16e3ea7f2e04d38ac2484d51a11de262aa7dc51`, `alexgshaw/log-summary-date-ranges@sha256:cbeb6ba905c2fec294f16cd5e16e3ea7f2e04d38ac2484d51a11de262aa7dc51`
- `regex-log`: `alexgshaw/regex-log@sha256:90101b2e815323a8da20528a1439bebc407eb9761c9c68a3d557730856c878e9`

`cancel-async-tasks`: failed official tests `test_outputs.py::test_tasks_cancel_above_max_concurrent`. Driver exit `2` reflects the publication gate; raw verifier command kind is `command`. Full bounded verifier detail and CTRF assertion messages are preserved in its `result.json`, native execution and captured CTRF.

`fix-git`: all reported official tests passed. Driver exit `2` reflects the publication gate; raw verifier command kind is `command`. Full bounded verifier detail and CTRF assertion messages are preserved in its `result.json`, native execution and captured CTRF.

`log-summary-date-ranges`: invalid prerequisite: {'log-summary-date-ranges': {'stage': 'check', 'detail': 'the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured'}}. Driver exit `2` preserves this invalid attempt. No verifier verdict, CTRF assertion or numeric score exists; the native invalid reason and written reward bytes are retained.

`regex-log`: failed official tests `test_outputs.py::test_regex_matches_dates`. Driver exit `2` reflects the publication gate; raw verifier command kind is `command`. Full bounded verifier detail and CTRF assertion messages are preserved in its `result.json`, native execution and captured CTRF.

Metric: `Terminal-Bench reward_file /logs/verifier/reward.txt`; actual official command `bash /tests/test.sh`, report `/logs/verifier/ctrf.json`, declared scorer class `snapshot-service`, also observed in measured verdicts. Raw reward files and CTRF were copied read-only from the verifier's host bind while present and before normal teardown; `verifier-file-observations.json` records source path, container ID, observation time, byte count and SHA-256. Full official test sources and instruction preimages are preserved externally; review copies are lossless base64-in-JSON preimages. No test, reference solution, gate or runtime source was changed.

## Raw execution counts and withheld publication

Raw ledger, derived from `diagnostic_execution.json`, verdicts, CTRF and reward bytes: selected=4, expected trials=4, measured tasks/trials=3/3, invalid tasks=1, unmeasured tasks=0. Task failure with an official reward is a measurement; provider/bootstrap/timeout/cleanup failure would not be converted to zero. The CSV task lacks required `/logs/verifier/ctrf.json`: `stage=check`, `the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured`. It is invalid, has no verifier verdict or numeric score, and is excluded from the measured numerator. Its written `0
` reward bytes alone do not establish a measured task failure. The retained invalid trace proves model execution, but the normal invalid-result serialization retains only the missing-report reason; it does not preserve the verifier subprocess streams. A deeper bootstrap/package cause is therefore unknown and is not invented.

Native diagnostic receipt coverage, summing the four one-task runs:

```json
{
  "eligible_tasks": 4,
  "expected_trials": 4,
  "invalid_tasks": 1,
  "invalid_trials": 1,
  "measured_tasks": 0,
  "measured_trials": 0,
  "selected_tasks": 4,
  "unmeasured_tasks": 3,
  "unmeasured_trials": 3
}
```

All publication scores are null. Measured raw tasks have publication outcomes `policy_enforcement_not_observed`; the CSV outcome is `invalid` with the exact missing-report reason. Gate status is truthfully `unknown`, receipt digest null, and operator authorization is explicit. `production_authorized=false`. No curve or comparable diagnostic score is claimed, and no diagnostic success is used to authorize a pilot. These observations do not certify S1/S3/S4/S5/S6 closure or all cached task scorers.

## Exact route and fresh identities

Runs root: `/tmp/w-tb89b-runs-20261015T041111Z-0b0fcf46`. Native run artifacts, observer evidence and the preparation packets are left intact there; work roots are separate fresh `/tmp/` directories outside the platform. Repository `runs/`, historical/frozen receipts and the operator's main checkout were not modified.

Each task's external `<run-id>-evidence/command.txt` and review copy `reports/w-tb89b-evidence/attempts/<task-id>/command.txt` preserve its exact executed command. The common shape is the prior one-task invocation from `reports/w-net-receipts.md`:

```text
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=<one-task> HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence <fresh-evidence>/policy-input.json --authorize-unobserved-diagnostic <truthful-explicit-reason> --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id <fresh-id> --runs-root <external-runs-root> --work-root <external-fresh-work-root>
```

`train` is required by the unchanged unobserved-diagnostic guard; `HG_TB_SPLIT=none` means no official train/eval split is asserted. All model settings match the live binding. The model gateway records actual connections to `127.0.0.1:8002`, and the native harness identity names the requested model/backend. The default harness configuration is retained, with no task-specific tuning.

| Task | Fresh run ID | External work root |
| --- | --- | --- |
| `cancel-async-tasks` | `w-tb89b-cancel-async-tasks-20261015T041323Z-1c4a4e29` | `/tmp/w-tb89b-cancel-async-tasks-20261015T041323Z-1c4a4e29-work` |
| `fix-git` | `w-tb89b-fix-git-20261015T041433Z-e497dc78` | `/tmp/w-tb89b-fix-git-20261015T041433Z-e497dc78-work` |
| `log-summary-date-ranges` | `w-tb89b-log-summary-date-ranges-20261015T041523Z-1af7642d` | `/tmp/w-tb89b-log-summary-date-ranges-20261015T041523Z-1af7642d-work` |
| `regex-log` | `w-tb89b-regex-log-20261015T041744Z-f072be85` | `/tmp/w-tb89b-regex-log-20261015T041744Z-f072be85-work` |

Serial driver intervals (UTC) and observed model use:

| Task | Start | End | Model calls | Input / output tokens |
| --- | --- | --- | --- | --- |
| `cancel-async-tasks` | 2026-10-15T04:13:35.409033+00:00 | 2026-10-15T04:14:33.568799+00:00 | 4 | 2618 / 322 |
| `fix-git` | 2026-10-15T04:14:43.902318+00:00 | 2026-10-15T04:15:23.670681+00:00 | 11 | 12780 / 500 |
| `log-summary-date-ranges` | 2026-10-15T04:15:25.920060+00:00 | 2026-10-15T04:17:44.643139+00:00 | 18 | 76508 / 5473 |
| `regex-log` | 2026-10-15T04:17:47.060119+00:00 | 2026-10-15T04:19:20.855635+00:00 | 3 | 1815 / 338 |

This worker ran one task at a time with `jobs=1`; the checked intervals do not overlap. Preflight `ps` also observed an existing operator MuSiQue `--jobs 20` run using the same endpoint. It was not started, stopped or changed by this worker. Consequently global endpoint exclusivity/concurrency is not attested, and timing/resource observations cannot be treated as uncontended benchmark performance. Raw process/GPU/container observations are preserved; this does not inflate Terminal-Bench task coverage.

An initial launcher preparation failed on a missing observer-inventory field (`KeyError: missing_source`) before any run ID or driver launch. That preparation packet and stderr remain intact; a corrected observer checks the actual required source files. It is not a task attempt, resumption or gate change. All actual model diagnostics use new IDs.

## Resource, lifecycle and provenance limits

Each task declares one CPU, 2048 MiB, no task GPU, 900-second agent and verifier timeouts. The task metadata also declares storage_mb=10240; no filesystem quota enforcement is inferred. Budget and model-weight digest remain null. Actor and verifier Docker inspections observe configured `NanoCpus=1000000000`, `Memory=2147483648`, `MemorySwap=4294967296`, `PidsLimit=1024` and writable roots; both keep their owned internal network and bridge, matching the existing declared-network route. These are observations of configuration, not trusted enforcement proofs. Docker statistics and SizeRw are samples, not peaks.

| Task | Actor last sampled writable bytes | Verifier last sampled writable bytes | Owned cleanup observed absent |
| --- | --- | --- | --- |
| `cancel-async-tasks` | 4587520 | 92811264 | True |
| `fix-git` | 4775936 | 76652544 | True |
| `log-summary-date-ranges` | 4960256 | 21016576 | True |
| `regex-log` | 53248 | 234905600 | True |

Manifest-bound resource, snapshot and cleanup receipts name raw samples by exact path/digest. Scoped post-run container/network/volume/snapshot listings and exact probes of observed containers/snapshots show owned-object absence. This is normal teardown evidence, not atomic lease-release or production lifecycle attestation. Snapshot samples identify observed committed images; short-lived images may be missed. Work trees and receipts are retained.

Verifier launches were configured with the documented free proxy and declared bridge egress. This is broader real scorer execution, **not a network-denied/offline test**. `test.sh` content hashes bind the selected official scripts but do not establish their transitive package/ABI/image rebuild custody. For the invalid CSV task, native aggregate usage is zero because invalid tasks are excluded from that aggregate; the retained trial trace instead reports its actual usage, and `native-progress.json` retains its live relay counters. The table uses per-trial trace usage for every task. Model weights/version custody remains unknown beyond the responding served-model identity. Full portable runtime, all other task scorers, trusted enforcement, filesystem quota and production admission remain separate obligations.

Source and identity bindings, directly from each policy/manifest:

| Task | Source-list SHA-256 | Split SHA-256 | Manifest SHA-256 | Scorer script SHA-256 |
| --- | --- | --- | --- | --- |
| `cancel-async-tasks` | `fe400305def7ab3e9cdada70929301637515e056cd846e66f6456716a3a8741e` | `522b8dff75c21fbe17354610b67a4218de43f3e71b7a6f5264586d8e43af18c2` | `1de7529dbe3163b89509d32242c81f265b9ad9a20d6fac255ab9e09524e7d25f` | `79600a6b863def31b4daa008297423010cd2d6243e689d67503e118e4dc53397` |
| `fix-git` | `a1dead1b3401bd0a4adaef76daf3aa7671093e291af23a0dbf6010a0266f1f84` | `b50cf1f1f536eac1eacb0356ae63798be43973ca99ab136467be17fe14cf1937` | `78de6dff54fb84fb3f909c962c84f3eb170a1e2776db42b908c4a71c77006168` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `log-summary-date-ranges` | `a2669cee7129af255c8fbd4eadddd287cc1b723594f3a0818f43f1c1c33c48db` | `f69b53501ea0f7593c8fff50a51da550329499ead0625a46da906dd3f08638f1` | `ae30b11ea128b92afaf9b3ef803a3185ca0933b91f8f14ec3ea16ac024be13ec` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `regex-log` | `3a0dbe403a73661ab196b4b66a19bdd8a9d9e640bc5f47dcb8dedbdbe1389341` | `9793fbb16141fe0bd2a1e0d0861ec27f8d2c5c3c4e99b8b9b2fd268ccb5d3069` | `846acd44bdec7246fe73ba5ff5f52b51887c06ce863a6954106b5bf6e94580a2` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |

Harness-list SHA-256 per task: `cancel-async-tasks` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `fix-git` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `log-summary-date-ranges` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `regex-log` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`.

Platform source hashes and git revision, external dataset revision/status, selected source preimages, model-gateway counters, endpoint/model binding, proxy observations and launch argv/environment are retained in the packet. `run-artifact-inventory.json` hashes the retained external artifacts by path, bytes and SHA-256; `SHA256SUMS` covers the committed review packet; `verify.py` rederives raw/publication counts, validates captured bytes, model/image/context bindings, serial intervals and additive-only registry scope. Exact validation commands and raw output are in `reports/w-tb89b-validation.txt`. The worktree commit is for parent review; it is not merged to main by this worker.

## Exact registry observation - w-tb89b

Bounded live-local Terminal-Bench execution - w-tb89b: 4 preselected cached tasks (cancel-async-tasks, fix-git, log-summary-date-ranges, regex-log) ran serially through unchanged loop/train diagnostic admission, rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none and the documented proxy, against qwen3.5-9b-local at http://127.0.0.1:8002/v1. New raw official verifier coverage is 3/89, cumulative 4/89 with prior openssl-selfsigned-cert; CTRF/raw rewards are retained for measured tasks; the CSV task is invalid because its required CTRF was absent. Raw ledger measured=3, invalid=1, unmeasured=0. Native publication remains measured=0, invalid=1, unmeasured=3 with score=null and policy_enforcement_not_observed. This is bounded online/proxy execution, not offline closure, benchmark-comparable performance, pilot expansion or production authorization. S1/S3/S4/S5/S6 remain PARTIAL; all shared/dataset statuses, next_actions, gates, history and production_authorized=false remain unchanged.
