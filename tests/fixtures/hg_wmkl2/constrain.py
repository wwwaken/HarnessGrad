"""Preserve previous import pins while obtaining the added upstream dependencies."""
import json
from pathlib import Path
import sys
from common import HERE, run

old = HERE.parent / 'hg_wmkl'
lines = (old / 'ds1000.lock').read_text().splitlines()
constraint = HERE / 'existing-pins.constraints.txt'
constraint.write_text(''.join(line.split(' --hash=')[0] + '\n' for line in lines if not line.startswith('scipy==')))
config = json.loads((HERE / 'acquisition.json').read_text())
old_records = json.loads((old / 'reused-artifacts.json').read_text())
command = [sys.executable, '-m', 'pip', 'download', '--index-url', 'https://pypi.org/simple',
           '--only-binary=:all:', '--no-cache-dir', '--timeout', '45', '--retries', '1',
           '--dest', config['payload_directory'], '--constraint', str(constraint),
           old_records['gensim']['path'], 'scipy==1.12.0', 'numpy==1.26.4',
           'tensorflow-cpu==2.16.1', 'xgboost==2.0.3']
assert run('acquire/constrained-download', command, timeout=600)['exit_code'] == 0
