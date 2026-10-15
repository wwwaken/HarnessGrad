#!/usr/bin/env python3
"""Read-only, offline, bounded BFCL runtime inventory. Run from repository root.

No BFCL module is executed here. AST edges are syntactic, not reachability claims.
Installed trees are observations, not reconstructed wheels or trusted builds.
"""
import ast
import csv
import email
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import sysconfig
import zipfile

OUT = Path(__file__).resolve().parent
BASE = Path('/mnt/8t/xubuqiang/anaconda3')
TARGETS = {
    'tree-sitter': '==0.21.3', 'tree-sitter-java': '==0.21.0',
    'tree-sitter-javascript': '==0.21.4', 'numpy': '==1.26.4',
    'pandas': '', 'requests': '', 'tqdm': '', 'python-dotenv': '>=1.0.1',
    'tenacity': '>=8.5.0', 'overrides': '', 'openai': '>=1.86.0',
    'anthropic': '==0.53.0', 'cohere': '==5.13.3', 'mistralai': '==1.7.0',
    'google-genai': '==1.24.0', 'qwen-agent': '', 'writer-sdk': '>=2.1.0',
    'datamodel-code-generator': '==0.25.7', 'boto3': '',
    'transformers': '(branch import; not pinned by BFCL)',
    'wandb': '==0.18.5 (optional BFCL extra)',
}


def norm(s):
    return re.sub(r'[-_.]+', '-', s).lower()


def digest(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def identity(p):
    p = Path(p)
    return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': digest(p)}


def write(name, rows):
    with (OUT / name).open('w') as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + '\n')
    print(f'{name}: {len(rows)} records', flush=True)


def write_chunks(stem, rows):
    """Keep each evidence file <1 MB, splitting on complete JSON records."""
    for old in OUT.glob(stem + '-[0-9][0-9][0-9].jsonl'):
        old.unlink()
    chunks, current, size = [], [], 0
    for row in rows:
        line = json.dumps(row, sort_keys=True, ensure_ascii=True) + '\n'
        if current and size + len(line.encode()) > 750000:
            chunks.append(current)
            current, size = [], 0
        current.append(row)
        size += len(line.encode())
    if current:
        chunks.append(current)
    for index, chunk in enumerate(chunks, 1):
        write(f'{stem}-{index:03}.jsonl', chunk)


def edges(path, module):
    text = path.read_text(errors='replace')
    tree = ast.parse(text, filename=str(path))
    lines = text.splitlines()
    result = []

    def visit(n, scope=(), guards=()):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in n.names]
            mods = names if isinstance(n, ast.Import) else [
                '.' * n.level + (n.module or '')]
            for mod in mods:
                result.append({'from': module, 'to': mod, 'names': names,
                               'source': f'{path}:{n.lineno}',
                               'text': ast.get_source_segment(text, n),
                               'scope': list(scope), 'guards': list(guards)})
        if isinstance(n, ast.Call):
            call = ast.unparse(n.func)
            if call in ('eval', 'exec', '__import__', 'importlib.import_module'):
                result.append({'from': module, 'dynamic_call': call,
                               'source': f'{path}:{n.lineno}',
                               'text': lines[n.lineno - 1],
                               'scope': list(scope), 'guards': list(guards)})
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            scope = scope + (n.name,)
        if isinstance(n, (ast.If, ast.Try)):
            guards = guards + (f'{type(n).__name__}@{n.lineno}',)
        for child in ast.iter_child_nodes(n):
            visit(child, scope, guards)

    visit(tree)
    return result


def source_graph():
    inv = json.loads(Path('tests/fixtures/e3_bfcl_source/inventory.json').read_text())
    modules, graph = [], []
    for item in inv['files']:
        p = Path(item['path'])
        if p.suffix != '.py':
            continue
        relative = item['original_path'].split('berkeley-function-call-leaderboard/')[1]
        module = relative[:-3].replace('/', '.')
        if module.endswith('.__init__'):
            module = module[:-9]
        record = identity(p)
        record.update(module=module, original_path=item['original_path'],
                      prior_inventory_sha256=item['sha256'],
                      matches_prior_inventory=(digest(p) == item['sha256']))
        modules.append(record)
        graph.extend(edges(p, module))
    write('source-modules.jsonl', modules)
    write('source-edges.jsonl', graph)
    return modules, graph


def sites():
    candidates = list(BASE.glob('lib/python*/site-packages'))
    candidates += list((BASE / 'envs').glob('*/lib/python*/site-packages'))
    candidates += list(Path('/mnt/20t/xubuqiang/venvs').glob('*/lib/python*/site-packages'))
    candidates += list(Path('/home/xubuqiang/.local/lib').glob('python*/site-packages'))
    candidates += list(Path('/usr/local/lib').glob('python*/dist-packages'))
    candidates += list(Path('/usr/lib').glob('python*/dist-packages'))
    return sorted(set(p.resolve() for p in candidates if p.is_dir()))


def scan():
    closure_file = OUT / 'selected-distributions.jsonl'
    if closure_file.exists():
        for line in closure_file.read_text().splitlines():
            TARGETS.setdefault(json.loads(line)['name'], 'transitive selected metadata')
    scope, found = [], []
    for root in sites():
        infos = sorted(root.glob('*.dist-info')) + sorted(root.glob('*.egg-info'))
        scope.append({'kind': 'installed-metadata', 'path': str(root), 'entries': len(infos),
                      'method': '*.dist-info and *.egg-info filenames; matching METADATA/PKG-INFO read'})
        for info in infos:
            name_guess = norm(info.name.rsplit('.dist-info', 1)[0].rsplit('.egg-info', 1)[0])
            if not any(name_guess.startswith(k + '-') or name_guess == k for k in TARGETS):
                continue
            meta = info / 'METADATA' if info.is_dir() else info
            if not meta.is_file():
                meta = info / 'PKG-INFO'
            if not meta.is_file():
                continue
            m = email.message_from_bytes(meta.read_bytes())
            if norm(m.get('Name', '')) not in TARGETS:
                continue
            found.append({'kind': 'installed-tree', 'name': m['Name'], 'version': m['Version'],
                          'site': str(root), 'metadata': identity(meta),
                          'wheel': (info / 'WHEEL').read_text() if (info / 'WHEEL').is_file() else None,
                          'requires_dist': m.get_all('Requires-Dist', []),
                          'status': 'FOUND installed metadata; original archive UNKNOWN'})
    cache_roots = [Path('/home/xubuqiang/.cache/pip'), Path('/mnt/20t/xubuqiang/.cache/pip'),
                   Path('/mnt/20t/xubuqiang/.uv-cache'), BASE / 'pkgs',
                   Path('tests/fixtures')]
    for root in cache_roots:
        count = zip_count = nonzip_bodies = 0
        errors = []
        for parent, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in ('__pycache__', '.git'))
            if Path(parent) == Path('tests/fixtures'):
                # Generated text evidence is not an input artifact cache.
                dirs[:] = [d for d in dirs if d != 'hg_bfclrt']
            for fn in sorted(files):
                count += 1
                p = Path(parent) / fn
                try:
                    if fn.endswith(('.whl', '.body')):
                        with p.open('rb') as f:
                            magic = f.read(4)
                        if magic != b'PK\x03\x04':
                            if fn.endswith('.body'):
                                nonzip_bodies += 1
                            continue
                        zip_count += 1
                        with zipfile.ZipFile(p) as z:
                            metadata = [n for n in z.namelist() if n.endswith('.dist-info/METADATA')]
                            for n in metadata:
                                m = email.message_from_bytes(z.read(n))
                                if norm(m.get('Name', '')) in TARGETS:
                                    wp = n.rsplit('/', 1)[0] + '/WHEEL'
                                    found.append({'kind': 'wheel-or-zip-body', **identity(p),
                                                  'name': m['Name'], 'version': m['Version'],
                                                  'metadata_member': n,
                                                  'wheel': z.read(wp).decode() if wp in z.namelist() else None,
                                                  'requires_dist': m.get_all('Requires-Dist', [])})
                    elif fn.endswith(('.conda', '.tar.bz2', '.tar.gz', '.tgz', '.zip')):
                        if any(norm(fn).startswith(k + '-') for k in TARGETS):
                            found.append({'kind': 'named-archive-unopened', **identity(p)})
                    elif fn in ('repodata_record.json', 'index.json') and 'info' in p.parts:
                        # Only the conda package root's own info/index.json, not arbitrary caches.
                        if p.parent.parent.parent == BASE / 'pkgs':
                            obj = json.loads(p.read_text())
                            if norm(obj.get('name', '')) in TARGETS:
                                found.append({'kind': 'conda-unpacked-metadata', **identity(p),
                                              'record': obj})
                except (OSError, ValueError, zipfile.BadZipFile) as e:
                    errors.append({'path': str(p), 'error': str(e)})
        scope.append({'kind': 'cache-or-fixture', 'path': str(root), 'exists': root.exists(),
                      'walk_followlinks': False, 'files_enumerated': count,
                      'zip_wheels_or_bodies_inspected': zip_count,
                      'opaque_nonzip_bodies_not_unpacked': nonzip_bodies,
                      'excluded_generated_packet': 'tests/fixtures/hg_bfclrt' if root == Path('tests/fixtures') else None,
                      'method': 'walk all regular entries; ZIP wheel/body METADATA; named archives; conda info/index.json',
                      'errors': errors})
    write('search-scope.jsonl', scope)
    write_chunks('candidates', found)
    return found


def installed_closure():
    # Chosen host interpreter only. Do not mix Python versions into one environment.
    from importlib.metadata import distributions
    root = BASE / 'lib/python3.12/site-packages'
    from packaging.requirements import Requirement
    from packaging.markers import default_environment
    ds = {}
    for info in sorted(root.glob('*.dist-info')):
        # Filename key avoids reading metadata for unrelated distributions.
        key = norm(info.name[:-10].rsplit('-', 1)[0])
        ds[key] = info
    queue = [(k, frozenset()) for k in TARGETS]
    smoke = OUT / 'smoke-base.jsonl'
    observed_tops = set()
    if smoke.exists():
        for line in smoke.read_text().splitlines():
            r = json.loads(line)
            if r['kind'] == 'observed-module' and str(root) + '/' in (r.get('path') or ''):
                observed_tops.add(r['module'].split('.')[0])
    observed_owners = []
    for name, info in ds.items():
        top = info / 'top_level.txt'
        record = info / 'RECORD'
        if top.is_file():
            tops = set(top.read_text(errors='replace').splitlines())
        elif record.is_file():
            tops = {row[0].split('/')[0].split('.')[0] for row in csv.reader(record.open())}
        else:
            continue
        hits = tops & observed_tops
        if hits:
            queue.append((name, frozenset()))
            observed_owners.append({'name': name, 'observed_top_modules': sorted(hits),
                                    'ownership_source': str(top if top.is_file() else record),
                                    'scope': 'import-smoke observed; may be optional/incidental'})
    write('observed-distribution-owners.jsonl', observed_owners)
    seen, recorded, rows, requirements = set(), set(), [], []
    while queue:
        name, extras = queue.pop(0)
        name = norm(name)
        if (name, extras) in seen:
            continue
        seen.add((name, extras))
        if name not in ds:
            if name not in recorded:
                rows.append({'name': name, 'status': 'ABSENT selected-site metadata', 'site': str(root)})
                recorded.add(name)
            continue
        info = ds[name]
        meta = info / 'METADATA'
        m = email.message_from_bytes(meta.read_bytes())
        if name not in recorded:
            rows.append({'name': name, 'version': m['Version'], 'status': 'FOUND selected-site metadata',
                     'metadata': identity(meta), 'dist_info': str(info),
                     'wheel': (info / 'WHEEL').read_text() if (info / 'WHEEL').is_file() else None,
                     'license_field': m.get('License'), 'license_expression': m.get('License-Expression'),
                     'license_files_declared': m.get_all('License-File', []),
                     'metadata_classifiers': m.get_all('Classifier', [])})
            recorded.add(name)
        for line, text in enumerate(meta.read_text(errors='replace').splitlines(), 1):
            if not text.startswith('Requires-Dist: '):
                continue
            r = Requirement(text[15:])
            active = r.marker is None or any(r.marker.evaluate(
                {**default_environment(), 'extra': extra}) for extra in extras | {''})
            requirements.append({'from': name, 'to': norm(r.name), 'text': text,
                                 'source': f'{meta}:{line}', 'active_no_extra': active,
                                 'evaluated_parent_extras': sorted(extras),
                                 'requested_extras': sorted(r.extras),
                                 'constraint': str(r.specifier),
                                 'extra_closure': 'recursive selected metadata'})
            if active:
                queue.append((norm(r.name), frozenset(r.extras)))
    write('selected-distributions.jsonl', rows)
    write('metadata-edges.jsonl', requirements)
    return rows


def files_and_edges():
    """Hash installed distribution members and read every retained Python import statement.

    The source universe is .py files actually observed in the import smoke, plus
    unexecuted transformers/wandb entry files. Statement scope and guards are preserved.
    Imports outside this universe remain boundaries, not guessed runtime edges.
    """
    distributions = [json.loads(l) for l in (OUT / 'selected-distributions.jsonl').read_text().splitlines()]
    observed = {}
    for line in (OUT / 'smoke-base.jsonl').read_text().splitlines():
        r = json.loads(line)
        if r['kind'] == 'observed-module' and r.get('path'):
            observed[Path(r['path']).resolve()] = r['module']
    for name in ('transformers', 'wandb'):
        observed[BASE / 'lib/python3.12/site-packages' / name / '__init__.py'] = name
    files, graph, native, licenses, errors = [], [], [], [], []
    parsed = set()
    for d in distributions:
        if not d.get('dist_info'):
            continue
        info = Path(d['dist_info'])
        record = info / 'RECORD'
        if not record.is_file():
            errors.append({'name': d['name'], 'error': 'RECORD absent; member universe UNKNOWN'})
            continue
        files.append({'name': d['name'], 'kind': 'installed-record', **identity(record)})
        for relative, advertised_digest, advertised_size in csv.reader(record.open()):
            p = (info.parent / relative).resolve()
            if p.suffix == '.pyc':
                continue
            if not p.is_file():
                errors.append({'name': d['name'], 'path': str(p), 'error': 'RECORD member absent'})
                continue
            if p in observed or '.so' in p.name or p.parent == info:
                row = {'name': d['name'], 'relative': relative,
                       'record_digest_untrusted': advertised_digest,
                       'record_size_untrusted': advertised_size, **identity(p)}
                files.append(row)
            if p.suffix == '.py' and p in observed:
                module = observed[p]
                try:
                    graph.extend(edges(p, module))
                    parsed.add(p)
                except (SyntaxError, UnicodeError) as e:
                    errors.append({'path': str(p), 'error': str(e)})
            if '.so' in p.name:
                native.append({'name': d['name'], **identity(p),
                               'build_python_exact': 'UNKNOWN (filename/WHEEL do not prove build interpreter)',
                               'dist_info_wheel': str(info / 'WHEEL')})
            if any(s in p.name.lower() for s in ('license', 'licence', 'notice', 'copying', 'copyright')):
                raw = p.read_bytes()
                dest = OUT / 'licenses' / f"{d['name']}--{digest(p)[:16]}.txt"
                dest.parent.mkdir(exist_ok=True)
                if b'\x00' not in raw and len(raw) < 900000:
                    dest.write_bytes(raw)
                    licenses.append({'name': d['name'], **identity(p), 'retained_path': str(dest.relative_to(Path.cwd())),
                                     'retained_sha256': digest(dest), 'text_read': True})
                else:
                    licenses.append({'name': d['name'], **identity(p), 'text_read': False,
                                     'retention': 'UNKNOWN text or too large'})
    # Include actually loaded stdlib Python files too, rather than guessing their imports.
    for p, module in sorted(observed.items()):
        if p in parsed or p.suffix != '.py' or not p.is_file():
            continue
        files.append({'name': 'observed-module outside selected RECORD universe',
                      'module': module, **identity(p)})
        try:
            graph.extend(edges(p, module))
        except (SyntaxError, UnicodeError) as e:
            errors.append({'path': str(p), 'error': str(e)})
    write_chunks('installed-files', files)
    # Store the source path/module once per file; every edge still has its exact line.
    grouped = {}
    for e in graph:
        path, line = e['source'].rsplit(':', 1)
        key = (e['from'], path)
        group = grouped.setdefault(key, {'module': e['from'], 'path': path, 'edges': []})
        item = {k: v for k, v in e.items() if k not in ('from', 'source')}
        item['line'] = int(line)
        group['edges'].append(item)
    write_chunks('installed-edges', list(grouped.values()))
    write('native-members.jsonl', native)
    write('licenses.jsonl', licenses)
    write('inspection-errors.jsonl', errors)


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'graph':
        source_graph()
    elif action == 'search':
        scan()
    elif action == 'closure':
        installed_closure()
    elif action == 'files':
        files_and_edges()
    else:
        raise SystemExit('graph | search | closure')
