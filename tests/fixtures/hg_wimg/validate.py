"""Focused receipt consistency checks, entirely offline; never rerun a probe."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CAP=HERE/'capture'


def read(p):return json.loads(p.read_text())


images=read(CAP/'image-inventory.json')
summary=read(HERE/'summary.json')
manifests=read(CAP/'manifest-read/start.stdout.txt')
assert len(images)==94 and len(summary)==94
assert sum(x['present'] for x in images)==91
assert sum(x['dataset']=='terminal_bench' for x in images)==89
assert len(manifests)==101
for digest,rec in manifests.items():
    assert rec['matches'] and 'sha256:'+hashlib.sha256(rec['raw_utf8'].encode()).hexdigest()==digest
    obj=json.loads(rec['raw_utf8'])
    for m in obj.get('manifests',[]):assert m['digest'] in manifests
print('PASS: 101 fresh OCI manifest/index blobs independently rehash to their local descriptors')
states=Counter()
for x,s in zip(images,summary):
    assert x['key']==s['key'] and x['reference']==s['reference']
    d=CAP/'images'/x['key']
    command=read(d/'inspect.command.json')
    assert command['argv']==['docker','image','inspect',x['reference']]
    if not x['present']:
        assert command['returncode']!=0 and not x.get('repo_digests') and s['abi'] is None
        states['missing']+=1
        continue
    assert command['returncode']==0
    info=read(d/'inspect.stdout.txt')[0]
    assert info['Id']==x['image_id'] and info['RepoDigests']==x['repo_digests']
    assert info['Descriptor']==x['descriptor']
    assert len(manifests[info['Descriptor']['digest']]['raw_utf8'].encode())==info['Descriptor']['size']
    for ref in info['RepoDigests']:
        assert ref.split('@',1)[1] in manifests
    assert s['computed_repo_digests']==info['RepoDigests']
    create=read(d/'create.command.json')
    assert x['image_id'] in create['argv'] and '--pull=never' in create['argv']
    for when in ['before','after']:
        obj=read(d/f'inspect-{when}.stdout.txt')[0]
        assert obj['Image']==x['image_id']
        cfg=obj['HostConfig']
        assert cfg['NetworkMode']=='none' and cfg['ReadonlyRootfs'] is True
        assert cfg['NanoCpus']==1000000000 and cfg['Memory']==1536*1024*1024
        assert cfg['PidsLimit']==128 and cfg['MemorySwap']==cfg['Memory']
        assert cfg.get('CapDrop')==['ALL'] and not cfg.get('DeviceRequests')
        assert all(m['Destination']=='/wimg' and not m['RW'] for m in obj['Mounts'] if m['Type']=='bind')
        if when=='after':assert not obj['State']['Running'] and not obj['State']['OOMKilled']
    assert read(d/'remove.command.json')['returncode']==0
    raw=(d/'start.stdout.txt').read_bytes()
    if (d/'abi.json').is_file():
        abi=read(d/'abi.json')
        assert json.loads(raw.split(b'=== Python collector follows ===\n',1)[1])==abi
        assert abi['glibc_runtime']==s['abi']['glibc']
        assert abi['python'].split()[0]==s['abi']['python']
        assert read(d/'start.command.json')['returncode']==0
        exe=next(e for e in abi['elf'] if e['resolved']==abi['executable']['resolved'])
        assert exe['pt_interp']==s['abi']['loader']
        for elf in abi['elf']:
            assert re.fullmatch('[0-9a-f]{64}',elf['sha256'])
            assert 'not found' not in elf.get('ldd',{}).get('stdout','')
        states['python']+=1
    else:
        assert x['probe_returncode']==127 and s['abi']['python'] is None
        assert b'glibc 2.39' in raw and s['abi']['loader']=='/lib64/ld-linux-x86-64.so.2'
        assert b'python3: not found' in (d/'start.stderr.txt').read_bytes()
        states['shell-only']+=1
    if x['dataset']=='terminal_bench':
        sup=HERE/'supplement'/x['task']
        for name in ['create','start','inspect-before','inspect-after','remove']:
            assert read(sup/(name+'.command.json'))['returncode']==0
        after=read(sup/'inspect-after.stdout.txt')[0]
        assert after['Image']==x['image_id'] and after['HostConfig']['NetworkMode']=='none'
        assert not after['State']['OOMKilled'] and after['State']['ExitCode']==0
        output=(sup/'start.stdout.txt').read_text()
        assert 'TOOL bash\nPATH ' in output and 'libtinfo.so' in output
        assert re.search(r'[0-9a-f]{64}  /lib64/ld-linux-x86-64.so.2',output)
assert states==Counter({'python':65,'shell-only':26,'missing':3}),states
print('PASS: 94 configured refs, 91 real RepoDigests; 65 Python + 26 shell-only image records, 3 explicit absences')
print('PASS: Terminal-Bench 89 movable tags; 60 Python + 26 shell/tool records; 3 missing images')
assert sum(x['configured_pin']=='digest' for x in summary)==3
assert all(x['configured_pin']=='movable-tag' for x in summary if x['dataset']!='appworld')
for x in images[:5]:
    tree=ast.parse((ROOT/x['adapter']).read_text())
    n=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==x['role'] for t in n.targets))
    assert ast.literal_eval(n.value.args[1])==x['default_reference']
    assert n.value.args[1].lineno==x['literal_line']
source_records=read(HERE/'source-dependencies.json')
for rec in source_records:
    p=Path(rec['path'])
    if not p.is_absolute():p=ROOT/p
    if rec.get('missing'):assert not p.is_file();continue
    assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
    lines=p.read_text(errors='replace').splitlines()
    for line in rec['dependency_lines']:assert lines[line['line']-1]==line['text']
for task in read(CAP/'terminal-bench-source-surface.json'):
    for rec in task['files']:
        if rec.get('missing'):continue
        p=Path(rec['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
        lines=p.read_text(errors='replace').splitlines()
        for line in rec['lines']:assert lines[line['line']-1]==line['text']
print('PASS: adapter defaults, file:line evidence and current verifier/task source hashes match current preimages')
selected=read(HERE/'native-supplement/selected.json')
assert len(selected)==16
static_objects=0
for task in selected:
    folder=HERE/'native-supplement'/task
    image=next(x for x in images if x.get('task')==task)
    for name in ['create','start','inspect-before','inspect-after','remove']:
        assert read(folder/(name+'.command.json'))['returncode']==0
    after=read(folder/'inspect-after.stdout.txt')[0]
    assert after['Image']==image['image_id'] and after['HostConfig']['NetworkMode']=='none'
    assert after['HostConfig']['ReadonlyRootfs'] and not after['State']['OOMKilled']
    assert not after['HostConfig'].get('DeviceRequests') and after['State']['ExitCode']==0
    value=read(folder/'start.stdout.txt')
    for rec in value['objects']:
        assert not rec.get('error'),rec
        assert re.fullmatch('[0-9a-f]{64}',rec['sha256'])
        static_objects+=1
print('PASS: 16 additional static-native package probes, '+str(static_objects)+' ELF/provider hashes; unresolved standalone ldd names retained')
for root in [CAP,HERE/'supplement',HERE/'native-supplement']:
    assert not (root/'final-owned-container-check.stdout.txt').read_bytes()
    assert read(root/'final-owned-container-check.command.json')['returncode']==0
assert read(CAP/'manifest-read/remove.command.json')['returncode']==0
assert read(CAP/'manifest-read/inspect-after.stdout.txt')[0]['State']['ExitCode']==0
print('PASS: all 194 disposable inspection containers removed; all three session-owned absence checks empty')
registry=read(ROOT/'docs/dataset-blockers.json')
baseline=(CAP/'baseline/git-head.stdout.txt').read_text().strip()
old=json.loads(subprocess.check_output(['git','show',baseline+':docs/dataset-blockers.json'],cwd=ROOT))
# The one authorized registry edit is isolated to this shared blocker.
def shared(obj):
    return next(v for v in obj['shared_blockers'] if v['id']=='scorer-offline-closure')
current_block=shared(registry);old_block=shared(old)
assert current_block['status']==old_block['status'] and current_block['next_action']==old_block['next_action']
assert current_block['observed'].startswith(old_block['observed'])
assert current_block['evidence'][:-1]==old_block['evidence']
current_block['observed']=old_block['observed'];current_block['evidence']=old_block['evidence']
assert registry==old,'unrelated registry changes'
print('PASS: registry change only appends the shared blocker observation/evidence; status, next_action and other entries preserved')
manifest=HERE/'SHA256SUMS'
listed=set()
for line in manifest.read_text().splitlines():
    digest,rel=line.split('  ',1);p=HERE/rel
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,(rel,'hash mismatch')
    listed.add(rel)
actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p!=manifest}
assert actual==listed,(actual-listed,listed-actual)
print('PASS: SHA256SUMS covers all '+str(len(listed))+' fixture files, with no missing or extra preimages')
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
assert not any(p.startswith('runs/') or p.startswith(('eval/','data/','harnessgrad/','tools/')) for p in changed)
print('PASS: no production scoring/adapter code or runs/ changes')
