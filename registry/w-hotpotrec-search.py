#!/usr/bin/env python3
"""Read-only HotpotQA historical evidence search; all outputs use the assigned scratch.
Run from the w-hotpotrec worktree. No model, adapter execution, Git mutation or network.
Required order: inventory, filesystem/transcripts/git/gitstores, blobs, executions/recover.
File inventories and raw outputs stay outside Git because several exceed 1 MB.
"""
import collections, glob, hashlib, json, os, pathlib, re, subprocess, sys
S = pathlib.Path('/mnt/20t/xubuqiang/hg-work/hotpotrec/evidence')
S.mkdir(exist_ok=True)
ROOT = '/mnt/20t/xubuqiang/Study/'
roots = [ROOT+'HarnessGrad/'+n for n in ['runs','runs_discarded_20260929-004559','.harnessgrad-state']]
roots += [ROOT+'HarnessGrad-evidence-archive',*sorted(glob.glob(ROOT+'hg-backup-20261014*')),ROOT+'hg-logs','/mnt/20t/xubuqiang/harnessgrad_work',ROOT+'harnessgrad_work',ROOT+'harnessgrad_cli',*sorted(glob.glob(ROOT+'HarnessGrad-real-work-20261117*')),ROOT+'HarnessGrad-appworld-controls-20261117',ROOT+'HarnessGrad-gaia-controls-20261117','/mnt/20t/xubuqiang/hg-census']
DENIED = {'api_bank','api-bank','nestful','sotuqa','tau2_bench','tau2-bench'}
def run(name,args,stdin=None):
    p=subprocess.run(args,input=stdin,capture_output=True)
    (S/(name+'.stdout')).write_bytes(p.stdout)
    (S/(name+'.stderr')).write_bytes(p.stderr)
    print(json.dumps({'name':name,'command':args,'exit':p.returncode,'stdout_bytes':len(p.stdout),'stdout_lines':p.stdout.count(b'\n'),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode(errors='replace')},sort_keys=True),flush=True)
    return p
mode=sys.argv[1]
if mode not in {'inventory','filesystem','transcripts','git','gitstores','blobs','executions','recover'}:
    raise SystemExit('usage: w-hotpotrec-search.py inventory|filesystem|transcripts|git|gitstores|blobs|executions|recover')
if mode=='inventory':
    allfiles=[]
    for root in roots:
        files=[];errors=[];excluded=[]
        for base,dirs,names in os.walk(root,followlinks=False,onerror=lambda e:errors.append(str(e))):
            for d in list(dirs):
                if d=='.git' or d in DENIED or (root.endswith('20261014') or root.endswith('pre-rewrite')) and d=='dot-git':
                    dirs.remove(d);excluded.append(os.path.join(base,d))
            for n in names:
                p=os.path.join(base,n)
                if any(x in DENIED for x in pathlib.Path(p).parts):continue
                if os.path.islink(p):excluded.append(p+' [symlink]');continue
                try:files.append((p,os.path.getsize(p)))
                except OSError as e: errors.append(str(e))
        allfiles.extend(p for p,n in files)
        print(json.dumps({'root':root,'files':len(files),'bytes':sum(n for p,n in files),'excluded':excluded,'errors':errors,'largest':sorted(files,key=lambda x:x[1],reverse=True)[:3]},sort_keys=True),flush=True)
    (S/'filesystem-files.json').write_text(json.dumps(sorted(allfiles),indent=2)+'\n')
    transcripts=sorted(glob.glob(os.path.expanduser('~/.codex/sessions/**/*.jsonl'),recursive=True))+[os.path.expanduser('~/.codex/history.jsonl'),os.path.expanduser('~/.bash_history')]
    (S/'transcript-files.json').write_text(json.dumps(transcripts,indent=2)+'\n')
    print(json.dumps({'transcript_files':len(transcripts),'transcript_bytes':sum(os.path.getsize(p) for p in transcripts)},sort_keys=True))
elif mode in ['filesystem','transcripts']:
    files=json.loads((S/('filesystem-files.json' if mode=='filesystem' else 'transcript-files.json')).read_text())
    out=bytearray();errors=bytearray();statuses=collections.Counter()
    for offset in range(0,len(files),300):
        p=subprocess.run(['rg','-l','-i','--null',r'hotpot(?:qa)?|1,?476|1,?382','--',*files[offset:offset+300]],capture_output=True)
        out.extend(p.stdout);errors.extend(p.stderr);statuses[p.returncode]+=1
    (S/(mode+'-matches.stdout')).write_bytes(out)
    (S/(mode+'-matches.stderr')).write_bytes(errors)
    print(json.dumps({'rg_chunk_exit_counts':statuses,'stderr':errors.decode(errors='replace'),'pattern':r'hotpot(?:qa)?|1,?476|1,?382'},sort_keys=True))
    matched=(S/(mode+'-matches.stdout')).read_bytes().decode().strip('\0').split('\0')
    print(json.dumps({'matched_files':matched},sort_keys=True))
elif mode=='git':
    run('branches',['git','for-each-ref','--format=%(refname:short) %(objectname)','refs/heads'])
    run('log-all',['git','log','--all','--format=%H %s'])
    for token in ['hotpot','hotpotqa','492','1476','1382','94/','v4']:
        run('pickaxe-'+token.replace('/','_'),['git','log','--all','--format=%H %s','--pickaxe-all','-S'+token,'--',':(exclude)data/datasets/api_bank/**',':(exclude)data/datasets/nestful/**',':(exclude)data/datasets/sotuqa/**',':(exclude)data/datasets/tau2_bench/**'])
    run('stash',['git','stash','list'])
    run('reflog',['git','reflog','--all','--format=%H %gs'])
    run('objects',['git','cat-file','--batch-all-objects','--batch-check'])
    run('reachable',['git','rev-list','--objects','--all'])
elif mode=='gitstores':
    for i,d in enumerate([ROOT+'hg-backup-20261014/dot-git',ROOT+'hg-backup-20261014-pre-rewrite/dot-git',ROOT+'HarnessGrad-appworld-controls-20261117/.git',ROOT+'HarnessGrad-gaia-controls-20261117/.git']):
        prefix=['git','--git-dir='+d]
        run('store'+str(i)+'-refs',prefix+['for-each-ref','--format=%(refname) %(objectname)'])
        run('store'+str(i)+'-log',prefix+['log','--all','--format=%H %s'])
        run('store'+str(i)+'-paths',prefix+['rev-list','--objects','--all'])
        run('store'+str(i)+'-objects',prefix+['cat-file','--batch-all-objects','--batch-check'])

elif mode=='blobs':
    import collections,hashlib,json,pathlib,re,subprocess
    S=pathlib.Path('/mnt/20t/xubuqiang/hg-work/hotpotrec/evidence')
    stores=[('', 'objects.stdout','reachable.stdout'),('/mnt/20t/xubuqiang/Study/hg-backup-20261014/dot-git','store0-objects.stdout','store0-paths.stdout'),('/mnt/20t/xubuqiang/Study/hg-backup-20261014-pre-rewrite/dot-git','store1-objects.stdout','store1-paths.stdout'),('/mnt/20t/xubuqiang/Study/HarnessGrad-appworld-controls-20261117/.git','store2-objects.stdout','store2-paths.stdout'),('/mnt/20t/xubuqiang/Study/HarnessGrad-gaia-controls-20261117/.git','store3-objects.stdout','store3-paths.stdout')]
    seen=set();pat=re.compile(rb'hotpot(?:qa)?',re.I);denied=re.compile(r'(?:^|/)(?:api_bank|api-bank|nestful|sotuqa|tau2_bench|tau2-bench)(?:/|\.)')
    for i,(store,inv,paths) in enumerate(stores):
        if not (S/inv).exists(): print(json.dumps({'store':store,'state':'not-yet-enumerated'}),flush=True);continue
        names={}
        for line in (S/paths).read_text().splitlines():
            fields=line.split(' ',1)
            if len(fields)>1:names[fields[0]]=fields[1]
        blobs=[];skip=[]
        for line in (S/inv).read_text().splitlines():
            sha,typ,size=line.split()
            if typ!='blob' or sha in seen:continue
            if denied.search(names.get(sha,'')):skip.append(sha);continue
            blobs.append((sha,int(size)));seen.add(sha)
        prefix=['git']+(['--git-dir='+store] if store else [])
        proc=subprocess.Popen(prefix+['cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        count=0;total=0;matches=[]
        with (S/('object-hits-'+str(i)+'.jsonl')).open('w') as out:
            for sha,size in blobs:
                proc.stdin.write((sha+'\n').encode());proc.stdin.flush()
                header=proc.stdout.readline().decode().strip();data=proc.stdout.read(size);proc.stdout.read(1)
                if header!=f'{sha} blob {size}' or len(data)!=size:raise RuntimeError(header)
                count+=1;total+=size
                if not pat.search(data):continue
                matches.append(sha)
                for n,line in enumerate(data.splitlines(),1):
                    if not pat.search(line):continue
                    out.write(json.dumps({'store':store or 'worktree-common-git','sha':sha,'path':names.get(sha),'line':n,'text':line.decode(errors='replace')})+'\n')
        proc.stdin.close();proc.wait()
        print(json.dumps({'store':store or 'worktree-common-git','scanned_unique_blobs':count,'bytes':total,'excluded_refused_blobs':len(skip),'matching_blobs':len(matches),'batch_exit':proc.returncode},sort_keys=True),flush=True)

elif mode=='executions':
    import json,pathlib,re,collections
    S=pathlib.Path('/mnt/20t/xubuqiang/hg-work/hotpotrec/evidence')
    files=S.joinpath('transcripts-matches.stdout').read_bytes().decode().strip('\0').split('\0')
    seen=set();count=0
    with (S/'execution-excerpts.jsonl').open('w') as out:
     for p in files:
      if not p.endswith('.jsonl'):continue
      for n,line in enumerate(open(p,errors='replace'),1):
       if 'hotpot' not in line.lower():continue
       try:x=json.loads(line)
       except:continue
       payload=x.get('payload',{})
       if not isinstance(payload,dict):continue
       item=payload.get('item',{})
       if payload.get('type')=='item_completed' and item.get('type')=='CommandExecution':
        command=item.get('command');stdout=item.get('stdout','');key=(json.dumps(command),stdout)
        if key in seen:continue
        seen.add(key)
        if not re.search(r'hotpotqa-h0|qa-h0-incomplete|hotpot.{0,50}(?:492|94|1476)',stdout+'\n'+json.dumps(command),re.I):continue
        out.write(json.dumps({'source':p,'line':n,'timestamp':x.get('timestamp'),'command':command,'exit_code':item.get('exit_code'),'stdout':stdout,'stderr':item.get('stderr')},ensure_ascii=False)+'\n');count+=1
       elif x.get('type')=='response_item' and payload.get('type')=='function_call':
        args=payload.get('arguments','')
        if re.search(r'hotpotqa-h0-10pct-v4|qa-h0-incomplete',args):
         key=args
         if key in seen:continue
         seen.add(key)
         out.write(json.dumps({'source':p,'line':n,'timestamp':x.get('timestamp'),'function':payload.get('name'),'arguments':args},ensure_ascii=False)+'\n');count+=1
    print('unique_execution_or_call_excerpts='+str(count))

elif mode=='recover':
    transcript='/home/xubuqiang/.codex/sessions/2026/10/12/rollout-2026-10-12T13-19-24-01a12e8d-26bd-7c90-ab31-5ab4e04eaaa8.jsonl'
    rows={n:json.loads(line) for n,line in enumerate(open(transcript),1) if n in {85,102,119,129}}
    row=rows[102]['payload']['item']['stdout']
    section=row[row.index('hotpotqa-h0-10pct-v5 aggregate files'):]
    line=next(line for line in section.splitlines() if line.startswith('selected meta '))
    meta=json.loads(line[len('selected meta '):])
    ids=meta['split']['train']
    recovered={'worker':'w-hotpotrec','state':'FOUND','run_id':meta['run_id'],'source_transcript':transcript,'source_line':102,'recovery':'JSON-decoded CommandExecution stdout selected meta; only the train ID list is retained; no original split-file digest is recomputed','binding_limit':'Not evidence for hotpot-v4-incomplete or its 94/1476 report','split_source_observed':meta['split_source'],'framework_version_observed':meta['framework_version'],'jobs_observed':meta['jobs'],'budget_trial_limit_observed':meta['budget']['counters']['trials'],'train_task_ids':ids}
    (S/'recovered-v5-train.json').write_text(json.dumps(recovered,indent=2)+'\n')
    print(json.dumps({'run_id':meta['run_id'],'train_ids':len(ids),'unique_train_ids':len(set(ids)),'first':ids[:3],'last':ids[-3:],'exact_output_path':str(S/'recovered-v5-train.json')},sort_keys=True))
