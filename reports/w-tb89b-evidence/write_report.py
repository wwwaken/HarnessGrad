"""Write a receipt narrative with all result/count/digest values derived from collected JSON."""
import json,pathlib
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89b-evidence'
s=json.loads((packet/'result.json').read_text());rows=s['rows'];raw=s['raw_execution_coverage'];pub=s['publication_coverage_sum_of_four_one_task_selections'];inv=s['inventory'];batch=s['batch'];total=inv['total_task_references'];new=raw['measured_tasks']
prior=json.loads(json.loads((packet/'previous-official-result.json').read_text())['stdout'])
# Prior custody packet identifies one task; do not infer any other historical result.
assert prior['raw_per_task']=={'openssl-selfsigned-cert':0.0} and prior['verifier_verdict']['kind']=='command' and prior['ctrf_files'] and not prior['invalid']
obs=(f"Bounded live-local Terminal-Bench execution - w-tb89b: {len(rows)} preselected cached tasks ({', '.join(r['task_id'] for r in rows)}) ran serially through unchanged loop/train diagnostic admission, rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none and the documented proxy, against qwen3.5-9b-local at http://127.0.0.1:8002/v1. New raw official verifier coverage is {new}/{total}, cumulative {new+1}/{total} with prior openssl-selfsigned-cert; CTRF/raw rewards are retained for measured tasks; the CSV task is invalid because its required CTRF was absent. Raw ledger measured={new}, invalid={raw['invalid_tasks']}, unmeasured={raw['unmeasured_tasks']}. Native publication remains measured={pub['measured_tasks']}, invalid={pub['invalid_tasks']}, unmeasured={pub['unmeasured_tasks']} with score=null and policy_enforcement_not_observed. This is bounded online/proxy execution, not offline closure, benchmark-comparable performance, pilot expansion or production authorization. S1/S3/S4/S5/S6 remain PARTIAL; all shared/dataset statuses, next_actions, gates, history and production_authorized=false remain unchanged.")
text=f'''# Terminal-Bench bounded live-local execution receipts - w-tb89b

**Real raw verifier execution widened by {new} tasks: {new}/{total} new, {new+1}/{total} cumulative including the prior OpenSSL task.** Measured tasks produced official CTRF and reward through the unchanged platform route; invalid attempts are reported separately. Shared and dataset blockers stay open; S4 remains PARTIAL. Raw verifier scores below are distinct from the policy publication receipt: {pub['unmeasured_tasks']} trials remain unmeasured for publication, with `score=null` and `policy_enforcement_not_observed`.

## Selection fixed before execution

{batch['selection_rule']}

Fresh command-derived inventory: **{total} task references, {inv['cached_images']} cached images**, missing {', '.join(inv['missing_images'])}. The existing adapter's full reference pool is {total}; this is not an 86-task execution or a claim that all cached tasks can run. Requested selected coverage is {len(rows)}/{total}. Each individual driver sees exactly one eligible and selected task; summed native coverage below describes four separate one-task selections. No task reruns, substitutions, improver or method tuning occurred.

`inventory-images-raw.json` preserves the exact Docker command, exit status, stdout and stderr. `inventory.json` records the observed task metadata, immutable IDs and RepoDigests. `batch.json` fixes the four-task choice before the first model driver launch. Model-list verification returned HTTP 200 for `http://127.0.0.1:8002/v1/models` and advertised `qwen3.5-9b-local`; raw response is in `endpoint-models.json`, with another pre-run response per task. No second endpoint or paid service was used.

## Per-task raw official results

| Task | Docker image ID | CTRF | Verdict / raw reward | Official tests (passed / total) |
| --- | --- | --- | --- | --- |
'''
for r in rows:
 v=r['verifier_verdict'] or {};tests=v.get('tests',{});text+=f"| `{r['task_id']}` | `{r['image_id']}` | {'Yes' if r['ctrf_produced'] else 'No'} | {('pass' if v.get('passed') else 'fail') if v else 'invalid'} / `{json.dumps(r['raw_score'])}` | {tests.get('passed', 'n/a')} / {tests.get('tests', 'n/a')} |\n"
text+='\nObserved RepoDigests (distinct from Docker image IDs):\n\n'
for r in rows:text+=f"- `{r['task_id']}`: "+', '.join('`'+d+'`' for d in r['repo_digests'])+'\n'
text+='\n'
for r in rows:
 v=r['verifier_verdict'] or {};failed=v.get('tests',{}).get('failed_names',[])
 text+=f"`{r['task_id']}`: "+(('invalid prerequisite: '+str(r['raw_invalid'])) if r['raw_invalid'] else ('failed official tests '+', '.join('`'+n+'`' for n in failed) if failed else 'all reported official tests passed'))+'. '
 if r['raw_invalid']:
  text+=f"Driver exit `{r['launch_observation']['returncode']}` preserves this invalid attempt. No verifier verdict, CTRF assertion or numeric score exists; the native invalid reason and written reward bytes are retained.\n\n"
 else:
  text+=f"Driver exit `{r['launch_observation']['returncode']}` reflects the publication gate; raw verifier command kind is `{v.get('kind')}`. Full bounded verifier detail and CTRF assertion messages are preserved in its `result.json`, native execution and captured CTRF.\n\n"
text+=f'''Metric: `Terminal-Bench reward_file /logs/verifier/reward.txt`; actual official command `bash /tests/test.sh`, report `/logs/verifier/ctrf.json`, declared scorer class `snapshot-service`, also observed in measured verdicts. Raw reward files and CTRF were copied read-only from the verifier's host bind while present and before normal teardown; `verifier-file-observations.json` records source path, container ID, observation time, byte count and SHA-256. Full official test sources and instruction preimages are preserved externally; review copies are lossless base64-in-JSON preimages. No test, reference solution, gate or runtime source was changed.

## Raw execution counts and withheld publication

Raw ledger, derived from `diagnostic_execution.json`, verdicts, CTRF and reward bytes: selected={len(rows)}, expected trials={raw['expected_trials']}, measured tasks/trials={new}/{raw['measured_trials']}, invalid tasks={raw['invalid_tasks']}, unmeasured tasks={raw['unmeasured_tasks']}. Task failure with an official reward is a measurement; provider/bootstrap/timeout/cleanup failure would not be converted to zero. The CSV task lacks required `/logs/verifier/ctrf.json`: `stage=check`, `the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured`. It is invalid, has no verifier verdict or numeric score, and is excluded from the measured numerator. Its written `0\n` reward bytes alone do not establish a measured task failure. The retained invalid trace proves model execution, but the normal invalid-result serialization retains only the missing-report reason; it does not preserve the verifier subprocess streams. A deeper bootstrap/package cause is therefore unknown and is not invented.

Native diagnostic receipt coverage, summing the four one-task runs:

```json
{json.dumps(pub,indent=2)}
```

All publication scores are null. Measured raw tasks have publication outcomes `policy_enforcement_not_observed`; the CSV outcome is `invalid` with the exact missing-report reason. Gate status is truthfully `unknown`, receipt digest null, and operator authorization is explicit. `production_authorized=false`. No curve or comparable diagnostic score is claimed, and no diagnostic success is used to authorize a pilot. These observations do not certify S1/S3/S4/S5/S6 closure or all cached task scorers.

## Exact route and fresh identities

Runs root: `{batch['runs_root']}`. Native run artifacts, observer evidence and the preparation packets are left intact there; work roots are separate fresh `/tmp/` directories outside the platform. Repository `runs/`, historical/frozen receipts and the operator's main checkout were not modified.

Each task's external `<run-id>-evidence/command.txt` and review copy `reports/w-tb89b-evidence/attempts/<task-id>/command.txt` preserve its exact executed command. The common shape is the prior one-task invocation from `reports/w-net-receipts.md`:

```text
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=<one-task> HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence <fresh-evidence>/policy-input.json --authorize-unobserved-diagnostic <truthful-explicit-reason> --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id <fresh-id> --runs-root <external-runs-root> --work-root <external-fresh-work-root>
```

`train` is required by the unchanged unobserved-diagnostic guard; `HG_TB_SPLIT=none` means no official train/eval split is asserted. All model settings match the live binding. The model gateway records actual connections to `127.0.0.1:8002`, and the native harness identity names the requested model/backend. The default harness configuration is retained, with no task-specific tuning.

| Task | Fresh run ID | External work root |
| --- | --- | --- |
'''
for r in rows:text+=f"| `{r['task_id']}` | `{r['run_id']}` | `{r['work_root']}` |\n"
text+='\nSerial driver intervals (UTC) and observed model use:\n\n| Task | Start | End | Model calls | Input / output tokens |\n| --- | --- | --- | --- | --- |\n'
for r in rows:
 t=r['agent_tokens'];o=r['launch_observation'];text+=f"| `{r['task_id']}` | {o['started_at']} | {o['ended_at']} | {t['calls']} | {t['input']} / {t['output']} |\n"
text+='''
This worker ran one task at a time with `jobs=1`; the checked intervals do not overlap. Preflight `ps` also observed an existing operator MuSiQue `--jobs 20` run using the same endpoint. It was not started, stopped or changed by this worker. Consequently global endpoint exclusivity/concurrency is not attested, and timing/resource observations cannot be treated as uncontended benchmark performance. Raw process/GPU/container observations are preserved; this does not inflate Terminal-Bench task coverage.

An initial launcher preparation failed on a missing observer-inventory field (`KeyError: missing_source`) before any run ID or driver launch. That preparation packet and stderr remain intact; a corrected observer checks the actual required source files. It is not a task attempt, resumption or gate change. All actual model diagnostics use new IDs.

## Resource, lifecycle and provenance limits

Each task declares one CPU, 2048 MiB, no task GPU, 900-second agent and verifier timeouts. The task metadata also declares storage_mb=10240; no filesystem quota enforcement is inferred. Budget and model-weight digest remain null. Actor and verifier Docker inspections observe configured `NanoCpus=1000000000`, `Memory=2147483648`, `MemorySwap=4294967296`, `PidsLimit=1024` and writable roots; both keep their owned internal network and bridge, matching the existing declared-network route. These are observations of configuration, not trusted enforcement proofs. Docker statistics and SizeRw are samples, not peaks.

'''
text+='| Task | Actor last sampled writable bytes | Verifier last sampled writable bytes | Owned cleanup observed absent |\n| --- | --- | --- | --- |\n'
for r in rows:
 ev=pathlib.Path(r['evidence_dir']);res=json.loads((ev/'resource-observation-receipt.json').read_text());text+=f"| `{r['task_id']}` | {res['roles']['agent']['last_sample_size_rw']} | {res['roles']['verifier']['last_sample_size_rw']} | {r['cleanup_observed_absent']} |\n"
text+='''
Manifest-bound resource, snapshot and cleanup receipts name raw samples by exact path/digest. Scoped post-run container/network/volume/snapshot listings and exact probes of observed containers/snapshots show owned-object absence. This is normal teardown evidence, not atomic lease-release or production lifecycle attestation. Snapshot samples identify observed committed images; short-lived images may be missed. Work trees and receipts are retained.

Verifier launches were configured with the documented free proxy and declared bridge egress. This is broader real scorer execution, **not a network-denied/offline test**. `test.sh` content hashes bind the selected official scripts but do not establish their transitive package/ABI/image rebuild custody. For the invalid CSV task, native aggregate usage is zero because invalid tasks are excluded from that aggregate; the retained trial trace instead reports its actual usage, and `native-progress.json` retains its live relay counters. The table uses per-trial trace usage for every task. Model weights/version custody remains unknown beyond the responding served-model identity. Full portable runtime, all other task scorers, trusted enforcement, filesystem quota and production admission remain separate obligations.

Source and identity bindings, directly from each policy/manifest:

| Task | Source-list SHA-256 | Split SHA-256 | Manifest SHA-256 | Scorer script SHA-256 |
| --- | --- | --- | --- | --- |
'''
for r in rows:text+=f"| `{r['task_id']}` | `{r['hashes']['source']}` | `{r['hashes']['split']}` | `{r['hashes']['manifest']}` | `{r['scorer']['scorer_sha256']}` |\n"
text+='\nHarness-list SHA-256 per task: '+', '.join(f"`{r['task_id']}` = `{r['hashes']['harness']}`" for r in rows)+'.\n\n'
text+='''Platform source hashes and git revision, external dataset revision/status, selected source preimages, model-gateway counters, endpoint/model binding, proxy observations and launch argv/environment are retained in the packet. `run-artifact-inventory.json` hashes the retained external artifacts by path, bytes and SHA-256; `SHA256SUMS` covers the committed review packet; `verify.py` rederives raw/publication counts, validates captured bytes, model/image/context bindings, serial intervals and additive-only registry scope. Exact validation commands and raw output are in `reports/w-tb89b-validation.txt`. The worktree commit is for parent review; it is not merged to main by this worker.

## Exact registry observation - w-tb89b

'''+obs+'\n'
(repo/'reports/w-tb89b-receipts.md').write_text(text)
(packet/'registry-observation.txt').write_text(obs+'\n')
print('wrote reports/w-tb89b-receipts.md')
