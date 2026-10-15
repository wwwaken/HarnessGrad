"""Read-only independent source, artifact, metadata graph and actual process audit."""
import argparse
import ast
import email
import hashlib
import json
from pathlib import Path
import sys
import zipfile
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.tags import parse_tag
from packaging.utils import canonicalize_name, parse_wheel_filename
from common import HERE, ROOT, digest

parser=argparse.ArgumentParser();parser.add_argument('--wheel-directory',type=Path);args=parser.parse_args()
read=lambda p:json.loads(p.read_text())
audit=read(HERE/'source-audit.json');inputs=read(HERE/'inputs.json');results=read(HERE/'results.json')
expected=['build-cython-ext','headless-terminal','hf-model-inference']
assert [r['task_id'] for r in audit['selected']]==expected
assert set(results)==set(inputs['profiles'])==set(expected)
assert audit['selected_task_count']==audit['distinct_profile_count']==len(expected)
assert [(r['task_id'],r['disposition']) for r in audit['considered_prefix']]==[
    ('build-cython-ext','selected-distinct-bootstrap'),('fix-code-vulnerability','duplicate-bootstrap-graph'),
    ('headless-terminal','selected-distinct-bootstrap'),('hf-model-inference','selected-distinct-bootstrap')]
assert audit['total_task_count']==len([p for p in Path(audit['selected'][0]['script_origin']).parents[2].iterdir() if p.is_dir() and (p/'task.toml').is_file()])
source_hashes=dict(line.split(maxsplit=1)[::-1] for line in (HERE/'raw/source-sha256sum.stdout.txt').read_text().splitlines())
for record in audit['selected']:
    origin=Path(record['script_origin']);assert digest(origin)==record['script_sha256']==source_hashes[str(origin)]
    assert (HERE/record['script_preimage']).read_bytes()==origin.read_bytes()
    assert (HERE/'profiles'/record['task_id']/'roots.in').read_text().splitlines()==record['root_requirements']
    for declaration in record['declarations']:
        assert origin.read_text().splitlines()[declaration['line']-1]==declaration['text']
    for kind in ['test_import_audit','image_declaration_audit']:
        item=record[kind];p=Path(item['origin'])
        assert digest(p)==item['sha256']==source_hashes[str(p)]
    test=record['test_import_audit'];source=Path(test['origin']).read_text();tree=ast.parse(source)
    actual=[{'line':n.lineno,'text':ast.get_source_segment(source,n)} for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
    assert sorted(actual,key=lambda n:n['line'])==[{'line':i['line'],'text':i['text']} for i in test['imports']]
    for item in record['image_declaration_audit']['excerpts']:
        assert Path(record['image_declaration_audit']['origin']).read_text().splitlines()[item['line']-1]==item['text']
artifacts={a['key']+'=='+a['version']:a for a in inputs['artifacts']}
assert len(artifacts)==len(inputs['artifacts'])
independent=dict(line.split(maxsplit=1)[::-1] for line in (HERE/'raw/wheel-sha256sum.stdout.txt').read_text().splitlines())
target_tags={t for s in inputs['python']['tags'] for t in parse_tag(s)}
environment=inputs['python']['marker_environment'];assert environment['python_full_version']=='3.12.4'
assert digest(inputs['python']['executable'])==inputs['python']['sha256']
for key,a in artifacts.items():
    p=(args.wheel_directory/a['filename']) if args.wheel_directory else Path(a['path'])
    assert p.stat().st_size==a['bytes']==a['advertised_size']
    assert digest(p)==a['sha256']==a['advertised_sha256']==a['discovery_sha256']==independent[a['path']]
    assert p.stat().st_size<=inputs['bounds']['max_http_wheel_bytes']
    assert a['url'].startswith('https://files.pythonhosted.org/') and a['status']==a['index_receipt']['status']==200
    assert a['index_receipt']['url']==f"https://pypi.org/pypi/{a['key']}/{a['version']}/json"
    assert a['index_receipt']['bytes']<=inputs['bounds']['max_index_response_bytes']
    assert not a['index_receipt']['body_retained']
    assert sorted(map(str,parse_wheel_filename(p.name)[3]&target_tags))==a['matching_tags'] and a['matching_tags']
    with zipfile.ZipFile(p) as z:
        for kind,info in a['metadata'].items():
            raw=z.read(info['member']);text=ROOT/info['path']
            assert raw==text.read_bytes() and hashlib.sha256(raw).hexdigest()==info['sha256'] and len(raw)==info['bytes']
    meta=email.message_from_bytes((ROOT/a['metadata']['METADATA']['path']).read_bytes())
    assert canonicalize_name(meta['Name'])==a['key'] and meta['Version']==a['version']
    assert meta.get_all('Requires-Dist',[])==a['requires_dist']
    if a['requires_python']:assert SpecifierSet(a['requires_python']).contains(environment['python_full_version'])
plugin=read(HERE/'plugin-audit.json');a=next(a for a in artifacts.values() if a['key']=='pytest-json-ctrf')
p=(args.wheel_directory/a['filename']) if args.wheel_directory else Path(a['path'])
assert plugin['artifact_sha256']==a['sha256']
with zipfile.ZipFile(p) as z:
    for module in plugin['modules']:
        data=z.read(module['member']);assert hashlib.sha256(data).hexdigest()==module['sha256']
        source=data.decode();tree=ast.parse(source)
        imports=[{'line':n.lineno,'text':ast.get_source_segment(source,n)} for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
        assert sorted(imports,key=lambda n:n['line'])==module['imports']
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): roots=[a.name.split('.')[0] for a in node.names]
            elif isinstance(node,ast.ImportFrom) and node.level==0:roots=[node.module.split('.')[0]]
            else:continue
            assert all(r in sys.stdlib_module_names or r in {'pytest','ctrf'} for r in roots)
network=read(HERE/'raw/network.json')
assert network['errno']==101 and network['interfaces']==[[1,'lo']] and not network['route'].splitlines()[1:]
assert 'Network is unreachable' in network['error']
cleanup=read(HERE/'raw/cleanup.json');runtime=read(HERE/'raw/runtime.json')
assert cleanup['directory']==runtime['work_directory'] and cleanup['removed'] and not Path(cleanup['directory']).exists()
assert runtime['sha256']==inputs['python']['sha256']
summary={}
for name,result in results.items():
    keys=inputs['profiles'][name];selected={canonicalize_name(s['name']):s for s in result['selected']}
    records={artifacts[key]['key']:artifacts[key] for key in keys}
    assert set(selected)==set(records)
    assert len(keys)<=inputs['bounds']['max_wheels_per_profile'] and sum(a['bytes'] for a in records.values())<=inputs['bounds']['max_bytes_per_profile']
    profile=HERE/'profiles'/name
    assert set((profile/'constraints.txt').read_text().splitlines())==set(keys)
    report=read(HERE/'raw'/(name+'.pip-report.json'))
    assert {canonicalize_name(x['metadata']['name']) for x in report['install']}==set(records)
    assert set((profile/'resolved.lock').read_text().splitlines())=={f"{s['name']}=={s['version']} --hash=sha256:{s['sha256']}" for s in result['selected']}
    for item in report['install']:
        key=canonicalize_name(item['metadata']['name']);a=records[key]
        assert item['metadata']['version']==a['version'] and item['download_info']['archive_info']['hashes']['sha256']==a['sha256']==selected[key]['sha256']
    # Rebuild the reachable active default dependency graph independently from wheel METADATA.
    pending=list(map(Requirement,(profile/'roots.in').read_text().splitlines()));reached=set()
    while pending:
        requirement=pending.pop();key=canonicalize_name(requirement.name)
        assert key in records and not requirement.extras
        assert requirement.specifier.contains(records[key]['version'])
        if key in reached:continue
        reached.add(key)
        for line in records[key]['requires_dist']:
            edge=Requirement(line)
            if edge.marker is None or edge.marker.evaluate(environment|{'extra':''}):pending.append(edge)
    assert reached==set(records)
    assert 'include-system-site-packages = false' in (HERE/'raw'/(name+'-pyvenv.cfg')).read_text()
    for field,label,wanted in [(None,'resolve-',0),('install','install-',0),('check','check-',0),('negative','negative-',1)]:
        r=result if field is None else result[field]
        actual=read(HERE/'raw'/(label+name+'.command.json'))
        assert all(r[k]==v for k,v in actual.items())
        assert actual['exit_code']==wanted and actual['elapsed_seconds']<actual['timeout_seconds']==180
        if field!='check':
            assert '--no-deps' not in r['argv']
            assert all(flag in r['argv'] for flag in ['--ignore-installed','--no-index','--no-cache-dir','--only-binary=:all:'])
        if field=='install':assert '--require-hashes' in r['argv']
        if field in (None,'negative'):assert '--dry-run' in r['argv']
    missing=result['negative_removed'];assert missing['name']=='pluggy' and missing['version']==records['pluggy']['version']
    assert 'pluggy' not in {canonicalize_name(parse_wheel_filename(f)[0]) for f in missing['remaining_files']}
    assert set(missing['remaining_files'])=={a['filename'] for key,a in records.items() if key!='pluggy'}
    assert any('pluggy<2,>=1.5' in d for d in records['pytest']['requires_dist'])
    stdout=(HERE/'raw'/('negative-'+name+'.stdout.txt')).read_text()
    stderr=(HERE/'raw'/('negative-'+name+'.stderr.txt')).read_text()
    assert 'pytest 8.4.1 depends on pluggy<2 and >=1.5' in stdout
    assert 'ResolutionImpossible' in stderr
    assert 'No broken requirements found.' in (HERE/'raw'/('check-'+name+'.stdout.txt')).read_text()
    summary[name]={'selected':len(selected),'resolve':result['exit_code'],'install':result['install']['exit_code'],'check':result['check']['exit_code'],'negative':result['negative']['exit_code'],'missing':missing['name']+'=='+missing['version']}
refetch=read(HERE/'refetch-result.json');assert refetch['exit_code']==0
actual=[json.loads(line) for line in (HERE/'raw/refetch-verification.stdout.txt').read_text().splitlines()]
assert len(actual)==len(artifacts)
for receipt in actual:
    a=next(a for a in artifacts.values() if a['filename']==receipt['filename'])
    assert receipt['verified'] and receipt['sha256']==a['sha256'] and receipt['bytes']==a['bytes'] and receipt['url']==a['url']
files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
assert all(p.stat().st_size<1024*1024 for p in files)
assert not [p for p in files if p.suffix in {'.whl','.deb','.conda','.gz','.zip','.body'}]
print(json.dumps({'valid':True,'scope':audit['scope'],'profiles':summary,'selected_task_ids':expected,
    'new_distinct_bootstrap_profiles':len(results),'unique_artifacts':len(artifacts),'unique_artifact_bytes':sum(a['bytes'] for a in artifacts.values()),
    'packet_files':len(files),'packet_bytes':sum(p.stat().st_size for p in files),'largest_file':max((p.stat().st_size,str(p.relative_to(HERE))) for p in files),
    'complete_dataset_profile_increment':0,'shared_or_dataset_blockers_closed':0},indent=2))
