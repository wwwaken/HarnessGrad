# w-jerichoadm: process-owned admission

FOUND — the refined rule is “Refuse a declared policy when, and only when, this process does not apply it.” The predicate retains presence-based unsupported declarations, all exec defaults and container state; network is presence-based only for exec/container routes (`eval/run/runner.py:44`, `eval/run/runner.py:55`, `eval/run/runner.py:61`, `eval/run/runner.py:65`, `eval/run/runner.py:74`). The ownership/admission table is now in `INTERFACE.md:841`.

The native plan was read through its final return (`eval/containers/sandbox.py:176`, `eval/containers/sandbox.py:424`) together with the native call site (`eval/run/runner.py:516`). None of the seven remaining explicit env resource/policy declarations below is applied by that native path. Read-only mounts, tmpfs and frozen verifier output are real protections, but they are fixed platform behavior and do not consume those declaration objects (`eval/containers/sandbox.py:248`, `eval/containers/sandbox.py:270`, `eval/containers/sandbox.py:316`, `eval/containers/sandbox.py:328`).

| Remaining refusal field | Where it would have to be applied; actual ownership/absence |
| --- | --- |
| `env.cpus` | Native runner call `eval/run/runner.py:516` / plan inputs `eval/containers/sandbox.py:176` do not pass/accept a CPU bound. Docker CPU flag is daemon-owned (`eval/containers/container.py:558`). |
| `env.memory_mb` | Same native call/plan (`eval/run/runner.py:516`, `eval/containers/sandbox.py:176`) has no memory bound. Docker memory flag is daemon-owned (`eval/containers/container.py:557`); conversion of declaration is `eval/containers/container.py:1053`. |
| `env.resources` | Native runner/plan would have to consume the object (`eval/run/runner.py:516`, `eval/containers/sandbox.py:176`); neither does. |
| `env.filesystems` | Plan's fixed mounts (`eval/containers/sandbox.py:248`, `eval/containers/sandbox.py:270`) do not consume this object or enforce declaration-specified byte/inode quotas; plan inputs are `eval/containers/sandbox.py:176`. |
| `env.resource_policy` | Native call/plan would have to consume it (`eval/run/runner.py:516`, `eval/containers/sandbox.py:176`); neither does. |
| `env.network_policy` | Plan reads only the separate `network` argument (`eval/containers/sandbox.py:183`, `eval/containers/sandbox.py:202`), not this declaration. |
| `env.artifact_policy` | Native plan's artifact freezing/writable output (`eval/containers/sandbox.py:316`, `eval/containers/sandbox.py:328`) does not consume this policy. It is not a plan input (`eval/containers/sandbox.py:176`). |
| `env.network` (exec/container only) | Native `none` is applied at `eval/containers/sandbox.py:205`; exec network is passed to daemon argv (`eval/containers/container.py:546`, `eval/containers/container.py:905`), so this process does not itself apply it there. |
| `env.exec_defaults` | Every exec still triggers (`eval/run/runner.py:61`). Docker receives PID/memory/CPU flags (`eval/containers/container.py:556`); namespace/cgroup application belongs to the daemon. No such declaration enters native plan inputs (`eval/containers/sandbox.py:176`). |
| `env.state=container` | Container stop/commit is daemon-owned (`eval/containers/container_state.py:190`). Native mount-plan inputs (`eval/containers/sandbox.py:176`) have no container-state implementation. |
| `verifier.artifact_policy` | Verifier native call freezes the task and opens the reward directory (`eval/verification/verifier.py:715`); neither that call nor plan inputs (`eval/containers/sandbox.py:176`) consumes this policy object. |

ABSENT — this is scoped to the enumerated file `eval/containers/sandbox.py`, not a repository-wide absence claim. Exact command: `rg -n 'cpus|memory_mb|resources|filesystems|resource_policy|network_policy|artifact_policy|exec_defaults|state=container' eval/containers/sandbox.py`; observed stdout `''`, exit 1. The complete plan review above distinguishes fixed mounts from declaration enforcement. The command/output is also retained in validation.

| Removed trigger | Existing application retained |
| --- | --- |
| `env.agent_timeout_s` | `phase_timeout` in `eval/run/runner.py:236`; native agent deadline passed at `eval/run/runner.py:518` and subprocess timeout applied at `eval/containers/sandbox.py:463`. |
| `env.verify_timeout_s` | Combined with caller/verifier limits at `eval/run/runner.py:237`, again bounded at `eval/verification/verifier.py:528`; native sandbox timeout `eval/verification/verifier.py:717`, host timeout `eval/verification/verifier.py:723`. |
| Native `env.network` | Runner forwards the declaration (`eval/run/runner.py:522`); plan rejects unsupported values and builds `--unshare-net` for `none` (`eval/containers/sandbox.py:202`, `eval/containers/sandbox.py:205`). Omission adds no network declaration/refusal. |
| Already exempt `verifier.timeout_s` | Same `phase_timeout` expression (`eval/run/runner.py:237`, `eval/verification/verifier.py:528`) and verifier subprocess deadlines above. |

No deadline or native plan implementation changed: the production diff is limited to `_refuse_unobserved_policies` (`eval/run/runner.py:41`). Native bridge/services still fail at `eval/policy/runtime_policy.py:17`; unsandboxed native isolation still fails at `eval/run/runner.py:242`; registry permits only native none/omission (`data/scaffolds/registry.py:361`).

The three requested cases moved intact to direct must-admit coverage (`tests/quality/test_shared_admission_wiring_codex163.py:77`). All other must-refuse cases remain, exec+none was added, and receipt-shape assertions still run on refused cases (`tests/quality/test_shared_admission_wiring_codex163.py:37`, `tests/quality/test_shared_admission_wiring_codex163.py:52`). Separate tests check network presence for both external routes (`tests/quality/test_shared_admission_wiring_codex163.py:89`). Adapter-observation/cache refusal controls now explicitly use exec network, retaining every refusal/cache assertion (`tests/quality/test_shared_admission_wiring_codex163.py:123`, `tests/quality/test_shared_admission_wiring_codex163.py:143`).

The transport control now parameterizes authorization false/true and requires both to return exit 0, answer “route reached”, transport “unix+isolated-loopback” and one connection (`tests/quality/test_native_model_route.py:169`). The synthetic echo upstream, payload preservation and namespace assertions remain (`tests/quality/test_native_model_route.py:136`). Host-loopback/egress isolation stays asserted in the authored mock projection control, which now uses the real admission hook instead of patching it away (`tests/quality/test_jericho_runtime_boundaries.py:177`, `tests/quality/test_jericho_runtime_boundaries.py:210`, `tests/quality/test_jericho_runtime_boundaries.py:218`). Its unsandboxed control now expects the runtime's isolation ValueError before launch (`tests/quality/test_jericho_runtime_boundaries.py:153`).

B7's stale adapter refusal was changed to assert actual adapter admission, then assert refusal for an additional unsupported native CPU declaration; all existing receipt/no-score assertions remain and exact `['env.cpus']` coverage was added (`tests/quality/test_runtime_blocker_evidence_b7.py:374`). New evidence identifies that augmented admission env explicitly (`tests/quality/test_runtime_blocker_evidence_b7.py:401`). UNKNOWN — the B7 body is unexecuted because its existing outer read-only guard fixture skipped it (`tests/quality/test_runtime_blocker_evidence_b7.py:61`). No frozen receipt was edited.

GAIA's refusal test was unchanged (`tests/quality/test_gaia_official_scorer.py:205`). The direct observation reports `cpus=2`, `memory_mb=4096`, and retained fields `['env.cpus', 'env.exec_defaults', 'env.memory_mb', 'env.network', 'env.state=container']` (validation command/output cited below). GAIA's control CLI exited before scoring in the selected tests; its actual scorer tests were deliberately deselected (`tests/quality/test_gaia_official_scorer.py:209`, `tests/quality/test_gaia_official_scorer.py:221`).

| Test file under `tests/quality/` | Collected before → after | Exact execution summary before | Exact execution summary after | Evidence before / after |
| --- | --- | --- | --- | --- |
| `test_shared_admission_wiring_codex163.py` | 50 → 56 | `50 passed` | `56 passed` | `reports/w-jerichoadm-validation.txt:121` / `reports/w-jerichoadm-validation.txt:471` |
| `test_native_model_route.py` | 14 → 15 | `14 passed` | `15 passed` | `reports/w-jerichoadm-validation.txt:147` / `reports/w-jerichoadm-validation.txt:498` |
| `test_gaia_official_scorer.py` | 10 → 10 | `2 passed, 8 deselected` | `2 passed, 8 deselected` | `reports/w-jerichoadm-validation.txt:169` / `reports/w-jerichoadm-validation.txt:520` |
| `test_unobserved_diagnostic_c2.py` | 18 → 18 | `18 passed` | `18 passed` | `reports/w-jerichoadm-validation.txt:199` / `reports/w-jerichoadm-validation.txt:550` |
| `test_runtime_blocker_evidence_b7.py` | 2 → 2 | `2 skipped` | `2 skipped` | `reports/w-jerichoadm-validation.txt:213` / `reports/w-jerichoadm-validation.txt:564` |
| `test_jericho_runtime_boundaries.py` | 17 → 17 | `16 passed, 1 skipped` | `16 passed, 1 skipped` | `reports/w-jerichoadm-validation.txt:242` / `reports/w-jerichoadm-validation.txt:593` |
| `test_web_gateway.py` | 43 → 43 | `42 passed, 1 deselected` | `42 passed, 1 deselected` | `reports/w-jerichoadm-validation.txt:297` / `reports/w-jerichoadm-validation.txt:648` |
| `test_services.py` | 43 → 43 | `31 passed, 12 deselected` | `31 passed, 12 deselected` | `reports/w-jerichoadm-validation.txt:352` / `reports/w-jerichoadm-validation.txt:703` |
| `test_isolation.py` | 16 → 16 | `1 failed, 6 passed, 9 deselected` | `1 failed, 6 passed, 9 deselected` | `reports/w-jerichoadm-validation.txt:401` / `reports/w-jerichoadm-validation.txt:752` |

The entire files were collected; execution used identical explicit selections before/after. No assertion was weakened to make counts pass. Nine dataset-driving isolation cases, eight GAIA cases, one web integration case and twelve service integration cases were deselected; exact selectors and full output are in validation. `test_isolations.py` is ABSENT within the exact named path `tests/quality/test_isolations.py`; `test_isolation.py` exists. The isolation failure is unchanged: `assert ".env" in snap` at `tests/quality/test_isolation.py:156`, and the exact named `.env` path is absent in this worktree (validation scope command). B7 skipped both tests for its outer guard; the Jericho snapshot case skipped for the absent ignored fixture (`tests/quality/test_jericho_runtime_boundaries.py:119`).

FOUND — direct actual Jericho declaration check used `TASK = {"task_id": "acorncourt"}`, `tid = TASK['task_id']`, and `data.datasets.jericho.ENV[tid]` with no authorization. Exact observed output: `_refuse_unobserved_policies(TASK, data.datasets.jericho.ENV[tid], None) = None`; `--unshare-net in native plan = True`. The full unexecuted plan and script are in `reports/w-jerichoadm-validation.txt:794`. The declaration retains kind files, network none and both 300-second deadlines; agent_runtime is present. No Jericho episode, scorer, model or GPU was run by this demonstration. The runtime projection was not staged by this plan-only check.

FOUND — `python3 tools/check_dataset_blockers.py` printed exactly:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

Evidence: `reports/w-jerichoadm-validation.txt:841`. Registry/journal/withdrawn requirements/AGENTS and frozen receipts were not edited; no registry proposal is warranted for this code-only ownership correction (explicit changed-file list in validation).

Most important UNKNOWN: the modified B7 guarded evidence path has not executed. Review its admission-env change independently; reproducing the full B7 Jericho control would exceed this task's no-dataset/no-scorer execution boundary (`tests/quality/test_runtime_blocker_evidence_b7.py:261`). Full production backend enforcement remains unobserved; this change supplies no production H0 authorization.
