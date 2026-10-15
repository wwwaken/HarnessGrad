#!/usr/bin/env python3
"""Capture BIRD's finite stdlib/SQLite native userland, without running a dataset.

The manifest is a reviewed admission pin, not auto-updated during verification.
Collection resolution is evidence only; execution sees only the captured files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--store', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    raw = args.out / 'commands'
    raw.mkdir(exist_ok=True)
    commands = []

    def capture(argv):
        result = subprocess.run(argv, capture_output=True, text=True,
                                env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})
        name = f'{len(commands):04d}'
        (raw / f'{name}.stdout.txt').write_text(result.stdout)
        (raw / f'{name}.stderr.txt').write_text(result.stderr)
        commands.append({'argv': argv, 'returncode': result.returncode, 'raw': f'commands/{name}'})
        if result.returncode:
            raise RuntimeError(commands[-1])
        return result.stdout, name

    exe = Path(sys.executable).resolve()
    stdlib = Path(sys.base_prefix) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}'
    entries = {}
    queue = []
    elf = {}

    def add(path, site, source_override=None):
        path = Path(os.path.normpath(path))
        if str(path) in entries:
            return
        source = Path(source_override or path).resolve(strict=True)
        if not source.is_file():
            raise ValueError(source)
        data = source.read_bytes()
        entries[str(path)] = {'source': (str(source.relative_to(Path.cwd()))
                                                       if source.is_relative_to(Path.cwd()) else str(source)), 'sha256': hashlib.sha256(data).hexdigest(),
                              'size': len(data), 'entry': site}
        if data.startswith(b'\x7fELF'):
            queue.append(path)

    add(exe, 'data/datasets/bird_minidev.py:257 (interpreter selected by native_runtime binding)')
    add(exe.parent / 'python3', 'data/datasets/bird_minidev.py:257 (closed child PATH alias)')
    # Entire stdlib source/extension superset, excluding ambient site packages and caches.
    for directory, dirs, files in os.walk(stdlib):
        dirs[:] = sorted(d for d in dirs if d not in {'site-packages', '__pycache__'})
        for name in sorted(files):
            if name.endswith(('.py', '.so')):
                add(Path(directory) / name,
                    'data/datasets/bird_minidev/verify/check.py:30 (stdlib/SQLite import closure)')
    for target, source in {
        '/scorer/check.py': 'data/datasets/bird_minidev/verify/check.py',
        '/scorer/data/__init__.py': 'data/__init__.py',
        '/scorer/data/scaffolds/__init__.py': 'data/scaffolds/__init__.py',
        '/scorer/data/scaffolds/scorer_input.py': 'data/scaffolds/scorer_input.py',
    }.items():
        add(target, source + ':1 (trusted scorer code, separate from actor files)', source)
    while queue:
        path = queue.pop(0)
        if str(path) in elf:
            continue
        dynamic, readelf_id = capture(['/usr/bin/readelf', '-lW', '-dW', str(path)])
        providers, ldd_id = capture(['/usr/bin/ldd', str(path)])
        if 'not found' in providers:
            raise ValueError(providers)
        graph = []
        for line in providers.splitlines():
            match = re.search(r'=> (/\S+)|^\s*(/\S+)', line)
            if match:
                dep = os.path.normpath(next(g for g in match.groups() if g))
                add(dep, f'ELF provider from {path}; commands/{ldd_id}.stdout.txt')
                graph.append(dep)
        interp = re.search(r'Requesting program interpreter: ([^\]]+)', dynamic)
        if interp:
            add(interp[1], f'PT_INTERP from {path}; commands/{readelf_id}.stdout.txt')
            graph.append(interp[1])
        elf[str(path)] = {'providers': sorted(set(graph)), 'readelf': readelf_id, 'ldd': ldd_id}
    # The launcher's bytes are also admitted; its own loader is the trusted host TCB.
    bwrap = Path('/usr/bin/bwrap')
    bwrap_hash, _ = capture(['/usr/bin/sha256sum', str(bwrap)])
    identity, _ = capture([str(exe), '-I', '-S', '-c',
        'import sys,sysconfig,sqlite3,json,platform; print(json.dumps(dict(version=sys.version, '
        'executable=sys.executable,soabi=sysconfig.get_config_var("SOABI"),sqlite=sqlite3.sqlite_version,'
        'kernel=platform.release(),machine=platform.machine()),sort_keys=True))'])
    manifest = {'schema': 1, 'dataset': 'bird_minidev', 'interpreter': str(exe),
                'loader': '/lib64/ld-linux-x86-64.so.2',
                'library_path': sorted({str(Path(p).parent) for p in entries
                                        if entries[p]['entry'].startswith(('ELF', 'PT_INTERP'))}),
                'environment': {'PATH': str(exe.parent), 'HOME': '/tmp', 'TMPDIR': '/tmp',
                                'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'},
                'python_flags': ['-I', '-S', '-B'],
                'identity': json.loads(identity),
                'launcher': {'path': str(bwrap), 'sha256': bwrap_hash.split()[0]},
                'files': dict(sorted(entries.items()))}
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    manifest_hash, _ = capture(['/usr/bin/sha256sum', str(args.manifest)])
    for start in range(0, len(entries), 100):
        paths = list(entries)[start:start + 100]
        hashes, _ = capture(['/usr/bin/sha256sum', *[entries[p]['source'] for p in paths]])
        for target, line in zip(paths, hashes.splitlines(), strict=True):
            digest, source = line.split('  ', 1)
            assert entries[target]['sha256'] == digest
            assert entries[target]['source'] == source
    args.store.mkdir(parents=True, exist_ok=True)
    payload = args.store / (manifest_hash.split()[0] + '.tar.gz')
    with tarfile.open(payload, 'w:gz') as tar:
        for path, entry in manifest['files'].items():
            tar.add(entry['source'], arcname=path.lstrip('/'), recursive=False)
    capture(['/usr/bin/sha256sum', str(payload)])
    (args.out / 'elf-graph.json').write_text(json.dumps(elf, indent=2, sort_keys=True) + '\n')
    (args.out / 'invocations.json').write_text(json.dumps(commands, indent=2) + '\n')
    summary = {'manifest_sha256': manifest_hash.split()[0], 'files': len(entries),
               'elf': len(elf), 'bytes': sum(e['size'] for e in entries.values()),
               'payload': str(payload), 'identity': manifest['identity']}
    (args.out / 'build-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
