# ALFWorld current runtime control receipts — w-alf

## CLOSED: alfworld / current-runtime-identity

A fresh selected **noop control actually ran**, and the adapter's TextWorld replay
scorer returned raw reward `0.0`. The dataset-owned identity requirement is closed.
The diagnostic publication receipt remains **unmeasured**, `score=null`, reason
`policy_enforcement_not_observed`; this is not a measured method curve, an oracle
success claim, a historical comparison, or permission to expand. Shared
`scorer-offline-closure` and `artifact-only-state-export` stay open.
No production code, policy, gate, scorer or historical receipt was changed.

## Requirement read before execution

Original `observed` from `docs/dataset-blockers.json`, preserved here before retirement:

> Historical identity source review is closed: retain alfworld-h0-10pct-v4 as journal-complete, 9 platform train-side tasks x3, jobs=1 (27 planned task-trials). Raw trial/provenance receipts are not in the repository, so measured coverage is not independently recertified. The 134-task valid_unseen pool uses a platform hash split; 30 actions and documented resource defaults are limits, not current runtime results. No current selected control/runtime receipt is established.

Original `next_action`:

> Establish current selected oracle/noop, scorer/runtime identity, effective limits and cleanup evidence independently of the completed historical generation and all shared gates. Historical comparison requires original trial/provenance receipts. Do not rerun or overwrite the completed generation.

Read `AGENTS.md`, `reports/measurement-coverage-hg-b3-review.md` (ALFWorld section),
`docs/adapter-integration-journal.md` (“ALFWorld — embodied runtime”), the referenced
`data/datasets/alfworld/verify/check.py`, `docs/terminal-bench-runtime-admission.md`,
`reports/w-net-receipts.md`, `reports/w-net-validation.txt`, and precedent commit
`5e252aa`. Source declarations were not substituted for runtime evidence.

## Commands and run identity

Executed preparation/collection commands in `/tmp/hg-alf`:

```sh
python3 reports/w-alf-evidence/launch.py
python3 reports/w-alf-evidence/collect.py
```

The launcher was invoked twice. The first version failed during driver import,
before any admission or run reservation. Exact first child command from
`reports/w-alf-evidence/command.txt`:

```sh
env HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 /tmp/hg-alf/reports/w-alf-evidence/observe_driver.py /tmp/hg-alf/reports/w-alf-evidence --harness ../data/datasets/alfworld/oracle_harness --dataset alfworld --sampling diagnostic --policy-evidence /tmp/hg-alf/reports/w-alf-evidence/policy-input.json --authorize-unobserved-diagnostic 'Operator requests one fresh selected ALFWorld noop control to establish current runtime/scorer identity, effective limits and cleanup independently of the completed historical generation. Existing dataset oracle harness is used with no walkthrough staged, no method and no model completion. Enforcement and shared gates remain unknown; no comparable publication, pilot expansion or production authorization.' --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id w-alf-noop-20261014T202120Z-c56ee678 --runs-root /tmp/hg-alf/runs --work-root /tmp/w-alf-noop-20261014T202120Z-c56ee678-work
```

`reports/w-alf-evidence/driver.stderr.txt` records `KeyError: None` in the installed
Python `ast.py` during observer-enabled imports; `launch-result.json` records
`returncode=1`, `run_exists=false`, `work_exists=false`. This was an observer bug:
reading all frames' locals interfered with a Python comprehension. The corrected
observer inspects only its named target functions. Original launcher/observer
versions are `import-failure-launcher.py` and `import-failure-observer.py` in the same
evidence directory. Those failed-attempt receipts are preserved. No control ran
in that attempt, and no score or diagnostic outcome is attributed to it.

Exact actual runtime child command from
`reports/w-alf-evidence/runtime-attempt/command.txt`:

```sh
env HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 /tmp/hg-alf/reports/w-alf-evidence/observe_driver.py /tmp/hg-alf/reports/w-alf-evidence/runtime-attempt --harness ../data/datasets/alfworld/oracle_harness --dataset alfworld --sampling diagnostic --policy-evidence /tmp/hg-alf/reports/w-alf-evidence/runtime-attempt/policy-input.json --authorize-unobserved-diagnostic 'Operator requests one fresh selected ALFWorld noop control to establish current runtime/scorer identity, effective limits and cleanup independently of the completed historical generation. Existing dataset oracle harness is used with no walkthrough staged, no method and no model completion. Enforcement and shared gates remain unknown; no comparable publication, pilot expansion or production authorization.' --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id w-alf-noop-20261014T202206Z-13b61fc3 --runs-root /tmp/hg-alf/runs --work-root /tmp/w-alf-noop-20261014T202206Z-13b61fc3-work
```

`observe_driver.py` delegates those arguments unchanged to `driver.py` using
`runpy`, with passive audit/profile callbacks only. It records calls/returns and
copies selected task evidence after verifier return, before normal removal; it
never substitutes platform functions, arguments or results. Full unfiltered
streams remain on disk and in the external archive. Committed command/process
summaries omit unrelated host environment values and unrelated processes.

`reports/w-alf-evidence/runtime-attempt/identity.json` binds:

- Run ID: `w-alf-noop-20261014T202206Z-13b61fc3`.
- Original run directory: `/tmp/hg-alf/runs/w-alf-noop-20261014T202206Z-13b61fc3`.
- Work root: `/tmp/w-alf-noop-20261014T202206Z-13b61fc3-work` (outside the platform).
- Review copy of run receipts: `reports/w-alf-evidence/execution/`.

`runtime-attempt/launch-result.json` records `returncode=2`, `run_exists=true`,
`work_exists=true`. This exit is the unchanged publication refusal after execution,
not failure to start or a failed scorer. `driver.stderr.txt` says:
`refusing staged curve: lifecycle publication gate or measurement incomplete`.

## Selected control and coverage

Paths below are relative to `reports/w-alf-evidence/` unless absolute.
`selection-summary.json` is a copy of `runtime-attempt/selection.json` with the
inline game replaced by its digest, explicitly labeled. It records the provisioned
pool, eligible IDs, selected ID, environment, verifier and setup paths. Raw values:

- Official pool `valid_unseen`, `tasks=134`, `game_files=134`, `with_solvable=134`.
- Platform hash side: train `81`, eval `53` (`runtime-attempt/split.json`);
  eligible `81`, selected `1`, expected trials `1` (`execution/diagnostic_receipt.json`).
- Selected task: `pick_heat_then_place_in_recep-Tomato-None-GarbageCan-10__trial_T20190908_225046_020282`.
- Existing harness: `data/datasets/alfworld/oracle_harness/`, descriptor
  `name=alfworld-oracle`, `version=1`, `role=control`, `backend=cli`, `env_kinds=[files]`.
  Driver `--harness ../data/datasets/alfworld/oracle_harness` selects these existing
  bytes without adding a harness or method. `--method-entrypoint` is forbidden by
  unobserved diagnostic admission (`driver.py:390-396`); `methods/noop` is a
  method-identity control and does not stage an ALFWorld reference trajectory.
- Actual arm **noop**, despite its generic trace label `agent_model=oracle`:
  `artifact-bindings.json` records `oracle_actions_present=false`,
  `walkthrough_present=false`, and raw action log `{"kind": "done", "step": 0}`.
  No actions were staged or taken. This does not establish the oracle arm's success.
- `runtime-attempt/run-one-result.json`: actor `exit_code=0`; trace usage
  `input_tokens=0`, `output_tokens=0`, `calls=0`.
  `execution/diagnostic_execution.json`: `invalid={}` and raw `per_task` zero.
- `execution/diagnostic_receipt.json`: jobs `1`, trials `1`, measured tasks/trials
  `0/0`, invalid tasks/trials `0/0`, unmeasured tasks/trials `1/1`, `score=null`.
  The sole outcome reason is `policy_enforcement_not_observed`.

The endpoint bound in `runtime-attempt/policy-input.json` is
`http://127.0.0.1:8002/v1`; the configured model is `qwen3.5-9b-local`.
`endpoint-models.json` and `endpoint-probe.json` in that directory record the local
model list and HTTP `status=200`. No model completion was sent by the control;
model-weights hash is `null`. `runtime-attempt-process-summary.json` has
`matching_lines=[]` at preflight, so no other driver/control execution was observed
then; this is not a machine-wide lease attestation.

## Executed scorer/runtime and hashes

`runtime-attempt/run-one-result.json` records:
`scorer_isolation_class=actor-workdir`, `scorer_isolation_declared=unknown`,
`harness_runtime.source=platform`, `model_gateway=null`, `web_gateway=null`,
`agent_package_projected=false`, `verifier_package=trusted`.

Actual route: files setup → existing noop control under bwrap →
`eval.verification.verifier._verify` → `_verify_inner` → sandboxed
`python3 check.py --workdir . --game game.tw-pddl --log alf_actions.jsonl --reward-file verifier/reward.txt --evidence-file verifier/evidence.json --budget 30`.
The verifier rematerialized the trusted scorer/library/game in the actor workdir,
mounted that tree read-only and reopened the verifier output directory writable.
`executed-commands.json` preserves the executed bwrap mount flags and verifier argv.
This is the recorded actor-workdir route, with no pristine-offline or
snapshot-service attestation (`eval/verification/verifier.py:456-491,594-612`).

`evidence.json` and `reward.txt` are byte copies captured before task cleanup.
Raw values: `measured=true`, `reward=0`, `official_game_points=0.0`,
`actions_in_log=0`, `actions_replayed=0`, `log_records=1`,
`agent_declared_done=true`, `budget=30`, `budget_exhausted=false`, `won=false`,
`won_at_step=null`, `steps=[]`.
The raw verdict is `passed=false`, `score=0.0`, verifier process `exit 1`:
`the log holds no actions, so the goal cannot have been satisfied`.
The scorer built/reset a fresh environment even with an empty action log
(`gym_env.replay`), then applied its explicit local empty-episode convention.
It does not demonstrate a successful action trajectory or upstream's undefined
empty-sequence reduction; those limits remain as documented in the prior review.

`artifact-bindings.json` compares captured materialized files against hashes taken
before execution in `runtime-attempt/source-hashes.json`; each `equal=true`:

| Captured input | SHA-256 |
| --- | --- |
| check.py | `c1e7b97377122babc47c519128244ffce60b4511c1b5faa061c10b50a1e03c6d` |
| gym_env.py | `46dfb6b0574c8ed391e30162c0d54ce6cd7e6030cf545ad867effaef6561e448` |
| alf | `60a3c1158c6cc2ead2dd28ada4580d364461fcc7628807afe4201bdb142b1c8d` |
| Stripped selected game | `e6934aec5438a8b6c7722b5a58659ed217cb1a19e54c47946483f8a05a66f5b7` |

`runtime-attempt/harness-hashes.json` binds the actual harness source and descriptor;
`staged-harness-integrity.json` confirms both retained workspace files match those
pre-execution hashes (`equal=true` for each).
`source-hashes.json` also binds adapter, runner, verifier, sandbox and the original
selected game/trajectory paths. `execution/diagnostic_receipt.json` records:

```json
{
  "harness": "39c3a29b1c857c50875777b03350d813aa11b257b4d12cf21cbc6b4e8c838d3d",
  "manifest": "217ce5138dcd25e4af7d0142415e13308ca120adabf9766ddc39876d8552c258",
  "model": null,
  "source": "99fa3b3809c45b0b288e4380929784b414d2caa0af681d3e5b14fdb299619ba5",
  "split": "ab9cce7d3e097316f20a2d78e91be34b6b09ac27c15171e0c03466180ef89ea5"
}
```

These source/split/launch-manifest/harness hashes bind the named observer manifests,
not a complete transitive dependency closure. The pre-execution metadata inventory
`runtime-attempt/package-versions.json` reads `alfworld=0.4.2`, `textworld=1.7.0`.
`python-runtime.json` records the orchestrator interpreter
`/mnt/8t/xubuqiang/anaconda3/bin/python3`, Python `3.12.4`, executable SHA-256
`0eb25a387ef43f21492b659f4865eae5bdaf8da30d6357097b2d9bb24873ebfb`.
The actual actor/verifier argv use `python`/`python3`; the observer did not resolve
an engine-process executable or hash every dependency loaded inside its namespace.

## Effective limits observed

`runtime-attempt/run-one-result.json.runtime_boundary` records actor timeout
`3600`, verifier timeout `300`, actor network `inherited`.
`executed-commands.json` independently records actual `subprocess.run` timeout
arguments `3600` and `300`, and actor `HG_AGENT_DEADLINE_S=3600`.
`evidence.json` records action budget `30` after the real replay. These are the
executed deadline arguments/budget, not a timeout-expiration test or utilization.
The adapter's old comment claiming a shorter harness default is not current evidence.
`execution/run_meta.json` and the diagnostic receipt record `jobs=1`, `trials=1`;
`runtime-attempt/launch-manifest.json` binds `rounds=0`. No improver was called.

`resource-observations.json` preserves immediate Popen-child observations for
actor bwrap PID `219098` and verifier bwrap PID `219109`: kernel `Cpus_allowed_list=0-143`,
cgroup `0::/user.slice/user-1026.slice/session-30486.scope`, CPU time/resident set/
address-space soft and hard rlimits `unlimited`. The sampled PIDs were the launchers,
not later TextWorld/actor-engine PIDs; no peak CPU/RAM number is claimed.
Post-execution cgroup ancestor reads in the same file record session/user memory
`max`, session pids `max`, user pids `679120`, user.slice CPU `max 100000` and
cpuset `0-143`. Missing controller files are recorded with their actual errors.
These later reads do not prove unchanged cgroup configuration during execution.
No per-task CPU or memory cap was proven; documented CPU/RAM defaults must not be
reported as effective native caps. `context.limits.resource/budget` remain `null`
in the immutable publication receipt. No filesystem-quota enforcement is claimed.

## Cleanup and preservation

`runtime-attempt/temporary-cleanup.json` records all observed tempfile directories:

- `/tmp/hg-sandbox-check-j889k7pp`: `exists_after=false`.
- `/tmp/hg-verify-check-0z7wpi91`: `exists_after=false`.
- `/tmp/hg-task-vzm02hjt`: `exists_after=false`.

`cleanup-observations.json` also preserves the actual task `shutil.rmtree` event,
`exists_before=true`, and the pre-removal relative file/hash inventory (setup,
action log, task, trace, rematerialized scorer/library and verdict files).
Both sampled bwrap PIDs have `exists=false` at the final observation.
The run directory, workspace/state, receipt copies and captured selected task tree
remain deliberately retained; no old run was removed, resumed or overwritten.
Private namespace tmpfs contents and unobserved engine scratch were not inventoried.
Observed directory absence is not a formal lifecycle admission: the immutable
receipt still has cleanup/snapshot `status=unknown`, `receipt_sha256=null`,
`lifecycle=null`.

Raw evidence with selected dataset payloads and unrelated process/environment
fields remains at the original ignored paths. It is also preserved outside git:
`/tmp/w-alf-noop-20261014T202206Z-13b61fc3-work/w-alf-original-evidence.tar.gz`,
SHA-256 `b4b7337e7231f09a2067b83e39c9addb4929d78bd246d9e424cf55a167ececc4` (`external-archive.json`).
Selected dataset content was not committed. `receipt-integrity.json` reads
`run_copy_matches=true`, `scorer_input_bindings_match=true`; the execution review
copies are byte-identical to the original run files.
`final-integrity-audit.json` independently records that the archive matches its
digest and original files, and that shared blockers and history are unchanged.

## Disposition and validation

Removed only ALFWorld's dataset-owned `current-runtime-identity` entry from the
live blocker list; the checker represents closure by removal, not a new status.
The selected noop identity, executed scorer route/hash, executed limits and
bounded cleanup observations now exist independently of historical summaries.
Unknown caps/dependency closure/formal lifecycle remain explicit rather than
being certified. The completed `alfworld-h0-10pct-v4` generation and its archives
remain untouched; its original trial/provenance receipts are still required for
any historical comparison. Both shared gates and `production_authorized=false`
remain unchanged. The pinned historical-review test now checks this limited
closure against the recorded raw and publication receipts.

Focused validation commands and raw output are in `reports/w-alf-validation.txt`.
