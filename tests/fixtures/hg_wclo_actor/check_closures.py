"""Validate manifest coverage, literal source locators and current bytes; no scorer imports."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 << 20), b''):
            result.update(block)
    return result.hexdigest()


def fixture_files():
    return sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'SHA256SUMS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-sums', action='store_true')
    parser.add_argument('--external-bytes', action='store_true', help='Also rehash external local data/runtime files')
    args = parser.parse_args()
    files = fixture_files()
    assert not any('__pycache__' in p.parts or p.suffix == '.pyc' for p in files)
    sums = ''.join(digest(p) + '  ' + str(p.relative_to(OUT)) + '\n' for p in files)
    if args.write_sums:
        (OUT / 'SHA256SUMS').write_text(sums)
    else:
        assert (OUT / 'SHA256SUMS').read_text() == sums, 'fixture hashes/file coverage mismatch'

    checked, missing, locators = {}, set(), set()

    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
        if not isinstance(value, dict):
            return
        if {'path', 'exists', 'location'} <= set(value):
            path = Path(value['path'])
            if value['location'] == 'checkout':
                assert not path.is_absolute() and '..' not in path.parts
                path = ROOT / path
            else:
                assert path.is_absolute()
            if value['exists']:
                assert re.fullmatch('[0-9a-f]{64}', value['sha256'])
                if value['location'] == 'checkout' or args.external_bytes:
                    assert path.is_file(), path
                    if str(path) not in checked:
                        checked[str(path)] = digest(path)
                    assert checked[str(path)] == value['sha256'], str(path) + ': byte drift'
                    assert path.stat().st_size == value['bytes'], str(path) + ': size drift'
                if 'line' in value and 'locator' in value:
                    lines = path.read_text().splitlines()
                    assert lines[value['line'] - 1] == value['locator'], str(path) + ': stale line'
                    locators.add((str(path), value['line']))
                if 'definitions' in value or 'imports' in value:
                    lines = path.read_text().splitlines()
                    for source_ref in value.get('definitions', []) + value.get('imports', []):
                        assert lines[source_ref['line'] - 1] == source_ref['locator'], str(path) + ': stale AST locator'
                        locators.add((str(path), source_ref['line']))
            else:
                missing.add(str(path))
        for subvalue in value.values():
            walk(subvalue)

    for path in files:
        if path.suffix == '.json':
            walk(json.loads(path.read_text()))
    scope = json.loads((OUT / 'scope.json').read_text())
    assert len(scope['datasets']) == 19 and len(scope['qa_command']) == 12 and len(scope['native_command']) == 7
    records = list((OUT / 'datasets').glob('*.json'))
    assert sorted(p.stem for p in records) == scope['datasets']
    for path in records:
        record = json.loads(path.read_text())
        assert record['executed_isolation_class_from_survey'] == 'actor-workdir'
        assert record['class_evidence_kind'] == 'source route; no new executed observation'
        assert record['entry_points'] and record['not_pinned_or_not_established']
        gold = json.loads((ROOT / record['gold_expected_data']['path']).read_text())
        assert gold['artifacts'] and not gold['missing_patterns'], record['dataset']
        assert all(a['exists'] for a in gold['artifacts']), record['dataset']
        assert record['survey_row'] in (ROOT / 'reports/w-shared-topology-survey.md').read_text()
        for binding in gold.get('archive_member_bindings', []):
            assert any(c['equals_local_artifact'] for c in binding.get('candidates', [])), binding
            artifact = next(a for a in gold['artifacts'] if a['path'] == binding['artifact'])
            assert any(c['sha256'] == artifact['sha256'] for c in binding['candidates'])
    # Registry changes may append observations/evidence only. No local/historical
    # requirement or shared next_action/status/reference may be relaxed by inspection.
    import subprocess
    baseline = json.loads(subprocess.check_output(
        ['git', 'show', scope['source_git_commit'] + ':docs/dataset-blockers.json'], cwd=ROOT, text=True))
    current = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
    assert current['datasets'] == baseline['datasets'], 'dataset/historical registry drift'
    for old, new in zip(baseline['shared_blockers'], current['shared_blockers'], strict=True):
        if old['id'] == 'scorer-offline-closure':
            assert new['observed'].startswith(old['observed'])
            assert new['evidence'][:len(old['evidence'])] == old['evidence']
            assert {k: v for k, v in new.items() if k not in ('observed', 'evidence')} == {
                k: v for k, v in old.items() if k not in ('observed', 'evidence')}
        else:
            assert new == old
    assert current['review'] == baseline['review']
    print(f'PASS: {len(records)} dataset records (12 QA + 7 native), all actor-workdir, all retain incomplete-closure findings')
    print(f'PASS: {len(files)} fixture files covered by SHA256SUMS; {len(locators)} exact source path/line/locator records')
    print(f'PASS: {len(checked)} unique files rehashed; external-bytes={args.external_bytes}; {len(missing)} explicitly missing file records retained')
    print('PASS: shared blocker retained; next_action/status, all dataset/local requirements and historical records unchanged')


if __name__ == '__main__':
    main()
