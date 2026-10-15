"""Read-only local prerequisites, with byte-preserved command output. No pulls."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'reports/w-e6-evidence/preflight'
OUT.mkdir(exist_ok=False)

def command(label, argv):
    info = {'argv': argv, 'cwd': str(ROOT), 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'timeout_s': 30}
    try:
        p = subprocess.run(argv, capture_output=True, timeout=30)
        info['returncode'] = p.returncode
        (OUT / (label + '.stdout.txt')).write_bytes(p.stdout)
        (OUT / (label + '.stderr.txt')).write_bytes(p.stderr)
    except Exception as exc:
        info['exception'] = repr(exc)
    (OUT / (label + '.json')).write_text(json.dumps(info, indent=2) + '\n')
    return info

command('git-head', ['git', 'rev-parse', 'HEAD'])
command('docker-version', ['docker', 'version', '--format', '{{json .}}'])
command('containers-before', ['docker', 'ps', '-a', '--no-trunc', '--format', '{{.ID}} {{.Names}} {{.Status}}'])
bindings = {}
for name, variables in {'appworld': ['IMAGE', 'SERVICE_IMAGE', 'VERIFIER_IMAGE'], 'gaia': ['IMAGE'], 'tau_bench': ['IMAGE']}.items():
    path = ROOT / 'data/datasets' / (name + '.py')
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in variables:
                    envkey, default = [ast.literal_eval(x) for x in node.value.args]
                    image = os.environ.get(envkey, default)
                    label = name + '-' + target.id.lower()
                    bindings[label] = {'image': image, 'source': str(path.relative_to(ROOT)), 'line': node.lineno, 'environment_override': envkey in os.environ}
                    command(label, ['docker', 'image', 'inspect', image])
command('busybox-file', ['file', shutil.which('busybox') or '/missing-host-busybox'])
command('bubblewrap-version', ['bwrap', '--version'])
(OUT / 'bindings.json').write_text(json.dumps(bindings, indent=2) + '\n')
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT / 'eval/verification/verifier.py', ROOT / 'eval/service/services.py', ROOT / 'eval/containers/container.py', ROOT / 'eval/containers/sandbox.py', *[ROOT / 'data/datasets' / (n + '.py') for n in ['appworld', 'gaia', 'tau_bench']]]}
(OUT / 'source-hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
print(json.dumps({'out': str(OUT), 'bindings': bindings}, indent=2))
