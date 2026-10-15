"""Copy only scorer code, never task data; recompute and authenticate local Git bytes."""
import hashlib, json, shutil, subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parents[3]
def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
ident={'baseline':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'files':[]}
source=P/'source'; source.mkdir(exist_ok=True)
g=Path('/mnt/20t/xubuqiang/datasets/gaia/_src/scorer.py')
b=g.read_bytes(); expected='0d44c07f3046eec521697c22e3eaca8719cc81e422a8eaf32695c5f22bdac6e2'; assert sha(b)==expected
(source/'scorer.py').write_bytes(b)
ident['gaia']={'upstream':'gaia-benchmark/leaderboard','adapter_pinned_revision':'9f133d71362ecb0a1c7ff6b4dcfc2a6b9f8ffd1e','sha256':sha(b),'source':str(g),'provenance_limit':'existing adapter pin, no fresh remote attestation'}
t=Path('/mnt/20t/xubuqiang/datasets/tau-bench')
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=t,text=True).strip(); assert commit=='59a200c6d575d595120f1cb70fea53cef0632f6b'
names=['__init__.py','types.py','agents/__init__.py','agents/base.py','envs/__init__.py','envs/base.py','envs/user.py','envs/tool.py','envs/retail/tools/modify_user_address.py','envs/retail/tools/transfer_to_human_agents.py']
for n in names:
    rel='tau_bench/'+n; body=(t/rel).read_bytes(); assert body==subprocess.check_output(['git','show',f'{commit}:{rel}'],cwd=t)
    dest=source/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(body)
    ident['files'].append({'upstream_path':rel,'source':str(t/rel),'retained':str(dest.relative_to(P)),'sha256':sha(body)})
ident['tau_bench']={'upstream':'sierra-research/tau-bench','local_git_revision':commit,'provenance_limit':'local Git-object equality, no new remote acquisition attestation'}
for rel in ['data/datasets/gaia.py','data/datasets/gaia/verify/check.py','data/datasets/tau_bench.py','data/datasets/tau_bench/verify/check.py']:
    body=(R/rel).read_bytes(); assert body==subprocess.check_output(['git','show',f"{ident['baseline']}:{rel}"],cwd=R)
    ident['files'].append({'local':rel,'sha256':sha(body)})
# All inputs authored here, unrelated to released tasks.
gaia=[]
def gc(i,a,g,**kw): gaia.append(dict(id=i,answer=a,gold=g,**kw))
for args in [('number-exact','1234','1234'),('currency-comma','$1,234','1234'),('percent-unscaled','42%','42'),('number-wrong','12.1','12'),('number-invalid','twelve','12'),('float-inf-invalid','words','inf'),('float-nan','nan','nan'),('text-case-space',' SEA GULL! ','seagull'),('text-wrong','other','seagull'),('text-internal-newline','sea\ngull','seagull'),('list-separator','alpha; beta','alpha,beta'),('list-order','beta,alpha','alpha,beta'),('list-punctuation','alpha!, beta','alpha,beta'),('list-numeric','1.0;$2','1;2'),('list-length','alpha','alpha,beta'),('list-empty-item','alpha,','alpha,'),('list-space','  alpha , BETA  ','alpha,beta'),('blank-answer','','text'),('whitespace-answer','   ','text'),('empty-gold','',''),('placeholder-gold','?','?'),('punctuation-empty','!','')]: gc(*args)
gc('missing-answer','','text',missing_answer=True)
save(P/'gaia-inputs.json',{'kind':'authored synthetic scorer controls','cases':gaia})
clean={'users':{'synthetic_user':{'user_id':'synthetic_user','address':{'address1':'Old','address2':'','city':'City','state':'XX','country':'Synthetic','zip':'00000'}}},'orders':{},'products':{}}
kwargs=dict(user_id='synthetic_user',address1='New',address2='',city='City',state='XX',country='Synthetic',zip='12345')
action={'name':'modify_user_address','arguments':kwargs}
changed=json.loads(json.dumps(clean)); changed['users']['synthetic_user']['address'].update(address1='New',zip='12345')
cases=[]
def tc(i,db,outputs=[],says=[],done=True,actions=None):
    cases.append(dict(id=i,clean_db=clean,agent_db=db,outputs=outputs,says=says,done=done,actions=[action] if actions is None else actions))
tc('address-correct',changed);tc('address-wrong',clean);tc('output-present',changed,['12345'],['ZIP: 12,345'])
tc('output-missing',changed,['12345'],[]);tc('output-case',changed,['COMPLETE'],['Complete'])
tc('output-comma-asymmetric',changed,['12,345'],['12,345']);tc('unfinished',changed,done=False)
tc('unknown-ground-truth-tool',clean,actions=[{'name':'not_a_tool','arguments':{}}])
bad=json.loads(json.dumps(action));bad['arguments']['user_id']='absent_user';tc('ground-truth-tool-error-noop',clean,actions=[bad])
tc('terminate-skip',changed,actions=[action,{'name':'transfer_to_human_agents','arguments':{'summary':'synthetic'}}])
save(P/'tau-inputs.json',{'kind':'wholly authored retail state, task actions and utterances','cases':cases})
save(P/'identities.json',ident)
print(json.dumps({'copied_source_files':len(names)+1,'gaia_inputs':len(gaia),'tau_inputs':len(cases),'identities':'identities.json'},sort_keys=True))
