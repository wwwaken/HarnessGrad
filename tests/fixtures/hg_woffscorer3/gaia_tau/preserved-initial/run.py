"""Independent upstream/local calls on identical authored state and predictions."""
import contextlib, copy, hashlib, importlib.util, io, json, sys, tempfile, traceback
from pathlib import Path
P=Path(__file__).resolve().parent; R=P.parents[3]
sys.path.insert(0,str(R)); sys.path.insert(0,str(P/'source'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def loadmod(name,p):
    spec=importlib.util.spec_from_file_location(name,p); mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def captured(fn):
    out,err=io.StringIO(),io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try: result={'return':fn(),'error':None}
        except Exception as exc: result={'return':None,'error':{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}}
    return dict(result,stdout=out.getvalue(),stderr=err.getvalue())
def gaia(mode):
    scorer=loadmod('scorer',P/'source/scorer.py')
    local=loadmod('gaia_local_check',R/'data/datasets/gaia/verify/check.py') if mode=='local' else None
    cases=json.loads((P/'gaia-inputs.json').read_text())['cases']; rows=[]
    for c in cases:
        if mode=='official':
            # Missing file has the same canonical empty-string payload; all original strings retained.
            result=captured(lambda:bool(scorer.question_scorer(c['answer'],c['gold'])))
        else:
            with tempfile.TemporaryDirectory(prefix='hg-woffscorer3-gaia-') as tmp:
                d=Path(tmp);(d/'gold.json').write_text(json.dumps({'gold':c['gold'],'task_id':c['id']}))
                if not c.get('missing_answer'):(d/'answer.txt').write_text(c['answer'])
                argv=['check.py','--answer',str(d/'answer.txt'),'--gold',str(d/'gold.json'),'--reward-file',str(d/'reward.txt'),'--evidence-file',str(d/'evidence.json')]
                old=sys.argv;sys.argv=argv
                try:result=captured(local.main)
                finally:sys.argv=old
                result.update(argv=argv,evidence=json.loads((d/'evidence.json').read_text()) if (d/'evidence.json').exists() else None,reward=float((d/'reward.txt').read_text()) if (d/'reward.txt').exists() else None)
                owned_tmp=d
            result['scratch_removed']=not owned_tmp.exists()
        rows.append(dict(id=c['id'],**result))
    return rows

def tau(mode):
    cases=json.loads((P/'tau-inputs.json').read_text())['cases'];rows=[]
    if mode=='official':
        from tau_bench.envs.base import Env
        from tau_bench.types import Action,Task
        addr=loadmod('upstream_modify',P/'source/tau_bench/envs/retail/tools/modify_user_address.py').ModifyUserAddress
        transfer=loadmod('upstream_transfer',P/'source/tau_bench/envs/retail/tools/transfer_to_human_agents.py').TransferToHumanAgents
    else:
        local=loadmod('tau_local_check',R/'data/datasets/tau_bench/verify/check.py')
    for c in cases:
        if mode=='official':
            def call():
                task=Task(user_id='synthetic_user',actions=[Action(name=a['name'],kwargs=a['arguments']) for a in c['actions']],instruction='authored scorer control',outputs=c['outputs'])
                env=Env(lambda:copy.deepcopy(c['clean_db']),[addr,transfer],[task],'',[],'human','unused-no-model',task_index=0)
                env.terminate_tools=['transfer_to_human_agents']
                env.data=copy.deepcopy(c['agent_db']);env.actions=[Action(name='respond',kwargs={'content':s}) for s in c['says']]
                # Real HumanUserSimulationEnv consumes only fixture stdin, never a model.
                stdin=sys.stdin;sys.stdin=io.StringIO('continue\n'*20)
                try:
                    response=env.step(Action(name='transfer_to_human_agents',kwargs={'summary':'authored end'})) if c['done'] else env.step(Action(name='not_a_tool',kwargs={}))
                finally:sys.stdin=stdin
                return {'response':response.model_dump(),'actions_after':[a.model_dump() for a in env.actions],'final_replayed_database':env.data,'user_class':type(env.user).__name__}
            result=captured(call)
        else:
            with tempfile.TemporaryDirectory(prefix='hg-woffscorer3-tau-') as tmp:
                d=Path(tmp)
                for n,v in [('gt',dict(domain='retail',task_id=c['id'],user_id='synthetic_user',actions=c['actions'],outputs=c['outputs'])),('clean',c['clean_db']),('agent',c['agent_db'])]:(d/(n+'.json')).write_text(json.dumps(v))
                log=[{'kind':'say','name':'respond','arguments':{'content':s}} for s in c['says']]
                if c['done']:log.append({'kind':'done'})
                (d/'log.jsonl').write_text(''.join(json.dumps(a)+'\n' for a in log))
                argv=['--gt',str(d/'gt.json'),'--clean-db',str(d/'clean.json'),'--db',str(d/'agent.json'),'--lib',str(R/'data/datasets/tau_bench/lib'),'--call-log',str(d/'log.jsonl'),'--reward',str(d/'reward.txt'),'--evidence',str(d/'evidence.json')]
                result=captured(lambda:local.main(argv));result.update(argv=argv,evidence=json.loads((d/'evidence.json').read_text()) if (d/'evidence.json').exists() else None,reward=float((d/'reward.txt').read_text()) if (d/'reward.txt').exists() else None)
                owned_tmp=d
            result['scratch_removed']=not owned_tmp.exists()
        rows.append(dict(id=c['id'],**result))
    return rows

dataset,mode=sys.argv[1:];inputfile=P/('gaia-inputs.json' if dataset=='gaia' else 'tau-inputs.json')
rows=(gaia if dataset=='gaia' else tau)(mode)
ident=[]
for name,m in list(sys.modules.items()):
    f=getattr(m,'__file__',None)
    if f and (str(P/'source') in f or name in ['numpy','litellm','pydantic']):
        path=Path(f); ident.append({'module':name,'path':str(path),'sha256':sha(path)})
print(json.dumps({'dataset':dataset,'mode':mode,'inputs_sha256':sha(inputfile),'loaded_modules':ident,'cases':rows,'production_runtime_observation':False},indent=2,sort_keys=True))
