# w-chess3: diagnostic control terminal-exchange receipt

## CLOSED: chessbench_puzzles / trusted-stepwise-transport

The AGENT'S OWN GENERATED SCRIPT caused the falsy-zero bug. A fresh, authorized live stepwise diagnostic now delivered a terminal observation with clean actor completion and channel cleanup. The fixed reference actor chose a legal move and lost; the trusted controller recorded an actual puzzle measurement. This closes only the named transport-execution requirement. The staged policy receipt still withholds publication because enforcement was not observed; no comparable model accuracy, curve point, pilot expansion or production authorization is claimed.

## Correction made before execution

Read the round-31 `reports/w-chess-receipts.md` and round-38 `reports/w-chess2-receipts.md` and their preserved evidence as starting facts. Repository search is preserved verbatim in `reports/w-chess3-evidence/actor-bug-search.txt`. The send gate `if data.get('solver_turn'):` is at `reports/w-chess2-evidence/actor-command-line-19.sh:25`, inside the model-generated script. Its first board carries integer zero. The platform does not use that gate: `eval/run/chess_stepwise.py:8` allowlists the public field, `eval/service/stepwise_transport.py` dispatches using `observation["status"]`, and `data/datasets/chessbench_puzzles.py:216`, `:254`, `:271` initialize, export and increment the counter. `awaiting_move` is readiness; the counter is zero-based.

Corrected the target's `observed` before running anything. The full corrected blocker, including all prior evidence locators and next_action, is retained at `reports/w-chess3-evidence/corrected-blocker-before-run.json`; its checker output is `reports/w-chess3-evidence/correction-checker.txt`. The final active-only registry removes this earned closure and retains the correction/receipt distinction in one appended review note. No platform code, admission gate, refusal, scorer or connection/submission allowance was changed.

## Diagnostic actor and exact invocation

`reports/w-chess3-control/actor.py` and `harness.json` are explicitly marked diagnostic control, not a candidate method. Before selecting or executing the released task, the actor's move rule was fixed to the lexicographically first legal UCI move from each current public FEN. It uses python-chess legality only, with no model, engine, search or puzzle-specific choice. The one connection stays open through newline-delimited observations/submissions; sends depend on `status=awaiting_move`, including turn zero, and stop on `solved`/`failed`. Actor-written events corroborate reception but never supply the score.

`tests/quality/test_chess3_diagnostic_actor.py` executes this unchanged actor in the real sandbox against fabricated multi-turn success and terminal-loss cases, checking turn-zero submission, one retained connection, legal moves, equality with controller-delivered observations, terminal reception and clean completion. These are synthetic protocol tests, separate from the single released-task run.

Exact command, cwd `/tmp/hg-chess3`, recorded in `reports/w-chess3-evidence/invocation.txt` and `execution/launch/command.txt`:

```sh
env HG_AGENT_BACKEND=mock python3 reports/w-chess3-evidence/launch.py --sampling diagnostic --rounds 0 --trials 1 --jobs 1 --authorize-unobserved-diagnostic 'Operator explicitly authorizes one fresh gated interactive ChessBench diagnostic using a deterministic protocol-correct reference actor marked as a diagnostic control, not a candidate method. Choose the lexicographically first legal UCI move from the current public FEN; no model calls, engine, search, gold access or puzzle tuning. One task, one trial, jobs=1, rounds=0. Existing gates, relay limits and unknown shared enforcement/lifecycle claims remain unchanged. Obtain a delivered terminal exchange and clean actor completion; raw controller evidence only, no comparable score publication, strict-replay comparison, expansion or production authorization.'
```

`reports/w-chess3-evidence/launch.py` uses the documented trusted-caller API `eval.run.runner.run_one`, selected-only adapter APIs, existing `Authorization.require_scope`, staged selection and policy receipt builder. It reserves a new external receipt directory without resume/overwrite and stages only the control harness into the external work root. CSV pin and sandbox preflight are checked before actor launch. The actor has no dataset/reference access. Only the trusted controller receives the selected private verifier record.

All `execution/` paths below are under `reports/w-chess3-evidence/`. They are byte-for-byte review copies of the external original run, whose identity is:

`execution/identity.json`:

```json
{
  "run_id": "w-chess3-stepwise-20261014T222208Z-728e7478",
  "run_dir": "/tmp/hg-w-chess3-receipts/w-chess3-stepwise-20261014T222208Z-728e7478",
  "work_root": "/tmp/w-chess3-stepwise-20261014T222208Z-728e7478-work",
  "workspace": "/tmp/w-chess3-stepwise-20261014T222208Z-728e7478-work/w-chess3-stepwise-20261014T222208Z-728e7478/workspace",
  "caller": "eval.run.runner.run_one",
  "side": "train",
  "harness": "w-chess3-diagnostic-protocol-control",
  "diagnostic_control": true,
  "candidate_method": false,
  "model_used": false,
  "endpoint": null
}
```

The launcher exited as recorded in `reports/w-chess3-evidence/launcher-exit.json`:

```json
{
  "exit_code": 0
}
```

## Selection, scope and provenance

`execution/launch/selection.json`:

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

The CSV row count establishes only the task-ID pool; only selected records are decoded. The platform hash-train side is used within the released CSV's `test` payload. This is not an official study split, heldout evaluation, resumed run, method tuning or expanded trial set.

`execution/launch/source.json`:

```json
{
  "path": "/mnt/20t/xubuqiang/datasets/chessbench_puzzles/_src/puzzles.csv",
  "sha256": "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48",
  "expected_sha256": "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48",
  "revision": "90ae0e6b121673fc3079aaeffa047580bb600c0a",
  "adapter_sha256": "61165a5351b9068ebdac5e66f34cba1b6ed3c658ee1198ebdaf789be4e11b261",
  "model_weights_sha256": null,
  "model_used": false
}
```

`execution/launch/manifest.json` binds the pre-execution task/source/harness hashes, protocol, staged shape, platform commit and external work root:

```json
{
  "run_id": "w-chess3-stepwise-20261014T222208Z-728e7478",
  "selected_task_ids": [
    "chessbench_puzzles/test/1287"
  ],
  "task_sha256": "4ad872dd86b728d125a01de2680b5ea217dcd0ed5a09b0787b456a93dafdfa00",
  "source_sha256": "4301d1b2aa402d42cd325b406b7a642a6ace6daa54d872955932718e860093b0",
  "harness_files_sha256": "1c970f47687941b7678a28d67fb31ea1171d006073c5d705b5c79de9e3e3e012",
  "platform_commit": "99a29904996a38eb66783f70c231809a574203ea",
  "protocol": "chessbench_puzzles.stepwise.v1",
  "endpoint": null,
  "model": null,
  "diagnostic_control": true,
  "candidate_method": false,
  "move_rule": "lexicographically first legal UCI",
  "env": {
    "kind": "files"
  },
  "timeout_s": 300,
  "rounds": 0,
  "trials": 1,
  "jobs": 1,
  "work_root": "/tmp/w-chess3-stepwise-20261014T222208Z-728e7478-work"
}
```

`execution/launch/harness-files.json` records the staged control source hashes:

```json
{
  ".gitignore": "0934a3e721123a834a881175f047aca1833ccc19929223e0632dd1fd867ee1b3",
  "actor.py": "da2dbeda7f49e312bf0c6d628c009a9ccb38fa880b8497247935bce73d94e1ed",
  "harness.json": "d33b8c54de7ef9278daea896a7c760771fa0bbec188d9de688ce348dc466d9fa"
}
```

`execution/launch/harness-after.json`:

```json
{
  "content_sha": "c54ac3a3259c9444c6d226fa6a267e307703da12",
  "status": ""
}
```

`execution/launch/platform-before.json` binds the protected platform file contents before execution. `execution/launch/platform-diff.json` is:

```json
{
  "added": [],
  "removed": [],
  "modified": []
}
```

## Delivered terminal exchange and raw controller measurement

`execution/task-result.json`, exact fields `exit_code`, `stderr`, `verdict`:

```json
{
  "exit_code": 0,
  "stderr": "",
  "verdict": {
    "kind": "stepwise",
    "protocol": "chessbench_puzzles.stepwise.v1",
    "evidence": {
      "schema": "harnessgrad.unix-stepwise-relay.v1",
      "protocol": "chessbench_puzzles.stepwise.v1",
      "status": "complete",
      "measured": true,
      "production_authorized": false,
      "limits": {
        "timeout_s": 300,
        "max_connections": 1,
        "max_submissions": 256,
        "max_message_bytes": 4096
      },
      "connections": 1,
      "rejections": [],
      "rejected_connections": 0,
      "transport": {
        "schema": "harnessgrad.public-stepwise-transport.v1",
        "contract": "chessbench_puzzles.stepwise.v1",
        "status": "terminal",
        "measured": false,
        "production_authorized": false,
        "submissions": 1,
        "limits": {
          "max_submissions": 256,
          "max_message_bytes": 4096
        },
        "events": [
          {
            "kind": "observation",
            "message": "{\"contract\":\"chessbench_puzzles.stepwise.v1\",\"fen\":\"5rk1/1R3p1p/p5p1/5n2/PPQ1p3/4P3/3q1PPP/2R3K1 b - - 2 29\",\"solver_turn\":0,\"status\":\"awaiting_move\",\"verdict\":\"awaiting_move\"}"
          },
          {
            "kind": "submission",
            "message": "{\"uci\": \"a6a5\"}"
          },
          {
            "kind": "observation",
            "message": "{\"contract\":\"chessbench_puzzles.stepwise.v1\",\"fen\":\"5rk1/1R3p1p/6p1/p4n2/PPQ1p3/4P3/3q1PPP/2R3K1 w - - 0 30\",\"solver_turn\":1,\"status\":\"failed\",\"verdict\":\"wrong_move\"}"
          }
        ]
      },
      "cleanup": {
        "server_closed": true,
        "thread_joined": true,
        "socket_removed": true
      },
      "comparability": "Interactive and offline ChessBench protocols are not comparable.",
      "metric": "ChessBench puzzle accuracy",
      "reward": 0.0,
      "correct": false,
      "verdict": "wrong_move"
    },
    "scorer_isolation_class": "in-process",
    "score": 0.0,
    "passed": false,
    "detail": "wrong_move"
  }
}
```

The transport records an initial `awaiting_move` observation at turn zero, the legal submission, and the terminal `failed` observation. Its inner `transport.measured=false` describes the pure delivery layer, which never scores; the trusted runner's outer `evidence.measured=true` and `verdict.score` above are the actual controller measurement. This is a measured losing task, not a timeout or an invented zero.

The actor's actual receive/send/completion trace is `execution/actor-trace.jsonl`, identical to `execution/task-result.json.trace`:

```jsonl
{"event": "control", "diagnostic_control": true, "candidate_method": false, "move_rule": "lexicographically first legal UCI", "model_used": false, "endpoint": null, "socket": "/tmp/hg-stepwise-cal7u6ed/stepwise.sock", "task_path": "/tmp/hg-task-wjla_ob4/task.json", "python_chess_version": "1.11.2", "socket_timeout_s": 300, "max_message_bytes": 4096}
{"event": "observation", "observation": {"contract": "chessbench_puzzles.stepwise.v1", "fen": "5rk1/1R3p1p/p5p1/5n2/PPQ1p3/4P3/3q1PPP/2R3K1 b - - 2 29", "solver_turn": 0, "status": "awaiting_move", "verdict": "awaiting_move"}}
{"event": "submission", "solver_turn": 0, "answer": {"uci": "a6a5"}}
{"event": "observation", "observation": {"contract": "chessbench_puzzles.stepwise.v1", "fen": "5rk1/1R3p1p/6p1/p4n2/PPQ1p3/4P3/3q1PPP/2R3K1 w - - 0 30", "solver_turn": 1, "status": "failed", "verdict": "wrong_move"}}
{"event": "terminal_received", "status": "failed", "verdict": "wrong_move"}
{"event": "completed", "terminal_received": true, "channel_closed": true}
```

`execution/raw-controller-outcomes.json` preserves the existing policy converter's pre-publication classification; `reports/w-chess3-evidence/raw-controller-summary.json` derives its coverage using the existing `measurement_summary` function and explicitly identifies itself as controller-only:

```json
{
  "source": "/tmp/hg-w-chess3-receipts/w-chess3-stepwise-20261014T222208Z-728e7478/raw-controller-outcomes.json",
  "interpretation": "Controller outcomes before policy publication gating; not a staged policy receipt.",
  "outcomes": [
    {
      "task_id": "chessbench_puzzles/test/1287",
      "trial": 1,
      "status": "measured",
      "score": 0.0,
      "reason": null
    }
  ],
  "score": 0.0,
  "coverage": {
    "selected_tasks": 1,
    "expected_trials": 1,
    "measured_tasks": 1,
    "measured_trials": 1,
    "invalid_tasks": 0,
    "invalid_trials": 0,
    "unmeasured_tasks": 0,
    "unmeasured_trials": 0
  }
}
```

## Staged policy receipt: publication remains unmeasured

`execution/diagnostic_receipt.json`, raw publication fields:

```json
{
  "stage": "diagnostic",
  "trials": 1,
  "jobs": 1,
  "score": null,
  "outcomes": [
    {
      "reason": "policy_enforcement_not_observed",
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
  }
}
```

The existing `build_receipt` policy deliberately converts a completed raw measurement into an unmeasured publication under unobserved diagnostic authorization (`eval/policy/diagnostic_policy.py`). Its raw enforcement fields, in the same receipt, are:

```json
{
  "comparable": false,
  "measured": false,
  "non_comparable_reason": "policy_enforcement_not_observed",
  "policy_enforcement_observed": false,
  "production_authorized": false,
  "run_id": "w-chess3-stepwise-20261014T222208Z-728e7478",
  "stage": "diagnostic",
  "task_id": "chessbench_puzzles/test/1287"
}
```

The exact operator authorization is preserved in full in that same `enforcement.operator_authorization`, `execution/launch/policy-input.json` and the command above. The raw controller loss is not substituted for the policy's null score. The published invalid/unmeasured counts above remain unchanged. The narrow blocker asks for delivered terminal execution, which now exists; it does not require published model accuracy or a solved puzzle.

Metric, source/split/manifest/model/harness hashes, endpoint and effective policy limits from `execution/diagnostic_receipt.json.context`:

```json
{
  "metric": {
    "name": "ChessBench puzzle accuracy",
    "scorer_sha256": "61165a5351b9068ebdac5e66f34cba1b6ed3c658ee1198ebdaf789be4e11b261"
  },
  "hashes": {
    "harness": "1c970f47687941b7678a28d67fb31ea1171d006073c5d705b5c79de9e3e3e012",
    "manifest": "4b5fc2b3bbbef5093e4900ed42f71c767499c2e93bd17743146d836079b90cf3",
    "model": null,
    "source": "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48",
    "split": "26781ee746b22e62e743d7c530778c0e3615027ec75f55ed337634267ff0b25f"
  },
  "endpoint": null,
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
    "Diagnostic control only, not a candidate method; no model calls or endpoint. Raw controller measurement is distinct from policy publication. Transitive dependency closure, CPU/memory enforcement and spend budget remain unproven; no comparison, expansion or production authorization."
  ]
}
```

## Endpoint, effective limits and cleanup

No model or endpoint was used. `execution/launch/model-binding.json`:

```json
{
  "model_used": false,
  "endpoint": null,
  "model": null,
  "actor": "deterministic diagnostic control; no model client",
  "runner_backend": "mock"
}
```

The runner backend label `mock` is used for a no-model scripted actor; it is not a mocked relay, task, reference or score. No model-weight digest applies, and no GPU utilization is claimed. Native networking is inherited, not network-isolated. No CPU/RAM quota or enforced token/monetary ceiling is attested.

`execution/task-result.json`, raw runtime/resource fields:

```json
{
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
  "env_usage": {},
  "identity": null
}
```

The controller's relay limits and cleanup booleans are in the raw verdict above; the actor's local socket/message limits are in its trace. The verifier deadline is recorded but no command verifier executed in this in-process stepwise branch. `execution/launch/sandbox-preflight.json`:

```json
{
  "ok": true,
  "detail": "bwrap active; 2 trees hidden; source read-only; .state/ writable; artifacts frozen for verification; plan v2; /usr/bin/bwrap"
}
```

Independent post-return path observations in `execution/cleanup-observation.json`:

```json
{
  "observed_at": "2026-10-14T22:22:10.926891+00:00",
  "attribution": "Actor trace paths, observed after run_one returned; observer removed nothing.",
  "paths": [
    {
      "path": "/tmp/hg-task-wjla_ob4/task.json",
      "exists": false
    },
    {
      "path": "/tmp/hg-stepwise-cal7u6ed",
      "exists": false
    },
    {
      "path": "/tmp/hg-stepwise-cal7u6ed/stepwise.sock",
      "exists": false
    }
  ],
  "workspace_retained_for_evidence": "/tmp/w-chess3-stepwise-20261014T222208Z-728e7478-work/w-chess3-stepwise-20261014T222208Z-728e7478/workspace",
  "workspace_exists": true
}
```

The observer removed no paths. The actor closes its one channel and exits successfully; the runner reports server closure, thread join and socket removal, with the socket directory absent afterward. The external original run and workspace remain for evidence. This native files run did not execute a container/snapshot lifecycle. Formal admission/lifecycle remains unknown, independently of successful relay cleanup. Raw `execution/diagnostic_receipt.json` fields:

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

## Preservation, closure and validation

`reports/w-chess3-evidence/collect.py` copied the completed external run without rewriting it. `artifact-inventory.json` lists every original/copy path, relative path, byte size and SHA-256. `run-artifacts.tar.gz` preserves the original receipt tree; `archive-sha256.json` records:

```json
{
  "path": "reports/w-chess3-evidence/run-artifacts.tar.gz",
  "bytes": 232884,
  "sha256": "0478ecda40635c818e676f9d64c747a4692afade4e2526a968f700de60bf59b0"
}
```

`reports/w-chess3-evidence/integrity-audit.json`:

```json
{
  "original_copy_archive_files_checked": 21,
  "all_copies_and_archive_match": true,
  "policy_manifest_matches": true,
  "launch_source_matches": true,
  "actor_trace_matches": true,
  "platform_diff": {
    "added": [],
    "removed": [],
    "modified": []
  }
}
```

Only `chessbench_puzzles / trusted-stepwise-transport` is removed from the active blocker list. The correction survives in the checked-in corrected blocker and appended registry review note. `chessbench_puzzles / interruption-closure`, all other blockers/shared gates, and historical records are unchanged. `runs/` was absent and is never created or touched; no historical run/receipt/archive is resumed, overwritten or removed. Scope, append-only journal, every evidence locator, original/copy/archive identities and the external work root are checked in `reports/w-chess3-evidence/report-audit.json`.

Only `chessbench_puzzles.stepwise.v1` was executed. No offline strict-replay evaluation, comparison, mixed point or curve was produced. The old offline-only claim is superseded solely by this diagnostic control's raw interactive measurement; there is still no model-driven interactive accuracy or comparable publication. Shared scorer/export/enforcement gates remain unresolved, and `interruption-closure` remains OPEN.

`reports/w-chess3-validation.txt` preserves exact checker and focused-test commands with raw output; `reports/w-chess3-evidence/focused-tests.txt` preserves the final focused output. Journal entry: `docs/adapter-integration-journal.md`, unique heading ending ` - w-chess3`.
