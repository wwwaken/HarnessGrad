"""Call complete installed upstream evaluator vs unchanged local verifier.
The upstream agent is a scripted input supplier, with no model or learned state.
"""
import contextlib,hashlib,importlib.util,io,json,os,shutil,sys,tempfile,traceback
from pathlib import Path
F=Path(__file__).resolve().parent
R=F.parents[3]
mode=sys.argv[1]
inputs=json.loads((F/'alfworld-inputs.json').read_text())
results=[]
class Pool:
 def push_first_sight(self,x): self.value=x
 def push_batch(self,x): self.value=x
 def get(self): return self.value
class ScriptedInput:
 unstick_by_beam_search=False
 action_space='admissible'
 report_frequency=0
 def __init__(self,actions,budget): self.actions=actions;self.max_nb_steps_per_episode=min(len(actions),budget);self.observation_pool=Pool();self.index=0
 def eval(self): pass
 def init(self,n): assert n==1
 def get_task_and_obs(self,x): return ['Controlled authored goal'],x
 def preprocess_task(self,x): return x
 def preprocess_observation(self,x): return x
 def preprocess_action_candidates(self,x): return x
 def admissible_commands_greedy_generation(self,*args):
  action=self.actions[self.index];self.index+=1
  return [action],None,None
 def finish_of_episode(self,*args): pass
class RecordingEnv:
 def __init__(self,env): self.env=env;self.records=[]
 def seed(self,x): return self.env.seed(x)
 def reset(self):
  out=self.env.reset();self.records.append({'operation':'reset','raw':out});return out
 def step(self,actions):
  out=self.env.step(actions);self.records.append({'operation':'step','actions':actions,'raw':out});return out
 def close(self): self.env.close()
for case in inputs['cases']:
 out={'id':case['id'],'actions':case['actions'],'budget':inputs['budget']}
 stdout,stderr=io.StringIO(),io.StringIO()
 scratch=Path(tempfile.mkdtemp(prefix='hg-woffscorer3-alfworld-'))
 try:
  with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
   if mode=='official':
    import textworld,textworld.gym
    from alfworld.agents.environment.alfred_tw_env import AlfredDemangler,AlfredInfos
    from alfworld.agents.eval.evaluate_dagger import evaluate_dagger
    id_=textworld.gym.register_games([str(F/'alfworld-game.tw-pddl')],textworld.EnvInfos(won=True,admissible_commands=True,extras=['gamefile']),batch_size=1,asynchronous=False,max_episode_steps=inputs['budget'],wrappers=[AlfredDemangler(shuffle=False),AlfredInfos])
    env=RecordingEnv(textworld.gym.make(id_))
    try:
     raw=evaluate_dagger(env,ScriptedInput(case['actions'],inputs['budget']),num_games=1)
     out.update(measured=True,raw=raw,reward=float(raw['res_points'][0]))
    finally:
     out['native_records']=env.records;env.close();out['env_closed']=True
   elif mode=='local':
    sys.path.insert(0,str(R/'data/datasets/alfworld/lib'))
    spec=importlib.util.spec_from_file_location('unchanged_alfworld_check',R/'data/datasets/alfworld/verify/check.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    log=scratch/'actions.jsonl';log.write_text(''.join(json.dumps({'kind':'action','action':a})+'\n' for a in case['actions']))
    reward=scratch/'reward.txt';evidence=scratch/'evidence.json'
    argv=['--workdir',str(scratch),'--game',str(F/'alfworld-game.tw-pddl'),'--log',str(log),'--reward-file',str(reward),'--evidence-file',str(evidence),'--budget',str(inputs['budget'])]
    code=module.main(argv)
    raw=json.loads(evidence.read_text());out.update(argv=argv,exit_code=code,evidence=raw,measured=raw.get('measured',False))
    if reward.is_file(): out['reward']=float(reward.read_text())
   else: raise ValueError(mode)
 except Exception as exc:
  out.update(measured=False,error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
 finally:
  out['stdout']=stdout.getvalue();out['stderr']=stderr.getvalue();shutil.rmtree(scratch);out['scratch_removed']=not scratch.exists();results.append(out)
print(json.dumps({'mode':mode,'inputs_sha256':hashlib.sha256((F/'alfworld-inputs.json').read_bytes()).hexdigest(),'game_sha256':hashlib.sha256((F/'alfworld-game.tw-pddl').read_bytes()).hexdigest(),'results':results},indent=2,default=str))
