# w-chess: released-task live stepwise receipt

## Released-task stepwise diagnostic — incomplete

**OPEN: `chessbench_puzzles / trusted-stepwise-transport`.** A real model-driven actor connected to the live controller and received its initial public board, but closed the connection without a move. The controller recorded `answer_receive_failed`, `measured=false`, and no score/reward. A delivered terminal exchange and puzzle measurement are still missing. The offline-only measurement claim remains; no protocol comparison or curve point was produced. `interruption-closure` and historical runs are untouched.

The receipt really records `scorer_isolation_class: "in-process"`, matching the w-obs fix. It describes the trusted platform controller; the actor ran separately in the native files sandbox. This confirms the recorded class, not a completed scorer measurement.

Exact executed shell command (cwd `/tmp/hg-chess`), transcribed in `reports/w-chess-evidence/invocation.txt`:

```sh
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 reports/w-chess-evidence/launch.py --sampling diagnostic --rounds 0 --trials 1 --jobs 1 --authorize-unobserved-diagnostic 'Operator explicitly authorizes one gated released ChessBench task through the live stepwise relay using the existing loop harness and local endpoint to obtain controller execution evidence. Dataset enforcement and shared scorer/export gates remain unknown; raw receipts only, no comparable score publication, strict-replay comparison, method tuning, expansion or production authorization.'
```

`execution/launch/command.txt` below preserves the command's equivalent absolute script-path reconstruction. The ordinary driver has no interaction-selection CLI flag. The observer script follows the trusted-caller interface documented in `docs/chessbench-puzzles-evaluation.md`: it sets only the public task's `interaction`, passes the adapter's selected setup/verifier to the public `eval.run.runner.run_one`, and uses the existing `diagnostic_policy` selection/receipt APIs and scoped `Authorization`. The harness, policy checks, refusal logic, scorer and production code were not patched. The caller permits only diagnostic sampling at the required staged shape; it uses train-side metadata, no method entrypoint, and preserves unknown gates as unknown. It checks the pinned CSV and sandbox before launch. This is execution permission, not evidence of enforcement.

Run/work paths, verbatim from `reports/w-chess-evidence/execution/identity.json` (original `/tmp/hg-chess/runs/w-chess-stepwise-20261014T202226Z-11489149/identity.json`):

```json
{
  "run_id": "w-chess-stepwise-20261014T202226Z-11489149",
  "run_dir": "/tmp/hg-chess/runs/w-chess-stepwise-20261014T202226Z-11489149",
  "work_root": "/tmp/w-chess-stepwise-20261014T202226Z-11489149-work",
  "workspace": "/tmp/w-chess-stepwise-20261014T202226Z-11489149-work/w-chess-stepwise-20261014T202226Z-11489149/workspace",
  "caller": "eval.run.runner.run_one",
  "side": "train",
  "harness": "loop"
}
```

Selection from `reports/w-chess-evidence/execution/launch/selection.json`:

```json
{
  "pool_tasks": 10000,
  "eligible_tasks": 6615,
  "eligible_task_ids_sha256": "190383f45c4510dc6f1d790b7c11467904004e61c1eef177c4b23d68ddf92ef8",
  "selected_task_ids": [
    "chessbench_puzzles/test/1287"
  ],
  "split_rule": "data.scaffolds.qa.base.is_eval: sha256(task_id)[0] % 3 == 0",
  "split_source": "hash",
  "official_payload_split": "test",
  "split_sha256": "26781ee746b22e62e743d7c530778c0e3615027ec75f55ed337634267ff0b25f"
}
```

Only selected puzzles were decoded through the adapter's selected reader. The caller counted CSV rows for the ID pool without deriving unselected boards or gold. The CLI-equivalent side is the platform's hash-train side within the released `test` CSV; this is not an official study split or a generalization result. There was no second diagnostic, resume, improvement, offline replay evaluation, or expansion.

Raw verdict from `reports/w-chess-evidence/execution/task-result.json`, field `verdict` (unchanged copy of `/tmp/hg-chess/runs/w-chess-stepwise-20261014T202226Z-11489149/task-result.json`):

```json
{
  "kind": "stepwise",
  "protocol": "chessbench_puzzles.stepwise.v1",
  "evidence": {
    "schema": "harnessgrad.unix-stepwise-relay.v1",
    "protocol": "chessbench_puzzles.stepwise.v1",
    "status": "incomplete",
    "measured": false,
    "production_authorized": false,
    "limits": {
      "timeout_s": 300,
      "max_connections": 1,
      "max_submissions": 256,
      "max_message_bytes": 4096
    },
    "connections": 1,
    "rejections": [
      "connection_budget"
    ],
    "rejected_connections": 20,
    "transport": {
      "schema": "harnessgrad.public-stepwise-transport.v1",
      "contract": "chessbench_puzzles.stepwise.v1",
      "status": "incomplete",
      "measured": false,
      "production_authorized": false,
      "submissions": 0,
      "limits": {
        "max_submissions": 256,
        "max_message_bytes": 4096
      },
      "events": [
        {
          "kind": "observation",
          "message": "{\"contract\":\"chessbench_puzzles.stepwise.v1\",\"fen\":\"5rk1/1R3p1p/p5p1/5n2/PPQ1p3/4P3/3q1PPP/2R3K1 b - - 2 29\",\"solver_turn\":0,\"status\":\"awaiting_move\",\"verdict\":\"awaiting_move\"}"
        }
      ],
      "reason": "answer_receive_failed"
    },
    "cleanup": {
      "server_closed": true,
      "thread_joined": true,
      "socket_removed": true
    },
    "comparability": "Interactive and offline ChessBench protocols are not comparable.",
    "reason": "answer_receive_failed"
  },
  "scorer_isolation_class": "in-process",
  "unmeasured": "answer_receive_failed",
  "detail": "answer_receive_failed"
}
```

The only controller event is the initial `awaiting_move` observation. The actor trace's shell step that first connected printed that same board and then exited without sending an answer. Later reconnects were rejected. `eval/service/unix_stepwise_relay.py:55-58` enforces the single-connection allowance; EOF is rejected at `:92-93`; `eval/service/stepwise_transport.py:142-145` records `answer_receive_failed`. `eval/run/chess_stepwise.py:58-70` returns an unmeasured verdict rather than a reward. There is no launch-policy refusal or identified production defect here: the existing actor did not maintain the required connection. No gate or allowance was weakened to accommodate it.

The trace's local harness `submitted: true` completion flag is not a relay submission: controller `transport.submissions` above is authoritative. An actor artifact does not score this branch.

Policy outcome and coverage, raw from `reports/w-chess-evidence/execution/diagnostic_receipt.json`:

```json
{
  "stage": "diagnostic",
  "trials": 1,
  "jobs": 1,
  "score": null,
  "outcomes": [
    {
      "reason": "answer_receive_failed",
      "score": null,
      "status": "unmeasured",
      "task_id": "chessbench_puzzles/test/1287",
      "trial": 1
    }
  ],
  "coverage": {
    "eligible_tasks": 6615,
    "expected_trials": 1,
    "invalid_tasks": 0,
    "invalid_trials": 0,
    "measured_tasks": 0,
    "measured_trials": 0,
    "selected_tasks": 1,
    "unmeasured_tasks": 1,
    "unmeasured_trials": 1
  },
  "enforcement": {
    "comparable": false,
    "measured": false,
    "non_comparable_reason": "policy_enforcement_not_observed",
    "operator_authorization": "Operator explicitly authorizes one gated released ChessBench task through the live stepwise relay using the existing loop harness and local endpoint to obtain controller execution evidence. Dataset enforcement and shared scorer/export gates remain unknown; raw receipts only, no comparable score publication, strict-replay comparison, method tuning, expansion or production authorization.",
    "policy_enforcement_observed": false,
    "production_authorized": false,
    "run_id": "w-chess-stepwise-20261014T202226Z-11489149",
    "stage": "diagnostic",
    "task_id": "chessbench_puzzles/test/1287"
  }
}
```

No zero was assigned to this incomplete task. Even a completed raw controller score under this authorization could not become a comparable diagnostic publication. The policy's lifecycle facts below remain unknown rather than being inferred from socket cleanup.

Endpoint, metric, provenance, limits and cleanup

- `reports/w-chess-evidence/preflight.json` and `execution/launch/endpoint.json`: endpoint answered with HTTP `200` and advertised `qwen3.5-9b-local`. The selected endpoint binding is in `execution/launch/manifest.json` and `diagnostic_receipt.json.context.endpoint`; the actor's backend/model identity and usage are in `task-result.json.identity` and its embedded trace. Native files execution uses the direct model route (`model_gateway=null`); no container gateway or independent packet/accounting observation is claimed.
- `execution/task-result.json.runtime_boundary` records the effective phase deadlines and inherited native network below. `verifier_timeout_s` is recorded but a command verifier was not executed for this in-process branch. Relay limits are the raw receipt limits above. No CPU/memory quota or monetary/token spend ceiling is attested; the policy budget and model-weight digest remain null. The existing harness configuration below is unchanged.

Raw `task-result.json` fields:

```json
{
  "exit_code": 0,
  "stderr": "",
  "identity": {
    "harness": "loop",
    "config": {
      "max_steps": 32,
      "submit_retries": 2,
      "parse_retries": 2,
      "finish_nudge_steps": 4,
      "repeat_nudge_limit": 2,
      "output_limit": 4000,
      "context_chars": 60000,
      "shell": "/usr/bin/bash",
      "shell_dialect": "Bash",
      "max_output_tokens": 2048
    },
    "agent_model": "qwen3.5-9b-local",
    "agent_backend": "openai"
  },
  "runtime_boundary": {
    "agent_timeout_s": 300,
    "verifier_timeout_s": 3600,
    "agent_network": "inherited",
    "agent_package_projected": false,
    "verifier_package": "trusted"
  },
  "model_gateway": null,
  "env_usage": {}
}
```

Raw usage from the final `usage` object in `task-result.json.trace`:

```json
{
  "calls": 29,
  "input_tokens": 189356,
  "output_tokens": 16193,
  "retries": 1,
  "context_trims": 1
}
```

Raw `diagnostic_receipt.json.context` provenance/limits (scorer hash binds the adapter file, not transitive dependencies):

```json
{
  "metric": {
    "name": "ChessBench puzzle accuracy",
    "scorer_sha256": "61165a5351b9068ebdac5e66f34cba1b6ed3c658ee1198ebdaf789be4e11b261"
  },
  "hashes": {
    "harness": "c5cef402f8e5d6250d4b3ed1959713c6594af18f4f6706ad83f152ef3b9c0579",
    "manifest": "f515282865b2efda8c8f7a38dd0bf195a196db90106aeff6f9dda69e89570206",
    "model": null,
    "source": "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48",
    "split": "26781ee746b22e62e743d7c530778c0e3615027ec75f55ed337634267ff0b25f"
  },
  "endpoint": "http://127.0.0.1:8002/v1",
  "limits": {
    "budget": null,
    "resource": {
      "agent_timeout_s": 300,
      "verifier_timeout_s": 3600
    }
  },
  "gates": {
    "detail": "Explicit operator authorization for one diagnostic; shared scorer/export gates and backend observations remain unresolved.",
    "receipt_sha256": null,
    "status": "unknown"
  },
  "comparability_notes": [
    "Only chessbench_puzzles.stepwise.v1; no offline strict-replay evaluation or mixed point.",
    "Hash-train side selected before payload decoding; released CSV test slice has no official study split. No method tuning or improvement.",
    "Raw controller measurement is distinct from policy publication. Unknown model-weight digest, transitive dependency closure, CPU/memory enforcement and spend budget; no comparison, expansion or production authorization."
  ]
}
```

Pre-execution manifest binding is verified by `reports/w-chess-evidence/integrity-audit.json`. `execution/launch/source.json` records CSV path/pin, upstream revision and adapter hash; `execution/launch/harness-files.json` records the staged file hashes; `execution/launch/platform-before.json` records the protected platform file hashes. `execution/launch/platform-diff.json` records empty `added`, `removed`, and `modified` lists. `execution/launch/harness-after.json` records the retained harness state. The source and manifest files predate the task run.

Cleanup: the controller receipt above records `server_closed=true`, `thread_joined=true`, `socket_removed=true`. Independent post-run path observations from `reports/w-chess-evidence/cleanup-observation.json`:

```json
{
  "observed_at": "2026-10-14T20:27:51.556295+00:00",
  "attribution": "Task path matched selected task.json; socket path also appears in actor trace. No paths removed by observer.",
  "paths": [
    {
      "path": "/tmp/hg-task-gazazzq3",
      "exists": false
    },
    {
      "path": "/tmp/hg-stepwise-74i44xz0",
      "exists": false
    }
  ],
  "workspace_retained_for_evidence": "/tmp/w-chess-stepwise-20261014T202226Z-11489149-work/w-chess-stepwise-20261014T202226Z-11489149/workspace"
}
```

The observer did not remove those paths. The external harness workspace remains as evidence. There was no container/snapshot execution. Raw policy lifecycle/admission fields from `execution/diagnostic_receipt.json`:

```json
{
  "cleanup": {
    "detail": "No verified lifecycle admission receipt; not attested by this observer.",
    "receipt_sha256": null,
    "status": "unknown"
  },
  "snapshot": {
    "detail": "No verified lifecycle admission receipt; not attested by this observer.",
    "receipt_sha256": null,
    "status": "unknown"
  },
  "lifecycle": null
}
```

The caller's source is `reports/w-chess-evidence/launch.py`, also copied before execution to `execution/launch/launch.py`. `artifact-inventory.json` binds every original run file to its review copy with path, byte count and SHA-256. `run-artifacts.tar.gz` preserves the original run tree; `archive-sha256.json` records its identity, and `integrity-audit.json` verifies copies/archive and the manifest binding. Original and historical receipts remain untouched.

Validation is preserved in `reports/w-chess-validation.txt`; focused raw output is `reports/w-chess-evidence/focused-tests.txt`. No production file changed. The registry retains status `runtime` and adds this incomplete receipt as evidence. The missing evidence is a solver decision submitted on the live connection and a delivered terminal verdict; wiring plus an initial observation is not a puzzle measurement.
