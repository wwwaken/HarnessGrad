#!/usr/bin/env python3
"""Compare old installed candidates to exact new archives; record link frontiers."""
import csv
import io
import json
from pathlib import Path
import zipfile

from w_bfclmem import OUT, sha, norm, write, chunks

archives = [json.loads(l) for l in (OUT / 'w-bfclmem-archives.jsonl').open()]
selected = [json.loads(l) for l in (OUT / 'selected-distributions.jsonl').open()]
bindings = []
for ai, archive in enumerate(archives, 1):
    old = [(i, x) for i, x in enumerate(selected, 1)
           if norm(x['name']) == archive['name']]
    if not old:
        continue
    for si, installed in old:
        base = dict(name=archive['name'], archive=archive['filename'], version=archive['version'],
                    archive_evidence=f'tests/fixtures/hg_bfclrt/w-bfclmem-archives.jsonl:{ai}',
                    old_evidence=f'tests/fixtures/hg_bfclrt/selected-distributions.jsonl:{si}')
        if installed.get('version') != archive['version'] or not installed.get('metadata'):
            bindings.append(dict(**base, state='UNKNOWN installed-member binding; version differs or metadata absent',
                                 installed_version=installed.get('version')))
            continue
        # Prior selected metadata is used to locate candidates, never to infer equality.
        metadata = installed['metadata']
        meta_path = Path(metadata['path'] if isinstance(metadata, dict) else metadata)
        site = meta_path.parent.parent
        with zipfile.ZipFile(archive['path']) as z:
            record = next(n for n in z.namelist() if n.endswith('.dist-info/RECORD'))
            for row in csv.reader(io.StringIO(z.read(record).decode())):
                member = row[0]
                p = site / member
                if '..' in Path(member).parts or not p.is_file() or p.is_symlink():
                    bindings.append(dict(**base, member=member, candidate=str(p),
                                         state='UNKNOWN missing/nonregular candidate in named installed site'))
                    continue
                wb, ib = z.read(member), p.read_bytes()
                bindings.append(dict(**base, member=member, candidate=str(p),
                                     archive_bytes=len(wb), installed_bytes=len(ib),
                                     archive_member_sha256=sha(wb), installed_sha256=sha(ib),
                                     equal=wb == ib,
                                     state='FOUND exact byte match' if wb == ib else 'FOUND mismatch; not archive custody'))
chunks('w-bfclmem-bindings', bindings)

native = []
for p in sorted(OUT.glob('w-bfclmem-native-*.jsonl')):
    native.extend((f'tests/fixtures/hg_bfclrt/{p.name}:{i}', json.loads(l))
                  for i, l in enumerate(p.open(), 1))
loaded = [(i, json.loads(l)) for i, l in enumerate((OUT / 'w-bfclmem-smoke.jsonl').open(), 1)
          if 'loaded_path' in l]
links = []
for evidence, member in native:
    for needed in member['needed']:
        bundled = [dict(evidence=e, member=m['member'], sha256=m['sha256'])
                   for e, m in native if Path(m['member']).name == needed]
        observed = [dict(evidence=f'tests/fixtures/hg_bfclrt/w-bfclmem-smoke.jsonl:{i}',
                         path=m['loaded_path'], sha256=m['sha256'])
                    for i, m in loaded if Path(m['loaded_path']).name == needed]
        links.append(dict(parent=evidence, member=member['member'], needed=needed,
                          bundled_candidates=bundled, loaded_basename_candidates=observed,
                          state='FOUND candidates; exact per-parent loader binding UNKNOWN',
                          dlopen='UNKNOWN branches not imported in offline smoke'))
write('w-bfclmem-links.jsonl', links)
write('w-bfclmem-binding-summary.jsonl', [dict(
    compared=sum('equal' in b for b in bindings),
    equal=sum(b.get('equal') is True for b in bindings),
    different=sum(b.get('equal') is False for b in bindings),
    unknown=sum('equal' not in b for b in bindings),
    native_members=len(native), linked_edges=len(links),
    no_candidate_edges=sum(not x['bundled_candidates'] and not x['loaded_basename_candidates'] for x in links),
    scope='prior selected-distributions only, same-version exact wheel members; links are candidate evidence, not complete dlopen or build provenance')])
