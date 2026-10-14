"""Read-only observer: preserve transient verifier files; never change the task."""
import datetime, hashlib, json, pathlib, shutil, subprocess, time
root = pathlib.Path('/tmp/hg-tbrun3')
run_id = 'w-tbrun3-terminal-bench-20261014T194115Z-7eab177b'
evidence = root/'runs'/(run_id+'-launch-evidence')
observations = []
while not (evidence/'launch-observation.json').exists():
    p = subprocess.run(['docker','ps','-aq','--filter',f'label=harnessgrad.run={run_id}'],capture_output=True,text=True,timeout=20)
    if p.returncode == 0 and p.stdout.strip():
        ids=p.stdout.split()
        q=subprocess.run(['docker','inspect',*ids],capture_output=True,text=True,timeout=20)
        if q.returncode==0:
            for c in json.loads(q.stdout):
                if not c['Name'].startswith('/hg-verify-'):
                    continue
                for m in c['Mounts']:
                    if m['Destination'] != '/logs/verifier':
                        continue
                    src=pathlib.Path(m['Source'])
                    for name in ('reward.txt','ctrf.json'):
                        f=src/name
                        if f.is_file():
                            data=f.read_bytes()
                            digest=hashlib.sha256(data).hexdigest()
                            dst=evidence/f'verifier-{name}-{digest}'
                            if not dst.exists():
                                dst.write_bytes(data)
                                observations.append(dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),container_id=c['Id'],source=str(f),copy=str(dst),sha256=digest,bytes=len(data)))
                                (evidence/'verifier-file-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
    time.sleep(0.25)
(evidence/'verifier-observer-completion.json').write_text(json.dumps(dict(file_observations=len(observations),completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
