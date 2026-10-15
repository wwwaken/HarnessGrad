#!/usr/bin/env python3
import json,pathlib,re,hashlib,subprocess,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];repo=ROOT.parents[2]
surface=repo/'tests/fixtures/hg_wimg/capture/terminal-bench-source-surface.json'
src=json.loads(surface.read_text()); rows=[];checks=[]
for task in src:
 for f in task['files']:
  p=pathlib.Path(f['path'])
  if not p.is_file():checks.append({'path':str(p),'present':False});continue
  b=p.read_bytes();h=hashlib.sha256(b).hexdigest();checks.append({'path':str(p),'present':True,'sha256':h,'recorded_sha256':f['sha256'],'matches_recorded':h==f['sha256']})
  if p.name in ('test.sh','Dockerfile'):
   dest=ROOT/'source/tasks'/task['task']/p.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
  lines=b.decode().splitlines();i=0
  while i<len(lines):
   start=i;block=[lines[i]]
   while block[-1].rstrip().endswith('\\') and i+1<len(lines):i+=1;block.append(lines[i])
   s='\n'.join(block)
   if not s.lstrip().startswith('#') and re.search(r'\b(uvx|uv|pip3?|apt-get|apt)\b',s) and (p.name in ('test.sh','Dockerfile') or re.search(r'\b(pip|uv|apt)',s)):
    rows.append({'task':task['task'],'path':str(p),'line':start+1,'end_line':i+1,'text':s,'phase':'verifier-bootstrap' if p.name=='test.sh' else 'image-build' if p.name=='Dockerfile' else 'other-source'})
   i+=1
for row in rows:
 if row['phase']=='other-source':
  source=pathlib.Path(row['path']); rel=source.relative_to('/mnt/20t/xubuqiang/datasets/terminal-bench'); dest=ROOT/'source/other-tests'/rel;dest=dest.with_name(dest.name+'.txt') if source.suffix=='.py' else dest;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
(ROOT/'source/inventory.json').write_text(json.dumps(rows,indent=2)+'\n');(ROOT/'source/source-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
text=['# Local Terminal-Bench bootstrap lines','', 'Verbatim external file:line commands; continuation lines retained. Image-build and other-source matches are separate from verifier bootstrap. All 89 test.sh and Dockerfile preimages are copied beside this index.','']
for r in rows:text.extend([f"## {r['task']} — {r['phase']}",f"{r['path']}:{r['line']}",'```sh',r['text'],'```',''])
(ROOT/'source/bootstrap-lines.md').write_text('\n'.join(text))
root=pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')
verifier=[a for a in rows if a['phase']=='verifier-bootstrap']
summary={'surface_path':str(surface.relative_to(repo)),'surface_sha256':hashlib.sha256(surface.read_bytes()).hexdigest(),'checkout':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'tasks_in_recorded_surface':len(src),'tasks_locally_present':len([p for p in root.iterdir() if (p/'task.toml').is_file()]),'files_checked':len(checks),'all_present':all(c['present'] for c in checks),'all_match':all(c.get('matches_recorded') for c in checks),'invocation_blocks':len(rows),'verifier_invocation_blocks':len(verifier),'uvx_tasks':len(set(a['task'] for a in verifier if a['text'].lstrip().startswith('uvx'))),'uv_tasks':len(set(a['task'] for a in verifier if a['text'].lstrip().startswith('uv '))),'pip_tasks':len(set(a['task'] for a in verifier if a['text'].lstrip().startswith('pip ')))}
(ROOT/'source/summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
