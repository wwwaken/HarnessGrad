"""Resolve recursive ELF paths and undefined symbol providers in CPython itself."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import ujson

out = Path('/receipts/providers')
out.mkdir()


def command(name, argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    (out / (name + '.stdout.txt')).write_text(p.stdout)
    (out / (name + '.stderr.txt')).write_text(p.stderr)
    (out / (name + '.command.json')).write_text(json.dumps({'argv': argv, 'returncode': p.returncode}, indent=2) + '\n')
    assert p.returncode == 0, (argv, p.stderr)
    return p.stdout


class DlInfo(ctypes.Structure):
    _fields_ = [('dli_fname', ctypes.c_char_p), ('dli_fbase', ctypes.c_void_p),
                ('dli_sname', ctypes.c_char_p), ('dli_saddr', ctypes.c_void_p)]


api = ctypes.CDLL(None)
api.dlsym.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
api.dlsym.restype = ctypes.c_void_p
api.dlvsym.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
api.dlvsym.restype = ctypes.c_void_p
api.dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(DlInfo)]
api.dladdr.restype = ctypes.c_int
api.dlerror.restype = ctypes.c_char_p

queue = [Path(ujson.__file__).resolve(), Path(sys.executable).resolve()]
files = {}
symbols = []
while queue:
    path = queue.pop(0)
    if str(path) in files:
        continue
    label = path.name
    ldd = command(label + '.ldd', ['ldd', '-v', str(path)])
    assert 'not found' not in ldd
    deps = set(re.findall(r'(?:=>\s+|^\s*)(/\S+)\s+\(', ldd, re.M))
    for dep in sorted(deps):
        queue.append(Path(dep).resolve())
    elf = command(label + '.readelf', ['readelf', '-h', '-l', '-d', '-V', '--dyn-syms', '-W', str(path)])
    identity = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'bytes': path.stat().st_size,
                'needed': re.findall(r'\(NEEDED\).*\[(.*?)\]', elf),
                'resolved_recursive_ldd_paths': sorted(deps)}
    pkg = subprocess.run(['dpkg-query', '-S', str(path)], capture_output=True, text=True)
    (out / (label + '.dpkg-owner.stdout.txt')).write_text(pkg.stdout)
    (out / (label + '.dpkg-owner.stderr.txt')).write_text(pkg.stderr)
    identity['dpkg_query_returncode'] = pkg.returncode
    identity['dpkg_owner'] = pkg.stdout.strip()
    files[str(path)] = identity
    # The Python executable is already in the main program scope; dependent DSOs
    # are located with RTLD_NOLOAD so this never substitutes a provider file.
    handle = api if path == Path(sys.executable).resolve() else ctypes.CDLL(str(path), mode=os.RTLD_NOLOAD | os.RTLD_NOW)
    for line in elf.splitlines():
        match = re.match(r'\s*\d+:\s+\S+\s+\d+\s+\S+\s+(GLOBAL|WEAK)\s+\S+\s+UND\s+(\S+)', line)
        if not match:
            continue
        binding, full = match.groups()
        name, _, version = full.partition('@')
        # ELF relocations also search the main executable/global scope.
        # dlsym on the extension handle alone omits CPython's global libpython.
        for scope in (handle, api):
            api.dlerror()
            addr = (api.dlvsym(scope._handle, name.encode(), version.encode()) if version
                    else api.dlsym(scope._handle, name.encode()))
            error = api.dlerror()
            if not error:
                break
        record = {'consumer': str(path), 'symbol': full, 'binding': binding}
        if error:
            record['error'] = error.decode()
            assert binding == 'WEAK', record
        elif addr:
            info = DlInfo()
            assert api.dladdr(addr, ctypes.byref(info)), record
            record['provider'] = str(Path(os.fsdecode(info.dli_fname)).resolve())
            record['provider_symbol'] = os.fsdecode(info.dli_sname) if info.dli_sname else None
        else:
            record['zero_address_without_dlerror'] = True
        symbols.append(record)

for symbol in symbols:
    if 'provider' in symbol:
        provider = Path(symbol['provider'])
        symbol['provider_sha256'] = hashlib.sha256(provider.read_bytes()).hexdigest()
command('package-versions', ['dpkg-query', '-W', '-f=${Package}\t${Version}\t${Architecture}\n'])
command('glibc', ['getconf', 'GNU_LIBC_VERSION'])
command('ldd-version', ['ldd', '--version'])
command('readelf-version', ['readelf', '--version'])
command('ldconfig-cache', ['/sbin/ldconfig', '-p'])
for source in ('/etc/ld.so.conf', '/etc/ld.so.cache', '/proc/self/maps'):
    (out / Path(source).name).write_bytes(Path(source).read_bytes())
(out / 'ld.so.conf.d.json').write_text(json.dumps({str(p): p.read_text() for p in Path('/etc/ld.so.conf.d').glob('*')}, indent=2) + '\n')
(out / 'symbols.json').write_text(json.dumps(symbols, indent=2) + '\n')
(out / 'files.json').write_text(json.dumps(files, indent=2) + '\n')
print(json.dumps({'files': files, 'undefined_symbols_checked': len(symbols),
                  'strong_resolution_failures': 0,
                  'optional_weak_unresolved': [s for s in symbols if 'error' in s],
                  'note': 'dlsym/dlvsym verifies available providers; LD_DEBUG records actual import bindings',
                  'passed': True}, indent=2))
