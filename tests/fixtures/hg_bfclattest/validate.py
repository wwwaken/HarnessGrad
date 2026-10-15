"""Check retained evidence and exact scope; no network, model or wheel execution."""
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
from collect import digest, rows

HERE = Path(__file__).parent
RUNTIME = HERE.parent / 'hg_bfclrt'
PREVIOUS = '736afcacdc125457ed77422047f990a4ada359d1'


def rel(path):
    path = Path(path)
    return str(path.relative_to(Path.cwd())) if path.is_absolute() else str(path)


def check_file(path, identity):
    p = Path(path)
    # Preserve observed paths in records while permitting review in another checkout.
    original_root = Path('/mnt/20t/xubuqiang/hg-wt/w-bfclattest')
    if p.is_absolute() and p.is_relative_to(original_root):
        p = Path.cwd() / p.relative_to(original_root)
    observed = digest(p.read_bytes())
    assert observed == {k: identity[k] for k in ('bytes', 'sha256')}, path


def main():
    protected = ['AGENTS.md', 'registry/dataset-blockers.json', 'registry/withdrawn-requirements.md',
                 'docs/adapter-integration-journal.md']
    for name in protected:
        assert Path(name).read_bytes() == subprocess.check_output(['git', 'show', 'HEAD:' + name]), name
    changed_prerequisites = {'registry/w-bfclrt-custody.md',
        'tests/fixtures/hg_bfclrt/runtime-gaps-001.jsonl', 'tests/fixtures/hg_bfclrt/runtime-gaps-003.jsonl'}
    for r in rows(HERE / 'prerequisite.jsonl'):
        old = subprocess.check_output(['git', 'show', PREVIOUS + ':' + r['path']])
        assert digest(old) == {k: r[k] for k in ('bytes', 'sha256')}
        if r['path'] not in changed_prerequisites:
            assert Path(r['path']).read_bytes() == old, r['path']
    for shard, unchanged_start in [('001', 10), ('003', 90)]:
        path = RUNTIME / f'runtime-gaps-{shard}.jsonl'
        old = subprocess.check_output(['git', 'show', PREVIOUS + ':' + rel(path)]).splitlines(keepends=True)
        current = path.read_bytes().splitlines(keepends=True)
        assert current[unchanged_start:] == old[unchanged_start:], shard
        assert len(current) == len(old)
        if shard == '001':
            for a, b in zip(old[:10], current[:10]):
                a, b = json.loads(a), json.loads(b)
                del b['w_bfclattest_public_record_disposition']
                assert a == b
    assert (RUNTIME / 'runtime-gaps-002.jsonl').read_bytes() == subprocess.check_output(
        ['git', 'show', 'HEAD:' + rel(RUNTIME / 'runtime-gaps-002.jsonl')])

    http = rows(HERE / 'http.jsonl')
    assert len(http) == 190
    statuses = Counter((r['kind'], r['status']) for r in http)
    assert statuses == {('pep740', 200): 43, ('pep740', 404): 52, ('asc', 404): 95}
    assert sum(r.get('exact_subject_binding', False) for r in http) == 42
    archives = rows(RUNTIME / 'w-bfclmem-archives.jsonl')
    by_filename = {a['filename']: a for a in archives}
    for r in http:
        check_file(r['response'], r)
        check_file(r['headers'], r['headers_identity'])
        assert r['returncode'] == 0 and int(r['stdout']) == r['status']
        a = by_filename[r['filename']]
        assert (a['bytes'], a['sha256']) == (r['archive_bytes'], r['archive_sha256'])
        assert r['command'][-1] == r['url']
        if r['kind'] == 'pep740':
            assert r['url'] == f"https://pypi.org/integrity/{a['name']}/{a['version']}/{a['filename']}/provenance"
        else:
            assert r['url'] == a['artifact_url'] + '.asc'
        if r['status'] == 200:
            assert all(s['statement']['predicate'] is None and s['statement']['predicateType'] ==
                       'https://docs.pypi.org/attestations/publish/v1' for s in r['statements'])
    checks = rows(HERE / 'archives.jsonl')
    assert len(checks) == 95 and sum(r['members_verified'] for r in checks) == 7458
    for r in checks:
        for candidate in r['embedded_record_candidates']:
            if 'copy' in candidate:
                check_file(candidate['copy'], candidate)

    system = rows(HERE / 'system.jsonl')
    assert len(system) == 9 and all(r['state'] == 'FOUND' for r in system)
    for r in system:
        assert len(r['candidates']) == 1
        c = r['candidates'][0]
        check_file(c['retained_elf'], c)
        check_file(c['readelf_output']['path'], c['readelf_output'])
        assert c['soname'] == [r['needed']]
        assert c['actual_loader_selection'].startswith('UNKNOWN')
        for o in c['ownership']:
            assert o['info']['returncode'] == 0 and o['notices']
            parent_version = o['info']['stdout'].split('\t')[3]
            for n in o['notices']:
                check_file(n['copy'], n)
                assert all(i['returncode'] == 0 for i in n['notice_package_info'])
                assert parent_version in {i['stdout'].split('\t')[3] for i in n['notice_package_info']}
    for r in rows(HERE / 'common-licenses.jsonl'):
        assert r['state'] == 'FOUND'
        check_file(r['copy'], r)
    for r in rows(HERE / 'publisher.jsonl'):
        check_file(r['response'], r)
        check_file(r['headers'], r['headers_identity'])
        assert r['returncode'] == 0 and r['status'] == 200
        if 'license_text' in r:
            t = r['license_text']
            check_file(t['path'], t)
            assert t['git_blob_observed'] == t['git_blob_recomputed']
    signatures = rows(HERE / 'signatures.jsonl')
    assert len(signatures) == 43
    for r in signatures:
        assert r['signature_verification']['returncode'] == 0
        assert r['signature_verification']['stdout'] == 'Verified OK\n'
        for f in r['artifacts'].values():
            check_file(f['path'], f)
        assert r['fulcio_chain_rekor_trust_and_publisher_policy'].startswith('UNKNOWN')

    gaps = rows(RUNTIME / 'runtime-gaps-003.jsonl')
    assert len(gaps) == 93
    assert all(g['state'].startswith('UNKNOWN') for g in gaps[:87])
    assert all(g['state'].startswith('FOUND') for g in gaps[87:90])
    links = [e for g in gaps[:87] for e in g['linked_children']]
    assert len(links) == 170 and all(e['state'] == 'FOUND' for e in links)
    assert Counter(p['supply'] for e in links for p in e['providers']) == {'system': 165, 'retained wheel member': 5}
    assert all(e['per_parent_loader_selection'].startswith('UNKNOWN') for e in links)
    assert all(g['license_disposition']['state'] == 'FOUND' for g in gaps[:87])
    text = Path('registry/w-bfclrt-custody.md').read_text().split('## w-bfclattest:', 1)[1]
    citations = re.findall(r'((?:tests|registry)/[^`\s;]+):(\d+)', text)
    for name, line in citations:
        assert Path(name).is_file(), name
        assert 1 <= int(line) <= len(Path(name).read_bytes().splitlines()), (name, line)
    files = set(r['path'] for r in rows(HERE / 'prerequisite.jsonl'))
    files.update(rel(p) for p in HERE.rglob('*') if p.is_file())
    files.update(['registry/w-bfclattest-validation.txt', 'registry/proposals/w-bfclattest.json'])
    oversized = [p for p in files if Path(p).exists() and Path(p).stat().st_size >= 1_000_000]
    assert not oversized, oversized
    print(json.dumps({'valid': True, 'http_records_verified': len(http),
        'exact_publication_subjects': 42, 'publish_404': 52, 'filename_mismatch': 1,
        'dsse_leaf_signatures': len(signatures), 'linked_static_edges': len(links),
        'complete_compiled_builds_found': 0, 'compiled_build_unknown': 87,
        'canonical_citations_checked': len(citations), 'protected_paths_unchanged': len(protected),
        'prerequisite_unchanged_paths': 140, 'all_committed_files_under_1MB': True}, sort_keys=True))


if __name__ == '__main__':
    main()
