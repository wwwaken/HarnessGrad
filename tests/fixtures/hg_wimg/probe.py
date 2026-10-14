"""Image-local import/ELF inspection only: never import a benchmark or create a world."""
import ctypes
import hashlib
import importlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys
import sysconfig


def identity(path):
    p = Path(path)
    try:
        h = hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                h.update(block)
        return {'path': str(p), 'resolved': str(p.resolve()), 'sha256': h.hexdigest(),
                'size': p.stat().st_size}
    except Exception as e:
        return {'path': str(p), 'error': repr(e)}


def command(argv):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=12)
        return {'argv': argv, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except Exception as e:
        return {'argv': argv, 'error': repr(e)}


def interp(path):
    """Read PT_INTERP directly, including on images without readelf."""
    try:
        with open(path, 'rb') as f:
            hdr = f.read(64)
            if hdr[:4] != b'\x7fELF':
                return None
            endian = '<' if hdr[5] == 1 else '>'
            if hdr[4] == 2:
                offset, entsize, count = struct.unpack_from(endian+'Q', hdr, 32)[0], *struct.unpack_from(endian+'HH', hdr, 54)
                fmt = endian+'IIQQQQQQ'
            else:
                offset, entsize, count = struct.unpack_from(endian+'I', hdr, 28)[0], *struct.unpack_from(endian+'HH', hdr, 42)
                fmt = endian+'IIIIIIII'
            for i in range(count):
                f.seek(offset+i*entsize)
                ph = struct.unpack(fmt, f.read(struct.calcsize(fmt)))
                if ph[0] == 3:
                    start, size = (ph[2], ph[5]) if hdr[4] == 2 else (ph[1], ph[4])
                    f.seek(start)
                    return f.read(size).rstrip(b'\0').decode()
    except Exception as e:
        return {'error': repr(e)}


label = sys.argv[1]
result = {'scope': 'base image import/ELF probe; no benchmark, scoring, model or GPU calls',
          'label': label, 'python': sys.version, 'implementation': platform.python_implementation(),
          'executable': identity(sys.executable), 'soabi': sysconfig.get_config_var('SOABI'),
          'libc': platform.libc_ver(), 'machine': platform.machine(), 'imports': {},
          'commands': [], 'elf': [], 'distributions': []}
result['glibc_confstr'] = os.confstr('CS_GNU_LIBC_VERSION') if 'CS_GNU_LIBC_VERSION' in os.confstr_names else None
try:
    c = ctypes.CDLL(None)
    c.gnu_get_libc_version.restype = ctypes.c_char_p
    result['glibc_runtime'] = c.gnu_get_libc_version().decode()
except Exception as e:
    result['glibc_runtime_error'] = repr(e)
modules = ['hashlib', '_hashlib', 'ssl', '_ssl', 'sqlite3', '_sqlite3', 'zlib', 'bz2', 'lzma', '_ctypes']
if label == 'gaia':
    modules += ['numpy']
if label == 'appworld-verifier':
    modules += ['appworld']
for name in modules:
    try:
        m = importlib.import_module(name)
        result['imports'][name] = {'file': getattr(m, '__file__', None),
                                   'version': getattr(m, '__version__', None)}
    except Exception as e:
        result['imports'][name] = {'error': repr(e)}
result['openssl'] = getattr(sys.modules.get('ssl'), 'OPENSSL_VERSION', None)
result['sqlite'] = getattr(sys.modules.get('sqlite3'), 'sqlite_version', None)
for d in sorted(md.distributions(), key=lambda d: d.metadata.get('Name', '').lower()):
    files = list(d.files or [])
    meta = [identity(d.locate_file(f)) for f in files if str(f).endswith(('.dist-info/METADATA', '.dist-info/RECORD'))]
    result['distributions'].append({'name': d.metadata.get('Name'), 'version': d.version,
                                    'requires': d.requires or [], 'metadata': meta})
maps = Path('/proc/self/maps').read_text()
result['process_maps'] = maps
seeds = {str(Path(sys.executable).resolve()), '/bin/sh', '/bin/bash'}
for line in maps.splitlines():
    tail = line.split()[-1]
    if tail.startswith('/') and not tail.endswith(' (deleted)'):
        seeds.add(tail)
# Metadata is only a superset of possible runtime imports. Inspect extension files
# for the AppWorld native import surface even if its top-level import is lazy.
if label == 'appworld-verifier':
    for root in sys.path:
        p = Path(root)
        if p.is_dir() and p.name in ('site-packages', 'dist-packages'):
            for pattern in ('orjson/*.so', 'xxhash/*.so', 'pydantic_core/*.so', 'greenlet/*.so', 'sqlalchemy/**/*.so'):
                seeds.update(str(x) for x in p.glob(pattern))
queue = sorted(seeds)
seen = set()
while queue:
    path = queue.pop(0)
    p = Path(path)
    if not p.is_file() or str(p.resolve()) in seen:
        continue
    seen.add(str(p.resolve()))
    with p.open('rb') as f:
        if f.read(4) != b'\x7fELF':
            continue
    item = identity(p)
    loader = interp(p)
    item['pt_interp'] = loader
    if isinstance(loader, str):
        item['loader'] = identity(loader)
        queue.append(loader)
    item['ldd'] = command(['ldd', str(p)])
    if shutil.which('readelf'):
        item['readelf'] = command(['readelf', '-l', '-d', '-V', '-W', str(p)])
    for match in re.findall(r'(/[^\s()]+)', item['ldd'].get('stdout', '')):
        if Path(match).is_file():
            queue.append(match)
    result['elf'].append(item)
for argv in (['getconf', 'GNU_LIBC_VERSION'], ['ldd', '--version'],
             ['dpkg-query', '-W', '-f=${Package}\t${Version}\t${Architecture}\n'],
             ['apk', 'info', '-v']):
    result['commands'].append(command(argv))
print(json.dumps(result, indent=2, sort_keys=True))
