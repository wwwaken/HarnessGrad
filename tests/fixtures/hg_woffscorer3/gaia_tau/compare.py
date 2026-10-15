import json
from pathlib import Path
P=Path(__file__).resolve().parent
result={}
for dataset in ['gaia','tau']:
    off,loc=[json.loads((P/f'{dataset}-{mode}.json').read_text()) for mode in ['official','local']]
    assert off['inputs_sha256']==loc['inputs_sha256']
    rows=[]
    for a,b in zip(off['cases'],loc['cases'],strict=True):
        assert a['id']==b['id']
        o=(float(a['return']) if dataset=='gaia' else a['return']['response']['reward']) if not a['error'] else None
        official_measured=not a['error'] and (dataset=='gaia' or a['return']['response']['info']['reward_info'] is not None)
        local_measured=b['reward'] is not None and not b['error']
        status='agree' if official_measured and local_measured and o==b['reward'] else ('diverge' if official_measured and local_measured else 'nonnumeric/classification')
        rows.append({'id':a['id'],'official':o,'local':b['reward'],'official_measured':official_measured,'local_measured':local_measured,'status':status,'official_error':a['error'],'local_error':b['error']})
    result[dataset]={'inputs':len(rows),'numeric_comparisons':sum(r['status']!='nonnumeric/classification' for r in rows),'agreements':sum(r['status']=='agree' for r in rows),'divergences':sum(r['status']=='diverge' for r in rows),'nonnumeric_or_classification':sum(r['status']=='nonnumeric/classification' for r in rows),'cases':rows}
print(json.dumps(result,indent=2,sort_keys=True))
