#!/usr/bin/env python3
"""Offline byte custody verification; does not import generators or invoke scorers."""
import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parent


def sha(body):
    return hashlib.sha256(body).hexdigest()


def blob(body):
    return hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()


def load(name):
    return json.loads((ROOT / name).read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pool', type=Path, default=ROOT.parent / 'installed/reasoning_gym.jsonl')
    args = parser.parse_args()
    response_count = 0
    for receipt_path in sorted((ROOT / 'responses').glob('*.receipt.json')):
        receipt = json.loads(receipt_path.read_bytes())
        stem = receipt_path.name.removesuffix('.receipt.json')
        body = (receipt_path.parent / (stem + '.body')).read_bytes()
        headers = (receipt_path.parent / (stem + '.headers')).read_bytes()
        assert sha(body) == receipt['body_sha256']
        assert len(body) == receipt['body_size']
        assert sha(headers) == receipt['headers_sha256']
        response_count += 1
    pypi = load('responses/pypi-0.1.25.body')
    for kind in ('bdist_wheel', 'sdist'):
        artifact = next(item for item in pypi['urls'] if item['packagetype'] == kind)
        body = (ROOT / f'responses/pypi-{kind}.body').read_bytes()
        assert sha(body) == artifact['digests']['sha256']
        assert len(body) == artifact['size']
    tag = load('responses/github-tag.body')
    commit = load('responses/github-commit.body')
    tree = load('responses/github-tree.body')
    assert tag['object']['sha'] == commit['sha'] == '21e6d2a9a581b3e11aafe711abfd37402f8482d5'
    assert tag['object']['type'] == 'commit'
    assert commit['tree']['sha'] == tree['sha']
    assert tree['truncated'] is False
    git_members = {item['path']: item for item in tree['tree']}
    installed = load('installed-members.json')
    installed_by_name = {item['path']: item for item in installed['members']}
    package_matches = 0
    installed_matches = 0
    with zipfile.ZipFile(ROOT / 'responses/pypi-bdist_wheel.body') as wheel, tarfile.open(ROOT / 'responses/pypi-sdist.body') as sdist:
        sdist_members = {item.name: item for item in sdist.getmembers()}
        record = csv.reader(io.StringIO(wheel.read('reasoning_gym-0.1.25.dist-info/RECORD').decode()))
        record_checked = 0
        for name, digest, size in record:
            if digest:
                algo, encoded = digest.split('=', 1)
                assert algo == 'sha256'
                body = wheel.read(name)
                assert base64.urlsafe_b64encode(hashlib.sha256(body).digest()).rstrip(b'=').decode() == encoded
                assert len(body) == int(size)
                record_checked += 1
        assert set(wheel.namelist()) == set(installed_by_name)
        for name in wheel.namelist():
            body = wheel.read(name)
            member = installed_by_name[name]
            assert member['wheel_sha256'] == sha(body) and member['wheel_size'] == len(body)
            assert member['byte_equality'] == (member['installed_sha256'] == sha(body) and member['installed_size'] == len(body))
            installed_matches += member['byte_equality']
            if name.startswith('reasoning_gym/'):
                assert git_members[name]['type'] == 'blob'
                assert git_members[name]['sha'] == blob(body)
                assert git_members[name]['size'] == len(body)
                sdist_body = sdist.extractfile(sdist_members['reasoning_gym-0.1.25/' + name]).read()
                assert body == sdist_body
                assert member['byte_equality']
                package_matches += 1
    assert installed_matches == 204 and package_matches == 200 and record_checked == 204
    assert installed['extra_non_pycache_package_files'] == []
    assert sha((ROOT / 'installed-RECORD.body').read_bytes()) == installed['installed_record_sha256']
    pool_bytes = args.pool.read_bytes()
    assert sha(pool_bytes) == 'c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177'
    rows = [json.loads(line) for line in pool_bytes.splitlines() if line.strip()]
    families = sorted({row['family'] for row in rows})
    assert len(families) == 89 and len(rows) == 1780
    assert [(row['family'], row['index']) for row in rows] == [(family, i) for family in families for i in range(20)]
    assert all(str(row['entry'].get('answer', '')).strip() for row in rows)
    eval_ids = [f'reasoning_gym/eval/{i}' for i in range(len(rows)) if hashlib.sha256(f'reasoning_gym/eval/{i}'.encode()).digest()[0] % 3 == 0]
    assert len(eval_ids) == 564
    attempts = load('attempts.json')
    for attempt in attempts['attempts']:
        assert attempt['exit_code'] == 1
        for field in ('script', 'stdout', 'stderr'):
            filename = attempt['script_snapshot'] if field == 'script' else attempt[field]
            assert sha((ROOT / filename).read_bytes()) == attempt[field + '_sha256']
    final = load('attempt-5.stdout.txt')
    assert final['regenerate_script_sha256'] == sha((ROOT / 'attempt-5-script.py').read_bytes())
    assert final['regenerate_script_sha256'] == sha((ROOT / 'regenerate.py').read_bytes())
    assert final['installed_pool_sha256'] == sha(pool_bytes)
    assert final['installed_pool_size'] == len(pool_bytes)
    assert final['seed'] == 20261008 and final['family_count'] == 89
    assert final['items_per_family'] == 20 and final['row_count'] == len(rows)
    assert final['whole_pool_byte_equality'] is False
    assert final['generated_sha256'] != final['installed_pool_sha256']
    assert final['scratch_cleanup_complete'] is True
    assert len(final['mismatching_coordinates']) == 84
    coords = {(row['family'], row['index']) for row in rows}
    assert all((row['family'], row['index']) in coords for row in final['mismatching_coordinates'])
    assert attempts['final_result']['successful_generator_pool_binding'] is False
    recovery = load('attempt-4-cleanup-recovery.json')
    assert recovery['cleanup_complete'] is True
    assert len(recovery['observed_files']) == 1
    assert sha((ROOT / 'attempt-4-scratch-file.body').read_bytes()) == recovery['observed_files'][0]['sha256']
    print(f'PASS responses={response_count}; PyPI wheel/sdist hashes+sizes; wheel RECORD={record_checked}; package members matching installed+sdist+Git commit={package_matches}; installed wheel members matching={installed_matches}/205 (RECORD rewrite only)')
    print(f'PASS installed pool bytes={len(pool_bytes)} sha256={sha(pool_bytes)} rows={len(rows)} families={len(families)} x20; nonempty-answer structure; derived platform train=1216 eval={len(eval_ids)}')
    print('PASS preserved attempt scripts/stdout/stderr; final completed regeneration receipt reports false equality, 84 mismatching rows in 6 families, cleanup complete; package/seed-to-pool reproduction remains OPEN')
    print('OPEN behavioral eligibility/offline scorer, transitive dependency custody, pristine verifier/runtime and run-selected manifest; static derived splits are not pilot selection.')


if __name__ == '__main__':
    main()
