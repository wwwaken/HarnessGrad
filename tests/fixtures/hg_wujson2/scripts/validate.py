"""Retain exact focused validation commands and original command output."""
import json
from pathlib import Path
import shlex
import subprocess
import sys

packet = Path(__file__).resolve().parents[1]
repo = packet.parents[2]
output = repo / 'reports/w-ujson2-validation.txt'
checks = [
    ['python3', 'tools/check_dataset_blockers.py'],
    ['python3', '-m', 'pytest', '-q', 'tests/quality/test_dataset_blockers.py',
     'tests/quality/test_w_ujson_receipts.py', '--basetemp=/tmp/harnessgrad-pytest-w-ujson2'],
    ['sha256sum', '--check', '--quiet', 'tests/fixtures/hg_wujson2/SHA256SUMS'],
    ['git', 'diff', '--check'],
    ['git', 'diff', '--exit-code', 'HEAD', '--', 'runs/', 'tests/fixtures/hg_wujson/',
     'tests/fixtures/ujson_pypi_codex226/', 'reports/w-ujson-receipts.md', 'eval/'],
    ['python3', '-c', '''import json,subprocess
from pathlib import Path
p='docs/dataset-blockers.json'
a=json.loads(subprocess.check_output(['git','show','HEAD:'+p]))
b=json.loads(Path(p).read_text())
for obj in (a,b):
 d=next(d for d in obj['datasets'] if d['dataset']=='twowikimultihopqa')
 x=next(x for x in d['blockers'] if x['id']=='ujson-native-offline-closure')
 assert x['status']=='external'
 x.pop('observed');x.pop('evidence')
assert a==b
print('Only target observed/evidence changed; statuses, next actions, gates and other registry entries unchanged.')'''],
]
with output.open('wb') as out:
    out.write(b'w-ujson2 focused validation (raw stdout/stderr follow each exact command)\n')
    out.flush()
    for argv in checks:
        command = '$ ' + shlex.join(argv) + '\n'
        out.write(command.encode()); out.flush()
        p = subprocess.run(argv, cwd=repo, stdout=out, stderr=out)
        out.write(f'[exit={p.returncode}]\n\n'.encode()); out.flush()
        print(shlex.join(argv[:4]), f'exit={p.returncode}', flush=True)
        if p.returncode:
            raise SystemExit(p.returncode)
    out.write(b'All focused checks passed. No benchmark/model/GPU/endpoint execution.\n')
