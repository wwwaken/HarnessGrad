#!/usr/bin/env python3
"""Separate direct upstream entry points from unchanged production local checks."""
import __future__
import ast
from collections.abc import Sequence
import contextlib
import hashlib
import importlib
import importlib.util
import io
import json
import multiprocessing
import gc
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

P=Path(__file__).resolve().parent
R=P.parents[3]
sys.path.insert(0,str(R))
CASES=json.loads((P/'inputs.json').read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def err():
 exc=sys.exception();return {'error':{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}}
def snapshot_runtime():
 import numpy
 import chess
 return {'numpy':{'version':numpy.__version__,'path':numpy.__file__,'sha256':sha(numpy.__file__)},'chess':{'version':chess.__version__,'path':chess.__file__,'sha256':sha(chess.__file__)}}

def chess_official():
 import chess
 source=P/'source/chessbench_puzzles/searchless_chess/src/puzzles.py'
 sys.path.insert(0,str(P/'source/chessbench_puzzles'))
 out={'dataset':'chessbench_puzzles','mode':'official','runtime':snapshot_runtime()}
 full_stdout=io.StringIO();full_stderr=io.StringIO()
 try:
  with contextlib.redirect_stdout(full_stdout),contextlib.redirect_stderr(full_stderr):
   module=importlib.import_module('searchless_chess.src.puzzles')
  evaluator=module.evaluate_puzzle_from_board
  out['full_module_import']={'successful':True}
 except Exception:
  out['full_module_import']={'successful':False,**err()}
  # Same exact upstream function body; postponing type annotation resolution avoids
  # importing engine definitions. There are no substitutes for scorer dependencies.
  node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_puzzle_from_board')
  namespace={'chess':chess,'Sequence':Sequence}
  code=compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec',flags=__future__.annotations.compiler_flag,dont_inherit=True)
  exec(code,namespace)
  evaluator=namespace['evaluate_puzzle_from_board']
  out['selected_function_execution']={'function':'evaluate_puzzle_from_board','body_modified':False,'selected_source_sha256':sha(P/'source/chess-selected-evaluate_puzzle_from_board.py')}
 out['full_import_stdout']=full_stdout.getvalue();out['full_import_stderr']=full_stderr.getvalue()
 rows=[]
 for case in CASES['chessbench_puzzles']:
  log=[]
  class ScriptedEngine:
   def __init__(self): self.tokens=iter(case['prediction'].strip().split())
   def play(self,*,board):
    token=next(self.tokens)
    log.append({'fen':board.fen(),'uci':token})
    return chess.Move.from_uci(token)
  row={'id':case['id'],'gold':case['gold'],'prediction':case['prediction']}
  try:
   board=chess.Board(case['gold']['fen'])
   row['returned']=evaluator(board,case['gold']['moves'],ScriptedEngine());row['reward']=float(row['returned']);row['final_fen']=board.fen()
  except Exception: row.update(err())
  row['engine_calls']=log;rows.append(row)
 out['cases']=rows;return out

def chess_local():
 from data.datasets import chessbench_puzzles
 out={'dataset':'chessbench_puzzles','mode':'local','runtime':snapshot_runtime(),'source':{'path':str(R/'data/datasets/chessbench_puzzles.py'),'sha256':sha(R/'data/datasets/chessbench_puzzles.py')},'cases':[]}
 for case in CASES['chessbench_puzzles']:
  row={'id':case['id'],'gold':case['gold'],'prediction':case['prediction']}
  try:
   row['returned']=chessbench_puzzles.score(case['prediction'],case['gold']);row['reward']=row['returned']['reward'];row['local_upstream_reward']=row['returned']['official']['upstream']['reward']
  except Exception: row.update(err())
  out['cases'].append(row)
 assert chessbench_puzzles._SPEC._records == []
 out['empty_dataset_record_cache']=True
 return out

def lcb_official():
 sys.path.insert(0,str(P/'source/livecodebench'))
 out={'dataset':'livecodebench','mode':'official','runtime':snapshot_runtime(),'cases':[]}
 try:
  module=importlib.import_module('lcb_runner.evaluation.compute_code_generation_metrics')
  metric=importlib.import_module('lcb_runner.evaluation.pass_k_utils')
  out['full_module_import']={'successful':True,'path':module.__file__,'sha256':sha(module.__file__)}
 except Exception:
  out['full_module_import']={'successful':False,**err()};return out
 for case in CASES['livecodebench']:
  row={'id':case['id'],'tests':case['tests'],'solution':case['solution']}
  stdout=tempfile.TemporaryFile(mode='w+',encoding='utf-8');stderr=tempfile.TemporaryFile(mode='w+',encoding='utf-8')
  try:
   # Upstream wrapper executes actual run_test inside its own child and Manager.
   with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
    results,metadata=module.check_correctness({'input_output':json.dumps(case['tests'],sort_keys=True)+'\n'},case['solution'],timeout=6,debug=False)
    row.update({'per_test':results,'metadata':metadata,'reward':float(metric.compute_metrics_from_results({'task':[results]},k_list=[1])['pass@1'])})
  except Exception: row.update(err())
  stdout.seek(0);stderr.seek(0)
  row['captured_stdout']=stdout.read();row['captured_stderr']=stderr.read();stdout.close();stderr.close();out['cases'].append(row)
 gc.collect()
 out['cleanup']={'active_children':[{'pid':p.pid,'name':p.name,'alive':p.is_alive()} for p in multiprocessing.active_children()]}
 assert out['cleanup']['active_children']==[]
 return out

def lcb_local():
 out={'dataset':'livecodebench','mode':'local','runtime':snapshot_runtime(),'cases':[]}
 work=Path(tempfile.mkdtemp(prefix='hg-woffscorer3-lcb-local-',dir='/tmp'))
 out['scratch_root']=str(work)
 try:
  for name in ('testing_util.py','pass_k_utils.py'):
   shutil.copy2(P/'source/livecodebench/lcb_runner/evaluation'/name,work/name)
  for case in CASES['livecodebench']:
   folder=work/case['id'];folder.mkdir()
   tests=P/'inputs/livecodebench'/case['id']/'tests.json';solution=P/'inputs/livecodebench'/case['id']/'solution.py'
   assert tests.read_text()==json.dumps(case['tests'],sort_keys=True)+'\n' and solution.read_text()==case['solution']
   argv=[sys.executable,str(P/'offline_exec.py'),str(R/'data/datasets/livecodebench/verify/check.py'),'--tests',str(tests),'--solution',str(solution),'--reward-file',str(folder/'reward.txt'),'--evidence-file',str(folder/'evidence.json')]
   row={'id':case['id'],'tests':case['tests'],'solution':case['solution'],'argv':argv,'cwd':str(work)}
   try:
    result=subprocess.run(argv,cwd=work,capture_output=True,text=True,timeout=40)
    row.update({'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'evidence_raw':(folder/'evidence.json').read_text() if (folder/'evidence.json').exists() else None,'reward_raw':(folder/'reward.txt').read_text() if (folder/'reward.txt').exists() else None})
    if row['evidence_raw'] is not None: row['evidence']=json.loads(row['evidence_raw'])
    if row['reward_raw'] is not None: row['reward']=float(row['reward_raw'])
   except Exception: row.update(err())
   out['cases'].append(row)
 finally:
  shutil.rmtree(work);out['cleanup']={'scratch_removed':not work.exists()}
 return out

mode=sys.argv[1]
result={'chess-official':chess_official,'chess-local':chess_local,'lcb-official':lcb_official,'lcb-local':lcb_local}[mode]()
print(json.dumps(result,indent=2,sort_keys=True,default=lambda x:x.item() if hasattr(x,'item') else str(x)))
