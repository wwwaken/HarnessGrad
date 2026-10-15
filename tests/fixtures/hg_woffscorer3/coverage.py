"""Derive a scope-specific coverage index from actual packet comparisons."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
read=lambda n:json.loads((P/n).read_text())
prior=['fever','physicsquestions','sportsunderstanding','gsm8k','strategyqa','hotpotqa','triviaqa','musique','twowikimultihopqa','reasoning_gym','bird_minidev','ds1000','spreadsheetbench','jericho','scienceworld']
new={}
b=read('bfcl/compare.json')
new['bfcl_v3']={'scope':'unchanged AST-selected Python prompting parser and undotted Simple checker; complete imports fail tree_sitter','counts':{k:v for k,v in b.items() if k!='cases'}}
c=read('code_chess/comparison.json')
for d,scope in [('livecodebench','complete upstream evaluation package, real run_test children and pass@1'),('chessbench_puzzles','unchanged AST-selected evaluate_puzzle_from_board; complete import fails absl')]:new[d]={'scope':scope,'counts':c[d]['counts']}
g=read('gaia_tau/comparison.json')
for d,up,scope in [('gaia','gaia','complete pinned question_scorer module and unchanged local verifier'),('tau','tau_bench','complete Env module, real terminal step/calculate_reward, authored retail state and human stdin')]:new[up]={'scope':scope,'counts':{k:v for k,v in g[d].items() if k!='cases'}}
for d,scope in [('alfworld','complete installed evaluate_dagger and real TextWorld/PDDL engine on authored game'),('appworld','installed complete generic evaluator/runtime, authored task predicate only; released task predicates unexecuted')]:
    off,loc=[read(f'worlds/{d}-{side}.json') for side in ['official','local']]
    def rows(data):
        if 'results' in data:return data['results']
        result=[]
        for child in data['children']:
            assert child['exit_code']==0 and len(child['output']['results'])==1
            row=child['output']['results'][0];assert row['id']==child['id'];result.append(row)
        return result
    official_rows,local_rows=rows(off),rows(loc)
    a=b=err=0
    for o,l in zip(official_rows,local_rows,strict=True):
        assert o['id']==l['id']
        if o.get('measured') and l.get('measured') and 'reward' in o and 'reward' in l:
            a+=o['reward']==l['reward'];b+=o['reward']!=l['reward']
        else:err+=1
    new[d]={'scope':scope,'counts':{'inputs':len(official_rows),'numeric_comparisons':a+b,'agreements':a,'divergences':b,'nonnumeric_or_classification':err}}
print(json.dumps({'prior_component_datasets':prior,'prior_component_dataset_count':len(prior),'new_component_datasets':new,'new_component_dataset_count':len(new),'combined_component_dataset_count':len(prior)+len(new),'wholly_without_any_component_execution_among_new_candidates':[],'still_no_new_packet_execution':['terminal_bench'],'still_incomplete_full_routes':['appworld','bfcl_v3','chessbench_puzzles','terminal_bench'],'terminal_bench':'prior one real official bash /tests/test.sh execution only, reports/w-net-receipts.md; no new replay or evidence reclassification','closure':'S1/S3/S4/S6 PARTIAL; no shared or dataset blocker closes'},indent=2,sort_keys=True))
