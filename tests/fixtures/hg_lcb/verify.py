"""Reproduce w-lcb findings offline from raw metadata and source, without imports.

--write saves derived review metadata and a transport-integrity manifest. These
are not an issued task-207 record, publisher signature, approval, or row proof.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B6 = 'reports/b6-blocker-evidence/'
PINS = {
    'docs/evidence/lcb740/prior-selection.inert.json': '683d0a0e689b4579ffd8f61a3e672299c8e944014efcc9cffa75e99af3512d38',
    'docs/evidence/lcb740/prior-launch.json': 'b2402fc26b4ea0c675c7880ffd72e5272793df084ee9471aebcb06022ed8e168',
    'docs/task-207-livecodebench-operator-packet.md': '5b490cb33868811e623606c6c35c6c7f695dd5bf39ea2f382b5baa0e1049927f',
    B6 + 'lcb-hub-proxy-revision/hop-0.body': '501d60839cc3f592b476d5d79b1093f29ade0144fb3318f1b261d3ece274e4d4',
    B6 + 'lcb-hub-proxy-tree/hop-0.body': '91b24116907e1c5e5ed962fa90afe8583a36e97148e0ef6ed8369df21b27dee8',
    B6 + 'lcb-hub-proxy-builder/hop-1.body': '973e37989fed0f069c8246776e918d0d96600d64a3730cd6242dd76bccf2f7bb',
}
SOURCES = ['data/datasets/livecodebench.py', 'data/datasets/livecodebench/prepare.py',
           'data/scaffolds/registry.py', 'tools/lcb740_identity.py',
           'tools/launch_lcb740_candidate.py', 'docs/independent-review-deferred.md']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads((ROOT / path).read_bytes())


def literals(path, names):
    values = {}
    for node in ast.parse((ROOT / path).read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    values[target.id] = ast.literal_eval(node.value)
                elif isinstance(target, ast.Tuple):
                    for item, value in zip(target.elts, ast.literal_eval(node.value)):
                        if isinstance(item, ast.Name) and item.id in names:
                            values[item.id] = value
    require(set(values) == set(names), f'missing source declarations: {path}')
    return values


def derive():
    inherited = []
    for path, expected in PINS.items():
        raw = (ROOT / path).read_bytes()
        require(sha(raw) == expected, f'inherited pin changed: {path}')
        inherited.append(dict(path=path, bytes=len(raw), sha256=sha(raw)))
    # Recheck the inherited acquisition chain as well as pinned entity bytes.
    for name in ['lcb-hub-proxy-revision', 'lcb-hub-proxy-tree', 'lcb-hub-proxy-builder']:
        directory = ROOT / B6 / name
        receipt_path = directory / 'receipt.json'
        for hop, receipt in enumerate(json.loads(receipt_path.read_bytes())):
            body_path = directory / f'hop-{hop}.body'
            headers_path = directory / f'hop-{hop}.headers'
            require(sha(body_path.read_bytes()) == receipt['sha256'], 'inherited response changed')
            require(sha(headers_path.read_bytes()) == receipt['headers_sha256'], 'inherited headers changed')
            for path in [body_path, headers_path]:
                rel = str(path.relative_to(ROOT))
                if rel not in PINS:
                    inherited.append(dict(path=rel, bytes=path.stat().st_size, sha256=sha(path.read_bytes())))
        inherited.append(dict(path=str(receipt_path.relative_to(ROOT)), bytes=receipt_path.stat().st_size, sha256=sha(receipt_path.read_bytes())))
    sources = []
    for path in SOURCES:
        raw = (ROOT / path).read_bytes()
        sources.append(dict(path=path, bytes=len(raw), sha256=sha(raw)))
    responses = []
    for receipt_path in sorted(HERE.glob('*/receipt.json')):
        receipt = json.loads(receipt_path.read_bytes())
        require('error' not in receipt and receipt['complete'], str(receipt_path))
        body = (receipt_path.parent / 'response.body').read_bytes()
        headers = (receipt_path.parent / 'response.headers').read_bytes()
        require(sha(body) == receipt['sha256'] and len(body) == receipt['bytes'], 'response body changed')
        require(sha(headers) == receipt['headers_sha256'], 'response headers changed')
        require(receipt['tls_certificate_validation'] is True, 'TLS validation required')
        responses.append(dict(name=receipt_path.parent.name, **receipt))
    by_name = {r['name']: r for r in responses}
    require(set(by_name) == {'viewer-openapi', 'viewer-openapi-contract', 'viewer-splits', 'viewer-size', 'viewer-info'}, 'response inventory changed')
    require(by_name['viewer-openapi']['status'] == 302, 'OpenAPI redirect changed')
    require(by_name['viewer-openapi-contract']['status'] == 200, 'no OpenAPI contract')
    require(by_name['viewer-splits']['status'] == 501, 'viewer refusal changed')
    refusal = json.loads((HERE / 'viewer-splits/response.body').read_bytes())
    require('arbitrary Python code' in refusal['error'], 'different viewer refusal')
    for name in ['viewer-size', 'viewer-info']:
        require(by_name[name]['status'] == 404, 'availability changed')
        require(json.loads((HERE / name / 'response.body').read_bytes()) == {'error': 'Not found.'}, 'different missing response')
    contract = json.loads((HERE / 'viewer-openapi-contract/response.body').read_bytes())
    api_parameters = {}
    for endpoint in ['/splits', '/size', '/info', '/rows', '/filter']:
        parameters = contract['paths'][endpoint]['get']['parameters']
        resolved = [contract['components']['parameters'][p['$ref'].rsplit('/', 1)[1]] if '$ref' in p else p for p in parameters]
        api_parameters[endpoint] = [p['name'] for p in resolved]
        require('revision' not in api_parameters[endpoint], 'review changed revision support')
        require('columns' not in api_parameters[endpoint], 'review changed projection support')
    adapter = literals('data/datasets/livecodebench.py', ['REVISION', 'PROBLEMS', 'POOL_SHA256', '_FILES'])
    identity = literals('tools/lcb740_identity.py', ['TASK_ID', 'ROW_INDEX', 'QUESTION_ID', 'REVISION', 'POOL_SHA256', 'SPLIT_SHA256', 'STATEMENT_SHA256', 'PUBLIC_URL'])
    upstream = read(B6 + 'lcb-hub-proxy-revision/hop-0.body')
    tree = read(B6 + 'lcb-hub-proxy-tree/hop-0.body')
    require(upstream['sha'] == adapter['REVISION'] == identity['REVISION'], 'revision mismatch')
    shards = adapter['_FILES']
    upstream_shards = {r['rfilename']: r['lfs']['sha256'] for r in upstream['siblings'] if r['rfilename'] in shards}
    require(upstream_shards == shards, 'upstream/adaptor shard mismatch')
    tree_shards = {r['path']: r['lfs']['oid'] for r in tree if r['path'] in shards}
    require(tree_shards == shards, 'tree/adaptor shard mismatch')
    builder_raw = (ROOT / (B6 + 'lcb-hub-proxy-builder/hop-1.body')).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(builder_raw)).encode() + b'\0' + builder_raw).hexdigest()
    require(blob == next(r['blobId'] for r in upstream['siblings'] if r['rfilename'] == 'code_generation_lite.py'), 'builder Git blob mismatch')
    builder = literals(B6 + 'lcb-hub-proxy-builder/hop-1.body', ['_URLS', 'ALLOWED_FILES'])
    order = builder['ALLOWED_FILES']['release_v6']
    require(order == builder['_URLS']['test'] == list(shards), 'release shard ordering mismatch')
    require(builder['_URLS']['train'] == [], 'unexpected upstream train sources')
    inert = read('docs/evidence/lcb740/prior-selection.inert.json')
    launch = read('docs/evidence/lcb740/prior-launch.json')
    packet = (ROOT / 'docs/task-207-livecodebench-operator-packet.md').read_text()
    target = json.loads(packet.split('```json\n', 1)[1].split('```', 1)[0])  # Unissued template only.
    selected, = inert['selected_reference_records']
    mapping = dict(task_id=selected['task_id'], row_index=int(selected['task_id'].rsplit('/', 1)[1]),
                   question_id=selected['question_id'], side=selected['side'], revision=inert['source']['dataset_revision'],
                   pool_sha256=inert['source']['declared_pool_sha256'],
                   split_sha256=inert['source']['inferred_original_full_split_sha256'],
                   public_statement_sha256=launch['public_statement_sha256'])
    require(all(target[k] == v for k, v in mapping.items()), 'task-207 target/inert mismatch')
    for key in ['task_id', 'row_index', 'question_id']:
        require(mapping[key] == identity[key.upper()], 'identity constant mismatch: ' + key)
    require(mapping['pool_sha256'] == adapter['POOL_SHA256'] == identity['POOL_SHA256'], 'pool declaration mismatch')
    require(mapping['split_sha256'] == identity['SPLIT_SHA256'], 'split declaration mismatch')
    require(mapping['public_statement_sha256'] == identity['STATEMENT_SHA256'], 'statement declaration mismatch')
    require(launch['public_statement_source'] == identity['PUBLIC_URL'], 'public source declaration mismatch')
    require(inert['active'] is inert['execution_authorized'] is inert['source']['pool_hash_freshly_verified'] is False, 'inert status changed')
    require(selected['mapping_status'] == 'FILENAME_INFERRED_NOT_POOL_ATTESTED', 'mapping status changed')
    # A conditional calculation over the declared ordinal namespace, not observed pool rows.
    split = {'train': [], 'eval': []}
    for i in range(adapter['PROBLEMS']):
        task = f'livecodebench/{i}'
        split['eval' if hashlib.sha256(task.encode()).digest()[0] % 3 == 0 else 'train'].append(task)
    split_sha = sha(json.dumps({side: sorted(ids) for side, ids in split.items()}, sort_keys=True).encode())
    require(split_sha == mapping['split_sha256'], 'conditional full split digest mismatch')
    require({side: len(ids) for side, ids in split.items()} == {'train': inert['counts']['imposed_train_tasks'], 'eval': inert['counts']['imposed_eval_tasks']}, 'split count mismatch')
    selection = inert['selection']
    ranked = sorted([dict(task_id=task, rank_sha256=sha(('livecodebench\0' + task).encode())) for task in selection['eligible_pool_task_ids']], key=lambda r: (r['rank_sha256'], r['task_id']))
    require(ranked == selection['ranked_candidates'], 'inert candidate ranking mismatch')
    count = min(30, (len(ranked) + 9) // 10)
    require([r['task_id'] for r in ranked[:count]] == selection['selected_task_ids'], 'inert selected IDs mismatch')
    candidates = []
    for record in inert['eligible_reference_records']:
        task = record['task_id']
        require(sha(task.encode()) == record['task_id_sha256'], 'task ID hash mismatch')
        require(task in split[record['side']], 'candidate side mismatch')
        candidates.append(dict(task_id=task, question_id=record['question_id'], side=record['side'],
                               binding=record['mapping_status']))
    return dict(schema='harnessgrad.w-lcb.metadata-review.v1', inherited_evidence=inherited, source_files=sources,
                responses=responses, viewer_contract_parameters=api_parameters,
                viewer_revision_query_authenticated=False,
                upstream=dict(revision=upstream['sha'], ordered_release_v6_files=order,
                              advertised_shard_sha256=upstream_shards, builder_git_blob_sha1=blob,
                              tree_paths=[r['path'] for r in tree], problem_count_obtained=None,
                              row_ids_obtained=[], row_rank_obtained=None, complete_catalog_obtained=False),
                local=dict(declared_problem_count=adapter['PROBLEMS'], compared_declarations=mapping,
                           inferred_candidate_records=candidates, ranked_candidates=ranked,
                           original_namespace_conditional_split=dict(namespace='livecodebench/0..1054', counts={side: len(ids) for side, ids in split.items()}, sha256=split_sha,
                               scope='conditional on declared ordinal namespace; no physical pool or question-ID mapping attested'),
                           task207_template_matches=True, inert_selection_matches=True),
                authenticated_row_pool_split_statement_linkage=False, row_attested=False,
                pool_freshly_verified_here=False, blocker_closed=False,
                independent_approval_required=False, production_authorized=False,
                payload_access=False, benchmark_execution=False)


def manifest_text():
    return ''.join(f'{sha(path.read_bytes())}  {path.relative_to(HERE)}\n' for path in sorted(HERE.rglob('*'))
                   if path.is_file() and path.name != 'SHA256SUMS' and '__pycache__' not in path.parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    derived = json.dumps(derive(), indent=2) + '\n'
    if args.write:
        (HERE / 'review.json').write_text(derived)
        (HERE / 'SHA256SUMS').write_text(manifest_text())
    else:
        require((HERE / 'review.json').read_text() == derived, 'derived review stale')
        require((HERE / 'SHA256SUMS').read_text() == manifest_text(), 'fixture manifest stale')
    print('PASS: raw response/body/header hashes, inherited pins, six shard metadata bindings, builder Git blob, local declarations, conditional 1055-ID split, and inert selection')
    print('Coverage: 6/6 upstream shard identities; 0 upstream row IDs; upstream problem count/rank unavailable; 3 local inferred candidates only')
    print('row_attested=false; pool_freshly_verified_here=false; blocker_closed=false; independent_approval_required=false')


if __name__ == '__main__':
    main()
