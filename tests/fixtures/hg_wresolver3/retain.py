"""Retain new wheel candidates and a source/build evidence chain, without builds."""
import json
from pathlib import Path
import shutil

from common import HERE, ROOT, digest, save, run

assert not (HERE / 'retained-targets.json').exists()
inputs = json.loads((HERE / 'inputs.json').read_text())
prior = json.loads((ROOT / 'tests/fixtures/hg_wresolver2/inputs.json').read_text())
old_keys = {a['key'] for a in prior['artifacts']}
retained = []
for record in inputs['artifacts']:
    if record['key'] in old_keys:
        continue
    source = Path(record['path'])
    assert digest(source) == record['sha256']
    dest = HERE / 'payloads' / source.name
    dest.parent.mkdir(exist_ok=True)
    shutil.copyfile(source, dest)
    retained.append({'key': record['key'], 'path': str(dest.relative_to(ROOT)),
                     'bytes': dest.stat().st_size, 'sha256': digest(dest)})
save(HERE / 'retained-targets.json', retained)
run('retained-target-sha256sum', ['sha256sum', *[ROOT / a['path'] for a in retained]])

# The absent public wheel was already built in w-wheelhouse. Retain its exact
# original raw build output, the sdist and a newly recomputed source digest.
files = []
for name in ['retry-build-fast-downward-textworld.stdout.txt',
             'retry-build-fast-downward-textworld.stderr.txt',
             'retry-build-fast-downward-textworld.receipt.json']:
    source = ROOT / 'tests/fixtures/hg_wwheelhouse/offline' / name
    dest = HERE / 'acquisition-chain' / name
    dest.parent.mkdir(exist_ok=True)
    shutil.copyfile(source, dest)
    files.append({'origin': str(source.relative_to(ROOT)), 'path': str(dest.relative_to(ROOT)),
                  'sha256': digest(dest)})
source = Path('/tmp/hg-wwheelhouse-payloads-e5uywviu/fast_downward_textworld-20.6.4.tar.gz')
dest = HERE / 'acquisition-chain' / source.name
shutil.copyfile(source, dest)
index = json.loads((HERE / 'index/fast-downward-textworld-20.6.4.json').read_text())
offered = next(a for a in index['urls'] if a['filename'] == source.name)
assert digest(dest) == offered['digests']['sha256']
files.append({'origin': str(source), 'path': str(dest.relative_to(ROOT)), 'sha256': digest(dest),
              'url': offered['url'], 'advertised_sha256': offered['digests']['sha256']})
save(HERE / 'acquisition-chain.json', files)
run('chain-sha256sum', ['sha256sum', *[ROOT / a['path'] for a in files]])
print(json.dumps({'retained_new_wheels': len(retained), 'retained_new_wheel_bytes': sum(a['bytes'] for a in retained),
                  'retained_build_chain_files': len(files)}, sort_keys=True))
