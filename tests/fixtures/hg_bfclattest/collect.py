"""Bounded, read-only BFCL archive/public-record and static-provider inspection.

No imported wheel code, model, dynamic loader, install, or scorer is executed.
Run from the repository root; input is the committed w-bfclmem packet.
"""
import argparse
import base64
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.request
import zipfile

HERE = Path(__file__).parent
SCRATCH = Path('/mnt/20t/xubuqiang/hg-work/bfclattest')
INPUT = HERE.parent / 'hg_bfclrt'


def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines()]


def write_rows(path, records):
    Path(path).write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in records))


def digest(data):
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def command(argv):
    p = subprocess.run(argv, text=True, capture_output=True, check=False)
    return {'command': argv, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}


def fetch(item):
    a, kind = item
    if kind == 'pep740':
        url = f"https://pypi.org/integrity/{a['name']}/{a['version']}/{a['filename']}/provenance"
    else:
        url = a['artifact_url'] + '.asc'
    # This exact command is also usable individually, without this collector.
    cmd = ['curl', '--silent', '--show-error', '--location', '--max-time', '40',
           '--dump-header', '<headers_path>', '--output', '<body_path>',
           '--write-out', '%{http_code}', url]
    key = f"{a['name']}-{a['version']}-{kind}"
    folder = HERE / 'http'
    folder.mkdir(exist_ok=True)
    body_path, headers_path = folder / (key + '.raw'), folder / (key + '.headers')
    cmd[cmd.index('<headers_path>')] = str(headers_path)
    cmd[cmd.index('<body_path>')] = str(body_path)
    result = command(cmd)
    b = body_path.read_bytes() if body_path.exists() else b''
    record = {'name': a['name'], 'version': a['version'], 'filename': a['filename'],
              'archive_sha256': a['sha256'], 'archive_bytes': a['bytes'],
              'kind': kind, 'url': url, 'response': str(body_path), **digest(b),
              **result, 'headers': str(headers_path)}
    if headers_path.exists():
        record['headers_identity'] = digest(headers_path.read_bytes())
    record['status'] = int(result['stdout']) if result['stdout'].isdigit() else None
    record['state'] = ('FOUND' if record['status'] == 200 else
                       'ABSENT' if record['status'] == 404 else 'UNKNOWN')
    if kind == 'pep740' and record['status'] == 200:
        provenance = json.loads(b)
        statements = []
        for bundle in provenance.get('attestation_bundles', []):
            for att in bundle.get('attestations', []):
                statement_raw = base64.b64decode(att['envelope']['statement'])
                statement = json.loads(statement_raw)
                subjects = statement.get('subject', [])
                statements.append({'publisher': bundle.get('publisher'),
                    'statement': statement, 'statement_identity': digest(statement_raw),
                    'subject_matches': [s for s in subjects
                        if s.get('name') == a['filename'] and
                        s.get('digest', {}).get('sha256') == a['sha256']],
                    'cryptographic_verification': 'UNKNOWN not performed'})
        record['statements'] = statements
        record['exact_subject_binding'] = any(s['subject_matches'] for s in statements)
    return record


def collect_http():
    archives = rows(INPUT / 'w-bfclmem-archives.jsonl')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(fetch, [(a, k) for a in archives for k in ('pep740', 'asc')]))
    write_rows(HERE / 'http.jsonl', records)
    from collections import Counter
    print(json.dumps({'requests': len(records), 'statuses': dict(Counter(
        f"{r['kind']}:{r['status']}" for r in records)),
        'exact_subject_bindings': sum(r.get('exact_subject_binding', False) for r in records)}, sort_keys=True))


def inspect_archives():
    archives = rows(INPUT / 'w-bfclmem-archives.jsonl')
    previous = { (r['archive'], r['member']): r
        for p in sorted(INPUT.glob('w-bfclmem-members-*.jsonl')) for r in rows(p)}
    records = []
    for a in archives:
        path = Path(a['path'])
        identity = digest(path.read_bytes())
        assert identity == {k: a[k] for k in ('bytes', 'sha256')}, a['filename']
        count = 0
        with zipfile.ZipFile(path) as z:
            candidates = []
            for member in z.namelist():
                if member.endswith('/'):
                    continue
                data = z.read(member)
                ident = digest(data)
                old = previous[(a['filename'], member)]
                assert ident == {k: old[k] for k in ('bytes', 'sha256')}, member
                count += 1
                if re.search(r'(attest|provenance|build[-_]details|sbom|RECORD\.(jws|p7s)$)', member, re.I):
                    candidate = {'member': member, **ident}
                    if '/sboms/' in member:
                        dest = HERE / 'embedded' / (ident['sha256'] + '.json')
                        dest.parent.mkdir(exist_ok=True)
                        dest.write_bytes(data)
                        candidate['copy'] = str(dest)
                    candidates.append(candidate)
            record = {'path': str(path), 'filename': a['filename'], **identity,
                'state': 'FOUND', 'all_previous_member_identities_equal': True,
                'members_verified': count, 'embedded_record_candidates': candidates,
                'embedded_search_regex': r'(attest|provenance|build[-_]details|sbom|RECORD\.(jws|p7s)$)',
                'command': 'TMPDIR=/tmp/bfclattest-tmp python3 -B tests/fixtures/hg_bfclattest/collect.py archives'}
            records.append(record)
    write_rows(HERE / 'archives.jsonl', records)
    print(json.dumps({'archives_verified': len(records), 'members_verified': sum(r['members_verified'] for r in records),
        'embedded_candidate_count': sum(len(r['embedded_record_candidates']) for r in records)}, sort_keys=True))


def inspect_system():
    needed = sorted({r['needed'] for r in rows(INPUT / 'w-bfclmem-links.jsonl')
                     if not r['bundled_candidates']})
    cache = command(['/sbin/ldconfig', '-p'])
    write_rows(HERE / 'ldconfig.jsonl', [cache])
    records = []
    for name in needed:
        paths = sorted({line.split(' => ')[1] for line in cache['stdout'].splitlines()
                        if line.lstrip().startswith(name + ' ') and '(libc6,x86-64' in line})
        candidates = []
        for path in paths:
            real = str(Path(path).resolve())
            data = Path(real).read_bytes()
            # Keep binary evidence outside git; system paths can later change.
            retained = SCRATCH / 'system' / (hashlib.sha256(data).hexdigest() + '.elf')
            retained.parent.mkdir(exist_ok=True)
            retained.write_bytes(data)
            readelf = command(['readelf', '-h', '-d', '-V', '-n', real])
            raw = SCRATCH / 'system' / (Path(real).name + '.readelf.txt')
            raw.parent.mkdir(exist_ok=True)
            raw.write_text(readelf['stdout'])
            owner = command(['dpkg-query', '-S', path, real])
            packages = sorted({pkg for line in owner['stdout'].splitlines() if ': ' in line
                               for pkg in line.rsplit(': ', 1)[0].split(', ')})
            ownership = []
            for package in packages:
                info = command(['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\t${Status}\n', package])
                listing = command(['dpkg-query', '-L', package])
                license_paths = sorted({s for s in listing['stdout'].splitlines() if s.endswith('/copyright')}
                    | {f"/usr/share/doc/{package.split(':')[0]}/copyright"})
                notices = []
                for license_path in license_paths:
                    license_file = Path(license_path)
                    if not license_file.is_file():
                        continue
                    b = license_file.read_bytes()
                    dest = HERE / 'licenses' / (hashlib.sha256(b).hexdigest() + '.txt')
                    dest.parent.mkdir(exist_ok=True)
                    dest.write_bytes(b)
                    notice_owner = command(['dpkg-query', '-S', str(license_file.resolve())])
                    notice_packages = sorted({pkg for s in notice_owner['stdout'].splitlines() if ': ' in s
                        for pkg in s.rsplit(': ', 1)[0].split(', ')})
                    notice_info = [command(['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\t${Status}\n', pkg]) for pkg in notice_packages]
                    notices.append({'path': license_path, 'realpath': str(license_file.resolve()),
                        'copy': str(dest), **digest(b), 'notice_owner': notice_owner, 'notice_package_info': notice_info,
                        'scope': 'system binary package copyright; not bundled in the selected wheel'})
                ownership.append({'package': package, 'info': info, 'listing': listing, 'notices': notices})
            candidates.append({'path': path, 'realpath': real, **digest(data),
                'soname': re.findall(r'\(SONAME\).*?\[(.*?)\]', readelf['stdout']),
                'readelf': {k:v for k,v in readelf.items() if k != 'stdout'},
                'readelf_output': {'path': str(raw), **digest(raw.read_bytes())},
                'owner_query': owner, 'ownership': ownership,
                'static_identity_only': True, 'actual_loader_selection': 'UNKNOWN not executed',
                'retained_elf': str(retained), 'retention': 'ELF raw bytes copied outside git at retained_elf'})
        records.append({'needed': name, 'state': 'FOUND' if candidates else 'ABSENT',
                        'scope': '/sbin/ldconfig -p exact SONAME rows whose ABI tuple starts (libc6,x86-64',
                        'candidates': candidates})
    write_rows(HERE / 'system.jsonl', records)
    print(json.dumps({'system_names': len(records), 'found': sum(bool(r['candidates']) for r in records),
        'candidate_files': sum(len(r['candidates']) for r in records)}, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=['http', 'archives', 'system'])
    args = p.parse_args()
    {'http': collect_http, 'archives': inspect_archives, 'system': inspect_system}[args.phase]()
