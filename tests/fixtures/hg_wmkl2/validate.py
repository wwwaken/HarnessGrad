"""Audit raw evidence, imports, retained bytes and metadata consistency without scoring."""
import ast
import json
from pathlib import Path
import re
from common import HERE, ROOT, digest

read = lambda name: json.loads((HERE / name).read_text())
for name in ['network.json', 'retry-network.json']:
    net = read('offline/' + name)
    assert net['errno'] == 101 and [n for _, n in net['interfaces']] == ['lo']
    assert not net['routes'].splitlines()[1:]
for label in ['host-original-pair', 'fresh-original-pair']:
    receipt = read('offline/' + label + '.receipt.json')
    versions = read('offline/' + label + '.stdout.txt')
    assert receipt['exit_code'] == 1
    assert versions['gensim'] == '4.3.2' and versions['scipy'] == '1.13.1'
    stderr = (HERE / ('offline/' + label + '.stderr.txt')).read_text()
    assert 'from scipy.linalg import get_blas_funcs, triu' in stderr
    assert re.search(r"ImportError: cannot import name 'triu' from 'scipy.linalg' \(.*/scipy/linalg/__init__\.py\)", stderr)
for name in ['gensim', 'tensorflow', 'xgboost']:
    assert read('offline/negative-' + name + '.receipt.json')['exit_code'] == 1
    assert f"No module named '{name}'" in (HERE / ('offline/negative-' + name + '.stderr.txt')).read_text()
for label in ['conda-install', 'original-profile-install', 'local-resolver', 'additions-install',
              'retry-additions-install', 'retry-completed-imports', 'exact-named-imports', 'installed-distributions']:
    assert read('offline/' + label + '.receipt.json')['exit_code'] == 0, label
assert read('offline/completed-imports.receipt.json')['exit_code'] == 1  # Initial failure remains.
assert read('offline-launch.receipt.json')['exit_code'] == 1
assert read('offline-launch-retry.receipt.json')['exit_code'] == 1
assert read('retry-launch.receipt.json')['exit_code'] == 0
result = read('offline/retry-completed-imports.stdout.txt')
assert all(v['ok'] for v in result['imports'].values())
assert {'gensim', 'tensorflow', 'xgboost.sklearn', 'tensorflow.keras.models', 'tensorflow.keras.layers'} <= set(result['imports'])
assert all(Path(v['path']).is_relative_to(Path(result['prefix'])) for v in result['imports'].values())
assert all(Path(v).is_relative_to(Path(result['prefix'])) for v in result['native_providers'])
expected = {'gensim': '4.3.2', 'scipy': '1.12.0', 'numpy': '1.26.4', 'tensorflow-cpu': '2.16.1', 'xgboost': '2.0.3'}
assert result['versions'] == expected
actual = {r['name'].lower().replace('_', '-'): r['version'] for r in read('offline/installed-distributions.stdout.txt')}
for line in (HERE.parent / 'hg_wmkl/ds1000.lock').read_text().splitlines():
    name, version = line.split(' --hash=')[0].split('==')
    assert actual[name.lower().replace('_', '-')] == ('1.12.0' if name.lower() == 'scipy' else version), name
named = read('offline/exact-named-imports.stdout.txt')
assert named['no_constructors_or_task_code_executed']
assert len(named['exact_import_statements_passed']) == 6
assert named['checked_requirement_count'] == len(named['selected_dependency_checks']) > 0
source = read('source-audit.json')
assert source['summary']['released_rows'] - source['summary']['excluded_rows'] == source['summary']['offered_rows']
for root, stats in source['summary']['imports'].items():
    assert stats['offered_rows'] == 0, root
for item in source['sources']:
    assert digest(Path(item['path'])) == item['sha256']
    copy = ROOT / item['numbered_copy']
    lines = copy.read_text().splitlines()
    assert [line.split('\t', 1)[1] for line in lines] == Path(item['path']).read_text().splitlines()
rows = [json.loads(line) for line in Path(source['contexts_path']).read_text().splitlines() if line.strip()]
assert digest(Path(source['contexts_path'])) == source['contexts_sha256']
for item in source['imports']:
    assert rows[item['row_index']]['code_context'].splitlines()[item['context_line'] - 1] == item['text']
for row in read('context-flow-sites.json')['rows']:
    for site in row['sites']:
        assert rows[row['row_index']]['code_context'].splitlines()[site['context_line']-1] == site['text']
# Every reported import site is in the census; hidden string row706 is included.
assert any(i['row_index'] == 706 and i['root'] == 'tensorflow' and i['kind'] == 'constant-string' for i in source['imports'])
for item in read('installed-source-hashes.json'):
    assert digest(Path(item['path'])) == item['sha256']
for item in read('selected-wheel-metadata.json'):
    assert digest(Path(item['path'])) == item['sha256']
    assert actual[item['name'].lower().replace('_', '-')] == item['version']
coverage = read('coverage.json')
assert coverage['complete_nonempty_count'] == len(coverage['complete_nonempty'])
assert coverage['no_third_party_payload_count'] == len(coverage['no_third_party_payload_required'])
assert coverage['partial_count'] == len(coverage['partial']) == 0
assert len(set(coverage['complete_nonempty'] + coverage['no_third_party_payload_required'])) == coverage['inventory_count']
print(json.dumps({'evidence_valid': True, 'versions': expected, 'successful_module_probes': len(result['imports']),
                  'exact_context_import_statements': len(named['exact_import_statements_passed']),
                  'selected_active_metadata_checks': named['checked_requirement_count'],
                  'source_summary': source['summary'], 'coverage': coverage}, indent=2))
