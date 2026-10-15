#!/usr/bin/env python3
"""Validate this custody packet without executing BFCL."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def rows(p):
    return [json.loads(l) for l in p.open()]


archives = rows(OUT / 'w-bfclmem-archives.jsonl')
assert len(archives) == 95
members = [r for f in sorted(OUT.glob('w-bfclmem-members-*.jsonl')) for r in rows(f)]
by_archive = {}
for m in members:
    by_archive.setdefault(m['archive'], {})[m['member']] = m
for a in archives:
    p = Path(a['path'])
    b = p.read_bytes()
    assert len(b) == a['bytes'] and hashlib.sha256(b).hexdigest() == a['sha256']
    with zipfile.ZipFile(p) as z:
        regular = {x.filename for x in z.infolist() if not x.is_dir()}
        assert regular == by_archive[a['filename']].keys()
        for name in regular:
            b = z.read(name)
            m = by_archive[a['filename']][name]
            assert len(b) == m['bytes'] and hashlib.sha256(b).hexdigest() == m['sha256']
for l in rows(OUT / 'w-bfclmem-licenses.jsonl'):
    b = (ROOT / l['copy']).read_bytes()
    assert len(b) == l['bytes'] and hashlib.sha256(b).hexdigest() == l['sha256']
edges = rows(OUT / 'w-bfclmem-dependencies.jsonl')
assert len(edges) == 676
assert sum(x['active_selected_extras'] for x in edges) == 155
assert all(x['specifier_satisfied'] for x in edges if x['active_selected_extras'])
source = rows(OUT / 'w-bfclmem-source-summary.jsonl')[0]
source_modules = [x for p in OUT.glob('w-bfclmem-source-modules-*.jsonl') for x in rows(p)]
source_edges = [x for p in OUT.glob('w-bfclmem-source-edges-*.jsonl') for x in rows(p)]
assert source['modules'] == len(source_modules) and source['edges'] == len(source_edges) and not source['errors']
smoke = rows(OUT / 'w-bfclmem-smoke.jsonl')
assert not any(x['state'] in ['IMPORT FAILED', 'GRAMMAR FAILED', 'API mismatch'] for x in smoke)
assert {x['grammar'] for x in smoke if x.get('language_abi') == 14 and not x['has_error']} == {'java', 'javascript'}
native = [x for p in sorted(OUT.glob('w-bfclmem-native-*.jsonl')) for x in rows(p)]
loaded_hashes = {x['sha256'] for x in smoke if 'loaded_path' in x}
for x in native[:3]:
    assert x['sha256'] in loaded_hashes, x['member']
assert len(native) == 87
assert len(rows(OUT / 'runtime-gaps-003.jsonl')) == 93
prior = subprocess.check_output(['git', 'show', 'HEAD:tests/fixtures/hg_bfclrt/runtime-gaps-001.jsonl'], cwd=ROOT).decode().splitlines()
current = (OUT / 'runtime-gaps-001.jsonl').read_text().splitlines()
assert prior[11:] == current[11:] and len(prior) == len(current)
for doc in ['registry/w-bfclmem-handler.md', 'registry/w-bfclrt-custody.md']:
    s = (ROOT / doc).read_text()
    if doc.endswith('custody.md'):
        s = s[s.index('## Concrete runtime frontier'):]
    for path, line in re.findall(r'\x60([^\x60\s]+):(\d+)\x60', s):
        p = ROOT / path
        assert p.is_file(), (doc, path)
        assert 0 < int(line) <= len(p.read_text().splitlines()), (doc, path, line)
paths = list(OUT.glob('w-bfclmem-*')) + list(OUT.glob('w_bfclmem*.py')) + list(OUT.glob('licenses/w-bfclmem-*.txt'))
assert all(p.stat().st_size < 1000000 for p in paths)
assert not list(Path('/tmp').glob('bfclmem-*')), 'task-owned temporary directory remains'
print(json.dumps(dict(valid=True, archives=len(archives), archive_members=len(members),
                      dependency_edges=len(edges), active_edges=155, source_modules=len(source_modules),
                      source_edges=len(source_edges), native_members=len(native), exact_grammar_loaded_hashes=True,
                      unchanged_prior_gap_rows=len(current)-11,
                      temporary_directories_remaining=0), sort_keys=True))
