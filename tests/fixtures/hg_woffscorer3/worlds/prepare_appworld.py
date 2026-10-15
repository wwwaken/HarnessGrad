"""Runs in already-local pinned image; reads package/public API docs, no tasks."""
import hashlib,importlib.metadata,json,os,pathlib,shutil,tarfile
F=pathlib.Path('/output')
root=pathlib.Path('/tmp/hg-woffscorer3-appworld-prepare')
root.mkdir(); os.environ['APPWORLD_ROOT']=str(root);os.environ['APPWORLD_CACHE']='/tmp/appworld-cache'
import appworld
from appworld.apps import get_all_apps
from appworld.collections.models import ModelCollection
from appworld.common.constants import DB_VERSION
from appworld.apps.admin.models import MainUser
from appworld.apps.supervisor.models import Supervisor,Task
identity={'upstream_git_revision':None,'distribution':'appworld','version':importlib.metadata.version('appworld'),'appworld_version':appworld.__version__,'image_id':os.environ['HG_IMAGE'],'files':[]}
base=pathlib.Path(appworld.__file__).parent
for rel in ['__init__.py','evaluator.py','environment.py','task.py','ground_truth.py','collections/models.py','common/utils.py','apps/supervisor/apis.py','apps/supervisor/models.py','apps/model_lib.py']:
 p=base/rel;b=p.read_bytes();target=F/'source'/'appworld'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 identity['files'].append({'path':str(p),'copy':str(target.relative_to(F)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
for leaf in ['METADATA','WHEEL','RECORD']:
 dist=importlib.metadata.distribution('appworld');p=pathlib.Path(dist._path)/leaf;b=p.read_bytes();target=F/'source'/'appworld-dist-info'/leaf;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 identity['files'].append({'path':str(p),'copy':str(target.relative_to(F)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
# Public API schema docs only. No released task directory or task ground truth is read.
data=root/'data';data.mkdir();shutil.copytree('/appworld/data/api_docs',data/'api_docs')
(data/'version.txt').write_text(DB_VERSION)
p=(root/'build-dbs');p.mkdir()
mc=ModelCollection.load(from_db_home_path=str(p),to_db_home_path=str(p),load_apps=get_all_apps(),create_db=True)
user={'first_name':'Synthetic','last_name':'Control','email':'control@example.com','phone_number':'1234567890','birthday':'1990-01-01'}
MainUser.create_save(**user);Supervisor.create_save(**user)
Task.create_save(supervisor_id=1,instruction='Return the authored number 42.')
task_id='hgcontrol_1';task=data/'tasks'/task_id;task.mkdir(parents=True)
mc.save(str(task/'dbs'),format='full');mc.close()
supervisor={'first_name':user['first_name'],'last_name':user['last_name'],'email':user['email'],'phone_number':user['phone_number']}
spec={'instruction':'Return the authored number 42.','supervisor':supervisor,'datetime':'2026-10-01T12:00:00','db_version':DB_VERSION}
(task/'specs.json').write_text(json.dumps(spec,indent=2)+'\n')
gold=task/'ground_truth';gold.mkdir()
values={'metadata.json':{'mode':'minimal','difficulty':1,'num_apps':1,'num_apis':1,'num_api_calls':1,'num_solution_code_lines':0},'public_data.json':{},'private_data.json':{},'answer.json':'42','test_data.json':[{'requirement':'authored answer equals 42','label':'no_op_fail'}]}
for name,value in values.items(): (gold/name).write_text(json.dumps(value,indent=2)+'\n')
(gold/'evaluation.py').write_text('''# Authored fixture evaluator; NOT a released task evaluator.\nimport json\ndef evaluate(test, public_data, private_data, main_user, models, ground_truth_answer):\n    with test("authored answer equals 42"):\n        test.answer(json.loads(models.end.supervisor.Task.all()[0].answer), ground_truth_answer)\n''')
with tarfile.open(F/'appworld-controlled-inputs.tar.gz','w:gz') as tf: tf.add(data,arcname='data')
identity['controlled_archive_sha256']=hashlib.sha256((F/'appworld-controlled-inputs.tar.gz').read_bytes()).hexdigest()
identity['controlled_members']=[{'path':str(p.relative_to(data)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(data.rglob('*')) if p.is_file()]
(F/'appworld-identities.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps({'authored_task_id':task_id,'controlled_members':len(identity['controlled_members']),'archive_sha256':identity['controlled_archive_sha256'],'no_released_tasks_read':True},indent=2))
