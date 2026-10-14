# w-tbrun4: proxy configured, real task executed, verifier still invalid

**OPEN: no valid verifier score; required `/logs/verifier/ctrf.json` is absent.** The real cached `openssl-selfsigned-cert` task ran with the local model, and its snapshot was checked in a fresh container. The configured proxy is present in the saved run metadata. The verifier wrote `0\n` without CTRF, so this is a scorer nonmeasurement, not a measured failure or a score of zero. The run is preserved and the blocker remains open.

A concrete runtime network defect is now identified: `eval/containers/container_state.py:79` unconditionally creates an internal network, and `:216-217` passes it to the verifier instead of the task's declared `bridge`. `eval/service/services.py:245` creates that network with `--internal`. A separate no-model control reproduced `Network is unreachable` for the documented proxy on that network type. Per the instruction to stop at a genuine code defect, no second benchmark task/trial or code workaround was attempted.

## Exact launch and why these flags

Working directory: `/tmp/hg-tbrun4`. Exact saved command: `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/command.txt` (review copy [command.txt](w-tbrun4-evidence/launch/command.txt)).

```sh
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=openssl-selfsigned-cert HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence /tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/policy-input.json --authorize-unobserved-diagnostic 'Operator explicitly requests one real cached openssl-selfsigned-cert diagnostic with HG_TB_SPLIT=none and the documented verifier egress proxy to obtain CTRF and a raw verifier score; runtime observations remain incomplete, with no comparable score publication, pilot expansion or production authorization.' --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id w-tbrun4-terminal-bench-20261014T195342Z-82530223 --runs-root /tmp/hg-tbrun4/runs --work-root /tmp/w-tbrun4-terminal-bench-20261014T195342Z-82530223-work
```

The previous reports at `/tmp/hg-tbrun/reports/w-tbrun-receipts.md`, `/tmp/hg-tbrun2/reports/w-tbrun2-receipts.md`, and `/tmp/hg-tbrun3/reports/w-tbrun3-receipts.md` were read before launch. The flag corrections are existing interfaces, not patches:

- `HG_TB_TASKS=openssl-selfsigned-cert` selects the cached task; `HG_TB_SPLIT=none` uses the adapter's supported undeclared split (`data/datasets/terminal_bench.py:288-289`). [selection.json](w-tbrun4-evidence/launch/selection.json) records the actual task list and `split=null`.
- `--rounds 0 --trials 1 --jobs 1` satisfies `eval/policy/diagnostic_policy.py:100-104`. No improver or tuning ran. No held-out claim is made.
- `--side train` is required by `driver.py:390-396` for this authorization; the suggested eval side would be refused. `loop_plain` lacks `env_kinds` and cannot run this exec environment; the existing `loop` descriptor declares `files` and `exec` ([harness-descriptor.json](w-tbrun4-evidence/launch/harness-descriptor.json)).
- `--policy-evidence` supplies the required context (`driver.py:402-413`) with gates honestly `unknown`; no admission evidence was invented. [policy-input.json](w-tbrun4-evidence/launch/policy-input.json) is the exact input.
- `HG_EGRESS_PROXY=http://172.17.0.1:17890` matches `docs/egress.md` and is intended for verifier processes only. [launch-input.json](w-tbrun4-evidence/launch/launch-input.json) records that environment; `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/run_meta.json` records `config.egress.proxy` with that same value.
- Fresh ID and external work root are preserved in `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/identity.json`. No old ID was resumed, no earlier run was overwritten, and no image set was pulled.

Selected image: `alexgshaw/openssl-selfsigned-cert:20251031`, also cached as `jevloop-tb:openssl-selfsigned-cert`. This task was retained because its official `tests/test.sh` downloads the uv installer from `astral.sh`, then runs pytest with `--ctrf`; it exercises the requested egress path. The exact original script, task metadata and Dockerfile are saved in `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/selected-verifier-test.sh`, `selected-task.toml`, and `selected-Dockerfile` (review copies under [launch/](w-tbrun4-evidence/launch)). No released solution was staged or consulted.

## Endpoint and proxy preflight

[endpoint-probe.json](w-tbrun4-evidence/launch/endpoint-probe.json) and [endpoint-models.json](w-tbrun4-evidence/launch/endpoint-models.json) preserve the responding model list from `http://127.0.0.1:8002/v1/models`. [endpoint-completion-probe.json](w-tbrun4-evidence/launch/endpoint-completion-probe.json) records HTTP `200` from the actual completion probe; [endpoint-completion-response.json](w-tbrun4-evidence/launch/endpoint-completion-response.json) records model `qwen3.5-9b-local` and content `OK`. The request is preserved beside them. The execution binding is independently saved at `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/run_meta.json` → `config.agent`: `backend=openai`, `model=qwen3.5-9b-local`, `base_url=http://127.0.0.1:8002/v1`. No paid or second model endpoint was used.

Host proxy probes [proxy-astral.json](w-tbrun4-evidence/launch/proxy-astral.json) and [proxy-pypi.json](w-tbrun4-evidence/launch/proxy-pypi.json) each record `returncode=0`, `stdout="200"`, `stderr=""` for curl through the canonical proxy. Host success did not establish reachability from the task's actual internal network; that distinction matters below.

## Real execution, verdict and coverage

Original driver run: `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223`. Launch evidence: `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence`. External work root: `/tmp/w-tbrun4-terminal-bench-20261014T195342Z-82530223-work`. [launch-observation.json](w-tbrun4-evidence/launch/launch-observation.json) records driver `returncode=2` and both run/work-root existence checks `true`.

`/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/events.jsonl` records agent, snapshot, verifier and teardown completion. `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/docker-events.jsonl` records a real `exec_start: bash /tests/test.sh` and its matching `exec_die` with `exitCode="0"` in verifier container `e5ee4383008ff87c7d2e986ab5e8ee283629e0c2646df9d539ba54ac5793e6bf`. Script exit success is not a task score: the official script writes its reward even when the tests cannot start.

[verifier-file-observations.json](w-tbrun4-evidence/launch/verifier-file-observations.json) preserves the observed fresh bind-mount reward. Exact source/copy/hash values:

```json
[
  {
    "observed_at": "2026-10-14T19:56:39.530552+00:00",
    "container_id": "e5ee4383008ff87c7d2e986ab5e8ee283629e0c2646df9d539ba54ac5793e6bf",
    "source": "/tmp/hg-cstate-8s0bi9vo/verdict/reward.txt",
    "copy": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/verifier-reward.txt-9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "sha256": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
    "bytes": 2
  }
]
```

The reward copy's bytes are `0\n`. No CTRF report was captured. This is corroborated by the platform's definitive invalid reason in `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/diagnostic_execution.json`:

```json
{
  "openssl-selfsigned-cert": {
    "stage": "check",
    "detail": "the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured"
  }
}
```

The complete saved raw scorer aggregates are `verdicts={}`, `per_task={}`. Thus no valid verifier verdict or score survives. `eval/verification/verifier.py:369-370` detects the missing report; `eval/run/runner.py:1098-1111` classifies it invalid. The runner drops the full invalid verdict and its stdout/stderr, so the exact failed bootstrap command cannot be recovered from this task run. Network-control evidence below establishes a real reachability defect without claiming to recover those lost streams.

Coverage and score read directly from `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/diagnostic_receipt.json` ([review copy](w-tbrun4-evidence/execution/diagnostic_receipt.json)):

```json
{
  "coverage": {
    "eligible_tasks": 1,
    "expected_trials": 1,
    "invalid_tasks": 1,
    "invalid_trials": 1,
    "measured_tasks": 0,
    "measured_trials": 0,
    "selected_tasks": 1,
    "unmeasured_tasks": 0,
    "unmeasured_trials": 0
  },
  "score": null,
  "outcomes": [
    {
      "reason": "{\"detail\": \"the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured\", \"stage\": \"check\"}",
      "score": null,
      "status": "invalid",
      "task_id": "openssl-selfsigned-cert",
      "trial": 1
    }
  ]
}
```

`unmeasured_trials=0` is categorical accounting: this nonmeasurement is classified invalid. It does not mean the task was measured. The authorization independently records `measured=false`, `comparable=false`, `production_authorized=false`, `non_comparable_reason=policy_enforcement_not_observed`. A future valid raw reward would still be distinct from a publishable diagnostic measurement (`eval/policy/diagnostic_policy.py:181-186`). No curve exists (`/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/result.json`, `curve_present=false`).

## Runtime network defect and no-model reproduction

The real task's saved declared environment is `network="bridge"` in `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/selection.json`. Its actual verifier `HostConfig.NetworkMode`, saved in `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/container-inspect-00081.json`, is the owned internal network `hg-w-tbrun4-terminal-bench-20261014T195342Z-82530223-openssl-selfsigned-cert`. The code paths are:

- `eval/containers/container_state.py:76-79`: unconditional `services_mod.create_network(...)`.
- `eval/service/services.py:245-247`: `docker network create --internal`.
- `eval/containers/container_state.py:213-218`: verifier receives that internal `network_name`; the adapter's declared `network` is used only if `network_name` is null, which this path never leaves it.
- `eval/verification/verifier.py:287-288,309-312`: creates the verifier on the supplied network and correctly passes `_check_env()` to its process. `_check_env` contains the proxy flags, but does not create a route to the proxy.

The isolated no-model control is preserved under `/tmp/hg-tbrun4/runs/w-tbrun4-egress-control-20261014T195910Z-ec4ee67b` (direct review copies [network-control/](w-tbrun4-evidence/network-control/)). [network-control.py](w-tbrun4-evidence/network-control.py) is the exact observer tool. `identity.json` states `model_calls=false`. It runs Python URL requests in the same cached image, with explicit proxy `http://172.17.0.1:17890`, once on the default bridge and once on a newly owned `--internal` network. It runs no task, verifier, solution, model or scorer and produces no benchmark score. Exact commands, streams and route-table readouts are in `bridge.json` and `internal.json`; `network-inspect.json` records `Internal=true`.

Raw URL observations, retaining the important host/container distinction:

```json
{
  "bridge": [
    {
      "url": "https://pypi.org/simple/",
      "status": 200
    },
    {
      "url": "https://astral.sh/uv/0.9.5/install.sh",
      "error": "HTTP Error 403: Forbidden",
      "error_class": "HTTPError"
    }
  ],
  "internal": [
    {
      "url": "https://pypi.org/simple/",
      "error": "<urlopen error [Errno 101] Network is unreachable>",
      "error_class": "URLError"
    },
    {
      "url": "https://astral.sh/uv/0.9.5/install.sh",
      "error": "<urlopen error [Errno 101] Network is unreachable>",
      "error_class": "URLError"
    }
  ]
}
```

Both internal-network requests fail with `[Errno 101] Network is unreachable`, and its saved `/proc/net/route` has no default route. The bridge control reaches PyPI; its Python request for the uv installer receives HTTP 403 even though the host curl preflight got HTTP 200. That separate HTTP difference is not resolved or relabelled as success. Either way, the actual verifier's internal network cannot reach the configured bridge proxy. No model rerun, alternate task, network attachment, temporary forwarder, or production-code fix was attempted after finding this defect.

The control's `network-remove.json` records the real removal command result. Its `containers-after.json` and `networks-after.json` record empty owned listings. These are control cleanup observations, not task score or admission receipts.

## Manifest, image and provenance receipts

A pre-execution observer manifest `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/launch-manifest.json` binds selection, image ID, source/harness file manifests, split, endpoint, resources, work root and run identity. Its actual SHA-256 is carried into the driver's `staged_plan.json`, `run_meta.json` and `diagnostic_receipt.json` as `context.hashes.manifest`, and all observer receipts use the same binding. This is an observer-authored manifest, not an invented production admission attestation.

Raw context hashes from the diagnostic receipt:

| Identity | Raw SHA-256 or unknown |
| --- | --- |
| `harness` | `84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2` |
| `manifest` | `0f28db5e637d925b054739f0f5604d259b8aad07a97c8d00082da49003499471` |
| `model` | `None` |
| `source` | `54985eac4739288c2fd1d686ae840c16f8fd317bdde0f8fb654e8bcc86df387b` |
| `split` | `362537284993db7da273d45c8041331811fad1ad73f17eddc2c8bc8f97895810` |

`source-files.json`, `split-selection.json` and `harness-files.json` are the exact bytes hashed for those fields. [provenance.json](w-tbrun4-evidence/launch/provenance.json) records:

```json
{
  "binding": {
    "adapter_id": "terminal_bench",
    "run_id": "w-tbrun4-terminal-bench-20261014T195342Z-82530223",
    "trial_id": "openssl-selfsigned-cert:1",
    "manifest_sha256": "0f28db5e637d925b054739f0f5604d259b8aad07a97c8d00082da49003499471"
  },
  "platform": {
    "content_sha": "dbddb89c3207a45b75625c1e0fed64b17ef2eafb9c37bd5b9f466fd277f7c749",
    "git_sha": "3b8a84b48a98494cebf88a4fbdd4872d52702f68",
    "dirty": true
  },
  "dataset": {
    "argv": [
      "git",
      "-C",
      "/mnt/20t/xubuqiang/datasets/terminal-bench",
      "rev-parse",
      "HEAD"
    ],
    "returncode": 0,
    "stdout": "2fd12b88aafdd04a52c298e3940bcb189f9766d6\n",
    "stderr": ""
  },
  "source_sha256": "54985eac4739288c2fd1d686ae840c16f8fd317bdde0f8fb654e8bcc86df387b",
  "split_sha256": "362537284993db7da273d45c8041331811fad1ad73f17eddc2c8bc8f97895810",
  "harness_files_sha256": "84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2",
  "harness_manifest_path": "/tmp/w-tbrun4-terminal-bench-20261014T195342Z-82530223-work/w-tbrun4-terminal-bench-20261014T195342Z-82530223/workspace/harness.json",
  "harness_manifest_sha256": "50b2cf63dfcbc937e4a47a04c3bda23240771103ab42c2717bfccfb3cb2a3f80",
  "model_weights_sha256": null,
  "scorer_script_sha256": "4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334",
  "note": "Model weights and transitive dependency closure remain unknown; launch manifest is observer-authored and bound before execution."
}
```

The model weight digest remains unknown. The script digest binds the official test script only; transitive online dependencies are not claimed pinned or offline-closed.

[image-observation-receipt.json](w-tbrun4-evidence/launch/image-observation-receipt.json) binds the real cache inspection and launched images. `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/image-inspect.json` records both cache aliases with ID `sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12` and the exact `RepoDigests` retained in that receipt. The task's `run_meta.json` environment and sampled Docker `Image` agree. The verifier's actual snapshot image is:

```json
[
  {
    "source": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/snapshot-inspect-00082.json",
    "source_sha256": "aecbf0cb2687be1b995a9ef98ccb4cb1d83998d31154d0dd816fbcb49a13ea48",
    "id": "sha256:8f13f4ddb7168fc33f56935ce756698cd253b455a9cf20189628031811be21ec",
    "repo_tags": [
      "hg-snapshot:w-tbrun4-terminal-bench-20261014T195342Z-82530223-openssl-selfsigned-cert"
    ],
    "size": 45792970,
    "parent": "sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12"
  }
]
```

## Resource and cleanup receipts, with uncertainty retained

The manifest-bound observer receipts below exist at the original paths and as direct review copies. Each embeds raw-file paths and SHA-256 values; their own hashes are recorded in `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/result.json`:

```json
{
  "resource": {
    "path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/resource-observation-receipt.json",
    "sha256": "5c075543997668d874c5e82f9129d1bd90547d6f6292baa9942dccc761a41f2f"
  },
  "snapshot": {
    "path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/snapshot-observation-receipt.json",
    "sha256": "a997571f4d9985e6ebe861aa2ded93b9cef790cf53fc3801895b46d48306965a"
  },
  "image": {
    "path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/image-observation-receipt.json",
    "sha256": "48c275e2c5fa6ca95794d246a9dc0a5a5a611106052d6d7134ae3ee93ebcdd2a"
  },
  "cleanup": {
    "path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/cleanup-observation-receipt.json",
    "sha256": "c13c851e3666666dc609e75ebed01fd0f6f2fe2cddcac883fb2076dbc49d483f"
  },
  "provenance": {
    "path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/provenance.json",
    "sha256": "2122b79a6a17aae5f2744d74f9928c6f10a14df95f73193fc321c40469f1829c"
  }
}
```

[resource-observation-receipt.json](w-tbrun4-evidence/launch/resource-observation-receipt.json) preserves declared limits `{"budget": null, "resource": {"agent_timeout_s": 900, "cpus": 1, "memory_mb": 2048, "verify_timeout_s": 900}}`, real Docker configuration readouts, and every saved statistics sample path. Compact raw readouts:

```json
{
  "agent": {
    "observation_path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/container-inspect-00000.json",
    "NanoCpus": 1000000000,
    "Memory": 2147483648,
    "MemorySwap": 4294967296,
    "PidsLimit": 1024,
    "ReadonlyRootfs": false,
    "last_sampled_size_rw": 4694016,
    "last_sample_path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/container-inspect-00081.json"
  },
  "verifier": {
    "observation_path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/container-inspect-00081.json",
    "NanoCpus": 1000000000,
    "Memory": 2147483648,
    "MemorySwap": 4294967296,
    "PidsLimit": 1024,
    "ReadonlyRootfs": false,
    "last_sampled_size_rw": 73728,
    "last_sample_path": "/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/container-inspect-00081.json"
  }
}
```

`SizeRw` values are last samples, not peak usage; `NanoCpus`, `Memory`, `MemorySwap` and `PidsLimit` are Docker configurations. No filesystem quota, trusted resource admission or peak-resource attestation is claimed. Budget remains `null` in the saved policy context. The task's harness/progress output and trace are preserved in `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/progress/round-0/`, including the usage-bearing invalid trace.

[snapshot-observation-receipt.json](w-tbrun4-evidence/launch/snapshot-observation-receipt.json) records the real snapshot image above. [cleanup-observation-receipt.json](w-tbrun4-evidence/launch/cleanup-observation-receipt.json) records exact inspected container/snapshot absence and scoped object listings. `containers-after.json`, `networks-after.json`, `snapshot-images-after.json`, plus final container/network/volume listings, each have `returncode=0`, `stdout=""`, `stderr=""`. Exact container probes `container-exact-after-00.json` and `container-exact-after-01.json` return `1`, `stdout="[]\n"`, and `no such object`; `snapshot-exact-after-00.json` returns `1` with `No such image`. The complete raw error strings and IDs are in those files, and Docker destroy events remain in `docker-events.jsonl`.

These observations establish no surviving selected Docker objects were found by those probes. They do not attest atomic lease release. Driver `cleanup.status="unknown"`, `snapshot.status="unknown"`, their `receipt_sha256=null`, and `lifecycle=null` are retained unchanged. `docs/enforcement-proof-decision.md` accepts uncertainty alone as a standing limit; it does not repair the missing verifier report or score. No admission receipt was synthesized to claim success.

Original task artifacts remain intact under the runs root. [artifact-inventory.json](w-tbrun4-evidence/artifact-inventory.json) inventories every original task/launch file by path, byte count and digest; [run-artifacts.tar.gz](w-tbrun4-evidence/run-artifacts.tar.gz) is the complete byte-for-byte review archive, with its identity in [archive-sha256.json](w-tbrun4-evidence/archive-sha256.json). [network-control-inventory.json](w-tbrun4-evidence/network-control-inventory.json) separately inventories the control. Raw sample review copies are compacted into the archive; their original runs-root files are untouched. All historical attempts and archives remain untouched.

## Disposition, comment fix and validation

`terminal_bench / cached-runtime-admission` remains open. The registry observation is updated to the actual proxy-configured attempt and the precise network defect. The missing artifact is `/logs/verifier/ctrf.json`, so no valid score exists. A real manifest is now bound and image/resource/snapshot/cleanup observation receipts exist; absence of an infallibility proof is not introduced as a new blocker. Shared `scorer-offline-closure` and `artifact-only-state-export` remain attached. No pilot expansion or production authorization follows.

The only production-file diff is the requested comment at `eval/verification/verifier.py:89-91`: canonical port `17890`, with a citation to `docs/egress.md`. Executable behavior, harnesses, adapter, network implementation and scorer are unchanged. No existing test specifically pins this Terminal-Bench registry entry or its current observation; its status remains open, so no pinned test changes are required.

[reports/w-tbrun4-validation.txt](w-tbrun4-validation.txt) preserves exact checker and focused test commands and complete outputs. The initial checker returned `valid=true`, `datasets=28`, `shared_blockers=2`, `historical_records=11`, `production_authorized=false`, exit code `0`. The focused registry, diagnostic authorization/policy, split, verifier, container-state and terminal-artifact suites returned `255 passed in 26.97s`, exit code `0`. Post-edit checker/registry validation and archive integrity results are appended there before commit. Pytest temporary roots are outside the platform. The unique journal entry ends in ` - w-tbrun4`. Changes are committed only in this registered isolated worktree; no main commit or merge is performed.
