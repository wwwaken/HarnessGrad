# w-net: agent-call audit of the preserved w-tbrun4 diagnostic

The previous agent **did run and exercised the local endpoint**. `env_usage.calls=0` is expected for this task: that field measures environment-service model spend, not the agent's spend. There is no second missing-agent wiring defect established by that value. The invalid diagnostic's aggregate agent usage also reads zero because the runner excludes invalid outcomes from its aggregate traces; the preserved invalid trace and gateway observations carry the actual agent evidence. No source was changed for this audit.

## Raw historical artifacts

Frozen execution artifact: `/tmp/hg-tbrun4/reports/w-tbrun4-evidence/execution/diagnostic_execution.json` (original: `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/diagnostic_execution.json`). Raw fields:

```json
{
  "env_usage": {"input": 0, "output": 0, "calls": 0, "services_reported": 0},
  "tokens": {"input": 0, "output": 0, "calls": 0, "tasks_reported": 0},
  "traces": {},
  "trial_traces": {},
  "model_gateway": null
}
```

Frozen trace: `/tmp/hg-tbrun4/reports/w-tbrun4-evidence/execution/progress/round-0/traces/openssl-selfsigned-cert.invalid.jsonl` (original: `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/progress/round-0/traces/openssl-selfsigned-cert.invalid.jsonl`). Its first record declares `harness="loop"`, `agent_model="qwen3.5-9b-local"`, `agent_backend="openai"`. Its final usage record is:

```json
{"usage": {"calls": 32, "input_tokens": 179300, "output_tokens": 10999, "retries": 0, "context_trims": 0}}
```

The trace contains model replies and executed shell commands; its first reply is `{"tool": "bash", "command": "mkdir -p /app/ssl && chmod 755 /app/ssl"}`. Those events belong to the actual task agent, not the endpoint preflight probe.

Frozen progress artifact: `/tmp/hg-tbrun4/reports/w-tbrun4-evidence/execution/progress/round-0/openssl-selfsigned-cert.json` (original: `/tmp/hg-tbrun4/runs/w-tbrun4-terminal-bench-20261014T195342Z-82530223/progress/round-0/openssl-selfsigned-cert.json`). Raw `harness_output` fields, with the unrelated dependency-overlay description omitted:

```json
{
  "exit_code": 0,
  "stderr": "",
  "model_gateway": {
    "published": true,
    "target": "127.0.0.1:8002",
    "connections": 32,
    "upstream_connect_failed": 0,
    "upstream_connect_error": null,
    "upstream_closed_first": 32,
    "client_closed_first": 0,
    "bytes_to_upstream": 708355,
    "bytes_to_client": 68268,
    "read_errors": []
  }
}
```

The gateway transport counters independently show traffic to the single local model endpoint. The trace's model-call count is harness-reported; the gateway's connection count is transport accounting, not a general interchangeable model-call metric.

## Source explanation

- `eval/service/services.py:177-203` defines environment usage as the environment's own model spend read from service recordings. `eval/run/runner.py:531-537` explicitly reads that spend separately. `INTERFACE.md:834-840` distinguishes agent, method and environment models and requires environment spend to remain separate from harness spend.
- The snapshot-container path returns `env_usage={}` in `eval/containers/container_state.py:221-223`. `eval/run/runner.py:977` initializes aggregate environment usage with zeros, and `:1259-1266` adds only the result's environment-service usage. Thus `env_usage.calls=0` does not imply the agent never ran.
- `base_harness/loop/agent.py:269-273` increments `USAGE["calls"]` for `_complete`; `:240-245` makes the real `client.chat.completions.create` request and records provider usage; `:609-613` invokes `_complete` and writes each model reply; `:745` writes the final `usage` block to the trace.
- `eval/containers/container_state.py:151-160` publishes the host-local agent endpoint through the model gateway, and `:176-180` executes the harness. The preserved progress gateway counters above corroborate this path actually ran.
- The missing CTRF causes an invalid outcome at `eval/run/runner.py:1102-1111`; `:1121-1127` writes its diagnostic progress and returns only the invalid classification. `:1179-1181` skips invalid outcomes in the merge. Aggregate harness `tokens` are then computed from aggregate `traces` at `:1299-1310`; the frozen aggregate has `traces={}`, so its zero tokens are incomplete spend accounting for this invalid outcome. This is an accounting limitation, not proof of missing agent execution. Reported here only, as requested.

## Requested recipe compatibility

The preserved launch command at `/tmp/hg-tbrun4/reports/w-tbrun4-evidence/launch/command.txt` uses `--harness loop --side train --policy-evidence ...`. The successful preflight recipe was not `loop_plain` on eval.

`base_harness/loop_plain/harness.json:1-8` omits `env_kinds`; `harnessgrad/environments.py:185` defaults such a descriptor to `files`, and `:190-195` refuses an `exec` requirement. `data/datasets/terminal_bench.py:194` declares `kind="exec"`. `base_harness/loop/harness.json:8-10` explicitly declares `files` and `exec`. `driver.py:801-804` enforces the compatibility check. `loop_plain` has real OpenAI completion code (`base_harness/loop_plain/agent.py:138-142`, `:153-157`) but its current descriptor is not admitted for Terminal-Bench; no descriptor or gate was modified.

The suggested `--side eval` together with `--authorize-unobserved-diagnostic` is refused at `driver.py:390-396`, which requires train. Staged execution also requires policy evidence at `driver.py:402-413`. These are existing gates; this audit does not weaken or bypass them.

Historical artifacts, source, endpoint state and runs were read only. No diagnostic was launched by this audit.
