"""Read-only independent receipt/source/result audit; no scorer replay."""
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[3]
def load(n):return json.loads((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ident=load('identities.json')
assert sha(P/'source/scorer.py')==ident['gaia']['sha256']
for rec in ident['files']:
    if 'local' in rec:
        path=R/rec['local'];assert sha(path)==rec['sha256'];assert path.read_bytes()==subprocess.check_output(['git','show',f"{ident['baseline']}:{rec['local']}"],cwd=R)
    else:assert sha(P/rec['retained'])==rec['sha256']
assert load('tau-full-import.json')['full_import'] is True
summary={}
for dataset in ['gaia','tau']:
    inp=load(f'{dataset}-inputs.json')['cases'];off=load(f'{dataset}-official.json');loc=load(f'{dataset}-local.json');comp=load('comparison.json')[dataset]
    assert off['inputs_sha256']==loc['inputs_sha256']==sha(P/f'{dataset}-inputs.json')
    counts=dict(inputs=0,numeric_comparisons=0,agreements=0,divergences=0,nonnumeric_or_classification=0)
    for i,o,l,c in zip(inp,off['cases'],loc['cases'],comp['cases'],strict=True):
        assert i['id']==o['id']==l['id']==c['id'];assert l['scratch_removed'] is True
        assert not o['error'] and not l['error']
        assert (l['return']==0)==(l['reward'] is not None)
        if l['reward'] is not None: assert float(l['evidence']['reward'])==l['reward']
        om=dataset=='gaia' or o['return']['response']['info']['reward_info'] is not None
        ov=float(o['return']) if dataset=='gaia' else o['return']['response']['reward']
        lm=l['reward'] is not None
        assert c['official']==ov and c['local']==l['reward'] and c['official_measured']==om and c['local_measured']==lm
        status=('agree' if ov==l['reward'] else 'diverge') if om and lm else 'nonnumeric/classification'
        assert c['status']==status
        counts['inputs']+=1
        if om and lm: counts['numeric_comparisons']+=1;counts['agreements' if status=='agree' else 'divergences']+=1
        else:counts['nonnumeric_or_classification']+=1
    assert {k:comp[k] for k in counts}==counts
    for result in [off,loc]:
        for m in result['loaded_modules']: assert sha(Path(m['path']))==m['sha256']
    summary[dataset]=counts
for path in P.glob('*.offline.txt'):
    lines=path.read_text().splitlines();guard=json.loads(lines[0])
    assert len(guard['socket_probes'])==3
    assert all(p=={'errno':1,'result':'denied'} for p in guard['socket_probes'].values())
    assert guard['cpu_limit_seconds']==120 and guard['nofile_limit']==256
    assert guard['production_runtime_observation'] is False
    audit=[json.loads(line) for line in lines if line.startswith('{"blocked_external_dataset_reads"')]
    assert len(audit)==1 and audit[0]['blocked_external_dataset_reads']==[]
assert (P/'offline_exec.py').read_bytes()==(R/'tests/fixtures/hg_woffscorer2/reasoning_gym/offline_exec.py').read_bytes()
print(json.dumps({'valid':True,'results':summary,'all_temporary_case_directories_removed':True},sort_keys=True))
