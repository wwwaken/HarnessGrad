# w-tbrun3: real Terminal-Bench execution, invalid verifier result

**OPEN: no valid verifier score.** The real `openssl-selfsigned-cert` task ran with the local model, the runtime created a content-addressed snapshot, and `bash /tests/test.sh` executed in a fresh verifier container. The script wrote `0\n`, but its required `/logs/verifier/ctrf.json` was absent. The platform correctly retained an invalid trial and a null score. This is a scorer failure, not a measured task failure. `terminal_bench / cached-runtime-admission` stays open.

The raw facts below come from intact files under the runs root, with complete byte inventories in [artifact-inventory.json](w-tbrun3-evidence/artifact-inventory.json). [run-artifacts.tar.gz](w-tbrun3-evidence/run-artifacts.tar.gz) contains byte-for-byte review copies of both fresh attempts, including every launch log, Docker inspection, statistics sample and event stream; [archive-sha256.json](w-tbrun3-evidence/archive-sha256.json) records its digest and original directories. No historical receipt was changed or resumed.

## Exact invocation and invocation corrections

Working directory: `/tmp/hg-tbrun3`. Executed command, copied verbatim from `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/command.txt`:

```sh
env HG_TB_TASKS=openssl-selfsigned-cert HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence /tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/policy-input.json --authorize-unobserved-diagnostic 'Operator explicitly requests one cached Terminal-Bench task with HG_TB_SPLIT=none at round 0 to obtain its real verifier reward and lifecycle artifacts; backend enforcement observations remain absent, with no production authorization or comparable score publication.' --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id w-tbrun3-terminal-bench-20261014T194115Z-7eab177b --runs-root /tmp/hg-tbrun3/runs --work-root /tmp/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-work
```

`--harness loop` resolves at `driver.py:434` to `base_harness/loop`; its actual [harness.json](/tmp/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-work/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b/workspace/harness.json) declares `env_kinds=["files", "exec"]`. No harness, verifier, adapter or production code was edited. No tuning or improver ran.

`HG_TB_SPLIT=none` is implemented at `data/datasets/terminal_bench.py:288-289`, producing `SPLIT=null`. Both `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/selection.json` and [run_meta.json](w-tbrun3-evidence/execution/run_meta.json) record that absence of a declaration (`split_declared=false`). The no-split warning is preserved in `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b/events.jsonl`. The suggested `--side eval` cannot accompany this authorization in this checkout: `driver.py:390-396` requires the train CLI side, and `harnessgrad/loops/eval_side.py:45-48` independently requires `--from-run` for eval. The final command therefore uses `--side train`, no split and no evolution. It is not a held-out evaluation or a generalization claim.

A prior fresh **preflight refusal within this work item**, `w-tbrun3-terminal-bench-20261014T194038Z-a228b8e2`, used `loop_plain` and the same no-split configuration. It passed split loading, then `driver.py:801-804` refused because `loop_plain` has no `env_kinds` declaration and defaults to `files`; `harnessgrad/environments.py::_check_env_kinds` reports the incompatibility. No task ran under that ID. The refusal was preserved before selecting the existing exec-capable `loop` harness and a different fresh ID. Its exact command is:

```sh
env HG_TB_TASKS=openssl-selfsigned-cert HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop_plain --dataset terminal_bench --sampling diagnostic --policy-evidence /tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194038Z-a228b8e2-launch-evidence/policy-input.json --authorize-unobserved-diagnostic 'Operator explicitly requests one cached Terminal-Bench task with HG_TB_SPLIT=none at round 0 to obtain its real verifier reward and lifecycle artifacts; backend enforcement observations remain absent, with no production authorization or comparable score publication.' --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id w-tbrun3-terminal-bench-20261014T194038Z-a228b8e2 --runs-root /tmp/hg-tbrun3/runs --work-root /tmp/w-tbrun3-terminal-bench-20261014T194038Z-a228b8e2-work
```

Its raw stdout, stderr, launch input and diagnostic receipt remain under `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194038Z-a228b8e2-launch-evidence/` and `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194038Z-a228b8e2/`. The receipt has `invalid_trials=1`, `unmeasured_trials=0`, `score=null` (direct review copy: [refused/diagnostic_receipt.json](w-tbrun3-evidence/refused/diagnostic_receipt.json)). This was a flag/harness choice correction, not a code patch. Exactly one real task executed across these attempts.

## Selection, cache, endpoint and provenance

`/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/selection.json` records `task_ids=["openssl-selfsigned-cert"]`, `split=null`, and image `alexgshaw/openssl-selfsigned-cert:20251031`. `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/image-inspect.json` records successful Docker inspection of that tag and `jevloop-tb:openssl-selfsigned-cert`, both with `Id`:

```text
sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12
```

The cache's `RepoDigests` are retained verbatim in that inspection. The launched image is independently recorded by `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b/run_meta.json` (`env.image_digest`) and `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/container-inspect-00000.json` (`Image`). The preflight cache listing is `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/cached-jevloop-images.json`; no image set was fetched.

The model was actually answering before launch: `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/endpoint-probe.json` and `endpoint-models.json` record HTTP status `200` and `qwen3.5-9b-local` available at `http://127.0.0.1:8002/v1/models`. `endpoint-completion-request.json`, `endpoint-completion-probe.json` and `endpoint-completion-response.json` in the same directory preserve the chat request, HTTP `200`, response model `qwen3.5-9b-local`, and content `"OK"`. `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b/run_meta.json` binds the run to `HG_AGENT_BACKEND=openai`, model `qwen3.5-9b-local`, base URL `http://127.0.0.1:8002/v1`. The task's [progress record](w-tbrun3-evidence/execution/progress/round-0/openssl-selfsigned-cert.json) independently records gateway `target="127.0.0.1:8002"`, `connections=32`, `upstream_connect_failed=0`. No paid or second model endpoint was used.

[provenance.json](w-tbrun3-evidence/provenance.json) records these actual identities and the exact files hashed:

```json
{
  "platform": {
    "content_sha": "76111cad711aa7ecee69225e15fecec9cf1182839c457a0d675e820f4dc67272",
    "git_sha": "1d31ea8670ef140cdc1e2a885ab92f761f44623e",
    "dirty": true
  },
  "dataset_commit": "2fd12b88aafdd04a52c298e3940bcb189f9766d6",
  "harness_tree_sha": "c9146ff1e0fd7ef76621f62345d1bec770298f0a",
  "harness_manifest_path": "/tmp/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-work/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b/workspace/harness.json",
  "harness_manifest_sha256": "50b2cf63dfcbc937e4a47a04c3bda23240771103ab42c2717bfccfb3cb2a3f80",
  "run_manifest_sha256": null,
  "model_weights_sha256": null
}
```

The harness manifest hash is the SHA-256 of the actual staged `harness.json`, **not a launch-bound run manifest**. The policy context's source/split/manifest/model/harness hashes remain `null`; no unknown hash was promoted to evidence. The dataset commit comes from `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/dataset-commit.json`; `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/dataset-status.json` records an empty status. The platform dirty flag is recorded as observed, with report tooling present before launch; production files were unchanged.

Metric identity: the official verifier's `/logs/verifier/reward.txt`, with declared report `/logs/verifier/ctrf.json`. `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/policy-input.json` records `scorer_sha256="4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334"`, the hash of the copied `selected-verifier-test.sh`. This binds that script only, not its transitive apt/uv/Python dependencies. Selected `task.toml`, Dockerfile and verifier script copies remain in the same directory; their hashes are in `provenance.json`. No released solution was staged or used.

## What actually ran and why it is unmeasured

Original real run: `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b`. External harness work root: `/tmp/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-work` (also recorded in `identity.json` and `run_meta.json`). `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/launch-observation.json` records driver `returncode=2`, `run_dir_exists=true`, `work_root_exists=true`. Complete command streams are `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/driver.stdout.txt` and `driver.stderr.txt`.

`/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b/events.jsonl` records agent phase completion, snapshot completion, verifier phase completion and teardown completion. The [invalid trace](w-tbrun3-evidence/execution/progress/round-0/traces/openssl-selfsigned-cert.invalid.jsonl) preserves the real agent actions and terminal usage record: `calls=32`, `input_tokens=184834`, `output_tokens=10294`, `retries=0`. The progress record gives harness `exit_code=0`, `stderr=""`, and the cached Python overlay identity. An independent in-flight trace read is retained at `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/agent-trace-inflight.jsonl`, with its exact read command in `agent-trace-inflight-observation.json`.

`/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/docker-events.jsonl` records verifier container `b22322a448cabc659c9e8390c83fd65a33400bd10d94aa1b95ae6ba5c8794a00`, `exec_start: bash /tests/test.sh`, and its matching `exec_die` with `exitCode="0"`. That script exits successfully even when its reward-writing branch writes zero; exit status is not a measurement.

The read-only observer preserved the verifier's real reward at:

```text
/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/verifier-reward.txt-9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
```

Its exact bytes are `0\n`, SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`. `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/verifier-file-observations.json` records the source bind-mount path, verifier container identity and copy hash. No CTRF report was observed or recovered. The definitive driver reason, preserved in [diagnostic_execution.json](w-tbrun3-evidence/execution/diagnostic_execution.json) and the progress record, is:

```json
{
  "openssl-selfsigned-cert": {
    "stage": "check",
    "detail": "the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured"
  }
}
```

`eval/verification/verifier.py:367-381` marks the missing report unmeasured; `eval/run/runner.py:1103-1111` carries it as a check failure, and `driver.py:1138-1142` refuses curve publication. The retained execution has `verdicts={}`, `per_task={}`; no valid score survives. The runner drops the original check stdout/stderr and full verdict on this invalid path, so the underlying reason the verifier failed to emit CTRF is **not established by the saved artifacts**. Network/dependency failure is not asserted as a diagnosis. No second real task was run to investigate it.

Raw [diagnostic_receipt.json](w-tbrun3-evidence/execution/diagnostic_receipt.json) coverage:

```json
{
  "eligible_tasks": 1,
  "expected_trials": 1,
  "invalid_tasks": 1,
  "invalid_trials": 1,
  "measured_tasks": 0,
  "measured_trials": 0,
  "selected_tasks": 1,
  "unmeasured_tasks": 0,
  "unmeasured_trials": 0
}
```

The counter `unmeasured_trials=0` is the driver's categorical accounting: this nonmeasurement is classified as `invalid_trials=1`. It does not mean the trial was measured. Receipt `score=null`, `lifecycle=null`; enforcement has `measured=false`, `comparable=false`, `production_authorized=false`, `non_comparable_reason="policy_enforcement_not_observed"`. No comparable curve exists. `staged_plan.json`, `diagnostic_receipt.json`, `diagnostic_execution.json`, `run_meta.json`, `events.jsonl`, progress JSON and invalid trace all exist; `curve.jsonl` does not ([result.json](w-tbrun3-evidence/result.json)).

## Resource, snapshot and cleanup observations

[resource-observations.json](w-tbrun3-evidence/resource-observations.json) names every raw `container-inspect-*.json` source used and all `container-stats-*.json` samples under `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence`. Both agent and verifier inspections record `NanoCpus=1000000000`, `Memory=2147483648`, `MemorySwap=4294967296`, `PidsLimit=1024`, `ReadonlyRootfs=false`. These are observed Docker configurations, not quota or peak-consumption attestations. The last sampled `SizeRw` values are agent `4694016` and verifier `65536`, both from `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/container-inspect-00080.json`; they are samples, not maxima. Declared inputs in `selection.json` and `policy-input.json` are `cpus=1`, `memory_mb=2048`, `agent_timeout_s=900`, `verify_timeout_s=900`, `network="bridge"`; budget is `null`. No trusted runtime admission receipt was produced.

The actual committed snapshot identity was:

```json
{
  "source": "/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/snapshot-inspect-00078.json",
  "id": "sha256:d6ec4c51ac3b8ffc5cae5c7a48b8b33e331e8a27e6fb6f214f8c6707d0ddcdb5",
  "repo_tags": [
    "hg-snapshot:w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-openssl-selfsigned-cert"
  ],
  "size": 45793186,
  "parent": "sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12"
}
```

The snapshot inspector's raw stdout and the verifier's `Image` agree on that digest. [snapshot-observations.json](w-tbrun3-evidence/snapshot-observations.json) retains all snapshot inspection paths. The driver snapshot receipt still says `status="unknown"`, `receipt_sha256=null`; no successful admission was invented. A committed snapshot existed and was subsequently removed by normal teardown; the Docker image itself is not retained as a task artifact.

[cleanup-observations.json](w-tbrun3-evidence/cleanup-observations.json) preserves the raw after-run checks. `/tmp/hg-tbrun3/runs/w-tbrun3-terminal-bench-20261014T194115Z-7eab177b-launch-evidence/containers-after.json`, `networks-after.json`, and `snapshot-images-after.json` each record `returncode=0`, `stdout=""`, `stderr=""` for their run-scoped listings. `network-exact-after.json` records exit `1` and `network ... not found`; `snapshot-exact-after.json` records exit `1` and `No such image: sha256:d6ec4c51ac3b8ffc5cae5c7a48b8b33e331e8a27e6fb6f214f8c6707d0ddcdb5`. Docker container destroy events are in `docker-events.jsonl`. These are genuine absence observations, **not a cleanup admission receipt or lease-release attestation**. The driver's cleanup field remains `status="unknown"`, `receipt_sha256=null`, `lifecycle=null`.

## Disposition and validation

The registry entry remains open and now cites this actual invalid execution. Missing for closure: a valid official verifier report and score, a launch-bound run manifest identity, and the required connected runtime/resource and lifecycle receipt bindings. Raw cache/image/resource/snapshot/absence observations are preserved, but cannot fill those absent fields. Shared `scorer-offline-closure` and `artifact-only-state-export` remain attached; no production authorization or pilot expansion is claimed. The earlier source review remains unchanged as historical evidence.

[reports/w-tbrun3-validation.txt](w-tbrun3-validation.txt) contains complete commands and outputs. The initial checker passed. Focused diagnostic, split, blocker, container-state and terminal-artifact tests returned **231 passed, 2 failed**. Both failures are unchanged synthetic fixtures in `test_unobserved_diagnostic_c2.py`: their mocked verifier omits `scorer_isolation_class`, and the current `common_class` rejects all-unknown aggregation at `eval/verification/isolation.py:30`. No production or test file was changed to hide them. Post-edit validation passed: checker `valid=true`, `datasets=28`, `shared_blockers=2`, `historical_records=11`, `production_authorized=false`; registry tests `54 passed in 2.77s`, exit `0` (raw [validation-post-edit.json](w-tbrun3-evidence/validation-post-edit.json)). The archive/original byte comparison and production-diff audit are recorded in [integrity-audit.json](w-tbrun3-evidence/integrity-audit.json).
