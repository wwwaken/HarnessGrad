"""Freeze locally chosen build dependencies and the observed wheel timestamp."""
import calendar
import hashlib
from pathlib import Path
import zipfile

packet = Path(__file__).resolve().parents[1]
versions = {'setuptools': '69.5.1', 'wheel': '0.43.0', 'setuptools_scm': '8.1.0', 'packaging': '24.0'}
lines = []
for name, version in versions.items():
    p = packet / 'acquired' / f'{name}-{version}-py3-none-any.whl'
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    lines.append(f'{name}=={version} --hash=sha256:{digest}')
    print(p.name, digest)
(packet / 'build-requirements.txt').write_text('\n'.join(lines) + '\n')
wheel = next((packet.parent / 'ujson_pypi_codex226/artifacts').glob('*.whl'))
with zipfile.ZipFile(wheel) as z:
    epoch = calendar.timegm(z.infolist()[0].date_time)
(packet / 'build-env.sh').write_text(f'export SETUPTOOLS_SCM_PRETEND_VERSION=5.10.0\nexport SOURCE_DATE_EPOCH={epoch}\nexport PYTHONHASHSEED=0\nexport TZ=UTC\nexport LC_ALL=C.UTF-8\n')
print('published wheel sha256', hashlib.sha256(wheel.read_bytes()).hexdigest())
print('SOURCE_DATE_EPOCH', epoch, '(from ZIP metadata; not authenticated build time)')
