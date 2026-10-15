#!/usr/bin/env python3
"""Recheck retained source, inputs, raw joins, guard observations and byte manifest."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
P=Path(__file__).resolve().parent;R=P.parents[3]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
identity=json.loads((P/'source-identity.json').read_text())
for source in identity['official_sources']:assert sha(P/source['path'])==source['sha256']
for source in identity['local_sources']:assert sha(R/source['path'])==source['sha256']
source=P/'source/chessbench_puzzles/searchless_chess/src/puzzles.py'
node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_puzzle_from_board')
assert (P/identity['selected_chess_function']['path']).read_text()=='\n'.join(source.read_text().splitlines()[node.lineno-1:node.end_lineno])+'\n'
assert sha(P/identity['selected_chess_function']['path'])==identity['selected_chess_function']['sha256']
assert sha(P/'offline_exec.py')==sha(R/'tests/fixtures/hg_woffscorer2/reasoning_gym/offline_exec.py')
inputs=json.loads((P/'inputs.json').read_text())
comparison=json.loads((P/'comparison.json').read_text())
assert json.loads(subprocess.check_output([sys.executable,str(P/'compare.py')],text=True))==comparison
for prefix,dataset in [('lcb','livecodebench'),('chess','chessbench_puzzles')]:
 official=json.loads((P/(prefix+'-official.json')).read_text());local=json.loads((P/(prefix+'-local.json')).read_text())
 assert [r['id'] for r in official['cases']]==[r['id'] for r in local['cases']]==[r['id'] for r in inputs[dataset]]
 for case,a,b in zip(inputs[dataset],official['cases'],local['cases']):
  for field in ('gold','prediction') if prefix=='chess' else ('tests','solution'):assert case[field]==a[field]==b[field]
 if prefix=='chess':assert local['empty_dataset_record_cache']
 else:
  assert official['full_module_import']['successful'];assert official['cleanup']['active_children']==[]
  assert local['cleanup']['scratch_removed'];assert not Path(local['scratch_root']).exists()
  for row in local['cases']:
   guard=json.loads(row['stderr'].splitlines()[0]);assert guard['socket_probes']=={'1':{'errno':1,'result':'denied'},'2':{'errno':1,'result':'denied'},'10':{'errno':1,'result':'denied'}}
   assert json.loads(row['stderr'].splitlines()[-1])['blocked_external_dataset_reads']==[]
for name in ['chess-official','chess-local','lcb-local','lcb-official-strict-probe']:
 lines=(P/(name+'-offline.txt')).read_text().splitlines();guard=json.loads(lines[0]);assert guard['production_runtime_observation'] is False
 assert all(v['result']=='denied' and v['errno']==1 for v in guard['socket_probes'].values())
 assert json.loads(lines[-1])['blocked_external_dataset_reads']==[]
lines=(P/'lcb-official-offline.txt').read_text().splitlines();guard=json.loads(lines[0]);assert guard['parent_netns']!=guard['netns'] and guard['external_probe']['result']=='no route'
assert json.loads(lines[-1])['blocked_external_dataset_reads']==[]
assert comparison['lcb_strict_probe']['numeric_scores']==0
manifest={}
for line in (P/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);assert sha(P/name)==digest,name;manifest[name]=digest
actual={str(path.relative_to(P)) for path in P.rglob('*') if path.is_file() and path.name!='SHA256SUMS'}
assert actual==manifest.keys(),(actual-manifest.keys(),manifest.keys()-actual)
print(json.dumps({'verified_fixture_files':len(manifest),'unchanged_source_files':len(identity['local_sources']),'official_source_files':len(identity['official_sources']),'comparisons':{d:comparison[d]['counts'] for d in ['livecodebench','chessbench_puzzles']},'guard_and_cleanup_checks':'passed'},indent=2,sort_keys=True))
