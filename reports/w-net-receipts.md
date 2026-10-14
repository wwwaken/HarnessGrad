# w-net: verifier declared-network parity and real scorer execution

**CLOSED: `terminal_bench / cached-runtime-admission`. The official verifier produced raw reward `0.0` and `/logs/verifier/ctrf.json`; the agent ran against the local endpoint.** This is a real task failure, not the previous missing-report nonmeasurement. The diagnostic publication receipt still withholds its score (`score=null`, `policy_enforcement_not_observed`); no comparable diagnostic result, pilot expansion or production authorization is claimed. Shared `scorer-offline-closure` and `artifact-only-state-export` remain open.

## Change and regression evidence

`eval/containers/container_state.py:218` now passes the task's declared network separately from the owned internal network. `eval/verification/verifier.py:294-299` retains that internal network and attaches the verifier to bridge before start only when the declaration is bridge; it avoids duplicate attachment when bridge is already primary. The comment cites the actor's identical rule at `eval/containers/container_state.py:111-112` and the adapter contract at `data/datasets/terminal_bench.py:35`. No gate, descriptor, scorer, task, model configuration, or admission requirement was weakened.

`tests/quality/test_verifier_declared_network_w_net.py` exercises the production actor-to-verifier path with Docker/model transports stubbed: bridge, none and missing declarations, internal-network retention, attachment before start and owned teardown. Before the fix, the bridge case failed while the other cases passed: `/tmp/hg-net/reports/w-net-evidence/regression-before.txt`. The new tests and affected verifier/admission suites passed: `/tmp/hg-net/reports/w-net-evidence/focused-tests.txt`. Complete commands/results are in `/tmp/hg-net/reports/w-net-validation.txt`.

## Commands, including refusals and the preserved failure

Read first: `/tmp/hg-tbrun4/reports/w-tbrun4-receipts.md`, its saved launch script/policy/task/network-control evidence, and its execution trace/progress. The established internal-network control was not rerun. Historical command from `/tmp/hg-tbrun4/reports/w-tbrun4-evidence/launch/command.txt`:

```sh
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=openssl-selfsigned-cert HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence /tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223-launch-evidence/policy-input.json --authorize-unobserved-diagnostic 'Operator explicitly requests one real cached openssl-selfsigned-cert diagnostic with HG_TB_SPLIT=none and the documented verifier egress proxy to obtain CTRF and a raw verifier score; runtime observations remain incomplete, with no comparable score publication, pilot expansion or production authorization.' --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id w-tbrun4-terminal-bench-20261014T195342Z-82530223 --runs-root /tmp/hg-tbrun4/runs --work-root /tmp/w-tbrun4-terminal-bench-20261014T195342Z-82530223-work
```

Its frozen diagnostic receipt remains invalid with `score=null` and no CTRF, at `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/diagnostic_receipt.json`. No historical run, receipt or archive was modified.

The requested literal recipe is not admitted by current source. Its exact fresh command and observed refusal are saved at `/tmp/hg-net/reports/w-net-evidence/requested-recipe-refusal.json`:

```sh
env HG_TB_TASKS=openssl-selfsigned-cert HG_TB_SPLIT=none HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop_plain --dataset terminal_bench --side eval --sampling diagnostic --rounds 0 --trials 1 --jobs 1 --authorize-unobserved-diagnostic 'Operator requests one cached task diagnostic after verifier network repair; gates remain unknown and no publication or production authorization is claimed.' --run-id w-net-requested-20261014T200809Z-4c6ade73 --runs-root /tmp/hg-net/runs --work-root /tmp/w-net-requested-20261014T200809Z-4c6ade73-work
```

```json
{
  "returncode": 2,
  "stdout": "",
  "stderr": "refusing unobserved diagnostic: explicit operator reason, diagnostic sampling, train side and no method entrypoint are required\n",
  "run_exists": false,
  "work_exists": false
}
```

`driver.py:390-396` requires train for this authorization; `:402-413` requires truthful policy evidence. Independently, `base_harness/loop_plain/harness.json:1-8` lacks exec capability, and `harnessgrad/environments.py:185-195` refuses it. The preserved successful preflight recipe already used existing `loop` on train with policy evidence. Those interfaces were used for the single real execution, with unknown gates left unknown and no improvement rounds. The train CLI flag does not claim an official train split: `HG_TB_SPLIT=none` means `split=null`.

Actual new command, byte-for-byte from `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/command.txt` (review copy `/tmp/hg-net/reports/w-net-evidence/launch/command.txt`):

```sh
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=openssl-selfsigned-cert HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence /tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/policy-input.json --authorize-unobserved-diagnostic 'Operator authorizes one cached openssl-selfsigned-cert diagnostic after the verifier declared-network repair, with HG_TB_SPLIT=none and the documented proxy; existing loop/train CLI is required by unchanged guards. Dataset enforcement observations remain unknown; this requests raw CTRF/scorer evidence only, with no comparable score publication, pilot expansion, or production authorization.' --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id w-net-terminal-bench-20261014T200818Z-fd0c4d1e --runs-root /tmp/hg-net/runs --work-root /tmp/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-work
```

Run root: `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e`.
External work root: `/tmp/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-work`.
Launch evidence root: `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence`.
All identities were fresh and checked absent before execution. No old ID was resumed, no existing run was overwritten, no model completion probe was sent, and no image was pulled.

`launch-input.json` records the exact task/model/proxy environment. `endpoint-probe.json` and `endpoint-models.json` preserve the responding local model list. `proxy-astral.json` and `proxy-pypi.json` preserve host curl observations; actual verifier success, rather than host probes, establishes that this task's bootstrap ran. `active-drivers-preflight.json` and `containers-preflight.json` under `/tmp/hg-net/reports/w-net-evidence/`, plus `h0-processes-preflight.json` in the launch root, preserve concurrency observations. Only this one task/trial/job was launched.

## Raw scorer result and artifact

Official `/logs/verifier/ctrf.json` review copy: `/tmp/hg-net/reports/w-net-evidence/ctrf.json`.
Original captured bind-file copy: `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/verifier-ctrf.json-67dbb020f78873084b681fa47cbe1f6e5c96f887ae80fab729aa91bb385e88ef`.
The source bind-mount path, observation time, container ID, byte count and digest are preserved in `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/verifier-file-observations.json`. `/tmp/hg-net/reports/w-net-evidence/artifact-copy-provenance.json` binds the short review copies to those originals. The temporary verifier bind directory was removed by normal teardown; its observed bytes survive in both locations above and the archive.

Raw values from `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/result.json`, `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e/diagnostic_execution.json`, and the CTRF file:

```json
{
  "verifier_verdict": {
    "kind": "command",
    "passed": false,
    "score": 0.0,
    "tests": {
      "tests": 6,
      "passed": 5,
      "failed": 1,
      "skipped": 0,
      "pending": 0,
      "other": 0,
      "failed_names": [
        "test_outputs.py::test_python_verification_script"
      ]
    },
    "scorer_isolation_class": "snapshot-service",
    "scorer_isolation_declared": "snapshot-service"
  },
  "raw_per_task": {
    "openssl-selfsigned-cert": 0.0
  },
  "invalid": {},
  "reward_bytes": [
    "0\n"
  ],
  "ctrf_files": [
    {
      "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/verifier-ctrf.json-67dbb020f78873084b681fa47cbe1f6e5c96f887ae80fab729aa91bb385e88ef",
      "sha256": "67dbb020f78873084b681fa47cbe1f6e5c96f887ae80fab729aa91bb385e88ef",
      "summary": {
        "tests": 6,
        "passed": 5,
        "failed": 1,
        "skipped": 0,
        "pending": 0,
        "other": 0,
        "start": 1792008655.9319706,
        "stop": 1792008656.216884
      }
    }
  ]
}
```

The failed official test is `test_outputs.py::test_python_verification_script`. The agent-created `/app/check_cert.py` raises `IndexError: list index out of range` while selecting a certificate-expiry line; the full task traceback and bounded verifier stdout/stderr survive in the raw verdict's `detail` and the CTRF test message. The official command was `bash /tests/test.sh`, preserved in `selected-verifier-test.sh`, the Docker exec events and the verdict detail. It successfully bootstrapped uv/pytest and tested the agent's artifact. No solution, reference script or task test was changed or staged by this worker.

## Publication coverage is still withheld

The scorer above ran and its raw reward is valid. The staged-policy receipt is deliberately stricter: unknown enforcement observations withhold score publication (`eval/policy/diagnostic_policy.py:181-186`). Driver exit is not scorer failure here. Raw fields from `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e/diagnostic_receipt.json` and `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/launch-observation.json`:

```json
{
  "driver_returncode": 2,
  "coverage": {
    "eligible_tasks": 1,
    "expected_trials": 1,
    "invalid_tasks": 0,
    "invalid_trials": 0,
    "measured_tasks": 0,
    "measured_trials": 0,
    "selected_tasks": 1,
    "unmeasured_tasks": 1,
    "unmeasured_trials": 1
  },
  "score": null,
  "outcomes": [
    {
      "reason": "policy_enforcement_not_observed",
      "score": null,
      "status": "unmeasured",
      "task_id": "openssl-selfsigned-cert",
      "trial": 1
    }
  ],
  "enforcement": {
    "comparable": false,
    "measured": false,
    "non_comparable_reason": "policy_enforcement_not_observed",
    "operator_authorization": "Operator authorizes one cached openssl-selfsigned-cert diagnostic after the verifier declared-network repair, with HG_TB_SPLIT=none and the documented proxy; existing loop/train CLI is required by unchanged guards. Dataset enforcement observations remain unknown; this requests raw CTRF/scorer evidence only, with no comparable score publication, pilot expansion, or production authorization.",
    "policy_enforcement_observed": false,
    "production_authorized": false,
    "run_id": "w-net-terminal-bench-20261014T200818Z-fd0c4d1e",
    "stage": "diagnostic",
    "task_id": "openssl-selfsigned-cert"
  },
  "curve_present": false
}
```

`selection.json` records the eligible adapter selection and `split=null`; `staged_plan.json` records the selected task. Raw execution contains the scorer verdict for that task; publication coverage marks it unmeasured solely because policy observations remain unknown. No null publication score is presented as a measured zero. No pilot is expanded.

## Network, identity, resource and cleanup receipts

Manifest-bound receipt identities (each original path has an identical review copy under `/tmp/hg-net/reports/w-net-evidence/launch/`):

```json
{
  "resource": {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/resource-observation-receipt.json",
    "sha256": "727d001ba36ac1996e74ba6768381162f143e6fcb7ddadfca961ec9f37e90f58"
  },
  "snapshot": {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/snapshot-observation-receipt.json",
    "sha256": "5b5be155b64846f94c2c22da165bc8f24edf459ed2534bd703ad3774da1fd03b"
  },
  "image": {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/image-observation-receipt.json",
    "sha256": "20ec12c181cf9fea20b4678082ce8df51dbd7e46b2561c29c79f7b631d57ba47"
  },
  "cleanup": {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/cleanup-observation-receipt.json",
    "sha256": "f401ee1d730f4f1b3dd92be6f835d0e00b3f7404a192f4cd50cc7fbb4fa6f3d1"
  },
  "provenance": {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/provenance.json",
    "sha256": "39ab730f99a20b0d5f021c9bab9bee3f5f2179ca836e9e3bd34ae8d2e67f08d4"
  }
}
```

The shared binding is:

```json
{
  "adapter_id": "terminal_bench",
  "run_id": "w-net-terminal-bench-20261014T200818Z-fd0c4d1e",
  "trial_id": "openssl-selfsigned-cert:1",
  "manifest_sha256": "27e0890e47bd3e1385e96590fe7d38f760bca5461e560230cb8dcecaf3ed5366"
}
```

`resource-observation-receipt.json` carries raw inspected actor/verifier networks and limits, plus every Docker statistics sample path/digest. Compact values, with their raw inspection paths:

```json
{
  "declared": {
    "budget": null,
    "resource": {
      "agent_timeout_s": 900,
      "cpus": 1,
      "memory_mb": 2048,
      "verify_timeout_s": 900
    }
  },
  "roles": {
    "agent": {
      "inspection_path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/container-inspect-00000.json",
      "networks": [
        "bridge",
        "hg-w-net-terminal-bench-20261014T200818Z-fd0c4d1e-openssl-selfsigned-cert"
      ],
      "limits": {
        "NanoCpus": 1000000000,
        "Memory": 2147483648,
        "MemorySwap": 4294967296,
        "PidsLimit": 1024,
        "ReadonlyRootfs": false
      },
      "last_sample_size_rw": 4677632,
      "last_sample_path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/container-inspect-00072.json"
    },
    "verifier": {
      "inspection_path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/container-inspect-00064.json",
      "networks": [
        "bridge",
        "hg-w-net-terminal-bench-20261014T200818Z-fd0c4d1e-openssl-selfsigned-cert"
      ],
      "limits": {
        "NanoCpus": 1000000000,
        "Memory": 2147483648,
        "MemorySwap": 4294967296,
        "PidsLimit": 1024,
        "ReadonlyRootfs": false
      },
      "last_sample_size_rw": 90087424,
      "last_sample_path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/container-inspect-00071.json"
    }
  }
}
```

Both roles retain the owned internal network plus bridge. SizeRw is a last sample, not peak usage; Docker limits are configuration observations. Budget and model-weight digest remain unknown/null. No resource-enforcement proof or admission attestation is invented.

`image-observation-receipt.json` preserves cached image IDs/RepoDigests and observed launched images. `snapshot-observation-receipt.json` preserves this actual committed snapshot:

```json
[
  {
    "source": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/snapshot-inspect-00072.json",
    "source_sha256": "1653176b5c88cca0eca27d1be9b86b54a7475cfb596253e93b593d8c47ac082d",
    "id": "sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779",
    "repo_tags": [
      "hg-snapshot:w-net-terminal-bench-20261014T200818Z-fd0c4d1e-openssl-selfsigned-cert"
    ],
    "size": 45791844,
    "parent": "sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12"
  }
]
```

`provenance.json` preserves platform source content/git hashes, dataset revision, source/split/harness hashes and the official scorer-script hash:

```json
{
  "binding": {
    "adapter_id": "terminal_bench",
    "run_id": "w-net-terminal-bench-20261014T200818Z-fd0c4d1e",
    "trial_id": "openssl-selfsigned-cert:1",
    "manifest_sha256": "27e0890e47bd3e1385e96590fe7d38f760bca5461e560230cb8dcecaf3ed5366"
  },
  "platform": {
    "content_sha": "5154b973e19e7caf67afddb8855dd38e19eb66591799d00bdaa28b74b7a765a6",
    "git_sha": "919e2b9bf82f4040e87e098fd37cab27d2d4d4d8",
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
  "harness_manifest_path": "/tmp/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-work/w-net-terminal-bench-20261014T200818Z-fd0c4d1e/workspace/harness.json",
  "harness_manifest_sha256": "50b2cf63dfcbc937e4a47a04c3bda23240771103ab42c2717bfccfb3cb2a3f80",
  "model_weights_sha256": null,
  "scorer_script_sha256": "4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334",
  "note": "Model weights and transitive dependency closure remain unknown; launch manifest is observer-authored and bound before execution."
}
```

The exact context hashes from the diagnostic receipt, including the unknown model digest:

```json
{
  "harness": "84664d6cd2efc596b01dd915e39417f656d92fe01d2c6eb666332d5477a545f2",
  "manifest": "27e0890e47bd3e1385e96590fe7d38f760bca5461e560230cb8dcecaf3ed5366",
  "model": null,
  "source": "54985eac4739288c2fd1d686ae840c16f8fd317bdde0f8fb654e8bcc86df387b",
  "split": "362537284993db7da273d45c8041331811fad1ad73f17eddc2c8bc8f97895810"
}
```

`launch-manifest.json` is observer-authored before execution, not a production admission attestation; its digest matches the diagnostic context. `platform-diff.json` and `platform-source-files.json` bind the uncommitted network patch used for execution. The scorer hash binds the official script, not its transitive online dependencies.

`cleanup-observation-receipt.json` records scoped listings and exact probes for the observed containers/snapshot, with raw return codes and streams. Raw scoped post-run listings:

```json
{
  "containers-after.json": {
    "argv": [
      "docker",
      "ps",
      "-a",
      "--no-trunc",
      "--filter",
      "label=harnessgrad.run=w-net-terminal-bench-20261014T200818Z-fd0c4d1e",
      "--format",
      "{{json .}}"
    ],
    "returncode": 0,
    "stdout": "",
    "stderr": ""
  },
  "networks-after.json": {
    "argv": [
      "docker",
      "network",
      "ls",
      "--no-trunc",
      "--filter",
      "label=harnessgrad.run=w-net-terminal-bench-20261014T200818Z-fd0c4d1e",
      "--format",
      "{{json .}}"
    ],
    "returncode": 0,
    "stdout": "",
    "stderr": ""
  },
  "snapshot-images-after.json": {
    "argv": [
      "docker",
      "image",
      "ls",
      "--no-trunc",
      "--filter",
      "reference=hg-snapshot:*w-net-terminal-bench-20261014T200818Z-fd0c4d1e*",
      "--format",
      "{{json .}}"
    ],
    "returncode": 0,
    "stdout": "",
    "stderr": ""
  }
}
```

Exact post-run probes (full IDs and raw errors remain in the receipt files):

```json
[
  {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/container-exact-after-00.json",
    "argv": [
      "docker",
      "inspect",
      "33b07aa5952a86161ef9d329a92a6e61026ae1df30c5abb5ab01ff6816fe58a3"
    ],
    "returncode": 1,
    "stdout": "[]\n",
    "stderr": "error: no such object: 33b07aa5952a86161ef9d329a92a6e61026ae1df30c5abb5ab01ff6816fe58a3\n"
  },
  {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/container-exact-after-01.json",
    "argv": [
      "docker",
      "inspect",
      "65a5383c36f88ae502ebee61c87906c10f4fdf9b2cd78c9b9afd267d43eb7cf3"
    ],
    "returncode": 1,
    "stdout": "[]\n",
    "stderr": "error: no such object: 65a5383c36f88ae502ebee61c87906c10f4fdf9b2cd78c9b9afd267d43eb7cf3\n"
  },
  {
    "path": "/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e-launch-evidence/snapshot-exact-after-00.json",
    "argv": [
      "docker",
      "image",
      "inspect",
      "sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779"
    ],
    "returncode": 1,
    "stdout": "[]\n",
    "stderr": "Error response from daemon: No such image: sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779\n"
  }
]
```

The observed owned Docker objects are absent by these probes. Atomic lease release is not attested. The driver's unchanged lifecycle fields are:

```json
{
  "snapshot": {
    "detail": "driver has no verified lifecycle receipt; trusted orchestration must attest",
    "receipt_sha256": null,
    "status": "unknown"
  },
  "cleanup": {
    "detail": "driver has no verified lifecycle receipt; trusted orchestration must attest",
    "receipt_sha256": null,
    "status": "unknown"
  },
  "lifecycle": null
}
```

This preserves the accepted uncertainty in `docs/enforcement-proof-decision.md`; uncertainty alone is not reintroduced as an extra closure requirement.

## Agent execution: zero environment calls is expected, not a second wiring defect

**The agent was invoked in both the old and new diagnostics.** `env_usage.calls=0` measures environment-service model spend, not agent spend. Source: `eval/service/services.py:177-203`, `INTERFACE.md:834-840`, `eval/containers/container_state.py:220-223` (`env_usage={}`), and the separate aggregation at `eval/run/runner.py:1259-1266`. Real agent completions are made at `base_harness/loop/agent.py:240-245`, counted at `:269-273` and written to the final trace usage at `:745`.

The historical saved invalid trace at `/tmp/hg-tbrun4/reports/w-tbrun4-evidence/execution/progress/round-0/traces/openssl-selfsigned-cert.invalid.jsonl` records `calls=32`, `input_tokens=179300`, `output_tokens=10999`; its progress record's gateway reports `connections=32`, target `127.0.0.1:8002`. The old aggregate dropped invalid traces (`eval/run/runner.py:1121-1127,1179-1181,1299-1310`), obscuring agent spend there. This is an accounting limitation; it is not an uninvoked agent. Detailed raw historical findings: `/tmp/hg-net/reports/w-net-calls-audit.md`. No accounting change was made.

New raw accounting from `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e/diagnostic_execution.json`, independently indexed at `/tmp/hg-net/reports/w-net-evidence/agent-model-account.json`:

```json
{
  "tokens": {
    "input": 163009,
    "output": 8527,
    "calls": 32,
    "tasks_reported": 1
  },
  "env_usage": {
    "input": 0,
    "output": 0,
    "calls": 0,
    "services_reported": 0
  },
  "model_gateway": {
    "published": true,
    "target": "127.0.0.1:8002",
    "connections": 32,
    "upstream_connect_failed": 0,
    "upstream_connect_error": null,
    "upstream_closed_first": 32,
    "client_closed_first": 0,
    "bytes_to_upstream": 629024,
    "bytes_to_client": 57957,
    "read_errors": []
  },
  "harness_output": {
    "openssl-selfsigned-cert": {
      "exit_code": 0,
      "stderr": ""
    }
  },
  "harness_failed": {}
}
```

The usage-bearing new trace is `/tmp/hg-net/runs/w-net-terminal-bench-20261014T200818Z-fd0c4d1e/progress/round-0/traces/openssl-selfsigned-cert.trial1.jsonl`. No standalone completion probe contributes to those counts. The observer's `agent-execution-observation.json` has `harness_output=null` because valid progress JSON omits that key; the complete aggregate above supplies the actual gateway and output fields.

## Preservation, validation and disposition

`/tmp/hg-net/reports/w-net-evidence/artifact-inventory.json` lists every original run/launch file with absolute path, byte count and SHA-256; `/tmp/hg-net/reports/w-net-evidence/run-artifacts.tar.gz` preserves them byte-for-byte, and `archive-sha256.json` records the archive identity. Direct review copies retain the execution/launch layout; raw repeated Docker samples remain in the archive and untouched original runs root. The fresh literal-recipe refusal is preserved separately. All earlier receipts and archives remain untouched.

`/tmp/hg-net/reports/w-net-validation.txt` contains full checker and test outputs. The affected focused suites passed; the additional boundary suites exposed a pre-existing Jericho monkeypatch signature failure, reproduced at the original commit in a registered temporary worktree. That baseline worktree was removed after inspection. The unrelated test stub was not changed. No existing registry test pins this Terminal-Bench entry, so none needed a status update.

The dataset-specific blocker is removed from `docs/dataset-blockers.json` because the requested real cached-task scorer and manifest/image/resource/snapshot/cleanup observations now exist. `docs/terminal-bench-runtime-admission.md` appends this disposition to its historical source review; the journal appends a unique heading ending in ` - w-net`. Shared scorer/export gates, unknown policy enforcement and lack of comparable publication remain explicit. Commit only in `/tmp/hg-net` on its isolated branch; no main commit or merge.
