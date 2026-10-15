"""Independent official generic evaluator vs unchanged local replay on authored task."""
import contextlib,hashlib,importlib.util,io,json,os,pathlib,resource,shutil,socket,sys,tarfile,tempfile,traceback
F=pathlib.Path('/fixture');mode=sys.argv[1]
resource.setrlimit(resource.RLIMIT_CPU,(120,120));resource.setrlimit(resource.RLIMIT_NOFILE,(256,256))
interfaces=pathlib.Path('/proc/net/dev').read_text();routes=pathlib.Path('/proc/net/route').read_text()
assert [x.split(':')[0].strip() for x in interfaces.splitlines() if ':' in x]==['lo']
assert len(routes.splitlines())==1
probe={}
sock=socket.socket();sock.settimeout(0.3)
try: sock.connect(('198.51.100.1',9));raise RuntimeError('external connect unexpectedly succeeded')
except OSError as exc: probe={'type':type(exc).__name__,'errno':exc.errno,'message':str(exc)}
finally: sock.close()
# Supplemental Python read denial: container data paths with released tasks are hidden by tmpfs.
blocked=[]
def audit(event,args):
 if event in {'open','os.scandir','os.listdir'} and args and isinstance(args[0],(str,bytes,os.PathLike)):
  path=os.fsdecode(args[0])
  if path.startswith('/appworld/data/tasks/'):
   blocked.append(path);raise PermissionError('released task reads excluded')
sys.addaudithook(audit)
inputs=json.loads((F/'appworld-inputs.json').read_text());out=[]
for case in inputs['cases']:
 if case['id'] != sys.argv[2]: continue
 result={'id':case['id'],'calls':case['calls']};stdout=io.StringIO();stderr=io.StringIO()
 scratch=pathlib.Path(tempfile.mkdtemp(prefix='hg-woffscorer3-appworld-'))
 try:
  with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
   with tarfile.open(F/'appworld-controlled-inputs.tar.gz') as tf:tf.extractall(scratch,filter='data')
   os.environ['APPWORLD_ROOT']=str(scratch);os.environ['APPWORLD_CACHE']=str(scratch/'cache')
   if mode=='official':
    from appworld import AppWorld
    import appworld.evaluator
    with AppWorld(task_id=inputs['task_id'],experiment_name='official-control',raise_on_failure=False,ground_truth_mode='minimal') as world:
     responses=[]
     for call in case['calls']:
      # Direct authentic Requester call, outside local execute-string replay.
      responses.append(getattr(world.requester,call['method'])(call['url'],data=call['data'],client=world.requester.client))
     tracker=appworld.evaluator.evaluate_task(inputs['task_id'],experiment_name='official-control')
     result.update(measured=True,reward=float(bool(tracker.success)),tracker=tracker.to_dict(),responses=responses)
    result['world_closed']=True
   elif mode=='local':
    spec=importlib.util.spec_from_file_location('unchanged_appworld_check',F/'appworld-local-check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    log=scratch/'calls.jsonl';log.write_text(''.join(json.dumps(c)+'\n' for c in case['calls']))
    reward=scratch/'reward.txt';evidence=scratch/'evidence.json'
    sys.argv=[str(F/'appworld-local-check.py'),'--task-id',inputs['task_id'],'--source-split','train','--log',str(log),'--reward-file',str(reward),'--evidence-file',str(evidence)]
    try:code=m.main()
    except SystemExit as exc:code=exc.code
    result.update(exit_code=code,evidence=json.loads(evidence.read_text()),argv=sys.argv)
    result['measured']=result['evidence'].get('measured',False)
    if reward.is_file():result['reward']=float(reward.read_text())
   else:raise ValueError(mode)
 except Exception as exc: result.update(measured=False,error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
 finally:
  result['stdout']=stdout.getvalue();result['stderr']=stderr.getvalue();shutil.rmtree(scratch);result['scratch_removed']=not scratch.exists();out.append(result)
print(json.dumps({'mode':mode,'network':{'interfaces':interfaces,'routes':routes,'external_probe':probe,'namespace':os.readlink('/proc/self/ns/net')},'inputs_sha256':hashlib.sha256((F/'appworld-inputs.json').read_bytes()).hexdigest(),'archive_sha256':hashlib.sha256((F/'appworld-controlled-inputs.tar.gz').read_bytes()).hexdigest(),'local_check_sha256':hashlib.sha256((F/'appworld-local-check.py').read_bytes()).hexdigest(),'blocked_released_task_reads':blocked,'results':out},indent=2,default=str))
