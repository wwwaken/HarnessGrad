"""Acquire the unchanged upstream compatibility pins; preserve all raw output."""
from pathlib import Path
import tempfile
import sys
from common import HERE, save, run

payloads = Path(tempfile.mkdtemp(prefix='hg-wmkl2-payloads-'))
save(HERE / 'acquisition.json', {'payload_directory': str(payloads), 'base_python': sys.executable})
# Exact upstream pins plus the recorded NumPy, constrain resolver against the import profile.
command = [sys.executable, '-m', 'pip', 'download', '--index-url', 'https://pypi.org/simple',
           '--only-binary=:all:', '--no-cache-dir', '--timeout', '45', '--retries', '1',
           '--dest', str(payloads), 'gensim==4.3.2', 'scipy==1.12.0', 'numpy==1.26.4',
           'tensorflow-cpu==2.16.1', 'xgboost==2.0.3']
# Gensim4.3.2 has no public cp312 wheel: use the earlier actually built and hashed wheel.
manifest = __import__('json').loads((HERE.parent / 'hg_wmkl/reused-artifacts.json').read_text())
command[command.index('gensim==4.3.2')] = manifest['gensim']['path']
r = run('acquire/download', command, timeout=600)
assert r['exit_code'] == 0
