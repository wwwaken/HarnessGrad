"""Launch a fresh network-denied synthetic closure; retain every raw receipt."""
import argparse
import datetime
import json
import os

from record import ROOT, record

parser = argparse.ArgumentParser()
parser.add_argument('--image-inspect', required=True)
parser.add_argument('--prefix', required=True)
args = parser.parse_args()
image = json.loads((ROOT / args.image_inspect).read_text())[0]['Id']
prefix = args.prefix
name = 'hg-wujson-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out = ROOT / prefix
out.mkdir()
identity = ROOT / (prefix + '-identity.json')
assert not identity.exists()
identity.write_text(json.dumps({'container_name': name, 'image': image,
                                'receipt_directory': str(out)}, indent=2) + '\n')
record(prefix + '-create', [
    'docker', 'create', '--name', name, '--pull=never', '--platform=linux/amd64',
    '--network=none', '--read-only', '--user', f'{os.getuid()}:{os.getgid()}',
    '--cpus=1', '--memory=512m', '--memory-swap=512m', '--pids-limit=128',
    '--cap-drop=ALL', '--security-opt=no-new-privileges',
    '--tmpfs=/tmp:rw,exec,nosuid,nodev,size=128m', '--mount',
    f'type=bind,src={out},dst=/receipts', '--entrypoint=/bin/sh', image,
    '/opt/hg-wujson/closure.sh'])
record(prefix + '-inspect-before', ['docker', 'inspect', name])
try:
    record(prefix + '-start', ['docker', 'start', '--attach', name], timeout=180, check=False)
finally:
    record(prefix + '-inspect-after', ['docker', 'inspect', name])
    record(prefix + '-build-report-copy', ['docker', 'cp',
           name + ':/opt/hg-wujson/build-install-report.json',
           str(ROOT / (prefix + '-build-install-report.json'))])
    record(prefix + '-remove', ['docker', 'rm', name])
    record(prefix + '-cleanup-check', ['docker', 'ps', '-a', '--filter',
           'name=^/' + name + '$', '--format', '{{json .}}'])
