"""Derive all counts/digests from executed receipts, then append observation only."""
import json
from pathlib import Path
from common import HERE, ROOT, save

read=lambda p:json.loads(Path(p).read_text())
prior=read(ROOT/'tests/fixtures/hg_wresolver4/summary.json')
artifacts=read(HERE/'artifacts.json')['artifacts']
result=read(HERE/'result.json')
selected=read(HERE/'selection.json')['selected']
source=read(HERE/'source.json')
literal=read(HERE/'context-literals.json')
tbhere=ROOT/'tests/fixtures/hg_wresolver5_tb'
tb=read(tbhere/'results.json')
tbinputs=read(tbhere/'inputs.json')
remainder=read(HERE/'remainder.json')
assert result['exit_code']==result['install']['exit_code']==result['check']['exit_code']==0
assert result['negative']['exit_code']==1
assert all(r['exit_code']==r['install']['exit_code']==r['check']['exit_code']==0 and r['negative']['exit_code']==1 for r in tb.values())
summary=dict(prior_bounded_profiles=prior['bounded_profiles'],prior_complete_nonempty_python_profiles=prior['complete_nonempty_python_profiles'],
     new_bounded_profiles=1+len(tb),bounded_profiles=prior['bounded_profiles']+1+len(tb),bounded_profiles_resolved=prior['bounded_profiles_resolved']+1+len(tb),
     complete_nonempty_python_profiles=prior['complete_nonempty_python_profiles']+1,shared_datasets=prior['shared_datasets'],
     no_third_party_payload=remainder['na_count'],remaining_datasets=sorted([*remainder['datasets'],'terminal_bench']),
     ds1000_selected_distributions=len(selected),ds1000_candidate_bytes=sum(a['bytes'] for a in artifacts),
     ds1000_static_context_rows=source['rows'],ds1000_direct_import_roots=len(source['import_roots']),
     new_tb_bootstrap_profiles=len(tb),tb_demonstrated_bootstrap_profiles=prior['tb_demonstrated_tasks']+len(tb),tb_tasks=remainder['terminal_task_count'],
     tb_undemonstrated_tooling_routes=remainder['terminal_task_count']-prior['tb_demonstrated_tasks']-len(tb),
     new_refusals=1+len(tb),selected_distributions={'ds1000':len(selected),**{n:len(r['selected']) for n,r in tb.items()}},
     production_authorized=False,
     meaning='Finite source-scoped Python metadata reconstruction. DS1000 covers declared Python roots plus all released direct/static-literal context imports, preserving version pins and Python3.10 with an explicit CPU PyTorch mapping. Terminal-Bench additions are host3.12 bootstrap tooling only. No native/Conda/image/ABI/runtime equivalence, scorer execution or blocker closure.')
save(HERE/'summary.json',summary)
print(json.dumps(summary,sort_keys=True,indent=2))
missing=read(HERE/'raw/negative-inventory.json')['omitted'][0]
observation=(f"Resolver profile extension 2026-10-15 - w-resolver5: DS1000's finite declared/static-import Python metadata profile passes kernel-network-denied dependency-aware resolution, hash-required installation and pip check on CPython 3.10.12, selecting {len(selected)} distributions. A metadata-only AST pass over {source['rows']} released code_context fields records exact JSONL/context import lines and hashes without exporting prompts, gold/reference code or task/test bodies; parseable import-bearing literal strings add no distribution outside the declared union. Original version pins are preserved. Conda pytorch==2.2.0 plus cpuonly maps explicitly to the official torch==2.2.0+cpu wheel for Python metadata only; Conda yaml/native libyaml custody remains a gap and actual import yaml is supplied by PyYAML. Removing {missing['name']}=={missing['version']} after installation produces ResolutionImpossible/exit 1. Three distinct selected Terminal-Bench direct-pip bootstrap profiles (build-cython-ext, headless-terminal, hf-model-inference) pass the same host CPython 3.12.4 checks, selecting "+'/'.join(str(len(tb[n]['selected'])) for n in sorted(tb))+" distributions; each missing pluggy==1.6.0 refuses. These are tooling reconstructions, not full task/image graphs. Updated cumulative scope is "+f"{summary['bounded_profiles_resolved']}/{summary['bounded_profiles']} bounded profiles and {summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']} complete nonempty dataset Python metadata profiles, carrying merged w-resolver4 receipts forward explicitly. Terminal-Bench has {summary['tb_demonstrated_bootstrap_profiles']}/{summary['tb_tasks']} demonstrated task tooling routes; no success is extrapolated to duplicate bootstraps. Remaining {len(summary['remaining_datasets'])} datasets are nine stdlib-only N/A routes and incomplete Terminal-Bench task/image/native graphs. All payloads/index bodies/bulk dumps remain outside git; compact text receipts contain URLs, filenames, sizes, recomputed hashes and re-fetch scripts. Initial redundant acquisition was SIGTERMed (exit 143); two unflushed-small-index digest errors are preserved and independently corrected, not treated as artifact absence. No artifact is declared unobtainable. No benchmark task, official scorer, container, model, endpoint, GPU or server is executed. No shared/dataset blocker closes; all statuses, full next_actions, dataset/history records, gates and production_authorized=false remain unchanged.")
(HERE/'observation.txt').write_text(observation+'\n')
root_names={r.split('==')[0].lower() for r in source['roots']}
root_artifacts=[a for a in artifacts if a['name'].lower() in root_names]
assert len(root_artifacts)==len(source['roots'])
artifact_table='\n'.join(f"| {a['filename']} | {a['bytes']:,} | `{a['sha256']}` |" for a in root_artifacts)
import_table=[]
for module,r in source['import_roots'].items():
    site=r['first_sites'][0]
    import_table.append(f"| {module} → {r['distribution']} | `test.jsonl:{site['jsonl_line']}`, `code_context:{site['context_line']}` (`{site['import_module']}`) |")
profile_table='\n'.join(f"| {n} / CPython 3.12.4 bootstrap only | {len(r['selected'])} | {r['exit_code']} / {r['install']['exit_code']} / {r['check']['exit_code']} | pluggy==1.6.0; {r['negative']['exit_code']}, ResolutionImpossible |" for n,r in tb.items())
gaps={
 'bfcl_v3':'JSONL route uses stdlib json and local scaffolds; no nonempty third-party wheel graph to count.',
 'bird_minidev':'JSON/CSV/sqlite3 route uses stdlib/local scaffolds. SQLite native custody is separate; no empty solve is counted.',
 'fever':'Inspected JSONL/scaffold reader and local score route use stdlib; no nonempty third-party wheel solve.',
 'musique':'Inspected JSONL/scaffold route uses stdlib json and local helpers; no nonempty wheel solve.',
 'physicsquestions':'Inspected CSV route uses stdlib csv/local scaffolds; no nonempty wheel solve.',
 'sportsunderstanding':'Inspected CSV route uses stdlib csv/local scaffolds; no nonempty wheel solve.',
 'strategyqa':'Inspected CSV route uses stdlib csv/local scaffolds; no nonempty wheel solve.',
 'tau_bench':'Fresh verifier/CLI/vendored-domain import audit is stdlib/local only; Dockerfile declares no pip install. Interpreter/image/data custody is separate; no empty solve is counted.',
 'twowikimultihopqa':'Inspected row/scorer route uses stdlib JSON/local helpers. The Parquet witness is outside this route; no empty solve is counted.',
 'terminal_bench':f"Only {summary['tb_demonstrated_bootstrap_profiles']}/{summary['tb_tasks']} task tooling routes have demonstrations across explicitly stated targets; {summary['tb_undemonstrated_tooling_routes']} other tooling routes and full per-task image/ML/native/application graphs remain undemonstrated. Shared bootstrap pins do not transfer a success to another task. New test import gaps include build-cython-ext numpy/pyknotid, headless-terminal's task-produced headless_terminal, and hf-model-inference transformers/torch/flask image dependencies. These are unattempted scopes, not unobtainable distributions or observed ModuleNotFoundErrors."
}
gap_table='\n'.join(f'| {n} | {gaps[n]} |' for n in sorted(gaps))
report=f'''# DS1000 and bounded Terminal-Bench tooling resolved offline - w-resolver5

**{summary['bounded_profiles_resolved']}/{summary['bounded_profiles']} bounded profiles and {summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']} complete nonempty dataset Python metadata profiles** now have demonstrations, carrying forward merged w-resolver4's {prior['bounded_profiles_resolved']}/{prior['bounded_profiles']} and {prior['complete_nonempty_python_profiles']}/{prior['shared_datasets']}. DS1000 adds the dataset profile; three Terminal-Bench additions are bootstrap-only. No shared or dataset blocker closes and no production execution is authorized.

## Selection and source derivation

Selection rule: work on the two remaining datasets with nonempty external Python graphs, rather than count the nine stdlib-only N/A routes. For DS1000, first derive direct and parseable-literal static import roots from **all {source['rows']} released `code_context` fields**, preserve the declared Python 3.10 target and all environment version pins, and attempt the finite union. For Terminal-Bench, sort task IDs with a finite exact direct `pip install` declaration, skip duplicate root-pin sets, and stop at three distinct bootstrap profiles. The skipped prefix entry is fix-code-vulnerability; only build-cython-ext, headless-terminal and hf-model-inference receive new receipts. This is the executed selection rule, not a claim of external preregistration.

The primary packet is `tests/fixtures/hg_wresolver5/`; Terminal-Bench's compact subpacket is `tests/fixtures/hg_wresolver5_tb/`. `source.py`, `source.json`, `source.stdout.txt`, `context_literals.py` and `context-literals.json` retain the derivation and exact import sites/hashes. DS1000 checker `data/datasets/ds1000/verify/check.py:49` constructs the program from `code_context`; the retained upstream `execution.py` executes it. The source path, release SHA-256, actual declaration/import lines and independent `sha256sum` are in `source.json` and `raw/source-sha256sum.stdout.txt`. The audit parses only context metadata, discards other JSON fields, exports no prompt/gold/reference code or test bodies, and executes no context/candidate. There are no AST syntax failures. Arbitrary generated-candidate imports are outside this finite source-scoped reconstruction, just as arbitrary candidate behavior is outside a default dependency lock.

| Import root → distribution | First freshly derived source site |
| --- | --- |
{chr(10).join(import_table)}

The all-context literal-string audit additionally finds `statsmodels` and `mpl_toolkits` → matplotlib, already covered by the declared union. All original declared version pins remain exact: the full root list is `profile/roots.in`. Pillow and PyYAML were unpinned imports; their candidates are freshly observed host versions, explicitly reconstruction choices rather than upstream/image version claims. `environment.yml` declares `pytorch::pytorch==2.2.0` with `pytorch::cpuonly`. The official CPU `torch==2.2.0+cpu` wheel satisfies original `==2.2.0` under PEP 440; the independent validator checks this. It preserves the CPU selector for this Python metadata mapping, without asserting Conda build/channel/native equivalence. Conda `yaml` denotes native libyaml and is **not** relabeled as a pip distribution: actual `import yaml` supplies the separate PyYAML Python root, while native libyaml custody remains a gap. The explicit pip tooling wheel is separately hash-pinned and locally seeds a fresh no-system-packages Python 3.10 venv; it is not invented as a scorer dependency.

## Exact artifacts outside the repository

DS1000 acquired **{len(artifacts)} wheels / {sum(a['bytes'] for a in artifacts):,} bytes** outside git. `artifacts.json` records exact versioned index URL/status/digest, artifact URL, filename, size, recomputed SHA-256 and only the relevant METADATA/WHEEL graph fields. `raw/wheel-sha256sum.stdout.txt` independently rehashes every actual candidate. Final hashes match the exact offered index entries; real target tags, Requires-Python and active dependency markers are independently validated on the recorded CPython 3.10.12 target. The original complete pip discovery set is used; partial redundant transfers are excluded.

| Root artifact | Bytes | Recomputed SHA-256 |
| --- | ---: | --- |
{artifact_table}

Terminal-Bench independently acquires **{len(tbinputs['artifacts'])} unique wheels / {sum(a['bytes'] for a in tbinputs['artifacts']):,} bytes**, also outside git. Exact pinned declaration lines, task test import-only AST excerpts, plugin import-only audit, wheel digests and process receipts are in its subpacket. Detailed bounded findings: `reports/w-resolver5-tb-notes.md`. Both packets include `refetch.py` scripts which refuse repository destinations and re-fetch only the recorded exact URLs, checking size and digest. DS1000's script receives a successful one-artifact flatbuffers smoke check (`refetch-smoke.json` and raw output); its complete-set default is available but was not executed as that smoke check. Terminal-Bench's script actually re-fetches and verifies its entire captured set. No wheel/package/archive, saved HTTP response body, bulk import dump or multi-MB JSON is committed.

DS1000 bounds: {read(HERE/'artifacts.json')['limits']['max_wheels']} wheels, {read(HERE/'artifacts.json')['limits']['max_profile_bytes']} bytes per candidate set, {read(HERE/'artifacts.json')['limits']['max_file_bytes']} bytes per individual exact fetch, 8 MiB per index response, 45-second socket operation timeouts; pip discovery has a 900-second subprocess bound and **post-download** count/size checks. A socket timeout is not a total wall-clock HTTP deadline and no enforced streaming pip quota is claimed. Final resolve/check/refusal subprocesses have 300-second bounds, install 600 seconds. Temporary offline venv/cache/negative roots are removed with actual cleanup receipts. Acquisition payloads and incomplete transfer evidence remain outside git, separate from runs/ and frozen receipts.

## Network denial, installation and mandatory-wheel refusal

Actual `unshare -Urn` receipts show loopback only, no external route, and external connect errno 101 (`Network is unreachable`). Each probe uses a fresh venv with system packages disabled, cleared proxy/package environment and isolated empty cache. Real pip uses `--ignore-installed --no-index --no-cache-dir --only-binary=:all:`, exact constraints and full dependency processing. No `--no-deps` is used. A dependency-aware dry-run generates the hash lock; a separate `--require-hashes` installation and `pip check` follow. The DS1000 full temporary pip report is deliberately reduced to selected graph fields plus its original digest/size; the report body is removed with the disposable workdir, not represented as a retained full report.

| Profile / target | Selected | Resolve / hash install / pip check | Required transitive wheel removed; refusal |
| --- | ---: | --- | --- |
| ds1000 / CPython 3.10.12 | {len(selected)} | {result['exit_code']} / {result['install']['exit_code']} / {result['check']['exit_code']} | {missing['name']}=={missing['version']}; {result['negative']['exit_code']}, ResolutionImpossible |
{profile_table}

Each negative removes only the named required wheel, retains every other candidate, and runs **after installation** with `--ignore-installed`; installed copies cannot hide absence. DS1000 stdout names `tensorflow-cpu 2.16.1 depends on flatbuffers>=23.5.26` and exact constraint `{missing['name']}=={missing['version']}`. Terminal-Bench stdout names `pytest 8.4.1 depends on pluggy<2 and >=1.5`. Raw stderr preserves `ResolutionImpossible`. These are refusals, not scores. No scorer, benchmark task, image/container, model, GPU, endpoint or server runs.

The Terminal-Bench target distinction is material: these are host CPython 3.12.4 **bootstrap metadata** reconstructions. Build-cython-ext's actual image declares Python 3.13/numpy and its test imports pyknotid; hf-model-inference's image declares transformers/torch/flask and Python 3.13; headless-terminal imports the task-produced headless_terminal. Those application/image/native roots remain outside the finite bootstrap proof. Build-cython shares pytest/plugin root pins with prior OpenSSL, but is a new direct-pip/task/target receipt; it is not claimed a globally new root-pin set or a complete task graph.

## Every failed or incomplete attempt

| Attempt | Exact distribution, exception or disposition | Evidence |
| --- | --- | --- |
| Initial redundant DS1000 refetch | Agent-owned acquisition process deliberately received SIGTERM; shell exit 143, not a resolver or artifact-obtainability failure. A gensim==4.3.2 redundant transfer had stalled; complete discovery wheel already existed. | `acquire.stdout.txt`, `acquire.stderr.txt`, `attempts/acquisition-correction.json`, executed initial script retained. Partial bytes remain outside git and are excluded. |
| Two initial small index digest captures | flatbuffers==25.12.19 and gast==0.7.0 index JSON were hashed before buffer flush, yielding the empty-file digest. These two captured values are invalid and never used as final index identities. | Exact old/new recomputed values in `attempts/acquisition-correction.json`; `finalize.py`, `finalize.stdout.txt` and independent `raw/index-sha256sum.stdout.txt` correct them after close. Active acquisition flushes before hashing. |
| DS1000 missing-wheel control | Required {missing['name']}=={missing['version']}; ResolutionImpossible; exit {result['negative']['exit_code']}. | `raw/negative.*`, omission inventory and post-install command receipts. |
| Three Terminal-Bench missing-wheel controls | Required pluggy==1.6.0; ResolutionImpossible; exit 1 for each. | Subpacket `raw/negative-*` and `results.json`. |

All final selected profiles succeed. No distribution is declared unobtainable. In particular, the CPU PyTorch artifact was checked at the official CPU index and its linked download-r2 host instead of inferring absence from the default PyPI graph. No version pin, dependency edge, admission gate or refusal is weakened. Source/native/image/production gaps below are unattempted scopes, not missing-wheel exceptions. Raw upstream metadata whitespace and pip-output blank lines are preserved; any corresponding full-diff whitespace warnings are evidence formatting, while source/report whitespace receives a separate clean check.

## Updated fraction and every remaining dataset gap

`summary.json` and raw `write-report.stdout.txt` derive arithmetic from actual successful/refusal receipts and merged w-resolver4's inherited summary. This phase adds **{summary['new_bounded_profiles']} successful bounded profiles**, including **one complete finite Python metadata dataset profile**: {summary['bounded_profiles_resolved']}/{summary['bounded_profiles']} bounded, {summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']} complete nonempty dataset Python metadata profiles. Inherited demonstrations are carried from their merged receipts, not falsely presented as freshly rerun after the payload-history repair. Terminal-Bench has {summary['tb_demonstrated_bootstrap_profiles']}/{summary['tb_tasks']} demonstrated task tooling routes across the explicitly different targets; this is not {summary['tb_demonstrated_bootstrap_profiles']} complete task/image closures. N/A datasets stay in the denominator and are never successful empty solves.

`remainder.py`, `remainder.json` and `raw/remainder-sha256sum.stdout.txt` freshly audit all N/A adapter/verifier/vendored routes and hash every Terminal-Bench task manifest, Dockerfile and verifier bootstrap. Each remaining gap is:

| Remaining dataset | Reason outside the complete nonempty numerator |
| --- | --- |
{gap_table}

DS1000 is now inside the numerator **only at the finite declared/static-import Python metadata scope**. Native Conda channel/build equivalence, cpuonly/libyaml providers, interpreter/ABI/image custody, arbitrary candidate imports, external resources, official scorer compatibility/execution, provenance/privacy, quotas, snapshots, cleanup enforcement and valid live controls remain unestablished. This packet does not modify an adapter or adopt these reconstruction locks. All shared/dataset statuses, complete next_actions, dataset/history records and gates remain unchanged.

## Exact registry observation - w-resolver5

{observation}

Validation: `reports/w-resolver5-validation.txt`. Independent validation checks source lines/hashes, every exact external candidate, target markers/tags, every active dependency edge including extras, real process/network/refusal/cleanup receipts, coverage arithmetic, all registry evidence locators, the unchanged protected registry projection and commit file sizes. The Terminal-Bench child diff was reviewed, its validator rerun, size checked, and its safe commit cherry-picked only into this isolated worker branch; no main write occurs.
'''
(ROOT/'reports/w-resolver5-payloads.md').write_text(report)
(HERE/'README.md').write_text('''# w-resolver5 compact evidence packet

Read reports/w-resolver5-payloads.md and reports/w-resolver5-validation.txt.
The primary packet contains DS1000 import/declaration derivation, exact URL/name/size/SHA-256 artifact metadata, original raw command output, real network-denied install/refusal/cleanup receipts, scripts, coverage arithmetic and unchanged registry projection. The sibling hg_wresolver5_tb packet supplies three explicit bootstrap-only reconstructions.

All payloads, saved index bodies, redundant partial downloads and bulk import-site lists stay outside the repository. artifacts.json identifies the actual candidate directory and every digest. refetch.py re-fetches exact URLs into a new external directory, checking sizes/hashes; --filename selects an explicit bounded subset. Its successful smoke check covers flatbuffers only, while the Terminal-Bench refetch script verified its entire set.

acquire.stdout.txt and attempts/acquire-executed-initial.py preserve an incomplete redundant refetch, terminated with SIGTERM/exit143. attempts/acquisition-correction.json discloses two invalid unflushed-index digest captures. finalize.py independently audits the complete initial discovery artifacts and corrects closed-file index hashes with raw sha256sum. Partial redundant transfers never enter the resolved candidate set. The active acquire.py flushes before hashing. No unobtainability conclusion is made.

source.py reads only code_context import metadata from all released DS1000 rows; context_literals.py audits parseable import-containing strings. No prompts, gold/reference code, test bodies, task execution or scores are exported. The original complete temporary pip report is reduced to graph fields and a digest/size receipt, then removed with the disposable workdir; no full-report retention is claimed.

Read-only verification: python3 tests/fixtures/hg_wresolver5/validate.py and python3 tests/fixtures/hg_wresolver5_tb/validate.py. Acquisition/probe generators refuse existing captures; never rerun in place. SHA256SUMS seals this primary packet. No shared/dataset blocker or production gate closes.
''')
heading='## 2026-10-15 — DS1000 and bounded Terminal-Bench tooling resolved offline - w-resolver5'
journal=ROOT/'docs/adapter-integration-journal.md'
assert heading not in journal.read_text()
with journal.open('a') as stream:
    stream.write(f'\n{heading}\n\n- Added DS1000 finite declared/static-import Python metadata reconstruction on CPython 3.10.12, preserving original pins and explicitly mapping Conda CPU PyTorch to official torch==2.2.0+cpu only for Python metadata. All {source["rows"]} code_context fields receive metadata-only AST auditing, including parseable import-bearing literal strings, without exporting task/gold/prompt bodies or executing them. {len(selected)} distributions pass kernel-network-denied resolve, require-hashes install and pip check; removing {missing["name"]}=={missing["version"]} after installation refuses. Conda/native/image/ABI/runtime equivalence remains open.\n- Reviewed independent child commit c6c6bcdfe55648468febe048c4bc7a7c0de8303f, reran its validator, checked its largest blob (128491 bytes), and cherry-picked its safe text-only diff into this isolated branch. It adds exactly {len(tb)} host CPython 3.12.4 Terminal-Bench bootstrap-only profiles: '+', '.join(f'{n} ({len(r["selected"])} distributions)' for n,r in tb.items())+f'. Missing pluggy==1.6.0 refuses each; no task/image/native closure or duplicate-task success is inferred.\n- Updated arithmetic from actual receipts: {summary["bounded_profiles_resolved"]}/{summary["bounded_profiles"]} bounded profiles, {summary["complete_nonempty_python_profiles"]}/{summary["shared_datasets"]} complete nonempty dataset Python metadata profiles; Terminal-Bench {summary["tb_demonstrated_bootstrap_profiles"]}/{summary["tb_tasks"]} tooling routes only. Remaining {len(summary["remaining_datasets"])} dataset gaps are individually sourced: nine stdlib-only N/A routes and incomplete Terminal-Bench task/image/native graphs. No artifact is declared unobtainable.\n- All downloaded payloads, index bodies, partial transfers and bulk import lists remain outside git. Initial redundant DS1000 acquisition was deliberately SIGTERMed (exit143); two unflushed-small-index digest capture errors are retained and independently corrected with closed-file hashes and raw sha256sum. Final candidates all match their exact index entries. No stale/partial transfer or invalid digest enters final evidence.\n- Registry changes are additive observed/evidence only under scorer-offline-closure; all statuses, complete next_actions, dataset/history records, gates and production_authorized=false remain unchanged. No shared/dataset blocker closes. No runs/, frozen receipt, existing run ID, benchmark task, official scorer, model/endpoint, server or GPU operation is touched.\n- Deliverables: reports/w-resolver5-payloads.md, tests/fixtures/hg_wresolver5/, tests/fixtures/hg_wresolver5_tb/ and reports/w-resolver5-validation.txt. Validation covers both independent packet validators, python3 tools/check_dataset_blockers.py, focused blocker/journal tests and a precommit largest-added-file check below 1 MB. Work is committed only in registered /tmp/hg-resolver5 (wg-resolver5) for parent review/merge; main is untouched by this worker.\n')
registry_path=ROOT/'docs/dataset-blockers.json'
registry=read(registry_path)
for blocker in registry['shared_blockers']:
    if blocker['id']=='scorer-offline-closure':
        blocker['observed']+=' '+observation
        blocker['evidence'] += [dict(kind='repository',path='reports/w-resolver5-payloads.md',locator='## Exact registry observation - w-resolver5'),
                                dict(kind='repository',path='tests/fixtures/hg_wresolver5/README.md',locator='# w-resolver5 compact evidence packet'),
                                dict(kind='repository',path='docs/adapter-integration-journal.md',locator=heading)]
        break
else:
    raise AssertionError('Missing shared blocker')
registry_path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
