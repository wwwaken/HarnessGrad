"""Authored lifecycle predicate. No benchmark imports, sockets or model calls."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--out', default='/verifier')
p.add_argument('--mode', choices=['normal', 'timeout'], required=True)
p.add_argument('--record')
p.add_argument('--state')
a = p.parse_args()
out = Path(a.out)
out.mkdir(exist_ok=True, parents=True)

def read(path):
    try:
        return Path(path).read_text()
    except OSError as exc:
        return {'error': str(exc)}

scratch = Path('/tmp') / ('hg-we6-probe-' + str(os.getpid()))
scratch.mkdir()
(scratch / 'marker').write_text('authored lifecycle scratch\n')
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)' if a.mode == 'timeout' else 'import time; time.sleep(1)'])
observation = {'pid': os.getpid(), 'ppid': os.getppid(), 'child_pid': child.pid,
               'mode': a.mode, 'scratch': str(scratch), 'scratch_exists': scratch.exists(),
               'limits': read('/proc/self/limits'), 'cgroup': read('/proc/self/cgroup'),
               'mountinfo': read('/proc/self/mountinfo'),
               'network_namespace': os.readlink('/proc/self/ns/net'),
               'route': read('/proc/net/route')}
if a.record:
    record = Path(a.record)
    observation['recording'] = {'path': str(record), 'exists': record.exists(),
                               'entries': sorted(str(x.relative_to(record)) for x in record.rglob('*'))}
if a.state:
    observation['state'] = {'path': a.state, 'content': read(a.state)}
(out / 'observation-before.json').write_text(json.dumps(observation, indent=2) + '\n')
if a.mode == 'timeout':
    time.sleep(60)
else:
    child.wait()
    observation['child_returncode'] = child.returncode
    observation['child_proc_exists_after_wait'] = Path('/proc', str(child.pid)).exists()
    time.sleep(2)  # observation window, within the unchanged platform limits
    (out / 'observation-after.json').write_text(json.dumps(observation, indent=2) + '\n')
    (out / 'reward.txt').write_text('1\n')
    (out / 'evidence.json').write_text(json.dumps({'measured': True, 'metric': 'authored-lifecycle-predicate', 'benchmark': False}) + '\n')
    print('authored lifecycle predicate completed', flush=True)
