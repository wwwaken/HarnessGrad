"""Write the report from saved artifacts; never infer a benchmark score."""
import json,pathlib
root=pathlib.Path('/tmp/hg-tbrun4'); out=root/'reports/w-tbrun4-evidence'
run_id='w-tbrun4-terminal-bench-20261014T195342Z-82530223'
run=root/'runs'/run_id; e=root/'runs'/(run_id+'-launch-evidence')
control=root/'runs/w-tbrun4-egress-control-20261014T195910Z-ec4ee67b'
def read(p): return json.loads(p.read_text())
def block(value): return '```json\n'+json.dumps(value,indent=2)+'\n```'
r=read(run/'diagnostic_receipt.json'); x=read(run/'diagnostic_execution.json'); result=read(e/'result.json')
p=read(e/'provenance.json'); resources=read(e/'resource-observation-receipt.json'); snap=read(e/'snapshot-observation-receipt.json'); launch=read(e/'launch-observation.json')
rows='\n'.join(f'| `{name}` | `{value}` |' for name,value in r['context']['hashes'].items())
limits={role:dict(observation_path=v['first']['source'],**v['first']['limits'],last_sampled_size_rw=v['last']['size_rw'],last_sample_path=v['last']['source']) for role,v in resources['roles'].items()}
control_values={mode:[json.loads(line) for line in read(control/(mode+'.json'))['stdout'].splitlines()] for mode in ('bridge','internal')}
text=f'''# w-tbrun4: proxy configured, real task executed, verifier still invalid

**OPEN: no valid verifier score; required `/logs/verifier/ctrf.json` is absent.** The real cached `openssl-selfsigned-cert` task ran with the local model, and its snapshot was checked in a fresh container. The configured proxy is present in the saved run metadata. The verifier wrote `0\\n` without CTRF, so this is a scorer nonmeasurement, not a measured failure or a score of zero. The run is preserved and the blocker remains open.

A concrete runtime network defect is now identified: `eval/containers/container_state.py:79` unconditionally creates an internal network, and `:216-217` passes it to the verifier instead of the task's declared `bridge`. `eval/service/services.py:245` creates that network with `--internal`. A separate no-model control reproduced `Network is unreachable` for the documented proxy on that network type. Per the instruction to stop at a genuine code defect, no second benchmark task/trial or code workaround was attempted.

## Exact launch and why these flags

Working directory: `{root}`. Exact saved command: `{e}/command.txt` (review copy [command.txt](w-tbrun4-evidence/launch/command.txt)).

```sh
{(e/'command.txt').read_text().strip()}
```

The previous reports at `/tmp/hg-tbrun/reports/w-tbrun-receipts.md`, `/tmp/hg-tbrun2/reports/w-tbrun2-receipts.md`, and `/tmp/hg-tbrun3/reports/w-tbrun3-receipts.md` were read before launch. The flag corrections are existing interfaces, not patches:

- `HG_TB_TASKS=openssl-selfsigned-cert` selects the cached task; `HG_TB_SPLIT=none` uses the adapter's supported undeclared split (`data/datasets/terminal_bench.py:288-289`). [selection.json](w-tbrun4-evidence/launch/selection.json) records the actual task list and `split=null`.
- `--rounds 0 --trials 1 --jobs 1` satisfies `eval/policy/diagnostic_policy.py:100-104`. No improver or tuning ran. No held-out claim is made.
- `--side train` is required by `driver.py:390-396` for this authorization; the suggested eval side would be refused. `loop_plain` lacks `env_kinds` and cannot run this exec environment; the existing `loop` descriptor declares `files` and `exec` ([harness-descriptor.json](w-tbrun4-evidence/launch/harness-descriptor.json)).
- `--policy-evidence` supplies the required context (`driver.py:402-413`) with gates honestly `unknown`; no admission evidence was invented. [policy-input.json](w-tbrun4-evidence/launch/policy-input.json) is the exact input.
- `HG_EGRESS_PROXY=http://172.17.0.1:17890` matches `docs/egress.md` and is intended for verifier processes only. [launch-input.json](w-tbrun4-evidence/launch/launch-input.json) records that environment; `{run}/run_meta.json` records `config.egress.proxy` with that same value.
- Fresh ID and external work root are preserved in `{e}/identity.json`. No old ID was resumed, no earlier run was overwritten, and no image set was pulled.

Selected image: `alexgshaw/openssl-selfsigned-cert:20251031`, also cached as `jevloop-tb:openssl-selfsigned-cert`. This task was retained because its official `tests/test.sh` downloads the uv installer from `astral.sh`, then runs pytest with `--ctrf`; it exercises the requested egress path. The exact original script, task metadata and Dockerfile are saved in `{e}/selected-verifier-test.sh`, `selected-task.toml`, and `selected-Dockerfile` (review copies under [launch/](w-tbrun4-evidence/launch)). No released solution was staged or consulted.

## Endpoint and proxy preflight

[endpoint-probe.json](w-tbrun4-evidence/launch/endpoint-probe.json) and [endpoint-models.json](w-tbrun4-evidence/launch/endpoint-models.json) preserve the responding model list from `http://127.0.0.1:8002/v1/models`. [endpoint-completion-probe.json](w-tbrun4-evidence/launch/endpoint-completion-probe.json) records HTTP `{read(e/'endpoint-completion-probe.json')['http_status']}` from the actual completion probe; [endpoint-completion-response.json](w-tbrun4-evidence/launch/endpoint-completion-response.json) records model `{read(e/'endpoint-completion-response.json')['model']}` and content `{read(e/'endpoint-completion-response.json')['choices'][0]['message']['content']}`. The request is preserved beside them. The execution binding is independently saved at `{run}/run_meta.json` → `config.agent`: `backend=openai`, `model=qwen3.5-9b-local`, `base_url=http://127.0.0.1:8002/v1`. No paid or second model endpoint was used.

Host proxy probes [proxy-astral.json](w-tbrun4-evidence/launch/proxy-astral.json) and [proxy-pypi.json](w-tbrun4-evidence/launch/proxy-pypi.json) each record `returncode=0`, `stdout="200"`, `stderr=""` for curl through the canonical proxy. Host success did not establish reachability from the task's actual internal network; that distinction matters below.

## Real execution, verdict and coverage

Original driver run: `{run}`. Launch evidence: `{e}`. External work root: `{read(e/'identity.json')['work_root']}`. [launch-observation.json](w-tbrun4-evidence/launch/launch-observation.json) records driver `returncode={launch['returncode']}` and both run/work-root existence checks `true`.

`{run}/events.jsonl` records agent, snapshot, verifier and teardown completion. `{e}/docker-events.jsonl` records a real `exec_start: bash /tests/test.sh` and its matching `exec_die` with `exitCode="0"` in verifier container `{resources['roles']['verifier']['first']['id']}`. Script exit success is not a task score: the official script writes its reward even when the tests cannot start.

[verifier-file-observations.json](w-tbrun4-evidence/launch/verifier-file-observations.json) preserves the observed fresh bind-mount reward. Exact source/copy/hash values:

{block(read(e/'verifier-file-observations.json'))}

The reward copy's bytes are `0\\n`. No CTRF report was captured. This is corroborated by the platform's definitive invalid reason in `{run}/diagnostic_execution.json`:

{block(x['invalid'])}

The complete saved raw scorer aggregates are `verdicts={json.dumps(x['verdicts'])}`, `per_task={json.dumps(x['per_task'])}`. Thus no valid verifier verdict or score survives. `eval/verification/verifier.py:369-370` detects the missing report; `eval/run/runner.py:1098-1111` classifies it invalid. The runner drops the full invalid verdict and its stdout/stderr, so the exact failed bootstrap command cannot be recovered from this task run. Network-control evidence below establishes a real reachability defect without claiming to recover those lost streams.

Coverage and score read directly from `{run}/diagnostic_receipt.json` ([review copy](w-tbrun4-evidence/execution/diagnostic_receipt.json)):

{block(dict(coverage=r['coverage'],score=r['score'],outcomes=r['outcomes']))}

`unmeasured_trials=0` is categorical accounting: this nonmeasurement is classified invalid. It does not mean the task was measured. The authorization independently records `measured=false`, `comparable=false`, `production_authorized=false`, `non_comparable_reason=policy_enforcement_not_observed`. A future valid raw reward would still be distinct from a publishable diagnostic measurement (`eval/policy/diagnostic_policy.py:181-186`). No curve exists (`{e}/result.json`, `curve_present=false`).

## Runtime network defect and no-model reproduction

The real task's saved declared environment is `network="bridge"` in `{e}/selection.json`. Its actual verifier `HostConfig.NetworkMode`, saved in `{resources['roles']['verifier']['first']['source']}`, is the owned internal network `{next(iter(resources['roles']['verifier']['first']['networks']))}`. The code paths are:

- `eval/containers/container_state.py:76-79`: unconditional `services_mod.create_network(...)`.
- `eval/service/services.py:245-247`: `docker network create --internal`.
- `eval/containers/container_state.py:213-218`: verifier receives that internal `network_name`; the adapter's declared `network` is used only if `network_name` is null, which this path never leaves it.
- `eval/verification/verifier.py:287-288,309-312`: creates the verifier on the supplied network and correctly passes `_check_env()` to its process. `_check_env` contains the proxy flags, but does not create a route to the proxy.

The isolated no-model control is preserved under `{control}` (direct review copies [network-control/](w-tbrun4-evidence/network-control/)). [network-control.py](w-tbrun4-evidence/network-control.py) is the exact observer tool. `identity.json` states `model_calls=false`. It runs Python URL requests in the same cached image, with explicit proxy `http://172.17.0.1:17890`, once on the default bridge and once on a newly owned `--internal` network. It runs no task, verifier, solution, model or scorer and produces no benchmark score. Exact commands, streams and route-table readouts are in `bridge.json` and `internal.json`; `network-inspect.json` records `Internal=true`.

Raw URL observations, retaining the important host/container distinction:

{block({k:v[1:] for k,v in control_values.items()})}

Both internal-network requests fail with `[Errno 101] Network is unreachable`, and its saved `/proc/net/route` has no default route. The bridge control reaches PyPI; its Python request for the uv installer receives HTTP 403 even though the host curl preflight got HTTP 200. That separate HTTP difference is not resolved or relabelled as success. Either way, the actual verifier's internal network cannot reach the configured bridge proxy. No model rerun, alternate task, network attachment, temporary forwarder, or production-code fix was attempted after finding this defect.

The control's `network-remove.json` records the real removal command result. Its `containers-after.json` and `networks-after.json` record empty owned listings. These are control cleanup observations, not task score or admission receipts.

## Manifest, image and provenance receipts

A pre-execution observer manifest `{e}/launch-manifest.json` binds selection, image ID, source/harness file manifests, split, endpoint, resources, work root and run identity. Its actual SHA-256 is carried into the driver's `staged_plan.json`, `run_meta.json` and `diagnostic_receipt.json` as `context.hashes.manifest`, and all observer receipts use the same binding. This is an observer-authored manifest, not an invented production admission attestation.

Raw context hashes from the diagnostic receipt:

| Identity | Raw SHA-256 or unknown |
| --- | --- |
{rows}

`source-files.json`, `split-selection.json` and `harness-files.json` are the exact bytes hashed for those fields. [provenance.json](w-tbrun4-evidence/launch/provenance.json) records:

{block(p)}

The model weight digest remains unknown. The script digest binds the official test script only; transitive online dependencies are not claimed pinned or offline-closed.

[image-observation-receipt.json](w-tbrun4-evidence/launch/image-observation-receipt.json) binds the real cache inspection and launched images. `{e}/image-inspect.json` records both cache aliases with ID `{read(e/'image-observation-receipt.json')['cache_images'][0]['id']}` and the exact `RepoDigests` retained in that receipt. The task's `run_meta.json` environment and sampled Docker `Image` agree. The verifier's actual snapshot image is:

{block(snap['snapshots'])}

## Resource and cleanup receipts, with uncertainty retained

The manifest-bound observer receipts below exist at the original paths and as direct review copies. Each embeds raw-file paths and SHA-256 values; their own hashes are recorded in `{e}/result.json`:

{block(result['observation_receipts'])}

[resource-observation-receipt.json](w-tbrun4-evidence/launch/resource-observation-receipt.json) preserves declared limits `{json.dumps(r['context']['limits'])}`, real Docker configuration readouts, and every saved statistics sample path. Compact raw readouts:

{block(limits)}

`SizeRw` values are last samples, not peak usage; `NanoCpus`, `Memory`, `MemorySwap` and `PidsLimit` are Docker configurations. No filesystem quota, trusted resource admission or peak-resource attestation is claimed. Budget remains `null` in the saved policy context. The task's harness/progress output and trace are preserved in `{run}/progress/round-0/`, including the usage-bearing invalid trace.

[snapshot-observation-receipt.json](w-tbrun4-evidence/launch/snapshot-observation-receipt.json) records the real snapshot image above. [cleanup-observation-receipt.json](w-tbrun4-evidence/launch/cleanup-observation-receipt.json) records exact inspected container/snapshot absence and scoped object listings. `containers-after.json`, `networks-after.json`, `snapshot-images-after.json`, plus final container/network/volume listings, each have `returncode=0`, `stdout=""`, `stderr=""`. Exact container probes `container-exact-after-00.json` and `container-exact-after-01.json` return `1`, `stdout="[]\\n"`, and `no such object`; `snapshot-exact-after-00.json` returns `1` with `No such image`. The complete raw error strings and IDs are in those files, and Docker destroy events remain in `docker-events.jsonl`.

These observations establish no surviving selected Docker objects were found by those probes. They do not attest atomic lease release. Driver `cleanup.status="unknown"`, `snapshot.status="unknown"`, their `receipt_sha256=null`, and `lifecycle=null` are retained unchanged. `docs/enforcement-proof-decision.md` accepts uncertainty alone as a standing limit; it does not repair the missing verifier report or score. No admission receipt was synthesized to claim success.

Original task artifacts remain intact under the runs root. [artifact-inventory.json](w-tbrun4-evidence/artifact-inventory.json) inventories every original task/launch file by path, byte count and digest; [run-artifacts.tar.gz](w-tbrun4-evidence/run-artifacts.tar.gz) is the complete byte-for-byte review archive, with its identity in [archive-sha256.json](w-tbrun4-evidence/archive-sha256.json). [network-control-inventory.json](w-tbrun4-evidence/network-control-inventory.json) separately inventories the control. Raw sample review copies are compacted into the archive; their original runs-root files are untouched. All historical attempts and archives remain untouched.

## Disposition, comment fix and validation

`terminal_bench / cached-runtime-admission` remains open. The registry observation is updated to the actual proxy-configured attempt and the precise network defect. The missing artifact is `/logs/verifier/ctrf.json`, so no valid score exists. A real manifest is now bound and image/resource/snapshot/cleanup observation receipts exist; absence of an infallibility proof is not introduced as a new blocker. Shared `scorer-offline-closure` and `artifact-only-state-export` remain attached. No pilot expansion or production authorization follows.

The only production-file diff is the requested comment at `eval/verification/verifier.py:89-91`: canonical port `17890`, with a citation to `docs/egress.md`. Executable behavior, harnesses, adapter, network implementation and scorer are unchanged. No existing test specifically pins this Terminal-Bench registry entry or its current observation; its status remains open, so no pinned test changes are required.

[reports/w-tbrun4-validation.txt](w-tbrun4-validation.txt) preserves exact checker and focused test commands and complete outputs. The initial checker returned `valid=true`, `datasets=28`, `shared_blockers=2`, `historical_records=11`, `production_authorized=false`, exit code `0`. The focused registry, diagnostic authorization/policy, split, verifier, container-state and terminal-artifact suites returned `255 passed in 26.97s`, exit code `0`. Post-edit checker/registry validation and archive integrity results are appended there before commit. Pytest temporary roots are outside the platform. The unique journal entry ends in ` - w-tbrun4`. Changes are committed only in this registered isolated worktree; no main commit or merge is performed.
'''
(root/'reports/w-tbrun4-receipts.md').write_text(text)
