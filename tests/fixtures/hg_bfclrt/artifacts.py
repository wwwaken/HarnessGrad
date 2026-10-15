#!/usr/bin/env python3
"""Read local wheel/license and native conda ownership bytes; never install."""
import hashlib
import json
from pathlib import Path
import re
import sys
import tarfile
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import BASE, OUT, identity, norm, write, write_chunks


def retain(name, raw):
    h = hashlib.sha256(raw).hexdigest()
    dest = OUT / 'licenses' / (name + '--' + h[:16] + '.txt')
    dest.parent.mkdir(exist_ok=True)
    if b'\x00' in raw or len(raw) >= 900000:
        return {'sha256': h, 'bytes': len(raw), 'retained_path': None, 'state': 'UNKNOWN text retention'}
    dest.write_bytes(raw)
    return {'sha256': h, 'bytes': len(raw), 'retained_path': str(dest.relative_to(Path.cwd())), 'state': 'FOUND read text'}


selected = {r['name']: r for r in (json.loads(l) for l in
            (OUT / 'selected-distributions.jsonl').read_text().splitlines())}
candidates = [json.loads(l) for f in sorted(OUT.glob('candidates-*.jsonl')) for l in f.read_text().splitlines()]
licenses, members = [], []
seen = set()
for r in candidates:
    if r['kind'] != 'wheel-or-zip-body':
        continue
    name = norm(r['name'])
    if r['version'] != selected.get(name, {}).get('version') and name != 'tree-sitter':
        continue
    if r['sha256'] in seen:
        continue
    seen.add(r['sha256'])
    with zipfile.ZipFile(r['path']) as z:
        for member in z.namelist():
            leaf = Path(member).name.lower()
            if leaf and any(x in leaf for x in ('license', 'licence', 'notice', 'copying', 'copyright')):
                licenses.append({'name': name, 'version': r['version'],
                                 'archive_path': r['path'], 'archive_sha256': r['sha256'],
                                 'member': member, **retain(name + '-archive-' + r['version'], z.read(member))})
            if '.so' in leaf:
                raw = z.read(member)
                members.append({'name': name, 'version': r['version'],
                                'archive_path': r['path'], 'archive_sha256': r['sha256'],
                                'member': member, 'bytes': len(raw),
                                'sha256': hashlib.sha256(raw).hexdigest(),
                                'wheel': r['wheel'], 'exact_build_interpreter': 'UNKNOWN',
                                'linked_library_closure': 'UNKNOWN (archive member not loaded)',
                                'platform_runtime_compatibility': 'UNKNOWN; tag is packaging evidence only'})
write('archive-licenses.jsonl', licenses)
write_chunks('archive-native', members)

# Resolve mapped native files to their installed conda record owners by exact path membership.
elfs = [json.loads(l) for f in sorted(OUT.glob('elf-*.jsonl')) for l in f.read_text().splitlines()]
ownership = {}
extra_licenses = []
for prefix in (BASE, BASE / 'envs/Efficient-MAS'):
    wanted = {str(Path(r['path']).relative_to(prefix)): r['path'] for r in elfs
              if Path(r['path']).is_relative_to(prefix)}
    for meta in sorted((prefix / 'conda-meta').glob('*.json')):
        r = json.loads(meta.read_text())
        hits = sorted(set(r.get('files', [])) & set(wanted))
        if not hits:
            continue
        # Record names/builds are observations, not inferred wheel filenames.
        record = {k: r.get(k) for k in ('name', 'version', 'build', 'build_number', 'subdir', 'fn', 'sha256', 'md5', 'depends', 'license')}
        artifacts = [p for p in (BASE / 'pkgs').glob(r['name'] + '-' + r['version'] + '-' + r['build'] + '.*')
                     if p.is_file() and p.name.endswith(('.conda', '.tar.bz2'))]
        archive_ids = [identity(p) for p in artifacts]
        for hit in hits:
            ownership.setdefault(wanted[hit], []).append({'metadata': identity(meta), 'record': record,
                                                        'observed_local_archives': archive_ids,
                                                        'archive_to_installed_member_binding': 'UNKNOWN (not unpacked)'})
        unpacked = BASE / 'pkgs' / (r['name'] + '-' + r['version'] + '-' + r['build']) / 'info'
        paths = list((unpacked / 'licenses').rglob('*'))
        paths += [unpacked / 'LICENSE.txt', unpacked / 'LICENSE', unpacked / 'COPYING']
        for p in sorted(set(p for p in paths if p.is_file())):
            extra_licenses.append({'name': r['name'], 'version': r['version'], 'record_metadata': str(meta),
                                   'source': identity(p), **retain('native-' + r['name'] + '-' + r['version'], p.read_bytes())})
# Validate selected native bytes against the actual locally cached conda package members.
# Metadata path membership alone can be stale after a pip upgrade.
import zstandard
archive_jobs = {}
for installed, owners in ownership.items():
    for owner in owners:
        for archive in owner['observed_local_archives']:
            archive_jobs.setdefault(archive['path'], []).append((installed, owner))
for archive, jobs in sorted(archive_jobs.items()):
    wants = {}
    for installed, owner in jobs:
        meta = Path(owner['metadata']['path'])
        prefix = meta.parent.parent
        wants[str(Path(installed).relative_to(prefix))] = (installed, owner)
    results = {}

    def scan_tar(stream):
        with tarfile.open(fileobj=stream, mode='r|') as tar:
            for member in tar:
                key = member.name.removeprefix('./')
                if key in wants and member.isfile():
                    f = tar.extractfile(member)
                    h = hashlib.sha256()
                    for b in iter(lambda: f.read(1024 * 1024), b''):
                        h.update(b)
                    results[key] = {'member': member.name, 'bytes': member.size, 'sha256': h.hexdigest()}

    if archive.endswith('.conda'):
        with zipfile.ZipFile(archive) as z:
            for part in z.namelist():
                if part.startswith('pkg-') and part.endswith('.tar.zst'):
                    with z.open(part) as raw, zstandard.ZstdDecompressor().stream_reader(raw) as stream:
                        scan_tar(stream)
    elif archive.endswith('.tar.bz2'):
        import bz2
        with bz2.open(archive, 'rb') as stream:
            scan_tar(stream)
    for key, (installed, owner) in wants.items():
        match = results.get(key)
        if match:
            installed_id = identity(installed)
            owner['archive_to_installed_member_binding'] = {
                'archive': archive, **match,
                'installed_sha256': installed_id['sha256'],
                'matches': installed_id['sha256'] == match['sha256']}
        else:
            owner['archive_to_installed_member_binding'] = 'UNKNOWN; requested member not observed in stream'
write('native-owners.jsonl', [{'path': r['path'], 'owners': ownership.get(r['path'], []),
                              'state': 'FOUND exact installed conda-record path membership' if r['path'] in ownership else
                              'UNKNOWN conda owner; see distribution RECORD/ELF/smoke evidence'} for r in elfs])

# System-native notice paths are enumerated, not assumed to prove ownership of conda builds.
scope = []
for package in ('libc6', 'libgcc-s1', 'libstdc++6', 'zlib1g', 'libbz2-1.0', 'liblzma5', 'libexpat1',
                'libffi8', 'libuuid1', 'libssl3', 'libtinfo6', 'libncursesw6'):
    p = Path('/usr/share/doc') / package / 'copyright'
    scope.append({'package': package, 'path': str(p), 'exists': p.is_file(), 'scope': 'exact named notice path'})
    if p.is_file():
        extra_licenses.append({'name': 'system-' + package, 'source': identity(p),
                               'binary_binding': 'UNKNOWN; named system package notice, not conda license',
                               **retain('system-' + package, p.read_bytes())})
write('native-license-search.jsonl', scope)
write('native-licenses.jsonl', extra_licenses)
