# w-decode2: platform text-subprocess decoding

Added `errors="replace"` at **57 call sites in 36 production/helper files**. The guard checks **66** text-mode subprocess calls: base_harness 8, eval 11, non-scored data helpers 20, harnessgrad 6, tools 21. Two individually justified strict sites remain. These are observed inventory/audit results, not benchmark measurements. Evidence: `reports/w-decode2-validation.txt:425`; `tests/quality/test_harness_decoding.py:34`.

**The required suites are not all green on this baseline.** Container/services remain 69/69 passing. The direct fast run retains the same nine failures as before: eight sandbox failures with a missing hard-coded sibling work root, plus the pre-existing unclassified `registry/` failure. Supplying an existing private work root outside the repository, with assertions unchanged, yields 56 fast passes and only the registry failure. Evidence: `reports/w-decode2-validation.txt:35`, `reports/w-decode2-validation.txt:313`, `reports/w-decode2-validation.txt:410`.

## FOUND, ABSENT, UNKNOWN

- **FOUND:** worktree baseline `e0c1cd3254e0168c9e9e1a7dabee750772ddc868`, branch `wg-w-decode2`; the reference guard exists in local commit `edf943f95a535d65d935ecfcf05c0ca1b21b2602`. Evidence: `reports/w-decode2-validation.txt:9` and exact source retrieval command `git show edf943f9:tests/quality/test_harness_decoding.py` (the retrieved guard was run unchanged first; `reports/w-decode2-validation.txt:132`).
- **ABSENT:** the guard file in the assigned baseline's **single enumerated path** `tests/quality/test_harness_decoding.py`. Exact command `git ls-tree --name-only e0c1cd3254e0168c9e9e1a7dabee750772ddc868 -- tests/quality/test_harness_decoding.py` returned no stdout, exit 0 (`reports/w-decode2-validation.txt:9`). This commit therefore creates that path using the retrieved guard's shape and extends it.
- **ABSENT:** additional implicit-strict text subprocesses outside the two exceptions in the enumerated Python scopes `base_harness/**/*.py`, `eval/**/*.py`, `data/**/*.py` excluding `data/**/verify/check.py`, `harnessgrad/**/*.py`, `tools/**/*.py`, plus the generated `tools/diagnose_appworld.py:ACTOR` Python source. Exact AST audit source, command and output: `reports/w-decode2-validation.txt:425`; guard scope/count enforcement: `tests/quality/test_harness_decoding.py:89`.
- **FOUND:** all 12 excluded `data/**/verify/check.py` files are byte-identical to both their before-state SHA-256 values and baseline Git blobs. The audit enumerates each path and validates it; protected-path diff output is empty. Evidence: `reports/w-decode2-validation.txt:425`; full observed hash map in [w-decode2-inventory.json](w-decode2-inventory.json). **Every `verify/check.py`, including spreadsheetbench's, was left untouched.**
- **UNKNOWN:** production scorer/runtime behavior with malformed structured stdout, and semantics of replacement bytes inside otherwise valid JSON strings. No production dataset/scorer/model/GPU execution or main-checkout inspection was used for this task; execution evidence and explicit unverified scope are in [w-decode2-validation.txt](w-decode2-validation.txt).

## The two platform judgement calls

`eval/verification/native_runtime.py:118` (**replace**): `FrozenRuntime.run` launches the selected check/control and returns a `CompletedProcess`, including its stdout/stderr. Sealing the executable does not make every dependency diagnostic a platform-authored receipt. The verifier handles authoritative reward/evidence as separate files (`eval/verification/verifier.py:747`), so a stray diagnostic byte should not abort capture before that handling. This patch changes only subprocess stream decoding; it does not relax receipt parsing or scorer custody. Evidence: `eval/verification/native_runtime.py:74`, `eval/verification/native_runtime.py:118`, `eval/verification/verifier.py:747`.

`eval/containers/harness_runtime.py:173` (**stay strict**): stdout is the platform-authored ASCII `X.Y` expression (`eval/containers/harness_runtime.py:143`) and becomes an overlay-cache key (`eval/containers/harness_runtime.py:218`). `_cached_version` already catches exceptions and returns `None` (`eval/containers/harness_runtime.py:124`); malformed host-probe output therefore does not crash the task, and strict decoding avoids storing a substituted version. The image branch at `eval/containers/harness_runtime.py:156` receives replacement decoding because capture also crosses the Docker CLI. Malformed image-version semantics are not newly validated by this one-line patch.

The existing `base_harness/dsh_agent/agent.py:201` strict Node JSON capability probe remains untouched: its exception handler records `probe_error` (`base_harness/dsh_agent/agent.py:208`). Both exemptions live at exact `file:line` keys with written reasons, and the regression test requires each to remain a real strict call (`tests/quality/test_harness_decoding.py:39`, `tests/quality/test_harness_decoding.py:114`).

## Controls and required tests

The actual patched `tools.import_env._run` and `eval.containers.container._run_streaming` calls were given a Python command writing `\xc0\xff` on both stdout and stderr. The strict reference raised `UnicodeDecodeError`; both patched calls returned exit 0, `before\ufffd\ufffdafter\n` and `err\ufffd\ufffd\n`, and both passed a UTF-8 JSON round trip. Exact command source/output: `reports/w-decode2-validation.txt:439`. The new regression controls fail before patching: capture raises a decode exception, and streaming loses stdout; `reports/w-decode2-validation.txt:219`. These controls execute neither Docker nor a scorer (`tests/quality/test_harness_decoding.py:128`).

| Suite/group | Before | After | Evidence |
| --- | --- | --- | --- |
| verifier + sandbox + integrity + parallel_tasks (unmodified environment) | 44 passed, 9 failed | 48 passed, 9 failed, including 4 new decoding tests | `reports/w-decode2-validation.txt:35`; `reports/w-decode2-validation.txt:313` |
| container + services (background runs) | 69 passed | 69 passed | `reports/w-decode2-validation.txt:125`; `reports/w-decode2-validation.txt:403` |
| original retrieved decoding guard | 2 passed | expanded guard and controls: 4 passed within fast run | `reports/w-decode2-validation.txt:132`; `reports/w-decode2-validation.txt:313` |
| expanded guard before source fix | 1 passed, 1 failed | 4 passed including controls | `reports/w-decode2-validation.txt:146`; `reports/w-decode2-validation.txt:410` |
| sandbox with an existing private SSD work root | 13 passed | 13 passed within 56-pass fast run | `reports/w-decode2-validation.txt:139`; `reports/w-decode2-validation.txt:410` |
| fast group with that work root, assertions unchanged | baseline fixture result above | 56 passed, 1 pre-existing integrity failure | `reports/w-decode2-validation.txt:410` |

Current collected counts are verifier 23, sandbox 13, container 26, services 43, decoding 4, integrity 5, parallel_tasks 12: `reports/w-decode2-validation.txt:448`. The unaffected existing suites therefore contribute 122 cases; direct runs preserve all baseline outcomes. No existing quality test/assertion was edited. The scratch plugin only assigns `test_sandbox.WORK_ROOT` to `/tmp/decode2-tmp/sandbox-work-root`; its exact source is in the validation log. It does not skip, mark, xfail or alter assertions.

`python3 tools/check_dataset_blockers.py` returned exactly:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

Evidence: `reports/w-decode2-validation.txt:460`. No registry transition is warranted by this stream-decoding change, and none is proposed. Registry/journal/AGENTS.md and all scored helpers are unchanged (`reports/w-decode2-validation.txt:425`). `git diff --check` produced no stdout and exit 0 (`reports/w-decode2-validation.txt:465`). All `/tmp/decode2-*` scratch was removed after execution (`reports/w-decode2-validation.txt:9`); persistent evidence is retained under `/mnt/20t/xubuqiang/hg-work/decode2/`.

## Full before/after inventory

Every row cites its source site. Calls below are one-line AST renderings (comments/whitespace normalized, arguments preserved), taken from the observed before and after source. `before` is the assigned baseline. The machine-readable companion contains the same 66 rows, output descriptions, policies and strict reasons: [w-decode2-inventory.json](w-decode2-inventory.json). Source scope and count evidence: `reports/w-decode2-validation.txt:425`.

### `base_harness/cli_agent/agent.py:155` → `base_harness/cli_agent/agent.py:155`

Output: task/agent CLI stdout and stderr. Policy: explicit replace → explicit replace.

Before: `subprocess.run(argv, cwd=workdir, env=env, timeout=timeout, input=prompt if use_stdin else None, capture_output=True, text=True, errors='replace')`

After: `subprocess.run(argv, cwd=workdir, env=env, timeout=timeout, input=prompt if use_stdin else None, capture_output=True, text=True, errors='replace')`

### `base_harness/codex_agent/agent.py:102` → `base_harness/codex_agent/agent.py:102`

Output: task/agent CLI stdout; stderr goes to the caller stream. Policy: explicit replace → explicit replace.

Before: `subprocess.Popen(command(workdir, answer), cwd=workdir, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors, text=True, errors='replace')`

After: `subprocess.Popen(command(workdir, answer), cwd=workdir, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors, text=True, errors='replace')`

### `base_harness/dsh_agent/agent.py:201` → `base_harness/dsh_agent/agent.py:201`

Output: platform-authored Node loader-probe JSON on stdout; loader diagnostics on stderr. Policy: implicit strict → implicit strict (exception).

Before: `subprocess.run([node, '--input-type=module', '-e', _LOADER_PROBE_JS], env=probe_env, capture_output=True, text=True, timeout=60)`

After: `subprocess.run([node, '--input-type=module', '-e', _LOADER_PROBE_JS], env=probe_env, capture_output=True, text=True, timeout=60)`

Strict reason: Keep the platform-authored Node loader JSON probe strict; its broad exception handler records a probe_error. This preserves the existing harness exemption without changing base_harness/.

### `base_harness/dsh_agent/agent.py:418` → `base_harness/dsh_agent/agent.py:418`

Output: task/agent CLI stdout and stderr. Policy: explicit replace → explicit replace.

Before: `subprocess.Popen(command(prompt_path, patch), cwd=workdir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace')`

After: `subprocess.Popen(command(prompt_path, patch), cwd=workdir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace')`

### `base_harness/loop/agent.py:684` → `base_harness/loop/agent.py:684`

Output: model-selected shell tool stdout and stderr. Policy: explicit replace → explicit replace.

Before: `subprocess.run([shell, '-c', cmd], cwd=workdir, capture_output=True, text=True, errors='replace')`

After: `subprocess.run([shell, '-c', cmd], cwd=workdir, capture_output=True, text=True, errors='replace')`

### `base_harness/loop_plain/agent.py:241` → `base_harness/loop_plain/agent.py:241`

Output: model-selected shell tool stdout and stderr. Policy: explicit replace → explicit replace.

Before: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, errors='replace')`

After: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, errors='replace')`

### `base_harness/loop_rrsi_parse/agent.py:272` → `base_harness/loop_rrsi_parse/agent.py:272`

Output: model-selected shell tool stdout and stderr. Policy: explicit replace → explicit replace.

Before: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, errors='replace')`

After: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, errors='replace')`

### `base_harness/oracle/agent.py:70` → `base_harness/oracle/agent.py:70`

Output: task oracle shell script stdout and stderr. Policy: explicit replace → explicit replace.

Before: `subprocess.run(['bash', str(script)], cwd=work, capture_output=True, text=True, errors='replace')`

After: `subprocess.run(['bash', str(script)], cwd=work, capture_output=True, text=True, errors='replace')`

### `eval/admission/pilot_admission.py:272` → `eval/admission/pilot_admission.py:272`

Output: Docker CLI payloads (including parsed inspection JSON) and diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['docker', '--host', 'unix:///var/run/docker.sock', *args], env=env, capture_output=True, text=True, timeout=timeout)`

After: `subprocess.run(['docker', '--host', 'unix:///var/run/docker.sock', *args], env=env, capture_output=True, text=True, errors='replace', timeout=timeout)`

### `eval/containers/container.py:230` → `eval/containers/container.py:230`

Output: streamed Docker/task/tool stdout and stderr, drained by two reader threads. Policy: implicit strict → explicit replace.

Before: `subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)`

After: `subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace', bufsize=1)`

### `eval/containers/container.py:277` → `eval/containers/container.py:277`

Output: Docker CLI stdout (including structured inspect metadata) and diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['docker', *args], capture_output=True, text=True, timeout=timeout)`

After: `subprocess.run(['docker', *args], capture_output=True, text=True, errors='replace', timeout=timeout)`

### `eval/containers/container.py:650` → `eval/containers/container.py:650`

Output: containerized task/tool/check stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)`

After: `subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=timeout_s)`

### `eval/containers/harness_runtime.py:156` → `eval/containers/harness_runtime.py:156`

Output: platform-authored interpreter X.Y stdout, parsed as a cache key; Docker/interpreter stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', python, image, '-c', expr], capture_output=True, text=True, timeout=180)`

After: `subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', python, image, '-c', expr], capture_output=True, text=True, errors='replace', timeout=180)`

### `eval/containers/harness_runtime.py:173` → `eval/containers/harness_runtime.py:173`

Output: platform-authored host interpreter X.Y stdout, parsed as a cache key; interpreter stderr. Policy: implicit strict → implicit strict (exception).

Before: `subprocess.run([python, '-c', expr], capture_output=True, text=True, timeout=120)`

After: `subprocess.run([python, '-c', expr], capture_output=True, text=True, timeout=120)`

Strict reason: Keep the platform-authored host interpreter X.Y probe strict. Its stdout becomes an overlay-cache key; _cached_version catches the decode exception and returns None rather than aborting the task or caching a substituted version.

### `eval/containers/sandbox.py:463` → `eval/containers/sandbox.py:463`

Output: sandboxed task/tool/check stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run(wrapped, input=input_text, capture_output=True, text=True, timeout=timeout_s, cwd=cwd, env=env)`

After: `subprocess.run(wrapped, input=input_text, capture_output=True, text=True, errors='replace', timeout=timeout_s, cwd=cwd, env=env)`

### `eval/policy/gaia_snapshot_attestation.py:108` → `eval/policy/gaia_snapshot_attestation.py:108`

Output: Git metadata stdout (commit/tree IDs and file records) and diagnostics; parsed by collect_source. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '--no-replace-objects', '-C', str(repo), '-c', 'core.fsmonitor=false', *args], check=True, capture_output=True, text=True, timeout=30)`

After: `subprocess.run(['git', '--no-replace-objects', '-C', str(repo), '-c', 'core.fsmonitor=false', *args], check=True, capture_output=True, text=True, errors='replace', timeout=30)`

### `eval/run/runner.py:506` → `eval/run/runner.py:506`

Output: unsandboxed harness/task stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s, cwd=workdir, env=child_env)`

After: `subprocess.run(argv, capture_output=True, text=True, errors='replace', timeout=timeout_s, cwd=workdir, env=child_env)`

### `eval/verification/native_runtime.py:118` → `eval/verification/native_runtime.py:118`

Output: sealed check/control stdout and stderr, including diagnostics; authoritative reward/evidence are separate files. Policy: implicit strict → explicit replace.

Before: `subprocess.run(plan, pass_fds=(*self.fds.values(), self.launcher), capture_output=True, text=True, timeout=timeout_s, env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})`

After: `subprocess.run(plan, pass_fds=(*self.fds.values(), self.launcher), capture_output=True, text=True, errors='replace', timeout=timeout_s, env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})`

### `eval/verification/verifier.py:722` → `eval/verification/verifier.py:722`

Output: host check-process stdout and stderr used in verdict detail; reward/evidence files handled separately. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s, cwd=cwd, env=_verifier_env(workdir))`

After: `subprocess.run(argv, capture_output=True, text=True, errors='replace', timeout=timeout_s, cwd=cwd, env=_verifier_env(workdir))`

### `data/datasets/alfworld/control.py:79` → `data/datasets/alfworld/control.py:79`

Output: task action CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, 'alf', 'do', action], cwd=workdir, check=True, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, 'alf', 'do', action], cwd=workdir, check=True, capture_output=True, text=True, errors='replace')`

### `data/datasets/alfworld/control.py:81` → `data/datasets/alfworld/control.py:81`

Output: task completion CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, 'alf', 'done'], cwd=workdir, check=True, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, 'alf', 'done'], cwd=workdir, check=True, capture_output=True, text=True, errors='replace')`

### `data/datasets/alfworld/control.py:108` → `data/datasets/alfworld/control.py:108`

Output: check-process diagnostic stdout and stderr; reward/evidence loaded from files. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, cwd=workdir, capture_output=True, text=True)`

After: `subprocess.run(argv, cwd=workdir, capture_output=True, text=True, errors='replace')`

### `data/datasets/alfworld/oracle_harness/agent.py:41` → `data/datasets/alfworld/oracle_harness/agent.py:41`

Output: task action CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'alf'), 'do', action], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(work / 'alf'), 'do', action], cwd=work, capture_output=True, text=True, errors='replace')`

### `data/datasets/alfworld/oracle_harness/agent.py:48` → `data/datasets/alfworld/oracle_harness/agent.py:48`

Output: task completion CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'alf'), 'done'], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(work / 'alf'), 'done'], cwd=work, capture_output=True, text=True, errors='replace')`

### `data/datasets/appworld/control.py:42` → `data/datasets/appworld/control.py:42`

Output: platform-authored AppWorld probe stdout containing log-directory path, plus dependency diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run([str(AW_PYTHON), str(probe)], cwd=workdir, text=True, capture_output=True)`

After: `subprocess.run([str(AW_PYTHON), str(probe)], cwd=workdir, text=True, errors='replace', capture_output=True)`

### `data/datasets/appworld/control.py:51` → `data/datasets/appworld/control.py:51`

Output: check-process stdout and stderr; reward/evidence loaded from files. Policy: implicit strict → explicit replace.

Before: `subprocess.run(cmd, cwd=workdir, text=True, capture_output=True)`

After: `subprocess.run(cmd, cwd=workdir, text=True, errors='replace', capture_output=True)`

### `data/datasets/jericho/oracle_harness/agent.py:41` → `data/datasets/jericho/oracle_harness/agent.py:41`

Output: task action CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'jer'), 'do', action], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(work / 'jer'), 'do', action], cwd=work, capture_output=True, text=True, errors='replace')`

### `data/datasets/jericho/oracle_harness/agent.py:48` → `data/datasets/jericho/oracle_harness/agent.py:48`

Output: task completion CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'jer'), 'done'], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(work / 'jer'), 'done'], cwd=work, capture_output=True, text=True, errors='replace')`

### `data/datasets/scienceworld/control.py:134` → `data/datasets/scienceworld/control.py:134`

Output: task action CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, 'scw', 'do', action], cwd=workdir, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, 'scw', 'do', action], cwd=workdir, capture_output=True, text=True, errors='replace')`

### `data/datasets/scienceworld/control.py:138` → `data/datasets/scienceworld/control.py:138`

Output: task completion CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, 'scw', 'done'], cwd=workdir, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, 'scw', 'done'], cwd=workdir, capture_output=True, text=True, errors='replace')`

### `data/datasets/scienceworld/control.py:155` → `data/datasets/scienceworld/control.py:155`

Output: check-process diagnostic stdout and stderr; reward/evidence loaded from files. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, cwd=workdir, capture_output=True, text=True)`

After: `subprocess.run(argv, cwd=workdir, capture_output=True, text=True, errors='replace')`

### `data/datasets/scienceworld/oracle_harness/agent.py:41` → `data/datasets/scienceworld/oracle_harness/agent.py:41`

Output: task action CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'scw'), 'do', action], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(work / 'scw'), 'do', action], cwd=work, capture_output=True, text=True, errors='replace')`

### `data/datasets/scienceworld/oracle_harness/agent.py:48` → `data/datasets/scienceworld/oracle_harness/agent.py:48`

Output: task completion CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'scw'), 'done'], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(work / 'scw'), 'done'], cwd=work, capture_output=True, text=True, errors='replace')`

### `data/datasets/spreadsheetbench/control.py:109` → `data/datasets/spreadsheetbench/control.py:109`

Output: check-process diagnostic stdout and stderr; reward/evidence loaded from files. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, *verifier['argv'][1:]], cwd=workdir, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, *verifier['argv'][1:]], cwd=workdir, capture_output=True, text=True, errors='replace')`

### `data/datasets/spreadsheetbench/oracle_harness/agent.py:36` → `data/datasets/spreadsheetbench/oracle_harness/agent.py:36`

Output: task submission CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'qa' / 'bin' / 'qa'), 'submit', 'result.xlsx'], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(work / 'qa' / 'bin' / 'qa'), 'submit', 'result.xlsx'], cwd=work, capture_output=True, text=True, errors='replace')`

### `data/scaffolds/command_control.py:147` → `data/scaffolds/command_control.py:147`

Output: check-process diagnostic stdout and stderr; reward/evidence loaded from files. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, *verifier['argv'][1:]], cwd=workdir, capture_output=True, text=True, env=env)`

After: `subprocess.run([sys.executable, *verifier['argv'][1:]], cwd=workdir, capture_output=True, text=True, errors='replace', env=env)`

### `data/scaffolds/qa/control.py:162` → `data/scaffolds/qa/control.py:162`

Output: check-process diagnostic stdout and stderr; reward/evidence loaded from files. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, cwd=workdir, capture_output=True, text=True, env=env)`

After: `subprocess.run(argv, cwd=workdir, capture_output=True, text=True, errors='replace', env=env)`

### `data/scaffolds/qa/control.py:187` → `data/scaffolds/qa/control.py:187`

Output: task answer-submission CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, f'{base.CLI_REL}/{base.CLI_FILE}', *cli_args], cwd=workdir, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, f'{base.CLI_REL}/{base.CLI_FILE}', *cli_args], cwd=workdir, capture_output=True, text=True, errors='replace')`

### `data/scaffolds/qa/oracle_harness/agent.py:51` → `data/scaffolds/qa/oracle_harness/agent.py:51`

Output: task answer-submission CLI stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(cli), 'submit-json' if structured else 'submit', '@.oracle/prediction.json' if structured else oracle.read_text(encoding='utf-8')], cwd=work, capture_output=True, text=True)`

After: `subprocess.run([sys.executable, str(cli), 'submit-json' if structured else 'submit', '@.oracle/prediction.json' if structured else oracle.read_text(encoding='utf-8')], cwd=work, capture_output=True, text=True, errors='replace')`

### `harnessgrad/methods.py:196` → `harnessgrad/methods.py:196`

Output: method-authored stdout parsed as a JSON response; method stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, cwd=where, input=payload, capture_output=True, text=True, timeout=timeout_s, env=env)`

After: `subprocess.run(argv, cwd=where, input=payload, capture_output=True, text=True, errors='replace', timeout=timeout_s, env=env)`

### `harnessgrad/methods.py:253` → `harnessgrad/methods.py:253`

Output: Git changed-path listing stdout; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(work), 'diff', '--name-only', before, after], capture_output=True, text=True)`

After: `subprocess.run(['git', '-C', str(work), 'diff', '--name-only', before, after], capture_output=True, text=True, errors='replace')`

### `harnessgrad/records.py:399` → `harnessgrad/records.py:399`

Output: Git platform revision stdout parsed as an identity field; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(PLATFORM_ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=10)`

After: `subprocess.run(['git', '-C', str(PLATFORM_ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, errors='replace', timeout=10)`

### `harnessgrad/records.py:406` → `harnessgrad/records.py:406`

Output: Git porcelain status stdout used for dirty-state observation; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(PLATFORM_ROOT), 'status', '--porcelain'], capture_output=True, text=True, timeout=10)`

After: `subprocess.run(['git', '-C', str(PLATFORM_ROOT), 'status', '--porcelain'], capture_output=True, text=True, errors='replace', timeout=10)`

### `harnessgrad/records.py:675` → `harnessgrad/records.py:675`

Output: Git diff and numstat stdout retained as round artifacts; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(work), *args], capture_output=True, text=True)`

After: `subprocess.run(['git', '-C', str(work), *args], capture_output=True, text=True, errors='replace')`

### `harnessgrad/runtime/compat.py:71` → `harnessgrad/runtime/compat.py:71`

Output: legacy method stdout parsed as a JSON response; method stderr retained in events. Policy: implicit strict → explicit replace.

Before: `subprocess.run(self.entrypoint, input=json.dumps(req), text=True, capture_output=True, timeout=self.timeout, env=env, cwd=req.get('cwd') or None, check=False)`

After: `subprocess.run(self.entrypoint, input=json.dumps(req), text=True, errors='replace', capture_output=True, timeout=self.timeout, env=env, cwd=req.get('cwd') or None, check=False)`

### `tools/apply_blocker_proposal.py:234` → `tools/apply_blocker_proposal.py:234`

Output: platform-authored blocker checker JSON stdout and checker diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(CHECKER), '--registry', str(args.registry)], capture_output=True, text=True, cwd=ROOT)`

After: `subprocess.run([sys.executable, str(CHECKER), '--registry', str(args.registry)], capture_output=True, text=True, errors='replace', cwd=ROOT)`

### `tools/build_bird_native_runtime.py:35` → `tools/build_bird_native_runtime.py:35`

Output: closure-build utility stdout/stderr retained as command evidence. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, capture_output=True, text=True, env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})`

After: `subprocess.run(argv, capture_output=True, text=True, errors='replace', env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})`

### `tools/build_tau_bench_gt.py:236` → `tools/build_tau_bench_gt.py:236`

Output: Git checkout revision stdout parsed as identity; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=10)`

After: `subprocess.run(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], capture_output=True, text=True, errors='replace', timeout=10)`

### `tools/configure_harness.py:70` → `tools/configure_harness.py:70`

Output: pip version stdout and Docker/pip diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', python, image, '-m', 'pip', '--version'], capture_output=True, text=True, timeout=180)`

After: `subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', python, image, '-m', 'pip', '--version'], capture_output=True, text=True, errors='replace', timeout=180)`

### `tools/configure_harness.py:182` → `tools/configure_harness.py:182`

Output: overlay-cleanup shell stdout and Docker/shell diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['docker', 'run', '--rm', '-v', f'{overlay}:/out', '--entrypoint', 'sh', image, '-c', 'rm -rf /out/* /out/.[!.]* 2>/dev/null; true'], capture_output=True, text=True, timeout=300)`

After: `subprocess.run(['docker', 'run', '--rm', '-v', f'{overlay}:/out', '--entrypoint', 'sh', image, '-c', 'rm -rf /out/* /out/.[!.]* 2>/dev/null; true'], capture_output=True, text=True, errors='replace', timeout=300)`

### `tools/configure_harness.py:216` → `tools/configure_harness.py:216`

Output: pip installation stdout and Docker/pip diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['docker', 'run', '--rm', '--network', 'bridge', '-u', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp', '-v', f'{overlay}:/out', '-v', f'{req}:/requirements.txt:ro', '--entrypoint', python, pinned, '-m', 'pip', 'install', '--no-cache-dir', '--target', '/out', '-r', '/requirements.txt'], capture_output=True, text=True, timeout=1800)`

After: `subprocess.run(['docker', 'run', '--rm', '--network', 'bridge', '-u', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp', '-v', f'{overlay}:/out', '-v', f'{req}:/requirements.txt:ro', '--entrypoint', python, pinned, '-m', 'pip', 'install', '--no-cache-dir', '--target', '/out', '-r', '/requirements.txt'], capture_output=True, text=True, errors='replace', timeout=1800)`

### `tools/configure_harness.py:269` → `tools/configure_harness.py:269`

Output: platform-authored package-verification probe stdout and Docker/interpreter diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['docker', 'run', '--rm', '--network', 'none', '-v', f'{overlay}:/overlay:ro', '-e', 'PYTHONPATH=/overlay', '--entrypoint', python, pinned, '-c', script], capture_output=True, text=True, timeout=300)`

After: `subprocess.run(['docker', 'run', '--rm', '--network', 'none', '-v', f'{overlay}:/overlay:ro', '-e', 'PYTHONPATH=/overlay', '--entrypoint', python, pinned, '-c', script], capture_output=True, text=True, errors='replace', timeout=300)`

### `tools/datasets.py:229` → `tools/datasets.py:229`

Output: curl stdout/stderr diagnostics; download payload is a separate binary output file. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['curl', '-sSL', '--fail', '--retry', '2', '--max-time', str(timeout), '-o', str(tmp), url], capture_output=True, text=True)`

After: `subprocess.run(['curl', '-sSL', '--fail', '--retry', '2', '--max-time', str(timeout), '-o', str(tmp), url], capture_output=True, text=True, errors='replace')`

### `tools/diagnose_appworld.py:39` → `tools/diagnose_appworld.py:39`

Output: generated actor task CLI stdout/stderr written into trace JSON. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(work / 'aw'), *args], capture_output=True, text=True, timeout=120)`

After: `subprocess.run([sys.executable, str(work / 'aw'), *args], capture_output=True, text=True, errors='replace', timeout=120)`

### `tools/export_harnesses.py:35` → `tools/export_harnesses.py:35`

Output: Git metadata and listing stdout, plus Git diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)`

After: `subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, errors='replace')`

### `tools/export_harnesses.py:134` → `tools/export_harnesses.py:134`

Output: Git blob stdout exported as text; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(work), 'show', f'{sha}:{rel}'], capture_output=True, text=True)`

After: `subprocess.run(['git', '-C', str(work), 'show', f'{sha}:{rel}'], capture_output=True, text=True, errors='replace')`

### `tools/import_env.py:60` → `tools/import_env.py:60`

Output: environment-import utility stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, capture_output=True, text=True, timeout=timeout)`

After: `subprocess.run(argv, capture_output=True, text=True, errors='replace', timeout=timeout)`

### `tools/improver.py:278` → `tools/improver.py:278`

Output: agent CLI version stdout parsed with a version regex; stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run([str(path), '--version'], capture_output=True, text=True, timeout=timeout)`

After: `subprocess.run([str(path), '--version'], capture_output=True, text=True, errors='replace', timeout=timeout)`

### `tools/improver.py:557` → `tools/improver.py:557`

Output: agent smoke-session stdout/stderr parsed for model name and diagnostic tail. Policy: implicit strict → explicit replace.

Before: `subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env, cwd=str(workdir))`

After: `subprocess.run(argv, capture_output=True, text=True, errors='replace', timeout=timeout, env=env, cwd=str(workdir))`

### `tools/merge_blocker_registry.py:31` → `tools/merge_blocker_registry.py:31`

Output: Git blob stdout parsed as registry JSON; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', 'show', ref], capture_output=True, text=True)`

After: `subprocess.run(['git', 'show', ref], capture_output=True, text=True, errors='replace')`

### `tools/run_tests.py:169` → `tools/run_tests.py:169`

Output: pytest stdout/stderr parsed for test summary and retained as logs. Policy: implicit strict → explicit replace.

Before: `subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)`

After: `subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors='replace', env=env)`

### `tools/serve_ui.py:529` → `tools/serve_ui.py:529`

Output: Git diff stdout displayed as patch; Git stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['git', '-C', str(work), 'diff', a, b], capture_output=True, text=True)`

After: `subprocess.run(['git', '-C', str(work), 'diff', a, b], capture_output=True, text=True, errors='replace')`

### `tools/serve_ui.py:881` → `tools/serve_ui.py:881`

Output: platform-authored shell stdout parsed as a listener PID; shell diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run(['bash', '-c', f"ss -ltnp 2>/dev/null | grep ':{target} ' | grep -oP 'pid=\\K[0-9]+' | head -1"], capture_output=True, text=True)`

After: `subprocess.run(['bash', '-c', f"ss -ltnp 2>/dev/null | grep ':{target} ' | grep -oP 'pid=\\K[0-9]+' | head -1"], capture_output=True, text=True, errors='replace')`

### `tools/validate_harness.py:170` → `tools/validate_harness.py:170`

Output: harness smoke stdout and stderr. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(entry.resolve()), '--task', str(task), '--workdir', str(tmpd)], capture_output=True, text=True, timeout=120, cwd=tmpd)`

After: `subprocess.run([sys.executable, str(entry.resolve()), '--task', str(task), '--workdir', str(tmpd)], capture_output=True, text=True, errors='replace', timeout=120, cwd=tmpd)`

### `tools/validate_method.py:125` → `tools/validate_method.py:125`

Output: method stdout parsed as JSON response; method stderr diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(entry)], input=json.dumps(request), capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))`

After: `subprocess.run([sys.executable, str(entry)], input=json.dumps(request), capture_output=True, text=True, errors='replace', timeout=timeout, cwd=str(ROOT))`

### `tools/validate_method.py:222` → `tools/validate_method.py:222`

Output: driver smoke-run stdout/stderr parsed as validation diagnostics. Policy: implicit strict → explicit replace.

Before: `subprocess.run([sys.executable, str(ROOT / 'driver.py'), '--harness', harness.name, '--mode', 'A', '--rounds', '1', '--run-id', run_id, '--dataset', 'demo', '--sampling', 'below_0.5', '--method-entrypoint', f'{sys.executable} {method / 'run.py'}', '--runs-root', tmp, '--work-root', str(Path(tmp) / 'work')], capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))`

After: `subprocess.run([sys.executable, str(ROOT / 'driver.py'), '--harness', harness.name, '--mode', 'A', '--rounds', '1', '--run-id', run_id, '--dataset', 'demo', '--sampling', 'below_0.5', '--method-entrypoint', f'{sys.executable} {method / 'run.py'}', '--runs-root', tmp, '--work-root', str(Path(tmp) / 'work')], capture_output=True, text=True, errors='replace', timeout=timeout, cwd=str(ROOT))`
