"""Authored lifecycle probe, no dataset input, network call or model."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('mode')
p.add_argument('--out', default='/verifier')
p.add_argument('--recording', action='store_true')
a = p.parse_args()
out = Path(a.out)
out.mkdir(exist_ok=True)
if a.recording:
    assert Path('/recordings/recording').is_dir()
child = None
if a.mode != 'single-timeout':
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
facts = {'pid': os.getpid(), 'child': child.pid if child else None,
         'recording_visible': Path('/recordings/recording').is_dir(),
         'limits': Path('/proc/self/limits').read_text(),
         'cgroup': Path('/proc/self/cgroup').read_text(), 'mode': a.mode}
(out / 'started.json').write_text(json.dumps(facts) + '\n')
print(json.dumps(facts), flush=True)
if a.mode in ('timeout', 'single-timeout'):
    time.sleep(20)
else:
    time.sleep(1)
    child.terminate()
    facts['child_returncode'] = child.wait(timeout=3)
    facts['child_proc_absent_after_wait'] = not Path('/proc', str(child.pid)).exists()
    (out / 'waited.json').write_text(json.dumps(facts) + '\n')
    print(json.dumps(facts), flush=True)
    if a.mode == 'missing-reward':
        raise RuntimeError('authored error after child wait, before reward')
    (out / 'reward.txt').write_text('not-a-number' if a.mode == 'malformed-reward' else '1')
    # Deliberately no evidence.json: exercise the declared-evidence absence exit.
