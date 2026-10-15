import json,hashlib,importlib.metadata
from pathlib import Path
F=Path(__file__).resolve().parent
S=F/'source'
base=Path(importlib.metadata.distribution('alfworld').locate_file('alfworld'))
identity={'upstream_git_revision':None,'distributions':{n:importlib.metadata.version(n) for n in ['alfworld','textworld','fast_downward_textworld','torch','numpy']},'files':[]}
for rel in ['data/alfred.pddl','data/alfred.twl2','agents/eval/evaluate_dagger.py','agents/environment/alfred_tw_env.py']:
 p=base/rel;b=p.read_bytes();out=S/('alfworld-'+p.name);out.write_bytes(b)
 identity['files'].append({'path':str(p),'copy':str(out.relative_to(F)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
for rel in ['data/datasets/alfworld/verify/check.py','data/datasets/alfworld/lib/gym_env.py']:
 p=F.parents[3]/rel;b=p.read_bytes();identity['files'].append({'path':rel,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
problem='''(define (problem control) (:domain alfred)
 (:objects agent1 - agent loc1 - location countertop_bar_1 - receptacle apple_bar_1 - object countertoptype - rtype appletype - otype)
 (:init (atLocation agent1 loc1) (receptacleAtLocation countertop_bar_1 loc1) (inReceptacle apple_bar_1 countertop_bar_1) (pickupable apple_bar_1) (objectAtLocation apple_bar_1 loc1) (objectType apple_bar_1 appletype) (receptacleType countertop_bar_1 countertoptype) (canContain countertoptype appletype))
 (:goal (and (holds agent1 apple_bar_1))))'''
game={'pddl_domain':(base/'data/alfred.pddl').read_text(),'grammar':(base/'data/alfred.twl2').read_text(),'pddl_problem':problem}
(F/'alfworld-game.tw-pddl').write_text(json.dumps(game,indent=2)+'\n')
cases=[{'id':'take-win','actions':['take apple 1 from countertop 1']},{'id':'look-no-win','actions':['look']},{'id':'invalid-no-win','actions':['dance in place']},{'id':'win-then-invalid','actions':['take apple 1 from countertop 1','dance in place']},{'id':'budget-truncation','actions':['look','look','look','look','take apple 1 from countertop 1']},{'id':'empty','actions':[]}]
(F/'alfworld-inputs.json').write_text(json.dumps({'domain':'authored PDDL problem; unchanged installed ALFWorld domain+grammar; no released game or generated walkthrough','budget':4,'cases':cases},indent=2)+'\n')
for package in ['alfworld','textworld','fast_downward_textworld','torch','numpy']:
 dist=importlib.metadata.distribution(package)
 for leaf in ['METADATA','WHEEL','RECORD']:
  p=Path(dist._path)/leaf
  if p.is_file():identity['files'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
 if package in ['textworld','fast_downward_textworld']:
  for rel in dist.files:
   p=Path(dist.locate_file(rel))
   if p.suffix == '.so' or str(rel).endswith(('pddl.py','logic/__init__.py','gym/envs/textworld.py','gym/envs/textworld_batch.py')):
    identity['files'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(F/'alfworld-identities.json').write_text(json.dumps(identity,indent=2)+'\n')
