# LCB /740 public-source candidate-path closure

The earlier six real oracle/noop controls remain untouched at `../lcb_control_evidence/`. This new evidence closes concrete public-statement and candidate/scorer separation gaps without a production endpoint/model request or H0 launch.

## Public prompt obtained

Fetched https://atcoder.jp/contests/abc360/tasks/abc360_a?lang=en with web_fetch, HTTP 200. Persisted English statement and public samples (no editorial/submissions) in isolated checkout `data/livecodebench/abc360_a.public.md`. SHA-256 `072b9614bc27ae5fb47d3a7fc90de200c15208722a145d6291985967cb50c14f` covers the persisted excerpt including provenance/delivery text, not the raw HTML. Public task identity abc360_a is independently bound by its upstream URL. Original `livecodebench/740` row identity remains filename-derived and explicitly unverified against the unread mixed pool. No custodian approval is asserted as necessary to use this public task.

## Executable path

`tools/lcb_candidate_path.py` provides a fixed localhost8002 relay over an AF_UNIX socket. Agent sandbox keeps `--unshare-net`; only its relay directory is mounted, so it cannot choose another upstream host/port. Only POST `/v1/chat/completions` is forwarded; caller-controlled upstream headers are not forwarded. Tested against a synthetic local HTTP server on an ephemeral port, not production8002.

`tools/launch_lcb740_candidate.py` stages only public task.md and a supplied agent entrypoint. Relay is stopped before verification. Candidate solution is copied alone into a fresh read-only sandbox for each stdin input. No tests file, expected output, trusted scorer module, relay socket, or verdict directory is mounted into candidate execution. Trusted platform compares captured stdout outside that namespace and writes output verdict separately. Candidate outputs/errors are not exported, avoiding input/expected-value feedback. CPU/address-space/output/time bounds and process-group timeout cleanup are applied.

Pinned upstream text/decimal comparison helpers retained. This is **not the unchanged official upstream execution path**: fresh external interpreter per case (no implicit import prelude), 3sec CPU/6sec wall, 512MiB address-space and 1MiB output cap. Must label results as scoped external-process LCB stdin verification. Supports /740 only.

## Actual gates

`tools/check_lcb_candidate_path.py`: **7/7 passed**, exit0, production endpoint/model requests=0:
- Honest synthetic candidate passes.
- Candidate verdict-file forgery fails.
- Candidate tests.json read fails.
- Candidate stack-frame expected-value exfiltration fails.
- Infinite loop bounded and fails.
- Dependency import/shadowing attempt fails (candidate has only solution.py, isolated Python).
- Agent-only Unix relay succeeds to fake endpoint while network remains none; relay omitted from verifier.

Synthetic fixtures exclusively drove development. No released private-case payload or values used for changes. Real references were not authored or changed. Main tracked clean (`git status` only preexisting untracked .overleaf-mcp/). `git diff --cached --check` passed. `candidate-path.patch` includes the original control patch plus new statement/execution/test files; original artifacts were not overwritten.

## Status and concrete next action

Executable candidate path exists; **H0 not authorized or launched**. The remaining immediately actionable binding is a self-contained agent that supports `HG_AGENT_UNIX_SOCKET` (HTTP over AF_UNIX) and a selected model/call-token budget. No honest command can substitute an unidentified agent. Existing OpenAI SDK base_url-only harnesses need a Unix transport adapter; no requirement for custodian/public-source approval is invented.

After parent selects that agent and authorizes a model execution, from isolated checkout:

```bash
env -i PATH=/mnt/8t/xubuqiang/anaconda3/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 python3 tools/launch_lcb740_candidate.py --agent /ABSOLUTE/UNIX_SOCKET_CAPABLE_AGENT.py --work-root /mnt/20t/xubuqiang/Study/lcb_candidate_work --output /mnt/20t/xubuqiang/Study/lcb_candidate_evidence/candidate-verdict.json
```

No request to 8002 was made during development; authentication/reachability there remains untested. Relay has input/response size bounds but not a model call/token budget enforcement mechanism. Broader kernel/runtime side channels are not proven absent by these synthetic tests. `launch.json` records all these limitations and source hashes.
