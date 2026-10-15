"""Fresh source-only audit of stdlib routes and remaining image/bootstrap scope."""
import ast
import json
from pathlib import Path
import re
import sys
from common import HERE, ROOT, digest, run, save

sources = []
def inspect(path):
    path = Path(path)
    text = path.read_text()
    imports = []
    if path.suffix=='.py':
        for node in ast.walk(ast.parse(text)):
            if isinstance(node,ast.Import):
                modules = [a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom) and not node.level:
                modules = [node.module] if node.module else []
            else:
                continue
            imports += [dict(module=m,line=node.lineno,text=text.splitlines()[node.lineno-1]) for m in modules]
    record = dict(path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                  sha256=digest(path),bytes=path.stat().st_size,imports=imports)
    sources.append(record)
    return record

names = ['bfcl_v3','bird_minidev','fever','musique','physicsquestions','sportsunderstanding','strategyqa','twowikimultihopqa']
facts = {}
for name in names:
    paths = [ROOT/f'data/datasets/{name}.py']
    if name=='bird_minidev':
        paths += [ROOT/'data/datasets/bird_minidev/verify/check.py']
    records = [inspect(p) for p in paths]
    external = [i for r in records for i in r['imports'] if i['module'].split('.')[0] not in sys.stdlib_module_names|{'data'}]
    assert not external,(name,external)
    facts[name] = dict(status='N/A; no nonempty external-wheel graph on inspected row/scorer route',
                       reason='JSON/JSONL/CSV and local scaffolds use stdlib. Conditional parquet_rows pyarrow branch is not on these adapter routes; BIRD sqlite3/native custody remains separate.',sources=[r['path'] for r in records],external_imports=external)
taupaths = [ROOT/'data/datasets/tau_bench.py', ROOT/'data/datasets/tau_bench/verify/check.py',ROOT/'data/datasets/tau_bench/image/tau_cli.py']
taupaths += sorted((ROOT/'data/datasets/tau_bench/lib').rglob('*.py'))
tau = [inspect(p) for p in taupaths]
external = [i for r in tau for i in r['imports'] if i['module'].split('.')[0] not in sys.stdlib_module_names|{'data','tau_bench'}]
assert not external,external
tau_docker = inspect(ROOT/'data/datasets/tau_bench/Dockerfile')
assert 'pip install' not in (ROOT/tau_docker['path']).read_text()
facts['tau_bench'] = dict(status='N/A; no nonempty external-wheel graph on inspected vendored route',
                          reason='Verifier/CLI/vendored domain tools use stdlib or local imports; Dockerfile declares no pip installer. Interpreter/image/data custody remains separate.',
                          python_files=len(tau),external_imports=external)
scaffolds = [inspect(ROOT/'data/scaffolds/qa'/p) for p in ['base.py','read.py','verify/check.py','evidence_scorers.py','prediction.py']]
for record in scaffolds:
    external = [i for i in record['imports'] if i['module'].split('.')[0] not in sys.stdlib_module_names|{'data'}]
    assert all(record['path'].endswith('/read.py') and i['module'].startswith('pyarrow') for i in external),external
tbroot = Path('/mnt/20t/xubuqiang/datasets/terminal-bench')
tasks = sorted(p for p in tbroot.iterdir() if (p/'task.toml').is_file())
tb = []
for task in tasks:
    tb.append(dict(task=task.name,sources=[dict(path=str(task/p),sha256=digest(task/p),bytes=(task/p).stat().st_size)
                                        for p in ['task.toml','environment/Dockerfile','tests/test.sh']]))
record = dict(datasets=facts,na_count=len(facts),sources=sources,terminal_tasks=tb,
              terminal_task_count=len(tasks),terminal_gap='Fresh bounded bootstrap-only metadata profiles are distinct from complete task/image/native graphs. Remaining per-task image/ML/native/service imports are not reconstructed, including tasks sharing a bootstrap. Do not extrapolate one source graph to other task receipts.',
              ds1000_native_gap='Python metadata reconstruction does not reproduce Conda cpuonly/libyaml/build/channel selectors, native providers or target image. Arbitrary candidate-generated imports and dynamically downloaded resources are outside finite static-root scope.')
save(HERE/'remainder.json',record)
run('remainder-sha256sum',['sha256sum',*[ROOT/r['path'] if not Path(r['path']).is_absolute() else r['path'] for r in sources],
                         *[r['path'] for t in tb for r in t['sources']]])
print(json.dumps(dict(na_count=len(facts),na_datasets=sorted(facts),terminal_task_count=len(tasks),tau_python_files=len(tau),
                     terminal_tasks=[t['task'] for t in tb]),indent=2,sort_keys=True))
