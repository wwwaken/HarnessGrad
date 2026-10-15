"""Preserve bounded artifacts and clean only the interrupted owned run; never resume."""
import datetime,json,pathlib,subprocess
packet=pathlib.Path(__file__).resolve().parent;root=pathlib.Path(json.loads((packet/'batch.json').read_text())['runs_root'])
ev=next(d for d in root.glob('*-evidence') if json.loads((d/'identity.json').read_text())['task_id']=='sqlite-db-truncate');ident=json.loads((ev/'identity.json').read_text());run_id=ident['run_id'];audit=ev/'interruption-cleanup';audit.mkdir(exist_ok=False)
def cap(n,args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=60)
 with (audit/(n+'.json')).open('x') as f:json.dump(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),f,indent=2);f.write('\n')
 return r
pid=json.loads((ev/'driver-process.json').read_text())['pid'];assert not pathlib.Path('/proc',str(pid)).exists()
r=cap('owned-containers',['docker','ps','-aq','--filter','label=harnessgrad.run='+run_id]);assert r.returncode==0
containers=r.stdout.split();assert containers
for i,cid in enumerate(containers):
 q=cap('inspect-before-'+str(i),['docker','inspect','--size',cid]);c=json.loads(q.stdout)[0];assert c['Config']['Labels']['harnessgrad.run']==run_id
 cap('top-before-'+str(i),['docker','top',cid])
 for name in ('trace.jsonl','answer.txt','recover.json'):cap('artifact-'+str(i)+'-'+name,['docker','cp',cid+':/app/'+name,str(audit/name)])
 cap('owned-remove-'+str(i),['docker','rm','-f',cid]);cap('owned-container-after-'+str(i),['docker','inspect',cid])
r=cap('owned-networks',['docker','network','ls','-q','--filter','label=harnessgrad.run='+run_id]);assert r.returncode==0
for i,nid in enumerate(r.stdout.split()):
 q=cap('network-inspect-'+str(i),['docker','network','inspect',nid]);n=json.loads(q.stdout)[0];assert n['Labels']['harnessgrad.run']==run_id
 cap('owned-network-remove-'+str(i),['docker','network','rm',nid]);cap('owned-network-after-'+str(i),['docker','network','inspect',nid])
# Same scoped/exact raw observation format as ordinary teardown.
for label,args in [('containers',['docker','ps','-a']),('networks',['docker','network','ls']),('volumes',['docker','volume','ls'])]:
 r=subprocess.run(args+['--filter','label=harnessgrad.run='+run_id,'--format','{{json .}}'],capture_output=True,text=True)
 (ev/(label+'-after.json')).write_text(json.dumps(dict(argv=args+['--filter','label=harnessgrad.run='+run_id,'--format','{{json .}}'],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n');assert r.returncode==0 and not r.stdout.strip()
args=['docker','image','ls','--filter','reference=hg-snapshot:*'+run_id+'*','--no-trunc','--format','{{json .}}'];r=subprocess.run(args,capture_output=True,text=True);(ev/'snapshots-after.json').write_text(json.dumps(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n');assert r.returncode==0 and not r.stdout.strip()
summary=dict(task_id=ident['task_id'],run_id=run_id,driver_pid=pid,driver_observed_absent=True,native_execution_present=(pathlib.Path(ident['run_dir'])/'diagnostic_execution.json').exists(),native_final_receipt_present=(pathlib.Path(ident['run_dir'])/'diagnostic_receipt.json').exists(),reason='launcher exited 143; driver absent; no final native execution/receipt; no CTRF; task was not resumed',cleanup_kind='explicit cleanup of exactly labeled owned orphan; raw scoped/exact observations retained',artifact_dir=str(audit),observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(packet/'interrupted-run-disposition.json').write_text(json.dumps(summary,indent=2)+'\n');(ev/'interrupted-disposition.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
