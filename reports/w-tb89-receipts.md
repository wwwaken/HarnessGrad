# Terminal-Bench bounded no-model diagnostic attempts - w-tb89

**Real verifier coverage did not widen.** All four selected tasks were refused before task loading by the unchanged staged-driver live-model gate. There are no new verifier scores or CTRF files. New raw official execution coverage is **0/89**; cumulative coverage remains **1/89**, using the earlier OpenSSL receipt. S4 remains PARTIAL; shared and dataset blockers remain OPEN/unchanged. No production or pilot authorization follows.

The requested no-model recipe is incompatible with the current driver. `driver.py:198-213` defines `live` as a non-mock backend with a model and credentials; `driver.py:442-446` refuses every staged run unless that live binding exists and matches policy evidence. Explicit unobserved authorization does not bypass this check. The actual stderr on all four attempts is:

```text
refusing staged policy: bind evidence to the live local agent endpoint
```

Raw source/line output: `reports/w-tb89-evidence/driver-guard-source.json`. No source, gate, admission, refusal, harness descriptor, scorer, task or reference solution was modified. No alternate sampling, fake live binding, direct-verifier bypass or endpoint call was used.

## Inventory and selection

Fresh read-only local inspection found **89 task references**, **86 cached images**, and **0 tasks missing required local source files**. Missing images: `mteb-leaderboard`, `pytorch-model-recovery`, `reshard-c4-data`. Their exact `docker image inspect` errors are retained as `reports/w-tb89-evidence/inventory/image-<task-id>.json`; no image pull was attempted. These are image-cache observations, not proof that 86 verifier bootstraps can execute.

Purposeful four-task surface diversity: async code, Git/file state, CSV aggregation and regex output; require cached image, complete local verifier sources, standard pytest/CTRF-only uvx bootstrap, zero GPU, no MCP/service prerequisite, <=1 CPU and <=2048 MiB. No result-dependent substitutions. Other cached tasks remain unexecuted, not certified runnable.

The four choices were fixed before the first driver attempt in `reports/w-tb89-evidence/batch.json`. Actual runnable tasks under the exact requested no-model staged route: **zero of these four**, due to the shared live-model prerequisite. Other cached tasks have not been executed or certified runnable. The inventory does not pad the execution numerator.

Raw inventory and hashes: `reports/w-tb89-evidence/inventory.json`; every image-inspection command, exit status, stdout and stderr is under `reports/w-tb89-evidence/inventory/`. The checkout commit and status are independently captured in `dataset-commit.json` and `dataset-status.json` there. All 89 task source preimages remain intact at `/tmp/w-tb89-controls-20261015T035134Z-bf8b6a2d/preparation-packet/inventory/sources`; the four selected source sets also have repository review copies.

## Per-task results

Image IDs below and the associated RepoDigests are observed Docker values, not inferred tags. Full RepoDigests remain in `result.json` and `inventory.json`. Every attempt has `endpoint=null`, `model=null`, `HG_AGENT_BACKEND=mock`, and no verifier verdict or score.

| Task | Observed image ID / digest | CTRF produced | Verdict / score | Exact unmeasured reason |
| --- | --- | --- | --- | --- |
| `cancel-async-tasks` | `sha256:84c7fae6b256dcc56a350790e2a9715eefc7dad662a9d8e8a472363aa71ef18d` | No | None / null | `refusing staged policy: bind evidence to the live local agent endpoint` |
| `fix-git` | `sha256:61e431c00c58df652287aadce5457634d9f9330cfdd153ebdf2802df0d540119` | No | None / null | `refusing staged policy: bind evidence to the live local agent endpoint` |
| `log-summary-date-ranges` | `sha256:cbeb6ba905c2fec294f16cd5e16e3ea7f2e04d38ac2484d51a11de262aa7dc51` | No | None / null | `refusing staged policy: bind evidence to the live local agent endpoint` |
| `regex-log` | `sha256:90101b2e815323a8da20528a1439bebc407eb9761c9c68a3d557730856c878e9` | No | None / null | `refusing staged policy: bind evidence to the live local agent endpoint` |

All driver exits were **2**. The administrative attempt ledger is **measured=0, invalid=0, unmeasured=4**: four requested tasks refused before task execution, not four measured failures or ordinary zeros. Actual task trials started: **0**. Native diagnostic receipts, native invalid/unmeasured/measured trial counts and publication scores are **absent**, because the driver refused before creating any run/work directory. These administrative counts must not be read as native receipt coverage. Requested selected coverage is **4/89**, separate from the **0/89** new measured coverage.

Prior real scorer custody was read only: `reports/w-tb89-evidence/previous-official-result.json` preserves the raw read of `/tmp/hg-net/reports/w-net-evidence/launch/result.json`, including its actual verdict, raw per-task entry and CTRF summary. `reports/w-net-receipts.md` retains the historical model-run and publication limits. The one-task pinned bootstrap in `reports/w-uvx-bootstrap.md` also retains its own scope; this packet adds no successful bootstrap or offline closure.

## Fresh identities, commands and raw artifacts

Runs root (outside the platform): `/tmp/w-tb89-controls-20261015T035134Z-bf8b6a2d`. Original evidence is left intact under that root; repository review copies live under `reports/w-tb89-evidence/attempts/<task-id>/`. These are launch/refusal artifacts, not fabricated native run receipts. No existing ID was resumed, and repository `runs/` and frozen receipts were untouched.

| Task | Fresh attempted run ID | Original evidence directory |
| --- | --- | --- |
| `cancel-async-tasks` | `w-tb89-cancel-async-tasks-20261015T035134Z-86e331e8` | `/tmp/w-tb89-controls-20261015T035134Z-bf8b6a2d/w-tb89-cancel-async-tasks-20261015T035134Z-86e331e8-evidence` |
| `fix-git` | `w-tb89-fix-git-20261015T035144Z-679b6acd` | `/tmp/w-tb89-controls-20261015T035134Z-bf8b6a2d/w-tb89-fix-git-20261015T035144Z-679b6acd-evidence` |
| `log-summary-date-ranges` | `w-tb89-log-summary-date-ranges-20261015T035148Z-b2bb406e` | `/tmp/w-tb89-controls-20261015T035134Z-bf8b6a2d/w-tb89-log-summary-date-ranges-20261015T035148Z-b2bb406e-evidence` |
| `regex-log` | `w-tb89-regex-log-20261015T035326Z-26b6db7f` | `/tmp/w-tb89-controls-20261015T035134Z-bf8b6a2d/w-tb89-regex-log-20261015T035326Z-26b6db7f-evidence` |

Each original/review directory contains the exact shell command (`command.txt`), structured argv/environment (`launch-input.json`), truthful unknown-gate policy input (`policy-input.json`), source/harness/split hashes, launch manifest, raw driver stdout/stderr, exit observation and cleanup queries. The command shape is the earlier production `loop`/train route:

```text
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=<one-task> HG_TB_SPLIT=none HG_AGENT_BACKEND=mock HG_AGENT_MODEL= HG_AGENT_BASE_URL= HG_AGENT_API_KEY= HG_AGENT_MAX_STEPS=1 CUDA_VISIBLE_DEVICES= python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence <fresh-evidence>/policy-input.json --authorize-unobserved-diagnostic <explicit-operator-reason> --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id <fresh-id> --runs-root <runs-root> --work-root <external-fresh-work-root>
```

The shape above uses placeholders only for readability; the byte-for-byte commands actually executed are in each `command.txt`. `HG_AGENT_MAX_STEPS=1` bounds the mock control if admitted; no step ran. Train is the unchanged authorization guard requirement; `HG_TB_SPLIT=none` records no official train/eval split. Runs were serial, never concurrent. The first three attempts and all four image probes are in `launch.py`; the fourth driver attempt is in `finish_regex.py`. `launch.stdout.txt`, `launch.stderr.txt`, `finish-regex.stdout.txt` and `finish-regex.stderr.txt` preserve script outcomes.

## Prerequisites, resources and cleanup

Three selected images passed a disposable network-disabled probe for bash, apt-get, image-local Python and writable `/app`. Their raw output reports Python 3.13.7. The original regex-log probe exited 1 after finding bash and apt-get but no `python3` on PATH. This probe initially overrequired image-local Python: the platform has a host-interpreter fallback (`reports/w-tb89-evidence/interpreter-fallback-source.json`). It is not reported as a proven missing platform prerequisite. The unused first regex identity is preserved under `preflight-only/regex-log/`; a distinct fresh identity then received the same actual driver refusal as the other three. It is excluded from task/driver attempt counts. No result-dependent substitute task was selected.

Four prerequisite containers used cached immutable IDs with `--pull=never --network none --cpus 1 --memory 256m --pids-limit 64 --rm`; no task tests or model ran in them. Each `prerequisite-cleanup.json` records the post-removal inspect error, confirming the named probe container was absent. Host proxy probes for the first three selected tasks returned HTTP 200 for Astral and PyPI; they establish host reachability only, not verifier bootstrap or offline closure. No proxy probe contacted a model endpoint.

The selected task declarations request one CPU, 2048 MiB, no GPU, with timeouts recorded in each policy context and task preimage; these were never observed on task runtime containers because admission stopped before creation. Budget is explicitly null, model weights/hash are null because no model is bound, and no model call/token cost is claimed. Disk/process observations are retained (`inventory/disk-before.json`, `disk-final.json`, `inventory/processes-before.json`, `processes-final.json`). No task cgroup peak, filesystem quota, snapshot lifecycle, successful teardown or trusted enforcement is inferred from preflight settings.

For every actual driver attempt, scoped post-run Docker queries returned exit 0 and empty stdout for containers, networks, volumes and snapshot tags. Run/work-directory absence was checked by `collect.py`. There were no task actors, verifiers or snapshots to clean up. `result.json` binds the raw cleanup probe paths and hashes. This is owned-object absence evidence, not a passing task lifecycle attestation.

## Source and metric bindings

Metric: `Terminal-Bench reward_file /logs/verifier/reward.txt`, expected official command `bash /tests/test.sh`, CTRF path `/logs/verifier/ctrf.json`, snapshot-service declared class. The command did not execute here. All per-attempt source/split/manifest/harness hashes and null model hash/endpoint are retained in `result.json` and the policy input. Scorer-script hashes cover test.sh only and do not establish transitive package/ABI closure.

| Task | test.sh SHA-256 | Source-list SHA-256 | Split SHA-256 | Manifest SHA-256 | Harness-list SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `cancel-async-tasks` | `79600a6b863def31b4daa008297423010cd2d6243e689d67503e118e4dc53397` | `fe400305def7ab3e9cdada70929301637515e056cd846e66f6456716a3a8741e` | `522b8dff75c21fbe17354610b67a4218de43f3e71b7a6f5264586d8e43af18c2` | `f14fae9949f7a649b622ef9f0d690e8605aadbfadb58dcc06157f41fd7012465` | `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2` |
| `fix-git` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` | `a1dead1b3401bd0a4adaef76daf3aa7671093e291af23a0dbf6010a0266f1f84` | `b50cf1f1f536eac1eacb0356ae63798be43973ca99ab136467be17fe14cf1937` | `b035f1e7426c9bbebc155d49b49258e15613d133a294d1f29fcdd4f2ad0fe641` | `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2` |
| `log-summary-date-ranges` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` | `a2669cee7129af255c8fbd4eadddd287cc1b723594f3a0818f43f1c1c33c48db` | `f69b53501ea0f7593c8fff50a51da550329499ead0625a46da906dd3f08638f1` | `f37abc945463c95548be1c5f0bf79a2d0cb2575ba6e379699fe767d7048eb7f4` | `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2` |
| `regex-log` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` | `3a0dbe403a73661ab196b4b66a19bdd8a9d9e640bc5f47dcb8dedbdbe1389341` | `9793fbb16141fe0bd2a1e0d0861ec27f8d2c5c3c4e99b8b9b2fd268ccb5d3069` | `a5ad08aeec46d787fb359280f9945793f84c239628647702ec10bc509ea4f0f8` | `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2` |

`run-artifact-inventory.json` binds retained external artifacts by path, byte count and SHA-256. `SHA256SUMS` covers the repository review packet; `verify.py` rechecks both inventories and raw-output-derived counts. Exact validation commands and their output are retained in `reports/w-tb89-validation.txt`.

The first validation assertion expected capitalized Docker absence text; the raw daemon output uses lowercase. `validation-first.txt` preserves that failed assertion, corrected to compare the actual error case-insensitively. The first staged whitespace check also detected upstream trailing whitespace in the regex-log instruction review copy (`staged-first-diff-check.json`). That one repository copy is losslessly encoded in `inventory/sources/regex-log/instruction.md.json`; validation decodes and compares it with the untouched external original. No task source or raw command output was normalized.

## Exact registry observation - w-tb89

Bounded Terminal-Bench no-model route attempts - w-tb89: fresh inventory confirms 89 task references, 86 cached images and missing mteb-leaderboard, pytorch-model-recovery and reshard-c4-data images. Four preselected tasks (cancel-async-tasks, fix-git, log-summary-date-ranges, regex-log) each receive the unchanged staged-driver refusal requiring a live local agent endpoint, despite explicit unobserved authorization. No task trial, verifier score, CTRF or native diagnostic receipt is produced; administrative ledger measured=0, invalid=0, unmeasured=4 is separate from absent native trial coverage. New official execution is 0/89 and cumulative raw official task coverage remains 1/89. Endpoint/model binding is none; only bounded network-disabled prerequisite probes and documented free-proxy host probes ran. This names a no-model admission prerequisite, not expanded S4 execution or offline closure. S1/S3/S4/S5/S6 remain PARTIAL; no shared/dataset blocker closes, no gate is weakened, and statuses, next_actions, dataset/history records and production_authorized=false remain unchanged.
