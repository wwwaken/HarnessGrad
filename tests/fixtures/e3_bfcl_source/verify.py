"""Offline byte/import audit. Does not import acquired code or approve custody."""
import ast
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREFIX = 'berkeley-function-call-leaderboard/'


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    inventory = json.loads((HERE / 'inventory.json').read_bytes())
    assert inventory['schema'] != 'harnessgrad.bfcl-ast-source.v1'
    assert inventory['approved_receipt_pin'] is inventory['independent_review'] is None
    assert inventory['custodian_approved'] is inventory['production_authorized'] is False
    assert inventory['measured'] is inventory['runtime_closure'] is False
    for field in ('reused_tree', 'reused_inventory'):
        item = inventory[field]
        body = (ROOT / item['path']).read_bytes()
        assert sha256(body) == item['sha256'] and len(body) == item['bytes']
    tree = json.loads((ROOT / inventory['reused_tree']['path']).read_bytes())
    entries = {e['path']: e for e in tree['tree']}
    decoded = {}
    receipts = sorted((HERE / 'responses').glob('*.json'))
    for path in receipts:
        receipt = json.loads(path.read_bytes())
        item = receipt.get('response_body')
        if item is None:
            assert 'transport_error' in receipt
            continue
        raw = (ROOT / item['path']).read_bytes()
        assert sha256(raw) == item['sha256'] and len(raw) == item['bytes']
        if receipt['status'] != 200:
            continue
        api = json.loads(raw)
        body = base64.b64decode(api['content'])
        sha = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        assert sha == api['sha'] == receipt['pinned_blob_sha1']
        assert len(body) == api['size'] == receipt['decoded']['bytes']
        assert sha256(body) == receipt['decoded']['sha256']
        decoded[sha] = body

    sources = {}
    for item in inventory['files']:
        body = (ROOT / item['path']).read_bytes()
        assert sha256(body) == item['sha256'] and len(body) == item['bytes']
        assert hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() == item['git_blob_sha1']
        entry = entries[item['original_path']]
        assert entry['sha'] == item['git_blob_sha1'] and entry['size'] == item['bytes']
        assert item['archive_member_verified'] is False
        if item['newly_acquired']:
            assert decoded[item['git_blob_sha1']] == body
        if item['original_path'].endswith('.py'):
            sources[item['original_path']] = ast.parse(body)

    modules = {}
    for path in sources:
        module = path.removeprefix(PREFIX).removesuffix('.py').replace('/', '.')
        modules[module.removesuffix('.__init__')] = path
    imports = []
    dynamic_calls = []
    for path, parsed in sources.items():
        parents = {child: node for node in ast.walk(parsed) for child in ast.iter_child_nodes(node)}
        for node in ast.walk(parsed):
            parent = parents.get(node)
            function_scope = []
            while parent is not None:
                if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_scope.append(parent.name)
                parent = parents.get(parent)
            scope = '.'.join(reversed(function_scope)) or '<module/class>'
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                assert not isinstance(node, ast.ImportFrom) or not node.level
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module]
                for name in names:
                    local = name == 'bfcl_eval' or name.startswith('bfcl_eval.')
                    imports.append(dict(path=path, line=node.lineno, module=name,
                                        scope=scope, repository_local=local,
                                        resolved_original_path=modules.get(name) if local else None))
                    if local:
                        assert name in modules, (path, node.lineno, name)
            if isinstance(node, ast.Call):
                name = ast.unparse(node.func)
                if name in ('eval', 'exec', '__import__', 'importlib.import_module'):
                    dynamic_calls.append(dict(path=path, line=node.lineno, scope=scope, call=name))
        parent = Path(path).parent
        while str(parent).startswith(PREFIX + 'bfcl_eval'):
            initializer = str(parent / '__init__.py')
            if initializer in entries:
                assert initializer in sources, initializer
                assert (ROOT / next(i['path'] for i in inventory['files'] if i['original_path'] == initializer)).read_bytes() == b''
            parent = parent.parent

    initializers = [p for p in sources if p.endswith('/__init__.py')]
    result = dict(schema='harnessgrad.e3-bfcl-static-audit.v1',
                  scope='byte identities, AST syntax and explicit import names only; no upstream execution',
                  original_files=len(inventory['files']), python_files=len(sources),
                  new_original_files=sum(i['newly_acquired'] for i in inventory['files']),
                  initializers=initializers, http_requests=len(receipts), verified_blobs=len(decoded),
                  unresolved_explicit_imports=[], imports=imports, dynamic_calls=dynamic_calls,
                  third_party_import_roots=sorted({i['module'].split('.')[0] for i in imports
                                                  if not i['repository_local']
                                                  and i['module'].split('.')[0] not in sys.stdlib_module_names}),
                  independent_review=None, custodian_approved=False,
                  source_gate_passed=False, production_authorized=False, measured=False)
    (HERE / 'static-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('imports', 'dynamic_calls', 'initializers')}, indent=2))


if __name__ == '__main__':
    main()
