"""Offline inventory review; consumes source/metadata only, never dataset rows."""
import collections
import fnmatch
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / 'responses' / (name + '.body')).read_bytes())


def repeated_json_object_keys(name):
    duplicates = []

    def pairs_hook(pairs):
        duplicates.extend(repeated(key for key, _ in pairs))
        return dict(pairs)

    json.loads((ROOT / 'responses' / (name + '.body')).read_bytes(),
               object_pairs_hook=pairs_hook)
    return duplicates


def repeated(values):
    return sorted(key for key, count in collections.Counter(values).items() if count > 1)


def schema_fields(features, prefix=''):
    fields = []
    for feature in features:
        path = prefix + feature['name']
        fields.append(path)
        for kind in ['struct', 'sequence']:
            children = feature.get(kind)
            if isinstance(children, list):
                fields.extend(schema_fields(children, path + '.'))
    return fields


def analyze():
    revision = read('hub-revision-final')
    tree = read('hub-tree-final')
    card = revision['cardData']
    configs, infos = card['configs'], card['dataset_info']
    files = [item for item in tree if item['type'] == 'file']
    directories = sorted(item['path'] for item in tree if item['type'] == 'directory')
    routes = {}
    for cfg in configs:
        routes[cfg['config_name']] = {}
        for split in cfg['data_files']:
            routes[cfg['config_name']][split['split']] = sorted(
                f['path'] for f in files if fnmatch.fnmatchcase(f['path'], split['path']))
    assignments = [p for c in routes.values() for paths in c.values() for p in paths]
    schemas = {i['config_name']: schema_fields(i['features']) for i in infos}
    groups = {}
    for field in ['oid', 'lfs.oid']:
        by_id = collections.defaultdict(list)
        for f in files:
            value = f['oid'] if field == 'oid' else f.get('lfs', {}).get('oid')
            if value is not None:
                by_id[value].append(f['path'])
        groups[field] = {k: v for k, v in sorted(by_id.items()) if len(v) > 1}
    counts = {i['config_name']: {s['name']: s.get('num_examples') for s in i['splits']}
              for i in infos}
    unbound = sorted(set(counts) - set(routes))
    viewer = read('viewer-info-proxy-retry')
    result = {
        'export_revision': revision['sha'],
        'scope': 'Every entry in hub-tree-final.body, every cardData.dataset_info schema/split, '
                 'every cardData.configs data_files entry and every siblings entry in '
                 'hub-revision-final.body; no payload bytes or row IDs.',
        'tree_entry_count': len(tree), 'directory_count': len(directories),
        'file_count': len(files), 'parquet_count': sum(f['path'].endswith('.parquet') for f in files),
        'directories': directories, 'routed_config_count': len(routes),
        'dataset_info_config_count': len(infos), 'info_without_routes_or_directories': unbound,
        'counts': counts, 'schemas': schemas,
        'missing_fields_all_schemas': {
            name: all(not any(p.rsplit('.', 1)[-1].replace('_', '').lower() == name.lower()
                              for p in paths) for paths in schemas.values())
            for name in ['HumanAnswers', 'Domain', 'VerifiedEval',
                         'QuestionPartOfVerifiedEval', 'DocPartOfVerifiedEval']},
        'routes': routes,
        'duplicate_tree_paths': repeated(i['path'] for i in tree),
        'duplicate_json_object_keys': {
            n: repeated_json_object_keys(n) for n in [
                'hub-tree-final', 'hub-revision-final', 'viewer-info-proxy-retry']},
        'duplicate_sibling_paths': repeated(s['rfilename'] for s in revision['siblings']),
        'sibling_file_inventory_equal': sorted(s['rfilename'] for s in revision['siblings'])
                                        == sorted(f['path'] for f in files),
        'duplicate_dataset_info_config_names': repeated(i['config_name'] for i in infos),
        'duplicate_route_config_names': repeated(i['config_name'] for i in configs),
        'duplicate_split_names': {i['config_name']: repeated(s['name'] for s in i['splits'])
                                  for i in infos if repeated(s['name'] for s in i['splits'])},
        'duplicate_feature_paths': {c: repeated(paths) for c, paths in schemas.items()
                                    if repeated(paths)},
        'multiply_assigned_payload_paths': repeated(assignments),
        'unassigned_parquet_paths': sorted(f['path'] for f in files
                                          if f['path'].endswith('.parquet')
                                          and f['path'] not in assignments),
        'repeated_file_identities': groups,
        'repeated_directory_oids': repeated(i['oid'] for i in tree if i['type'] == 'directory'),
        'root_nonpayload_files': sorted(f['path'] for f in files if '/' not in f['path']),
        'rc_web_plus_wikipedia_count_equals_rc': {
            s: counts['rc.web'][s] + counts['rc.wikipedia'][s] == counts['rc'][s]
            for s in ['train', 'validation', 'test']},
        'context_no_context_declared_counts_equal': {
            c: counts[c] == counts[c + '.nocontext']
            for c in ['rc', 'rc.web', 'rc.wikipedia', 'unfiltered']},
        'viewer_configs_equal_routed_configs': sorted(viewer['dataset_info']) == sorted(routes),
        'viewer_pending': viewer['pending'], 'viewer_failed': viewer['failed'],
        'viewer_partial': viewer['partial'],
        'row_duplicate_incidence': 'UNKNOWN: row IDs and payloads not accessed',
        'human_answer_preservation_or_redundancy': 'UNKNOWN: schema omission cannot settle values',
        'official_numeric_denominator': 'UNKNOWN: no selected Domain/VerifiedEval key inventory',
        'duplicate_route_split_names': {c['config_name']: repeated(s['split'] for s in c['data_files'])
                                       for c in configs if repeated(s['split'] for s in c['data_files'])},
    }
    return result


def verify_responses():
    count = failures = 0
    for receipt_path in sorted((ROOT / 'responses').glob('*.receipt.json')):
        record = json.loads(receipt_path.read_text())
        if 'body' not in record:
            assert 'error' in record, receipt_path
            failures += 1
            continue
        body = (ROOT / record['body']).read_bytes()
        assert len(body) == record['bytes'] <= 950_000, receipt_path
        assert hashlib.sha256(body).hexdigest() == record['sha256'], receipt_path
        if 'view' in record:
            assert json.loads((ROOT / record['view']).read_bytes()) == json.loads(body), receipt_path
        count += 1
    return count, failures


if __name__ == '__main__':
    count, failures = verify_responses()
    result = analyze()
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    dest = ROOT / 'inventory.json'
    if '--check' in sys.argv:
        assert dest.read_text() == encoded, 'inventory differs'
    else:
        dest.write_text(encoded)
    assert result['sibling_file_inventory_equal']
    assert not result['duplicate_tree_paths']
    assert not result['multiply_assigned_payload_paths']
    print(json.dumps({'verified_response_bodies': count, 'retained_transport_failures': failures,
                      'inventory_matches': True, 'tree_entries': result['tree_entry_count'],
                      'routed_configs': result['routed_config_count'],
                      'dataset_info_configs': result['dataset_info_config_count'],
                      'rows_accessed': 0}, sort_keys=True))
