# Terminal-Bench bounded live-local execution receipts - w-tb89c

**New raw verifier coverage: 5/89; cumulative unique coverage: 9/89.** The prior measured tasks are `cancel-async-tasks` (0.0), `fix-git` (1.0), `openssl-selfsigned-cert` (0.0), `regex-log` (0.0). This batch adds only tasks supported by official CTRF and command/reward receipts. Shared and dataset blockers remain open; S4 remains PARTIAL. Raw verifier measurements are separate from withheld diagnostic publication.

## Selection and prerequisites fixed before execution

Fixed five new surfaces: SQLite WAL recovery, ELF extraction, Git leak recovery, C/Python polyglot and Git sanitization. Require cached immutable image, complete official verifier sources, shell/Python parse success, read-only network-disabled tool/input existence probes, no GPU/MCP, <=1 CPU/2048 MiB, declared agent/verifier timeouts <=900s; standard uv/pytest bootstrap via documented proxy. All five selected before any model trial; no result-dependent substitution or rerun. Purposeful coverage, not a performance sample.

Fresh inventory: 89 task references, 86 cached images. Missing images: mteb-leaderboard, pytorch-model-recovery, reshard-c4-data. Their image inspections are read-only inventory checks; no missing image was pulled or executed. There are 41 cached tasks meeting the CPU/memory/GPU/MCP/source/timeout metadata bounds, including the selected 5. There are 36 other metadata candidates and 81 cached tasks outside this selection. Neither number certifies runtime readiness. Exactly 5 selected tasks passed fresh image tool/input probes; prerequisite-verified tasks left outside this fixed selection: 0. After the batch, no further prerequisite-verified task remains queued. No task reruns or result-dependent substitutions occurred.

`inventory-task-metadata-raw.json` preserves raw task.toml text for all inventory rows. `reports/w-tb89c-evidence/inventory.json` derives the inventory from `image-<task>.json`, preserving exact Docker inspection argv, return code, stdout and stderr. `prerequisite-<task>.json` preserves each `docker run --rm --pull=never --network none --read-only` probe against the inspected immutable image ID. These probes check shell/package-manager/tool availability and existing task inputs without running the official scorer or reading reference solutions. `shell-syntax-<task>.json` and `prepare.py` bind shell/Python parse checks; complete selected test/source preimages are retained. The preparation stderr retains an upstream Python escape-sequence SyntaxWarning; parsing succeeded. Host proxy probes returned HTTP 200 for the uv installer, pytest CTRF and GitPython indexes. Actual verifier execution supplies bootstrap evidence; no offline dependency closure is inferred from host probes.

The local model-list probe returned HTTP 200 and advertised `qwen3.5-9b-local`; `endpoint-models.json` preserves the raw body and status. Each task rechecked that model before launch. No model server was started; only the local endpoint was used.

## Per-task official raw results

| Task | Docker image ID | CTRF | Verdict / raw score | Official tests passed / total |
| --- | --- | --- | --- | --- |
| `db-wal-recovery` | `sha256:0e33ea5ec823975d1bd6c3778395c9f94251dd88f571146057bff6adb7e4594e` | Yes | fail / `0.0` | 0 / 7 |
| `extract-elf` | `sha256:6932e4cb318464307eacd497ef8dc617eaf551b6a90231f815ec0b911895cfed` | Yes | fail / `0.0` | 1 / 2 |
| `git-leak-recovery` | `sha256:62160e522a4238b8bcd522411ea97b5b200f811e5899d34947e66809bef7e586` | Yes | fail / `0.0` | 4 / 5 |
| `polyglot-c-py` | `sha256:0f1c3b7816d70cf5551573fd6aeef76893f2ae3000be2419997b6871b5d987ed` | Yes | fail / `0.0` | 0 / 1 |
| `sanitize-git-repo` | `sha256:4b5234da5bb0d67f3b0bf8db40a2883c07a5219f62b64c2bf9ff1ac84cd0f672` | Yes | fail / `0.0` | 1 / 3 |

Observed RepoDigests (preserved separately from image IDs):

- `db-wal-recovery`: `docker.1panel.live/alexgshaw/db-wal-recovery@sha256:0e33ea5ec823975d1bd6c3778395c9f94251dd88f571146057bff6adb7e4594e`, `alexgshaw/db-wal-recovery@sha256:0e33ea5ec823975d1bd6c3778395c9f94251dd88f571146057bff6adb7e4594e`
- `extract-elf`: `alexgshaw/extract-elf@sha256:6932e4cb318464307eacd497ef8dc617eaf551b6a90231f815ec0b911895cfed`, `hub.rat.dev/alexgshaw/extract-elf@sha256:6932e4cb318464307eacd497ef8dc617eaf551b6a90231f815ec0b911895cfed`
- `git-leak-recovery`: `docker.1panel.live/alexgshaw/git-leak-recovery@sha256:62160e522a4238b8bcd522411ea97b5b200f811e5899d34947e66809bef7e586`, `alexgshaw/git-leak-recovery@sha256:62160e522a4238b8bcd522411ea97b5b200f811e5899d34947e66809bef7e586`
- `polyglot-c-py`: `docker.1panel.live/alexgshaw/polyglot-c-py@sha256:0f1c3b7816d70cf5551573fd6aeef76893f2ae3000be2419997b6871b5d987ed`, `alexgshaw/polyglot-c-py@sha256:0f1c3b7816d70cf5551573fd6aeef76893f2ae3000be2419997b6871b5d987ed`
- `sanitize-git-repo`: `docker.1panel.live/alexgshaw/sanitize-git-repo@sha256:4b5234da5bb0d67f3b0bf8db40a2883c07a5219f62b64c2bf9ff1ac84cd0f672`, `alexgshaw/sanitize-git-repo@sha256:4b5234da5bb0d67f3b0bf8db40a2883c07a5219f62b64c2bf9ff1ac84cd0f672`

`db-wal-recovery`: Official failures: `test_outputs.py::test_recovered_json_exists`, `test_outputs.py::test_recovered_json_is_valid`, `test_outputs.py::test_recovered_data_structure`, `test_outputs.py::test_recovered_data_sorted`, `test_outputs.py::test_recovered_data_completeness`, `test_outputs.py::test_no_duplicate_ids`, `test_outputs.py::test_wal_was_decrypted`. Driver return code: `2`. Full native result, bounded scorer detail, captured CTRF/reward and trace remain intact.

`extract-elf`: Official failures: `test_outputs.py::test_output_matches_reference`. Driver return code: `2`. Full native result, bounded scorer detail, captured CTRF/reward and trace remain intact.

`git-leak-recovery`: Official failures: `test_outputs.py::test_repository_contents_checksum`. Driver return code: `2`. Full native result, bounded scorer detail, captured CTRF/reward and trace remain intact.

`polyglot-c-py`: Official failures: `test_outputs.py::test_fibonacci_polyglot`. Driver return code: `2`. Full native result, bounded scorer detail, captured CTRF/reward and trace remain intact.

`sanitize-git-repo`: Official failures: `test_outputs.py::test_removal_of_secret_information`, `test_outputs.py::test_correct_replacement_of_secret_information`. Driver return code: `2`. Full native result, bounded scorer detail, captured CTRF/reward and trace remain intact.

Metric identity: `Terminal-Bench reward_file /logs/verifier/reward.txt`; official command `bash /tests/test.sh`, required report `/logs/verifier/ctrf.json`; scorer isolation class `snapshot-service`. `verifier-file-observations.json` records host-bind source, observed container, time, bytes and SHA-256 for read-only captures before ordinary teardown. A zero reward without CTRF is invalid, excluded from measured coverage. Provider, bootstrap, timeout, snapshot and cleanup failures are not converted into task scores.

## Counts and publication boundary

Raw execution ledger, derived from native execution/verdicts and captured bytes:

```json
{
  "selected_tasks": 5,
  "expected_trials": 5,
  "measured_tasks": 5,
  "measured_trials": 5,
  "invalid_tasks": 0,
  "unmeasured_tasks": 0
}
```

Native diagnostic publication coverage, summing separate one-task selections:

```json
{
  "eligible_tasks": 5,
  "expected_trials": 5,
  "invalid_tasks": 0,
  "invalid_trials": 0,
  "measured_tasks": 0,
  "measured_trials": 0,
  "selected_tasks": 5,
  "unmeasured_tasks": 5,
  "unmeasured_trials": 5
}
```

All publication scores are null. Measured raw outcomes remain `unmeasured` for publication with `policy_enforcement_not_observed`; any invalid outcome retains its native reason. Gate status remains `unknown`, receipt SHA-256 null, `production_authorized=false`. No curve, performance-comparable score or production admission is claimed. The cumulative numerator is the union of the prior measured task IDs and the new measured task IDs, with no overlap; `prior-tb89b-result.json` and `prior-openssl-result.json` preserve the exact `git show` output used for that union. Offline resolver/tooling coverage remains a separate scope.

## Exact invocation, model binding and serial execution

External runs root: `/tmp/w-tb89c-runs-20261015T043105Z-2bb62685`. Fresh work roots and run IDs are listed below. Repository `runs/`, frozen receipts and the operator's checkout were not changed. Each `attempts/<task>/command.txt` is an exact executed command; each `launch-input.json` preserves argv and environment. The common recipe is:

```text
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=<one-task> HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence <fresh-evidence>/policy-input.json --authorize-unobserved-diagnostic <truthful-explicit-reason> --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id <fresh-id> --runs-root <external-runs-root> --work-root <fresh-external-work-root>
```

`--side train` satisfies the unchanged unobserved-diagnostic guard; `HG_TB_SPLIT=none` records split=null and claims no official train/eval split. Default harness settings were retained. Each gateway targets `127.0.0.1:8002`, and the native harness identity names the live local model/backend. Model-weight digest is unknown/null.

| Task | Fresh run ID | Work root |
| --- | --- | --- |
| `db-wal-recovery` | `w-tb89c-db-wal-recovery-20261015T043148Z-cb15a3a7` | `/tmp/w-tb89c-db-wal-recovery-20261015T043148Z-cb15a3a7-work` |
| `extract-elf` | `w-tb89c-extract-elf-20261015T043324Z-cc8159b9` | `/tmp/w-tb89c-extract-elf-20261015T043324Z-cc8159b9-work` |
| `git-leak-recovery` | `w-tb89c-git-leak-recovery-20261015T043706Z-0ab2385b` | `/tmp/w-tb89c-git-leak-recovery-20261015T043706Z-0ab2385b-work` |
| `polyglot-c-py` | `w-tb89c-polyglot-c-py-20261015T043834Z-dc4ac8d2` | `/tmp/w-tb89c-polyglot-c-py-20261015T043834Z-dc4ac8d2-work` |
| `sanitize-git-repo` | `w-tb89c-sanitize-git-repo-20261015T044136Z-18b33773` | `/tmp/w-tb89c-sanitize-git-repo-20261015T044136Z-18b33773-work` |

| Task | Start UTC | End UTC | Model calls | Input / output tokens |
| --- | --- | --- | --- | --- |
| `db-wal-recovery` | 2026-10-15T04:31:53.817659+00:00 | 2026-10-15T04:33:24.430374+00:00 | 32 | 93410 / 1115 |
| `extract-elf` | 2026-10-15T04:33:27.177187+00:00 | 2026-10-15T04:37:06.701548+00:00 | 32 | 177480 / 11251 |
| `git-leak-recovery` | 2026-10-15T04:37:09.093664+00:00 | 2026-10-15T04:38:34.752225+00:00 | 13 | 13575 / 2515 |
| `polyglot-c-py` | 2026-10-15T04:38:37.301559+00:00 | 2026-10-15T04:41:36.367416+00:00 | 32 | 130302 / 6336 |
| `sanitize-git-repo` | 2026-10-15T04:41:47.314155+00:00 | 2026-10-15T04:43:18.506379+00:00 | 32 | 161563 / 3647 |

This worker launched one task/trial/job at a time; the driver intervals do not overlap. Preflight process snapshots observed no other platform driver. Repeated samples subsequently caught one other worktree pytest driver (`verify_demo`, run ID `vkind`) during the polyglot task. `concurrency-audit.json` preserves its exact sampled argv, sample paths/digests and raw `run_meta.json`: backend `mock`, agent model=null/base_url empty, no environment gateway/model and no method/improver model. It is a synthetic test, with no local model endpoint configured. `verify.py` requires this retained no-model proof for every foreign sampled driver and rejects any unaccounted driver. These observations are not an endpoint reservation and do not prove absence of arbitrary direct API clients. The initial overly broad receipt-audit assertion and failure output remain in `verify-pre-registry.stderr.txt`; this classification correction changed no platform gate, run or result. No operator process was started, stopped or modified. Timing is not a benchmark-performance result. Agent usage comes from the retained trial trace, including invalid traces; environment-service `env_usage` is a different account.

## Resource, snapshot, cleanup and provenance observations

| Task | Declared CPU / memory MiB | Agent / verifier timeout s | Actor / verifier last SizeRw bytes | Owned cleanup observed absent |
| --- | --- | --- | --- | --- |
| `db-wal-recovery` | 1 / 2048 | 900 / 900 | 110592 / 114855936 | True |
| `extract-elf` | 1 / 2048 | 900 / 900 | 741376 / 199593984 | True |
| `git-leak-recovery` | 1 / 2048 | 900 / 900 | 188416 / 181260288 | True |
| `polyglot-c-py` | 1 / 2048 | 900 / 900 | 72900608 / 170999808 | True |
| `sanitize-git-repo` | 1 / 2048 | 900 / 900 | 4833280 / 77459456 | True |

The selected metadata declares no task GPU and storage_mb=10240. Resource receipts bind exact Docker inspections/stats and declared limits to the manifest. Both actor and verifier inspections record CPU/memory/swap/PID/rootfs settings and actual networks. Sampled SizeRw and Docker statistics are not peaks or trusted enforcement proofs; no filesystem quota is inferred. Budget and model-weight digest remain null. Snapshot receipts identify actually observed committed images with raw inspection path/digest; short-lived images can be missed. Cleanup receipts preserve scoped container/network/volume/snapshot listings and exact probes of observed containers/snapshots. Owned-object absence is observational teardown evidence, not atomic lease release or trusted production lifecycle attestation. Native lifecycle/publication fields remain unknown.

The documented proxy and declared bridge egress are retained. This is broader online/proxy official scorer execution, not a network-denied/offline scorer test. Official script hashes do not certify transitive package, image/ABI or rebuild custody. No scorer, task, test, reference solution, runtime, gate or admission code was changed.

| Task | Source-list SHA-256 | Split SHA-256 | Manifest SHA-256 | Official scorer script SHA-256 |
| --- | --- | --- | --- | --- |
| `db-wal-recovery` | `856f0da9e07e3e01365009cbd72fa92f14174d602cc65674d3591373b0f35a1c` | `38fb19663ef648f1b3e9dd258356091dc874eaff86ecfa70f99bdae27429c460` | `6d8bb16d4c574d8c8b9469606e75ca9f3abd0020ad66138251ce15712275fd8c` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `extract-elf` | `df2ce7ddb40d35af79ac5d808c312e5b972c6333db8920825285bf01d161b2e0` | `1bcc85c07053a6b52de6d3b64c26f0a9628cad5995d602b4b64f480cd3289115` | `3fff3fbc6af0caf73481a95820fb4b989e75917f9c4c49390770c41c3bcf43dc` | `84ee50194effb4c72b9cbd0306cccaf0f855f3634227cd8359928722a53bbdaf` |
| `git-leak-recovery` | `3d88d213e5d640ac6bb0044f9d1cce5346cae0d042e26c13716ca00067e42044` | `dad4aa91331d113a1a76af70c19acb6b1bde76ab86b3301d8d878c283458fca8` | `902e9202121fda9d365e073e644f6d79c9ca9d239561f496a19878b817311314` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `polyglot-c-py` | `dc871f7eb7027cd07d228923ea1db5d02181f518ffc65981184d831ecfa9a2ae` | `a789bd94dd24831477fe77cd9995b3e1c768b3977c3a23ebf1accd0353d81025` | `40ed256356317c00589019438253a667f6dd648f7a19975ae2232a1d3bf56450` | `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` |
| `sanitize-git-repo` | `02b800eb064a2d17d9cecfb7479d6ed25bdc2e99d8672815a0450c5126fa2877` | `b9c9c8418a9aeea6c7e87b6205d6af63fa49e15b959a19a830a7bb9ca26296f5` | `07e578738e777f4daef812ea9fd0fae9d007d9fe8f1c449541af79cfe14123c7` | `16014722171ae4479112051d2e8af7d0c5bb231bae6aff1b80cfa19e718c814f` |

Harness-list SHA-256 per task: `db-wal-recovery` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `extract-elf` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `git-leak-recovery` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `polyglot-c-py` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`, `sanitize-git-repo` = `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2`.

Platform commit: `2ef797eea1dd28e7c1fc09b2983abf33d2a988b3`. Dataset commit: `2fd12b88aafdd04a52c298e3940bcb189f9766d6`. Both command outputs and working-tree statuses are preserved. Per-task platform/harness/source lists and base64 preimages bind the actual bytes. The observer manifest is a pre-execution binding, not a production admission attestation.

`run-artifact-inventory.json` preserves paths, sizes and recomputed hashes for retained external artifacts. Compact review copies live under `reports/w-tb89c-evidence/attempts/`; full repeated raw samples remain outside the platform. `SHA256SUMS` binds the review packet. `verify.py` validates byte custody, route/identity/count bindings, serial intervals, prerequisite receipts, prior/new task union and additive-only registry scope. Raw validation commands and output are in `reports/w-tb89c-validation.txt`. This worktree commit is for parent review and is not merged to main by this worker.

## Exact registry observation - w-tb89c

Bounded live-local Terminal-Bench execution - w-tb89c: 5 preselected cached tasks (db-wal-recovery, extract-elf, git-leak-recovery, polyglot-c-py, sanitize-git-repo) ran serially through unchanged loop/train diagnostic admission, rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none and HG_EGRESS_PROXY=http://172.17.0.1:17890, bound to qwen3.5-9b-local at http://127.0.0.1:8002/v1. New raw official verifier coverage is 5/89, cumulative 9/89 unique tasks including the prior 4 measured tasks. Raw ledger selected=5, expected_trials=5, measured=5, invalid=0, unmeasured=0; only tasks with official CTRF, command verdict and reward count. Native publication measured=0, invalid=0, unmeasured=5, all scores null; unknown policy enforcement remains unknown. Image/tool/input prerequisites were freshly checked for the fixed selection; 86 images are cached, with 81 cached tasks outside this selection not certified runnable. The three absent images were not executed or pulled. This is bounded online/proxy scorer execution, not offline closure, comparable benchmark performance, pilot expansion or production authorization. S1/S3/S4/S5/S6 remain PARTIAL; no shared or dataset blocker closes, and all statuses, next_actions, history, gates and production_authorized=false remain unchanged.
