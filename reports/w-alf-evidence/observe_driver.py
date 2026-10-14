"""Passive call/audit observer; delegates unchanged driver arguments and return code."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
sys.argv = [str(ROOT / 'driver.py'), *sys.argv[2:]]
events = []
temporary = []
processes = []
lock = threading.Lock()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(event, args):
    if event == 'tempfile.mkdtemp':
        temporary.append(str(args[0]))
    if event == 'shutil.rmtree' and Path(args[0]).name.startswith('hg-task-'):
        path = Path(args[0])
        events.append({'event': event, 'path': str(path), 'exists_before': path.exists(),
                       'files': {str(p.relative_to(path)): sha(p)
                                 for p in sorted(path.rglob('*')) if p.is_file()}})


def profile(frame, event, arg):
    filename, name = frame.f_code.co_filename, frame.f_code.co_name
    if not ((filename.endswith('/subprocess.py') and name in ('run', '__init__'))
            or (filename.endswith('/eval/run/runner.py') and name == 'run_one')
            or (filename.endswith('/eval/verification/verifier.py') and name == '_verify')):
        return profile
    values = frame.f_locals
    if event == 'call' and filename.endswith('/subprocess.py') and name == 'run':
        env = values.get('kwargs', {}).get('env') or {}
        events.append({'event': 'subprocess.run', 'args': values.get('popenargs'),
                       'timeout': values.get('timeout'),
                       'cwd': str(values.get('kwargs', {}).get('cwd')),
                       'deadline_env': env.get('HG_AGENT_DEADLINE_S')})
    if event == 'return' and filename.endswith('/subprocess.py') and name == '__init__':
        obj = values.get('self')
        pid = getattr(obj, 'pid', None)
        if pid:
            p = Path('/proc') / str(pid)
            row = {'pid': pid, 'argv': values.get('args'), 'sampled_at_ns': time.time_ns()}
            for field in ('limits', 'cgroup', 'status'):
                try:
                    row[field] = (p / field).read_text()
                except OSError as exc:
                    row[field] = {'unavailable': str(exc)}
            processes.append(row)
    if event == 'return' and filename.endswith('/eval/run/runner.py') and name == 'run_one':
        with (OUT / 'run-one-result.json').open('x') as f:
            json.dump(arg, f, indent=2)
    if event == 'return' and filename.endswith('/eval/verification/verifier.py') and name == '_verify':
        path = Path(values['workdir'])
        target = OUT / 'selected-task-at-verification'
        shutil.copytree(path, target)
        events.append({'event': 'verifier-return', 'workdir': str(path),
                       'sandbox': values['sandbox'], 'timeout_s': values['timeout_s'],
                       'verifier': values['verifier'], 'verdict': arg})
    return profile


sys.addaudithook(audit)
sys.setprofile(profile)
threading.setprofile(profile)
try:
    runpy.run_path(str(ROOT / 'driver.py'), run_name='__main__')
finally:
    sys.setprofile(None)
    threading.setprofile(None)
    for name, value in (
            ('call-observations.json', events), ('process-observations.json', processes),
            ('temporary-cleanup.json', [dict(path=p, exists_after=Path(p).exists())
                                        for p in temporary])):
        with (OUT / name).open('x') as f:
            json.dump(value, f, indent=2, default=str)
