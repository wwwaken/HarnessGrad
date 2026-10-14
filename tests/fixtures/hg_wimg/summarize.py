"""Derive the review table only from fresh inspection bytes and current source."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CAP=HERE/'capture'
images=json.loads((CAP/'image-inventory.json').read_text())
manifests=json.loads((CAP/'manifest-read/start.stdout.txt').read_text())
surfaces=json.loads((HERE/'supplement/verifier-surfaces.json').read_text())
bytask={s['task']:s for s in surfaces}
host=json.loads((CAP/'native/host-probe.stdout.txt').read_text())


def write(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def sources():
    files=[ROOT/'harnessgrad/environments.py', ROOT/'data/scaffolds/qa/base.py',
           ROOT/'data/scaffolds/qa/verify/check.py']
    for name in ('gaia','tau_bench','appworld','terminal_bench','chessbench_puzzles','alfworld',
                 'scienceworld','bird_minidev','ds1000','spreadsheetbench'):
        files.append(ROOT/'data/datasets'/f'{name}.py')
        files+=sorted((ROOT/'data/datasets'/name).rglob('*.py'))
    files.append(Path('/mnt/20t/xubuqiang/datasets/gaia/_src/scorer.py'))
    out=[]
    for p in sorted(set(files)):
        label=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
        if not p.is_file():out.append({'path':label,'missing':True});continue
        data=p.read_bytes();text=data.decode(errors='replace')
        rec={'path':label,'sha256':hashlib.sha256(data).hexdigest(),'imports':[],
             'dependency_lines':[{'line':i,'text':s} for i,s in enumerate(text.splitlines(),1)
                                 if re.search(r'import |from |resolve_digest|image_digest|IMAGE|image|argv|kind.*files|subprocess|LoadLibrary|load_lib|java|soffice|evaluate\(',s)]}
        try:
            tree=ast.parse(text)
            rec['imports']=[{'line':n.lineno,'text':ast.get_source_segment(text,n)} for n in ast.walk(tree)
                            if isinstance(n,(ast.Import,ast.ImportFrom))]
        except SyntaxError as e:rec['ast_error']=str(e)
        out.append(rec)
    return out


write(HERE/'source-dependencies.json',sources())
rows=[]
for x in images:
    row=dict(x)
    row['computed_repo_digests']=[]
    for ref in x.get('repo_digests',[]):
        digest=ref.split('@',1)[1]
        record=manifests.get(digest,{})
        raw=record.get('raw_utf8')
        computed='sha256:'+hashlib.sha256(raw.encode()).hexdigest() if raw else None
        assert computed==digest,(x['key'],ref)
        row['computed_repo_digests'].append(ref.split('@')[0]+'@'+computed)
    p=CAP/'images'/x['key']/'abi.json'
    if p.exists():
        abi=json.loads(p.read_text())
        exe=next(e for e in abi['elf'] if e['resolved']==abi['executable']['resolved'])
        row['abi']={'python':abi['python'].split()[0],'glibc':abi.get('glibc_runtime'),
                    'loader':exe['pt_interp'],'resolved_loader':exe['loader']['resolved'],
                    'executable':abi['executable'],'elf_files':len(abi['elf']),
                    'distributions':{d['name']:d['version'] for d in abi['distributions'] if d['name']}}
    elif x['present']:
        text=(CAP/'images'/x['key']/'start.stdout.txt').read_text()
        libc=re.search(r'^glibc ([0-9.]+)$',text,re.M)
        shell=text.split('=== shell ABI ===\n',1)[1].split('=== interpreter ===',1)[0]
        loader=re.search(r'^\s*(/\S*ld-(?:linux|musl)\S*)\s+\(',shell,re.M)
        bash=re.search(r'GNU bash, version ([^\n]+)',text)
        row['abi']={'python':None,'python_absence':'python3 absent on PATH (probe exit 127)',
                    'glibc':libc.group(1) if libc else None,'loader':loader.group(1) if loader else None,
                    'bash':bash.group(1) if bash else None,'shell_only':True}
    else:row['abi']=None
    rows.append(row)
write(HERE/'summary.json',rows)
bykey={x['key']:x for x in rows}
tb=[x for x in rows if x['dataset']=='terminal_bench']
py=Counter((x['abi']['python'],x['abi']['glibc']) for x in tb if x['abi'] and x['abi']['python'])
native_names=['chessbench_puzzles','alfworld','scienceworld','bird_minidev','ds1000','spreadsheetbench']
native_lines=[385,532,452,308,168,357]
loader='/lib64/ld-linux-x86-64.so.2'
report=[]


def add(s=''):report.append(s)


def ref(x):return '<br>'.join('`'+s+'`' for s in x['computed_repo_digests']) or '**Absent locally; no repo digest obtainable**'


add('# Image and ABI custody — w-img')
add()
add('**`scorer-offline-closure` remains open.** This is a fresh local image/ABI custody inventory, not an offline scorer installation or a live scoring control. Source baseline: `'+(CAP/'baseline/git-head.stdout.txt').read_text().strip()+'`. Capture timestamps are UTC in each command receipt (the session began '+json.loads((CAP/'session.json').read_text())['session'].split('hg-wimg-')[1].rsplit('-',1)[0]+'); dates are not inferred from the older reports.')
add()
add('## Image custody coverage — w-img')
add()
add('The topology survey places exactly **four** standard routes in `snapshot-service`: **gaia, tau_bench, terminal_bench, appworld**; the other 19 are `actor-workdir`. Its container snapshot and mounted-service distinction is retained. The six other datasets in the requested minimum list are native `files` routes and have no adapter image. Chess also has its separate trusted `in-process` controller. No image was invented for a native route.')
add()
add('Fresh `docker image inspect` covers **94 configured references**: GAIA, Tau-bench, three AppWorld roles and all **89** Terminal-Bench task manifests. **91 are locally present, all 91 have RepoDigests**. No present configured image lacks a repo digest. Three Terminal-Bench refs are missing. Every reported repo digest is both read from that fresh inspect and independently recomputed from its actual local OCI manifest bytes; none is transcribed from earlier reports. **101 index/child/attestation manifest blobs** were read and hashed. This is not a rehash of every compressed layer or authenticated publisher provenance.')
add()
add('All relevant `HG_*` image/task-selection overrides were unset in this inspection (`capture/environment.json`). The table describes current defaults and the checked local task checkout, not every possible environment override or historical run. Tags visible in `docker images`, including `jevloop-tb:*` and AppWorld `:20261009-clean2`, are not automatically the adapter reference. The actual Terminal-Bench checkout names `alexgshaw/*:20251031`; no `jevloop-tb` substitute was used. AppWorld already defaults to digest references for all three roles.')
add()
add('| Dataset / route | Adapter reference and file:line | Fresh repo digest | Configured pin | Image-local ABI now recorded / verifier surface |')
add('| --- | --- | --- | --- | --- |')
for key,title,dep in [
 ('gaia','gaia / snapshot','`question_scorer` imports NumPy; CPython + NumPy/OpenBLAS native ABI'),
 ('tau_bench','tau_bench / snapshot','Vendored replay/hash/domain tools + stdlib/hashlib/OpenSSL; no third-party replay package'),
 ('appworld-verifier','appworld / mounted service','AppWorld evaluator/replay + SQLite, Pydantic, orjson, xxhash, SQLAlchemy and imported dependencies')]:
    x=bykey[key];a=x['abi']
    add(f'| `{title}` | `{x["reference"]}`<br>`{x["adapter"]}:{x["literal_line"]}`'+ ('; consumed at `data/datasets/appworld.py:288`' if key=='appworld-verifier' else '')+f' | {ref(x)} | **{x["configured_pin"]}** | CPython {a["python"]}; glibc {a["glibc"]}; loader `{a["loader"]}`. {dep}. |')
add('| `terminal_bench` / snapshot | Per-task `environment.docker_image`, consumed at `data/datasets/terminal_bench.py:198`; `state=container` at line 202. All 89 exact refs and manifest file:line appear below. | 86 present repo digests below; **3 absent** | **89 movable tags** | 60 CPython records; 26 shell-only records (`python3` absent on PATH); 3 images unavailable. Per-task test bootstrap/import/process/tool surface below and in the JSON appendix; later `uvx` ABI is unestablished. |')
native_deps={
 'chessbench_puzzles':'`chess==1.11.2` declaration; pure-Python board replay, no Stockfish requirement',
 'alfworld':'ALFWorld/TextWorld, NumPy and `libdownward.so`/C++ runtime; direct package versions are declared, complete host closure unpinned',
 'scienceworld':'ScienceWorld + Py4J + prepared JRE/JAR; package/JRE declarations exist, selected JVM/Py4J/host ABI and IPC still need runtime binding',
 'bird_minidev':'stdlib `sqlite3` → native SQLite/zlib/libc; no sqlite CLI requirement or configured SQLite ABI pin',
 'ds1000':'scientific test-context imports: NumPy/pandas/SciPy/sklearn/Matplotlib/seaborn/Torch/PIL/YAML and native math/plotting libraries; candidate imports can expand this',
 'spreadsheetbench':'openpyxl/et-xmlfile and optional lxml/NumPy/Pillow; formula branch LibreOffice/UNO/Calc/fonts/native libraries; LibreOffice version unpinned'}
for name,line in zip(native_names,native_lines):
    add(f'| `{name}` / native | **No image**, `data/datasets/{name}.py:{line}` (`files`) | Not applicable | **No image pin; native interpreter unpinned** | Host base only, freshly observed: CPython {host["python"].split()[0]}, glibc {host["glibc_runtime"]}, `{loader}`. {native_deps[name]}. These are not image ABI measurements. |')
add()
add('Native host probe: `capture/native/host-probe.stdout.txt` records executable/loader/library hashes, SOABI, stdlib import resolution and distribution metadata. It does **not** import the six native datasets, construct worlds, run Java/LibreOffice/scientific tests or establish their complete native dependency closure. Their dataset-specific surface/pin gaps build on `reports/w-tbdep-transitive-inventory.md`; current source hashes/import lines are in `source-dependencies.json`. Native host facts must not be substituted for an image or snapshot fact.')
add()
add('### AppWorld roles checked separately')
add()
add('| Role / adapter source | Configured reference / independently checked repo digest | ABI |')
add('| --- | --- | --- |')
for key,use in [('appworld-actor',296),('appworld-service',304),('appworld-verifier',288)]:
    x=bykey[key];a=x['abi']
    add(f'| `{key}` — `data/datasets/appworld.py:{x["literal_line"]}`, used at line {use} | `{x["reference"]}`<br>RepoDigest: {ref(x)}<br>**digest-pinned** | CPython {a["python"]}; glibc {a["glibc"]}; `{a["loader"]}` |')
add()
add('Actor, service and verifier digests are different. Only the **verifier** import/ELF probe is used to describe the evaluator surface. The service-recording trust contract remains separate. The tag `harnessgrad/appworld-service:20261009-clean2` is an alias for the default service image, not the evaluator image.')
add()
add('## Verifier transitive surface and pin gaps')
add()
add('- **GAIA:** `data/datasets/gaia.py:202` selects `python3`; `data/datasets/gaia/verify/check.py:72` imports the upstream scorer, then line 99 calls it. The scorer file was read/hash-inventoried without import (`source-dependencies.json`); NumPy is an import-time dependency even for Python normalization. The image import probe observes NumPy **'+bykey['gaia']['abi']['distributions']['numpy']+'**, `_multiarray_umath`/`_umath_linalg`, bundled `libscipy_openblas64_`, libgfortran/libquadmath, libstdc++/libgcc, libm/libpthread/libc, libpython and the loader. Exact provider paths and SHA-256 values are in `capture/images/gaia/abi.json`. Common stdlib probes also load SSL/SQLite/compression/ctypes; those are labelled inspection coverage, not additional metric requirements. The scorer source SHA declaration is distinct from the movable image/base and unversioned pip/apt build recipe. GAIA benchmark refusal remains in force; no preparation, task or scorer execution occurred.')
add('- **Tau-bench:** `data/datasets/tau_bench.py:341` selects `python3`; check lines 116 and 138 reach vendored hash and domain tools. Current AST/import inventory includes the vendored library in `source-dependencies.json`. The scoring library uses local modules/stdlib, not a model SDK. Observed `_hashlib`/OpenSSL **'+json.loads((CAP/'images/tau_bench/abi.json').read_text())['openssl']+'**, `libcrypto.so.3`, libpython/libm/libc/loader are on record. The larger stdlib probe superset is not a claim that replay requires SQLite/SSL sockets. The image/base remain movable; vendored source does not pin the snapshot interpreter. The previously reported absent clean DB files remain a separate input-custody gap.')
appdist=bykey['appworld-verifier']['abi']['distributions']
add('- **AppWorld:** `data/datasets/appworld/verify/check.py:44`, `:52`, `:56` import `AppWorld`, replay calls and evaluate. Importing the package only (no constructor/evaluate) loads its eager Python/native dependencies. Observed versions include '+', '.join(f'`{n} {appdist[n]}`' for n in ['appworld','pydantic','orjson','xxhash','SQLAlchemy','greenlet'])+'. Raw distribution `Requires-Dist` metadata and metadata/RECORD hashes are in `capture/images/appworld-verifier/abi.json`, along with 103 ELF/provider identities, including SQLite, OpenSSL, libffi, libstdc++/libgcc, compression, CFFI/cryptography, Pydantic, orjson/xxhash, greenlet and SQLAlchemy extensions. Metadata is a conservative declared surface, not proof every listed distribution runs during each evaluator. Default image digests fix these base bytes; the rebuild recipe still uses a floating Python base and ranged `uvicorn<1`/transitive requirements. Per-task dynamic evaluator/data use, official provenance/execution, and service lifecycle remain unestablished.')
add('- **Terminal-Bench:** `data/datasets/terminal_bench.py:234` executes `bash /tests/test.sh`, with trusted tests staged at line 238. All 89 task Dockerfiles/manifests, test imports, process calls and bootstrap lines are inventoried from the actual external checkout; no tests ran. `capture/terminal-bench-source-surface.json` records exact file/line/text and recomputed source hashes. `supplement/verifier-surfaces.json` adds AST imports/process calls, explicitly marking dynamic arguments; each available task’s supplement records `command -v`, file hashes, optional readelf, resolved ldd providers/hashes and package inventory. Common tool lookups are a conservative inspection superset, not asserted per-task prerequisites. Bash/libtinfo/libc/loader are recorded even when Python is missing. Task-specific compilers, runtimes, service clients, ML/data artifacts and dynamically selected subprocesses remain additional surfaces. Source pins such as uv/pytest versions do not supply wheel hashes, apt/build pins or the Python patch/ABI subsequently selected by `uvx`; package availability in the base is not offline bootstrap closure. No Torch/model import, download, package install, service request or task invocation was used.')
add()
add('**Configured tags remain findings even though the driver resolves them.** `harnessgrad/environments.py:76` resolves actor refs and line 87 resolves service refs through `eval/containers/container.py:306` / `:324`; driver consumption is at `driver.py:812`. That records a local immutable identity for an individual run; it does not make the adapter’s movable tag an immutable declaration. Snapshot verification creates from the actor filesystem snapshot (`eval/verification/verifier.py:286`), so none of these base-image probes attests an actor-modified snapshot. AppWorld uses its separate pinned verifier image. No production code or image reference was changed.')
add()
add('### Terminal-Bench installed scientific/native supplement')
add()
add('Sixteen present bases declare installed scientific/plotting distributions. A separate fresh, network-disabled **static ELF** probe inventories their native files and hashes key objects/providers: NumPy/OpenBLAS/Fortran, SciPy BLAS/LAPACK, pandas, sklearn/OpenMP, Pillow image/font/compression libraries, Matplotlib/FreeType, Torch CPU/Python/C10, torchvision and MuJoCo where available. No scientific/ML package is imported by this supplement, and no model/GPU code runs. This installed-package superset may include actor capabilities; only the per-task test import/process inventory establishes verifier relevance. Native file inventory does not mean every file was ldd-probed; key selected objects and recursive resolved providers are identified separately.')
add()
add('**Standalone ldd unresolved names are retained below.** They do not prove a library is absent from the image or an import fails: package import can preload bundled providers or alter search paths. This inspection does not perform that ML import or substitute guessed resolutions. `install-windows-3.11` metadata exposes no RECORD-listed native members to this selector (zero supplemental ELF objects); its earlier interpreter/stdlib/tool ABI record is unaffected.')
add()
add('| Task / raw static-native record | Selected/resolved ELF objects hashed | Standalone ldd unresolved SONAMEs |')
add('| --- | --- | --- |')
for task in json.loads((HERE/'native-supplement/selected.json').read_text()):
    value=json.loads((HERE/'native-supplement'/task/'start.stdout.txt').read_text())
    unresolved=sorted({n for o in value['objects'] for n in o.get('unresolved_sonames',[])})
    add('| [`'+task+'`](../tests/fixtures/hg_wimg/native-supplement/'+task+'/start.stdout.txt) | '+str(sum('sha256' in o for o in value['objects']))+' | '+(', '.join('`'+n+'`' for n in unresolved) if unresolved else 'None reported for selected objects')+' |')
add()
add('## Explicit unpinned / missing list')
add()
add('- **Movable adapter image refs:** GAIA, Tau-bench, **all 89 Terminal-Bench tasks**. Digest-pinned default AppWorld actor/service/verifier are excluded from this list; their environment overrides can still select other refs.')
add('- **Unavailable configured image/digest/ABI:** '+', '.join('`'+x['task']+'` (`'+x['reference']+'`)' for x in tb if not x['present'])+'. Missing means unknown, not a fabricated digest or a zero score.')
add('- **Present TB bases without `python3` on PATH:** '+', '.join('`'+x['task']+'`' for x in tb if x['abi'] and not x['abi']['python'])+'. Their shell/libc/loader identities exist, while their future bootstrap interpreter/package ABI does not.')
add('- **Remaining transitive pin gaps:** image rebuild bases/package resolver inputs and wheels; task-specific dynamic imports/programs/data and post-bootstrap interpreter/native libraries; actor-snapshot executable/library integrity; native six datasets’ execution-selected dependency trees; host kernel/CPU ABI. Fresh ldd closures cover only the identified imported/selected installed objects, not all possible task branches or symbol-provider proofs.')
add('- **Shared action still unmet:** official provenance/execution, selected-input binding, trusted class-specific lifecycle/resource/cleanup observations and valid live controls. These disposable inspection containers provide no production lifecycle or scoring authorization. Service connectivity and comparisons between matching known classes remain required. **Zero complete offline scorer closures are certified by this work.**')
add()
add('## Acquisition, preservation and review')
add()
add('The w-ujson method is reused: fresh digest resolution, image-local interpreter/libc/loader reads, recursive ldd/provider hashes, import-only probes, explicit `--pull=never --network=none --read-only`, dropped capabilities, no GPU devices, fixed CPU/memory/PID settings, before/after inspect and removal receipts. Only the fixture scripts are mounted for ABI inspection; no benchmark payload is mounted. Network namespace output shows only loopback and no IPv4 route. No network connectivity call was made. Limits are requested Docker settings, not trusted production resource observations. All available ABI probes were launched by the freshly inspected immutable image ID, never by a tag.')
add()
add('The root-owned local containerd socket refused direct access; that raw refusal is preserved. A disposable network-disabled metadata reader instead mounted the daemon’s local **content-blob directory read-only**, read only the selected image descriptors and their manifests, and hashed their exact bytes. `capture/manifest-read/start.stdout.txt` contains original UTF-8 manifest bytes and computed digests, bound to the fresh Docker inspect descriptors. No registry connection, image pull/build, content write, tag update, snapshot creation from an actor, benchmark, model, GPU or endpoint call occurred.')
add()
add('Historical fixtures were audited, not repaired: this checkout has only three files under `hg_wclo_runtime` and **no SHA256SUMS or per-dataset record preimages**; `hg_wtbdep` has **125/810** matching manifest preimages and **685 absent**; `hg_wujson` has **996/996** matching listed preimages. Counts and recomputed hashes are in `capture/prior-fixture-audit.json`. Prior reports remain context, not a substitute for missing bytes. Historical runs/receipts/archives were untouched; no `runs/` path was accessed. Initial missing-Python probe failures are retained; the independent tool-inspection supplement uses fresh names/receipts and never edits or reruns an old receipt.')
add()
add('Exact commands/status/stdout/stderr live beside every receipt (`*.command.json`, `*.stdout.txt`, `*.stderr.txt`). All three owned-container absence checks are empty; all 194 inspection containers (91 import/shell + 86 tool + 16 static-native + one metadata reader) have removal receipts. Collection programs and probe sources are included. `SHA256SUMS` binds every fixture file except itself; `reports/w-img-validation.txt` records capture/derivation/verification commands and blocker checker output. Shared blocker status and next_action remain unchanged.')
add()
add('## Terminal-Bench per-task custody appendix')
add()
add('All rows use adapter `data/datasets/terminal_bench.py:198`; each manifest locator below is the actual external input file. Task checkout commit: `'+(CAP/'baseline/terminal-bench-head.stdout.txt').read_text().strip()+'`. Every ref is a **movable tag**, including unavailable ones. Loader is the PT_INTERP read from the Python ELF where available; otherwise it is the shell ldd loader. SHA-256s and resolved loader/provider paths are in the linked raw receipts, not inferred from the distro name. No executed task result is asserted.')
add()
add('Observed CPython/glibc groups: '+ '; '.join(f'**{n}** × Python {p}/glibc {g}' for (p,g),n in sorted(py.items()))+'; plus **26** shell-only bases (glibc 2.39).')
add()
add('| Task / exact adapter input file:line | Configured movable image tag | Fresh repo digest | Image-local interpreter / glibc / loader | Verifier import surface (static; dynamic calls remain in JSON) |')
add('| --- | --- | --- | --- | --- |')
for x in tb:
    a=x['abi']
    abi='**Image absent; all ABI values unknown**' if not a else ('CPython '+a['python'] if a['python'] else '**python3 absent on PATH**; Bash '+a['bash'])+'; glibc '+str(a['glibc'])+'; `'+str(a['loader'])+'`'
    modules=sorted({m.split('.')[0] for i in bytask[x['task']]['imports'] for m in i['modules'] if m})
    mods=', '.join('`'+m+'`' for m in modules) or 'No Python import found by AST; shell/bootstrap surface in raw inventory'
    raw='../tests/fixtures/hg_wimg/capture/images/'+x['key']+'/start.stdout.txt' if x['present'] else '../tests/fixtures/hg_wimg/capture/images/'+x['key']+'/inspect.stderr.txt'
    add(f'| [`{x["task"]}`]({raw})<br>`{x["manifest"]}:{x["manifest_line"]}` | `{x["reference"]}` | {ref(x)} | {abi} | {mods} |')
(ROOT/'reports/w-img-abi-custody.md').write_text('\n'.join(report)+'\n')
print(json.dumps({'report_rows':len(rows),'present_images':sum(x['present'] for x in rows),
                  'verified_manifest_blobs':len(manifests),'tb_python':sum(py.values()),
                  'tb_shell_only':sum(bool(x['abi']) and not x['abi']['python'] for x in tb),
                  'tb_missing':[x['task'] for x in tb if not x['present']]}))
