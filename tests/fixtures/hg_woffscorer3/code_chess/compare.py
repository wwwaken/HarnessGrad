#!/usr/bin/env python3
import json
from pathlib import Path
P=Path(__file__).resolve().parent
def compare(prefix,dataset):
 official=json.loads((P/(prefix+'-official.json')).read_text());local=json.loads((P/(prefix+'-local.json')).read_text())
 om={r['id']:r for r in official['cases']};lm={r['id']:r for r in local['cases']}
 assert om.keys()==lm.keys()
 counts={'inputs':len(om),'numeric_comparisons':0,'agreements':0,'divergences':0,'nonnumeric_inputs':0,'official_exceptions':0,'local_unmeasured':0}
 rows=[]
 for id,a in om.items():
  b=lm[id]
  assert a.get('gold')==b.get('gold') and a.get('prediction')==b.get('prediction') and a.get('tests')==b.get('tests') and a.get('solution')==b.get('solution')
  row={'id':id,'official_reward':a.get('reward'),'local_reward':b.get('reward'),'official_error':a.get('error'),'local_evidence':b.get('evidence')}
  if 'reward' in a and 'reward' in b:
   same=a['reward']==b['reward'];row['status']='agree' if same else 'diverge';counts['numeric_comparisons']+=1;counts['agreements' if same else 'divergences']+=1
  else: row['status']='nonnumeric';counts['nonnumeric_inputs']+=1
  if 'error' in a:counts['official_exceptions']+=1
  if 'reward' not in b:counts['local_unmeasured']+=1
  if prefix=='lcb':
   row['official_per_test']=a.get('per_test');row['local_per_test']=b.get('evidence',{}).get('per_test');row['official_metadata']=a.get('metadata');row['per_test_equal']=row['official_per_test']==row['local_per_test'] if row['local_per_test'] is not None else None
  else:
   row['local_upstream_reward']=b.get('local_upstream_reward');row['strict_verdict']=b.get('returned',{}).get('verdict')
  rows.append(row)
 result={'dataset':dataset,'counts':counts,'per_input':rows}
 if prefix=='chess':
  numeric=[r for r in rows if r['official_reward'] is not None and r['local_upstream_reward'] is not None]
  result['upstream_diagnostic_counts']={'numeric_comparisons':len(numeric),'agreements':sum(r['official_reward']==r['local_upstream_reward'] for r in numeric),'divergences':sum(r['official_reward']!=r['local_upstream_reward'] for r in numeric),'nonnumeric_inputs':len(rows)-len(numeric)}
 return result
strict=json.loads((P/'lcb-official-strict-probe.json').read_text())
print(json.dumps({'livecodebench':compare('lcb','livecodebench'),'chessbench_puzzles':compare('chess','chessbench_puzzles'),'lcb_strict_probe':{'inputs':len(strict['cases']),'exceptions':sum('error' in r for r in strict['cases']),'numeric_scores':sum('reward' in r for r in strict['cases'])}},indent=2,sort_keys=True))
