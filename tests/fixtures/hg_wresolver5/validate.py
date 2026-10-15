"""Independent graph, raw-receipt, source, registry-boundary and size checks."""
import argparse
import ast
from collections import Counter
import email
import json
from pathlib import Path
import re
import zipfile
import warnings
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.tags import parse_tag
from packaging.utils import canonicalize_name, parse_wheel_filename
from common import HERE, ROOT, digest

parser = argparse.ArgumentParser()
parser.add_argument('--seal',action='store_true')
args = parser.parse_args()
read = lambda path: json.loads(Path(path).read_text())
inputs = read(HERE/'artifacts.json')
target = read(HERE/'target.json')
assert target['marker_environment']['python_full_version'].startswith('3.10.')
assert digest(target['executable'])==target['executable_sha256']
tags = {t for text in target['tags'] for t in parse_tag(text)}
records = {canonicalize_name(r['name']):r for r in inputs['artifacts']}
assert len(records)==len(inputs['artifacts'])
independent = dict(line.split(maxsplit=1)[::-1] for line in (HERE/'raw/wheel-sha256sum.stdout.txt').read_text().splitlines())
index_hashes = dict(line.split(maxsplit=1)[::-1] for line in (HERE/'raw/index-sha256sum.stdout.txt').read_text().splitlines())
for name,r in records.items():
    path = Path(inputs['directory'])/r['filename']
    assert path.stat().st_size==r['bytes'] and digest(path)==r['sha256']==independent[str(path)]
    assert not path.is_relative_to(ROOT)
    assert r['status']==200 and r['url'].startswith('https://')
    index_path=Path(inputs['directory']).parent/('torch-cpu-index.html' if name=='torch' else r['name']+'-'+r['version']+'.json')
    assert digest(index_path)==r['index']['sha256']==index_hashes[str(index_path)]
    if name!='torch':
        offered=next(e for e in read(index_path)['urls'] if e['filename']==r['filename'])
        assert offered['url']==r['url'] and offered['size']==r['bytes'] and offered['digests']['sha256']==r['sha256']
    assert parse_wheel_filename(path.name)[3]&tags
    if r['requires_python']:
        assert SpecifierSet(r['requires_python']).contains(target['marker_environment']['python_full_version'])
    with zipfile.ZipFile(path) as wheel:
        metadata = email.message_from_bytes(wheel.read(next(n for n in wheel.namelist() if n.endswith('.dist-info/METADATA'))))
    assert canonicalize_name(metadata['Name'])==name and metadata['Version']==r['version']
    assert metadata.get_all('Requires-Dist',[])==r['requires_dist']
    assert metadata.get('Requires-Python')==r['requires_python']
selection = read(HERE/'selection.json')
selected = {canonicalize_name(e['name']):e for e in selection['selected']}
assert set(selected)==set(records)
assert selection['environment']['python_full_version']==target['marker_environment']['python_full_version']
roots = (HERE/'profile/roots.in').read_text().splitlines()
assert roots==read(HERE/'source.json')['roots']
assert set((HERE/'profile/constraints.txt').read_text().splitlines())=={f"{r['name']}=={r['version']}" for r in records.values()}
assert set((HERE/'profile/resolved.lock').read_text().splitlines())=={f"{r['name']}=={r['version']} --hash=sha256:{r['sha256']}" for r in records.values()}
for name,e in selected.items():
    r=records[name]
    assert e['version']==r['version'] and e['sha256']==r['sha256']
    assert e['requires_dist']==r['requires_dist']
# Independent extras-aware traversal of actual selected METADATA, using target
# markers and original root pins. No dependency is dropped to obtain a solution.
pending=[Requirement(r) for r in roots]
extras={}
visited=set()
while pending:
    requirement=pending.pop()
    name=canonicalize_name(requirement.name)
    extras.setdefault(name,set()).update(requirement.extras)
    record=records[name]
    assert requirement.specifier.contains(record['version']),(requirement,record['version'])
    key=(name,tuple(sorted(extras[name])))
    if key in visited:
        continue
    visited.add(key)
    for literal in record['requires_dist']:
        edge=Requirement(literal)
        contexts=extras[name]|{''}
        if edge.marker is None or any(edge.marker.evaluate(target['marker_environment']|{'extra':extra}) for extra in contexts):
            assert canonicalize_name(edge.name) in records,str(edge)
            pending.append(edge)
assert {name for name,_ in visited}==set(records)
assert Requirement('torch==2.2.0').specifier.contains(records['torch']['version'])
assert records['torch']['version']=='2.2.0+cpu'
for r in read(HERE/'source.json')['sources']:
    path=Path(r['path'])
    if not path.is_absolute():path=ROOT/path
    assert digest(path)==r['sha256'] and path.stat().st_size==r['bytes']
    lines=path.read_text().splitlines()
    for excerpt in r['excerpts']:
        assert lines[excerpt['line']-1]==excerpt['text']
assert digest(read(HERE/'source.json')['dataset_source']['path'])==read(HERE/'source.json')['dataset_source']['sha256']
source=read(HERE/'source.json')
counts=Counter()
first={}
def context_only(pairs):
    return {k:v for k,v in pairs if k=='code_context'}
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for row,line in enumerate(Path(source['dataset_source']['path']).open(),1):
        context=json.loads(line,object_pairs_hook=context_only)['code_context']
        for node in ast.walk(ast.parse(context)):
            modules=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and not node.level and node.module else []
            for module in modules:
                root=module.split('.')[0]
                if root in source['import_roots']:
                    counts[root]+=1
                    first.setdefault(root,[])
                    if len(first[root])<4:
                        first[root].append(dict(jsonl_line=row,context_line=node.lineno,import_module=module))
assert row==source['rows']
for module,record in source['import_roots'].items():
    assert record['import_site_count']==counts[module] and record['first_sites']==first[module]
assert read(HERE/'context-literals.json')['extra_external_distributions_outside_declared_roots']==[]
refetch=read(HERE/'refetch-smoke.json')
assert refetch['result']['exit_code']==0
refetched=Path(refetch['directory'])/refetch['filename']
assert digest(refetched)==records['flatbuffers']['sha256']
remainder=read(HERE/'remainder.json')
assert remainder['na_count']==len(remainder['datasets'])
for r in remainder['sources']+[r for t in remainder['terminal_tasks'] for r in t['sources']]:
    path=Path(r['path'])
    if not path.is_absolute():path=ROOT/path
    assert digest(path)==r['sha256']
result=read(HERE/'result.json')
for label in ['resolve','install','check','negative']:
    command=read(HERE/f'raw/{label}.command.json')
    actual=result if label=='resolve' else result[label]
    assert all(actual[k]==v for k,v in command.items())
    assert command['exit_code']==(1 if label=='negative' else 0)
    if label!='check':
        for flag in ['--ignore-installed','--no-index','--no-cache-dir','--only-binary=:all:']:
            assert flag in command['argv']
        assert '--no-deps' not in command['argv']
assert '--require-hashes' in result['install']['argv']
assert 'No broken requirements found.' in (HERE/'raw/check.stdout.txt').read_text()
assert 'include-system-site-packages = false' in (HERE/'raw/pyvenv.cfg').read_text()
network=read(HERE/'raw/network.json')
assert network['errno']==101 and network['interfaces']==[[1,'lo']]
assert not network['route'].splitlines()[1:]
runtime=read(HERE/'raw/runtime.json')
assert runtime['version']==target['version'] and runtime['executable_sha256']==target['executable_sha256']
cleanup=read(HERE/'raw/cleanup.json')
assert cleanup['removed'] and not Path(cleanup['directory']).exists()
omitted=read(HERE/'raw/negative-inventory.json')['omitted']
assert omitted==[dict(name=records['flatbuffers']['name'],version=records['flatbuffers']['version'],filename=records['flatbuffers']['filename'])]
assert read(HERE/'raw/negative-inventory.json')['retained_candidates']==len(records)-1
negative=(HERE/'raw/negative.stdout.txt').read_text()+(HERE/'raw/negative.stderr.txt').read_text()
assert 'flatbuffers' in negative and 'ResolutionImpossible' in negative
boundary=read(HERE/'boundary-before.json')
registry=read(ROOT/'docs/dataset-blockers.json')
shared_before=read(HERE/'shared-before.json')
for blocker in registry['shared_blockers']:
    if blocker['id']=='scorer-offline-closure':
        assert blocker['observed']==shared_before['observed']+' '+(HERE/'observation.txt').read_text().strip()
        assert blocker['evidence'][:len(shared_before['evidence'])]==shared_before['evidence']
        assert len(blocker['evidence'])==len(shared_before['evidence'])+3
        blocker.pop('observed');blocker.pop('evidence')
assert registry==boundary['protected_registry']
summary=read(HERE/'summary.json')
tb=read(ROOT/'tests/fixtures/hg_wresolver5_tb/results.json')
assert summary['new_bounded_profiles']==1+len(tb)
prior=read(ROOT/'tests/fixtures/hg_wresolver4/summary.json')
assert summary['bounded_profiles_resolved']==summary['bounded_profiles']==prior['bounded_profiles']+summary['new_bounded_profiles']
assert summary['complete_nonempty_python_profiles']==prior['complete_nonempty_python_profiles']+1
assert summary['tb_demonstrated_bootstrap_profiles']==prior['tb_demonstrated_tasks']+len(tb)
assert summary['shared_datasets']==prior['shared_datasets']
assert summary['production_authorized'] is False
for path in HERE.rglob('*'):
    if path.is_file() and '__pycache__' not in str(path):
        assert path.stat().st_size<1_000_000,(path,path.stat().st_size)
        assert path.suffix not in ['.whl','.conda','.deb','.zip','.gz','.bz2','.body']
seal=HERE/'SHA256SUMS'
paths=sorted(p for p in HERE.rglob('*') if p.is_file() and p!=seal and '__pycache__' not in str(p))
if args.seal:
    seal.write_text(''.join(f'{digest(p)}  {p.relative_to(HERE)}\n' for p in paths))
else:
    for line in seal.read_text().splitlines():
        sha,path=line.split('  ',1)
        assert digest(HERE/path)==sha,path
print(json.dumps(dict(valid=True,ds1000_selected=len(records),target=target['marker_environment']['python_full_version'],
                      static_context_rows=read(HERE/'source.json')['rows'],summary=summary,packet_files=len(paths)),sort_keys=True))
