"""Generate the scoped report from recorded command outputs, without another run."""
import json
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
def read(name): return json.loads((OUT/name).read_text())
l=read('launch-input.json'); s=read('result-summary.json'); d=read('driver-result.json')
m=read('execution/run_meta.json'); p=read('policy-input.json'); roles=read('role-observations.json')
reason=l['argv'][l['argv'].index('--authorize-unobserved-diagnostic')+1]
report=f'''# AppWorld unchanged-budget actor diagnostic - w-appworld2

**AppWorld successful-task-evidence remains OPEN.** One fresh actor diagnostic produced authentic raw measured TGC **0.0**, `success=false`, with **{s['passes']}/{s['raw_verdict']['evidence']['num_tests']} requirements passing**. It did not obtain successful actor-task evidence. The formal staged receipt remains **score=null, measured=0, unmeasured=1, invalid=0** because `policy_enforcement_not_observed`. No shared blocker closes; no pilot expansion is authorized.

All packet-relative paths below are under `reports/w-appworld2-evidence/`. Raw command outputs, the actor trace, service recording, official verifier bytes and copied driver receipts are preserved. Existing `runs/`, frozen receipts, historical journal paragraphs and prior evidence packets were not modified or resumed.

## Driver requirements and exact attempt

Read `AGENTS.md`, the exact AppWorld blocker, `reports/w-appworld-receipts.md` and `reports/w-awp-released-predicates.md` first, then the generic actor, public CLI/runtime prompt, task-bound service, separate replay checker, deterministic selector, staged policy and historical protocol review. `starting-appworld.json` preserves the starting blocker, including its unchanged next action. `review-source/` preserves reviewed runtime bytes with `review-source-hashes.json`; it is an evidence copy, not code used to alter the actor.

The driver requires a provisioned pool with its admitted digest, locally present pinned actor/service/verifier images, Docker/container-boundary preflight, the existing dependency overlay, explicit live model binding, and a work root outside the platform. Diagnostic policy also requires a dataset/side/endpoint-bound context with source/split/manifest/model/harness hash slots, resource/budget limits and comparability notes. Unknown dataset gates require explicit `--authorize-unobserved-diagnostic`; that permission never attests policy enforcement or permits staged score publication. The driver refuses rather than bypassing these boundaries. Actual preflight and execution output is in `driver.stdout.txt` and `driver.stderr.txt`.

`endpoint-models.json` records the `/models` response from **http://127.0.0.1:8002/v1**. An additional generic, task-free `Reply with OK.` completion returned **OK**, model `qwen3.5-9b-local`; exact request/status and unmodified response bytes are `endpoint-completion-request.json` and `endpoint-completion.raw.json`. The `/models` record's `model_completion_probe_sent=false` describes that models request only; the separate completion is explicitly retained. The probe used 16 maximum output tokens and returned 2, separate from actor usage. No server was started and no paid endpoint was used.

Preflight `processes-before.json` found an operator-owned Musique run (its argv includes `jobs=40`) and existing model servers, including a process on 8001. They were left untouched; this diagnostic used only 8002 and **one worker**. Endpoint exclusivity/global concurrency cannot be claimed. `containers-before.json` and `networks-before.json` preserve contemporaneous Docker listings. The process filter also captured its own long shell command; no global-idleness inference is made from that noisy listing. `inherited-overrides.json` and `dotenv-overrides.json` are empty: no hidden AppWorld/model/budget override was applied.

Registered worktree `/tmp/hg-appworld2`, branch `wg-appworld2`, baseline `{m['platform']['git_sha']}`. The driver records `platform.dirty=true`, content SHA `{m['platform']['content_sha']}`, because new evidence files existed. `runtime-unchanged.json` records an empty successful tracked-runtime diff. This was not relabeled a clean checkout.

Fresh run ID: **`{l['run_id']}`**. `launch-input.json` records both fresh paths absent before launch:

- Run directory: `{l['run_root']}`.
- Work root: `{l['work_root']}`.

Both are outside the platform; the repository's `runs/` was not used. `launch.py` was invoked once, via `python3 reports/w-appworld2-evidence/launch.py > reports/w-appworld2-evidence/launcher.stdout.txt 2> reports/w-appworld2-evidence/launcher.stderr.txt`. It launches the driver once and passively observes run-owned Docker objects. No retry or second diagnostic occurred.

Exact driver command (`command.txt`; argv/environment also in `launch-input.json`):

```sh
{(OUT/'command.txt').read_text().strip()}
```

The truthful authorization reason is: “{reason}”

`driver-result.json`: start `{d['started_at']}`, end `{d['ended_at']}`, return code **{d['returncode']}**. Actor and verifier each exited 0; driver exit 2 is the retained staged-publication refusal after execution, not an actor/scorer infrastructure error. The driver printed task `done (88s)`; the actor's own trace reports `{s['trace_tail'][1]['wall_clock_s']['total']}` seconds. These measure different scopes.

## Selection, budget and provenance

`split-selection.json` and `execution/diagnostic_receipt.json` bind the deterministic `diagnostic_task_set` choice **`{l['task_id']}`**, source split **train**, scenario `cf6abd2`, variant 2, from **{s['staged_counts']['eligible_tasks']} eligible train+dev study tasks**. Selected tasks=1, expected trials=1, trials=1, jobs=1, rounds=0. No held-out task executes. This repeats the unchanged selector's earlier choice, not a task chosen for ease or adjusted after seeing a result. No oracle, gold answer or released solution was supplied to the actor.

The actual trace identity (`execution/diagnostic_execution.json.identity_declared`) retains **max_steps=32**, **max_output_tokens=2048**, submit_retries=2, parse_retries=2, finish_nudge_steps=4, repeat_nudge_limit=2, output_limit=4000, context_chars=60000. No actor/prompt/CLI/scorer/model/selection/budget code was changed, and no budget override was added. `policy-input.json` retains actor/verifier 900-second deadlines and requested 2 CPUs / 4096 MiB / 1024 PIDs. Full effective identity and resource observations are preserved separately from requested policy.

Freshly computed hash inventories are `source-hashes.json` (adapter, CLI, checker, provisioned release bundle and pool), `harness-hashes.json` (generic loop files), `selected-source-hashes.json` (selected spec and predicate bytes, hashed only after completion), and `review-source-hashes.json`. Image preflight is in `image-actor.json`, `image-service.json`, `image-verifier.json`. No historical digest was substituted for a fresh computation. Policy canonical-JSON hash domains are:

```json
{json.dumps(p['context']['hashes'],indent=2)}
```

The model weight hash is **null/unknown**; advertised model identity and existing process path do not authenticate weights. Driver split source is `{m['split_source']}`, split SHA `{m['split_sha']}`. It hashes a different representation from the policy split digest; neither is relabeled as the other. Source/image pins do not establish upstream authentication, full transitive closure or production custody.

## Authentic replay result and formal refusal

`execution/diagnostic_execution.json.verdicts.{l['task_id']}` records unchanged checker metric **`appworld.task_goal_completion` / TGC**, `measured=true`, `success=false`, `score=0.0`, `num_tests=8`, six passes and two failures, with no invalid task or scorer-unmeasured marker. `result-summary.json.raw_counts` derives **measured=1, invalid=0, unmeasured=0** only at this raw scorer layer.

The raw verifier wrote `0.0\\n` and complete evidence; exact captured bytes are:

- `verifier-reward.txt-51ff0d2f0d3a5d61edec31785532ea0d570f8c348d58b15b94ff9c2ca6e926a4`.
- `verifier-evidence.json-e6f59180c1dd5424b36dba3ffff54bae4facf5b7fc5ad5eee987802f8ac4804a`.

`verifier-file-observations.jsonl` binds those copies to verifier `{roles['verifier']['container_id']}` and `/tmp/hg-verdict-4mf75dyd/`, with capture times, sizes and SHA-256. The actor has no recording mount; the service owns the recording, and a fresh separately pinned verifier mounts it read-only and replays API calls before `world.evaluate()`. This is real actor execution followed by the production replay checker, not a synthetic/gold-injected success control.

The two failed official requirements are `assert answers match.` (`'<<not_given>>' == 'null'`) and the updated note body comparison. The actor left the requested item marked done and also changed an unrelated item from not done to done. Complete expected/actual lists remain in the raw evidence; no corrected answer, replay, replacement state or alternative score was inserted.

Formal `execution/diagnostic_receipt.json` retains `score=null`, coverage measured_trials=0 / unmeasured_trials=1 / invalid_trials=0, reason `policy_enforcement_not_observed`, `comparable=false`, `production_authorized=false`, `policy_enforcement_observed=false`, `lifecycle=null`, gates/cleanup/snapshot status `unknown`. Passive Docker observations do not override these fields. There is no valid published success or comparable production diagnostic.

## What this establishes about 9B success at the existing budget

The trace `execution/progress/round-0/traces/{l['task_id']}.trial1.jsonl` and service API log establish that this 9B actor can initialize, discover documentation, obtain in-world credentials, authenticate, find the note, perform a state-changing PATCH and read it back with the existing budget. There are **{s['api_call_count']} recorded API calls**, **{s['actor_commands']} shell commands**, and **{s['tokens']['calls']} model calls**, with **{s['tokens']['input']} input / {s['tokens']['output']} output tokens**, zero retries and zero context trims. A failed guessed documentation lookup returned an application message at step 6 and discovery recovered at step 7; shell commands still exited 0. `model_gateway` records target `127.0.0.1:8002`, {s['model_gateway']['connections']} connections and {s['model_gateway']['upstream_connect_failed']} upstream connect failures.

The actor voluntarily submitted `{{"answer": {{"task_id": "cf6abd2_2", "status": "completed"}}}}` at **step 15**, after a readback displaying the incorrect state. It used 16 of 32 reply steps and ended normally, with 16 reply steps unused. The actor trace clock is model=61.6 s, commands=10.2 s, total=71.8 s, below the existing 900-second deadline. Thus **this loss is not evidence of exhausted step/output/deadline budget**; neither truncation/retry exhaustion nor provider/scorer failure explains it.

There is also a task-facing completion gap: the supervisor documentation returned at step 7 advertises `complete_task`, but none of the 14 logged API routes submits supervisor completion. The final harness answer does not become a supervisor API call in this recording. The generic public runtime prompt tells the actor to give its final answer through the harness; the scorer measures the replayed world's answer. The observed missing answer and semantic state error are distinct failures. This source/trace diagnosis is recorded without modifying the prompt, translating the final answer, replaying corrected actions or feeding task-specific hints back to the actor.

**Success reachability at this budget remains unestablished, not disproved.** One deterministic selected task/trial failed; this cannot establish that all 9B actors/tasks fail, that success is impossible, or a success-rate estimate. This run demonstrates substantial action reachability within spare budget, but no authentic successful actor-task receipt. The earlier `w-appworld` raw loss and historical 16/32-step zeros are retained; the released-predicate gold-answer controls in `w-awp` establish scorer positives only. None establishes full actor success. No budget increase or tuning is justified or performed here, and no further sampling was launched to search for a passing task.

## Lifecycle, resources, retained artifacts and comparison limits

`container-observations.jsonl` contains passive run-owned inspections; `role-observations.json` is their derived index. Actual image IDs:

- Actor `{roles['actor']['container_id']}`: `{roles['actor']['image']}`.
- Service `{roles['service']['container_id']}`: `{roles['service']['image']}`.
- Verifier `{roles['verifier']['container_id']}`: `{roles['verifier']['image']}`.

All three observed Docker configurations have NanoCpus=2000000000, Memory=4294967296 bytes, PidsLimit=1024. Actor/verifier root filesystems are read-only, with 512 MiB `/tmp` tmpfs; service root is writable. `live-cgroups.json` independently samples actor/service `cpu.max=200000 100000`, `memory.max=4294967296`, `pids.max=1024`; no live verifier cgroup file was sampled. The prior report's service lacked these caps; this worktree's inherited baseline already applies them. This evidence-only task did not add them. No filesystem quota enforcement is claimed.

`network-observations.jsonl` preserves the owned internal service network. All roles attach to `hg-{l['run_id']}-{l['task_id']}`; service recording is RW for the service and RO for the verifier, with no actor recording bind. `docker-events.jsonl` records actor/verifier exit 0 and destruction; service is killed during teardown after the verifier exits, exit 137 with `OOMKilled=false`. It is not classified as a scorer OOM or substituted with a task loss.

`cleanup-observations.json` records exact absent-after Docker inspections for all three role IDs and the owned network, no run-labeled objects, and temporary task/verdict directories absent. `cleanup-processes-after.json` records sampled host PIDs absent and the external work/run roots retained. These observations cover this run's roles, not an exhaustive daemon/namespace audit or a trusted platform lifecycle attestation. Boundary/interpreter preflight containers are outside this collector's run-owned identity filter.

All **{s['copied_run_files']}** original run files remain intact at the external run directory and have byte-identical committed review copies under `execution/`; `artifact-copy-provenance.json` records original/copy paths, lengths and recomputed hashes. Worktree staging and service recording remain retained. `packet-sha256.json` inventories final packet bytes. Endpoint sharing, unknown model weights, platform dirty state, unobserved production enforcement and the changed inherited service envelope preclude an equivalence or model-improvement claim against older runs. This task adds one failed raw observation only.

## Exact registry observation - w-appworld2

Only `appworld / successful-task-evidence` receives this new bounded observed suffix and report/journal evidence. Status remains `measurement`; family, next_action, historical runs, dataset taxonomy/shared references, shared blockers and production authorization remain unchanged.

Fresh unchanged-budget diagnostic `{l['run_id']}` selected deterministic study task `{l['task_id']}` from 147 eligible, one trial/jobs=1/rounds=0 on `http://127.0.0.1:8002/v1` (`qwen3.5-9b-local`). Raw official TGC was measured=true, success=false, score=0.0, six passes/two failures across eight requirements; the actor made an incorrect note edit and omitted supervisor completion. The actor submitted at step 15 after 16 model calls within its unchanged 32-step/2048-output-token budget; spare budget demonstrates action reachability but neither success nor impossibility. Formal staged score remains null, measured=0/unmeasured=1/invalid=0 for policy_enforcement_not_observed. No successful actor-task receipt exists in this attempt; successful-task-evidence remains OPEN. No shared blocker closes and no expansion is authorized.

Validation commands/output are retained in `reports/w-appworld2-validation.txt`; packet audit checks original/copy hashes, full packet identities, raw-vs-formal outcomes, unchanged runtime/shared/other-dataset records, verbatim evidence locators and journal heading. Registry source tests run without another model/benchmark execution.
'''
(ROOT/'reports/w-appworld2-receipts.md').write_text(report)
print('wrote reports/w-appworld2-receipts.md')
