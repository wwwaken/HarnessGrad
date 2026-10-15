"""Derive the closure inventory and import/ELF citations from retained raw commands."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
STDLIB = Path(sys.base_prefix) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}'
SITE = STDLIB / 'site-packages'
sources = {}
citations = []


def cite(path, needle):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    lines = path.read_text().splitlines()
    matches = [i for i, line in enumerate(lines, 1) if needle in line]
    assert matches, (str(path), needle)
    number = matches[0]
    key = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    sources[key] = path
    citations.append({'file': key, 'line': number, 'text': lines[number - 1]})
    return f'{key}:{number}'


stdlib_edges = {
    '_ctypes': ('ctypes/__init__.py', 'from _ctypes import'),
    '_hashlib': ('hashlib.py', 'import _hashlib'),
    '_blake2': ('hashlib.py', 'import _blake2'),
    '_sha2': ('hashlib.py', 'import _sha2'),
    '_json': ('json/decoder.py', 'from _json import'),
    '_struct': ('struct.py', 'from _struct import'),
    '_random': ('random.py', 'import _random'),
    '_bisect': ('bisect.py', 'from _bisect import'),
    '_datetime': ('datetime.py', 'from _datetime import'),
    '_opcode': ('opcode.py', 'from _opcode import'),
    '_pickle': ('pickle.py', 'from _pickle import'),
    '_bz2': ('bz2.py', 'from _bz2 import'),
    '_lzma': ('lzma.py', 'from _lzma import'),
    '_socket': ('socket.py', 'import _socket'),
    '_ssl': ('ssl.py', 'import _ssl'),
    '_posixsubprocess': ('subprocess.py', 'from _posixsubprocess import'),
    '_contextvars': ('contextvars.py', 'from _contextvars import'),
    '_asyncio': ('asyncio/events.py', 'from _asyncio import'),
    '_csv': ('csv.py', 'from _csv import'),
    '_elementtree': ('xml/etree/ElementTree.py', 'from _elementtree import'),
    '_heapq': ('heapq.py', 'from _heapq import'),
    '_queue': ('queue.py', 'from _queue import'),
    '_uuid': ('uuid.py', 'import _uuid'),
    'select': ('selectors.py', 'import select'),
    'fcntl': ('subprocess.py', 'import fcntl'),
    'math': ('random.py', 'from math import'),
    'binascii': ('base64.py', 'import binascii'),
    'zlib': ('gzip.py', 'import zlib'),
    'pyexpat': ('xml/parsers/expat.py', 'from pyexpat import'),
    'array': ('socket.py', 'import array'),
    'unicodedata': ('stringprep.py', 'from unicodedata import'),
}
package_edges = {
    '_mklinit': ('mkl/__init__.py', 'from . import _mklinit'),
    '_py_mkl_service': ('mkl/__init__.py', 'from ._py_mkl_service import'),
    '_multiarray_umath': ('numpy/core/overrides.py', 'from numpy.core._multiarray_umath import'),
    '_multiarray_tests': ('numpy/core/_add_newdocs.py', "add_newdoc('numpy.core._multiarray_tests'"),
    '_umath_linalg': ('numpy/linalg/linalg.py', 'from numpy.linalg import _umath_linalg'),
    '_pocketfft_internal': ('numpy/fft/_pocketfft.py', 'from . import _pocketfft_internal'),
    '_psutil_linux': ('psutil/_pslinux.py', 'from . import _psutil_linux'),
    '_psutil_posix': ('psutil/_pslinux.py', 'from . import _psutil_posix'),
    'readline': ('textworld/agents/human.py', 'import readline'),
    'resource': ('fast_downward/driver/limits.py', 'import resource'),
}
for name in ['_common', '_bounded_integers', '_generator', 'bit_generator', '_mt19937',
             '_pcg64', '_philox', '_sfc64', 'mtrand']:
    package_edges[name] = ('numpy/random/__init__.py',
                           'from . import ' + name if name in {'_common', '_bounded_integers'}
                           else 'from .' + name + ' import')


def module_site(target, dataset):
    name = Path(target).name.split('.')[0]
    if name in stdlib_edges:
        path, needle = stdlib_edges[name]
        return cite(STDLIB / path, needle)
    if name in package_edges:
        path, needle = package_edges[name]
        return cite(SITE / path, needle)
    if name == 'libfrotz':
        return cite(SITE / 'jericho/jericho.py', 'frotz_lib = cdll.LoadLibrary')
    if name == 'libdownward':
        return cite(SITE / 'fast_downward/interface.py', 'downward_lib = cdll.LoadLibrary')
    if name.startswith(('libmkl', 'libiomp', 'libtbb')):
        return cite(SITE / 'numpy/_distributor_init.py', 'import mkl')
    if target.endswith('/python3.12'):
        return cite(f'data/datasets/{dataset}.py', '"python3", "check.py"')
    return None


def native_site(target, dataset, loaded, graph, capture):
    direct = module_site(target, dataset)
    if direct is not None:
        return direct
    parents = list(dict.fromkeys([p for p in loaded if p in graph]
                   + [p for p, info in graph.items() if target in info['providers']]))
    for parent in parents:
        info = graph[parent]
        raw = OUT / capture / f'commands/{info["readelf"]}.stdout.txt'
        needed = next((i for i, row in enumerate(raw.read_text().splitlines(), 1)
                       if Path(target).name in row and ('NEEDED' in row or 'interpreter:' in row)), None)
        if needed:
            return f'{capture}/commands/{info["readelf"]}.stdout.txt:{needed} (parent `{parent}`)'
    raise AssertionError((target, parents))


facts = {'complete_pinned_native_surfaces': {'numerator': 3, 'denominator': 7}, 'datasets': {}}
for dataset, capture in [('jericho', 'jericho-final-capture'), ('alfworld', 'alfworld-locale-capture')]:
    helper = 'jer_env' if dataset == 'jericho' else 'gym_env'
    for path, needle in [
        (f'data/datasets/{dataset}.py', 'spec["native_runtime"]'),
        (f'data/datasets/{dataset}/verify/check.py', 'from data.scaffolds.scorer_input'),
        (f'data/datasets/{dataset}/verify/check.py', f'import {helper}'),
        (f'data/datasets/{dataset}/verify/check.py', f'{helper}.load_game' if dataset == 'jericho' else f'{helper}.replay'),
        (f'data/datasets/{dataset}/lib/{helper}.py', 'from jericho import FrotzEnv' if dataset == 'jericho' else 'import textworld'),
        ('data/runtimes/__init__.py', f'"{dataset}": {{'),
        ('data/scaffolds/scorer_input.py', 'import hashlib'),
        ('eval/verification/native_runtime.py', 'fcntl.fcntl(fd, F_ADD_SEALS'),
        ('eval/verification/native_runtime.py', "'--ro-bind-data'"),
        ('eval/verification/verifier.py', 'with admit(binding) as runtime'),
        ('eval/verification/verifier.py', 'proc = native_runtime.run'),
    ]:
        cite(path, needle)
    manifest = json.loads((ROOT / f'data/runtimes/{dataset}-native.json').read_text())
    summary = json.loads((OUT / capture / 'build-summary.json').read_text())
    graph = json.loads((OUT / capture / 'elf-graph.json').read_text())
    raw_hashes = {}
    for record in json.loads((OUT / capture / 'invocations.json').read_text()):
        assert record['returncode'] == 0
        if record['argv'][0] == '/usr/bin/sha256sum':
            for number, row in enumerate((OUT / capture / (record['raw'] + '.stdout.txt')).read_text().splitlines(), 1):
                sha, source = row.split('  ', 1)
                raw_hashes[source] = (sha, f'{capture}/{record["raw"]}.stdout.txt:{number}')
    lines = ['# ' + dataset + ' closed admitted surface', '',
             'All destinations, including conservative unused providers. Each hash below comes from an independent retained sha256sum command. Entry sites lead from the selected scorer; ELF edges cite numbered raw readelf/ldd output.', '',
             '| Destination | SHA-256 | Entry and raw evidence |', '| --- | --- | --- |']
    for target, entry in manifest['files'].items():
        assert raw_hashes[entry['source']][0] == entry['sha256']
        citation = entry['entry']
        if target in graph:
            citation += f'; {capture}/commands/{graph[target]["readelf"]}.stdout.txt'
        lines.append(f'| `{target}` | `{entry["sha256"]}` | {citation}; {raw_hashes[entry["source"]][1]} |')
    (OUT / f'{dataset}-closure-files.md').write_text('\n'.join(lines) + '\n')

    trace = (OUT / 'bound-replay-final.strace.txt').read_text().splitlines()
    processes = {}
    for number, row in enumerate(trace, 1):
        if ('execve("/lib64/ld-linux-x86-64.so.2"' in row
                and ', "/scorer/check.py",' in row):
            selected = 'jericho' if '--rom' in row else 'alfworld'
            if selected == dataset:
                processes[row.split()[0]] = {'exec_line': number, 'loads': {}}
    assert processes, dataset
    for number, row in enumerate(trace, 1):
        pid = row.split()[0]
        if pid not in processes or 'mmap(' not in row or ' = -1' in row:
            continue
        for name in re.findall(r'<(/[^>]+)>', row):
            target = os.path.normpath(name.removesuffix(' (deleted)'))
            if target.startswith('/tmp/') and Path(target).name in {'libfrotz.so', 'libdownward.so'}:
                suffix = '/jericho/libfrotz.so' if dataset == 'jericho' else '/fast_downward/libdownward.so'
                target = next(p for p in manifest['files'] if p.endswith(suffix))
            elif target.startswith('/usr/lib/locale/'):
                assert target in manifest['files']
                continue  # data mmap, not an ELF mapping
            assert target in manifest['files'], (dataset, pid, target, number)
            processes[pid]['loads'].setdefault(target, number)
    loaded = sorted({p for process in processes.values() for p in process['loads']} | {manifest['loader']})
    assert manifest['interpreter'] in loaded
    rows = ['# ' + dataset + ' actual bound-check ELF loads', '',
            'Authored replay only. Both production checks run synchronously: no scorer child executable is expected. The separate inherited-child control is in pytest-targeted stdout. Copied ctypes destinations are linked to the admitted package library and checked independently by the audit control. Loader initial mapping is identified by the exec line; kernel/vDSO are outside this file closure.', '',
            '| Mapped/admitted object | Fresh SHA-256 | Scoring entry | Actual trace |', '| --- | --- | --- | --- |']
    for target in loaded:
        direct = native_site(target, dataset, loaded, graph, capture)
        locations = [f'bound-replay-final.strace.txt:{info["loads"][target]}'
                     for info in processes.values() if target in info['loads']]
        if not locations:
            locations = [f'bound-replay-final.strace.txt:{next(iter(processes.values()))["exec_line"]} (initial loader)']
        rows.append(f'| `{target}` | `{manifest["files"][target]["sha256"]}` | {direct} | {locations[0]} |')
    (OUT / f'{dataset}-actual-native.md').write_text('\n'.join(rows) + '\n')
    (OUT / f'{dataset}-scorer-loads.json').write_text(json.dumps({'processes': processes, 'loaded': loaded}, indent=2) + '\n')
    facts['datasets'][dataset] = {**summary, 'unique_payload_digests': len({e['sha256'] for e in manifest['files'].values()}),
                                  'actual_check_elf_destinations_including_loader': len(loaded),
                                  'actual_check_launches': len(processes), 'capture': capture}

    controls = []
    for row_number, row in enumerate((OUT / 'pytest-targeted.stdout.txt').read_text().splitlines(), 1):
        start = row.find('{')
        if start < 0:
            continue
        try:
            record = json.loads(row[start:])
        except json.JSONDecodeError:
            continue
        if record.get('dataset') == dataset and 'runtime' in record:
            controls.append((row_number, record))
    assert len(controls) == 1, dataset
    number, record = controls[0]
    control_loads = {}
    for role in ['parent', 'child']:
        audit = {r['path']: r['sha256'] for r in record[role]['ctypes']}
        mapped = set()
        for line in record[role]['maps'].splitlines():
            columns = line.split(maxsplit=5)
            if len(columns) != 6 or not columns[5].startswith('/'):
                continue
            target = columns[5].removesuffix(' (deleted)')
            if target in audit:
                matches = [p for p, e in manifest['files'].items()
                           if e['sha256'] == audit[target] and Path(p).name == Path(target).name]
                assert len(matches) == 1, matches
                target = matches[0]
            assert target in manifest['files'], target
            if target in graph:
                mapped.add(target)
        control_loads[role] = sorted(mapped)
    (OUT / f'{dataset}-control-loads.json').write_text(json.dumps({'raw_line': number, 'loads': control_loads,
        'ctypes_audit': {role: record[role]['ctypes'] for role in ['parent', 'child']}}, indent=2) + '\n')
    control_union = sorted(set(control_loads['parent']) | set(control_loads['child']))
    rows = [f'# {dataset} inherited parent/child control ELF loads', '',
            'These are authored process-inheritance controls, separate from the synchronous bound checks. Their additional subprocess imports are not attributed to the scoring check. Copied ctypes objects are normalized by the audit-time digest, not by a guessed temporary name.', '',
            '| Object | SHA-256 | Entry | Parent | Child | Raw maps |',
            '| --- | --- | --- | --- | --- | --- |']
    for target in control_union:
        direct = native_site(target, dataset, control_union, graph, capture)
        rows.append(f'| `{target}` | `{manifest["files"][target]["sha256"]}` | {direct} | '
                    + str(target in control_loads['parent']) + ' | ' + str(target in control_loads['child'])
                    + f' | pytest-targeted.stdout.txt:{number} |')
    (OUT / f'{dataset}-control-native.md').write_text('\n'.join(rows) + '\n')
    facts['datasets'][dataset]['inherited_control_elf_counts'] = {role: len(paths) for role, paths in control_loads.items()}

# Preserve raw source preimages and numbered citations, including installed importers.
source_records = []
for name, path in sorted(sources.items()):
    target = OUT / 'source' / (name.lstrip('/').replace('/', '__'))
    target.parent.mkdir(exist_ok=True)
    result = subprocess.run(['/usr/bin/nl', '-ba', str(path)], capture_output=True)
    assert result.returncode == 0
    target.with_suffix(target.suffix + '.numbered.txt').write_bytes(result.stdout)
    target.write_bytes(path.read_bytes())
    digest = subprocess.run(['/usr/bin/sha256sum', str(path)], capture_output=True)
    assert digest.returncode == 0
    target.with_suffix(target.suffix + '.sha256sum.txt').write_bytes(digest.stdout)
    source_records.append({'file': name, 'snapshot': str(target.relative_to(OUT)),
                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
(OUT / 'source-sites.json').write_text(json.dumps({'sources': source_records, 'citations': citations}, indent=2) + '\n')
(OUT / 'facts.json').write_text(json.dumps(facts, indent=2) + '\n')
print(json.dumps(facts, indent=2))
