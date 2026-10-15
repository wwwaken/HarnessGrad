#!/usr/bin/env python3
"""Copy scorer-only pinned archive members, and author fresh controlled inputs."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

P = Path(__file__).resolve().parent
R = P.parents[3]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name, data): (P/name).write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
identities = {'archives':[], 'official_sources':[], 'local_sources':[], 'provenance_limit':'Existing adapter-pinned archive custody; no new remote authenticity attestation.'}
archives = [
 ('livecodebench','/mnt/20t/xubuqiang/datasets/livecodebench/_src/upstream.tar.gz','28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24','56c7c42aee979def86b69547ecd6d5a877a0e4940af8923bf4325ca0defecbaf'),
 ('chessbench_puzzles','/mnt/20t/xubuqiang/datasets/chessbench_puzzles/_src/searchless_chess.tar.gz','90ae0e6b121673fc3079aaeffa047580bb600c0a','9cf0832b04024a9e0a6edb59f0dee62aeadee3b9b97799b9a7521b2221f7d39a')]
for dataset, path, revision, expected in archives:
 actual=sha(path); assert actual==expected
 identities['archives'].append({'dataset':dataset,'path':path,'revision':revision,'sha256':actual,'bytes':Path(path).stat().st_size})
 with tarfile.open(path) as archive:
  for member in archive.getmembers():
   if not member.isfile(): continue
   sub = member.name.split('/',1)[1]
   if dataset=='livecodebench' and sub.startswith('lcb_runner/evaluation/') and sub.endswith('.py') and Path(sub).name not in {'old_results_check.py','compute_scores.py'}:
    target=P/'source/livecodebench'/sub
   elif dataset=='chessbench_puzzles' and sub.startswith('src/') and sub.endswith('.py') and Path(sub).name not in {'bagz.py','data_loader.py','metrics_evaluator.py','tournament.py','train.py','training.py'}:
    target=P/'source/chessbench_puzzles/searchless_chess'/sub
   else: continue
   target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(archive.extractfile(member).read())
   identities['official_sources'].append({'dataset':dataset,'member':member.name,'path':str(target.relative_to(P)),'sha256':sha(target),'bytes':target.stat().st_size})
for relative in ['data/datasets/livecodebench.py','data/datasets/livecodebench/verify/check.py','data/datasets/chessbench_puzzles.py','data/scaffolds/qa/base.py','tests/fixtures/hg_woffscorer2/reasoning_gym/offline_exec.py']:
 identities['local_sources'].append({'path':relative,'sha256':sha(R/relative)})
source=P/'source/chessbench_puzzles/searchless_chess/src/puzzles.py'
node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_puzzle_from_board')
selected='\n'.join(source.read_text().splitlines()[node.lineno-1:node.end_lineno])+'\n'
(P/'source/chess-selected-evaluate_puzzle_from_board.py').write_text(selected)
identities['selected_chess_function']={'path':'source/chess-selected-evaluate_puzzle_from_board.py','sha256':sha(P/'source/chess-selected-evaluate_puzzle_from_board.py'),'first_line':node.lineno,'last_line':node.end_lineno,'body_modified':False,'annotations':'future annotations only at compile time'}
save('source-identity.json',identities)
stdio={'inputs':['1 2\n','3 4\n','10 -3\n'],'outputs':['3\n','7\n','7\n'],'fn_name':None}
call={'inputs':['[1,2,3]','[]','[-4,6]'],'outputs':['6','0','2'],'fn_name':'total'}
lcb=[
 {'id':'stdio-pass','tests':stdio,'solution':'a,b=map(int,input().split()); print(a+b)\n'},
 {'id':'stdio-wrong-first','tests':stdio,'solution':'print(0)\n'},
 {'id':'stdio-partial','tests':stdio,'solution':'print(3)\n'},
 {'id':'stdio-timeout','tests':stdio,'solution':'while True: pass\n'},
 {'id':'stdio-runtime','tests':stdio,'solution':'raise RuntimeError("authored-runtime-control")\n'},
 {'id':'stdio-syntax','tests':stdio,'solution':'this is invalid python @\n'},
 {'id':'stdio-empty','tests':stdio,'solution':''},
 {'id':'call-pass','tests':call,'solution':'class Solution:\n    def total(self, xs): return sum(xs)\n'},
 {'id':'call-wrong','tests':call,'solution':'class Solution:\n    def total(self, xs): return len(xs)\n'},
 {'id':'call-missing-method','tests':call,'solution':'class Solution:\n    def other(self, xs): return sum(xs)\n'},
 {'id':'empty-tests','tests':{'inputs':[],'outputs':[],'fn_name':None},'solution':'print(0)\n'},
 {'id':'mismatched-tests','tests':{'inputs':['1\n','2\n'],'outputs':['0\n'],'fn_name':None},'solution':'print(0)\n'}]
fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
chess=[]
def add(id,moves,prediction, f=fen): chess.append({'id':id,'prediction':prediction,'gold':{'fen':f,'moves':moves,'puzzle_id':'authored-'+id,'answer':' '.join(moves[1::2])}})
add('reference-short',['e2e4','e7e5'],'e7e5')
add('reference-long',['e2e4','e7e5','g1f3','b8c6'],'e7e5 b8c6')
add('trailing-ignored',['e2e4','e7e5'],'e7e5 a1a8 nonsense')
add('wrong-legal',['e2e4','e7e5'],'d7d5')
add('missing-solver',['e2e4','e7e5'],'')
add('missing-later',['e2e4','e7e5','g1f3','b8c6'],'e7e5')
add('malformed-solver',['e2e4','e7e5'],'not-uci')
add('illegal-reference-setup',['e2e5','e7e5'],'e7e5')
add('illegal-reference-solver',['e2e4','e7e4'],'e7e4')
add('setup-only',['e2e4'],'')
add('empty-reference',[],'')
add('invalid-fen',['e2e4','e7e5'],'e7e5','not-fen')
matefen='6k1/8/5KQ1/8/8/8/8/8 b - - 0 1'
add('reference-mate',['g8h8','g6g7'],'g6g7',matefen)
add('alternate-mate',['h7h8','g6g7'],'g6h6','8/5K1k/6Q1/8/8/8/8/8 b - - 0 1')
add('immediate-mate-extra-reference',['g8h8','g6g7','h8g8','g7g8'],'g6g7',matefen)
save('inputs.json',{'scope':'Authored controls only; zero released task rows, no accuracy estimate.','livecodebench':lcb,'chessbench_puzzles':chess})
for case in lcb:
 folder=P/'inputs/livecodebench'/case['id'];folder.mkdir(parents=True,exist_ok=True)
 (folder/'tests.json').write_text(json.dumps(case['tests'],sort_keys=True)+'\n')
 (folder/'solution.py').write_text(case['solution'])
print(json.dumps({'archives':identities['archives'],'input_counts':{'livecodebench':len(lcb),'chessbench_puzzles':len(chess)}}))
