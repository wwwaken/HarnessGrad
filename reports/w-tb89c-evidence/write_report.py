"""Derive the report and exact registry observation from preserved receipts."""
import json, pathlib
repo = pathlib.Path(__file__).resolve().parents[2]
packet = repo/'reports/w-tb89c-evidence'
def read(p): return json.loads(p.read_text())
s = read(packet/'result.json'); rows=s['rows']; batch=s['batch']; inv=s['inventory']
raw=s['raw_execution_coverage']; pub=s['publication_coverage_sum_of_one_task_selections']
prior=read(packet/'prior-tb89b-result.json'); assert prior['returncode']==0
prior=json.loads(prior['stdout'])
old={r['task_id']:r['raw_score'] for r in prior['rows'] if r['raw_measured']}
net=read(packet/'prior-openssl-result.json'); assert net['returncode']==0
net=json.loads(json.loads(net['stdout'])['stdout'])
assert net['ctrf_files'] and not net['invalid']; old.update(net['raw_per_task'])
assert not set(old).intersection(batch['selected'])
new=raw['measured_tasks']; cumulative=len(old)+new; total=inv['total_task_references']
observation=(f"Bounded live-local Terminal-Bench execution - w-tb89c: {len(rows)} preselected cached tasks ({', '.join(batch['selected'])}) ran serially through unchanged loop/train diagnostic admission, rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none and HG_EGRESS_PROXY=http://172.17.0.1:17890, bound to qwen3.5-9b-local at http://127.0.0.1:8002/v1. New raw official verifier coverage is {new}/{total}, cumulative {cumulative}/{total} unique tasks including the prior {len(old)} measured tasks. Raw ledger selected={raw['selected_tasks']}, expected_trials={raw['expected_trials']}, measured={new}, invalid={raw['invalid_tasks']}, unmeasured={raw['unmeasured_tasks']}; only tasks with official CTRF, command verdict and reward count. Native publication measured={pub['measured_tasks']}, invalid={pub['invalid_tasks']}, unmeasured={pub['unmeasured_tasks']}, all scores null; unknown policy enforcement remains unknown. Image/tool/input prerequisites were freshly checked for the fixed selection; {inv['cached_images']} images are cached, with {batch['cached_unselected']} cached tasks outside this selection not certified runnable. The three absent images were not executed or pulled. This is bounded online/proxy scorer execution, not offline closure, comparable benchmark performance, pilot expansion or production authorization. S1/S3/S4/S5/S6 remain PARTIAL; no shared or dataset blocker closes, and all statuses, next_actions, history, gates and production_authorized=false remain unchanged.")
text=f'''# Terminal-Bench bounded live-local execution receipts - w-tb89c

**New raw verifier coverage: {new}/{total}; cumulative unique coverage: {cumulative}/{total}.** The prior measured tasks are {', '.join(f'`{k}` ({v})' for k,v in sorted(old.items()))}. This batch adds only tasks supported by official CTRF and command/reward receipts. Shared and dataset blockers remain open; S4 remains PARTIAL. Raw verifier measurements are separate from withheld diagnostic publication.

## Selection and prerequisites fixed before execution

{batch['selection_rule']}

Fresh inventory: {total} task references, {inv['cached_images']} cached images. Missing images: {', '.join(inv['missing_images'])}. Their image inspections are read-only inventory checks; no missing image was pulled or executed. There are {len(batch['metadata_candidates'])} cached tasks meeting the CPU/memory/GPU/MCP/source/timeout metadata bounds, including the selected {len(rows)}. There are {len(batch['metadata_candidates'])-len(rows)} other metadata candidates and {batch['cached_unselected']} cached tasks outside this selection. Neither number certifies runtime readiness. Exactly {len(batch['prerequisite_verified'])} selected tasks passed fresh image tool/input probes; prerequisite-verified tasks left outside this fixed selection: {len(batch['prerequisite_verified_not_selected'])}. After the batch, no further prerequisite-verified task remains queued. No task reruns or result-dependent substitutions occurred.

`inventory-task-metadata-raw.json` preserves raw task.toml text for all inventory rows. `reports/w-tb89c-evidence/inventory.json` derives the inventory from `image-<task>.json`, preserving exact Docker inspection argv, return code, stdout and stderr. `prerequisite-<task>.json` preserves each `docker run --rm --pull=never --network none --read-only` probe against the inspected immutable image ID. These probes check shell/package-manager/tool availability and existing task inputs without running the official scorer or reading reference solutions. `shell-syntax-<task>.json` and `prepare.py` bind shell/Python parse checks; complete selected test/source preimages are retained. The preparation stderr retains an upstream Python escape-sequence SyntaxWarning; parsing succeeded. Host proxy probes returned HTTP 200 for the uv installer, pytest CTRF and GitPython indexes. Actual verifier execution supplies bootstrap evidence; no offline dependency closure is inferred from host probes.

The local model-list probe returned HTTP 200 and advertised `qwen3.5-9b-local`; `endpoint-models.json` preserves the raw body and status. Each task rechecked that model before launch. No model server was started; only the local endpoint was used.

## Per-task official raw results

| Task | Docker image ID | CTRF | Verdict / raw score | Official tests passed / total |
| --- | --- | --- | --- | --- |
'''
for r in rows:
    v=r['verifier_verdict'] or {}; t=v.get('tests',{})
    verdict=('pass' if v.get('passed') else 'fail') if r['raw_measured'] else ('invalid' if r['raw_invalid'] else 'unmeasured')
    text+=f"| `{r['task_id']}` | `{r['image_id']}` | {'Yes' if r['ctrf_produced'] else 'No'} | {verdict} / `{json.dumps(r['raw_score'])}` | {t.get('passed','n/a')} / {t.get('tests','n/a')} |\n"
text+='\nObserved RepoDigests (preserved separately from image IDs):\n\n'
for r in rows:
    text+=f"- `{r['task_id']}`: "+', '.join(f'`{d}`' for d in r['repo_digests'])+'\n'
text+='\n'
for r in rows:
    v=r['verifier_verdict'] or {}; failed=v.get('tests',{}).get('failed_names',[])
    text+=f"`{r['task_id']}`: "
    if r['raw_invalid']:
        text+=f"invalid: `{json.dumps(r['raw_invalid'],sort_keys=True)}`. No score is inferred from missing CTRF or reward bytes alone. "
    elif r['raw_measured']:
        text+=('Official failures: '+', '.join(f'`{n}`' for n in failed)+'. ' if failed else 'All reported official tests passed. ')
    else:
        text+=f"Unmeasured; native not-run data: `{json.dumps(r['raw_not_run'])}`. "
    text+=f"Driver return code: `{r['launch_observation']['returncode']}`. Full native result, bounded scorer detail, captured CTRF/reward and trace remain intact.\n\n"
text+=f'''Metric identity: `Terminal-Bench reward_file /logs/verifier/reward.txt`; official command `bash /tests/test.sh`, required report `/logs/verifier/ctrf.json`; scorer isolation class `snapshot-service`. `verifier-file-observations.json` records host-bind source, observed container, time, bytes and SHA-256 for read-only captures before ordinary teardown. A zero reward without CTRF is invalid, excluded from measured coverage. Provider, bootstrap, timeout, snapshot and cleanup failures are not converted into task scores.

## Counts and publication boundary

Raw execution ledger, derived from native execution/verdicts and captured bytes:

```json
{json.dumps(raw,indent=2)}
```

Native diagnostic publication coverage, summing separate one-task selections:

```json
{json.dumps(pub,indent=2)}
```

All publication scores are null. Measured raw outcomes remain `unmeasured` for publication with `policy_enforcement_not_observed`; any invalid outcome retains its native reason. Gate status remains `unknown`, receipt SHA-256 null, `production_authorized=false`. No curve, performance-comparable score or production admission is claimed. The cumulative numerator is the union of the prior measured task IDs and the new measured task IDs, with no overlap; `prior-tb89b-result.json` and `prior-openssl-result.json` preserve the exact `git show` output used for that union. Offline resolver/tooling coverage remains a separate scope.

## Exact invocation, model binding and serial execution

External runs root: `{batch['runs_root']}`. Fresh work roots and run IDs are listed below. Repository `runs/`, frozen receipts and the operator's checkout were not changed. Each `attempts/<task>/command.txt` is an exact executed command; each `launch-input.json` preserves argv and environment. The common recipe is:

```text
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=<one-task> HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence <fresh-evidence>/policy-input.json --authorize-unobserved-diagnostic <truthful-explicit-reason> --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id <fresh-id> --runs-root <external-runs-root> --work-root <fresh-external-work-root>
```

`--side train` satisfies the unchanged unobserved-diagnostic guard; `HG_TB_SPLIT=none` records split=null and claims no official train/eval split. Default harness settings were retained. Each gateway targets `127.0.0.1:8002`, and the native harness identity names the live local model/backend. Model-weight digest is unknown/null.

| Task | Fresh run ID | Work root |
| --- | --- | --- |
'''
for r in rows: text+=f"| `{r['task_id']}` | `{r['run_id']}` | `{r['work_root']}` |\n"
text+='\n| Task | Start UTC | End UTC | Model calls | Input / output tokens |\n| --- | --- | --- | --- | --- |\n'
for r in rows:
    o=r['launch_observation']; t=r['agent_tokens']
    text+=f"| `{r['task_id']}` | {o['started_at']} | {o['ended_at']} | {t['calls']} | {t['input']} / {t['output']} |\n"
text+='''
This worker launched one task/trial/job at a time; the driver intervals do not overlap. Preflight process snapshots observed no other platform driver. Repeated samples subsequently caught one other worktree pytest driver (`verify_demo`, run ID `vkind`) during the polyglot task. `concurrency-audit.json` preserves its exact sampled argv, sample paths/digests and raw `run_meta.json`: backend `mock`, agent model=null/base_url empty, no environment gateway/model and no method/improver model. It is a synthetic test, with no local model endpoint configured. `verify.py` requires this retained no-model proof for every foreign sampled driver and rejects any unaccounted driver. These observations are not an endpoint reservation and do not prove absence of arbitrary direct API clients. The initial overly broad receipt-audit assertion and failure output remain in `verify-pre-registry.stderr.txt`; this classification correction changed no platform gate, run or result. No operator process was started, stopped or modified. Timing is not a benchmark-performance result. Agent usage comes from the retained trial trace, including invalid traces; environment-service `env_usage` is a different account.

## Resource, snapshot, cleanup and provenance observations

'''
text+='| Task | Declared CPU / memory MiB | Agent / verifier timeout s | Actor / verifier last SizeRw bytes | Owned cleanup observed absent |\n| --- | --- | --- | --- | --- |\n'
for r in rows:
    e=r['declared_limits']['resource']; res=read(pathlib.Path(r['evidence_dir'])/'resource-observation-receipt.json')['roles']
    text+=f"| `{r['task_id']}` | {e['cpus']} / {e['memory_mb']} | {e['agent_timeout_s']} / {e['verify_timeout_s']} | {res.get('agent',{}).get('last_sample_size_rw')} / {res.get('verifier',{}).get('last_sample_size_rw')} | {r['cleanup_observed_absent']} |\n"
text+='''
The selected metadata declares no task GPU and storage_mb=10240. Resource receipts bind exact Docker inspections/stats and declared limits to the manifest. Both actor and verifier inspections record CPU/memory/swap/PID/rootfs settings and actual networks. Sampled SizeRw and Docker statistics are not peaks or trusted enforcement proofs; no filesystem quota is inferred. Budget and model-weight digest remain null. Snapshot receipts identify actually observed committed images with raw inspection path/digest; short-lived images can be missed. Cleanup receipts preserve scoped container/network/volume/snapshot listings and exact probes of observed containers/snapshots. Owned-object absence is observational teardown evidence, not atomic lease release or trusted production lifecycle attestation. Native lifecycle/publication fields remain unknown.

The documented proxy and declared bridge egress are retained. This is broader online/proxy official scorer execution, not a network-denied/offline scorer test. Official script hashes do not certify transitive package, image/ABI or rebuild custody. No scorer, task, test, reference solution, runtime, gate or admission code was changed.

| Task | Source-list SHA-256 | Split SHA-256 | Manifest SHA-256 | Official scorer script SHA-256 |
| --- | --- | --- | --- | --- |
'''
for r in rows: text+=f"| `{r['task_id']}` | `{r['hashes']['source']}` | `{r['hashes']['split']}` | `{r['hashes']['manifest']}` | `{r['scorer']['scorer_sha256']}` |\n"
text+='\nHarness-list SHA-256 per task: '+', '.join(f"`{r['task_id']}` = `{r['hashes']['harness']}`" for r in rows)+'.\n\n'
text+=f"Platform commit: `{read(packet/'platform-commit.json')['stdout'].strip()}`. Dataset commit: `{read(packet/'dataset-commit.json')['stdout'].strip()}`. Both command outputs and working-tree statuses are preserved. Per-task platform/harness/source lists and base64 preimages bind the actual bytes. The observer manifest is a pre-execution binding, not a production admission attestation.\n\n"
text+='''`run-artifact-inventory.json` preserves paths, sizes and recomputed hashes for retained external artifacts. Compact review copies live under `reports/w-tb89c-evidence/attempts/`; full repeated raw samples remain outside the platform. `SHA256SUMS` binds the review packet. `verify.py` validates byte custody, route/identity/count bindings, serial intervals, prerequisite receipts, prior/new task union and additive-only registry scope. Raw validation commands and output are in `reports/w-tb89c-validation.txt`. This worktree commit is for parent review and is not merged to main by this worker.

## Exact registry observation - w-tb89c

'''+observation+'\n'
(repo/'reports/w-tb89c-receipts.md').write_text(text)
(packet/'registry-observation.txt').write_text(observation+'\n')
print(json.dumps(dict(report='reports/w-tb89c-receipts.md',new_raw=new,cumulative_raw=cumulative,denominator=total),indent=2))
