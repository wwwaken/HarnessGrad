"""BIRD Mini-Dev SQLite benchmark, official EX metric and separately named Soft-F1/R-VES."""
from __future__ import annotations
import json, os, zipfile
from pathlib import Path
from data import registry
KIND='dataset'
DATASET_ROOT=Path(os.environ.get('HG_BIRD_MINIDEV_DATA','/mnt/20t/xubuqiang/datasets/bird_minidev'))
BASE=DATASET_ROOT/'_src'/'unpacked'/'minidev'/'MINIDEV'
QUESTIONS=BASE/'mini_dev_sqlite.json'; GOLD=BASE/'mini_dev_sqlite_gold.sql'; DBS=BASE/'dev_databases'
REVISION='cc48ba16838204e4e214512030cb572eeb5f7bcdd999bae4b9b6ff12ec13b92f'

def _rows():
 q=json.load(open(QUESTIONS)); gs=[x.rstrip('\n').split('\t',1)[0] for x in open(GOLD)]
 return [{'task_id':f'bird_minidev/{i}','question_id':x['question_id'],'db_id':x['db_id'],'question':x['question'],'evidence':x.get('evidence',''),'gold_sql':gs[i]} for i,x in enumerate(q)]
_RECORDS=_rows(); _BY={x['task_id']:x for x in _RECORDS}
TASKS=[{'task_id':x['task_id'],'goal':x['question']+'\nWrite one SQLite query to answer it into answer.sql.','inputs':[]} for x in _RECORDS]
SPLIT=registry.default_split(TASKS); OFFICIAL_EVAL=None
DEFAULT_ENV={'kind':'files'}; ENV={x['task_id']:{'kind':'files'} for x in _RECORDS}

def _setup(x): return {'files':[{'path':'TASK.md','content':x['question']+'\n\nWrite SQL to answer this question in answer.sql.\n'}, {'path':'schema.json','content':json.dumps({'db_id':x['db_id'],'evidence':x['evidence']})}]}
def _verify(x):
 db=DBS/x['db_id']/(x['db_id']+'.sqlite')
 return {'kind':'command','argv':['python3','check.py','--db','database.sqlite','--gold','gold.sql','--pred','answer.sql','--reward-file','verifier/reward.txt','--evidence-file','verifier/evidence.json'],'reward_file':'/verifier/reward.txt','evidence_file':'/verifier/evidence.json','inputs':[{'path':'check.py','from':str(Path(__file__).parent/'bird_minidev'/'verify'/'check.py')},{'path':'gold.sql','content':x['gold_sql']},{'path':'database.sqlite','from':str(db)}]}
SETUP={x['task_id']:_setup(x) for x in _RECORDS}; VERIFY={x['task_id']:_verify(x) for x in _RECORDS}
def load(): return TASKS,{x['task_id']:x['gold_sql'] for x in _RECORDS}
def oracle_files(task): return {'answer.sql':_BY[task['task_id']]['gold_sql']}
def downloads(): return [{'kind':'http','name':'BIRD Mini-Dev ZIP','version':REVISION,'url':'https://bird-bench.oss-cn-beijing.aliyuncs.com/minidev.zip','size':'800943648 bytes','sha256':'cc48ba16838204e4e214512030cb572eeb5f7bcdd999bae4b9b6ff12ec13b92f','dst':'_src/minidev.zip','note':'Official 500-question Mini-Dev release with SQLite databases and gold SQL; EX is the published exact-set metric.'}]
def provision_status(): return {'root':str(DATASET_ROOT),'present':QUESTIONS.is_file() and GOLD.is_file() and DBS.is_dir(),'tasks':len(_RECORDS)}
