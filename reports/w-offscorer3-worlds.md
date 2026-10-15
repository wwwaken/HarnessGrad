# ALFWorld and AppWorld official generic execution - w-offscorer3-worlds

S4 gains bounded offline execution of complete installed upstream ALFWorld evaluation and AppWorld generic evaluation/replay components. **S1, S3, S4 and S6 remain partial; no blocker is closed.** AppWorld's task-specific predicate in this packet is authored fixture code, **not a released official task evaluator**. This distinction limits its new evidence to authentic generic scoring machinery, rather than released task-scoring equivalence.

Packet root: `tests/fixtures/hg_woffscorer3/worlds/`. Baseline: `9f78bcd`; isolated registered worktree `/tmp/hg-offscorer3-worlds`. Previous method packets `reports/w-offscorer-equivalence.md` and `reports/w-offscorer2-coverage.md` were read first. Inputs are wholly authored; no released benchmark task, heldout input, oracle walkthrough, model, GPU, endpoint or production runner executes. Production adapters and scorers remain unchanged. These are scorer controls, not measured benchmark scores or H0 authorization.

## Commands, raw custody and boundaries

Exact final replay, executed at repository root:

```bash
bash -x tests/fixtures/hg_woffscorer3/worlds/commands.sh > tests/fixtures/hg_woffscorer3/worlds/commands-output.txt 2> tests/fixtures/hg_woffscorer3/worlds/commands-exact.txt
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer3/worlds/verify.py
python3 tools/check_dataset_blockers.py
```

`commands.sh` and expanded `commands-exact.txt` retain every argument, bound, image identity and path. `alfworld-official.json` / `alfworld-local.json` preserve raw results, actual native observations, per-case stdout/stderr and exceptions. AppWorld official/local JSON retain child argv, exit codes, exact stdout/stderr, network receipts, native API responses and complete tracker/evidence values. `comparison.json` derives per-input joined outcomes and counts. `SHA256SUMS` is freshly computed across retained packet bytes; `verify.py` recomputes every listed hash and source/controlled-archive equality. Exact validation/checker output is `reports/w-offscorer3-worlds-validation.txt`.

ALFWorld uses an unchanged copy of the earlier kernel seccomp `offline_exec.py`, which closes inherited socket descriptors and actively tests AF_INET, AF_INET6 and AF_UNIX denial. Native Fast Downward inherits syscall denial. Guard receipts record interpreter/libseccomp hashes, 120 CPU seconds, 256 FDs and no attempted external dataset payload reads. Each side has a 150-second wall bound.

AppWorld runs in the already-local pinned verifier image with `--network none`, read-only root, bounded private `/tmp`, one CPU, 1 GiB memory, 128 pids, 120 CPU seconds, 256 FDs and a 150-second wall bound per side. All released `/appworld` data is hidden by a read-only empty tmpfs during scoring; only the fixture archive's authored task is loaded. The network receipt checks `lo` as the sole interface, no IPv4 routes, and a failed external IP connection. Local IPC is allowed for actual FastAPI/Starlette test-client activity; this is offline, not socketless. Every case uses a fresh child interpreter and fresh external `/tmp/hg-woffscorer3-appworld-*` root. Child exits are awaited, scratch deletion is recorded, and post-execution named-container inspection fails with `no such object` in each `appworld-*-cleanup.txt`, confirming automatic removal. These fixture receipts do not establish production trusted custody, quota, snapshot lifecycle or transitive image closure.

The preparation script builds SQLite schemas through actual `ModelCollection.load(..., create_db=True)` and adds only a synthetic user, supervisor and task. It copies public API docs, no task directory. Exact acquisition/preparation command (executed before final scoring):

```bash
docker run --rm --network none --read-only --tmpfs /tmp:rw,nosuid,size=256m --cpus 1 --memory 1g --pids-limit 128 --ulimit cpu=120:120 --ulimit nofile=256:256 -e PYTHONDONTWRITEBYTECODE=1 -e CUDA_VISIBLE_DEVICES= -e HG_IMAGE=sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca --mount type=bind,src=/tmp/hg-offscorer3-worlds/tests/fixtures/hg_woffscorer3/worlds,dst=/output --entrypoint python sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca /output/prepare_appworld.py > tests/fixtures/hg_woffscorer3/worlds/appworld-prepare.json 2> tests/fixtures/hg_woffscorer3/worlds/appworld-prepare.stderr.txt
```

## Installed official identities

Version+byte custody does not authenticate a published Git commit or wheel acquisition. `upstream_git_revision` is null. Complete installed modules genuinely import and execute; there is no AST-selected scorer or reimplemented official reduction here. Metadata/WHEEL/RECORD identities and selected exact source copies are retained in `*-identities.json` / `source/`. The AppWorld source-inspection text files preserve additional full original source reads; they are not used as replacement modules.

| Component | Actual installed identity | Recomputed source SHA-256 |
| --- | --- | --- |
| ALFWorld evaluator | `alfworld==0.4.2`, `agents/eval/evaluate_dagger.py` | `d85f9da274eaea9bb2129d55d630f2a3477a4572cdc368c04993ccf152745fcb` |
| ALFWorld domain | installed `data/alfred.pddl` | `f1473041ed01da514de1f87adfd7ef0804862361f83ccf63c75e43633b0eb280` |
| ALFWorld grammar | installed `data/alfred.twl2` | `c5b22f0f73309a7fd7c8e5b71de42ad4803b60766ab4a51cc2feb34162be036b` |
| Native PDDL runtime | installed `fast_downward/libdownward.so` | `eab180829afd721c7a0637d000348694acb75b322f56049b95a9495c8d9ca81b` |
| AppWorld generic evaluator | `appworld==0.1.3.post1`, image installed `evaluator.py` | `4e773fb91cdad3ad10deeacde2d0b1f717454be599e6758419e8e1bb88b75cba` |
| AppWorld runtime | image installed `environment.py` | `ad650588158727c4ebe72a080638ec0174c33af8a8b9e9b81f3d9bfda55d3fd9` |
| AppWorld task loader | image installed `task.py` | `6b74420e30579e27c36cf2ace41f743d3d5f0640af4d15cae13df0419b42d5ea` |

AppWorld image ID is `sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca`; actual `docker image inspect` is retained. Current common authored AppWorld archive SHA-256 is `0ec0c7e565474d437edbd40050a9e0dbb0602629800e49f38e9c2f1e0057db43`. The archive contains only `hgcontrol_1` under `data/tasks/`; validator checks all member digests.

## ALFWorld measured comparisons

Official side invokes unchanged full `evaluate_dagger(env, ScriptedInput(...), num_games=1)`. The supplied agent is a deterministic action-list feeder with no neural model or inference; its observation/preprocessing methods pass strings through. The environment is actual installed TextWorld/PDDL with authentic `AlfredDemangler` and `AlfredInfos`. Authored PDDL problem asks the agent to hold one apple; installed domain/grammar are unchanged. Native reset, action responses, `won` and `done` flags are retained. Local side calls unchanged `data/datasets/alfworld/verify/check.py:main(argv)` with unchanged `gym_env.py`, rebuilding a fresh native world from the same game and actions.

Both sides share the maximum environment budget of four and exact action bytes. The upstream scripted-agent loop horizon is `min(len(actions), budget)`, because an exhausted input supplies no further action; local `main` receives budget four and replays only available actions. These caller configurations are not identical for short/empty traces. In particular, empty horizon zero is an explicit API boundary control, not an ordinary official episode or numeric divergence.

| Input | Official result | Local reward | Outcome |
| --- | --- | --- | --- |
| `take-win` | 1.0 | 1.0 | agree |
| `look-no-win` | 0.0 | 0.0 | agree |
| `invalid-no-win` | 0.0 | 0.0 | agree |
| `win-then-invalid` | 1.0 | 1.0 | agree |
| `budget-truncation` | 0.0 | 0.0 | agree |
| `empty` | `ValueError` | 0.0 | nonnumeric caller boundary |

**Six controlled inputs, five numeric comparisons, five numeric agreements, zero numeric divergences, one official exception, zero local unmeasured.** The exception is `zero-size array to reduction operation maximum which has no identity` at official `np.max(sequence_game_points)` with zero upstream loop steps. No score is filled in. `win-then-invalid` also exposes a legitimate execution-policy difference: upstream executes an additional step after `done` before its prior-done mask stops the loop; local stops at first done. Final binary outcomes agree on this input. Positive controls are actual native goal satisfaction, not fixture-supplied `won` flags. This covers authored single-goal replay and full evaluator reduction, not released ALFWorld tasks, six task-family breadth or general equivalence.

## AppWorld measured comparisons

Official side imports complete authentic AppWorld and directly invokes the authentic requester methods on a fresh `AppWorld`, then calls unchanged `appworld.evaluator.evaluate_task`. Local side executes a byte-identical copy of unchanged production `verify/check.py:main`, which replays the same URL/method/data calls through `world.execute` and obtains `world.evaluate`. The byte copy is verified against current production source. No fake world, requester, model collection or tracker stands in for upstream.

The input task has a **wholly authored `ground_truth/evaluation.py`**, calling actual official `test.answer` to compare its supervisor-task stored answer against authored target `42`. This executes generic official `evaluate_task`, ground-truth loader, `TestTracker`, answer normalization, API replay and TGC success plumbing. It **does not execute any released task's evaluation predicate**, prove original task-score correctness, authenticate released-task provenance, or close AppWorld S4.

| Input | Official generic TGC | Local replay TGC | Outcome |
| --- | --- | --- | --- |
| `correct-answer` | 1.0 | 1.0 | agree |
| `wrong-answer` | 0.0 | 0.0 | agree |
| `no-calls` | 0.0 | 0.0 | agree |
| `numeric-answer` | 1.0 | 1.0 | agree |
| `wrong-then-correct` | 1.0 | 1.0 | agree |
| `invalid-api` | 0.0 | 0.0 | agree |

**6 controlled inputs; 6 numeric comparisons; 6 agreements, 0 numeric divergences; 0 final official exceptions; 0 final local unmeasured.** Counts are common-input generic-workflow outcomes, not released-task scorer equivalence.

## Preserved fixture/import/execution failures

No failed receipt is substituted with zero or overwritten without a preserved copy.

- Host Python package discovery found no installed `appworld`; complete upstream import instead succeeds in the already-local pinned verifier image. This is an image-installed execution profile, not a new host dependency closure.
- `appworld-preserved-first-attempt/` retains six actual `TypeError: object of type 'NoneType' has no len()` failures in `GroundTruth.__init__` because authored minimal metadata omitted required count metadata. The fixture metadata was completed; no upstream code changed.
- `appworld-preserved-second-attempt/` retains the first successful correct-answer followed by five missing-DB-root failures: official cached home-path helpers retained the previous deleted scratch root in a shared process. Fresh child interpreters per case remove that fixture cross-case state; this is not a production cache-lifecycle diagnosis.
- `appworld-preserved-third-attempt/` retains six local unmeasured missing-task failures when unchanged local check detected installed `/appworld/data` and rebound away from the controlled root. Final scoring hides bundled `/appworld` entirely so the unchanged check respects its authored `APPWORLD_ROOT`; no original dataset is exposed.
- `appworld-preserved-fifth-attempt/` retains five local `io.UnsupportedOperation: fileno` failures at authentic `safety_guard.disable()` followed by an `AttributeError` when its still-patched `SystemExit` alias caught that exception. Fixture `StringIO` capture lacks the real file descriptor required by `faulthandler.enable`; final capture uses real `tempfile.TemporaryFile` descriptors. This fixes the capture harness and allows authentic upstream safety restoration; no safety function is disabled or replaced. The failed per-case scratch deletions remain explicit; automatic container removal removes their private tmpfs.
- `appworld-preserved-fourth-attempt/` retains five local child serialization failures (`TypeError: object supporting the buffer API required`) after genuine `world.execute` left safety patches affecting the fixture's late `Path.read_bytes` call. No-calls child completed normally. The fixture now computes digest bytes before upstream execute; this permits unchanged scoring and captures raw evidence without changing or disabling upstream safety behavior. The failed command log and child stderr are retained.

This packet adds no execution for BFCL, ChessBench, GAIA, LiveCodeBench or Tau-Bench; parent integration may include their independent packets. Terminal-Bench retains its **partial** existing one-task official `bash /tests/test.sh` evidence from `reports/w-net-receipts.md`, not broadened by these controls. AppWorld released task-specific evaluator execution remains outside this packet even if its generic workflow runs successfully. S1, S3, S4 and S6 remain partial.
