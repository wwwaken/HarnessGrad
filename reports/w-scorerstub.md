# w-scorerstub: materialize declared scorer inputs in direct test runners

FOUND: the three requested file-level baselines and final runs completed separately. Exact shell bodies, exit statuses and complete pytest output are in the validation transcript.

- ALFWorld before: `3 failed, 2 passed in 20.83s`; after: `5 passed in 24.44s` (reports/w-scorerstub-validation.txt:5; reports/w-scorerstub-validation.txt:301).
- DS-1000 before: `1 failed, 25 passed in 25.05s`; after: `26 passed in 23.09s` (reports/w-scorerstub-validation.txt:110; reports/w-scorerstub-validation.txt:309).
- LiveCodeBench before: `5 failed, 10 passed in 107.91s (0:01:47)`; after: `15 passed in 102.06s (0:01:42)` (reports/w-scorerstub-validation.txt:142; reports/w-scorerstub-validation.txt:317).
- Unchanged BIRD/GAIA suites: `28 passed, 1 warning in 18.74s`; the warning is GAIA's upstream unequal-answer-list warning (reports/w-scorerstub-validation.txt:325).

## Runner repair and real-task evidence

FOUND: ALFWorld now stages every declared input, including the shim, and uses the declared argv with the caller's budget override (`data/datasets/alfworld/control.py:94`). The changed core is:

```python
verifier = alfworld.VERIFY[record["task_id"]]
for entry in verifier["inputs"]:
    target = workdir / entry["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if "content" in entry:
        target.write_text(entry["content"], encoding="utf-8")
    else:
        source = Path(entry["from"])
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)
argv = [sys.executable, *verifier["argv"][1:]]
argv[argv.index("--budget") + 1] = str(budget)
```

The verdict now includes `"stderr": proc.stderr.strip(),` (`data/datasets/alfworld/control.py:122`). Complete before/after source quotes are in reports/w-scorerstub-validation.txt:473.

FOUND: one existing ALFWorld differential test was rerun with an in-memory pytest plugin that prints the actual helper return and its evidence; the plugin does not change scorer inputs or assertions (reports/w-scorerstub-validation.txt:339). Exact observed output:

```text
TASK look_at_obj_in_light-AlarmClock-None-DeskLamp-308__trial_T20190908_222951_616606
RUN_CHECK {
 "actions_replayed": 3,
 "official_game_points": 1.0,
 "returncode": 0,
 "reward": 1,
 "stderr": "",
 "stdout": "reward 1: the goal was satisfied at step 3 of 3 (official game points 1; agent declared done=True)",
 "why": "the goal was satisfied at step 3 of 3",
 "won_at_step": 2
}
MEASURED true
SCORER_INPUT {"expected_sha256": "21a35ce8c25c2e8232a1f4c20a9e6fdac230d30965b0de1c866f0a1bcbbfd25d", "files": {"game.tw-pddl": "2d02e30d98b1ac7022b046157c9a2507e92bb3b64b00d6f43490c8604d20ab0a"}, "path": "native-inputs", "sha256": "21a35ce8c25c2e8232a1f4c20a9e6fdac230d30965b0de1c866f0a1bcbbfd25d", "task_id": "look_at_obj_in_light-AlarmClock-None-DeskLamp-308__trial_T20190908_222951_616606", "verified": true}
SHIPPED_SHIM_MATCH True
.
1 passed in 8.72s
```

The successful shipped check, byte-equal staged shim, and verified receipt establish that `data.scaffolds.scorer_input` resolved in this real task. The win tests now also assert `measured`, `scorer_input.verified`, and the selected task identity (`tests/quality/test_alfworld_official_scorer.py:169`).

FOUND: LiveCodeBench's helper stages `dataset.VERIFY[CONTROL_TASK]["inputs"]` instead of a hand-written dependency list (`tests/quality/test_livecodebench_official_scorer.py:194`). Its hand-written argv is deliberately retained: these scorer unit cases replace the test payload, including an invalid file, so they must exercise the check's manual unbound route rather than assert an unrelated task digest. This reason is documented beside the override (`tests/quality/test_livecodebench_official_scorer.py:201`; manual semantics: `data/scaffolds/scorer_input.py:70`).

## Assertion review

FOUND: scoring expectations, pass/fail tallies, malformed/missing-answer behavior, archive-byte comparisons, and existing gold exclusions are retained in the complete diff (reports/w-scorerstub-validation.txt:473). ALFWorld's `assert reward == 0` becomes `assert reward == 0, detail`, preserving the predicate and exposing failures (`tests/quality/test_alfworld_official_scorer.py:192`).

Two structural assertions intentionally change meaning from rejecting every extra input to requiring all meaningful inputs and their correct sources. Additive platform inputs are now allowed, as requested; metric and privacy predicates are retained or extended. The exact before/after edits are in reports/w-scorerstub-validation.txt:473.

DS-1000 before:

```python
assert paths == {"verify/check.py", "execution.py", "seaborn-data"}
```

DS-1000 after (source mapping defined immediately above):

```python
assert sources.keys() | {"context.json", "data/__init__.py",
                        "data/scaffolds/__init__.py"} <= inputs.keys()
for path, source in sources.items():
    assert inputs[path]["from"] == str(source)
```

This pins the evaluator, execution module, shim, and every `SEABORN_CSVS` source, checks empty package initializers and exact task context, and retains both reference-code exclusion from SETUP and existence checks for every declared `from` (`tests/quality/test_ds1000_official_scorer.py:193`). The obsolete directory entry is replaced by per-CSV requirements, matching the declaration (`data/datasets/ds1000.py:200`).

LiveCodeBench before:

```python
assert set(inputs) == {"verify/check.py", "tests.json", "testing_util.py",
                       "pass_k_utils.py"}
```

LiveCodeBench after:

```python
assert {"verify/check.py", "tests.json", "testing_util.py", "pass_k_utils.py",
        "data/__init__.py", "data/scaffolds/__init__.py",
        "data/scaffolds/scorer_input.py"} <= inputs.keys()
```

The test now checks the exact `from` for all five file-backed inputs, empty package initializers, reference-answer exclusion when a reference exists, and excluded SETUP artifact paths. Existing released-test byte/privacy and task metadata assertions remain (`tests/quality/test_livecodebench_official_scorer.py:112`). Archive-member byte comparisons remain at `tests/quality/test_livecodebench_official_scorer.py:87`.

## Other runners and bounded search results

FOUND: BIRD already copies the shim trio into its two-row synthetic SQLite fixture (`tests/quality/test_bird_minidev_official_scorer.py:175`). Its deliberate synthetic database/gold are why its small hand-written fixture remains; copying a production task's database/gold would change these scorer unit cases. It was left unchanged and its suite passed (reports/w-scorerstub-validation.txt:325).

ABSENT: `scorer_input` or `data.scaffolds` references in the enumerated single-file scope `data/datasets/gaia/verify/check.py`; exact search command, empty output and exit 1 are in reports/w-scorerstub-validation.txt:399. GAIA stages its sibling upstream `scorer.py`, which is the dependency this check uses (`tests/quality/test_gaia_official_scorer.py:111`); its suite passed unchanged (reports/w-scorerstub-validation.txt:325).

FOUND: DS-1000 already copies all declared verifier inputs and sets its workdir import path (`tests/quality/test_ds1000_official_scorer.py:87`). The enumerated runner inventory command/output is in reports/w-scorerstub-validation.txt:406. Command/QA/ScienceWorld/SpreadsheetBench helpers already iterate declared inputs (`data/scaffolds/command_control.py:133`; `data/scaffolds/qa/control.py:147`; `data/datasets/scienceworld/control.py:149`; `data/datasets/spreadsheetbench/control.py:102`); Jericho delegates to the verifier (`data/datasets/jericho/control.py:109`). No claim is made about runtime results for those unrun suites.

UNKNOWN: full repository regression results, arbitrary future input forms, nondefault ALFWorld budgets, and production authorization. The main remaining review question is whether LiveCodeBench's intentionally unbound fixture remains appropriately separated from task-bound control coverage; its retained platform/oracle tests passed in the full file (reports/w-scorerstub-validation.txt:317; `tests/quality/test_livecodebench_official_scorer.py:150`; `tests/quality/test_livecodebench_official_scorer.py:261`).

## Registry and cleanup

FOUND: `python3 tools/check_dataset_blockers.py` returned exactly:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

Evidence: reports/w-scorerstub-validation.txt:392. No registry/journal proposal is warranted for this helper/test repair; the source-only checker inputs are outside the source diff (reports/w-scorerstub-validation.txt:473). All owned `/tmp/scorerstub-*` directories were removed; the enumerated cleanup check returned no paths (reports/w-scorerstub-validation.txt:652). The validation transcript also lists committed file sizes and explicitly unverified work.

The validation transcript intentionally preserves whitespace from verbatim pytest output and the quoted source diff. The staged source/report whitespace check passes; the full staged whitespace check flags only that raw transcript (reports/w-scorerstub-validation.txt:670).
