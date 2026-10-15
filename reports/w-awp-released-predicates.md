# AppWorld released evaluator predicates - w-awp

**732 released task-specific `evaluate` entrypoints exist; 3/732 exercised offline on nine controlled inputs. Official and local TGC agree 9/9, with zero numeric or tracker divergences. No blocker closes.**

Baseline `48c2848afa0daff71713bbcd807debc7350be831`, registered worktree `/tmp/hg-awp`, branch `wg-awp`. Read `AGENTS.md`, the requested five context sources and the prior AppWorld evidence/scripts. This is bounded scorer-component execution, not a benchmark scoring run, actor-task success, production verifier admission or pilot authorization. No production adapter/scorer/gate changes, model/GPU/endpoint calls, `runs/` access or frozen-receipt changes occur.

## Released inventory and actual reachability

All packet-relative paths below are under `tests/fixtures/hg_wawp/`. `prepare.py` decrypts the **actual provisioned** `/mnt/20t/xubuqiang/datasets/appworld/_src/data-0.1.0.bundle`, inventories ZIP members, parses each released `evaluation.py` and hashes the original bytes. Fresh bundle SHA-256: `fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250`. `inventory.json` retains member paths, file sizes, exact `evaluate` line numbers, split and recomputed bundle/image file hashes for every task. `prepare-v2.stdout.txt`, `inventory-summary.json` and `document.stdout.txt` retain raw/derived counts.

The release contains **732 `ground_truth/evaluation.py:evaluate` entrypoints**, one per task: train 90, dev 57, test_normal 168, test_challenge 417. There are **226 distinct evaluation.py byte digests**, not 732 different implementations. All 732 members exist in the verifier image and **732/732 original bytes match**; missing members and bundle/image mismatches are both **0**. This establishes local bundle-to-image byte correspondence, not newly acquired independent remote provenance.

`reachability.json` is the complete per-task inventory with final execution status and reasons. Only the following three are dynamically demonstrated reachable; static presence does not imply the others load or run successfully:

| Released identity (bundle member under `data/tasks/`) | Split | Released checks | Reachability |
| --- | --- | --- | --- |
| `82e2fac_1/ground_truth/evaluation.py:18`, `evaluate` | train | Answer comparison; no model changes | Executed official + local, all three controls |
| `50e1ac9_1/ground_truth/evaluation.py:18`, `evaluate` | dev | Order-insensitive normalized song-title comparison; no model changes | Executed official + local, all three controls |
| `cf6abd2_2/ground_truth/evaluation.py:18`, `evaluate` | train | Answer plus seven simple_note.Note change/record/field checks | Executed official + local, all three controls |

The predicates are **unchanged released files**, retained verbatim in `selected-root/data/tasks/<id>/ground_truth/evaluation.py`; no authored predicate, mock model collection or replacement tracker is used. Selection is bounded and stated before execution in `inputs.json`: first released train task, first released dev task, and the prior mounted-service train task. No released solution/API-call oracle is staged or executed. All gold/task content staged here is study-side; held-out content is limited to inventory identity/hash metadata.

## Recomputed predicate and gold identities

The SHA-256 values below were recomputed from the actual archive members and staged bytes. `gold-identities.json` retains all six original ground-truth files for each selected task (`evaluation.py`, `answer.json`, `private_data.json`, `public_data.json`, `test_data.json`, `metadata.json`) with byte lengths and hashes. `selected-byte-pins.json` also binds task specs, task DB deltas, shared API docs, version and base databases to archive/image/host bytes: **104 members, 139990861 bytes, 104/104 matching**. The 13 large shared base-DB members remain external, mounted read-only at `/base-dbs`; their absolute host paths and hashes are recorded and independently rechecked. The other 91 selected/shared members are included in this packet. This packet is not a portable complete image/dependency export.

| Task | Released evaluation.py SHA-256 | Released answer.json SHA-256 |
| --- | --- | --- |
| `82e2fac_1` | `66b1f382e038d71d35ef80799922303236568b755315cde514c1727ec4ee5496` | `9e51f1611c70c853f26161cd290d769f4cc6814527fdfe8ba1f263b043413f57` |
| `50e1ac9_1` | `047963fcd71ed0d71ea747aa5e9713933758c22c929d7f23f8a6e03766eb890d` | `2efb882e1dd53a0191bb4571e46bba4b76511bf97b0f18b7cdf36df32fc7b9b8` |
| `cf6abd2_2` | `0a1187c3e72dd9e33c2be0be8052563ad15803a23ff235a483df9628a4c72524` | `74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b` |

The installed distribution is `appworld 0.1.3.post1`; `runtime-source-pins.json` binds the installed evaluator, environment, task and ground-truth loader. Actual image for every execution is the already-local pinned verifier `sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca`. The separate actor/service images were not run. `local-source-pins.json` and each execution receipt recompute unchanged local `data/datasets/appworld/verify/check.py` SHA-256 `0271f08e42199bcc417222b896979408161392743271d5d9479983d4602a0ca5`.

## Exact execution commands and offline envelope

Exact preparation commands and stdout/stderr locations are in `preparation-commands.txt`. The final scoring collector was invoked exactly as:

```sh
python3 tests/fixtures/hg_wawp/execute.py > tests/fixtures/hg_wawp/execute-final.stdout.txt 2> tests/fixtures/hg_wawp/execute-final.stderr.txt
python3 tests/fixtures/hg_wawp/compare.py > tests/fixtures/hg_wawp/compare.stdout.txt 2> tests/fixtures/hg_wawp/compare.stderr.txt
python3 tests/fixtures/hg_wawp/validate.py
python3 tests/fixtures/hg_wawp/document.py > tests/fixtures/hg_wawp/document.stdout.txt
```

`execution-commands.json` records **every exact Docker command**, container name, case and mode; `commands-exact.txt` includes both preserved attempts as well. For each case, Docker creates a fresh container with `--pull=never --network none --read-only`, read-only fixture, local-check and base-DB binds, `/tmp` tmpfs 512 MiB, masked read-only `/appworld`, one CPU, 2 GiB RAM, 128 PIDs, CPU rlimit 120 seconds, NOFILE 256 and empty `CUDA_VISIBLE_DEVICES`. The collector allows 150 wall-clock seconds per attach, one container at a time. Actual pre/post `docker inspect` is retained. There are no GPU/device requests or model bindings.

Inside each container the precise child command is `python /fixture/run_case.py <official|local> <case-id>`. It verifies that only loopback exists and the route table has no routes; an external connect probe fails `ENETUNREACH` (errno 101) in every final receipt. This is Docker network-namespace isolation, allowing the installed in-process FastAPI/TestClient runtime; it is not a claim of socket-syscall denial. `run_case.py` stages a fresh selected root and sets `APPWORLD_ROOT`; masked `/appworld` prevents unchanged local check from rebinding to the image's unrestricted task tree.

Official mode directly invokes authentic `world.requester.post('/supervisor/message', data=..., client=world.requester.client)` for submitted calls, then authentic **`appworld.evaluator.evaluate_task(task_id, experiment_name='wawp')`**. Local mode executes the **actual read-only bound production check**, via `runpy.run_path('/adapter/check.py', run_name='__main__')`, with exact argv retained in `run_case.py`: task ID, source split, the same JSONL input, reward and evidence files. It replays through unchanged `world.execute` and calls `world.evaluate()`. Thus this tests direct-request vs local execute-string replay around the same installed released scorer, not two independently implemented metrics.

A passive Python call profiler records the actual released `evaluate` file, symbol and first line; **nine official and nine local released-predicate invocations** are retained in raw stderr. It changes no scoring function. Every receipt binds the input, local-check and selected predicate hashes. Validation verifies JSONL calls equal the official input calls. Raw stdout/stderr/return codes are in `raw/<case-id>/<official|local>/`; exact extracted reward/evidence/result bytes and parsed receipts are in `outputs/`. `SHA256SUMS` covers the packet. `cleanup.json` records all **18 final containers removed and absent**, and raw child cleanup receipts confirm scratch absence. Four earlier attempt containers have separate removal/absence receipts. These are collector-owned controls, not production lifecycle enforcement evidence.

## Same-input results and findings

`inputs/*.jsonl` contains each controlled submission. `no-calls` is empty; `wrong-answer` submits the authored sentinel `HG_WAWP_WRONG_SENTINEL`; `gold-answer-only` submits the released `answer.json` value via the public completion API, without carrying out the task's application edits. Gold injection is an explicit scorer positive/boundary control and is **never actor success evidence**.

| Released predicate | Input | Official TGC | Local TGC | Official/local passes / failures |
| --- | --- | --- | --- | --- |
| `82e2fac_1` | no-calls | 0.0 | 0.0 | 1 / 1, both |
| `82e2fac_1` | wrong-answer | 0.0 | 0.0 | 1 / 1, both |
| `82e2fac_1` | gold-answer-only | 1.0 | 1.0 | 2 / 0, both |
| `50e1ac9_1` | no-calls | 0.0 | 0.0 | 1 / 1, both |
| `50e1ac9_1` | wrong-answer | 0.0 | 0.0 | 1 / 1, both |
| `50e1ac9_1` | gold-answer-only | 1.0 | 1.0 | 2 / 0, both |
| `cf6abd2_2` | no-calls | 0.0 | 0.0 | 1 / 7, both |
| `cf6abd2_2` | wrong-answer | 0.0 | 0.0 | 1 / 7, both |
| `cf6abd2_2` | gold-answer-only | 0.0 | 0.0 | 2 / 6, both |

Final counts from `comparison.json`: **9 controlled inputs, 9 numeric comparisons, 9 agreements, 0 divergences; 9 exact tracker agreements, 0 tracker divergences; 0 final official route failures/nonzero exits, 0 local nonzero exits, 0 official/local unmeasured.** Both routes execute **36 requirement checks: 12 passes, 24 failures**. These are requirement-level predicate failures, not 24 infrastructure errors or 24 task measurements. There are two positive scorer controls per route, no successful measured actor-task receipt.

Findings and preserved limitations:

- Gold-answer-only passes the two answer-only predicates but fails the note-edit predicate. It supplies the correct null answer while leaving the required note edit absent. Its six failures include no changed `simple_note.Note`, no single updated note, and four subsequent updated-note checks. The released tracker retains those four as failures with code context but no exception-detail text; no invented exception type is assigned. No numeric or tracker disagreement was found on these controls.
- **First attempt** (`preserved-first-attempt/`): both children fail before scorer loading with `FileExistsError` at the fixture's base-DB symlink. Initial staging had left a real base-DB directory. Raw outputs, collector scripts, commands and cleanup survive. The duplicate staged directory was removed, keeping the read-only external base-DB bind; no released or adapter bytes changed. These failures are not scored zero.
- **Second attempt** (`preserved-second-attempt/`): the official no-call predicate completes and emits reward 0.0, then the collector exits 1 with `Exception: 0`; local completes exit 0. Installed `SafetyGuard.__init__` assigns `builtins.SystemExit = Exception`. The collector now captures the original SystemExit class before AppWorld construction, uses it for its own exit/catch and leaves upstream safety behavior intact. Raw failed official exit is retained, not counted as a valid final numeric comparison or replaced with zero. This is a collector exit-handling finding.
- Host `tests/fixtures/hg_wclo_runtime/datasets/appworld.json`, referenced by the earlier closure report, is absent in this checkout. No old inventory/hash was trusted: the bundle, image files, selected gold and host base-DB bytes were freshly inspected and recomputed here.
- No selected predicate is absent, unloadable or dependency-blocked in the final pinned-image profile. The other 729 are **unexecuted**, not asserted reachable or failing. Error/timeout paths beyond the preserved fixture failures, arbitrary API/state equivalence, broad task semantics and production service/recording isolation remain untested.

## Coverage and closure boundary

**Coverage is exactly 3/732 released task evaluator entrypoints**, with three distinct file digests out of 226. Remaining: **729**, comprising train **88**, dev **56**, test_normal **168**, test_challenge **417**. The 144 unselected study predicates are outside this bounded control set; all 585 held-out predicates are excluded from execution. Every identity and reason is listed in `reachability.json`; no dynamic result is inferred from a static file/hash match.

This supersedes only the earlier statement that AppWorld had no released-predicate execution at all. It does not execute the remaining AppWorld predicates, BFCL/ChessBench complete routes or additional Terminal-Bench tasks. Complete execution-selected offline/transitive runtime/image/ABI/provenance custody, selected-input/lifecycle enforcement and valid production live controls remain unmet. **S1, S3, S4 and S6 remain PARTIAL; `scorer-offline-closure` stays open.** All dataset blockers, including `appworld / successful-task-evidence`, stay unchanged. Gates/statuses/next_actions/history and `production_authorized=false` remain unchanged.

Validation: all 583 SHA-256 manifest members pass, the packet validator passes, the blocker registry remains valid with production authorization false, and all 56 focused registry tests pass. Exact commands and output are in `reports/w-awp-validation.txt`.
