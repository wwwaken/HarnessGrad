"""Read scorer sources and installed metadata; never execute a scorer or task."""
import ast
import collections
import hashlib
import importlib.metadata as md
import json
import pathlib
import platform
import subprocess
import sys
import sysconfig
import warnings

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def source(p):
    p = pathlib.Path(p)
    if not p.is_file() or p.suffix != '.py':
        return None
    txt = p.read_text()
    try:
        tree = ast.parse(txt)
    except (SyntaxError, UnicodeError):
        return None
    return {'path': str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
            'sha256': sha(p), 'imports': [
                {'line': n.lineno, 'text': ast.get_source_segment(txt, n),
                 'roots': [a.name.split('.')[0] for a in n.names] if isinstance(n, ast.Import)
                 else [(n.module or '').split('.')[0]]}
                for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]}

if __name__ == '__main__':
    # This branch runs in a fresh, kernel-isolated network namespace.
    if len(sys.argv) > 1:
        import importlib
        before = set(sys.modules)
        errors = {}
        for mod in sys.argv[1:]:
            try:
                importlib.import_module(mod)
            except Exception as exc:
                errors[mod] = repr(exc)
        modules = []
        for name, mod in sorted(sys.modules.items()):
            p = getattr(mod, '__file__', None)
            if p and pathlib.Path(p).is_file():
                modules.append({'name': name, 'path': str(pathlib.Path(p).resolve()),
                                'preexisting': name in before})
        print(json.dumps({'requested': sys.argv[1:], 'errors': errors, 'modules': modules}, indent=2))
        raise SystemExit(bool(errors))

    groups = {
        'alfworld': ['textworld.gym', 'alfworld.agents.environment.alfred_tw_env'],
        'chessbench_puzzles': ['chess'], 'qa_parquet_startup': ['pyarrow.parquet'],
        'ds1000': ['numpy', 'pandas', 'scipy', 'sklearn', 'matplotlib.pyplot', 'seaborn', 'torch', 'PIL', 'yaml', 'statsmodels.api', 'gensim'],
        'livecodebench': ['numpy'], 'reasoning_gym': ['reasoning_gym'],
        'jericho': ['jericho'], 'scienceworld': ['scienceworld'],
        'spreadsheetbench': ['openpyxl'],
    }
    env = dict(__import__('os').environ, CUDA_VISIBLE_DEVICES='', PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg')
    (HERE / 'audit').mkdir(exist_ok=True)
    receipt = []
    imported = {}
    for name, mods in groups.items():
        cmd = ['unshare', '-Urn', sys.executable, str(__file__), *mods]
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
        (HERE/'audit'/f'{name}.stdout.json').write_text(p.stdout)
        (HERE/'audit'/f'{name}.stderr.txt').write_text(p.stderr)
        receipt.append({'command': cmd, 'exit_code': p.returncode})
        imported[name] = json.loads(p.stdout)
    (HERE/'audit'/'commands.json').write_text(json.dumps(receipt, indent=2)+'\n')
    paths = set()
    datasets = {}
    for p in sorted((ROOT/'tests/fixtures/hg_wclo_actor/datasets').glob('*.json')):
        d = json.loads(p.read_text())
        # Leads only: source bytes and statements are independently read below.
        ds_paths = [f['path'] for f in d['adapter_and_check_sources']
                    if f['path'].endswith('.py') and not f['path'].endswith('/prepare.py')]
        datasets[p.stem] = {'source_paths': ds_paths}
        paths.update(ROOT/x if not pathlib.Path(x).is_absolute() else pathlib.Path(x) for x in ds_paths)
    paths.update((ROOT/'data/scaffolds/qa').rglob('*.py'))
    for group in imported.values():
        paths.update(pathlib.Path(m['path']) for m in group['modules'] if not m['preexisting'])
    src = [s for p in sorted(paths) if (s := source(p))]
    (HERE/'source-imports.json').write_text(json.dumps(src, indent=2)+'\n')
    mapping = md.packages_distributions()
    distributions = {}
    for name, data in imported.items():
        packages = set()
        for m in data['modules']:
            if m['preexisting'] or 'site-packages/' not in m['path']:
                continue
            packages.update(mapping.get(m['name'].split('.')[0], []))
        datasets.setdefault(name, {})['imported_distributions'] = sorted(packages)
        for pkg in packages:
            d = md.distribution(pkg)
            key = d.metadata['Name'].lower().replace('_', '-')
            if key in distributions:
                continue
            roots = sorted(r for r, ds in mapping.items() if pkg in ds)
            witnesses = [dict(path=s['path'], line=i['line'], text=i['text'])
                         for s in src for i in s['imports'] if set(i['roots']) & set(roots)]
            distributions[key] = {'name': d.metadata['Name'], 'version': d.version,
                'installed_wheel': d.read_text('WHEEL'), 'direct_url': d.read_text('direct_url.json'),
                'requirements': d.requires or [], 'import_roots': roots, 'source_witnesses': witnesses}
    # DS-1000 scoring executes the released code_context, not only execution.py.
    # Preserve import locations/counts only, never questions, answers or complete contexts.
    context = ROOT/'tests/fixtures/hg_wclo_actor/gold/ds1000.json'
    cp = pathlib.Path(json.loads(context.read_text())['artifacts'][0]['path'])
    census = []
    for rownum, line in enumerate(cp.open(), 1):
        row = json.loads(line)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            t = ast.parse(row['code_context'])
        for n in ast.walk(t):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                census.append({'jsonl_line': rownum, 'context_line': n.lineno, 'text': ast.unparse(n)})
    (HERE/'ds1000-context-imports.json').write_text(json.dumps({'source': str(cp), 'sha256': sha(cp), 'rows': rownum,
        'note': 'Static import statements only; no contexts executed. Imports in dynamically executed strings may add dependencies.', 'imports': census}, indent=2)+'\n')
    (HERE/'installed-distributions.json').write_text(json.dumps(distributions, indent=2)+'\n')
    (HERE/'source-scope.json').write_text(json.dumps({'datasets': datasets, 'environment': {
        'executable': sys.executable, 'python': sys.version, 'SOABI': sysconfig.get_config_var('SOABI'),
        'platform': sysconfig.get_platform(), 'libc': platform.libc_ver()},
        'note': 'Fresh imports are source-led leads, not task-selected execution or production closure.'}, indent=2)+'\n')
    print(json.dumps({'groups': {k: {'packages': len(v.get('imported_distributions', [])),
        'errors': imported.get(k, {}).get('errors', {})} for k,v in datasets.items()},
        'distribution_count': len(distributions), 'source_count': len(src)}, indent=2))
