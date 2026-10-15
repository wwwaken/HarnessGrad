# w-taubench: service-owned communication and termination evidence

FOUND: the adapter can use the existing §2.5.7 service contract without a platform change. It now declares a bounded `tau` service with `record: True`, `needs_model: False`, and the service source in its command. The HTTP client is staged as `./tau`; the verifier explicitly reads `/recordings/tau/episode.json`. Source: `data/datasets/tau_bench.py:186`, `data/datasets/tau_bench.py:336`, `data/datasets/tau_bench.py:354`. The platform excludes recordings from the harness and mounts them read-only in the verifier: `eval/service/services.py:491`; the documented contract is `INTERFACE.md:708`. The existing AppWorld declaration/consumer provided the pattern: `data/datasets/appworld.py:285`, `data/datasets/appworld.py:323`.

The service owns the database and accepted events together and publishes an atomic JSON snapshot. It fixes the task/domain from platform `HG_ENV_TASK_ID`, loads the domain's image assets, and exposes only tool calls, says, done, and read-only discovery. It accepts no client-provided recording/database path, task selector, reset or executable code. Source: `data/datasets/tau_bench/service.py:32`, `data/datasets/tau_bench/service.py:46`, `data/datasets/tau_bench/service.py:92`, `data/datasets/tau_bench/service.py:125`. This is a source-level action-surface claim; real container isolation remains UNKNOWN below.

The original ground-truth replay, terminating-action skip, database hashing, section comparison and output substring rule remain in the checker. Its database source is now the service recording. A valid unfinished episode earns zero; an unavailable, malformed or differently task-bound recording exits 3 without a reward. Source: `data/datasets/tau_bench/verify/check.py:139`, `data/datasets/tau_bench/verify/check.py:212`, `data/datasets/tau_bench/verify/check.py:248`, `data/datasets/tau_bench/verify/check.py:259`. The positive/negative mutation control exercises the real staged hash functions with fake tools: `tests/quality/test_tau_bench_recording_w_taubench.py:148`.

Both explicit done and `transfer_to_human_agents` end the episode. The service freezes its state and rejects subsequent calls/messages; the checker stops accumulating events at the first termination. Source: `data/datasets/tau_bench/service.py:47`, `data/datasets/tau_bench/service.py:61`, `data/datasets/tau_bench/service.py:69`, `data/datasets/tau_bench/verify/check.py:97`. The schema rejected my initial service declaration with `state="container"`; the adapter now uses supported `state="mount"`, because its database belongs to the service. The intermediate failure and corrected results are retained in `registry/w-taubench-validation.txt:144`; the platform restriction is `data/scaffolds/registry.py:342`.

FOUND, exact synthetic observations: the complete original checker was extracted from observed base `5e5441cc48f3ce79390895f8159e0666ff944587`. The control supplies an unchanged synthetic database and fabricated local JSONL, while the service recording has no required utterance. Original stdout was:

> reward 1: database hash matches the ground truth (c53430b91485..., 0 actions replayed), the agent declared done, and all 1 required output(s) were said

Fixed stdout was:

> reward 0: required output(s) not said: ['confirmed']

Both observations report `database_hash_matched: true`. The same complete-checker differential gives terminating tool **0 → 1** and post-done utterance **1 → 0**; accepted event count for post-done changes **3 → 1**. Exact command and all six losslessly encoded JSON observations: `registry/w-taubench-validation.txt:257`. Fixture construction: `tests/quality/test_tau_bench_recording_w_taubench.py:278`. These are authored recorded-service controls, never released-task scores. The shipped CLI also talks to a real local HTTP server with fake tools, including refused post-termination and reset requests: `tests/quality/test_tau_bench_recording_w_taubench.py:203`.

FOUND: service/verifier suites before **48 passed, 20 skipped**; final new tau suite plus those same suites **66 passed, 20 skipped**. Exact outputs: `registry/w-taubench-validation.txt:141`, `registry/w-taubench-validation.txt:240`. The runner blocks unmocked Docker calls, supplies an explicitly synthetic digest for service metadata tests, and skips lifecycle and real sandbox cases: `tests/fixtures/tau_bench_w_taubench_runner.py:1`. This is controlled unit coverage, not a claim that the unmodified container suites passed. Additional tau image-declaration cases: **3 passed, 3 deselected** (`registry/w-taubench-validation.txt:254`). The initially incorrect `-k tau_bench` selection ran zero tests and is preserved immediately before its correction.

ABSENT in an enumerated scope: no pre-existing tau-named suite under `tests/quality` at the observed base. Exact `git ls-tree ... | rg '/[^/]*tau[^/]*$'` command, empty output and exit 1: `registry/w-taubench-validation.txt:132`. ABSENT locally: `data/datasets/tau_bench/db` (`local_clean_db_directory_exists=False`, `registry/w-taubench-validation.txt:321`). It was not restored or downloaded.

FOUND custody identity: original checker SHA-256 `b2cad46a3f541eae927334961a76c91c79e3dbb730b5016f0dc325a544dad6ec`; new staged Git blob SHA-256 `5298bbb2b39629ed25704f6113e58232bb2db8946b6b677a082ffc7b44e0c38e`. Exact Git-blob hashing command/output: `registry/w-taubench-validation.txt:303`. The same blob is committed by this worker; the final response reports the post-commit hash check. ABSENT over exactly `registry/dataset-blockers.json`: checker path, old hash and new hash literal pins; its tau row has no blocker/evidence hash (`registry/w-taubench-validation.txt:319`). Historical custody artifacts are preserved; an old hash remains in `tests/fixtures/hg_migration_site/jericho-runtime-b7.json:4974`. Pins outside the explicitly searched active registry file are UNKNOWN.

FOUND checker output (`python3 tools/check_dataset_blockers.py`):

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

Exact command/output: `registry/w-taubench-validation.txt:268`. The task changes no active registry, journal, AGENTS.md or platform file; the protected-path diff is empty (`registry/w-taubench-validation.txt:324`). Only the two explicitly requested standalone registry deliverables are added.

UNKNOWN, principal review target: actual execution of the service-command/client/recording path in the declared existing image, including its database/library/policy bytes, service UID permissions and real verifier mount. No image inspection, build, pull, container start/stop, model/GPU access, benchmark rerun, selected-task trial or production authorization was performed. The synthetic controls cannot close that runtime uncertainty. Full exclusions and committed byte sizes are in `registry/w-taubench-validation.txt:348`.
