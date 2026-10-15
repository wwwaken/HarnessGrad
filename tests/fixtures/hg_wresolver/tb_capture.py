"""Fresh bounded container; inspect before cleanup; never resume or pull an image."""
import json
import os
import sys
from pathlib import Path
import tempfile

from common import HERE, ROOT, save, run

attempt = sys.argv[1] if len(sys.argv) > 1 else 'tb'
assert attempt.isalnum() and attempt.startswith('tb')
assert not (HERE / (attempt + '-result.json')).exists(), 'Never overwrite a prior capture'
prior = ROOT / 'tests/fixtures/hg_wuvx'
image = json.loads((prior / 'raw/image-inspect.stdout.txt').read_text())[0]['Id']
out = HERE / attempt
out.mkdir()
name_dir = Path(tempfile.mkdtemp(prefix='hg-wresolver-name-'))
name = 'hg-wresolver-' + name_dir.name
name_dir.rmdir()
try:
    inspect = run(HERE / 'raw', attempt + '-image-inspect', ['docker', 'image', 'inspect', image])
    assert inspect['exit_code'] == 0
    result = run(HERE / 'raw', attempt + '-container', ['docker', 'run', '--name', name, '--pull=never',
        '--network=none', '--read-only', '--cpus=1', '--memory=512m', '--pids-limit=64',
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--tmpfs', '/tmp:rw,exec,size=256m', '--cap-drop=ALL', '--security-opt=no-new-privileges',
        '--mount', f'type=bind,src={HERE},dst=/packet/tests/fixtures/hg_wresolver,readonly',
        '--mount', f'type=bind,src={prior / "artifacts"},dst=/prior,readonly',
        '--mount', f'type=bind,src={out},dst=/out', '--entrypoint', '/usr/local/bin/python3.13',
        image, '/packet/tests/fixtures/hg_wresolver/tb_probe.py'], timeout=180)
    run(HERE / 'raw', attempt + '-container-inspect', ['docker', 'inspect', name])
    save(HERE / (attempt + '-result.json'), result)
finally:
    cleanup = run(HERE / 'raw', attempt + '-container-cleanup', ['docker', 'rm', '-f', name])
    assert cleanup['exit_code'] == 0
    run(HERE / 'raw', attempt + '-container-absence', ['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$', '--format', '{{.Names}}'])
assert result['exit_code'] == 0
