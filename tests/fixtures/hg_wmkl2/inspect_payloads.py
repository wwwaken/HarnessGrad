"""Read exact archive metadata and installed source bytes, no imports/execution."""
from email.parser import BytesParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlparse
import zipfile
from common import HERE, ROOT, digest, save

work = json.loads((HERE / 'work.json').read_text())
prefix = Path(work['directory']) / 'ds1000'
plan = json.loads((HERE / 'offline/plan.json').read_text())
records = []
for item in plan['install']:
    path = Path(unquote(urlparse(item['download_info']['url']).path))
    assert digest(path) == item['download_info']['archive_info']['hashes']['sha256']
    with zipfile.ZipFile(path) as archive:
        metadata_name = next(n for n in archive.namelist() if n.endswith('.dist-info/METADATA'))
        wheel_name = next(n for n in archive.namelist() if n.endswith('.dist-info/WHEEL'))
        raw = archive.read(metadata_name)
        headers = BytesParser().parsebytes(raw)
        wheel = archive.read(wheel_name).decode()
    records.append({'name': headers['Name'], 'version': headers['Version'], 'path': str(path),
                    'sha256': digest(path), 'bytes': path.stat().st_size,
                    'requires_python': headers['Requires-Python'], 'requires_dist': headers.get_all('Requires-Dist', []),
                    'wheel_metadata': wheel, 'already_supplied_by_conda': headers['Name'].lower() == 'numpy'})
    if headers['Name'].lower().replace('_', '-') in ['tensorflow-cpu', 'xgboost', 'scipy', 'gensim']:
        target = HERE / 'metadata' / (headers['Name'] + '-' + headers['Version'] + '.txt')
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(raw)
save(HERE / 'selected-wheel-metadata.json', records)
# The exact host failure site and unchanged source after the compatible dependency install.
host_site = Path(sys.prefix) / 'lib/python3.12/site-packages'
installed_site = prefix / 'lib/python3.12/site-packages'
sources = []
for label, base, relative in [('host-gensim-matutils', host_site, 'gensim/matutils.py'),
                              ('installed-gensim-matutils', installed_site, 'gensim/matutils.py'),
                              ('host-scipy-linalg-init', host_site, 'scipy/linalg/__init__.py'),
                              ('installed-scipy-linalg-init', installed_site, 'scipy/linalg/__init__.py'),
                              ('installed-scipy-special-matrices', installed_site, 'scipy/linalg/_special_matrices.py')]:
    path = base / relative
    target = HERE / 'source' / (label + '.numbered.txt')
    target.write_text(''.join(f'{i:4}\t{line}\n' for i, line in enumerate(path.read_text().splitlines(), 1)))
    sources.append({'path': str(path), 'sha256': digest(path), 'numbered_copy': str(target.relative_to(ROOT))})
assert sources[0]['sha256'] == sources[1]['sha256'], 'No Gensim import-source patch allowed'
save(HERE / 'installed-source-hashes.json', sources)
old = json.loads((HERE.parent / 'hg_wmkl/coverage.json').read_text())
complete = sorted(old['newly_complete'] + old['previously_complete'] + ['ds1000'])
empty = old['no_third_party_payload_required']
coverage = {'scope': 'Recorded source-led scorer import payload installation, with upstream-compatible SciPy and added released-context packages. Not the incompatible original host stack.',
            'complete_nonempty': complete, 'no_third_party_payload_required': empty, 'partial': [],
            'complete_nonempty_count': len(complete), 'no_third_party_payload_count': len(empty),
            'partial_count': 0, 'inventory_count': len(complete) + len(empty),
            'production_authorized': False, 'dataset_eligibility_changed': False,
            'newly_resolved_profile': 'ds1000', 'ds1000_scope': 'Import-only, target CPython3.12.4, recorded scientific roots and explicit Gensim/TensorFlow/XGBoost import sites.'}
save(HERE / 'coverage.json', coverage)
# Both selected and unused candidate payloads are retained externally; no old bytes modified.
external = json.loads((HERE / 'reused-and-downloaded-artifacts.json').read_text())
paths = sorted({record['path'] for record in external} | {record['path'] for record in records})
(HERE / 'EXTERNAL_SHA256SUMS').write_text(''.join(f'{digest(Path(path))}  {path}\n' for path in paths))
print(json.dumps({'selected_resolver_wheels': len(records), 'new_lock_entries': len((HERE / 'additions.lock').read_text().splitlines()),
                  'retained_external_and_reused_artifacts': len(paths), 'coverage': coverage,
                  'sources': sources, 'key_payloads': [r for r in records if r['name'].lower().replace('_','-') in ['tensorflow-cpu','xgboost','scipy','gensim']]}, indent=2))
