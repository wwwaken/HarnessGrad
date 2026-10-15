"""Audit packet integrity and unchanged authorized production/registry scope."""
import hashlib,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];BASE='9f78bcd'
def original(name):return subprocess.check_output(['git','show',f'{BASE}:{name}'],cwd=R)
def load(p):return json.loads(p.read_text())
manifest={}
for line in (P/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1);path=P/name
    assert path.is_file() and not path.is_symlink() and name not in manifest
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
    manifest[name]=digest
actual={str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=P/'SHA256SUMS'}
assert set(manifest)==actual
before=json.loads(original('docs/dataset-blockers.json'));after=load(R/'docs/dataset-blockers.json')
assert {k:v for k,v in before.items() if k!='shared_blockers'}=={k:v for k,v in after.items() if k!='shared_blockers'}
changes=[]
for a,b in zip(before['shared_blockers'],after['shared_blockers'],strict=True):
    if a==b:continue
    assert a['id']==b['id']=='scorer-offline-closure'
    assert {k:v for k,v in a.items() if k not in {'observed','evidence'}}=={k:v for k,v in b.items() if k not in {'observed','evidence'}}
    assert b['observed'].startswith(a['observed']) and b['evidence'][:len(a['evidence'])]==a['evidence']
    assert all(e['locator'] in (R/e['path']).read_text() for e in b['evidence'] if e['kind']=='repository')
    changes.append(b['id'])
assert changes==['scorer-offline-closure']
j=(R/'docs/adapter-integration-journal.md').read_bytes();assert j.startswith(original('docs/adapter-integration-journal.md'))
assert j.count(b'## 2026-10-15 Bounded official scorer evidence extension - w-offscorer3')==1
pins=load(P/'local-source-pins.json');assert pins['baseline']==BASE
for f in pins['files']:
    b=(R/f['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==f['sha256'];assert b==original(f['path'])
changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=R,text=True).splitlines()
assert all(f in ['docs/dataset-blockers.json','docs/adapter-integration-journal.md'] or f.startswith('tests/fixtures/hg_woffscorer3/') or f.startswith('reports/w-offscorer3-') for f in changed),changed
worlds=load(P/'worlds/comparison.json')
for dataset in ['alfworld','appworld']:
    inp=load(P/f'worlds/{dataset}-inputs.json');off,loc=[load(P/f'worlds/{dataset}-{mode}.json') for mode in ['official','local']]
    expected=hashlib.sha256((P/f'worlds/{dataset}-inputs.json').read_bytes()).hexdigest()
    if dataset=='appworld':
        def extract(data):
            rows=[]
            for child in data['children']:
                assert child['exit_code']==0 and len(child['output']['results'])==1
                output=child['output'];assert output['inputs_sha256']==expected and output['blocked_released_task_reads']==[]
                assert output['network']['external_probe']['errno']==101
                rows.extend(output['results'])
            return rows
        o,l=extract(off),extract(loc)
    else:
        assert off['inputs_sha256']==loc['inputs_sha256']==expected;o,l=off['results'],loc['results']
    for i,a,b,c in zip(inp['cases'],o,l,worlds[dataset]['results'],strict=True):
        assert i['id']==a['id']==b['id']==c['id']
        assert a['scratch_removed'] is True and b['scratch_removed'] is True
        field='calls' if dataset=='appworld' else 'actions'
        assert i[field]==a[field]==b[field]
        measured=a.get('measured',False) and b.get('measured',False)
        assert c['numeric_comparison']==measured
        assert c['official_reward']==a.get('reward') and c['local_reward']==b.get('reward')
        assert c['agreement']==(a['reward']==b['reward'] if measured else None)
coverage=json.loads(subprocess.check_output([sys.executable,str(P/'coverage.py')],cwd=R,text=True))
assert coverage==load(P/'coverage-summary.json')
for dataset in ['alfworld','appworld']:
    c=worlds[dataset]['counts'];d=coverage['new_component_datasets'][dataset]['counts']
    assert (c['numeric_comparisons'],c['numeric_agreements'],c['numeric_divergences'],c['nonnumeric_inputs'])==(d['numeric_comparisons'],d['agreements'],d['divergences'],d['nonnumeric_or_classification'])
print(json.dumps({'valid':True,'manifest_members':len(manifest),'production_source_pins_verified':len(pins['files']),'new_component_dataset_count':coverage['new_component_dataset_count'],'registry_change_only':'scorer-offline-closure observed plus additive evidence','closure':'S1/S3/S4/S6 remain PARTIAL'},sort_keys=True))
