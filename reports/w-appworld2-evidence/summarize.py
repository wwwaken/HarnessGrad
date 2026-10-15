"""Read completed own run only; preserve copies, compute a bounded evidence index."""
import hashlib
import json
from pathlib import Path
import subprocess
import datetime

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]

def save(name, body):
    (OUT / name).write_text(json.dumps(body, indent=2) + '\n')

def command(argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=40)
    return dict(command=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr,
                observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())

def digest(path):
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

launch = json.loads((OUT / 'launch-input.json').read_text())
run = Path(launch['run_root'])
assert not run.is_relative_to(ROOT)
rows = []
for source in sorted(run.rglob('*')):
    if source.is_file():
        target = OUT / 'execution' / source.relative_to(run)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        rows.append(dict(source=str(source), copy=str(target.relative_to(OUT)),
                         bytes=source.stat().st_size, sha256=digest(source)['sha256']))
save('artifact-copy-provenance.json', rows)
e = json.loads((run / 'diagnostic_execution.json').read_text())
s = json.loads((run / 'diagnostic_receipt.json').read_text())
tid = launch['task_id']
trace_file = OUT / 'execution' / 'progress/round-0/traces' / (tid + '.trial1.jsonl')
trace = [json.loads(l) for l in trace_file.read_text().splitlines() if l.strip()]
log_file = OUT / 'execution' / 'recordings' / tid / 'appworld/experiments/outputs/harness/tasks' / tid / 'logs/api_calls.jsonl'
api_calls = [json.loads(l) for l in log_file.read_text().splitlines() if l.strip()]
observations = [json.loads(l) for l in (OUT/'container-observations.jsonl').read_text().splitlines()]
roles = {}
for o in observations:
    obj = o['inspect']
    cfg = obj['Config']
    image = cfg['Image']
    manifest = json.loads((OUT/'launch-manifest.json').read_text())
    role = next(role for role, ref in manifest['images'].items() if image == ref)
    entry = roles.setdefault(role, dict(container_id=obj['Id'], image=obj['Image'],
        configured_image=image, command=cfg['Cmd'], observations=[]))
    entry['observations'].append(dict(observed_at=o['observed_at'], state=obj['State'],
        resource={k:obj['HostConfig'].get(k) for k in ['NanoCpus','Memory','PidsLimit','ReadonlyRootfs','Tmpfs','NetworkMode']},
        mounts=obj['Mounts'], networks=obj['NetworkSettings']['Networks'], env=cfg['Env']))
save('role-observations.json', roles)
raw = e['verdicts'][tid]
summary = dict(run_id=launch['run_id'], run_root=str(run), work_root=launch['work_root'],
    copied_run_files=len(rows), raw_verdict=raw,
    raw_counts=dict(measured=int(raw.get('evidence',{}).get('measured') is True and not raw.get('unmeasured')),
        invalid=len(e['invalid']), unmeasured=int(raw.get('evidence',{}).get('measured') is not True or bool(raw.get('unmeasured')))),
    staged_counts=s['coverage'], staged_score=s['score'], enforcement=s['enforcement'],
    tokens=e['tokens'], model_gateway=e['model_gateway'], identity_declared=e['identity_declared'],
    api_call_count=len(api_calls), api_routes=[dict(method=c.get('method'),url=c['url']) for c in api_calls],
    actor_commands=len([o for o in trace if 'command' in o]),
    reply_steps=[o['step'] for o in trace if 'reply' in o],
    submissions=[o for o in trace if 'submitted' in o],
    shell_nonzero=[dict(step=o['step'],exit=o['exit']) for o in trace if 'command' in o and o.get('exit')],
    trace_tail=trace[-3:], passes=len(raw['evidence'].get('passes',[])), failures=len(raw['evidence'].get('failures',[])))
save('result-summary.json',summary)
selected_source=Path('/mnt/20t/xubuqiang/datasets/appworld/_src/unpacked/data/tasks')/tid
save('selected-source-hashes.json',[digest(selected_source/p) for p in ['specs.json','ground_truth/evaluation.py']])
save('runtime-unchanged.json',command(['git','diff','--exit-code','HEAD','--','driver.py','base_harness','eval','data','harnessgrad','tools']))
cleanup = dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    processes=[dict(container_id=role['container_id'],pid=ob['state']['Pid'],
                    proc_exists=(Path('/proc')/str(ob['state']['Pid'])).exists())
               for role in roles.values() for ob in role['observations'] if ob['state']['Pid']],
    run_network=command(['docker','network','inspect','hg-'+launch['run_id']+'-'+tid]),
    work_root_retained=Path(launch['work_root']).exists(), run_root_retained=run.exists())
save('cleanup-processes-after.json',cleanup)
print(json.dumps(summary,indent=2))
