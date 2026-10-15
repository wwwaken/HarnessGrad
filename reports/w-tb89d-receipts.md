# Terminal-Bench bounded live-local verifier receipts - w-tb89d

**New measured raw coverage: 1/89; cumulative unique coverage: 10/89.** Only official command verdicts accompanied by the required CTRF and reward contribute. The prior unique measured IDs are `cancel-async-tasks`, `db-wal-recovery`, `extract-elf`, `fix-git`, `git-leak-recovery`, `openssl-selfsigned-cert`, `polyglot-c-py`, `regex-log`, `sanitize-git-repo`. Raw measurements remain separate from policy-withheld publication. No shared or dataset blocker is closed; S4 remains PARTIAL.

## Selection, prerequisites and runnable remainder

The initial fixed five tasks were `log-summary-date-ranges`, `write-compressor`, `gcode-to-text`, `git-multibranch` and `sqlite-db-truncate`, covering date-range aggregation, constrained compression, G-code interpretation, SSH/Git deployment and truncated-database recovery. `batch.json` was fixed before their model trials. All passed cached image inspection, complete official source checks, shell/Python parsing and read-only network-disabled tool/input probes, with task GPU=0, no MCP, CPU<=1, memory<=2048 MiB and declared agent/verifier timeouts<=900 seconds. The initial host installer/index probes did **not** establish transitive dependency readiness: four runs later lacked CTRF, and the fifth was interrupted.

A separate no-model bootstrap probe installed ordinary dependencies in a disposable image and attempted the pinned uv download. It failed with `curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to github.com:443`; the host release-archive probe also failed at `release-assets.githubusercontent.com:443`. Raw argv, streams, image ID, limits and cleanup are in `bootstrap-prerequisite-result.json`, `github-uv-release-probe.json` and their external artifact directories. This identifies a live dependency gap; the four original invalid native records retain only their missing-CTRF reason, so this separate probe is not presented as captured stderr from those original runs.

Two additional tasks, `fix-code-vulnerability` and `kv-store-grpc`, were separately preselected in `batch-supplement.json` before either model trial. Their official scorers use pip directly. Besides the same image/source/tool/resource checks, disposable no-model containers installed the exact pinned pytest/CTRF and relevant gRPC dependencies, checked pytest's `--ctrf` option and queried installed versions/imports. No official tests, reference solutions, answers or model were used in dependency probes. The first probe mistakenly tried to import the distribution name as a Python module; its raw failure is retained, and the corrected probe checks installed distribution metadata and the actual pytest option. The observation-script syntax correction and its raw error are also retained. Neither changes task/runtime/admission behavior.

The total selection is 7 distinct new task IDs, within the recorded nine-task bound. No initial task is replaced or rerun. Fresh inventory: 89 references, 86 cached images, missing `mteb-leaderboard`, `pytorch-model-recovery`, `reshard-c4-data`. Missing images were inspected only, never pulled or executed. There are 41 metadata-bounded cached candidates. Before this work, 77 cached tasks had no measured coverage. Outside both selections remain 70 such cached tasks, including 25 metadata-bounded candidates; their runtime readiness is unverified. Exactly two supplemental tasks had successful end-to-end dependency smoke checks before launch. After execution, prerequisite-verified tasks still queued: 0. Initial local probes alone are not relabeled complete dependency readiness.

Raw command outputs live in `inventory-task-metadata-raw.json`, every `image-<task>.json`, `prerequisite-<task>.json`, `shell-syntax-<task>.json` and `dependency-bootstrap-<task>*.json`. `availability-all.json` derives the historical/new ID sets and remainder counts. The selected tests and metadata are preserved as hash-bound preimages.

## Per-task results

| Task | Inspected Docker image ID | CTRF | Raw verdict / score | Required CTRF passed / total |
| --- | --- | --- | --- | --- |
| `log-summary-date-ranges` | `sha256:cbeb6ba905c2fec294f16cd5e16e3ea7f2e04d38ac2484d51a11de262aa7dc51` | No | invalid / `null` | n/a / n/a |
| `write-compressor` | `sha256:3618e1f8a997b437c09cd3dbaac736705809c05f6f12f584b65722175970ebe1` | No | invalid / `null` | n/a / n/a |
| `gcode-to-text` | `sha256:0979ef40c6a3e8c4e7ab5b6c2524c74625a84799e15cd45dd98dcf83b11efd4d` | No | invalid / `null` | n/a / n/a |
| `git-multibranch` | `sha256:5bc449921c138295f6ddd8dca2977319fee2ce523811dbe56cec4ca663385fb5` | No | invalid / `null` | n/a / n/a |
| `sqlite-db-truncate` | `sha256:aabac93c93bd1f310e6a6fb893911d7735026ed18491c72133c9196a09092ca4` | No | invalid / `null` | n/a / n/a |
| `fix-code-vulnerability` | `sha256:cac325252991f823713b2d0441502972901dd782bd67f66c03d9b1e410dac5c0` | Yes | fail / `0.0` | 4 / 6 |
| `kv-store-grpc` | `sha256:3399400800dcb207634daa42bc1b052e831e285cc9d221eea66c47bc0fc79791` | Yes | invalid / `null` | 5 / 7 |

Observed RepoDigests, preserved separately from image IDs:

- `log-summary-date-ranges`: `docker.1panel.live/alexgshaw/log-summary-date-ranges@sha256:cbeb6ba905c2fec294f16cd5e16e3ea7f2e04d38ac2484d51a11de262aa7dc51`, `alexgshaw/log-summary-date-ranges@sha256:cbeb6ba905c2fec294f16cd5e16e3ea7f2e04d38ac2484d51a11de262aa7dc51`
- `write-compressor`: `docker.1panel.live/alexgshaw/write-compressor@sha256:3618e1f8a997b437c09cd3dbaac736705809c05f6f12f584b65722175970ebe1`, `alexgshaw/write-compressor@sha256:3618e1f8a997b437c09cd3dbaac736705809c05f6f12f584b65722175970ebe1`
- `gcode-to-text`: `docker.1panel.live/alexgshaw/gcode-to-text@sha256:0979ef40c6a3e8c4e7ab5b6c2524c74625a84799e15cd45dd98dcf83b11efd4d`, `alexgshaw/gcode-to-text@sha256:0979ef40c6a3e8c4e7ab5b6c2524c74625a84799e15cd45dd98dcf83b11efd4d`
- `git-multibranch`: `docker.1panel.live/alexgshaw/git-multibranch@sha256:5bc449921c138295f6ddd8dca2977319fee2ce523811dbe56cec4ca663385fb5`, `alexgshaw/git-multibranch@sha256:5bc449921c138295f6ddd8dca2977319fee2ce523811dbe56cec4ca663385fb5`
- `sqlite-db-truncate`: `docker.1panel.live/alexgshaw/sqlite-db-truncate@sha256:aabac93c93bd1f310e6a6fb893911d7735026ed18491c72133c9196a09092ca4`, `alexgshaw/sqlite-db-truncate@sha256:aabac93c93bd1f310e6a6fb893911d7735026ed18491c72133c9196a09092ca4`
- `fix-code-vulnerability`: `docker.1panel.live/alexgshaw/fix-code-vulnerability@sha256:cac325252991f823713b2d0441502972901dd782bd67f66c03d9b1e410dac5c0`, `alexgshaw/fix-code-vulnerability@sha256:cac325252991f823713b2d0441502972901dd782bd67f66c03d9b1e410dac5c0`
- `kv-store-grpc`: `docker.1panel.live/alexgshaw/kv-store-grpc@sha256:3399400800dcb207634daa42bc1b052e831e285cc9d221eea66c47bc0fc79791`, `alexgshaw/kv-store-grpc@sha256:3399400800dcb207634daa42bc1b052e831e285cc9d221eea66c47bc0fc79791`

`log-summary-date-ranges`: invalid reason: `{"log-summary-date-ranges": {"detail": "the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured", "stage": "check"}}`. Native driver return code: `2`. Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.

`write-compressor`: invalid reason: `{"write-compressor": {"detail": "the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured", "stage": "check"}}`. Native driver return code: `2`. Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.

`gcode-to-text`: invalid reason: `{"gcode-to-text": {"detail": "the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured", "stage": "check"}}`. Native driver return code: `2`. Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.

`git-multibranch`: invalid reason: `{"git-multibranch": {"detail": "the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured", "stage": "check"}}`. Native driver return code: `2`. Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.

`sqlite-db-truncate`: invalid reason: `{"sqlite-db-truncate": {"detail": "launcher exited 143; driver absent; no final native execution/receipt; no CTRF; task was not resumed", "stage": "observer-interruption"}}`. Native driver return code: `null`. The launcher returned 143; the driver exit code and final native result are unknown. The partial actor trace was captured before scoped orphan cleanup; no task or old ID was resumed. Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.

`fix-code-vulnerability`: Failed official checks: `test_outputs.py::test_cwe_id`, `test_outputs.py::test_hkey_error_cases`. Native driver return code: `2`. Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.

`kv-store-grpc`: invalid reason: `{"kv-store-grpc": {"detail": "timeout after 900s", "stage": "observer-agent-timeout"}}`. Native driver return code: `2`. Agent timeout is retained as an observer-invalid diagnostic; native scorer reward `0.0` and any CTRF remain visible, without converting the timeout into a task score. Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.

Metric identity: `Terminal-Bench reward_file /logs/verifier/reward.txt`; official command `bash /tests/test.sh`; required report `/logs/verifier/ctrf.json`; declared/observed measured scorer class `snapshot-service`. A reward of zero with no CTRF is invalid and excluded. Provider, timeout, scorer, interruption, snapshot and cleanup failures are never inferred to be ordinary zero scores. Explicit observed agent timeouts are excluded from valid raw coverage even when the unchanged platform subsequently runs the verifier and retains a native reward; those native values are preserved separately. The Bottle scorer runs its original repository tests and the additional `/tests/test_outputs.py` suite; the table counts the required additional-suite CTRF, while the official reward combines both exit codes. No complete original-suite CTRF tally is claimed.

## Counts and publication boundary

Raw execution ledger:

```json
{
  "selected_tasks": 7,
  "expected_trials": 7,
  "measured_tasks": 1,
  "measured_trials": 1,
  "invalid_tasks": 6,
  "unmeasured_tasks": 0
}
```

Native publication coverage, summed only over the 6 completed one-task native receipts:

```json
{
  "eligible_tasks": 6,
  "expected_trials": 6,
  "invalid_tasks": 5,
  "invalid_trials": 5,
  "measured_tasks": 0,
  "measured_trials": 0,
  "selected_tasks": 6,
  "unmeasured_tasks": 1,
  "unmeasured_trials": 1
}
```

The interrupted attempt has no final native execution or diagnostic receipt; missing native receipts=1. It is included as an observer-classified invalid/missing-CTRF attempt in the raw ledger, with no invented native outcome or score. The native `eligible_tasks` count belongs to completed one-task HG_TB_TASKS selectors; it does not certify all 89 inventory tasks as runnable. Observer-excluded agent-timeout attempts=1; native publication records are preserved verbatim even when their reason only names unknown policy enforcement. All observed publication scores are null. Valid raw measurements remain publication-unmeasured with `policy_enforcement_not_observed`; native invalid reasons remain invalid. The native gRPC publication receipt independently marks the agent timeout invalid, while retaining its scorer verdict in execution artifacts. Unknown gate/enforcement/lifecycle observations stay unknown, and no production authorization or comparable curve is claimed.

The cumulative numerator is the union of the prior 9 unique measured IDs and these newly measured IDs: `fix-code-vulnerability`. `prior-tb89c-result.json`, `prior-tb89b-result.json`, `prior-openssl-result.json` and `availability-all.json` preserve/derive this union from exact retained git command outputs.

## Invocation, seriality and endpoint binding

The local `/models` probe returned HTTP 200 and advertised `qwen3.5-9b-local`; the local chat-completion probe returned HTTP 200 and `OK`. Both raw responses are retained. Each actual task rechecked the model list. No model server was started and worker model calls used only `http://127.0.0.1:8002/v1`.

Each `attempts/<task>/command.txt` and `launch-input.json` preserves the exact executed command and environment. The common invocation is:

```text
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=<single-task> HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence <fresh-policy-input> --authorize-unobserved-diagnostic <truthful-bounded-coverage-reason> --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id <fresh-id> --runs-root <external-root> --work-root <fresh-external-work-root>
```

`--side train` satisfies the unchanged unobserved-diagnostic guard. `HG_TB_SPLIT=none` records split=null; no official train/eval split is asserted. Harness defaults and method configuration were unchanged. Model-weight digest and budget remain unknown/null.

External run roots:

- `/tmp/w-tb89d-runs-20261015T051838Z-f0b311e1`
- `/tmp/w-tb89d-supplement-runs-20261015T054835Z-c6d5f501`

| Task | Fresh run ID | External work root |
| --- | --- | --- |
| `log-summary-date-ranges` | `w-tb89d-log-summary-date-ranges-20261015T052111Z-254e4b46` | `/tmp/w-tb89d-log-summary-date-ranges-20261015T052111Z-254e4b46-work` |
| `write-compressor` | `w-tb89d-write-compressor-20261015T053445Z-32417279` | `/tmp/w-tb89d-write-compressor-20261015T053445Z-32417279-work` |
| `gcode-to-text` | `w-tb89d-gcode-to-text-20261015T053722Z-aa7e1f97` | `/tmp/w-tb89d-gcode-to-text-20261015T053722Z-aa7e1f97-work` |
| `git-multibranch` | `w-tb89d-git-multibranch-20261015T053910Z-c59479ab` | `/tmp/w-tb89d-git-multibranch-20261015T053910Z-c59479ab-work` |
| `sqlite-db-truncate` | `w-tb89d-sqlite-db-truncate-20261015T054122Z-60c1eaa2` | `/tmp/w-tb89d-sqlite-db-truncate-20261015T054122Z-60c1eaa2-work` |
| `fix-code-vulnerability` | `w-tb89d-fix-code-vulnerability-20261015T054910Z-fcc2f445` | `/tmp/w-tb89d-fix-code-vulnerability-20261015T054910Z-fcc2f445-work` |
| `kv-store-grpc` | `w-tb89d-kv-store-grpc-20261015T055051Z-13b207fd` | `/tmp/w-tb89d-kv-store-grpc-20261015T055051Z-13b207fd-work` |

| Task | Start UTC | End / cleanup observation UTC | Agent model calls | Input / output tokens |
| --- | --- | --- | --- | --- |
| `log-summary-date-ranges` | 2026-10-15T05:21:21.096806+00:00 | 2026-10-15T05:34:45.764538+00:00 | 32 | 273565 / 14249 |
| `write-compressor` | 2026-10-15T05:35:03.647263+00:00 | 2026-10-15T05:37:21.984578+00:00 | 32 | 225050 / 1145 |
| `gcode-to-text` | 2026-10-15T05:38:07.881837+00:00 | 2026-10-15T05:39:10.606273+00:00 | 10 | 29313 / 277 |
| `git-multibranch` | 2026-10-15T05:39:28.508906+00:00 | 2026-10-15T05:41:22.557608+00:00 | 17 | 26664 / 1646 |
| `sqlite-db-truncate` | 2026-10-15T05:41:45.066308+00:00 | 2026-10-15T05:47:30.314151+00:00 | unknown | unknown / unknown |
| `fix-code-vulnerability` | 2026-10-15T05:49:28.932302+00:00 | 2026-10-15T05:50:51.006416+00:00 | 32 | 272756 / 3208 |
| `kv-store-grpc` | 2026-10-15T05:51:17.733431+00:00 | 2026-10-15T06:06:51.847318+00:00 | unknown | unknown / unknown |

Worker concurrency was one; execution/cleanup intervals do not overlap. The pre-existing operator MuSiQue driver used port 8010, whose read-only observed proxy source forwards to 8001/8002. `operator-routing-observation.json`, per-run `operator-run-meta.json` and `concurrency-audit.json` retain the route and sampled process proof. The user permits operator sharing; endpoint exclusivity and timing comparability are not claimed. No operator process or server was started, stopped or changed.

An initial observer-only preflight stopped before any task driver/admission because it treated all foreign drivers as exclusive conflicts. The unused ID and raw refusal/source remain intact. Accounting for explicitly permitted operator sharing changed only the observer, with no platform gate, admission or refusal changed. Actual trials used fresh IDs. Later the initial launcher session returned 143 during `sqlite-db-truncate`; the cause and driver exit status were unobserved. The driver was absent, its container remained, and no final native receipt existed. `interrupted-run-disposition.json`, `launcher-terminal-observation.json` and external `interruption-cleanup/` preserve that distinction, the bounded partial artifact capture, scoped/exact owned cleanup and absence probes. The supplemental launcher used a new process session and new IDs. No old run was resumed.

Agent spend comes from completed retained trace usage records, including native-invalid traces. Partial trace spend remains unknown. Native aggregates are retained separately because invalid traces can be omitted from their token totals; environment-service `env_usage` is also a separate account.

## Resources, cleanup and provenance

| Task | CPU / memory MiB | Agent / verifier timeout s | Last actor / verifier SizeRw bytes | Owned objects observed absent |
| --- | --- | --- | --- | --- |
| `log-summary-date-ranges` | 1 / 2048 | 900 / 900 | 7852032 / 27615232 | True |
| `write-compressor` | 1 / 2048 | 900 / 900 | 81920 / 36646912 | True |
| `gcode-to-text` | 1 / 2048 | 900 / 900 | 4591616 / 27615232 | True |
| `git-multibranch` | 1 / 2048 | 900 / 900 | 520192 / 64344064 | True |
| `sqlite-db-truncate` | 1 / 2048 | 900 / 900 | 4685824 / unobserved | True |
| `fix-code-vulnerability` | 1 / 2048 | 900 / 900 | 401408 / 6389760 | True |
| `kv-store-grpc` | 1 / 2048 | 900 / 900 | 44302336 / 23257088 | True |

Task metadata also declares storage_mb=10240 and GPU=0. Actual Docker inspections retain CPU/memory/swap/PID/rootfs/network settings; SizeRw/statistics are samples, with no peak or filesystem-quota proof inferred. Snapshot receipts bind observed committed images and their exact inspection paths/hashes; short-lived images may be missed. The interrupted attempt never produced an observed verifier snapshot. Scoped/exact absence probes are teardown observations, with no trusted atomic lease release or lifecycle/admission attestation inferred. Resource, snapshot and cleanup observations are manifest-bound; native unknown lifecycle fields remain unknown.

This is online/proxy scorer execution. Script hashes and installed dependency smoke checks do not establish complete portable offline, image/ABI or transitive rebuild custody. No task, official scorer/test, reference solution, production runtime, method, gate or admission code was changed. Repository `runs/`, frozen receipts and the operator checkout remain untouched.

| Task | Source-list SHA-256 | Split SHA-256 | Manifest SHA-256 | Official scorer script SHA-256 |
| --- | --- | --- | --- | --- |
| `log-summary-date-ranges` | `a2669cee7129af255c8fbd4eadddd287cc1b723594f3a0818f43f1c1c33c48db` | `f69b53501ea0f7593c8fff50a51da550329499ead0625a46da906dd3f08638f1` | `cc5c79922e03c487ef0fae03ff20d316733ac25fbb2c8f347de11e9005d067e5` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `write-compressor` | `f8cbe8ce19f66aec100d87064e06515a4f65b418a2b4e2e2b872ba6244a38d6c` | `25cfcb86ef8ef89a116d3be7869682d1be5a58002c2fa7354e3393e416ae4925` | `d22cf7468124c489036d35fe48de055e5e373a9b70c1f9aa59aed01aea5ba885` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `gcode-to-text` | `36e263a7d8782dfb96f69fd20ea87c6245d44450e7d0a7e60838dbcb2957225d` | `31085ee0d076e1d3a6adc6a13e7cb9fbfeaab6589d1df12e24a264a72cb9db12` | `1f0558cc19c2fb5166d48b1184670cbbde81714e294fbdc5f68bbda1024ab668` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `git-multibranch` | `1391051f94185a0b17677a0bee2296b0513c01e65cb745a1d76809b4ea6d4ca5` | `75085087f935f99d986813aa07403fd9a71cbfb7878fe32fd4d23c3e7f9e972b` | `c9a23a611cd92b31c5f722a2592d2a93e90e42e61ed36c7eb4a0dbdab5ecc5df` | `ddbde3eea6ffa8fda105cbd86597a53bd409f41e13223900aa27e77a84b6b155` |
| `sqlite-db-truncate` | `a2981a3356a922d29c32f888a19c727b87a56a875e60c0524165dfb09918d127` | `cfcba3fbcfc9788921eb99c06f6f4bfaf5211eddf386545730c13149a829272e` | `76d0b7a0b86bc279f088556ae7aa8f2456307fca11ff1c715236cd773a26e085` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `fix-code-vulnerability` | `c054ca067bfb35a608d0bd71e0db7d218013c789d665be5f93b8749012018440` | `0e346a41a110effff84c8eb32b83c86e421b838b5e7be18683b9e4350b4c2da7` | `e0f5d9957e63d793ac6e1f91b80b71861c5a6147b25024591c1e4ce2ed37a59f` | `f1611da693cb4cfc5e8482698c6a1858a5c67220ae9db89b50aed66584e9b17f` |
| `kv-store-grpc` | `7ef43d0e9e10fd9a6065639492af49a58aa0dc0a29a057c9eb45aa7b6284e636` | `74b86f330ff0529fa0c7866abf340f3e9611bf967e2c81ef3a667b0d8096d621` | `4f5c2989d7b8b6f7c22bd19897058c380dfddc1442dcc46bb1229acf3bbc4f29` | `c348467a076bf614d0a850e25b2263f85bbf7b4c7a8d344fbd5454a0611a0df8` |

Harness-list hashes: `log-summary-date-ranges` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `write-compressor` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `gcode-to-text` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `git-multibranch` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `sqlite-db-truncate` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `fix-code-vulnerability` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `kv-store-grpc` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`.

Platform commit: `31ff59160bcca58c2bb91ebaf8e09c7c8b7db338`. Dataset commit: `2fd12b88aafdd04a52c298e3940bcb189f9766d6`. Command outputs/statuses and actual platform/source/harness content hashes are retained. Each observer manifest binds bytes before execution and is explicitly not production admission evidence.

`run-artifact-inventory.json` binds every retained file in both external roots by path, size and recomputed SHA-256. Compact review copies are under `reports/w-tb89d-evidence/attempts/`; repeated samples, raw host snapshots and original work/run artifacts remain external and intact. `SHA256SUMS` binds the review packet/report. `verify.py` audits source/hash/route/count custody, CTRF/reward agreement, interruption treatment, serial execution, the historical/new union and additive-only registry scope. Raw checker, audit and focused test output is in `reports/w-tb89d-validation.txt`. Commit is only in this registered worktree for parent review; main is untouched.

## Exact registry observation - w-tb89d

Bounded live-local Terminal-Bench execution - w-tb89d: 7 new cached task surfaces were preselected across an initial five-task selection and a supplemental two-task pip-bootstrap selection, all launched serially with unchanged loop/train diagnostic admission, rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none, HG_EGRESS_PROXY=http://172.17.0.1:17890 and direct qwen3.5-9b-local at http://127.0.0.1:8002/v1. New measured raw official verifier coverage is 1/89; cumulative unique coverage is 10/89 including the prior 9. Observer-recorded agent timeouts=1, excluded from valid raw coverage even when a native scorer reward exists. Raw ledger selected=7, expected_trials=7, measured=1, invalid=6, unmeasured=0; only command verdicts with official CTRF and reward count. Four initial native executions lacked CTRF and remain invalid; the fifth initial attempt was interrupted before a final native receipt and is excluded, with its trace preserved and exactly owned orphan resources cleaned. A no-model probe failed to download the pinned uv release through the proxy; the supplemental tasks passed full pinned pip dependency smoke checks before model trials. Initial attempts were retained, never replaced, resumed or rerun. Native publication coverage is available for 6 attempts: measured=0, invalid=5, unmeasured=1, observed scores null; 1 interrupted attempt has no native publication receipt. Inventory is 86/89 images cached; the three absent images were not pulled or executed. Outside these selections 70 cached tasks have no prior measured coverage, including 25 metadata-bounded candidates, with zero further prerequisite-verified tasks queued. This is bounded online/proxy execution evidence; complete offline closure, comparable performance, pilot expansion and production authorization are not established. S4 remains PARTIAL; no shared or dataset blocker closes, and all statuses, next_actions, history, gates and production_authorized=false remain unchanged.
