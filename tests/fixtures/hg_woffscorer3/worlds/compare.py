import json
from pathlib import Path
F=Path(__file__).resolve().parent
out={}
for name in ['alfworld','appworld']:
 sides={}
 for side in ['official','local']:
  obj=json.loads((F/f'{name}-{side}.json').read_text())
  if name=='appworld':rows=[row for child in obj['children'] for row in child['output']['results']]
  else:rows=obj['results']
  sides[side]={r['id']:r for r in rows}
 rows=[]
 for id_,official in sides['official'].items():
  local=sides['local'][id_];measured=official.get('measured',False) and local.get('measured',False)
  rows.append({'id':id_,'official_measured':official.get('measured',False),'official_reward':official.get('reward'),'official_error':official.get('error'),'local_measured':local.get('measured',False),'local_reward':local.get('reward'),'local_error':local.get('error') or (local.get('evidence',{}).get('error')),'numeric_comparison':measured,'agreement':official['reward']==local['reward'] if measured else None})
 out[name]={'counts':{'controlled_inputs':len(rows),'numeric_comparisons':sum(x['numeric_comparison'] for x in rows),'numeric_agreements':sum(x['agreement'] is True for x in rows),'numeric_divergences':sum(x['agreement'] is False for x in rows),'nonnumeric_inputs':sum(not x['numeric_comparison'] for x in rows),'official_errors':sum(x['official_error'] is not None for x in rows),'local_unmeasured':sum(not x['local_measured'] for x in rows)},'results':rows}
(F/'comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
