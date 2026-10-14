# w-chess2: ChessBench actor connection diagnosis and live receipt

**OPEN: `chessbench_puzzles / trusted-stepwise-transport` (`runtime`). No measured stepwise receipt exists.** Actor errors caused both incomplete attempts. No production/actor code was changed. Added only a refusal regression test and evidence; offline-only measurement and protocol separation remain in force.

## Socket diagnosis — actor lifecycle error, correct relay refusal

The previous actor disconnected itself. This is case **(b)**, not a platform/relay defect. Its model-generated first successful socket command created and connected the socket at `reports/w-chess2-evidence/previous-step-6.sh:9`, read at `:13`, printed the observation/FEN through `:32`, and reached the end at `:41` without any send or persistent command loop. Process exit closed its descriptor. These are exact extracted shell commands, not reconstructed code: `previous-step-6.json` names trace line 15 in the byte-for-byte `previous-trace.jsonl`, copied from `reports/w-chess-evidence/execution/task-result.json.trace`. That event has `step=6`, `exit=0`, `command_ms=37` and the initial public board in `output`.

The next command created a new socket and connected again (`reports/w-chess2-evidence/previous-step-7.sh:10`, `:11`); its raw trace event (`previous-step-7.json`, trace line 17) reports an empty receive followed by JSONDecodeError. The reference `loop` executes each shell action via a fresh `subprocess.run([shell, "-c", cmd], ...)` at `base_harness/loop/agent.py:684`; it does not promise to retain Python variables or descriptors between commands. That is normal shell process behavior. Its HTTP `Connection: close` setting at `:232` concerns the model HTTP API, not the separate AF_UNIX stepwise socket; it is not this disconnect's cause.

`eval/run/chess_stepwise.py:10` instructs the actor to connect once, read an observation and send one newline-delimited answer. `docs/chessbench-puzzles-evaluation.md`, **Opt-in runner wiring**, expressly requires one connection retained through the terminal observation. `eval/service/unix_stepwise_relay.py:55` reserves/rejects repeat connections; `:91` receives from the same descriptor and `:92` rejects EOF. `eval/service/stepwise_transport.py:143` converts that receive failure to `answer_receive_failed` at `:145`. `eval/run/chess_stepwise.py:58` and `:68` withhold reward for incomplete exchange. Nothing in this sequence is a transport defect. The previous raw controller evidence remains `measured=false`, `submissions=0`, `reason=answer_receive_failed` in `reports/w-chess-evidence/execution/task-result.json.verdict.evidence`; the previous staged counts remain in its `diagnostic_receipt.json` and were not rewritten.

## Actor selection and command

Selected the **existing, unmodified** `base_harness/codex_agent` instead of changing `loop`, its generated commands, or any relay limit. `base_harness/codex_agent/agent.py:102` launches a long-lived CLI, uses an ephemeral local-endpoint configuration at `:91`, and waits for its completion at `:106`. The installed CLI provides persistent terminal sessions; this makes retaining an open socket possible, but does not guarantee that the model will use them correctly. The observer supplied no chess move, reference line, search strategy, prompt repair, model tuning, retry trial or expanded task set. Model-generated commands remain unchanged in the trace. The goal remains the runner's existing interactive goal. A completed losing move would count; missing transport completion will not.

The launch script is adapted only to select that existing harness and record its executable binding from the prior observer `reports/w-chess-evidence/launch.py`. It still invokes public `run_one`, selected-only loading and the existing scoped diagnostic authorization. Unknown gates stay unknown. `reports/w-chess2-evidence/preflight.json` records the endpoint's actual HTTP response/model advertisement, the CLI version and executable SHA-256 before launch. No paid endpoint is configured.

Exact executed command, cwd `/tmp/hg-chess2`, also preserved in `reports/w-chess2-evidence/invocation.txt`:

```sh
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local HG_AGENT_CODEX_COMMAND=/home/xubuqiang/.nvm/versions/node/v22.16.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex python3 reports/w-chess2-evidence/launch.py --sampling diagnostic --rounds 0 --trials 1 --jobs 1 --authorize-unobserved-diagnostic 'Operator requests one fresh gated interactive ChessBench diagnostic after diagnosing the prior actor disconnect. Select the existing unmodified codex_agent harness with persistent terminal support and bind it only to the local qwen3.5-9b-local endpoint. One task, one trial, jobs=1, rounds=0; shared scorer/export and enforcement gates remain unknown. Raw controller evidence only; no comparable score publication, strict-replay comparison, method tuning, expansion or production authorization.'
```

Only `chessbench_puzzles.stepwise.v1` was requested. No strict-replay run, mixed comparison, curve point, method improvement or production authorization is part of this diagnostic. `interruption-closure` and all historical runs/archives are preserved.

## Released-task stepwise diagnostic — unmeasured

The selected actor **did not produce a measurement**. Its first executed socket client (`reports/w-chess2-evidence/actor-command-line-19.sh:8`) connects once and loops on `recv` at `:12`. But its `if data.get('solver_turn')` at `:25` gates the only send at `:42`. The actual initial controller observation has integer `solver_turn=0`, so that condition is false; the process waits for another board without sending the first answer. `data/datasets/chessbench_puzzles.py:216` initializes the counter to zero, `:254` exports it, and `:271` increments it. The readiness signal is `status=awaiting_move`, not truthiness of the turn index. This is another model-generated actor error, not a relay defect.

`actor-trace-line-19.json` records the first client `status=in_progress`, `exit_code=null`; its source is trace line 19 of `actor-trace.jsonl` (an exact extraction of `execution/task-result.json.trace`). The actor then launches another client at trace lines 21–22; `actor-trace-line-22.json` records `Connection ended, no more responses.` and `exit_code=0`. That is a rejected second connection while the allowance is already consumed, not a fresh puzzle. `actor-stderr-live.txt` also records attempts to use `write_stdin` on sessions without open stdin and a tool-argument parse error. Those observed errors do not show that the controller closed a healthy first connection. The preserved first command explains the missing submission; the controller receipt is authoritative about submissions and completion.

The CLI wrapper ultimately records `{"error":"codex timed out","timeout_s":210.0,"deadline_s":300.0}` at trace line 84 (`actor-trace-line-84.json`). The wrapper's default stop margin is source at `base_harness/codex_agent/agent.py:72`, and its timeout handling returns a failing actor exit at `:113`. `finish()` prioritizes that actor exit at `eval/run/chess_stepwise.py:56`, so **outer unmeasured reason** is `actor_exit_before_clean_completion` even though the **transport reason** is `answer_receive_failed`. No ordinary failed-puzzle score or zero was assigned. There was no second task/trial, actor code repair, relay relaxation or follow-up run.

Original identity, preserved unchanged at `reports/w-chess2-evidence/execution/identity.json`:

```json
{
  "run_id": "w-chess2-stepwise-20261014T220158Z-ca40c19f",
  "run_dir": "/tmp/hg-chess2/runs/w-chess2-stepwise-20261014T220158Z-ca40c19f",
  "work_root": "/tmp/w-chess2-stepwise-20261014T220158Z-ca40c19f-work",
  "workspace": "/tmp/w-chess2-stepwise-20261014T220158Z-ca40c19f-work/w-chess2-stepwise-20261014T220158Z-ca40c19f/workspace",
  "caller": "eval.run.runner.run_one",
  "side": "train",
  "harness": "codex_agent"
}
```

Selection and split, `execution/launch/selection.json` (all paths in this section are under `reports/w-chess2-evidence/`):

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

The released CSV's official payload split is `test`; selection uses the platform hash-train side, not heldout evaluation or an official study split. Counting rows establishes the ID pool without deriving unselected boards/gold. Only the selected record was decoded using the adapter's existing selected-only APIs. The selected ID repeats the deterministic diagnostic selection, not a resumed run; the run ID and external workspace are fresh.

Controller verdict and raw actor exit, `execution/task-result.json`:

```json
{
  "exit_code": 1,
  "stderr": "",
  "verdict": {
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
      "rejected_connections": 14,
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
      "reason": "actor_exit_before_clean_completion"
    },
    "scorer_isolation_class": "in-process",
    "unmeasured": "actor_exit_before_clean_completion",
    "detail": "actor_exit_before_clean_completion"
  },
  "identity": {
    "harness": "codex-agent",
    "agent_backend": "codex",
    "agent_model": "qwen3.5-9b-local"
  },
  "runtime_boundary": {
    "agent_timeout_s": 300,
    "verifier_timeout_s": 3600,
    "agent_network": "inherited",
    "agent_package_projected": false,
    "verifier_package": "trusted"
  },
  "harness_runtime": {
    "source": "platform",
    "python": null,
    "note": "the platform's interpreter supplies the dependencies"
  },
  "model_gateway": null,
  "env_usage": {}
}
```

Staged policy score, outcomes and coverage, `execution/diagnostic_receipt.json`:

```json
{
  "stage": "diagnostic",
  "trials": 1,
  "jobs": 1,
  "score": null,
  "outcomes": [
    {
      "reason": "actor_exit_before_clean_completion",
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
    "operator_authorization": "Operator requests one fresh gated interactive ChessBench diagnostic after diagnosing the prior actor disconnect. Select the existing unmodified codex_agent harness with persistent terminal support and bind it only to the local qwen3.5-9b-local endpoint. One task, one trial, jobs=1, rounds=0; shared scorer/export and enforcement gates remain unknown. Raw controller evidence only; no comparable score publication, strict-replay comparison, method tuning, expansion or production authorization.",
    "policy_enforcement_observed": false,
    "production_authorized": false,
    "run_id": "w-chess2-stepwise-20261014T220158Z-ca40c19f",
    "stage": "diagnostic",
    "task_id": "chessbench_puzzles/test/1287"
  }
}
```

The actor `identity.agent_backend=codex` describes the CLI. Its task-scoped provider configuration routes exclusively to the explicitly selected local model; it does not select a paid Codex endpoint. Preflight's raw `/models` HTTP response is in `preflight.json`; a second pre-launch response is in `execution/launch/endpoint.json`. The executable path, actual CLI version and executable SHA-256 are in `preflight.json`. `execution/launch/command.txt` binds the executable environment and exact invocation. These observations do not attest model weights or packet-level egress enforcement.

Metric, hashes, limits and comparison restrictions from `execution/diagnostic_receipt.json.context`:

```json
{
  "comparability_notes": [
    "Only chessbench_puzzles.stepwise.v1; no offline strict-replay evaluation or mixed point.",
    "Hash-train side selected before payload decoding; released CSV test slice has no official study split. No method tuning or improvement.",
    "Raw controller measurement is distinct from policy publication. Unknown model-weight digest, transitive dependency closure, CPU/memory enforcement and spend budget; no comparison, expansion or production authorization."
  ],
  "dataset": "chessbench_puzzles",
  "endpoint": "http://127.0.0.1:8002/v1",
  "gates": {
    "detail": "Explicit operator authorization for one diagnostic; shared scorer/export gates and backend observations remain unresolved.",
    "receipt_sha256": null,
    "status": "unknown"
  },
  "hashes": {
    "harness": "3ae117030f717df421535b105d28347d8b2fe9c4b13c677e2e258b5eb3360cb6",
    "manifest": "40ce318d1c316070b50ec7373476fcccc430ac19cbf7544d6f6f931a8f06e21d",
    "model": null,
    "source": "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48",
    "split": "26781ee746b22e62e743d7c530778c0e3615027ec75f55ed337634267ff0b25f"
  },
  "limits": {
    "budget": null,
    "resource": {
      "agent_timeout_s": 300,
      "verifier_timeout_s": 3600
    }
  },
  "metric": {
    "name": "ChessBench puzzle accuracy",
    "scorer_sha256": "61165a5351b9068ebdac5e66f34cba1b6ed3c658ee1198ebdaf789be4e11b261"
  },
  "side": "train"
}
```

`execution/launch/source.json` binds the pinned released CSV and upstream revision to this scorer file:

```json
{
  "path": "/mnt/20t/xubuqiang/datasets/chessbench_puzzles/_src/puzzles.csv",
  "sha256": "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48",
  "expected_sha256": "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48",
  "revision": "90ae0e6b121673fc3079aaeffa047580bb600c0a",
  "adapter_sha256": "61165a5351b9068ebdac5e66f34cba1b6ed3c658ee1198ebdaf789be4e11b261",
  "model_weights_sha256": null
}
```

`execution/launch/manifest.json` binds the selected task, protocol, platform commit, endpoint, model, effective task timeout, staged shape and external work root before execution. `execution/launch/harness-files.json` contains each staged harness file SHA-256; `execution/launch/harness-after.json` records its final git tree identity and clean status. There is no model-weight digest or enforced monetary/token ceiling attested: their policy fields are null. CPU/RAM quotas and transitive scorer dependency closure remain unproven. Runtime reports actor/verifier deadlines separately; no command verifier was launched on this trusted in-process controller branch (`eval/run/runner.py:522`). `model_gateway=null` reflects native direct model routing; it is not a claim that container gateway observations exist.

No completed `turn.completed` usage event is present in `actor-trace.jsonl`; the trace ends at the CLI timeout. Model token/call usage is therefore unknown, not zero. Model-produced action and error events are preserved, not converted into resource measurements.

## Cleanup and integrity

The controller's raw cleanup values are in `execution/task-result.json.verdict.evidence.cleanup` above. Independent post-run path observations in `cleanup-observation.json`:

```json
{
  "observed_at": "2026-10-14T22:05:43.849381+00:00",
  "attribution": "Task path matched selected task.json; sole candidate socket directory observed during this run. No paths removed by observer.",
  "paths": [
    {
      "path": "/tmp/hg-task-_rvaztnu",
      "exists": false
    },
    {
      "path": "/tmp/hg-stepwise-lgizndvi",
      "exists": false
    }
  ],
  "workspace_retained_for_evidence": "/tmp/w-chess2-stepwise-20261014T220158Z-ca40c19f-work/w-chess2-stepwise-20261014T220158Z-ca40c19f/workspace"
}
```

`live-process-observation.json` records sampled launcher/descendant process IDs and Linux start-time ticks during the run. `process-cleanup-observation.json` checks those same identities after completion; every recorded entry has `present=false`, `same_process=false`, `current=null`. The observer sent no signals and removed no paths. The external workspace and original run directory are retained. This is a native files run; no container/snapshot execution or snapshot teardown was observed.

Formal lifecycle/admission remains unknown in `execution/diagnostic_receipt.json`, independently of successful relay cleanup:

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

`execution/launch/platform-before.json` hashes the protected platform files before the task; `execution/launch/platform-diff.json` records `added=[]`, `removed=[]`, `modified=[]`. The observer and review copies did not modify production code, harness code, trusted reference data or gates during execution. Registry/journal/test edits occurred after the run.

`collect.py` copies the original completed run directory without rewriting any run receipt. `artifact-inventory.json` records each original path, review-copy path, exact byte size and SHA-256. `run-artifacts.tar.gz` preserves the full original run tree; `archive-sha256.json` records the archive's exact path, byte size and digest. `integrity-audit.json` verifies every original/copy/archive member matches and the policy manifest hash matches. The executed launch source is preserved both at `launch.py` and `execution/launch/launch.py`. `previous-trace.jsonl` and extracted previous commands provide file/line references into the prior immutable evidence rather than changing that evidence.

## Disposition and validation

`trusted-stepwise-transport` remains **runtime/open** in `docs/dataset-blockers.json`; this receipt is added as evidence. The precise missing evidence is a real solver decision sent on the retained live connection, delivery of its terminal observation, and a clean actor exit with channel cleanup. Selecting a CLI with persistent terminal support did not guarantee a compatible model-authored client. There is no demonstrated platform defect to fix here, and changing the generated client or inventing a guaranteed losing submission to force a measurement would not satisfy this task. A future authorized attempt needs an actor that actually follows the documented protocol, with a fresh run ID and the existing gates.

`interruption-closure`, shared gates, all historical entries/run directories and the original diagnostic receipts remain untouched. Offline strict replay remains the only measured path; any point that mixes it with stepwise must still be rejected. There is no production or expansion authorization.

Added `test_disconnect_after_initial_board_cannot_reconnect_or_score` in `tests/quality/test_chessbench_stepwise_runner.py` to reproduce initial-board close/reconnect with a fabricated puzzle and assert that no score is published. The existing multi-turn, refusal, cleanup, cache and mixed-protocol checks remain. Full commands/output are preserved in `reports/w-chess2-validation.txt`; the original pre-edit focused output is `focused-tests.txt`, and final focused/checker output has its own files. No production fix was made.

Final validation: `reports/w-chess2-evidence/focused-final.txt` records `147 passed in 38.96s`. `checker-final.txt` records `valid=true`, `datasets=28`, `shared_blockers=2`, `historical_records=11`, `production_authorized=false`. `report-audit.json` verifies original/copy/archive identities, exact trace extractions, manifest binding, append-only journal, unchanged production files, and unchanged registry content outside this target. The raw checker/test output is reproduced in `reports/w-chess2-validation.txt`.
