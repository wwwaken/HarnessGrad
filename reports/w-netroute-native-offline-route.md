# Native offline model route (w-netroute)

FOUND: native `network: none` can keep `--unshare-net` and expose an ordinary HTTP model URL through a fixed AF_UNIX route. The host fixes the upstream; the namespace-local bootstrap binds only `127.0.0.1` and changes only the child model base URL (eval/service/native_model_route.py:23-48; eval/service/native_model_forwarder.py:44-60). Socket and bootstrap binds are infrastructure, outside setup/task metadata (eval/containers/model_route.py:7-35; eval/run/runner.py:444-453,520-523).

FOUND: the socket source is checked for absolute/non-symlink socket type at launch, writable-source aliases and overlapping mount destinations are refused, and final infrastructure mounts follow all parent/immutable mounts so no later bind covers or reopens them (eval/containers/model_route.py:11-30; eval/containers/sandbox.py:378-390). This adds visibility, so native `PLAN_VERSION` is 4; Docker remains untouched (reports/w-netroute-native-offline-route-validation.txt:270; reports/w-netroute-native-offline-route-validation.txt:233). Existing immutable-runtime binds/remount ordering is retained in eval/containers/sandbox.py:365-376.

FOUND: admission is no longer determined by control role or mock/live backend. Network policy remains separate from the platform model transport (eval/policy/runtime_policy.py:10-18; tests/quality/test_native_model_route.py:72-79).

| Declared network | Native files path / admit_native_network | Exec path (unchanged) |
| --- | --- | --- |
| omitted / `None` | Admitted; inherited host network, no model transport added. | Native admission is bypassed. Omitted network defaults to `none`; a local live model can cause an internal-network gateway. |
| `none` | Admitted for live, mock and control. Private network namespace; live backend needs a valid configured HTTP model route. Missing URL/unsupported URL fails closed; no-sandbox is refused. | Native admission is bypassed. Isolated Docker network; local model uses the existing internal gateway. |
| `bridge` | Refused: unsupported native policy. | Native admission is bypassed; declared Docker bridge policy. |
| `services` | Refused: native service network cannot be honoured. | Native admission is bypassed; declared services use the per-task internal network. |

Matrix sources: eval/policy/runtime_policy.py:10-18; eval/containers/sandbox.py:202-205; eval/run/runner.py:239-245,424-453,468-469; eval/service/services.py:236-247; INTERFACE.md:824-838. The independent policy-observation refusal remains in eval/run/runner.py:39-87 and is explicitly asserted by tests/quality/test_native_model_route.py:184-193. This is transport closure, not production authorization.

FOUND: exact live command: `TMPDIR=/tmp python3 tests/quality/native_model_route_control.py`. The control invokes native admission with `kind=files`, `network=none`, backend `openai`; the launched client also observes backend `openai`. Observed model metadata: HTTP 200, model ID `qwen3.5-9b-local`; isolated DNS: `gaierror: [Errno -3] Temporary failure in name resolution`; isolated TCP `1.1.1.1:80`: `OSError: [Errno 101] Network is unreachable`. With identical mounts and only `--unshare-net` removed, DNS resolves and TCP connects. Distinct network-namespace IDs and cleanup booleans are recorded exactly (JSON_LINE markers preserve trailing whitespace) (reports/w-netroute-native-offline-route-validation.txt:6). This comparison establishes namespace-caused denial for these probes rather than an unavailable host route. It does not establish arbitrary kernel escape resistance.

FOUND: an earlier comparison to `1.1.1.1:443` timed out even without isolation, so its assertion failed; that incomplete control is preserved (reports/w-netroute-native-offline-route-validation.txt:386). The corrected port-80 control and the final explicit-backend control are separate invocations (reports/w-netroute-native-offline-route-validation.txt:401; reports/w-netroute-native-offline-route-validation.txt:6). No old run ID or dataset receipt is used by the control (tests/quality/native_model_route_control.py:53-91).

FOUND: synthetic HTTP tests exercise actual runner launch with backend `openai`, private bwrap networking, the separate diagnostic authorization, unchanged request/response bytes, and gateway accounting (tests/quality/test_native_model_route.py:169-193). Another live bwrap test sends 131073-byte bodies twice over keep-alive and changes both Host and absolute HTTP target; the destination still remains the fixed synthetic upstream, and the bound bootstrap rejects writes (tests/quality/test_native_model_route.py:136-166). Cleanup, launch revalidation, timeout and exit-code tests are in tests/quality/test_native_model_route.py:90-133,196-214.

FOUND: raw inherited-suite baseline: **231 passed, 10 failed, 2 skipped**; raw after plus new tests: **245 passed, 10 failed, 2 skipped** (reports/w-netroute-native-offline-route-validation.txt:16; reports/w-netroute-native-offline-route-validation.txt:114). The two isolation failures are the missing gitignored `.env` and the existing `test_the_harness_cannot_read_the_platform_or_its_answers` failure. Eight other baseline failures name the absent sibling `harnessgrad_work` fixture path; no fix to either isolation condition was attempted. The targeted sandbox suite, with only its WORK_ROOT fixture path mapped to disposable scratch, is **13 passed before / 13 passed after**, using the exact original sandbox bytes for before (reports/w-netroute-native-offline-route-validation.txt:221; reports/w-netroute-native-offline-route-validation.txt:227; wrapper at reports/w-netroute-native-offline-route-validation.txt:721).

FOUND: all requested inherited suites and all named-code matches, with that fixture path supplied and only the two disclosed isolation conditions deselected, finish **253 passed, 2 skipped, 2 deselected** (reports/w-netroute-native-offline-route-validation.txt:212). The two skips are the inherited tests requiring a read-only outer guard; the raw invocation did not provide it (tests/quality/test_runtime_blocker_evidence_b7.py:57-69). ABSENT: modifications to any inherited test assertions, searched by the exact enumerated `git diff -- <11 inherited suite paths>` command with empty output (reports/w-netroute-native-offline-route-validation.txt:233).

FOUND: `python3 tools/check_dataset_blockers.py` returns exactly `{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}` (reports/w-netroute-native-offline-route-validation.txt:270). ABSENT: edits in the enumerated scope AGENTS.md, registry/dataset-blockers.json, docs/adapter-integration-journal.md, base_harness, eval/containers/immutable_runtime.py and eval/containers/container.py, by the recorded `git diff --` command (reports/w-netroute-native-offline-route-validation.txt:233). No registry proposal is needed for this transport-only change; the checker still refuses production authorization. Cleanup checks report every named worker pytest basetemp and fixture directory absent (reports/w-netroute-native-offline-route-validation.txt:270).

UNKNOWN / not verified: real generation and live SDK/streaming behavior; no dataset, benchmark, official scorer, pilot or production H0 was run. The real endpoint proof is metadata-only; the runner proof uses a synthetic provider. This is the main uncertainty for review (reports/w-netroute-native-offline-route-validation.txt:764). HTTP URLs containing TLS/userinfo/query/fragment semantics are explicitly refused, not silently downgraded (eval/service/native_model_route.py:56-64).

Changed line ranges (new-file coordinates; deleted native refusal was old lines 15-19):

- INTERFACE.md:824-825,831-839.
- eval/containers/sandbox.py:72,81,184-185,378-390,436-437,456.
- eval/policy/runtime_policy.py:11-18 (old live-backend refusal removed).
- eval/run/runner.py:17,196-197,444-453,520-523,539-540.
- eval/containers/model_route.py:1-35 (new).
- eval/service/native_model_route.py:1-109 (new).
- eval/service/native_model_forwarder.py:1-65 (new).
- tests/quality/test_native_model_route.py:1-214 (new).
- tests/quality/native_model_route_control.py:1-95 (new).
- This report and its standalone validation file: all lines (new).

Exact source hashes, commands, failed attempts, outputs, and committed file sizes are retained in reports/w-netroute-native-offline-route-validation.txt; source hashes start at reports/w-netroute-native-offline-route-validation.txt:759.
