"""Write a raw-derived receipt report; keep missing native receipts explicit."""
import json,pathlib
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89d-evidence'
read=lambda p:json.loads(p.read_text())
s=read(packet/'result.json');rows=s['rows'];batch=s['batch'];inv=s['inventory'];raw=s['raw_execution_coverage'];pub=s['publication_coverage_sum_of_one_task_selections'];available=read(packet/'availability-all.json');timeouts=[r for r in rows if r['agent_timeout_observed']]
old=available['prior_unique_measured'];new=raw['measured_tasks'];total=inv['total_task_references'];cumulative=len(old)+new
assert not set(old)&{r['task_id'] for r in rows};assert total==len(read(packet/'inventory.json')['rows'])
obs=(f"Bounded live-local Terminal-Bench execution - w-tb89d: {len(rows)} new cached task surfaces were preselected across an initial five-task selection and a supplemental two-task pip-bootstrap selection, all launched serially with unchanged loop/train diagnostic admission, rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none, HG_EGRESS_PROXY=http://172.17.0.1:17890 and direct qwen3.5-9b-local at http://127.0.0.1:8002/v1. New measured raw official verifier coverage is {new}/{total}; cumulative unique coverage is {cumulative}/{total} including the prior {len(old)}. Observer-recorded agent timeouts={len(timeouts)}, excluded from valid raw coverage even when a native scorer reward exists. Raw ledger selected={raw['selected_tasks']}, expected_trials={raw['expected_trials']}, measured={raw['measured_tasks']}, invalid={raw['invalid_tasks']}, unmeasured={raw['unmeasured_tasks']}; only command verdicts with official CTRF and reward count. Four initial native executions lacked CTRF and remain invalid; the fifth initial attempt was interrupted before a final native receipt and is excluded, with its trace preserved and exactly owned orphan resources cleaned. A no-model probe failed to download the pinned uv release through the proxy; the supplemental tasks passed full pinned pip dependency smoke checks before model trials. Initial attempts were retained, never replaced, resumed or rerun. Native publication coverage is available for {s['native_execution_receipts']} attempts: measured={pub['measured_tasks']}, invalid={pub['invalid_tasks']}, unmeasured={pub['unmeasured_tasks']}, observed scores null; {s['missing_native_receipts']} interrupted attempt has no native publication receipt. Inventory is {inv['cached_images']}/{total} images cached; the three absent images were not pulled or executed. Outside these selections {available['cached_new_outside_batch']} cached tasks have no prior measured coverage, including {available['metadata_new_outside_batch']} metadata-bounded candidates, with zero further prerequisite-verified tasks queued. This is bounded online/proxy execution evidence; complete offline closure, comparable performance, pilot expansion and production authorization are not established. S4 remains PARTIAL; no shared or dataset blocker closes, and all statuses, next_actions, history, gates and production_authorized=false remain unchanged.")
text=f'''# Terminal-Bench bounded live-local verifier receipts - w-tb89d

**New measured raw coverage: {new}/{total}; cumulative unique coverage: {cumulative}/{total}.** Only official command verdicts accompanied by the required CTRF and reward contribute. The prior unique measured IDs are {', '.join('`'+x+'`' for x in old)}. Raw measurements remain separate from policy-withheld publication. No shared or dataset blocker is closed; S4 remains PARTIAL.

## Selection, prerequisites and runnable remainder

The initial fixed five tasks were `log-summary-date-ranges`, `write-compressor`, `gcode-to-text`, `git-multibranch` and `sqlite-db-truncate`, covering date-range aggregation, constrained compression, G-code interpretation, SSH/Git deployment and truncated-database recovery. `batch.json` was fixed before their model trials. All passed cached image inspection, complete official source checks, shell/Python parsing and read-only network-disabled tool/input probes, with task GPU=0, no MCP, CPU<=1, memory<=2048 MiB and declared agent/verifier timeouts<=900 seconds. The initial host installer/index probes did **not** establish transitive dependency readiness: four runs later lacked CTRF, and the fifth was interrupted.

A separate no-model bootstrap probe installed ordinary dependencies in a disposable image and attempted the pinned uv download. It failed with `curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to github.com:443`; the host release-archive probe also failed at `release-assets.githubusercontent.com:443`. Raw argv, streams, image ID, limits and cleanup are in `bootstrap-prerequisite-result.json`, `github-uv-release-probe.json` and their external artifact directories. This identifies a live dependency gap; the four original invalid native records retain only their missing-CTRF reason, so this separate probe is not presented as captured stderr from those original runs.

Two additional tasks, `fix-code-vulnerability` and `kv-store-grpc`, were separately preselected in `batch-supplement.json` before either model trial. Their official scorers use pip directly. Besides the same image/source/tool/resource checks, disposable no-model containers installed the exact pinned pytest/CTRF and relevant gRPC dependencies, checked pytest's `--ctrf` option and queried installed versions/imports. No official tests, reference solutions, answers or model were used in dependency probes. The first probe mistakenly tried to import the distribution name as a Python module; its raw failure is retained, and the corrected probe checks installed distribution metadata and the actual pytest option. The observation-script syntax correction and its raw error are also retained. Neither changes task/runtime/admission behavior.

The total selection is {len(rows)} distinct new task IDs, within the recorded nine-task bound. No initial task is replaced or rerun. Fresh inventory: {total} references, {inv['cached_images']} cached images, missing {', '.join('`'+x+'`' for x in inv['missing_images'])}. Missing images were inspected only, never pulled or executed. There are {len(batch['metadata_candidates'])} metadata-bounded cached candidates. Before this work, {available['cached_not_previously_measured']} cached tasks had no measured coverage. Outside both selections remain {available['cached_new_outside_batch']} such cached tasks, including {available['metadata_new_outside_batch']} metadata-bounded candidates; their runtime readiness is unverified. Exactly two supplemental tasks had successful end-to-end dependency smoke checks before launch. After execution, prerequisite-verified tasks still queued: {available['remaining_certified_queue_after_fixed_batch']}. Initial local probes alone are not relabeled complete dependency readiness.

Raw command outputs live in `inventory-task-metadata-raw.json`, every `image-<task>.json`, `prerequisite-<task>.json`, `shell-syntax-<task>.json` and `dependency-bootstrap-<task>*.json`. `availability-all.json` derives the historical/new ID sets and remainder counts. The selected tests and metadata are preserved as hash-bound preimages.

## Per-task results

| Task | Inspected Docker image ID | CTRF | Raw verdict / score | Required CTRF passed / total |
| --- | --- | --- | --- | --- |
'''
for r in rows:
 v=r['verifier_verdict'] or {};t=v.get('tests',{});kind=('pass' if v.get('passed') else 'fail') if r['raw_measured'] else ('invalid' if r['raw_invalid'] else 'unmeasured')
 text+=f"| `{r['task_id']}` | `{r['image_id']}` | {'Yes' if r['ctrf_produced'] else 'No'} | {kind} / `{json.dumps(r['raw_score'])}` | {t.get('passed','n/a')} / {t.get('tests','n/a')} |\n"
text+='\nObserved RepoDigests, preserved separately from image IDs:\n\n'
for r in rows:text+='- `'+r['task_id']+'`: '+', '.join('`'+d+'`' for d in r['repo_digests'])+'\n'
text+='\n'
for r in rows:
 text+='`'+r['task_id']+'`: '
 if r['raw_invalid']:text+='invalid reason: `'+json.dumps(r['raw_invalid'],sort_keys=True)+'`. '
 elif r['raw_measured']:
  failed=(r['verifier_verdict'].get('tests') or {}).get('failed_names',[])
  text+=('Failed official checks: '+', '.join('`'+f+'`' for f in failed)+'. ') if failed else 'All checks in the required CTRF passed. '
 else:text+='Unmeasured exclusion: `'+json.dumps(r['raw_exclusion_reason'])+'`. '
 text+=f"Native driver return code: `{json.dumps(r['launch_observation']['returncode'])}`. "
 if r['interrupted']:text+='The launcher returned 143; the driver exit code and final native result are unknown. The partial actor trace was captured before scoped orphan cleanup; no task or old ID was resumed. '
 if r['agent_timeout_observed']:text+='Agent timeout is retained as an observer-invalid diagnostic; native scorer reward `'+json.dumps(r['native_raw_score'])+'` and any CTRF remain visible, without converting the timeout into a task score. '
 text+='Full retained native/observer artifacts and exact commands are indexed by the artifact inventory.\n\n'
text+='''Metric identity: `Terminal-Bench reward_file /logs/verifier/reward.txt`; official command `bash /tests/test.sh`; required report `/logs/verifier/ctrf.json`; declared/observed measured scorer class `snapshot-service`. A reward of zero with no CTRF is invalid and excluded. Provider, timeout, scorer, interruption, snapshot and cleanup failures are never inferred to be ordinary zero scores. Explicit observed agent timeouts are excluded from valid raw coverage even when the unchanged platform subsequently runs the verifier and retains a native reward; those native values are preserved separately. The Bottle scorer runs its original repository tests and the additional `/tests/test_outputs.py` suite; the table counts the required additional-suite CTRF, while the official reward combines both exit codes. No complete original-suite CTRF tally is claimed.

'''
text+=f'''## Counts and publication boundary

Raw execution ledger:

```json
{json.dumps(raw,indent=2)}
```

Native publication coverage, summed only over the {s['native_execution_receipts']} completed one-task native receipts:

```json
{json.dumps(pub,indent=2)}
```

The interrupted attempt has no final native execution or diagnostic receipt; missing native receipts={s['missing_native_receipts']}. It is included as an observer-classified invalid/missing-CTRF attempt in the raw ledger, with no invented native outcome or score. The native `eligible_tasks` count belongs to completed one-task HG_TB_TASKS selectors; it does not certify all {total} inventory tasks as runnable. Observer-excluded agent-timeout attempts={len(timeouts)}; native publication records are preserved verbatim even when their reason only names unknown policy enforcement. All observed publication scores are null. Valid raw measurements remain publication-unmeasured with `policy_enforcement_not_observed`; native invalid reasons remain invalid. The native gRPC publication receipt independently marks the agent timeout invalid, while retaining its scorer verdict in execution artifacts. Unknown gate/enforcement/lifecycle observations stay unknown, and no production authorization or comparable curve is claimed.

The cumulative numerator is the union of the prior {len(old)} unique measured IDs and these newly measured IDs: {', '.join('`'+r['task_id']+'`' for r in rows if r['raw_measured']) or '(none)'}. `prior-tb89c-result.json`, `prior-tb89b-result.json`, `prior-openssl-result.json` and `availability-all.json` preserve/derive this union from exact retained git command outputs.

## Invocation, seriality and endpoint binding

The local `/models` probe returned HTTP 200 and advertised `qwen3.5-9b-local`; the local chat-completion probe returned HTTP 200 and `OK`. Both raw responses are retained. Each actual task rechecked the model list. No model server was started and worker model calls used only `http://127.0.0.1:8002/v1`.

Each `attempts/<task>/command.txt` and `launch-input.json` preserves the exact executed command and environment. The common invocation is:

```text
env HG_EGRESS_PROXY=http://172.17.0.1:17890 HG_TB_TASKS=<single-task> HG_TB_SPLIT=none HG_AGENT_BACKEND=openai HG_AGENT_MODEL=qwen3.5-9b-local HG_AGENT_BASE_URL=http://127.0.0.1:8002/v1 HG_AGENT_API_KEY=local python3 driver.py --harness loop --dataset terminal_bench --sampling diagnostic --policy-evidence <fresh-policy-input> --authorize-unobserved-diagnostic <truthful-bounded-coverage-reason> --rounds 0 --trials 1 --jobs 1 --side train --improver none --run-id <fresh-id> --runs-root <external-root> --work-root <fresh-external-work-root>
```

`--side train` satisfies the unchanged unobserved-diagnostic guard. `HG_TB_SPLIT=none` records split=null; no official train/eval split is asserted. Harness defaults and method configuration were unchanged. Model-weight digest and budget remain unknown/null.

External run roots:

'''
for root in batch['runs_roots']:text+='- `'+root+'`\n'
text+='\n| Task | Fresh run ID | External work root |\n| --- | --- | --- |\n'
for r in rows:text+=f"| `{r['task_id']}` | `{r['run_id']}` | `{r['work_root']}` |\n"
text+='\n| Task | Start UTC | End / cleanup observation UTC | Agent model calls | Input / output tokens |\n| --- | --- | --- | --- | --- |\n'
for r in rows:
 o=r['launch_observation'];t=r['agent_tokens'] or dict(calls='unknown',input='unknown',output='unknown')
 text+=f"| `{r['task_id']}` | {o['started_at']} | {o['ended_at']} | {t['calls']} | {t['input']} / {t['output']} |\n"
text+='''
Worker concurrency was one; execution/cleanup intervals do not overlap. The pre-existing operator MuSiQue driver used port 8010, whose read-only observed proxy source forwards to 8001/8002. `operator-routing-observation.json`, per-run `operator-run-meta.json` and `concurrency-audit.json` retain the route and sampled process proof. The user permits operator sharing; endpoint exclusivity and timing comparability are not claimed. No operator process or server was started, stopped or changed.

An initial observer-only preflight stopped before any task driver/admission because it treated all foreign drivers as exclusive conflicts. The unused ID and raw refusal/source remain intact. Accounting for explicitly permitted operator sharing changed only the observer, with no platform gate, admission or refusal changed. Actual trials used fresh IDs. Later the initial launcher session returned 143 during `sqlite-db-truncate`; the cause and driver exit status were unobserved. The driver was absent, its container remained, and no final native receipt existed. `interrupted-run-disposition.json`, `launcher-terminal-observation.json` and external `interruption-cleanup/` preserve that distinction, the bounded partial artifact capture, scoped/exact owned cleanup and absence probes. The supplemental launcher used a new process session and new IDs. No old run was resumed.

Agent spend comes from completed retained trace usage records, including native-invalid traces. Partial trace spend remains unknown. Native aggregates are retained separately because invalid traces can be omitted from their token totals; environment-service `env_usage` is also a separate account.

## Resources, cleanup and provenance

| Task | CPU / memory MiB | Agent / verifier timeout s | Last actor / verifier SizeRw bytes | Owned objects observed absent |
| --- | --- | --- | --- | --- |
'''
for r in rows:
 lim=r['declared_limits']['resource'];res=read(pathlib.Path(r['evidence_dir'])/'resource-observation-receipt.json')['roles']
 text+=f"| `{r['task_id']}` | {lim['cpus']} / {lim['memory_mb']} | {lim['agent_timeout_s']} / {lim['verify_timeout_s']} | {res.get('agent',{}).get('last_sample_size_rw','unobserved')} / {res.get('verifier',{}).get('last_sample_size_rw','unobserved')} | {r['cleanup_observed_absent']} |\n"
text+='''
Task metadata also declares storage_mb=10240 and GPU=0. Actual Docker inspections retain CPU/memory/swap/PID/rootfs/network settings; SizeRw/statistics are samples, with no peak or filesystem-quota proof inferred. Snapshot receipts bind observed committed images and their exact inspection paths/hashes; short-lived images may be missed. The interrupted attempt never produced an observed verifier snapshot. Scoped/exact absence probes are teardown observations, with no trusted atomic lease release or lifecycle/admission attestation inferred. Resource, snapshot and cleanup observations are manifest-bound; native unknown lifecycle fields remain unknown.

This is online/proxy scorer execution. Script hashes and installed dependency smoke checks do not establish complete portable offline, image/ABI or transitive rebuild custody. No task, official scorer/test, reference solution, production runtime, method, gate or admission code was changed. Repository `runs/`, frozen receipts and the operator checkout remain untouched.

| Task | Source-list SHA-256 | Split SHA-256 | Manifest SHA-256 | Official scorer script SHA-256 |
| --- | --- | --- | --- | --- |
'''
for r in rows:text+=f"| `{r['task_id']}` | `{r['hashes']['source']}` | `{r['hashes']['split']}` | `{r['hashes']['manifest']}` | `{r['scorer']['scorer_sha256']}` |\n"
text+='\nHarness-list hashes: '+', '.join('`'+r['task_id']+'` = `'+r['hashes']['harness']+'`' for r in rows)+'.\n\n'
text+=f"Platform commit: `{read(packet/'platform-commit.json')['stdout'].strip()}`. Dataset commit: `{read(packet/'dataset-commit.json')['stdout'].strip()}`. Command outputs/statuses and actual platform/source/harness content hashes are retained. Each observer manifest binds bytes before execution and is explicitly not production admission evidence.\n\n"
text+='''`run-artifact-inventory.json` binds every retained file in both external roots by path, size and recomputed SHA-256. Compact review copies are under `reports/w-tb89d-evidence/attempts/`; repeated samples, raw host snapshots and original work/run artifacts remain external and intact. `SHA256SUMS` binds the review packet/report. `verify.py` audits source/hash/route/count custody, CTRF/reward agreement, interruption treatment, serial execution, the historical/new union and additive-only registry scope. Raw checker, audit and focused test output is in `reports/w-tb89d-validation.txt`. Commit is only in this registered worktree for parent review; main is untouched.

## Exact registry observation - w-tb89d

'''+obs+'\n'
(repo/'reports/w-tb89d-receipts.md').write_text(text);(packet/'registry-observation.txt').write_text(obs+'\n')
print(json.dumps(dict(new_raw=new,cumulative_raw=cumulative,denominator=total,native_receipts=s['native_execution_receipts'],missing_native_receipts=s['missing_native_receipts']),indent=2))
