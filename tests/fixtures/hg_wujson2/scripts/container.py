"""Launch one fresh constrained, network-denied container and retain lifecycle logs."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

packet = Path(__file__).resolve().parents[1]
repo = packet.parents[2]
mode = sys.argv[1]
assert mode in ('build', 'comparison', 'published-runtime', 'rebuilt-runtime')
receipts = packet / mode
receipts.mkdir()
name = 'hg-wujson2-' + mode + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
recorder = str(packet / 'scripts/record.py')

def record(label, argv, check=True):
    p = subprocess.run([sys.executable, recorder, mode + '-' + label, *argv])
    if check:
        p.check_returncode()
    return p.returncode

image = 'python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b'
script = 'runtime.sh' if mode.endswith('-runtime') else mode + '.sh'
argv = ['docker', 'create', '--name', name, '--pull=never', '--platform=linux/amd64',
        '--network=none', '--read-only', '--user', f'{os.getuid()}:{os.getgid()}',
        '--cpus=2', '--memory=1g', '--memory-swap=1g', '--pids-limit=128',
        '--cap-drop=ALL', '--security-opt=no-new-privileges',
        '--tmpfs=/tmp:rw,exec,nosuid,nodev,size=512m',
        '--mount', f'type=bind,src={packet},dst=/packet,readonly',
        '--mount', f'type=bind,src={packet.parent / "hg_wujson/deployment-v6"},dst=/opt/hg-wujson,readonly',
        '--mount', f'type=bind,src={receipts},dst=/receipts',
        '--entrypoint=/bin/sh', image, '/packet/scripts/' + script, mode]
record('create', argv)
try:
    record('inspect-before', ['docker', 'inspect', name])
    rc = record('start', ['docker', 'start', '--attach', name], check=False)
    record('inspect-after', ['docker', 'inspect', name])
    inspect = json.loads((packet / 'commands' / (mode + '-inspect-after.stdout.txt')).read_text())[0]
    assert rc == 0 and inspect['State']['ExitCode'] == 0, inspect['State']
finally:
    record('remove', ['docker', 'rm', '-f', name])
    record('cleanup', ['docker', 'container', 'ls', '--all', '--no-trunc', '--filter', 'name=^/' + name + '$', '--format', '{{json .}}'])
