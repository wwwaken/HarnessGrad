"""Derive identities, actual loaded subsets and file/line entry citations from raw capture."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
manifest_path = ROOT / 'data/runtimes/bird_minidev-native.json'
manifest = json.loads(manifest_path.read_text())
graph = json.loads((OUT / 'final-capture/elf-graph.json').read_text())


def site(path, needle):
    source = (ROOT / path).read_text()
    rows = source.splitlines()
    found = [(i, line) for i, line in enumerate(rows, 1) if needle in line]
    assert found, (path, needle)
    number, text = found[0]
    return {'file': path, 'line': number, 'text': text, 'locator': f'{path}:{number}'}


sites = [site('data/datasets/bird_minidev.py', '"argv": ["python3"'),
         site('data/datasets/bird_minidev.py', 'spec["native_runtime"]'),
         site('data/datasets/bird_minidev/verify/check.py', 'import sqlite3'),
         site('data/datasets/bird_minidev/verify/check.py', 'from data.scaffolds.scorer_input'),
         site('data/datasets/bird_minidev/verify/check.py', 'sqlite3.connect'),
         site('data/scaffolds/scorer_input.py', 'import hashlib'),
         site('data/scaffolds/scorer_input.py', 'import tempfile'),
         site('eval/verification/native_runtime.py', 'fcntl.fcntl(fd, F_ADD_SEALS'),
         site('eval/verification/native_runtime.py', "'--ro-bind-data'"),
         site('eval/verification/native_runtime.py', "'--inhibit-cache'"),
         site('eval/verification/verifier.py', 'with admit(binding) as runtime'),
         site('eval/verification/verifier.py', 'proc = native_runtime.run'),
         site('harnessgrad/records.py', '"protocol", "native_runtime"')]
(OUT / 'source-sites.json').write_text(json.dumps(sites, indent=2) + '\n')
# Preserve the actual source preimages cited in this packet.
source_dir = OUT / 'source'
source_dir.mkdir(exist_ok=True)
for name in sorted({s['file'] for s in sites}):
    (source_dir / name.replace('/', '__')).write_bytes((ROOT / name).read_bytes())

trace = (OUT / 'bound-check.strace.txt').read_text().splitlines()
scorers = {}
for i, line in enumerate(trace, 1):
    if 'execve("/lib64/ld-linux-x86-64.so.2"' in line and '/scorer/check.py' in line:
        scorers[line.split()[0]] = {'exec_line': i, 'loads': {}}
for i, line in enumerate(trace, 1):
    pid = line.split()[0]
    if pid not in scorers or 'mmap(' not in line or ' = -1' in line:
        continue
    for path in re.findall(r'<(/[^>]+)>', line):
        path = os.path.normpath(path.removesuffix(' (deleted)'))
        if path in manifest['files']:
            scorers[pid]['loads'].setdefault(path, i)
        else:
            raise AssertionError(('unadmitted scorer map', pid, path, i))
assert scorers
loaded = sorted({p for s in scorers.values() for p in s['loads']})
assert manifest['interpreter'] in loaded and any('libsqlite3' in p for p in loaded)
# Kernel's initial PT_INTERP mapping precedes strace mmap observations; include
# its separately observed exec and the parent/child /proc/self/maps capture.
loaded = sorted(set(loaded) | {manifest['loader']})
# BIRD invokes no child executable: no later execve on any scorer pid, nor an
# execve whose parent was a scorer in this trace (the trace covers exec/open/mmap).
# This is bounded to the traced check. The separate probe explicitly starts Python.
(OUT / 'scorer-loads.json').write_text(json.dumps({'processes': scorers, 'loaded': loaded}, indent=2) + '\n')

commands = json.loads((OUT / 'final-capture/invocations.json').read_text())
sha_index = {}
for call in commands:
    if call['argv'][0] != '/usr/bin/sha256sum':
        continue
    for line in (OUT / 'final-capture' / (call['raw'] + '.stdout.txt')).read_text().splitlines():
        digest, path = line.split('  ', 1)
        sha_index[path] = {'sha256': digest, 'raw': 'final-capture/' + call['raw'] + '.stdout.txt'}
for path, entry in manifest['files'].items():
    assert sha_index[entry['source']]['sha256'] == entry['sha256']

lines = ['# Complete admitted userland and actual scorer subset - w-hostpin', '',
         'Every file below has a fresh independent raw sha256sum record. The manifest fixes',
         'the absolute destination and eliminates ambient aliases/search/caches. ELF parent',
         'DT_NEEDED/PT_INTERP citations reference verbatim readelf output, with numbered lines.', '',
         '| Destination | SHA-256 | Entry into scoring / ELF provider edge | Raw hash |',
         '| --- | --- | --- | --- |']
for path, entry in manifest['files'].items():
    edges = []
    for parent, details in graph.items():
        if path not in details['providers']:
            continue
        raw = f"final-capture/commands/{details['readelf']}.stdout.txt"
        rows = (OUT / raw).read_text().splitlines()
        basename = Path(path).name
        matched = [(i, text) for i, text in enumerate(rows, 1)
                   if ('NEEDED' in text and f'[{basename}]' in text)
                   or ('Requesting program interpreter:' in text and path in text)]
        for number, text in matched:
            edges.append(f'`{parent}` → `{raw}:{number}`')
    if '/python3.12/' in path or path.startswith('/scorer/'):
        edges.insert(0, entry['entry'])
    if not edges:
        edges = [entry['entry']]
    actual = '**actual scorer load**; ' if path in loaded else ''
    lines.append(f"| `{path}` | `{entry['sha256']}` | {actual}{'; '.join(edges)} | `{sha_index[entry['source']]['raw']}` |")
(OUT / 'closure-files.md').write_text('\n'.join(lines) + '\n')

routes = ['alfworld', 'jericho', 'scienceworld', 'bird_minidev', 'ds1000',
          'spreadsheetbench', 'chessbench_puzzles']
optins = []
for dataset in routes:
    tree = ast.parse((ROOT / f'data/datasets/{dataset}.py').read_text())
    if any(isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
           and node.slice.value == 'native_runtime' and isinstance(node.ctx, ast.Store)
           for node in ast.walk(tree)):
        optins.append(dataset)
assert optins == [manifest['dataset']]
facts = {'complete_pinned_native_surfaces': {'numerator': len(optins), 'denominator': len(routes)},
         'host_routes': routes, 'native_runtime_optins': optins,
         'scoped_dataset': 'bird_minidev', 'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
         'files': len(manifest['files']), 'elf_destinations': len(graph),
         'unique_payload_digests': len({e['sha256'] for e in manifest['files'].values()}),
         'actual_scorer_elf_destinations_including_loader': len(loaded),
         'scorer_processes_in_trace': len(scorers), 'identity': manifest['identity']}
actual_lines = ['# Actual scorer native objects - w-hostpin', '',
    'Source entries: interpreter selection `data/datasets/bird_minidev.py:257`; SQLite',
    '`data/datasets/bird_minidev/verify/check.py:30`; JSON `:28`; trusted helper `:37`',
    'then `data/scaffolds/scorer_input.py:14` (hashlib) and `:17` (tempfile).',
    'The helper imports tempfile → shutil/random → compression, math and random',
    'extensions; hashlib selects _hashlib/_blake2/_sha2; SQLite imports datetime.',
    'The complete parent DT_NEEDED/PT_INTERP links and independent raw hashes are',
    'in closure-files.md. File/line locators below refer to repository source.', '',
    '| Mapped ELF destination | Fresh SHA-256 | Source entry | First raw trace line |',
    '| --- | --- | --- | --- |']
for path in loaded:
    name = Path(path).name
    if 'sqlite' in name or '_datetime' in name:
        entry = 'data/datasets/bird_minidev/verify/check.py:30'
    elif any(part in name for part in ('hashlib', 'blake2', 'sha2', 'crypto')):
        entry = 'data/scaffolds/scorer_input.py:14'
    elif '_json' in name:
        entry = 'data/datasets/bird_minidev/verify/check.py:28'
    elif name.startswith(('libc.', 'libdl.', 'libpthread.', 'libutil.', 'libm.', 'ld-linux', 'python3')):
        entry = 'data/datasets/bird_minidev.py:257'
    else:
        entry = 'data/scaffolds/scorer_input.py:17'
    trace_line = next((r['loads'][path] for r in scorers.values() if path in r['loads']),
                      next(iter(scorers.values()))['exec_line'])
    actual_lines.append(f"| `{path}` | `{manifest['files'][path]['sha256']}` | `{entry}` | `bound-check.strace.txt:{trace_line}` |")
(OUT / 'actual-scorer-native.md').write_text('\n'.join(actual_lines) + '\n')
(OUT / 'facts.json').write_text(json.dumps(facts, indent=2) + '\n')
print(json.dumps(facts, indent=2))
for path in loaded:
    print(path, manifest['files'][path]['sha256'])
