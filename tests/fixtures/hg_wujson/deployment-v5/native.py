"""Native import and exact installed-member mapping, on fabricated JSON only."""
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform
import sys
import zipfile

import ujson

assert sys.implementation.name == 'cpython' and sys.version_info[:2] == (3, 12)
assert platform.system() == 'Linux' and platform.machine() == 'x86_64'
assert platform.libc_ver()[0] == 'glibc'
assert ujson.__version__ == '5.10.0'
root = Path('/opt/hg-wujson')
wheel = next(root.glob('*.whl'))
assert hashlib.sha256(wheel.read_bytes()).hexdigest() == 'f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1'
members = {}
with zipfile.ZipFile(wheel) as archive:
    for name in archive.namelist():
        if name.endswith('/') or name.endswith('/RECORD'):
            continue
        installed = Path(ujson.__file__).parent / name
        assert archive.read(name) == installed.read_bytes(), name
        members[name] = {'installed_path': str(installed),
                         'sha256': hashlib.sha256(installed.read_bytes()).hexdigest()}
payload = {'synthetic': ['fictional azure', 0.125, 1e100, True, None, '\u96ea']}
assert ujson.loads(ujson.dumps(payload, ensure_ascii=False)) == payload
notices = {}
for name in ('ujson-LICENSE.txt', 'double-conversion-LICENSE'):
    path = Path('/usr/local/share/licenses/hg-wujson') / name
    assert path.read_bytes() == (root / 'notices' / name).read_bytes()
    notices[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
print(json.dumps({'python': sys.version, 'executable': sys.executable,
                  'platform': platform.platform(), 'machine': platform.machine(),
                  'glibc': platform.libc_ver(), 'pip': importlib.metadata.version('pip'),
                  'ujson': ujson.__version__, 'module': ujson.__file__,
                  'import_spec': str(importlib.util.find_spec('ujson')),
                  'wheel_sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
                  'installed_members': members, 'notices': notices,
                  'synthetic_roundtrip': payload, 'passed': True}, indent=2))
