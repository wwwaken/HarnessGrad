"""Assemble ONLY retained local wheel bytes; refuse a second capture in this packet."""
import email
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

from common import HERE, ROOT, digest, save, run

assert not (HERE / 'inputs.json').exists(), 'Use a new evidence packet for a new capture'
prior = ROOT / 'tests/fixtures/hg_wwheelhouse'
manifest = json.loads((prior / 'manifest.json').read_text())
built = json.loads((prior / 'built-artifacts.json').read_text())
scope = json.loads((prior / 'source-scope.json').read_text())['datasets']
normalize = lambda s: re.sub(r'[-_.]+', '-', s).lower()
available = {normalize(k): r for k, r in manifest['artifacts'].items()
             if r['status'] == 'obtained-wheel'}
available.update({normalize(k): r for k, r in built.items() if r['status'] == 'built-offline'})
profiles = {
    'chessbench_puzzles': ['chess'],
    'scienceworld': ['scienceworld'],
    'jericho': ['jericho'],
    'spreadsheetbench': ['openpyxl'],
    'reasoning_gym': ['reasoning-gym'],
}
work = Path(tempfile.mkdtemp(prefix='hg-wresolver-payloads-'))
wheels = work / 'wheels'
wheels.mkdir()
# The inherited source-led import profiles are the finite candidate corpus. This
# does not claim that their selected-import set is a Requires-Dist closure.
keys = {normalize(k) for name in profiles
        for k in scope[name].get('imported_distributions', [])}
records = []
for key in sorted(keys & available.keys()):
    old = available[key]
    source = Path(old['local_path'])
    actual = digest(source)
    assert actual == old['sha256'], (source, actual, old['sha256'])
    target = wheels / source.name
    shutil.copyfile(source, target)
    assert digest(target) == actual
    # Vendor the two complete small profiles. The failed-profile corpus remains
    # in a separately recorded retained directory, never an invented wheel.
    if key in {'chess', 'scienceworld', 'py4j'}:
        provided = HERE / 'payloads' / source.name
        provided.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, provided)
    else:
        provided = target
    with zipfile.ZipFile(target) as archive:
        members = {}
        for suffix in ['METADATA', 'WHEEL']:
            member = next(n for n in archive.namelist() if n.endswith('.dist-info/' + suffix))
            dest = HERE / 'metadata' / key / suffix
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(archive.read(member))
            members[suffix] = {'member': member, 'path': str(dest.relative_to(ROOT)),
                               'sha256': digest(dest)}
    meta = email.message_from_bytes((HERE / 'metadata' / key / 'METADATA').read_bytes())
    assert normalize(meta['Name']) == key and meta['Version'] == old['version']
    records.append({'key': key, 'name': meta['Name'], 'version': meta['Version'],
                    'source': str(source), 'path': str(target),
                    'provided_path': str(provided), 'sha256': actual,
                    'prior_sha256': old['sha256'], 'bytes': target.stat().st_size,
                    'metadata': members, 'requires_python': meta.get('Requires-Python'),
                    'requires_dist': meta.get_all('Requires-Dist', [])})
by_key = {r['key']: r for r in records}
for name, roots in profiles.items():
    directory = HERE / 'profiles' / name
    directory.mkdir(parents=True)
    (directory / 'roots.in').write_text(''.join(f"{by_key[k]['name']}=={by_key[k]['version']}\n" for k in roots))
    # Freeze every available observed import version; absent dependencies remain
    # absent and are left to the real resolver to report.
    (directory / 'constraints.txt').write_text(''.join(
        f"{r['name']}=={r['version']}\n" for r in records))
    profiles[name] = {'roots': roots, 'prior_imports': scope[name]['imported_distributions']}
uvx = ROOT / 'tests/fixtures/hg_wuvx/artifacts'
uvx_records = []
expected = dict(line.split(maxsplit=1)[::-1] for line in (uvx / 'SHA256SUMS').read_text().splitlines())
for p in sorted((uvx / 'wheels').glob('*.whl')) + [uvx / 'uv-x86_64-unknown-linux-gnu.tar.gz']:
    relative = str(p.relative_to(uvx))
    actual = digest(p)
    assert expected[relative] == actual
    uvx_records.append({'path': str(p.relative_to(ROOT)), 'sha256': actual, 'bytes': p.stat().st_size})
# Preserve registry scope and the no-change comparison inputs before any edit.
registry = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
save(HERE / 'registry-before.json', registry)
save(HERE / 'inputs.json', {'payload_directory': str(work), 'wheel_directory': str(wheels),
     'artifacts': records, 'profiles': profiles, 'uvx_artifacts': uvx_records,
     'missing_from_inherited_import_corpus': sorted(keys - available.keys()),
     'baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
     'policy': 'retained local bytes only; no downloads, model, endpoint, task, scorer or GPU calls'})
run(HERE / 'raw', 'wheel-sha256sum', ['sha256sum', *[r['path'] for r in records]])
run(HERE / 'raw', 'uvx-sha256sum', ['sha256sum', *[ROOT / r['path'] for r in uvx_records]])
print(json.dumps({'artifacts': len(records), 'bytes': sum(r['bytes'] for r in records),
                  'payload_directory': str(work), 'missing': sorted(keys - available.keys())}))
