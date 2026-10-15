#!/usr/bin/env python3
"""Read exact wheel custody; never imports BFCL or calls a model.

Run after wheel-only resolve.json exists in --scratch. Payloads stay outside git.
Tags, exercised ABI and build provenance remain distinct.
"""
import argparse
import concurrent.futures
import email
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def norm(s):
    return re.sub(r'[-_.]+', '-', s).lower()


def write(name, rows):
    p = OUT / name
    p.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in rows))
    assert p.stat().st_size < 1000000, p
    print(f'{name}: {len(rows)} records')


def chunks(stem, rows):
    group, size, index = [], 0, 1
    for row in rows:
        n = len(json.dumps(row, sort_keys=True).encode()) + 1
        if size + n > 700000 and group:
            write(f'{stem}-{index:03}.jsonl', group)
            group, size, index = [], 0, index + 1
        group.append(row)
        size += n
    if group:
        write(f'{stem}-{index:03}.jsonl', group)


def collect(scratch):
    from packaging.markers import default_environment
    from packaging.requirements import Requirement
    from packaging.tags import sys_tags, parse_tag
    report = json.loads((scratch / 'resolve.json').read_text())
    env = default_environment()
    env['extra'] = ''
    tags = set(sys_tags())
    archives, members, edges, licenses, native = [], [], [], [], []
    versions = {norm(x['metadata']['name']): x['metadata']['version'] for x in report['install']}

    extras = {name: set() for name in versions}
    changed = True
    while changed:
        changed = False
        for item in report['install']:
            parent = norm(item['metadata']['name'])
            for text in item['metadata'].get('requires_dist', []):
                req = Requirement(text)
                if req.marker is None or any(req.marker.evaluate(dict(env, extra=e)) for e in (extras[parent] or {''})):
                    target = norm(req.name)
                    if target in extras and not req.extras.issubset(extras[target]):
                        extras[target].update(req.extras)
                        changed = True

    def fetch(item):
        m = item['metadata']
        url = 'https://pypi.org/pypi/' + m['name'] + '/' + m['version'] + '/json'
        dest = scratch / 'indexes' / (norm(m['name']) + '-' + m['version'] + '.json')
        dest.parent.mkdir(exist_ok=True)
        if not dest.exists():
            with urllib.request.urlopen(url, timeout=40) as r:
                assert r.status == 200
                dest.write_bytes(r.read())
        return url, dest, json.loads(dest.read_bytes())

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        index = list(pool.map(fetch, report['install']))
    for item, (url, index_path, upstream) in zip(report['install'], index):
        p = Path(urllib.parse.unquote(urllib.parse.urlparse(item['download_info']['url']).path))
        b = p.read_bytes()
        identity = dict(path=str(p), filename=p.name, bytes=len(b), sha256=sha(b))
        m = item['metadata']
        match = [x for x in upstream['urls'] if x['filename'] == p.name]
        assert len(match) == 1
        assert match[0]['digests']['sha256'] == sha(b)
        assert match[0]['size'] == len(b)
        with zipfile.ZipFile(p) as z:
            meta_name = next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))
            wheel_name = meta_name.rsplit('/', 1)[0] + '/WHEEL'
            meta = email.message_from_bytes(z.read(meta_name))
            wheel = email.message_from_bytes(z.read(wheel_name))
            wt = wheel.get_all('Tag', [])
            assert any(tags.intersection(parse_tag(t)) for t in wt), (p, wt)
            archives.append(dict(**identity, name=norm(m['name']), version=m['version'],
                           requested=item['requested'], state='FOUND archive bytes; tag-compatible',
                           requires_python=meta.get('Requires-Python'), wheel_tags=wt,
                           generator=wheel.get('Generator'), wheel_text=z.read(wheel_name).decode(),
                           requires_dist=meta.get_all('Requires-Dist', []),
                           index_url=url, index_path=str(index_path), index_sha256=sha(index_path.read_bytes()),
                           artifact_url=match[0]['url'], upstream_sha256_matches=True,
                           build_provenance='UNKNOWN exact build interpreter/toolchain/source commit; WHEEL Generator is not an attestation',
                           dlopen_frontier='UNKNOWN unexercised runtime branches; DT_NEEDED is not a complete dlopen graph'))
            for req_text in meta.get_all('Requires-Dist', []):
                req = Requirement(req_text)
                active = req.marker is None or any(req.marker.evaluate(dict(env, extra=e)) for e in (extras[norm(m['name'])] or {''}))
                selected = versions.get(norm(req.name))
                satisfies = selected is not None and req.specifier.contains(selected)
                if active:
                    assert satisfies, (m['name'], req_text, selected)
                edges.append(dict(parent=norm(m['name']), parent_version=m['version'],
                                  requirement=req_text, active_selected_extras=active, parent_extras=sorted(extras[norm(m['name'])]), requested_target_extras=sorted(req.extras),
                                  target=norm(req.name), selected_version=selected,
                                  specifier_satisfied=satisfies if active else None,
                                  metadata_member=meta_name, archive_sha256=sha(b)))
            for info in z.infolist():
                if info.is_dir():
                    continue
                content = z.read(info.filename)
                row = dict(archive=p.name, name=norm(m['name']), version=m['version'],
                           member=info.filename, bytes=len(content), sha256=sha(content))
                members.append(row)
                if re.search(r'(^|/)(licen[sc]e[^/]*|notice[^/]*|copying[^/]*|authors[^/]*)$', info.filename, re.I):
                    dest = OUT / 'licenses' / ('w-bfclmem-' + sha(content)[:20] + '.txt')
                    if not dest.exists():
                        dest.write_bytes(content)
                    licenses.append(dict(**row, copy=str(dest.relative_to(ROOT)),
                                         scope='this exact archive member/version; bundled component terms require full text review'))
                if content[:4] == b'\x7fELF':
                    with tempfile.TemporaryDirectory(prefix='bfclmem-elf-') as temp:
                        obj = Path(temp) / Path(info.filename).name
                        obj.write_bytes(content)
                        r = subprocess.run(['readelf', '-h', '-d', '-V', '-n', '-p', '.comment', str(obj)],
                                           text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           env=dict(os.environ, LC_ALL='C'))
                        assert r.returncode == 0, r.stderr
                        native.append(dict(**row, command=['readelf', '-h', '-d', '-V', '-n', '-p', '.comment', '<exact member temp path>'],
                                           output=r.stdout, stderr=r.stderr,
                                           needed=re.findall(r'Shared library: \[(.*?)\]', r.stdout),
                                           build_provenance='UNKNOWN exact builder; compiler string/ELF build ID recorded, not inferred'))
    write('w-bfclmem-archives.jsonl', archives)
    chunks('w-bfclmem-members', members)
    write('w-bfclmem-dependencies.jsonl', edges)
    write('w-bfclmem-licenses.jsonl', licenses)
    chunks('w-bfclmem-native', native)
    write('w-bfclmem-environment.jsonl', [dict(report_environment=report['environment'],
          collector_python=sys.version, collector_executable=sys.executable,
          libc=platform.libc_ver(), marker_environment=env, selected=len(archives),
          active_edges=sum(x['active_selected_extras'] for x in edges),
          missing_active_edges=sum(x['active_selected_extras'] and not x['specifier_satisfied'] for x in edges),
          extras_policy='no optional extras; qwen-agent==0.0.25 and writer-sdk==2.1.0 candidates; numpy==1.26.4; python-dotenv==1.2.2 explicitly supplements observed undeclared qwen import',
          scope='ten missing direct roots plus numpy constraint and observed dotenv runtime supplement; not complete BFCL project lock or scorer execution',
          resolve_sha256=sha((scratch / 'resolve.json').read_bytes()))])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scratch', type=Path, default=Path('/mnt/20t/xubuqiang/hg-work/bfclmem'))
    args = p.parse_args()
    collect(args.scratch)
